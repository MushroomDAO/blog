import { handleAgentProxy } from '../_lib/agent-proxy.js';

export async function onRequest(context) {
	return handleAgentProxy(context);
}
