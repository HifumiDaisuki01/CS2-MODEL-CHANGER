# Temporary console-only deployment probe

Build with .NET 10 and the exact server CSS API:

```sh
dotnet build -c Release -p:CssApiPath=/absolute/CounterStrikeSharp.API.dll
```

Copy the DLL to a new `plugins/ThreeModelProbe/` directory, load through CSS, then run `pmc_deploy_probe` from the trusted server console. Before starting, query the real values of `bot_quota`, `sv_hibernate_when_empty`, `bot_join_after_player`, `bot_stop` and `bot_dont_shoot` over RCON, and put them in the probe directory as `baseline.json`, mapping names to integer values (boolean false/true becomes 0/1). This required snapshot is restored during cleanup. It avoids assuming ConVar types across engine builds. Requires no human players or existing bots. Does not change map or game type. Cancels if a human joins.

The probe finds the existing PMC instance and calls its public `SetModelNextServerFrame` for Aluona, Myers and MIKA on one T and one CT test bot. It checks the model path and collision bounds, health and armor before/after each application, explicitly respawns and reapplies each model, then restores original bot models. Test bots and temporary cvars are cleaned up. Unload and remove the probe after collecting `report.json`.

This is not a human command/menu, automatic spawn-selection, reconnect, client download/rendering, or hitbox/damage equivalence test. No real player database writes are performed.
