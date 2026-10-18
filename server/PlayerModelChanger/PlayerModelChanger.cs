using CounterStrikeSharp.API.Core;

using CounterStrikeSharp.API.Core.Attributes.Registration;
using CounterStrikeSharp.API;
using CounterStrikeSharp.API.Modules.Utils;
using System.Drawing;
using CounterStrikeSharp.API.Modules.Config;
using Microsoft.Extensions.Logging;
using CounterStrikeSharp.API.Modules.Memory;
using System.Runtime.InteropServices;
namespace PlayerModelChanger;

public partial class PlayerModelChanger : BasePlugin, IPluginConfig<ModelConfig>
{
    public override string ModuleName => "Player Model Changer";
    public override string ModuleVersion => "1.8.6-aluona.1";

    public override string ModuleAuthor => "samyyc";
    public required ModelConfig Config { get; set; }
    public required ModelService Service { get; set; }
    public required DefaultModelManager DefaultModelManager { get; set; }

    public required ModelMenuManager MenuManager { get; set; } = new();

    private static PlayerModelChanger? _Instance { get; set; }

    public bool Enable = true;

    public override void Load(bool hotReload)
    {
        _Instance = this;
        InitializeServerCompatibility();
        IStorage? Storage = null;
        switch (Config.StorageType)
        {
            case "sqlite":
                Storage = new SqliteStorage(ModuleDirectory);
                break;
            case "mysql":
                Storage = new MySQLStorage(Config.MySQLIP, Config.MySQLPort, Config.MySQLUser, Config.MySQLPassword, Config.MySQLDatabase, Config.MySQLTable);
                break;
        }
        ;
        if (Storage == null)
        {
            throw new Exception("[PlayerModelChanger] Failed to initialize storage. Please check your config");
        }
        DefaultModelManager = new DefaultModelManager();
        this.Service = new ModelService(Config, Storage, Localizer, DefaultModelManager);
        DefaultModelManager.ReloadConfig(ModuleDirectory, Service);
        if (!Config.DisablePrecache)
        {
            RegisterListener<Listeners.OnServerPrecacheResources>(PrecacheResource);
        }
        RegisterEventHandler<EventPlayerSpawn>(OnPlayerSpawnEvent);
        RegisterListener<Listeners.OnTick>(OnTick);
        RegisterListener<Listeners.OnMapEnd>(() =>
        {
            _compatGeneration++;
            Service.ClearMapDefaultModel();
        });

        Utils.InitializeLangPrefix();

        RegisterEventHandler<EventPlayerActivate>((@event, info) =>
        {
            if (@event.Userid != null)
            {
                MenuManager.RemovePlayer(@event.Userid.Slot);
                MenuManager.AddPlayer(@event.Userid.Slot, new ModelMenuPlayer { Player = @event.Userid, Buttons = 0 });
                ScheduleSpawnModel(@event.Userid);
            }
            return HookResult.Continue;
        });

        RegisterEventHandler<EventPlayerDisconnect>((@event, info) =>
        {
            if (@event.Userid != null)
            {
                MenuManager.RemovePlayer(@event.Userid.Slot);
            }
            return HookResult.Continue;
        });

        if (hotReload)
        {
            MenuManager.ReloadPlayer();
        }

        Logger.LogInformation($"Loaded {Service.GetModelCount()} model(s) successfully.");
    }

    private void PrecacheResource(ResourceManifest manifest)
    {
        foreach (var model in Service.GetAllModels())
        {
            Logger.LogInformation($"Precaching {model.Path}");
            if (ModelResources.Allows(model.Path)) manifest.AddResource(model.Path);
        }
    }

    public override void Unload(bool hotReload)
    {
        _compatGeneration++;
        if (_smokePhase != 0) EndModelSmoke("CANCELLED", "Plugin unloading");
        _Instance = null;
        RemoveListener<Listeners.OnServerPrecacheResources>(PrecacheResource);
        RemoveListener<Listeners.OnTick>(OnTick);
        DeregisterEventHandler<EventPlayerSpawn>(OnPlayerSpawnEvent);
        Logger.LogInformation("Unloaded successfully.");
    }

    public static PlayerModelChanger getInstance()
    {
        return _Instance!;
    }

    public void ReloadConfig()
    {
        var config = typeof(ConfigManager)
                   .GetMethod("Load")!
                   .MakeGenericMethod(typeof(ModelConfig))
                   .Invoke(null, new object[] { Path.GetFileName(ModuleDirectory) }) as IBasePluginConfig;
        OnConfigParsed((config as ModelConfig)!);
        Unload(true);
        Load(false);
        Service.ReloadConfig(ModuleDirectory, Config);
    }
    public void OnConfigParsed(ModelConfig config)
    {
        var availableStorageType = new[] { "sqlite", "mysql" };
        if (!availableStorageType.Contains(config.StorageType))
        {
            throw new Exception($"[PlayerModelChanger] Unknown storage type: {Config.StorageType}, available types: {string.Join(",", availableStorageType)}");
        }

        if (config.StorageType == "mysql")
        {
            if (config.MySQLIP == "")
            {
                throw new Exception("[PlayerModelChanger] You must fill in the MySQL_IP");
            }
            if (config.MySQLPort == "")
            {
                throw new Exception("[PlayerModelChanger] You must fill in the MYSQL_Port");
            }
            if (config.MySQLUser == "")
            {
                throw new Exception("[PlayerModelChanger] You must fill in the MYSQL_User");
            }
            if (config.MySQLPassword == "")
            {
                throw new Exception("[PlayerModelChanger] You must fill in the MYSQL_Password");
            }
            if (config.MySQLDatabase == "")
            {
                throw new Exception("[PlayerModelChanger] You must fill in the MySQL_Database");
            }
        }

        if (config.ModelForBots == null)
        {
            config.ModelForBots = new BotsConfig();
        }
        for (int i = 0; i < config.Models.Count; i++)
        {
            var entry = config.Models.ElementAt(i);
            ModelService.InitializeModel(entry.Key, entry.Value);
            if (config.Models.Where(m => m.Value.Name == entry.Value.Name).Count() > 1)
            {
                throw new Exception($"[PlayerModelChanger] Found duplicated model name: {entry.Value.Name}");
            }
        }

        Config = config;
    }

    public void OnTick()
    {
        Inspection.UpdateCamera();
        MenuManager.Update();
    }

    public HookResult OnPlayerSpawnEvent(EventPlayerSpawn e, GameEventInfo info)
    {
        if (e.Userid is { IsValid: true } player) ScheduleSpawnModel(player);
        return HookResult.Continue;
    }
}
