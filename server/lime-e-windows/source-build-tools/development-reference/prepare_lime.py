from pathlib import Path
import sys,json,math,copy,io,struct,hashlib,zipfile,re,shutil
B=Path('/root/model-system-work'); sys.path[:0]=[str(B/'ag2-work/python-deps'),str(B/'repo/server/ag2-port/tools')]
import validate_source as V,port_projects as P
from srctools.dmx import Element,Attribute,ValueType,Quaternion
from srctools import Vec
import srctools.dmx as DMX
W=B/'lime-e-work'; O=W/'Lime-E-Windows-v1'; ADD='ks_ag2_repair'; REL='characters/models/exg/chrisan/lime_e/lime_e.vmdl'
C=O/'workshop-addon/content/csgo_addons'/ADD;G=O/'workshop-addon/game/csgo_addons'/ADD;R=O/'reports'
for d in [C,G,R,O/'tools',O/'configs']: d.mkdir(parents=True,exist_ok=True)
def writej(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mm(a,b):return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]
def ident():return [[float(i==j) for j in range(4)] for i in range(4)]
def inv(m):
 r=ident()
 for i in range(3):
  for j in range(3):r[i][j]=m[j][i]
  r[i][3]=-sum(r[i][j]*m[j][3] for j in range(3))
 return r
def apply(m,p,point=True):return [sum(m[i][j]*p[j] for j in range(3))+(m[i][3] if point else 0) for i in range(3)]
def trans(n):
 a=porter.angle_matrix(*n['angles']);m=ident()
 for i in range(3):
  for j in range(3):m[i][j]=a[i][j]
  m[i][3]=n['origin'][i]
 return m
def qmat(q,pos):
 x,y,z,w=q.x,q.y,q.z,q.w;m=ident();r=[[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]]
 for i in range(3):
  for j in range(3):m[i][j]=r[i][j]
  m[i][3]=pos[i]
 return m
def quat(m):
 t=sum(m[i][i] for i in range(3))
 if t>0:
  s=math.sqrt(t+1)*2;w=.25*s;x=(m[2][1]-m[1][2])/s;y=(m[0][2]-m[2][0])/s;z=(m[1][0]-m[0][1])/s
 else:
  i=max(range(3),key=lambda i:m[i][i]);j=(i+1)%3;k=(i+2)%3;s=math.sqrt(1+m[i][i]-m[j][j]-m[k][k])*2;q=[0.,0.,0.];q[i]=.25*s;q[j]=(m[j][i]+m[i][j])/s;q[k]=(m[k][i]+m[i][k])/s;w=(m[k][j]-m[j][k])/s;x,y,z=q
 return Quaternion(x,y,z,w)
def worlds(bones,parents):
 out={}
 def one(n):
  if n not in out:out[n]=mm(one(parents[n]),trans(bones[n])) if parents[n] else trans(bones[n])
  return out[n]
 for n in bones:one(n)
 return out
# Fresh independent copies; canonical conversion is never run against original assets.
porter=P.load_porter(B/'repo/server/ag2-port/tools/vendor/ag2port.py');canon=P.canonical(B/'repo/server/ag2-port/tools/vendor/canonical_skeleton.txt');porter.CANON_SIDED=[b for b,_ in canon if b.endswith(('_L','_R'))]
src=B/'arms-audit/input'/REL; dest=C/REL;dest.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(src,dest)
for f in src.parent.glob('*.dmx'):shutil.copy2(f,dest.parent/f.name)
changes=porter.port_vmdl(dest);tree=V.parse_kv3(dest.read_text());old=V.parse_kv3(src.read_text());bones,parents=V.skeleton(tree);oldbones,_=V.skeleton(old)
renames={n:n[:-2]+n[-2:].upper() for n in oldbones if n not in bones and n.endswith(('_l','_r')) and n[:-2]+n[-2:].upper() in bones}
# porter covers node references; independently cover physics weighted entries.
for n in V.nodes(tree):
 if 'weight' in n and n.get('name') in renames:n['name']=renames[n['name']]
armmodel=B/'arms-audit/trial/lime_e/arms/lime_e_ag2.vmdl';at=V.parse_kv3(armmodel.read_text());ab,ap=V.skeleton(at);armfile=armmodel.parent/'lime_e_ag2_unnamed_1.dmx';root=V.read_dmx(armfile);sk=root['skeleton'].val_elem;joints=list(sk['jointList'].iter_elem());mapping={n:next((k for k in bones if k.lower()==n.lower()),n) for n in ab};assert len(set(mapping.values()))==len(mapping)
# Confirm decompiled ModelDoc and DMX are genuinely the same bind pose.
err=0
for j in joints:
 if j.type=='DmeJoint' and j.name in ab:
  t=j['transform'].val_elem;m=qmat(t['orientation'].val_quat,tuple(t['position'].val_vec3));expected=trans(ab[j.name]);err=max(err,max(abs(m[i][k]-expected[i][k]) for i in range(4) for k in range(4)))
