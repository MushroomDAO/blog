from pathlib import Path
import json,sys,subprocess
r=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/openarch-research')
def read(p):return (r/p).read_text()
c=read('server/openarch-app/docker-compose.yml');root=read('docker-compose.yml');q=next(r.rglob('EmbeddingQueryDTO.java')).read_text();api=next(r.rglob('QueryAPI.java')).read_text();policy=next(r.rglob('HXQLQueryConverter.java')).read_text();pom=read('pom.xml')
checks={'apache2_declared':'Apache 2.0' in read('README.md'),'compose_include':'include:' in root,'mongo_replica_set':'--replSet' in c,'mongo_tmpfs':'type: tmpfs' in c,'opensearch_security_disabled':'plugins.security.disabled=true' in c,'opensearch_no_data_mount':'volumes:' not in c.split('  opensearch:')[1].split('  opensearch-dashboards:')[0],'debug_port_exposed':'5005:5005' in root,'default_password_documented':'{noop}' in read('docs/DEFAULT_USERS.md'),'java25':'<maven.compiler.target>25' in pom,'embedding_vector_required':'if (vector == null)' in q,'hybrid_chunkfts':'String chunkFTS' in q,'security_policy_in_query':'securityPolicyService.addSecurityPolicies' in policy,'vector_endpoint':'@PostMapping("/embeddings")' in api,'repository_sync_route':'return sync ? rqm : osqm' in api}
report={'commit':subprocess.check_output(['git','-C',str(r),'rev-parse','HEAD'],text=True).strip(),'scope':'Static source/config assertions only; no Docker executable, no runtime/security/performance validation','checks':checks,'passed':sum(checks.values()),'total':len(checks)}
print(json.dumps(report,indent=2));assert all(checks.values())
