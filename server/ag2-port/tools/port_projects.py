"""Reuse the pinned AG2 porter without its Steam/setup/material-placeholder paths.

Read source compiled models; write a NEW independent Workshop build project.
Nothing here installs, compiles, mounts, uploads, or edits a running server.
"""
import argparse, hashlib, importlib.util, json, re, shutil, struct, subprocess
from pathlib import Path
from validate_source import validate, parse_kv3, skeleton, nodes

ADDON = 'ks_ag2_repair'

def safe_relative(path):
    if not isinstance(path,str) or not path or '\\' in path or ':' in path or path.startswith('/') or any(p in ['','.','..'] for p in path.split('/')):
        raise ValueError('Unsafe relative resource path')
    return path

def sha(path):
    with Path(path).open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()

def refs(path):
    b=Path(path).read_bytes()
    if len(b)<16 or struct.unpack_from('<H',b,4)[0]!=12: raise ValueError('Invalid resource header: '+str(path))
    table=8+struct.unpack_from('<I',b,8)[0];count=struct.unpack_from('<I',b,12)[0];out=[]
    if table<16 or table+count*12>len(b):raise ValueError('Invalid block table')
    for i in range(count):
        p=table+12*i
        if b[p:p+4]!=b'RERL':continue
        start=p+4+struct.unpack_from('<I',b,p+4)[0];size=struct.unpack_from('<I',b,p+8)[0]
        if start+size>len(b):raise ValueError('Invalid RERL block')
        t=start+struct.unpack_from('<I',b,start)[0];n=struct.unpack_from('<I',b,start+4)[0]
        if t+n*16>start+size:raise ValueError('Invalid RERL entries')
        for j in range(n):
            q=t+16*j+8;target=q+struct.unpack_from('<q',b,q)[0]
            if not start<=target<start+size:raise ValueError('Invalid RERL string')
            end=b.index(0,target,start+size);s=b[target:end].decode()
            if not s.endswith('_c'):s+='_c'
            if '..' in s or '\\' in s or s.startswith('/'):raise ValueError('Unsafe resource reference')
            out.append(s)
    return out

def run_tool(cli, arguments, log):
    r=subprocess.run([str(cli),*map(str,arguments)],capture_output=True,text=True)
    Path(log).write_text(r.stdout+'\nSTDERR\n'+r.stderr)
    if r.returncode:raise RuntimeError('Source2Viewer failed; see '+str(log))
    return r.stdout

def load_porter(path):
    spec=importlib.util.spec_from_file_location('upstream_ag2_porter',path)
    porter=importlib.util.module_from_spec(spec);spec.loader.exec_module(porter)
    return porter

def canonical(path):
    pairs=[]
    for line in Path(path).read_text().splitlines():
        words=line.split()
        if len(words)==2:pairs.append((words[0],None if words[1]=='-' else words[1]))
    if len(pairs)!=74:raise ValueError('Unexpected canonical skeleton reference')
    return pairs

