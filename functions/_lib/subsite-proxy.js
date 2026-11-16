/**
 * Factory for creating a reverse proxy handler to an external Cloudflare Pages site.
 *
 * @param {Object} options
 * @param {string} options.prefix Path prefix without leading/trailing slashes, e.g. 'ethereum', 'agent', 'topic'
 * @param {string} options.defaultTarget Default upstream origin URL, e.g. 'https://topic-research.pages.dev'
 * @param {string} [options.envKey] Optional environment variable name to override the target URL
 * @returns {(context: any) => Promise<Response>}
 */
export function createSubsiteProxy({ prefix, defaultTarget, envKey }) {
	const baseNoSlash = `/${prefix}`;
	const baseWithSlash = `/${prefix}/`;
	const prefixRegex = new RegExp(`^/${prefix}`);

	function rewriteUrl(val) {
		if (!val || typeof val !== 'string') return val;
		if (
			val.startsWith('http://') ||
			val.startsWith('https://') ||
			val.startsWith('//') ||
			val.startsWith('#') ||
			val.startsWith('javascript:') ||
			val.startsWith('mailto:') ||
			val.startsWith('data:')
		) {
			return val;
		}
		if (val.startsWith('/')) {
			if (val.startsWith(baseWithSlash) || val === baseNoSlash) {
				return val;
			}
			return `/${prefix}${val}`;
		}
		return val;
	}

	class AttributeRewriter {
		constructor(attributeName) {
			this.attributeName = attributeName;
		}
		element(el) {
			const attr = el.getAttribute(this.attributeName);
			if (attr) {
				el.setAttribute(this.attributeName, rewriteUrl(attr));
			}
		}
	}

	class InputNextRewriter {
		element(el) {
			const name = el.getAttribute('name');
			const value = el.getAttribute('value');
			if (name === 'next' && value && value.startsWith('/')) {
				el.setAttribute('value', rewriteUrl(value));
			}
		}
	}

	class RobotsMetaRewriter {
		element(el) {
			const content = el.getAttribute('content') || '';
			if (content.toLowerCase().includes('noindex')) {
				el.setAttribute('content', 'index, follow, max-image-preview:large');
			}
		}
	}

	return async function handleProxy(context) {
		const request = context.request;
		const url = new URL(request.url);

		// Enforce trailing slash on base path so relative asset paths (./styles.css) resolve under /{prefix}/
		if (url.pathname === baseNoSlash) {
			return new Response(null, {
				status: 301,
				headers: {
					Location: `${baseWithSlash}${url.search}`,
					'X-Robots-Tag': 'index, follow',
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

		// Rewrite upstream redirects to remain within /{prefix}/ and strip noindex
		if (response.status >= 300 && response.status < 400 && response.headers.has('location')) {
			let location = response.headers.get('location');
			if (location.startsWith(targetOrigin)) {
				location = location.slice(targetOrigin.length);
			}
			if (location.startsWith('/')) {
				location = `/${prefix}${location}`;
			}
			const redirectHeaders = new Headers(response.headers);
			redirectHeaders.delete('x-robots-tag');
			redirectHeaders.set('X-Robots-Tag', 'index, follow');
			redirectHeaders.set('location', location);
			return new Response(response.body, {
				status: response.status,
				statusText: response.statusText,
				headers: redirectHeaders,
			});
		}

		// Clean headers: strip any upstream noindex tags and ensure index, follow
		const responseHeaders = new Headers(response.headers);
		responseHeaders.delete('x-robots-tag');
		responseHeaders.set('X-Robots-Tag', 'index, follow');

		const contentType = responseHeaders.get('content-type') || '';
		if (contentType.includes('text/html') && typeof HTMLRewriter !== 'undefined') {
			const transformed = new HTMLRewriter()
				.on('meta[name="robots" i]', new RobotsMetaRewriter())
				.on('a[href]', new AttributeRewriter('href'))
				.on('form[action]', new AttributeRewriter('action'))
				.on('link[href]', new AttributeRewriter('href'))
				.on('script[src]', new AttributeRewriter('src'))
				.on('img[src]', new AttributeRewriter('src'))
				.on('input[name="next"]', new InputNextRewriter())
				.transform(
					new Response(response.body, {
						status: response.status,
						statusText: response.statusText,
						headers: responseHeaders,
					})
				);
			return transformed;
		}

		return new Response(response.body, {
			status: response.status,
			statusText: response.statusText,
			headers: responseHeaders,
		});
	};
}
