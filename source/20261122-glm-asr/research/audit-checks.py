from pathlib import Path
import json,unittest
p=Path(__file__).parent
class MetadataChecks(unittest.TestCase):
 def test_complete_weight_elements(self):
  a=json.loads((p/'model-api.json').read_text());w=json.loads((p/'weight-audit.json').read_text());self.assertEqual(w['totalElements'],a['safetensors']['total']);self.assertEqual(w['totalElements'],2257843200)
 def test_weight_bytes_and_digest(self):
  a=json.loads((p/'model-api.json').read_text());w=json.loads((p/'weight-audit.json').read_text());f=next(x for x in a['siblings']if x['rfilename']=='model.safetensors');self.assertEqual(w['bytes'],f['size']);self.assertEqual(w['sha256'],f['lfs']['sha256'])
 def test_source_benchmark_arithmetic(self):
  glm=[6.73,1.81,2,4.19,5.78];whisper=[18.39,4.72,1.86,3.43,6.23];self.assertEqual(round(sum(glm)/5,2),4.10);self.assertEqual(round(sum(whisper)/5,2),6.93);self.assertEqual(sum(a<b for a,b in zip(glm,whisper)),3)
 def test_encoder_decoder_and_sampling(self):
  c=json.loads((p/'config.json').read_text());f=json.loads((p/'processor_config.json').read_text());self.assertEqual(c['audio_config']['num_hidden_layers'],32);self.assertEqual(c['text_config']['num_hidden_layers'],28);self.assertEqual(f['feature_extractor']['sampling_rate'],16000)
if __name__=='__main__':unittest.main(verbosity=2)
