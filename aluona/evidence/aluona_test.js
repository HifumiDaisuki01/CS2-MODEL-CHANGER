import { Instance, CSPlayerPawn, BaseModelEntity } from "cs_script/point_script";

const MODEL = "characters/models/aluona/aluona.vmdl";

function apply(pawn) {
    if (!(pawn instanceof CSPlayerPawn) || !pawn.IsValid()) return;
    const before = pawn.GetModelName();
    pawn.SetModel(MODEL);
    Instance.Msg("[CS2CM] player model before=" + before + " after=" + pawn.GetModelName());
}

function applyAll() {
    const players = Instance.FindEntitiesByClass("player");
    Instance.Msg("[CS2CM] applyAll player count=" + players.length);
    for (const pawn of players) apply(pawn);
}

Instance.RegisterCheatCommand("cs2cm_apply", applyAll);
Instance.OnScriptInput("Apply", applyAll);
Instance.OnPlayerReset(({ player }) => Instance.QueueAfterThinks(() => apply(player)));
Instance.QueueAfterThinks(applyAll);
Instance.Msg("[CS2CM] official cs_script model test loaded; model=" + MODEL);
