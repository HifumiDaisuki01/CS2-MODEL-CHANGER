using System;
using System.IO;
using System.Text;
using System.Linq;
using System.Collections.Generic;
using System.Security.Cryptography;
public class BatchModels {
 public class Asset { public string Path, Source, Hash; public long Bytes; public string[] Refs; public string Error; }
 public class Model { public string Id, Path, Status; public string[] Missing, Conflicts, CaseMismatch, Dependencies, ArmsCandidates; public bool RerlParsed, HasPhysics; }
 public static List<Asset> Assets=new List<Asset>();
 public static List<Model> Models=new List<Model>();
 public static List<string> Conflicts=new List<string>();
 static string Hash(string f) { using(var s=File.OpenRead(f)) using(var h=SHA256.Create()) return BitConverter.ToString(h.ComputeHash(s)).Replace("-","").ToLowerInvariant(); }
 static uint U(byte[] b,int p) { return BitConverter.ToUInt32(b,p); }
 static string Z(byte[] b,int p) { int e=p; while(e<b.Length && b[e]!=0)e++; if(e==b.Length)throw new Exception("unterminated string"); return Encoding.UTF8.GetString(b,p,e-p); }
 static string[] ReadRefs(string f,out bool phys) {
  byte[] b=File.ReadAllBytes(f); phys=false;
  if(b.Length<16 || BitConverter.ToUInt16(b,4)!=12) throw new Exception("unsupported resource header");
  int table=checked(8+(int)U(b,8)), count=checked((int)U(b,12)); if(count>1000 || table<16 || table+count*12>b.Length)throw new Exception("bad block table");
  var refs=new List<string>();
  for(int i=0;i<count;i++){ int p=table+i*12; string tag=Encoding.ASCII.GetString(b,p,4); if(tag=="PHYS")phys=true; if(tag!="RERL")continue;
   int start=checked(p+4+(int)U(b,p+4)), length=checked((int)U(b,p+8)); if(start<0 || length<8 || start+length>b.Length)throw new Exception("bad RERL block");
   int t=checked(start+(int)U(b,start)), n=checked((int)U(b,start+4)); if(n>100000 || t<start || (long)t+n*16>start+length)throw new Exception("bad RERL entries");
   for(int j=0;j<n;j++){int q=t+j*16+8; long target=q+BitConverter.ToInt64(b,q); if(target<start || target>=start+length)throw new Exception("bad RERL name"); string s=Z(b,(int)target).Replace('\\','/'); if(!s.EndsWith("_c",StringComparison.Ordinal))s+="_c"; refs.Add(s);}
  } return refs.Distinct(StringComparer.Ordinal).ToArray();
 }
 public static void Run(string source,string output,string baseList) {
  Assets.Clear(); Models.Clear(); Conflicts.Clear();
  if(Directory.Exists(output))throw new Exception("output must not exist"); Directory.CreateDirectory(output);
  var roots=new List<string>(); foreach(string d in Directory.GetDirectories(source)){if(Directory.Exists(System.IO.Path.Combine(d,"characters")))roots.Add(d);}
  string old=System.IO.Path.Combine(source,"CS2_Aluona_Package_A.auto-fixed","CS2_Aluona_Package_A","addon","game","csgo_addons","cs2cm_aluona_localtest"); if(Directory.Exists(old))roots.Insert(0,old);
  foreach(string root in roots) foreach(string f in Directory.EnumerateFiles(root,"*",SearchOption.AllDirectories)) {
   if(!f.EndsWith("_c",StringComparison.OrdinalIgnoreCase))continue;
   string rel=f.Substring(root.Length+1).Replace('\\','/'); bool ph; string[] rr=new string[0]; string err=null;
   try{rr=ReadRefs(f,out ph);}catch(Exception e){err=e.Message;}
   Assets.Add(new Asset{Path=rel,Source=f,Hash=Hash(f),Bytes=new FileInfo(f).Length,Refs=rr,Error=err});
   if(Assets.Count%500==0)Console.WriteLine("Indexed "+Assets.Count+" compiled resources");
  }
  Build(output,baseList);
 }
 public static void Build(string output,string baseList) {
  Models.Clear(); Conflicts.Clear();
  var groups=Assets.GroupBy(a=>a.Path,StringComparer.OrdinalIgnoreCase).ToDictionary(g=>g.Key,g=>g.ToArray(),StringComparer.OrdinalIgnoreCase);
  foreach(var g in groups)if(g.Value.Select(a=>a.Hash).Distinct().Count()>1)Conflicts.Add(g.Key);
  var bases=new HashSet<string>(File.ReadAllLines(baseList),StringComparer.Ordinal);
  var copy=new Dictionary<string,Asset>(StringComparer.OrdinalIgnoreCase);
  foreach(var g in groups.Where(g=>g.Key.EndsWith(".vmdl_c",StringComparison.OrdinalIgnoreCase)).OrderBy(g=>g.Key)){
   var m=new Model{Path=g.Key.Substring(0,g.Key.Length-2)}; m.Id="m_"+g.Value[0].Hash.Substring(0,12);
   var missing=new HashSet<string>();var conflicts=new HashSet<string>();var casing=new HashSet<string>();var seen=new HashSet<string>(StringComparer.Ordinal);var queue=new Queue<string>();queue.Enqueue(g.Key);bool parsed=true; var closure=new List<Asset>();
   while(queue.Count>0){string p=queue.Dequeue();if(!seen.Add(p))continue;Asset[] candidates;
    if(!groups.TryGetValue(p,out candidates)){if(!bases.Contains(p))missing.Add(p);continue;}
    if(candidates.Select(item=>item.Hash).Distinct().Count()>1){conflicts.Add(p);continue;}
    Asset a=candidates[0];if(a.Path!=p)casing.Add(p+" -> "+a.Path);if(a.Error!=null){parsed=false;missing.Add("PARSE: "+p+": "+a.Error);} closure.Add(a);foreach(string r in a.Refs)queue.Enqueue(r);
   }
   bool physics;try{ReadRefs(g.Value[0].Source,out physics);}catch{physics=false;}m.HasPhysics=physics;m.RerlParsed=parsed;
   m.Missing=missing.OrderBy(x=>x).ToArray();m.Conflicts=conflicts.OrderBy(x=>x).ToArray();m.CaseMismatch=casing.OrderBy(x=>x).ToArray();m.Dependencies=seen.OrderBy(x=>x).ToArray();
   string folder=System.IO.Path.GetDirectoryName(g.Key.Replace('/',System.IO.Path.DirectorySeparatorChar)).Replace('\\','/');
   m.ArmsCandidates=groups.Keys.Where(p=>p.StartsWith(folder+"/",StringComparison.Ordinal) && p.EndsWith(".vmdl_c") && (p.IndexOf("arm",StringComparison.OrdinalIgnoreCase)>=0 || p.IndexOf("hand",StringComparison.OrdinalIgnoreCase)>=0)).ToArray();
   bool arm=g.Key.IndexOf("arm",StringComparison.OrdinalIgnoreCase)>=0 || g.Key.IndexOf("hand",StringComparison.OrdinalIgnoreCase)>=0;
   m.Status=conflicts.Count>0?"conflict":missing.Count>0 || casing.Count>0?"dependency_pending":arm?"arms_candidate":"files_complete_candidate";
   if(g.Key.StartsWith("particles/",StringComparison.Ordinal))m.Status="auxiliary_resource"; else if(!g.Key.StartsWith("characters/",StringComparison.Ordinal))m.Status="path_compatibility_pending"; else if(arm && m.Status=="dependency_pending")m.Status="arms_dependency_pending";
   if(m.Status=="files_complete_candidate")foreach(var a in closure)copy[a.Path]=a;
   Models.Add(m);
  }
  string dest=System.IO.Path.Combine(output,"inspection-only","dependency-closures");Directory.CreateDirectory(dest);
  foreach(var a in copy.Values){string target=System.IO.Path.Combine(dest,a.Path.Replace('/',System.IO.Path.DirectorySeparatorChar));Directory.CreateDirectory(System.IO.Path.GetDirectoryName(target));if(!File.Exists(target))File.Copy(a.Source,target,false);if(Hash(target)!=a.Hash)throw new Exception("copy hash mismatch "+a.Path);}
  File.WriteAllLines(System.IO.Path.Combine(output,"SHA256SUMS.txt"),copy.Values.OrderBy(a=>a.Path).Select(a=>a.Hash+"  "+a.Path),new UTF8Encoding(false));
 }
}