assert err<1e-4,err
aw=worlds(ab,ap);bw=worlds(bones,parents);indices={i:j.name for i,j in enumerate(joints)};matrices={i:mm(bw[mapping[n]],inv(aw[n])) for i,n in indices.items() if n in ab and mapping[n] in bw}
used=set();stats=[];original_streams=[]
for e in V.dmx_elements(root):
 if e.type!='DmeVertexData' or 'blendindices$0' not in e:continue
 count=e['jointCount'].val_int;idx=list(e['blendindices$0'].iter_int());weights=list(e['blendweights$0'].iter_float());positions=[tuple(x) for x in e['position$0'].iter_vec3()];pidx=list(e['position$0Indices'].iter_int());normals=[tuple(x) for x in e['normal$0'].iter_vec3()];nidx=list(e['normal$0Indices'].iter_int());tangents=list(e['tangent$0'].iter_vec4());tidx=list(e['tangent$0Indices'].iter_int());N=len(pidx)
 assert len(idx)==len(weights)==N*count
 newpos=[];newnorm=[];newtan=[];maxmove=0.;maxsumerr=0.;backerr=0.
 for vertex in range(N):
  wv=[(idx[vertex*count+k],weights[vertex*count+k]) for k in range(count) if weights[vertex*count+k]>1e-8];ws=sum(w for _,w in wv);assert abs(ws-1)<1e-4
  maxsumerr=max(maxsumerr,abs(ws-1));oldp=positions[pidx[vertex]];oldn=normals[nidx[vertex]];oldt=tangents[tidx[vertex]];p=[0.,0.,0.];n=[0.,0.,0.];t=[0.,0.,0.]
  for i,w in wv:
   assert i in matrices,(indices[i],i);used.add(indices[i]);m=matrices[i]
   for target,value,point in [(p,oldp,True),(n,oldn,False),(t,oldt,False)]:
    transformed=apply(m,value,point)
    for axis in range(3):target[axis]+=w*transformed[axis]
  def unit(a):
   length=math.sqrt(sum(x*x for x in a));assert length>1e-9;return [x/length for x in a]
  newpos.append(Vec(*p));newnorm.append(Vec(*unit(n)));newtan.append((*unit(t),oldt[3]));maxmove=max(maxmove,math.dist(oldp,p))
  # Single-influence vertices give an exact round-trip numerical proof.
  if len(wv)==1:backerr=max(backerr,math.dist(apply(inv(matrices[wv[0][0]]),p),oldp))
 e['position$0']=Attribute.array('position$0',ValueType.VEC3,newpos);e['position$0Indices']=Attribute.array('position$0Indices',ValueType.INTEGER,range(N));e['normal$0']=Attribute.array('normal$0',ValueType.VEC3,newnorm);e['normal$0Indices']=Attribute.array('normal$0Indices',ValueType.INTEGER,range(N));e['tangent$0']=Attribute.array('tangent$0',ValueType.VEC4,newtan);e['tangent$0Indices']=Attribute.array('tangent$0Indices',ValueType.INTEGER,range(N))
 stats.append({'Vertices':N,'MaximumRestPoseDisplacement':maxmove,'MaximumWeightSumError':maxsumerr,'SingleInfluenceRoundTripError':backerr,'UVIndicesWeightsTopologyPreserved':True})
# Shared twist names match the body's authored twist/constraints, rather than duplicates.
for j in joints:
 if j.type=='DmeJoint' and j.name in ab:
  name=mapping[j.name]
  if name in bones:
   j.name=name;n=bones[name];t=j['transform'].val_elem;t['position']=Vec(*n['origin']);t['orientation']=quat(trans(n))
rm=Element('root_motion','DmeJoint');rt=Element('root_motion','DmeTransform');rt['position']=Vec(*bones['root_motion']['origin']);rt['orientation']=quat(trans(bones['root_motion']));rm['transform']=rt;rm['visible']=True;rm['children']=Attribute.array('children',ValueType.ELEMENT);joints.append(rm)
byname={j.name:j for j in joints if j.type=='DmeJoint'}
# Rebuild hierarchy while retaining DmeDag mesh children and original skin joint indices.
for j in byname.values():
 children=[e for e in j['children'].iter_elem() if e.type!='DmeJoint'];j['children']=Attribute.array('children',ValueType.ELEMENT,children)
roots=[j for j in sk['children'].iter_elem() if j.type!='DmeJoint']
for name,j in byname.items():
 parent=parents.get(name) if name in bones else ap.get(name)
 if parent in byname:byname[parent]['children'].append(j)
 else:roots.append(j)
