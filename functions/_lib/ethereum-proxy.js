const DEFAULT_TARGET = 'https://ethereum-research-bot.pages.dev';

/**
 * Handle proxy requests for /ethereum and /ethereum/*
 *
 * @param {EventContext<any, any, any>} context
 * @returns {Promise<Response>}
 */
export async function handleEthereumProxy(context) {
	const request = context.request;
	const url = new URL(request.url);

	// Enforce trailing slash on /ethereum so relative asset paths (./styles.css) resolve under /ethereum/
	if (url.pathname === '/ethereum') {
		return new Response(null, {
			status: 301,
			headers: {
				Location: `/ethereum/${url.search}`,
			},
		});
	}

	const targetOrigin = (context.env?.ETHEREUM_RESEARCH_BOT_URL || DEFAULT_TARGET).replace(/\/+$/, '');
	const targetPath = url.pathname.replace(/^\/ethereum/, '') || '/';
	const targetUrl = new URL(targetPath + url.search, targetOrigin);

	const forwardHeaders = new Headers(request.headers);
	forwardHeaders.delete('host');

	const init = {
		method: request.method,
		headers: forwardHeaders,
		redirect: 'manual',
	};

	if (request.method !== 'GET' && request.method !== 'HEAD') {
		init.body = request.body;
	}

	let response;
	try {
		response = await fetch(targetUrl.toString(), init);
	} catch (err) {
		return new Response(`Bad Gateway: Failed to fetch upstream (${err.message})`, {
			status: 502,
			headers: { 'content-type': 'text/plain; charset=utf-8' },
		});
	}

	// Rewrite upstream redirects to remain within /ethereum
	if (response.status >= 300 && response.status < 400 && response.headers.has('location')) {
		let location = response.headers.get('location');
		if (location.startsWith(targetOrigin)) {
			location = location.slice(targetOrigin.length);
		}
		if (location.startsWith('/')) {
			location = `/ethereum${location}`;
		}
		const newHeaders = new Headers(response.headers);
		newHeaders.set('location', location);
		return new Response(response.body, {
			status: response.status,
			statusText: response.statusText,
			headers: newHeaders,
		});
	}

	return response;
}
