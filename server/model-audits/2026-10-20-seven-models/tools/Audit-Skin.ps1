$ErrorActionPreference='Stop'
Add-Type -TypeDefinition @'
using System;
using System.Collections.Generic;
public static class SkinWeightAudit {
 public static int Size(int t){switch(t){case 5121:return 1;case 5123:return 2;case 5125:case 5126:return 4;default:throw new Exception("Unsupported glTF type");}}
 static double Read(byte[] b,int o,int t,bool norm){switch(t){case 5121:return norm?b[o]/255.0:b[o];case 5123:return norm?BitConverter.ToUInt16(b,o)/65535.0:BitConverter.ToUInt16(b,o);case 5125:return BitConverter.ToUInt32(b,o);case 5126:return BitConverter.ToSingle(b,o);default:throw new Exception("Unsupported glTF type");}}
 public static Dictionary<int,double> Sum(byte[] b,int jo,int js,int jt,int wo,int ws,int wt,bool wn,int count){
  var result=new Dictionary<int,double>();int jz=Size(jt),wz=Size(wt);
  for(int v=0;v<count;v++)for(int c=0;c<4;c++){
   double w=Read(b,wo+v*ws+c*wz,wt,wn);if(Double.IsNaN(w)||Double.IsInfinity(w))throw new Exception("Non-finite weight");if(w<=0.00000001)continue;
   int j=(int)Read(b,jo+v*js+c*jz,jt,false);if(!result.ContainsKey(j))result[j]=0;result[j]+=w;
  }return result;
 }
}
'@
$root='C:\Users\Administrator\Desktop\新版模型包带手臂（NL和Meme等通用）'
$old='C:\Users\Administrator\Desktop\新版模型包检查'
$logs=@{}
Get-ChildItem -LiteralPath (Join-Path $old 'logs') -Filter *.path | ForEach-Object {
 $path=[IO.File]::ReadAllText($_.FullName).Trim().Substring($root.Length+1).Replace('\','/')
 $logs[$path]=[IO.Path]::ChangeExtension($_.FullName,'txt')
}
$metadata=@{}
Import-Csv -LiteralPath (Join-Path $old '模型列表.csv') -Encoding UTF8 | ForEach-Object {$metadata[$_.'模型路径']=$_}
$paths=@{
 '10018'='characters/exg/10018/10018.vmdl_c'
 '10032'='characters/exg/10032/10032.vmdl_c'
 '10052'='characters/exg/10052/10052.vmdl_c'
 '10073'='characters/exg/10073/10073.vmdl_c'
 '10092'='characters/exg/10092/10092.vmdl_c'
 '10096'='characters/exg/10096/10096.vmdl_c'
 lime_e='characters/models/exg/chrisan/lime_e/lime_e.vmdl_c'
 xmanuka='characters/models/neon/xmanuka/xmanuka.vmdl_c'
}
$results=@(foreach($id in @('10018','10052','10073','10092','10096','lime_e','xmanuka')){
 $path=$paths[$id];$data=[IO.File]::ReadAllText((Join-Path $PSScriptRoot ($id+'\DATA.txt')));$meta=$metadata[$path]
 $gm=[regex]::Match($data,'m_meshGroups\s*=\s*\[(.*?)\]','Singleline')
 $groups=@([regex]::Matches($gm.Groups[1].Value,'"([^"]+)"')|ForEach-Object {$_.Groups[1].Value})
 $mm=[regex]::Match($data,'m_refMeshGroupMasks\s*=\s*\[(.*?)\]','Singleline')
 $masks=@([regex]::Matches($mm.Groups[1].Value,'\d+')|ForEach-Object {[uint64]$_.Value})
 $first=0..($groups.Count-1)|Where-Object {$groups[$_] -match '#&firstperson_default$'}|Select-Object -First 1
 if($null -eq $first){throw "Missing firstperson_default: $id"}
 $meshIndices=@(0..($masks.Count-1)|Where-Object {($masks[$_] -band ([uint64]1 -shl $first)) -ne 0})
 $glb=Join-Path $PSScriptRoot ($id+'\'+$id+'-rigged.glb');$b=[IO.File]::ReadAllBytes($glb)
 $len=[BitConverter]::ToUInt32($b,12);$j=[Text.Encoding]::UTF8.GetString($b,20,$len)|ConvertFrom-Json
 $binStart=28+$len
 $lm=[regex]::Match($data,'m_refLODGroupMasks\s*=\s*\[(.*?)\]','Singleline')
$lod=@([regex]::Matches($lm.Groups[1].Value,'\d+')|ForEach-Object {[uint64]$_.Value})
$sourceIndices=@(0..($lod.Count-1)|Where-Object {($lod[$_] -band 1) -ne 0})
if($j.meshes.Count -ne $sourceIndices.Count){throw "glTF highest-LOD/source order cannot be matched: $id"}
 $weighted=@{};$vertices=0;$names=@();$done=@{};$unskinned=@()
 foreach($mi in $meshIndices){
   $gi=@(0..($sourceIndices.Count-1)|Where-Object {$sourceIndices[$_] -eq $mi})
 if($gi.Count -ne 1){throw 'First-person mesh not present in exported highest LOD'}
 $mesh=$j.meshes[$gi[0]];$names+=$mesh.name
  $node=$j.nodes|Where-Object {$null -ne $_.mesh -and $_.mesh -eq $gi[0]}|Select-Object -First 1
  if($null -eq $node.skin){$unskinned+=$mesh.name;continue};$skin=$j.skins[[int]$node.skin]
  foreach($primitive in $mesh.primitives){
 $streamKey=([string]$gi[0])+'_'+$primitive.attributes.POSITION+'_'+$primitive.attributes.JOINTS_0+'_'+$primitive.attributes.WEIGHTS_0
 if($done.ContainsKey($streamKey)){continue};$done[$streamKey]=$true
   $ja=$j.accessors[[int]$primitive.attributes.JOINTS_0];$wa=$j.accessors[[int]$primitive.attributes.WEIGHTS_0]
   if($ja.type -ne 'VEC4' -or $wa.type -ne 'VEC4' -or $ja.count -ne $wa.count){throw 'Unexpected skin stream'}
   $jv=$j.bufferViews[[int]$ja.bufferView];$wv=$j.bufferViews[[int]$wa.bufferView]
   $jo=$binStart+[int]$jv.byteOffset+[int]$ja.byteOffset;$wo=$binStart+[int]$wv.byteOffset+[int]$wa.byteOffset
   $js=if($jv.byteStride){[int]$jv.byteStride}else{4*[SkinWeightAudit]::Size($ja.componentType)}
   $ws=if($wv.byteStride){[int]$wv.byteStride}else{4*[SkinWeightAudit]::Size($wa.componentType)}
   $sums=[SkinWeightAudit]::Sum($b,$jo,$js,$ja.componentType,$wo,$ws,$wa.componentType,[bool]$wa.normalized,$ja.count)
   foreach($entry in $sums.GetEnumerator()){
    $bone=$j.nodes[[int]$skin.joints[$entry.Key]].name
    if(!$weighted.ContainsKey($bone)){$weighted[$bone]=0.0};$weighted[$bone]+=$entry.Value
   };$vertices+=$ja.count
  }
 }
 $canonicalHands=@($weighted.Keys|Where-Object {$_ -match 'finger_|hand_[lr]$'})
 $hands=@($weighted.Keys|Where-Object {$_ -match 'finger|hand|palm'})
 $arms=@($weighted.Keys|Where-Object {$_ -match 'arm_(upper|lower)|forearm|foretwist|upperarm'})
 $legs=@($weighted.Keys|Where-Object {$_ -match 'leg_(upper|lower)|ankle|ball_[lr]$|toe'})
 [pscustomobject]@{
  Name=if($id -eq '10089'){'mingchao_feibi'}else{$id}
  Path=$path;Bones=[int]$meta.'骨骼数';AG2=$meta.AG2;Legacy=$meta.'旧动画引用';Missing=$meta.'缺失依赖'
  LegacyViewmodelWeightedBones=@($weighted.Keys|Where-Object {$_ -match 'v_weapon'})
CanonicalHandFingerSkinInfluence=($canonicalHands.Count -gt 0)
WeightedBoneNames=@($weighted.Keys|Sort-Object)
UnskinnedFirstPersonMeshNames=$unskinned;FirstPersonMeshIndices=$meshIndices;FirstPersonMeshNames=$names;FirstPersonVertices=$vertices
  PositiveWeightedHandFingerBones=$hands;PositiveWeightedArmBones=$arms;PositiveWeightedLegBones=$legs
  HasHandSkinInfluence=($hands.Count -gt 0);HasArmSkinInfluence=($arms.Count -gt 0);HasLegSkinInfluence=($legs.Count -gt 0)
  ModelDocExportSucceeded=(Test-Path -LiteralPath (Join-Path $PSScriptRoot ($id+'\'+$id+'.vmdl')))
  GLTFSkinAuditSucceeded=$true;GameVerified=$false
 }
})
$results|ConvertTo-Json -Depth 12|Set-Content -LiteralPath (Join-Path $PSScriptRoot 'firstperson-skin-audit.json') -Encoding UTF8
$results|Select-Object Name,Bones,FirstPersonVertices,HasHandSkinInfluence,HasArmSkinInfluence,HasLegSkinInfluence,ModelDocExportSucceeded|Format-Table -AutoSize
