import { handleJidanProxy } from '../_lib/jidan-proxy.js';

export async function onRequest(context) {
	return handleJidanProxy(context);
}
