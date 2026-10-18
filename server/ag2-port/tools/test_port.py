import io,json,os,struct,tempfile,unittest
from pathlib import Path
from port_projects import safe_relative,refs,canonical,prepare
from validate_source import parse_kv3,skeleton,compare_geometry,read_dmx,validate

class GuardAndParserTests(unittest.TestCase):
 def test_real_kv3_structure_and_resources(self):
  t=parse_kv3('<!-- kv3 test -->\n{ root = { _class = "Skeleton" children = [ { _class = "Bone" name = "root_motion" children = [ { _class = "Bone" name = "pelvis" origin = [0,42,-2] } ] } ] } resource = resource:"a/b.vmat" enabled = true }')
  bones,parents=skeleton(t);self.assertEqual(parents,{'root_motion':None,'pelvis':'root_motion'});self.assertEqual(t['resource'],'a/b.vmat');self.assertTrue(t['enabled'])
 def test_duplicate_and_truncated_sources_rejected(self):
  for text in ['{ a=1 a=2 }','{ a=[1,2','{ a=1 } unexpected']:
   with self.assertRaises((ValueError,IndexError)):parse_kv3(text)
 def test_unsafe_resource_paths_rejected(self):
  for path in ['../model.vmdl','/tmp/model.vmdl','C:/model.vmdl','characters//model.vmdl','characters/./model.vmdl','characters\\model.vmdl']:
   with self.assertRaises(ValueError):safe_relative(path)
  self.assertEqual(safe_relative('characters/models/a/a.vmdl'),'characters/models/a/a.vmdl')
 def test_original_tree_cannot_be_used_as_output(self):
  with tempfile.TemporaryDirectory() as d:
   source=Path(d)/'input';source.mkdir()
   with self.assertRaises(ValueError):prepare(source,'missing','missing','missing','missing','missing',source/'out')
   self.assertEqual(list(source.iterdir()),[])
 def test_rerl_reader_and_corruption(self):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/'resource.vmat_c';name=b'materials/a.vtex\0';rerl=struct.pack('<II',8,1)+struct.pack('<Qq',123,8)+name
   b=struct.pack('<IHHII',28+len(rerl),12,1,8,1)+b'RERL'+struct.pack('<II',8,len(rerl))+rerl;f.write_bytes(b)
   self.assertEqual(refs(f),['materials/a.vtex_c'])
   corrupt=bytearray(b);struct.pack_into('<q',corrupt,44,999999);f.write_bytes(corrupt)
   with self.assertRaises((ValueError,struct.error)):refs(f)
 def test_physics_shape_name_and_geometry_changes_not_hidden(self):
  old={'_class':'PhysicsShapeSphere','name':'hand_l','parent_bone':'hand_l','radius':2.0}
  alias=dict(old,parent_bone='hand_L');self.assertTrue(compare_geometry(old,alias)['NamesAndNumericGeometryPreserved'])
  self.assertFalse(compare_geometry(old,dict(alias,radius=2.5))['NamesAndNumericGeometryPreserved'])
  self.assertFalse(compare_geometry(old,dict(alias,name='hand_L'))['NamesAndNumericGeometryPreserved'])
 def test_nonempty_dmx9_prefix_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/'x.dmx';f.write_bytes(b'<!-- dmx encoding binary 9 format model 22 -->\n\0'+struct.pack('<I',1))
   with self.assertRaises(ValueError):read_dmx(f)

@unittest.skipUnless(os.environ.get('AG2_DELIVERY'),'Private model fixtures are not redistributed in Git')
class ConvertedModelTests(unittest.TestCase):
 def setUp(self):
  self.root=Path(os.environ['AG2_DELIVERY']);self.content=self.root/'workshop-addon/content/csgo_addons/ks_ag2_repair';self.game=self.root/'workshop-addon/game/csgo_addons/ks_ag2_repair'
  self.rows=json.loads((self.root/'reports/results.json').read_text());self.canon=canonical(os.environ['AG2_CANONICAL']);self.base=set(Path(os.environ['AG2_BASE']).read_text().splitlines())
 def test_all_three_real_converted_sources(self):
  self.assertEqual(len(self.rows),3)
  for row in self.rows:
   with self.subTest(model=row['Id']):
    r=validate(self.content/row['Path'],self.root/'reports'/(row['Id']+'-original.vmdl'),self.canon,self.game,self.base)
    self.assertTrue(r['StaticSourcePassed'],r['Failures']);self.assertEqual(r['CriticalBonesPresent'],24);self.assertFalse(r['ParentDifferences']);self.assertTrue(r['Geometry']['NamesAndNumericGeometryPreserved']);self.assertFalse(r['Compiled']);self.assertTrue(any(d['WeightedJointCount']>0 for d in r['DMX']))
    self.assertTrue(all(not d['UnresolvedWeightedJoints'] for d in r['DMX']))
    self.assertTrue(all(x['OnlyCanonicalNameBytesChanged'] for x in row['DMXPayloadChecks']))
 def test_missing_materials_block_delivery(self):
  with tempfile.TemporaryDirectory() as d:
   row=self.rows[0];r=validate(self.content/row['Path'],self.root/'reports'/(row['Id']+'-original.vmdl'),self.canon,d,self.base)
   self.assertFalse(r['StaticSourcePassed']);self.assertTrue(r['MissingMaterials'])

if __name__=='__main__':unittest.main(verbosity=2)
