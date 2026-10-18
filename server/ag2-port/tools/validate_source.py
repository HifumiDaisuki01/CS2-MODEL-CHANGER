"""Fail-closed ModelDoc/DMX checks. This never claims compilation or gameplay success."""
import io, json, re, struct
from pathlib import Path

TOKEN = re.compile(r'\s+|//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|[{}\[\]=,:]|[^\s{}\[\]=,:]+', re.S)

def parse_kv3(text):
    text = re.sub(r'^\ufeff?\s*<!--.*?-->', '', text, count=1, flags=re.S)
    tokens = [m.group() for m in TOKEN.finditer(text) if not m.group().isspace() and not m.group().startswith(('//', '/*'))]
    pos = 0
    def pop():
        nonlocal pos
        if pos >= len(tokens): raise ValueError('Truncated KV3')
        t = tokens[pos]; pos += 1; return t
    def scalar(t):
        if t.startswith('"'): return json.loads(t)
        if t == 'true': return True
        if t == 'false': return False
        if t == 'null': return None
        try: return float(t) if any(c in t for c in '.eE') else int(t)
        except ValueError: return t
    def value():
        t = pop()
        if t == '{':
            out = {}
            while tokens[pos] != '}':
                if tokens[pos] == ',': pop(); continue
                key = scalar(pop())
                if pop() != '=': raise ValueError('Expected KV3 assignment')
                if key in out: raise ValueError('Duplicate KV3 key: '+str(key))
                out[key] = value()
            pop(); return out
        if t == '[':
            out = []
            while tokens[pos] != ']':
                if tokens[pos] == ',': pop(); continue
                out.append(value())
            pop(); return out
        if t in ['}', ']', '=', ',']: raise ValueError('Unexpected KV3 token '+t)
        if pos < len(tokens) and tokens[pos] == ':': pop(); return value()
        return scalar(t)
    result = value()
    if pos != len(tokens): raise ValueError('Trailing KV3 tokens')
    return result

def nodes(tree):
    if isinstance(tree, dict):
        yield tree
        for v in tree.values(): yield from nodes(v)
    elif isinstance(tree, list):
        for v in tree: yield from nodes(v)

def skeleton(tree):
    result = {}; parents = {}
    def visit(n, parent=None):
        if not isinstance(n, dict): return
        if n.get('_class') == 'Bone':
            name = n['name']
            if name in result: raise ValueError('Duplicate skeleton bone '+name)
            result[name] = n; parents[name] = parent; parent = name
        for c in n.get('children', []): visit(c, parent)
    for n in nodes(tree):
        if n.get('_class') == 'Skeleton': visit(n)
    return result, parents

def read_dmx(path):
    """Use srctools with explicit binary9 prefix/array adaptation, in memory only.

    Source2Viewer's writer uses binary9: a prefix count and array offset32.
    srctools2.7 understands the scalar payloads here, but assumes the old offset14.
    Reject nonzero prefix metadata or unsupported scalar types instead of skipping them.
    """
    import srctools.dmx as dmx
    raw = Path(path).read_bytes()
    if not raw.startswith(b'<!-- dmx encoding binary 9 format model 22 -->\n\0'):
        raise ValueError('Expected Source2Viewer DMX binary9 model22')
    p = raw.index(b'-->') + 5
    if struct.unpack_from('<I', raw, p)[0] != 0: raise ValueError('Nonempty DMX9 prefix unsupported')
    adapted = raw[:p] + raw[p+4:]
    old = dmx.ARRAY_OFFSET
    try:
        dmx.ARRAY_OFFSET = 32
        stream = io.BytesIO(adapted)
        elem, fmt, ver = dmx.Element.parse(stream, unicode=True)
        if stream.tell() != len(adapted): raise ValueError('Unconsumed DMX bytes')
        return elem
    finally: dmx.ARRAY_OFFSET = old

