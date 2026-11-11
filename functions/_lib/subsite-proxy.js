/**
 * Factory for creating a reverse proxy handler to an external Cloudflare Pages site.
 *
 * @param {Object} options
 * @param {string} options.prefix Path prefix without leading/trailing slashes, e.g. 'ethereum' or 'agent'
 * @param {string} options.defaultTarget Default upstream origin URL, e.g. 'https://ethereum-research-bot.pages.dev'
 * @param {string} [options.envKey] Optional environment variable name to override the target URL
 * @returns {(context: any) => Promise<Response>}
 */
export function createSubsiteProxy({ prefix, defaultTarget, envKey }) {
	const baseNoSlash = `/${prefix}`;
	const baseWithSlash = `/${prefix}/`;
	const prefixRegex = new RegExp(`^/${prefix}`);

	return async function handleProxy(context) {
		const request = context.request;
		const url = new URL(request.url);

		// Enforce trailing slash on base path so relative asset paths (./styles.css) resolve under /{prefix}/
		if (url.pathname === baseNoSlash) {
			return new Response(null, {
				status: 301,
				headers: {
					Location: `${baseWithSlash}${url.search}`,
				},
			});
		}

		const targetOrigin = (envKey && context.env?.[envKey] ? context.env[envKey] : defaultTarget).replace(/\/+$/, '');
		const targetPath = url.pathname.replace(prefixRegex, '') || '/';
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

		// Rewrite upstream redirects to remain within /{prefix}/
		if (response.status >= 300 && response.status < 400 && response.headers.has('location')) {
			let location = response.headers.get('location');
			if (location.startsWith(targetOrigin)) {
				location = location.slice(targetOrigin.length);
			}
			if (location.startsWith('/')) {
				location = `/${prefix}${location}`;
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
	};
}
