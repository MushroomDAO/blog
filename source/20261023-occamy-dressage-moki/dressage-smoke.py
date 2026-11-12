"""Run four fixture-free upstream control tests, not the complete pytest suite."""
import pathlib,runpy,sys
root=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/mycelium-dressage-20261023')
sys.path.insert(0,str(root))
module=runpy.run_path(str(root/'tests/test_resume_readiness_simple.py'))
for name in ['test_sglang_router_client_wait_until_ready_uses_workers_health','test_generation_controller_resume_keeps_paused_when_backend_not_ready','test_generation_controller_resume_releases_after_backend_ready','test_generation_controller_skips_zero_output_preempt_routed_experts']:
 module[name]();print('PASS',name)
print('4 source functions passed with mock HTTP; no GPU or RL training.')
