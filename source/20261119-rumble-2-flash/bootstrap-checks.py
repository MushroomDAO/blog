from pathlib import Path
p=Path(__file__).parent;old=p.parent/'20261118-cheetah';slug='rumble-2-flash-small-asr-phone-call-benchmarks'
for name in ['check.py','verify-public.py','verify-preserved.py','verify-wechat.cjs','wechat-content-canonical.py','remote-preflight.cjs','check-semantic.py','mine-kb.py','verify-kb.py','compress-figures.py']:
 s=(old/name).read_text().replace('cheetah-rust-local-llm-memory-loading-guide',slug).replace('fa73ba12-661b-435d-998e-261312844620','00613c57-ed07-4b19-8cfd-1fe57eff41a9').replace('DA3M0\\/Cheetah','Reson8\\/Rumble-2-Flash').replace('Cheetah：','Rumble-2-Flash：').replace('Cheetah Rust mmap 本地模型 权重加载 62MB 空闲 RSS','Rumble-2-Flash Reson8 小模型 电话语音识别 H200 批处理')
 if name=='verify-preserved.py':s=s.replace("slugs=['copilotkit", "slugs=['cheetah-rust-local-llm-memory-loading-guide','copilotkit")
 (p/name).write_text(s)