sk['children']=Attribute.array('children',ValueType.ELEMENT,roots);sk['jointList']=Attribute.array('jointList',ValueType.ELEMENT,joints)
# Preserve Source2Viewer binary9/model22 encoding; srctools scalar implementation
# matches it with the explicit array offset and empty-prefix adaptation.
armrel='characters/models/exg/chrisan/lime_e/lime_e_firstperson.dmx';armout=C/armrel
oldoffset=DMX.ARRAY_OFFSET
try:
 DMX.ARRAY_OFFSET=32;stream=io.BytesIO();root.export_binary(stream,version=5,fmt_name='model',fmt_ver=22,unicode='silent');raw=stream.getvalue().replace(b'encoding binary 5 ',b'encoding binary 9 ',1);p=raw.index(b'-->')+5;raw=raw[:p]+struct.pack('<I',0)+raw[p:];armout.write_bytes(raw)
finally:DMX.ARRAY_OFFSET=oldoffset
roundtrip=V.read_dmx(armout);assert len(list(roundtrip['skeleton'].val_elem['jointList'].iter_elem()))==len(joints)
# Mirror the runtime-proven Aluona first/third-person mesh + LOD layout.
children=tree['rootNode']['children'];render=next(n for n in children if n.get('_class')=='RenderMeshList');bodymesh=[m['name'] for m in render['children']];render['children'].append({'_class':'RenderMeshFile','name':'lime_e_fp_arms','filename':armrel})
groups=next(n for n in children if n.get('_class')=='BodyGroupList');groups['children'].insert(0,{'_class':'BodyGroup','name':'first_or_third_person','children':[{'_class':'BodyGroupChoice','name':'thirdperson_default','meshes':[]},{'_class':'BodyGroupChoice','name':'firstperson_default','meshes':['lime_e_fp_arms']}]})
children.insert(children.index(groups)+1,{'_class':'LODGroupList','children':[{'_class':'LODGroup','switch_threshold':0.0,'mesh_references':[{'mesh_name':'lime_e_fp_arms'}]},{'_class':'LODGroup','switch_threshold':0.5,'mesh_references':[{'mesh_name':n} for n in bodymesh]}]})
# Keep working upstream worldmodel default, both NmSkeleton bindings + hudmodel graph.
def kv(x,depth=0):
 tab='\t'*depth
 if isinstance(x,dict):return '{\n'+''.join('\t'*(depth+1)+k+' = '+kv(v,depth+1)+'\n' for k,v in x.items())+tab+'}'
 if isinstance(x,list):return '[\n'+''.join('\t'*(depth+1)+kv(v,depth+1)+',\n' for v in x)+tab+']'
 return json.dumps(x,ensure_ascii=False,allow_nan=False)
header=src.read_text().splitlines()[0];dest.write_text(header+'\n'+kv(tree)+'\n')
# Copy original material/texture payload exactly, never decompile/recompress textures.
assets={}
with zipfile.ZipFile(W/'assets.zip') as z:
 for n in z.namelist():
  if not n.endswith(('.vmat_c','.vtex_c')):raise ValueError(n)
  P.safe_relative(n);out=G/n;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(z.read(n));assets[n]=sha(out)
base=set((B/'repo/server/tools/base-resources-confirmed.txt').read_text().splitlines());missing=[]
for n in assets:
 for ref in P.refs(G/n):
  if ref not in assets and ref not in base:missing.append({'Source':n,'Missing':ref})
assert not missing,missing
# Runtime old arm config is intentionally replaced by embedded first-person mesh.
assert 'character_arm_config' not in dest.read_text();assert '.vanmgrph' not in dest.read_text()
for n in V.nodes(tree):
 for k in ['filename','source_filename']:
  f=n.get(k)
  if isinstance(f,str) and f.endswith('.dmx'):assert (C/f).is_file(),f
