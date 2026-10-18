using System.Text.Json;
using CounterStrikeSharp.API;
using CounterStrikeSharp.API.Core;
using CounterStrikeSharp.API.Modules.Cvars;

namespace PlayerModelChanger;

public partial class PlayerModelChanger
{
    private sealed record SmokeBot(CCSPlayerController Player, uint Serial, string OriginalModel);
    private readonly List<SmokeBot> _smokeBots = [];
    private readonly Dictionary<int, string> _smokeState = [];
    private int _smokePhase, _smokeAt, _smokeDeadline, _smokeQuota, _smokeApplied;
    private bool _smokeHibernate, _smokeJoinAfterPlayer;
    private void RegisterModelSmokeTest()
    {
        AddCommand("pmc_selftest", "Console-only empty-server model lifecycle check", (player, command) =>
        {
            if (player != null || _smokePhase != 0 || Utilities.GetPlayers().Any(p => p.IsValid && !p.IsHLTV))
            { command.ReplyToCommand("Requires empty server, with no bots or players."); return; }
            if (!Config.Models.TryGetValue("aluona", out var model) || !ModelResources.Allows(model.Path))
            { command.ReplyToCommand("Verified Aluona resource unavailable."); return; }
            _smokeBots.Clear(); _smokeState.Clear(); _smokeApplied = 0;
            _smokeQuota = ConVar.Find("bot_quota")!.GetPrimitiveValue<int>();
            _smokeHibernate = ConVar.Find("sv_hibernate_when_empty")!.GetPrimitiveValue<bool>();
            _smokeJoinAfterPlayer = ConVar.Find("bot_join_after_player")!.GetPrimitiveValue<bool>();
            Server.ExecuteCommand("sv_hibernate_when_empty 0");
            Server.ExecuteCommand("bot_join_after_player 0");
            _smokePhase = 1; _smokeDeadline = Server.TickCount + 64 * 30;
            Server.ExecuteCommand("bot_add_t"); Server.ExecuteCommand("bot_add_ct"); Server.ExecuteCommand("bot_quota 2");
            command.ReplyToCommand("Aluona server lifecycle check started; no client rendering claims.");
        });
        RegisterListener<Listeners.OnTick>(ModelSmokeTick);
    }
    private static string SmokeState(CCSPlayerController p)
    {
        var pawn = p.PlayerPawn.Value!; var c = pawn.Collision!;
        return JsonSerializer.Serialize(new { pawn.Health, pawn.ArmorValue,
            Min = new[] {c.Mins.X,c.Mins.Y,c.Mins.Z}, Max = new[] {c.Maxs.X,c.Maxs.Y,c.Maxs.Z} });
    }
    private void ModelSmokeTick()
    {
        if (_smokePhase == 0) return;
        try
        {
            if (Utilities.GetPlayers().Any(p => p.IsValid && !p.IsBot && !p.IsHLTV)) throw new Exception("Human joined; cancelled");
            if (Server.TickCount > _smokeDeadline) throw new TimeoutException("Model smoke test timeout");
            if (_smokePhase == 1)
            {
                var bots = Utilities.GetPlayers().Where(p => p.IsValid && p.IsBot && p.PawnIsAlive && p.TeamNum is 2 or 3).ToArray();
                if (bots.Length != 2 || bots.Select(p => p.TeamNum).Distinct().Count() != 2) return;
                foreach (var p in bots) _smokeBots.Add(new(p,p.EntityHandle.Raw,p.PlayerPawn.Value!.CBodyComponent!.SceneNode!.GetSkeletonInstance().ModelState.ModelName));
                SmokeApply(); _smokePhase = 2; return;
            }
            if (Server.TickCount < _smokeAt) return;
            if (_smokePhase == 3)
            {
                if (_smokeBots.Any(b => !b.Player.IsValid || b.Player.EntityHandle.Raw != b.Serial || !b.Player.PawnIsAlive)) return;
                SmokeApply(); _smokePhase = 4; return;
            }
            foreach (var b in _smokeBots)
            {
                if (!b.Player.IsValid || b.Player.EntityHandle.Raw != b.Serial || !b.Player.PawnIsAlive) throw new Exception("Test bot unavailable");
                string model = b.Player.PlayerPawn.Value!.CBodyComponent!.SceneNode!.GetSkeletonInstance().ModelState.ModelName;
                if (model != Config.Models["aluona"].Path || SmokeState(b.Player) != _smokeState[b.Player.Slot]) throw new Exception("Model, collision bounds, health or armor mismatch");
            }
            if (_smokePhase == 2)
            {
                foreach (var b in _smokeBots) b.Player.Respawn();
                _smokePhase = 3; _smokeAt = Server.TickCount + 24; return;
            }
            foreach (var b in _smokeBots) b.Player.PlayerPawn.Value!.SetModel(b.OriginalModel);
            EndModelSmoke("PASS",null);
        }
        catch (Exception e) { EndModelSmoke("FAIL",e.ToString()); }
    }
    private void SmokeApply()
    {
        foreach (var b in _smokeBots)
        {
            _smokeState[b.Player.Slot] = SmokeState(b.Player);
            _ = SetModelNextServerFrame(b.Player, Config.Models["aluona"],false); _smokeApplied++;
        }
        _smokeAt = Server.TickCount + 8;
    }
    private void EndModelSmoke(string result,string? error)
    {
        File.WriteAllText(Path.Combine(ModuleDirectory,"server-smoke-report.json"),JsonSerializer.Serialize(new {
            Result=result, ModelApplications=_smokeApplied, Teams=new[]{"T","CT"}, RespawnThenExplicitReapply=true,
            CollisionBoundsHealthAndArmorUnchanged=result=="PASS", HumanAutoSpawnAndReconnectTested=false,
            ClientRenderingTested=false, ClientAutoDownloadTested=false, HitboxDamageValidation=false,
            Error=error,TimeUtc=DateTimeOffset.UtcNow }));
        _smokePhase=0;
        foreach(var b in _smokeBots)
            if(b.Player.IsValid && b.Player.EntityHandle.Raw==b.Serial) Server.ExecuteCommand("kickid "+b.Player.UserId);
        Server.ExecuteCommand("bot_quota "+_smokeQuota);
        Server.ExecuteCommand("bot_join_after_player "+(_smokeJoinAfterPlayer?1:0));
        Server.ExecuteCommand("sv_hibernate_when_empty "+(_smokeHibernate?1:0));
        _smokeBots.Clear();
    }
}
