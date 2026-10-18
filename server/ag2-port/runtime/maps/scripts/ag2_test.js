import { Instance, CSPlayerPawn } from "cs_script/point_script";
const models = {
 myers: "characters/models/exg/myers/myers.vmdl",
 km_decade: "characters/models/exg/aquaz/km_decade/km_decade.vmdl",
 dujiaoshou: "characters/models/exg/dujiaoshou/dujiaoshou.vmdl"
};
let active = "myers";
function apply(pawn) {
 if (!(pawn instanceof CSPlayerPawn) || !pawn.IsValid() || !pawn.IsAlive()) return;
 const before = pawn.GetModelName();
 pawn.SetModel(models[active]);
 Instance.Msg("[AG2TEST] id=" + active + " before=" + before + " after=" + pawn.GetModelName());
}
function applyAll() {
 const players = Instance.FindEntitiesByClass("player");
 Instance.Msg("[AG2TEST] playerCount=" + players.length);
 for (const pawn of players) apply(pawn);
}
for (const id of Object.keys(models)) {
 Instance.RegisterCheatCommand("ag2_apply_" + id, () => { active = id; applyAll(); });
}
Instance.RegisterCheatCommand("ag2_verify", () => {
 for (const pawn of Instance.FindEntitiesByClass("player")) {
  if (pawn instanceof CSPlayerPawn && pawn.IsValid()) Instance.Msg("[AG2TEST] current=" + pawn.GetModelName() + " alive=" + pawn.IsAlive() + " crouched=" + pawn.IsDucked());
 }
});
Instance.OnPlayerReset(({player}) => Instance.QueueAfterThinks(() => apply(player)));
Instance.OnPlayerJump(() => Instance.Msg("[AG2TEST] jump model=" + active));
Instance.OnPlayerLand(() => Instance.Msg("[AG2TEST] land model=" + active));
Instance.OnGunFire(() => Instance.Msg("[AG2TEST] fire model=" + active));
Instance.OnGunReload(() => Instance.Msg("[AG2TEST] reload model=" + active));
Instance.OnPlayerKill(() => Instance.Msg("[AG2TEST] death model=" + active));
Instance.QueueAfterThinks(applyAll);
Instance.Msg("[AG2TEST] official cs_script loaded; precache props must remain alive");