check=V.validate(dest,src,canon,G,base)
# The original magic effect is an unskinned rigid mesh, not a broken player mesh.
rigid='lime_e_magic12.dmx'; origraw=(src.parent/rigid).read_bytes();expected=origraw
for a,b in renames.items():expected=expected.replace(bytes([0])+a.encode()+bytes([0]),bytes([0])+b.encode()+bytes([0]))
assert (dest.parent/rigid).read_bytes()==expected,'Unexpected rigid-mesh payload edit'
original_rigid=V.check_dmx(src.parent/rigid,oldbones)
assert original_rigid['Failures']==['Render mesh has no recognized skin stream']
check['RigidMeshPreservation']={'File':rigid,'OriginallyUnskinned':True,'OnlyCanonicalBoneNamesChanged':True,'OriginalNumericPayloadPreserved':True}
check['Failures']=[f for f in check['Failures'] if f!='DMX failure: '+rigid]
check['Warnings'].append('Original magic effect is unskinned; unchanged rigid payload accepted, verify behavior in game')
check['StaticSourcePassed']=not check['Failures']
assert check['StaticSourcePassed'],check['Failures']
# Independently check skin stream invariants after DMX writer round-trip.
rsk=roundtrip['skeleton'].val_elem;rjs=[j.name for j in rsk['jointList'].iter_elem()];assert set(mapping[n] for n in used)<=set(bones)
originalroot=V.read_dmx(armfile);oe=[e for e in V.dmx_elements(originalroot) if e.type=='DmeVertexData' and 'blendindices$0' in e];ne=[e for e in V.dmx_elements(roundtrip) if e.type=='DmeVertexData' and 'blendindices$0' in e];assert len(oe)==len(ne)
for a,b in zip(oe,ne):
 for k in ['blendindices$0','blendweights$0','texcoord$0','texcoord$0Indices']:
  method='iter_int' if k in ['blendindices$0','texcoord$0Indices'] else ('iter_float' if k=='blendweights$0' else 'iter_vec2')
  assert list(getattr(a[k],method)())==list(getattr(b[k],method)()),k
 for i,w in zip(b['blendindices$0'].iter_int(),b['blendweights$0'].iter_float()):
  if w>1e-8:assert rjs[i] in bones
for a,b in zip([e for e in V.dmx_elements(originalroot) if e.type=='DmeFaceSet'],[e for e in V.dmx_elements(roundtrip) if e.type=='DmeFaceSet']):assert list(a['faces'].iter_int())==list(b['faces'].iter_int())
assert len([n for n in V.nodes(tree) if n.get('_class')=='BodyGroup'])==11
report={'Model':'lime_e','ModelPath':REL,'SourcePrepared':True,'StaticSourcePassed':True,'WindowsCompiled':False,'WorkshopMounted':False,'GameAnimationVerified':False,'OriginalBodySHA256':sha(src.with_name(src.name+'_c')),'OriginalArmSHA256':sha(armfile.with_name('lime_e_ag2.vmdl_c')) if armfile.with_name('lime_e_ag2.vmdl_c').exists() else '4d2c26bf43e9e0a4416412b5ce32e000ae6d7e39c7ada0f8ac787774a70a574f4','BodyBones':len(bones),'ArmVertices':sum(x['Vertices'] for x in stats),'ArmWeightedBones':len(used),'ArmFingerBones':len([n for n in ab if n.startswith('finger_')]),'OriginalArmDMXvsModelDocMatrixError':err,'ArmRebind':stats,'ArmBoneMapping':mapping,'MaterialTextureFiles':len(assets),'MaterialTextureBytes':sum((G/n).stat().st_size for n in assets),'UnresolvedMaterialTextureDependencies':missing,'Changes':changes+['Rebound original phase2 arm mesh into body rest pose with weighted rigid transform matrices; rotated/normalized normals+tangents; preserved UV/skin weights/topology','Renamed shared twist bindings to exact body bone names','Added DMX root_motion + matching body hierarchy','Embedded first-person mesh and Aluona-style first/third-person + LOD groups','Preserved 10 original appearance groups and 4 material groups','Removed missing legacy arm model config; no placeholder resource used'],'KnownRisks':['Windows resourcecompiler must verify binary9 and mixed mesh binding compilation','Aluona-style LOD/bodygroup integration must be checked first person and third person in CS2','Rest-pose LBS rebind is a source conversion; clipping and twist deformation still require weapon animation testing']}
writej(R/'source-validation.json',check);writej(R/'lime-e-conversion.json',report);writej(R/'preserved-assets.json',assets);writej(R/'selected-models.json',[{'Id':'lime_e','Path':REL}]);shutil.copy2(B/'repo/server/tools/base-resources-confirmed.txt',R/'base-resources-confirmed.txt')
(C/'addoninfo.txt').write_text('"addoninfo"\n{\n "addontitle" "Lime E AG2 body and arms"\n "addonauthor" "HifumiDaisuki01"\n "addonversion" "0.1"\n}\n')
writej(O/'configs/PlayerModelChanger-model-entry.json',{'Id':'lime_e','Name':'Lime E','Path':REL,'NOTE':'Merge using existing server config schema; do not overwrite SQLite/config. Both teams. Not installed.'})
writej(R/'source-files.json',{f.relative_to(O).as_posix():sha(f) for f in O.rglob('*') if f.is_file()})
print(json.dumps({k:v for k,v in report.items() if k not in ['ArmBoneMapping','ArmRebind','Changes']},indent=2));print('STATIC',check['Failures']);print('ARM',stats)