def prepare(source, manifest, base_list, cli, vendor, canon_file, output):
    source=Path(source).resolve();output=Path(output).resolve()
    if output==source or source in output.parents or output in source.parents:raise ValueError('Input/output trees must be independent')
    if output.exists():raise ValueError('Use a new output directory')
    rows=json.loads(Path(manifest).read_text(encoding='utf-8-sig'));base=set(Path(base_list).read_text().splitlines())
    porter=load_porter(vendor);canon=canonical(canon_file)
    # The experimental Linux script only names the sided core bones, omitting fingers.
    # Extend that documented hook to the complete pinned 74-bone reference; its
    # existing scoped Bone/reference/DMX code then updates all canonical names.
    porter.CANON_SIDED=[b for b,_ in canon if b.endswith(('_L','_R'))]
    reports=output/'reports';reports.mkdir(parents=True)
    content=output/'workshop-addon/content/csgo_addons'/ADDON
    game=output/'workshop-addon/game/csgo_addons'/ADDON
    content.mkdir(parents=True);game.mkdir(parents=True)
    results=[];all_copies={}
    for row in rows:
        ident=row['Id'];rel=row['Path'];src=source/(rel+'_c')
        if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,47}',ident):raise ValueError('Unsafe model identifier')
        safe_relative(rel)
        if not rel.startswith('characters/') or not rel.endswith('.vmdl'):raise ValueError('Expected original character ModelDoc path')
        if sha(src)!=row['OriginalSHA256']:raise ValueError('Original model SHA mismatch: '+ident)
        dest=content/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        result={'Id':ident,'Path':rel,'SourceConverted':False,'Compiled':False,'Mounted':False,'GameAnimationVerified':False}
        try:
            for block in ['DATA','RERL','PHYS','CTRL']:
                run_tool(cli,['-i',src,'-b',block],reports/(ident+'-original-'+block+'.txt'))
            run_tool(cli,['-i',src,'-o',dest,'-d'],reports/(ident+'-decompile.log'))
            if not dest.is_file() or not list(dest.parent.glob('*.dmx')):raise ValueError('No ModelDoc/DMX source produced')
            original=reports/(ident+'-original.vmdl');shutil.copy2(dest,original)
            before=parse_kv3(dest.read_text());old_bones,_=skeleton(before)
            original_dmx={f.name:f.read_bytes() for f in dest.parent.glob('*.dmx')}
            changes=porter.port_vmdl(dest)
            new_bones,_=skeleton(parse_kv3(dest.read_text()))
            rename={b:b[:-2]+b[-2:].upper() for b in old_bones if b not in new_bones and b.endswith(('_l','_r')) and b[:-2]+b[-2:].upper() in new_bones}
            # Physics vertex skin weights use {name, weight}, not a Bone node.
            # Only this unambiguous weight structure is retargeted; shape/hitbox
            # names remain untouched and are checked independently below.
            text=dest.read_text();weight_fixes=0
            for old,new in rename.items():
                pattern=r'(\bname\s*=\s*")'+re.escape(old)+r'("\s+weight\s*=)'
                text,n=re.subn(pattern,lambda m:m[1]+new+m[2],text);weight_fixes+=n
            dest.write_text(text)
            if weight_fixes:changes.append('Retargeted %d physics skin-weight bone names'%weight_fixes)
            # Preserve exact compiled materials/textures; do not run upstream
            # renaming, shader-default substitution, lossy image re-encoding,
            # setup, gameinfo, or Steam/account functions.
            dependencies=set();queue=[p for p in row['AllDependencies'] if p.endswith('.vmat_c')]
            while queue:
                p=queue.pop()
                safe_relative(p)
                if p in dependencies:continue
                dependencies.add(p);f=source/p
                if p in base:continue
                if not f.is_file():
                    if p not in base:raise ValueError('Missing material/texture dependency: '+p)
                    continue
                queue.extend(refs(f))
                target=game/p;target.parent.mkdir(parents=True,exist_ok=True)
                digest=sha(f)
                if target.exists() and sha(target)!=digest:raise ValueError('Resource path conflict: '+p)
                if not target.exists():shutil.copy2(f,target)
                if sha(target)!=digest:raise ValueError('Copy checksum mismatch: '+p)
                all_copies[p]=digest
            check=validate(dest,original,canon,game,base)
            dmx_proof=[]
            for name,raw in original_dmx.items():
                expected=raw
                for old,new in rename.items():expected=expected.replace(b'\0'+old.encode()+b'\0',b'\0'+new.encode()+b'\0')
                actual=(dest.parent/name).read_bytes();valid=actual==expected and len(actual)==len(raw)
                dmx_proof.append({'File':name,'Bytes':len(raw),'OnlyCanonicalNameBytesChanged':valid})
            if not all(x['OnlyCanonicalNameBytesChanged'] for x in dmx_proof):check['Failures'].append('DMX numeric payload changed')
            old_p=old_bones['pelvis'];new_tree=parse_kv3(dest.read_text());nb,_=skeleton(new_tree)
            rm=nb['root_motion'];rot=porter.angle_matrix(*rm['angles'])
            position=[sum(rot[i][j]*nb['pelvis']['origin'][j] for j in range(3))+rm['origin'][i] for i in range(3)]
            pos_error=max(abs(a-b) for a,b in zip(position,old_p['origin']))
            old_rot=porter.angle_matrix(*old_p['angles']);new_rot=porter.angle_matrix(*nb['pelvis']['angles'])
            angle_error=max(abs(sum(rot[i][k]*new_rot[k][j] for k in range(3))-old_rot[i][j]) for i in range(3) for j in range(3))
            if pos_error>1e-4 or angle_error>1e-6:check['Failures'].append('Pelvis world-space rest transform changed')
            check['StaticSourcePassed']=not check['Failures']
            result.update(check);result.update(SourceConverted=True,Changes=changes,BoneRenames=rename,OriginalBones=len(old_bones),MaterialDependencies=sorted(dependencies))
            result.update(DMXPayloadChecks=dmx_proof,PelvisWorldPositionError=pos_error,PelvisRotationMatrixError=angle_error)
            result['State']='source_converted_static_pass_compile_required' if check['StaticSourcePassed'] else 'source_converted_static_failed'
            # Actual authored sources stay private, including the .vmdl backup.
            project=output/'models'/ident;project.mkdir(parents=True)
            (project/'project.json').write_text(json.dumps({'Id':ident,'ModelDoc':dest.relative_to(output).as_posix(),'CompiledDestination':(game/(rel+'_c')).relative_to(output).as_posix(),'OriginalSHA256':row['OriginalSHA256'],'State':result['State']},indent=2))
        except Exception as e:
            result.update(State='failed',Error=str(e))
        (reports/(ident+'-result.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2))
        results.append(result)
        print(ident,result.get('State'),result.get('Failures',result.get('Error')))
    (reports/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
    (reports/'preserved-assets.json').write_text(json.dumps(all_copies,indent=2))
    (content/'addoninfo.txt').write_text('"addoninfo"\n{\n "addontitle" "KS AG2 repair isolated test"\n "addonauthor" "HifumiDaisuki01"\n "addonversion" "0.1"\n}\n')
    return results

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['source','manifest','base-list','cli','vendor','canonical','output']:p.add_argument('--'+name,required=True)
    a=p.parse_args()
    result=prepare(a.source,a.manifest,a.base_list,a.cli,a.vendor,a.canonical,a.output)
    raise SystemExit(0 if len(result)==3 and all(x.get('StaticSourcePassed') for x in result) else 1)