def dmx_elements(root):
    from srctools.dmx import ValueType
    seen = set(); todo = [root]
    while todo:
        e = todo.pop()
        if id(e) in seen: continue
        seen.add(id(e)); yield e
        for attr in e.values():
            if attr.type is ValueType.ELEMENT:
                todo.extend(attr.iter_elem() if attr.is_array else [attr.val_elem])

def check_dmx(path, bones):
    root = read_dmx(path); all_elem = list(dmx_elements(root))
    skel = root['skeleton'].val_elem
    joints = [e.name for e in skel['jointList'].iter_elem()]
    missing_all = sorted(set(joints)-set(bones))
    used = set(); streams = 0; failures = []
    for e in all_elem:
        if e.type != 'DmeVertexData': continue
        index_name=next((key for key in ['jointIndices','blendindices$0'] if key in e),None)
        weight_name=next((key for key in ['jointWeights','blendweights$0'] if key in e),None)
        if index_name is None:continue
        indices = list(e[index_name].iter_int())
        weights = list(e[weight_name].iter_float()) if weight_name else []
        streams += 1
        if len(indices) != len(weights): failures.append('Joint index/weight length mismatch'); continue
        for i, w in zip(indices, weights):
            if abs(w) <= 1e-8: continue
            if i < 0 or i >= len(joints): failures.append('Skin joint index out of range'); continue
            used.add(joints[i])
    unresolved = sorted(used-set(bones))
    if unresolved: failures.append('Weighted joints absent from ModelDoc skeleton')
    if any(e.type=='DmeMesh' for e in all_elem) and not streams:failures.append('Render mesh has no recognized skin stream')
    materials = sorted({e['mtlName'].val_string for e in all_elem if e.type == 'DmeMaterial' and 'mtlName' in e})
    return {'File':Path(path).name,'JointListCount':len(joints),'WeightedJointCount':len(used),'SkinStreams':streams,
            'UnresolvedWeightedJoints':unresolved,'UnweightedOrHelperNames':missing_all,'Materials':materials,'Failures':failures}

def compare_geometry(before, after):
    """Physics/hitbox shape names and numeric geometry must survive conversion."""
    classes = {'PhysicsShapeCapsule','PhysicsShapeSphere','PhysicsShapeBox','PhysicsShapeHull','HitboxCapsule','HitboxSphere','HitboxBox'}
    def signature(n):
        if isinstance(n,list):return [signature(v) for v in n]
        if not isinstance(n,dict):return n
        result={k:signature(v) for k,v in n.items() if k not in ['parent_bone','bone_name','bone','children']}
        if 'weight' in result and isinstance(result.get('name'),str):
            result['name']=re.sub(r'_([lr])$',lambda m:'_'+m[1].upper(),result['name'])
        return result
    old = [signature(n) for n in nodes(before) if n.get('_class') in classes]
    new = [signature(n) for n in nodes(after) if n.get('_class') in classes]
    return {'ShapeCountBefore':len(old),'ShapeCountAfter':len(new),'NamesAndNumericGeometryPreserved':old == new}

