from pathlib import Path
import subprocess,re,json,concurrent.futures,hashlib,argparse
parser=argparse.ArgumentParser(description='Read compiled model DATA with Source 2 Viewer; no decompile, mount, or live writes')
parser.add_argument('--input',required=True);parser.add_argument('--output',required=True);parser.add_argument('--cli',required=True);parser.add_argument('--threads',type=int,default=4)
args=parser.parse_args();root=Path(args.input);output=Path(args.output);cli=args.cli
if output.resolve()==root.resolve() or output.resolve().is_relative_to(root.resolve()):raise ValueError('Output must be outside original inputs')
if output.exists() and any(output.iterdir()):raise ValueError('Use an empty report output')
output.mkdir(parents=True,exist_ok=True)
logs=output/'logs';logs.mkdir(exist_ok=True)
def inspect(f):
 rel=f.relative_to(root).as_posix();r=subprocess.run([cli,'-i',str(f),'-b','DATA'],capture_output=True,text=True)
 text=r.stdout; p=logs/(hashlib.sha256(rel.encode()).hexdigest()[:16]+'.txt');p.write_text(text+'\nSTDERR\n'+r.stderr)
 match=re.search(r'm_boneName\s*=\s*\[(.*?)\]',text,re.S);bones=re.findall(r'"([^"\n]+)"',match.group(1)) if match else []
 names=[b.lower() for b in bones]; csbones=[b for b in bones if b.lower() in ['pelvis','spine_0','spine_1','spine_2','neck_0','head_0','leg_upper_l','leg_upper_r','arm_upper_l','arm_upper_r']]
 refs=re.findall(r'Resource Name:.*?--- Resource Blocks:',text,re.S)
 ext=[]
 if refs:
  ext=re.findall(r'\b[0-9A-F]{16}\s+([^\r\n]+)',refs[0]);ext=[x.strip() for x in ext]
 hints=[x for x in re.findall(r'"([^"\n]+)"',text) if any(k in x.lower() for k in ['viewmodel','arms','skeleton','animgraph']) and ('/' in x or '.' in x)]
 return {'SourceSHA256':hashlib.sha256(f.read_bytes()).hexdigest(),'Path':rel[:-2],'EmbeddedName':re.search(r'm_name\s*=\s*"([^"]*)"',text).group(1) if re.search(r'm_name\s*=\s*"([^"]*)"',text) else None,'ToolExit':r.returncode,'BoneCount':len(bones),'Bones':bones,'CSBones':csbones,'ExternalReferences':ext,'ViewAnimationHints':sorted(set(hints)),'HasPHYS':bool(re.search(r'-- Block: PHYS',text)),'HasANIM':bool(re.search(r'-- Block: ANIM',text)),'HasAGRP':bool(re.search(r'-- Block: AGRP',text)),'HasCTRL':bool(re.search(r'-- Block: CTRL',text)),'Log':p.name}
def main():
 files=list(root.rglob('*.vmdl_c'))
 with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as pool: rows=list(pool.map(inspect,files))
 rows.sort(key=lambda x:x['Path']);(output/'semantic-review.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
 print('Models',len(rows),'tool errors',sum(x['ToolExit']!=0 for x in rows),'with CS bones',sum(bool(x['CSBones']) for x in rows),'with PHYS',sum(x['HasPHYS'] for x in rows),'without bones',sum(x['BoneCount']==0 for x in rows))
if __name__=='__main__':main()
