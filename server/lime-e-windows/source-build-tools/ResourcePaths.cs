using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
public static class Ag2VpkDirectory {
 static string ReadZ(byte[] bytes,ref int pos) {
  int start=pos;while(pos<bytes.Length && bytes[pos]!=0)pos++;
  if(pos>=bytes.Length)throw new InvalidDataException("Truncated VPK string");
  string value=Encoding.UTF8.GetString(bytes,start,pos-start);pos++;return value;
 }
 public static HashSet<string> Read(string path) {
  using(var file=File.OpenRead(path))using(var reader=new BinaryReader(file)) {
   if(reader.ReadUInt32()!=0x55aa1234)throw new InvalidDataException("Invalid VPK magic");
   uint version=reader.ReadUInt32(),size=reader.ReadUInt32();
   if(version!=1 && version!=2)throw new InvalidDataException("Unsupported VPK version");
   if(size>64*1024*1024)throw new InvalidDataException("Oversized VPK directory");
   file.Position=version==1?12:28;
   byte[] tree=reader.ReadBytes((int)size);if(tree.Length!=size)throw new InvalidDataException("Truncated VPK directory");
   var names=new HashSet<string>(StringComparer.Ordinal);int pos=0;
   while(true) {
    string ext=ReadZ(tree,ref pos);if(ext.Length==0)break;
    while(true) {
     string dir=ReadZ(tree,ref pos);if(dir.Length==0)break;
     while(true) {
      string name=ReadZ(tree,ref pos);if(name.Length==0)break;
      if(pos+18>tree.Length)throw new InvalidDataException("Truncated VPK entry");
      int preload=BitConverter.ToUInt16(tree,pos+4);
      if(BitConverter.ToUInt16(tree,pos+16)!=65535)throw new InvalidDataException("Invalid VPK entry terminator");
      pos+=18+preload;if(pos>tree.Length)throw new InvalidDataException("Truncated VPK preload");
      string resource=(dir==" "?"":dir+"/")+name+(ext==" "?"":"."+ext);
      if(resource.Contains("..") || resource.Contains("\\") || resource.StartsWith("/"))throw new InvalidDataException("Unsafe VPK path");
      names.Add(resource);
     }
    }
   }
   return names;
  }
 }
}
