import {Instance,CSPlayerPawn} from "cs_script/point_script";
const MODEL="characters/models/exg/chrisan/lime_e/lime_e.vmdl";
function pawn(){const p=Instance.GetPlayerController(0)?.GetPlayerPawn();return p instanceof CSPlayerPawn&&p.IsValid()?p:undefined;}
function apply(p){if(!(p instanceof CSPlayerPawn)||!p.IsValid()||!p.IsAlive())return;const before=p.GetModelName();p.SetModel(MODEL);Instance.Msg("[LIME_TEST] before="+before+" after="+p.GetModelName());}
Instance.RegisterCheatCommand("lime_e_apply",()=>apply(pawn()));
Instance.RegisterCheatCommand("lime_e_verify",()=>{const p=pawn();if(!p){Instance.Msg("[LIME_TEST] local pawn missing");return;}const w=p.GetActiveWeapon();Instance.Msg("[LIME_TEST] model="+p.GetModelName()+" alive="+p.IsAlive()+" crouched="+p.IsDucked()+" weapon="+(w?.GetClassName()??"none")+" clip="+(w?.GetClipAmmo()??0));});
Instance.OnPlayerReset(({player})=>Instance.QueueAfterThinks(()=>apply(player)));
Instance.OnPlayerJump(()=>Instance.Msg("[LIME_TEST] jump"));
Instance.OnPlayerLand(()=>Instance.Msg("[LIME_TEST] land"));
Instance.OnGunFire(({weapon})=>Instance.Msg("[LIME_TEST] fire "+weapon.GetClassName()));
Instance.OnGunReload(({weapon})=>Instance.Msg("[LIME_TEST] reload "+weapon.GetClassName()));
Instance.OnPlayerKill(()=>Instance.Msg("[LIME_TEST] death"));
Instance.QueueAfterThinks(()=>apply(pawn()));
Instance.Msg("[LIME_TEST] official script loaded; precache prop must remain alive");