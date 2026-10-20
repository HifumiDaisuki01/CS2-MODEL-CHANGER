using System.Globalization;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using ValveKeyValue;
using ValveResourceFormat;
using ValveResourceFormat.ResourceTypes;

static string Hash(byte[] bytes)=>Convert.ToHexStringLower(SHA256.HashData(bytes));
static void Check(bool ok,string message){if(!ok)throw new InvalidDataException(message);}
static string Fingerprint(KVObject node){
 using var ms=new MemoryStream();using var w=new BinaryWriter(ms,Encoding.UTF8,true);
 void Put(KVObject n){
  w.Write(n.ValueType.ToString());w.Write(n.Flag.ToString());
  if(n.IsArray){w.Write(n.Count);foreach(var child in n.Values)Put(child);}
  else if(n.IsCollection){w.Write(n.Count);foreach(var kv in n.Children.OrderBy(x=>x.Key,StringComparer.Ordinal)){w.Write(kv.Key);Put(kv.Value);}}
  else if(n.ValueType.ToString().Contains("Blob",StringComparison.OrdinalIgnoreCase)){var b=n.AsBlob();w.Write(b.Length);w.Write(b);}
  else w.Write(n.ToString(CultureInfo.InvariantCulture)??"<null>");
 }
 Put(node);w.Flush();return Hash(ms.ToArray());
}
static KVDocument Parse(string s)=>KVSerializer.Create(KVSerializationFormat.KeyValues3Text).Deserialize(new MemoryStream(Encoding.UTF8.GetBytes(s)));
static string RemoveArmSettingText(string original){
 var serializer=KVSerializer.Create(KVSerializationFormat.KeyValues3Text);var (document,spans)=serializer.DeserializeWithSourceMap(original);Check(document.Root.ContainsKey("character_arm_config"),"Missing root arm setting");int depth=0,start=-1,end=-1;
 for(int i=0;i<spans.Count;i++){
  var span=spans[i];string token=original[span.Start..span.End];
  if(token=="{"){depth++;continue;}if(token=="}"){depth--;continue;}
  if(depth==1 && token.Trim('"')=="character_arm_config"){
   Check(start<0,"Duplicate root arm property");start=span.Start;int braces=0;bool began=false;
   for(int j=i+1;j<spans.Count;j++){var t=original[spans[j].Start..spans[j].End];if(t=="{"){began=true;braces++;}else if(t=="}" && began){braces--;if(braces==0){end=spans[j].End;break;}}}
   Check(end>start,"Arm setting is not a complete object");break;
  }
 }
 Check(start>=0&&end>start,"Unable to locate parsed property source span");return original.Remove(start,end-start);
}
static List<string> Strings(KVObject n){var result=new List<string>();void Walk(KVObject p){if(p.IsCollection||p.IsArray){foreach(var v in p.Values)Walk(v);}else if(p.ValueType.ToString().Contains("String"))result.Add(p.ToString());}Walk(n);return result;}
static List<(string Tag,int Offset,int Size)> Blocks(byte[] b){
 Check(b.Length>=16&&BitConverter.ToUInt16(b,4)==12,"Unsupported resource header");Check(BitConverter.ToUInt32(b,0)==b.Length,"Unexpected streamed tail or length");
 int table=checked(8+(int)BitConverter.ToUInt32(b,8)),count=checked((int)BitConverter.ToUInt32(b,12));Check(table>=16&&count>0&&count<1000&&table+count*12<=b.Length,"Invalid block table");var result=new List<(string,int,int)>();
 for(int i=0;i<count;i++){int p=table+12*i;var tag=Encoding.ASCII.GetString(b,p,4);int offset=checked(p+4+(int)BitConverter.ToUInt32(b,p+4)),size=checked((int)BitConverter.ToUInt32(b,p+8));Check(offset>=table+count*12&&offset+size<=b.Length,"Invalid block bounds");result.Add((tag,offset,size));}return result;
}
static BinaryKV3 DataView(Resource resource,byte[] bytes){
 var block=resource.DataBlock!;var data=new BinaryKV3(BlockType.DATA){Resource=resource,Offset=block.Offset,Size=block.Size};using var stream=new MemoryStream(bytes);using var reader=new BinaryReader(stream);data.Read(reader);return data;
}
try{
 Check(args.Length==4,"Usage: ResourceRepair INPUT.vmdl_c NEW_OUTPUT.vmdl_c EXPECTED_OBSOLETE_ANIMSET.vmdl REPORT.json");
 string input=Path.GetFullPath(args[0]),output=Path.GetFullPath(args[1]),missing=args[2],report=Path.GetFullPath(args[3]);Check(input!=output&&!File.Exists(output),"Use a new independent output");Check(missing.StartsWith("characters/")&&missing.EndsWith(".vmdl")&&!missing.Contains(".."),"Invalid expected resource");
 byte[] original=File.ReadAllBytes(input);var blocks=Blocks(original);Check(blocks.Count(b=>b.Tag=="DATA")==1&&blocks.Count(b=>b.Tag=="RERL")==1,"Expected one primary DATA and RERL block");
 using var resource=new Resource();resource.Read(input);var data=DataView(resource,original);var root=data.Data.Root;var info=root["m_modelInfo"];var embedded=Parse(info["m_keyValueText"].ToString());Check(Hash(original)=="6ebc7c80c53befdb2face68f0b74e9ed4be9998d5d2c5d05a08f8e6f3676ccd0","Only independently audited 10052 input is allowed");
 Check(missing=="characters/models/shared/animsets/animset_ct.vmdl","Only approved obsolete animset may be removed");
 Check(!embedded.Root.ContainsKey("character_arm_config"),"Unexpected separate arm configuration");
 Check(root.ContainsKey("m_refAnimIncludeModels")&&root["m_refAnimIncludeModels"].IsArray,"Expected animation include array");var include=root["m_refAnimIncludeModels"];Check(include.Count==1&&include[0].ToString()==missing,"Include list differs from approved legacy-only list");
 var refs=resource.ExternalReferences!;var originalRefs=refs.ResourceRefInfoList.Select(r=>new{r.Id,r.Name}).ToArray();
 foreach(string required in new[]{"animation/graphs/worldmodel/worldmodel.vnmgraph","animation/graphs/viewmodel/viewmodel.vnmgraph","animation/skeletons/characters/worldmodel.vnmskel","animation/skeletons/characters/viewmodel.vnmskel"})Check(refs.ResourceRefInfoList.Any(r=>r.Name==required),"Missing target AG2 reference: "+required);
 include.RemoveAt(0);Check(include.Count==0,"Animation include not removed");string expectedFingerprint=Fingerprint(root);Check(!Strings(root).Any(s=>s.Contains(missing,StringComparison.Ordinal)),"Obsolete animset still referenced in DATA");int removed=refs.ResourceRefInfoList.RemoveAll(r=>r.Name==missing);Check(removed==1,"Unexpected RERL removal count");
 using var dm=new MemoryStream();data.Serialize(dm);using var rm=new MemoryStream();refs.Serialize(rm);var replacement=new Dictionary<string,byte[]>{{"DATA",dm.ToArray()},{"RERL",rm.ToArray()}};
 using var target=new MemoryStream();using(var writer=new BinaryWriter(target,Encoding.UTF8,true)){
  writer.Write((uint)0);writer.Write(BitConverter.ToUInt16(original,4));writer.Write(BitConverter.ToUInt16(original,6));writer.Write((uint)8);writer.Write(blocks.Count);foreach(var b in blocks){writer.Write(Encoding.ASCII.GetBytes(b.Tag));writer.Write((uint)0);writer.Write((uint)0);}
  for(int i=0;i<blocks.Count;i++){
   while(target.Position%16!=0)writer.Write((byte)0);var block=blocks[i];int offset=checked((int)target.Position);byte[] bytes=replacement.TryGetValue(block.Tag,out var changed)?changed:original.AsSpan(block.Offset,block.Size).ToArray();writer.Write(bytes);long end=target.Position;target.Position=16+12*i+4;writer.Write((uint)(offset-(16+12*i+4)));writer.Write((uint)bytes.Length);target.Position=end;
  }long length=target.Length;target.Position=0;writer.Write((uint)length);writer.Flush();
 }
 byte[] updated=target.ToArray();var after=Blocks(updated);var proof=new List<object>();for(int i=0;i<blocks.Count;i++){var a=blocks[i];var b=after[i];Check(a.Tag==b.Tag,"Block order changed");bool changed=a.Tag is "DATA" or "RERL";var beforeHash=Hash(original.AsSpan(a.Offset,a.Size).ToArray());var afterHash=Hash(updated.AsSpan(b.Offset,b.Size).ToArray());Check(changed||beforeHash==afterHash,"Unrelated block changed: "+a.Tag);proof.Add(new{Index=i,Block=a.Tag,BeforeSHA256=beforeHash,AfterSHA256=afterHash,ByteIdentical=beforeHash==afterHash});}
 Directory.CreateDirectory(Path.GetDirectoryName(output)!);File.WriteAllBytes(output,updated);
 try{
  using var verify=new Resource();verify.Read(output);var actual=DataView(verify,updated);Check(Fingerprint(actual.Data.Root)==expectedFingerprint,"DATA semantic round trip differs");var nested=Parse(actual.Data.Root["m_modelInfo"]["m_keyValueText"].ToString());Check(Fingerprint(nested.Root)==Fingerprint(embedded.Root),"Embedded model settings changed");
  var expectedRefs=originalRefs.Where(r=>r.Name!=missing).OrderBy(r=>r.Id).Select(r=>$"{r.Id}:{r.Name}");var actualRefs=verify.ExternalReferences!.ResourceRefInfoList.OrderBy(r=>r.Id).Select(r=>$"{r.Id}:{r.Name}");Check(expectedRefs.SequenceEqual(actualRefs),"Remaining resource IDs/names changed");Check(Hash(File.ReadAllBytes(input))==Hash(original),"Source modified");
 }catch{File.Delete(output);throw;}
 var result=new{Input=input,Output=output,InputSHA256=Hash(original),OutputSHA256=Hash(updated),RemovedAnimationInclude=missing,RemovedGameSetting="m_refAnimIncludeModels[0]",StructuredKV3Editing=true,ResourceBlockTableRebuilt=true,OnlyDataAndReferenceBlocksChanged=true,OtherGameSettingsSemanticallyUnchanged=true,SkeletonAndMeshSettingsUnchanged=true,UnrelatedBlockHashes=proof,SourceBytesUnchanged=true,Recompiled=false,AG2ConversionPerformed=false,GameTested=false,StaticRepairPassed=true,Tool="ValveResourceFormat 20.1.7467 structured serializer"};Directory.CreateDirectory(Path.GetDirectoryName(report)!);File.WriteAllText(report,JsonSerializer.Serialize(result,new JsonSerializerOptions{WriteIndented=true}));Console.WriteLine("PASS "+Path.GetFileName(input)+" -> "+Hash(updated));
}catch(Exception e){Console.Error.WriteLine(e);return 1;}return 0;
