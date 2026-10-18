import contextlib, io, json, pathlib, struct, tempfile, types, unittest, zlib
from verify_vpk import inspect
from stage_model import stage

class ModelToolsTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def fixture(self,external=False):
        path=self.root/'addon_dir.vpk';body=b'hello';pre=body[:2];tail=body[2:]
        tree=b'vmdl_c\0characters/models/test\0test\0'+struct.pack('<IHHIIH',zlib.crc32(body),len(pre),0 if external else 0x7fff,0,len(tail),0xffff)+pre+b'\0\0\0'
        path.write_bytes(struct.pack('<IIIIIII',0x55aa1234,2,len(tree),0 if external else len(tail),0,0,0)+tree+(b'' if external else tail))
        if external:(self.root/'addon_000.vpk').write_bytes(tail)
        return path
    def arguments(self):
        vpk=self.fixture();config=self.root/'models.json';config.write_text(json.dumps({'StorageType':'sqlite','Untouched':42,'Models':{'existing':{'path':'characters/old.vmdl'}}}))
        catalog=self.root/'catalog.json';catalog.write_text(json.dumps({'Archives':{'old_dir.vpk':'existing-hash'},'Models':['characters/old.vmdl']}))
        mam=self.root/'mam.cfg';mam.write_text('mm_extra_addons "123" // keep\nmm_client_extra_addons "999"\nmm_addon_debug 0\n')
        return types.SimpleNamespace(id='test',name='Test',workshop='3821951835',model='characters/models/test/test.vmdl_c',vpk=str(vpk),config=str(config),catalog=str(catalog),mam_config=str(mam),output=str(self.root/'staged'))
    def test_inline_crc_and_preload(self):
        result=inspect(self.fixture());self.assertTrue(result['AllEntryCRCsValid']);self.assertEqual(result['Entries'][0]['Bytes'],5)
    def test_split_archive(self):
        self.assertEqual(len(inspect(self.fixture(True))['ArchiveSHA256']),2)
    def test_corrupt_payload(self):
        path=self.fixture();path.write_bytes(path.read_bytes()[:-1]+b'!')
        with self.assertRaises(ValueError):inspect(path)
    def test_missing_chunk(self):
        path=self.fixture(True);(self.root/'addon_000.vpk').unlink()
        with self.assertRaises(FileNotFoundError):inspect(path)
    def test_merge_preserves_previous_models_and_no_live_writes(self):
        args=self.arguments();before=pathlib.Path(args.config).read_bytes()
        with contextlib.redirect_stdout(io.StringIO()):stage(args)
        out=pathlib.Path(args.output);models=json.loads((out/'PlayerModelChanger.json').read_text());catalog=json.loads((out/'resource-catalog.json').read_text())
        self.assertEqual(models['Untouched'],42);self.assertIn('existing',models['Models']);self.assertEqual(models['Models']['test']['path'],'characters/models/test/test.vmdl')
        self.assertIn('old_dir.vpk',catalog['Archives']);self.assertIn('characters/old.vmdl',catalog['Models'])
        mam=(out/'multiaddonmanager.cfg').read_text();self.assertIn('"123,3821951835" // keep',mam);self.assertIn('mm_client_extra_addons "999"',mam)
        self.assertEqual(pathlib.Path(args.config).read_bytes(),before)
    def test_reject_wrong_model_without_writing(self):
        args=self.arguments();args.model='characters/absent.vmdl'
        with self.assertRaises(ValueError):stage(args)
        self.assertFalse(pathlib.Path(args.output).exists())
    def test_output_cannot_overwrite_live_source(self):
        args=self.arguments();args.output=str(self.root)
        with self.assertRaises(ValueError):stage(args)
    def test_reject_duplicate_mam_assignments(self):
        args=self.arguments();pathlib.Path(args.mam_config).write_text('mm_extra_addons "1"\nmm_extra_addons "2"\n')
        with self.assertRaises(ValueError):stage(args)

if __name__=='__main__':unittest.main()
