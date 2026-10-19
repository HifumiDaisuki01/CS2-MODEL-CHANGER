using System.Collections;
using System.Reflection;
using System.Text.Json;
using CounterStrikeSharp.API;
using CounterStrikeSharp.API.Core;
using CounterStrikeSharp.API.Modules.Cvars;

public sealed class ThreeModelProbe : BasePlugin
{
    public override string ModuleName => "ThreeModelProbe";
    public override string ModuleVersion => "1.0.0";
    public override string ModuleAuthor => "HifumiDaisuki01";
    private readonly string[] _ids = ["aluona", "myers", "mika"];
    private readonly List<CCSPlayerController> _bots = [];
    private readonly List<object> _checks = [];
    private readonly Dictionary<string,int> _cvars = [];
    private readonly Dictionary<int,string> _original = [], _before = [];
    private readonly Dictionary<int,uint> _identities = [];
    private object? _pmc;
    private IDictionary? _models;
    private MethodInfo? _apply;
    private int _phase, _at, _deadline, _index;
    private bool _respawn;
    public override void Load(bool hotReload)
    {
        AddCommand("pmc_deploy_probe", "Console-only empty-server three-model probe", (p,c) =>
        {
            if (p != null || _phase != 0 || Utilities.GetPlayers().Any(x=>x.IsValid && !x.IsHLTV))
            { c.ReplyToCommand("Requires empty server, no bots or humans."); return; }
            try
            {
                var type=AppDomain.CurrentDomain.GetAssemblies().Select(a=>a.GetType("PlayerModelChanger.PlayerModelChanger")).First(t=>t!=null)!;
                _pmc=type.GetMethod("getInstance")!.Invoke(null,null)!;
                var config=type.GetProperty("Config")!.GetValue(_pmc)!;
                _models=(IDictionary)config.GetType().GetProperty("Models")!.GetValue(config)!;
                foreach(var id in _ids) if(!_models.Contains(id)) throw new Exception("Missing configured model "+id);
                _apply=type.GetMethod("SetModelNextServerFrame")!;
                _checks.Clear(); _bots.Clear(); _original.Clear(); _identities.Clear(); _cvars.Clear();
                var saved=JsonSerializer.Deserialize<Dictionary<string,int>>(File.ReadAllText(Path.Combine(ModuleDirectory,"baseline.json")))!;
                foreach(var name in new[]{"bot_quota","sv_hibernate_when_empty","bot_join_after_player","bot_stop","bot_dont_shoot"})
                    _cvars[name]=saved[name];
                // Wake the engine before relying on Tick-based deadlines.
                Server.ExecuteCommand("sv_hibernate_when_empty 0; bot_join_after_player 0; bot_stop 1; bot_dont_shoot 1");
                _index=0;_respawn=false;_phase=1;_deadline=Server.TickCount+64*45;
                Server.ExecuteCommand("bot_add_t; bot_add_ct; bot_quota 2");
                c.ReplyToCommand("Started: explicit PMC apply/respawn checks on test bots; no client claims.");
            }
            catch(Exception e){Finish("FAIL",e.ToString());}
        });
        RegisterListener<Listeners.OnTick>(Tick);
        RegisterListener<Listeners.OnMapEnd>(()=>{if(_phase!=0)Finish("CANCELLED","Map ended");});
    }
    private static string Model(CCSPlayerController p)=>p.PlayerPawn.Value!.CBodyComponent!.SceneNode!.GetSkeletonInstance().ModelState.ModelName;
    private static string State(CCSPlayerController p)
    {
        var pawn=p.PlayerPawn.Value!;var box=pawn.Collision!;
        return JsonSerializer.Serialize(new{pawn.Health,pawn.ArmorValue,Min=new[]{box.Mins.X,box.Mins.Y,box.Mins.Z},Max=new[]{box.Maxs.X,box.Maxs.Y,box.Maxs.Z}});
    }
    private void Apply()
    {
        _before.Clear();
        foreach(var p in _bots){_before[p.Slot]=State(p);_apply!.Invoke(_pmc,[p,_models![_ids[_index]],false]);}
        _at=Server.TickCount+24;_phase=2;
    }
    private void Tick()
    {
        if(_phase==0)return;
        try
        {
            if(Utilities.GetPlayers().Any(p=>p.IsValid&&!p.IsBot&&!p.IsHLTV))throw new Exception("Human joined; cancelled");
            if(Server.TickCount>_deadline)throw new TimeoutException("45-second probe deadline");
            if(_phase==1)
            {
                var bots=Utilities.GetPlayers().Where(p=>p.IsValid&&p.IsBot&&p.PawnIsAlive&&p.TeamNum is 2 or 3).ToArray();
                if(bots.Length!=2||bots.Select(p=>p.TeamNum).Distinct().Count()!=2)return;
                foreach(var p in bots){_bots.Add(p);_original[p.Slot]=Model(p);_identities[p.Slot]=p.EntityHandle.Raw;}
                Apply();return;
            }
            if(Server.TickCount<_at)return;
            foreach(var p in _bots)if(!p.IsValid||p.EntityHandle.Raw!=_identities[p.Slot])throw new Exception("Test identity changed");
            if(_phase==3){if(_bots.All(p=>p.PawnIsAlive))Apply();return;}
            if(_phase==4)
            {
                foreach(var p in _bots)if(Model(p)!=_original[p.Slot])throw new Exception("Original model restore failed");
                Finish("PASS",null);return;
            }
            var m=_models![_ids[_index]]!;string expected=(string)m.GetType().GetProperty("Path")!.GetValue(m)!;
            foreach(var p in _bots)
            {
                if(!p.PawnIsAlive||Model(p)!=expected||State(p)!=_before[p.Slot])throw new Exception("Model or bounds/health/armor mismatch for "+_ids[_index]);
                _checks.Add(new{Id=_ids[_index],Team=p.TeamNum,AfterRespawnExplicitReapply=_respawn,Model=Model(p),BoundsHealthArmorUnchanged=true});
            }
            if(!_respawn){_respawn=true;foreach(var p in _bots)p.Respawn();_phase=3;_at=Server.TickCount+32;return;}
            _respawn=false;_index++;
            if(_index<_ids.Length){Apply();return;}
            foreach(var p in _bots)p.PlayerPawn.Value!.SetModel(_original[p.Slot]);
            _phase=4;_at=Server.TickCount+16;
        }
        catch(Exception e){Finish("FAIL",e.ToString());}
    }
    private void Finish(string result,string? error)
    {
        _phase=0;
        File.WriteAllText(Path.Combine(ModuleDirectory,"report.json"),JsonSerializer.Serialize(new{
            Result=result,Checks=_checks,OriginalBotModelRestoreVerified=result=="PASS",Error=error,TimeUtc=DateTimeOffset.UtcNow,
            HumanSpawnReconnectPersistenceTested=false,HumanMenuOrDefaultCommandTested=false,ClientAutoDownloadTested=false,ClientRenderingTested=false,HitboxDamageEquivalenceTested=false
        },new JsonSerializerOptions{WriteIndented=true}));
        foreach(var p in _bots)if(p.IsValid&&_identities.TryGetValue(p.Slot,out var id)&&p.EntityHandle.Raw==id)Server.ExecuteCommand("kickid "+p.UserId);
        foreach(var (name,value) in _cvars)Server.ExecuteCommand(name+" "+value);
        _bots.Clear();
    }
    public override void Unload(bool hotReload){if(_phase!=0)Finish("CANCELLED","Plugin unloading");}
}
