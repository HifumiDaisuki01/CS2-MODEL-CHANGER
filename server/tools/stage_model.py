#!/usr/bin/env python3
"""Validate a downloaded model VPK and stage merged configs; never change a live server."""
import argparse, json, pathlib, re
from verify_vpk import inspect

def stage(args):
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,47}', args.id): raise ValueError('Invalid model identifier')
    if not re.fullmatch(r'[1-9][0-9]{0,19}', args.workshop): raise ValueError('Invalid Workshop ID')
    model=args.model.removesuffix('_c')
    if not model.startswith(('characters/', 'phase2/characters/')) or not model.endswith('.vmdl') or '..' in model or '\\' in model:
        raise ValueError('Expected a canonical characters/ or phase2/characters/ .vmdl path')
    report=inspect(args.vpk)
    if model+'_c' not in {entry['Path'] for entry in report['Entries']}: raise ValueError('Model not found in this VPK (paths are case sensitive)')
    config=json.loads(pathlib.Path(args.config).read_text(encoding='utf-8-sig'))
    models=config.setdefault('Models', {})
    entry={'name':args.name,'path':model,'permissions':[],'permissionsOr':[],'side':'All','disableleg':False,'hideinmenu':False}
    if args.id in models and models[args.id].get('path')!=model: raise ValueError('Existing identifier has another path; choose a new identifier')
    if args.id not in models: models[args.id]=entry
    catalog=json.loads(pathlib.Path(args.catalog).read_text(encoding='utf-8-sig')) if args.catalog else {'Archives':{},'Models':[]}
    catalog.setdefault('Archives',{}).update(report['ArchiveSHA256'])
    catalog['Models']=sorted(set(catalog.get('Models',[]))|{model})
    mam=pathlib.Path(args.mam_config).read_text(encoding='utf-8-sig')
    pattern=r'(?m)^(\s*mm_extra_addons\s+)"([0-9,\s]*)"([^\r\n]*)$'
    matches=list(re.finditer(pattern,mam))
    if len(matches)>1: raise ValueError('Multiple mm_extra_addons assignments; resolve the effective config first')
    if matches:
        match=matches[0];ids=[i.strip() for i in match[2].split(',') if i.strip()]
        if args.workshop not in ids: ids.append(args.workshop)
        mam=mam[:match.start()]+match[1]+'"'+','.join(ids)+'"'+match[3]+mam[match.end():]
    else: mam+='\nmm_extra_addons "'+args.workshop+'"\n'
    out=pathlib.Path(args.output).resolve()
    sources=[pathlib.Path(p).resolve() for p in [args.config,args.mam_config,args.vpk]+([args.catalog] if args.catalog else [])]
    if any(p.is_relative_to(out) for p in sources): raise ValueError('Output must be separate from source/live config directories')
    if out.exists() and any(out.iterdir()): raise ValueError('Use an empty staging output directory')
    out.mkdir(parents=True,exist_ok=True)
    for name,data in [('PlayerModelChanger.json',config),('resource-catalog.json',catalog),('vpk-validation.json',report)]:
        (out/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    (out/'multiaddonmanager.cfg').write_text(mam)
    print('STAGED',args.id,'files at',out,'; live server unchanged; dependency and client tests still required')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['id','name','workshop','model','vpk','config','mam-config','output']: parser.add_argument('--'+name,required=True)
    parser.add_argument('--catalog');stage(parser.parse_args())
