import { handleTopicProxy } from '../_lib/topic-proxy.js';

export async function onRequest(context) {
	return handleTopicProxy(context);
}
