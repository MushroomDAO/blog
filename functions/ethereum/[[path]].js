import { handleEthereumProxy } from '../_lib/ethereum-proxy.js';

export async function onRequest(context) {
	return handleEthereumProxy(context);
}
