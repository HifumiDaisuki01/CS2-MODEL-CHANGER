using CounterStrikeSharp.API;
using CounterStrikeSharp.API.Core;
using CounterStrikeSharp.API.Modules.Timers;
using Microsoft.Extensions.Logging;

namespace PlayerModelChanger;

public partial class PlayerModelChanger
{
    internal ResourceCatalog ModelResources = new();
    private int _compatGeneration;
    private void InitializeServerCompatibility()
    {
        RegisterModelSmokeTest();
        ModelResources = ResourceCatalog.Load(Path.Combine(ModuleDirectory, "resource-catalog.json"));
        if (ModelResources.Failure != null) Logger.LogWarning("Models safely unavailable: {Reason}", ModelResources.Failure);
        AddCommand("pmc_status", "Model resource and persistence status", (_, command) =>
            command.ReplyToCommand($"PlayerModelChanger {ModuleVersion}; configured={Service.GetModelCount()}; verifiedResources={ModelResources.Count}; storage={Config.StorageType}; commands=css_models,css_model; botModels=disabled; resourceError={ModelResources.Failure ?? "none"}"));
    }

    private void ScheduleSpawnModel(CCSPlayerController player)
    {
        if (!Enable || !player.IsValid || player.IsBot || player.IsHLTV) return;
        uint controller = player.EntityHandle.Raw;
        int? user = player.UserId;
        int generation = _compatGeneration;
        // Run after normal skin/loadout initialization; never restore health, gear or position.
        AddTimer(0.35f, () =>
        {
            if (generation != _compatGeneration || !player.IsValid || player.EntityHandle.Raw != controller || player.UserId != user ||
                player.AuthorizedSteamID == null || player.TeamNum is not (2 or 3) || !player.PawnIsAlive ||
                player.PlayerPawn.Value is not { IsValid: true } pawn) return;
            try
            {
                if (!Service.MapDefaultModelInitialized(player))
                    Service.SetMapDefaultModel(player, pawn.CBodyComponent!.SceneNode!.GetSkeletonInstance().ModelState.ModelName);
                var model = Service.GetPlayerNowTeamModel(player);
                _ = SetModelNextServerFrame(player, model, model?.Disableleg ?? false);
            }
            catch (Exception e) { Logger.LogError(e, "Could not apply saved model; original model retained"); }
        }, TimerFlags.STOP_ON_MAPCHANGE);
    }

    private bool TryReadyPawn(CCSPlayerController player, uint controller, uint pawn, int? user, byte team, int generation)
        => generation == _compatGeneration && player.IsValid && player.EntityHandle.Raw == controller && player.UserId == user &&
           player.TeamNum == team && player.PawnIsAlive && player.PlayerPawn.Value is { IsValid: true } current && current.EntityHandle.Raw == pawn;

    public Task SetModelNextServerFrame(CCSPlayerController player, Model? model, bool disableleg)
    {
        if (!player.IsValid || !player.PawnIsAlive || player.PlayerPawn.Value is not { IsValid: true } initial) return Task.CompletedTask;
        uint controller = player.EntityHandle.Raw, pawnIdentity = initial.EntityHandle.Raw;
        int? user = player.UserId; byte team = player.TeamNum; int generation = _compatGeneration;
        return Server.NextFrameAsync(() =>
        {
            if (!TryReadyPawn(player, controller, pawnIdentity, user, team, generation)) return;
            var pawn = player.PlayerPawn.Value!;
            if (model != null && !ModelResources.Allows(model.Path)) model = null;
            string? path = model?.Path;
            if (path == null && !player.IsBot) path = Service.GetMapDefaultModel(player);
            if (string.IsNullOrEmpty(path)) return;
            try
            {
                // Visual model API only: no damage hooks, scale, health, equipment or movement writes.
                pawn.SetModel(path);
                if (model == null || player.IsBot) return;
                if (model.FixedSkin >= 0) pawn.AcceptInput("Skin", pawn, pawn, model.FixedSkin.ToString());
                else if (model.Skins.Count != 0) pawn.AcceptInput("Skin", pawn, pawn, Service.GetSkinPreference(player, model).ToString());
                if (model.FixedMeshgroups.Count != 0 || model.Meshgroups.Count != 0)
                {
                    ulong mask = pawn.CBodyComponent!.SceneNode!.GetSkeletonInstance().ModelState.MeshGroupMask;
                    if (!Service.InitMeshgroupPreference(player, model, mask))
                    {
                        mask = Utils.CalculateMeshgroupmask(Service.GetMeshgroupPreference(player, model).ToArray(), model.FixedMeshgroups);
                        if (mask != 0) { pawn.CBodyComponent.SceneNode.GetSkeletonInstance().ModelState.MeshGroupMask = mask; Utilities.SetStateChanged(pawn, "CBaseEntity", "m_CBodyComponent"); }
                    }
                }
            }
            catch (Exception e) { Logger.LogError(e, "Model apply failed; default selection remains available"); }
        });
    }
}