def validate(vmdl, original, canonical, game_root, base_resources):
    after = parse_kv3(Path(vmdl).read_text()); before = parse_kv3(Path(original).read_text())
    bones, parents = skeleton(after); expected = dict(canonical)
    critical = ['root_motion','pelvis','spine_0','spine_1','spine_2','spine_3','neck_0','head_0','clavicle_L','clavicle_R',
                'arm_upper_L','arm_upper_R','arm_lower_L','arm_lower_R','hand_L','hand_R','leg_upper_L','leg_upper_R','leg_lower_L','leg_lower_R','ankle_L','ankle_R','wpnPivot','wpn']
    fail = []; warnings = []
    absent = [b for b in critical if b not in bones]
    if absent: fail.append('Missing critical bones: '+','.join(absent))
    parent_bad = {b:{'Expected':p,'Actual':parents[b]} for b,p in expected.items() if b in bones and parents[b] != p}
    core_bad = {b:p for b,p in parent_bad.items() if b in critical}
    if core_bad: fail.append('Critical parent mismatch')
    if parent_bad and not core_bad: warnings.append('Non-core parent differences require finger checks')
    classes = [n.get('_class') for n in nodes(after)]
    if classes.count('AnimGraph2List') != 1 or classes.count('NmSkeletonList') != 1: fail.append('Missing or duplicate AG2 list')
    graph_refs = [n.get('filename') for n in nodes(after) if n.get('_class') in ['DefaultAnimGraph2','AnimGraph2']]
    skel_refs = [n.get('filename') for n in nodes(after) if n.get('_class') == 'NmSkeletonReference']
    if len(graph_refs)!=4 or len(skel_refs)!=2: fail.append('Wrong graph/skeleton reference counts')
    legacy = [str(v) for n in nodes(after) for v in n.values() if isinstance(v,str) and ('.vanmgrph' in v or 'animsets/animset_' in v)]
    if legacy: fail.append('Legacy animation dependencies remain')
    bone_fields={'parent_bone','bone','bone_name','anklebone','toebone','start_bone','end_bone'}
    unresolved_bones=[{'Class':n.get('_class'),'Field':k,'Bone':v} for n in nodes(after) for k,v in n.items() if k in bone_fields and isinstance(v,str) and v and v not in bones]
    if unresolved_bones:fail.append('Unresolved explicit bone references')
    missing_base = [p for p in graph_refs+skel_refs if p+'_c' not in base_resources]
    if missing_base: fail.append('AG2 original-game dependencies not confirmed')
    pelvis = bones.get('pelvis',{}).get('origin',[])
    if len(pelvis)!=3 or abs(pelvis[1])<abs(pelvis[2]): fail.append('Pelvis transform is not Y-up')
    geo = compare_geometry(before,after)
    if not geo['NamesAndNumericGeometryPreserved']: fail.append('Physics/hitbox numeric geometry changed')
    dmx = [check_dmx(p,bones) for p in sorted(Path(vmdl).parent.glob('*.dmx'))]
    if not dmx: fail.append('No DMX geometry/animation files')
    for d in dmx:
        if d['Failures']: fail.append('DMX failure: '+d['File'])
    referenced_files = [n.get('filename') for n in nodes(after) if n.get('_class') in ['RenderMeshFile','AnimFile']]
    missing_sources=[]
    for p in referenced_files:
        if not p: continue
        # Source files use addon-relative paths, not OS absolute paths.
        addon_content=Path(vmdl)
        while addon_content.name!='ks_ag2_repair' and addon_content.parent!=addon_content: addon_content=addon_content.parent
        if not (addon_content/p).is_file() and not (Path(vmdl).parent/p).is_file(): missing_sources.append(p)
    if missing_sources: fail.append('ModelDoc mesh or animation source missing')
    mat_refs=sorted({p for d in dmx for p in d['Materials']})
    missing_mats=[]
    for p in mat_refs:
        p=p.removesuffix('_c')
        if not p.endswith('.vmat'):p+='.vmat'
        if not (Path(game_root)/(p+'_c')).is_file() and p+'_c' not in base_resources: missing_mats.append(p)
    if missing_mats: fail.append('Material files missing')
    return {'StaticSourcePassed':not fail,'Compiled':False,'Mounted':False,'GameAnimationVerified':False,'Failures':fail,'Warnings':warnings,
            'SourceBoneCount':len(bones),'CriticalBonesPresent':24-len(absent),'MissingCore':absent,'ParentDifferences':parent_bad,'UnresolvedBoneReferences':unresolved_bones,
            'PelvisOrigin':pelvis,'Graphs':graph_refs,'Skeletons':skel_refs,'MissingBaseResources':missing_base,'LegacyReferences':legacy,
            'DMX':dmx,'Materials':mat_refs,'MissingMaterials':missing_mats,'MissingSourceFiles':missing_sources,'Geometry':geo}
