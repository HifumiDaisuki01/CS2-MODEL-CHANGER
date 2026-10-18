using PlayerModelChanger;
using System.Security.Cryptography;
using System.Text.Json;
using Microsoft.Data.Sqlite;

int passed=0;
void Check(bool condition,string message){if(!condition)throw new Exception(message);}
void Test(string name,Action action){action();Console.WriteLine("PASS "+name);passed++;}
string root=Path.Combine(Path.GetTempPath(),"AluonaTests-"+Guid.NewGuid().ToString("N"));Directory.CreateDirectory(root);
try
{
 Test("SQLite T/CT selection survives a fresh storage instance",()=>{
  var first=new SqliteStorage(root);first.SetPlayerTModel(76561198000000001,"aluona",false);first.SetPlayerCTModel(76561198000000001,"aluona",false);
  var reopened=new SqliteStorage(root);Check(reopened.GetPlayerTModel(76561198000000001)=="aluona"&&reopened.GetPlayerCTModel(76561198000000001)=="aluona","Selection not committed");
 });
 Test("default selection persists independently for both teams",()=>{
  var db=new SqliteStorage(root);db.SetPlayerTModel(76561198000000001,"@default",false);db.SetPlayerCTModel(76561198000000001,"@default",false);
  var reopened=new SqliteStorage(root);Check(reopened.GetPlayerTModel(76561198000000001)=="@default"&&reopened.GetPlayerCTModel(76561198000000001)=="@default","Reset lost");
 });
 Test("SQLite parameterization keeps model identifiers as data",()=>{
  var db=new SqliteStorage(root);string value="'; DROP TABLE players; --";db.SetPlayerTModel(76561198000000002,value,false);
  Check(db.GetPlayerTModel(76561198000000002)==value&&db.GetPlayerCTModel(76561198000000001)=="@default","Unsafe SQL");
 });
 string archive=Path.Combine(root,"model.vpk");File.WriteAllText(archive,"fixture archive");string catalog=Path.Combine(root,"resource-catalog.json");
 void WriteCatalog(string model="characters/models/aluona/aluona.vmdl")=>File.WriteAllText(catalog,JsonSerializer.Serialize(new ResourceCatalog {Archives=new(){{archive,Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(archive)))}},Models=[model]}));
 Test("only a hash-verified archive authorizes a model",()=>{WriteCatalog();var c=ResourceCatalog.Load(catalog);Check(c.Count==1&&c.Allows("characters/models/aluona/aluona.vmdl")&&!c.Allows("characters/other.vmdl"),"Wrong authorization");});
 Test("modified or missing archives safely deny models",()=>{File.AppendAllText(archive,"changed");Check(ResourceCatalog.Load(catalog).Count==0,"Modified archive accepted");File.Delete(archive);Check(ResourceCatalog.Load(catalog).Count==0,"Missing archive accepted");});
 Test("invalid model paths and malformed catalog safely deny models",()=>{File.WriteAllText(archive,"fixture archive");WriteCatalog("characters/../outside.vmdl");Check(ResourceCatalog.Load(catalog).Count==0,"Traversal accepted");File.WriteAllText(catalog,"{broken");Check(ResourceCatalog.Load(catalog).Count==0,"Malformed JSON accepted");});
 Test("phase2 characters allowed while traversal and unrelated roots stay denied",()=>{WriteCatalog("phase2/characters/models/example/example_ag2.vmdl");Check(ResourceCatalog.Load(catalog).Count==1,"Phase2 denied");foreach(var bad in new[]{"phase2/characters/../bad.vmdl","phase2/materials/bad.vmdl","particles/test.vmdl","Phase2/characters/test.vmdl","phase2/characters/back\\\\slash.vmdl"}){WriteCatalog(bad);Check(ResourceCatalog.Load(catalog).Count==0,"Unsafe path accepted: "+bad);}});
 using var sql=new SqliteConnection("Data Source="+Path.Combine(root,"data.db"));sql.Open();using var query=sql.CreateCommand();query.CommandText="select sqlite_version()";Console.WriteLine("SQLite="+query.ExecuteScalar());
 Console.WriteLine("RESULT "+passed+" checks passed");
}
finally{SqliteConnection.ClearAllPools();Directory.Delete(root,true);}
