using System;
using System.IO;
using System.Net.Sockets;
using System.Text;
using System.Threading;
public sealed class LocalVConsole : IDisposable {
 readonly TcpClient client;readonly NetworkStream stream; readonly Thread reader;readonly StreamWriter log;readonly FileStream wire;
 volatile bool running=true;
 public LocalVConsole(int port,string logPath){
  client=new TcpClient();client.Connect("127.0.0.1",port);stream=client.GetStream();log=new StreamWriter(logPath,true,new UTF8Encoding(false));log.AutoFlush=true;wire=new FileStream(logPath+".wire.bin",FileMode.Append,FileAccess.Write,FileShare.Read);
  reader=new Thread(ReadLoop);reader.IsBackground=true;reader.Start();
 }
 byte[] ReadN(int count){var b=new byte[count];int pos=0;while(pos<count){int n=stream.Read(b,pos,count-pos);if(n==0)throw new EndOfStreamException();pos+=n;}return b;}
 void ReadLoop(){try{using(var all=new MemoryStream()){var buf=new byte[16384];int cursor=0;while(running){int got=stream.Read(buf,0,buf.Length);if(got==0)break;wire.Write(buf,0,got);wire.Flush();all.Write(buf,0,got);byte[] b=all.GetBuffer();int end=(int)all.Length;while(cursor+12<=end){if(b[cursor]!=80||b[cursor+1]!=82||b[cursor+2]!=78||b[cursor+3]!=84){cursor++;continue;}int len=(b[cursor+8]<<8)|b[cursor+9];if(len<40){cursor++;continue;}if(cursor+len>end)break;int start=cursor+40,count=len-40;for(int i=0;i<count;i++)if(b[start+i]==0){count=i;break;}string s=Encoding.UTF8.GetString(b,start,count);lock(log){log.Write(s);}cursor+=len;}}}}catch(Exception e){if(running)lock(log){log.WriteLine("[transport] "+e.Message);}}}
 public void Send(string command){var c=Encoding.UTF8.GetBytes(command);int n=13+c.Length;if(n>65535)throw new Exception("Command too long");var b=new byte[n];Encoding.ASCII.GetBytes("CMND").CopyTo(b,0);b[5]=0xD4;b[8]=(byte)(n>>8);b[9]=(byte)n;c.CopyTo(b,12);lock(log){log.WriteLine("\n[COMMAND] "+command);}stream.Write(b,0,b.Length);stream.Flush();}
 public void Dispose(){running=false;client.Close();reader.Join(1500);wire.Dispose();log.Dispose();}
}
