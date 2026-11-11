import { createSubsiteProxy } from './subsite-proxy.js';

export const handleEthereumProxy = createSubsiteProxy({
	prefix: 'ethereum',
	defaultTarget: 'https://ethereum-research-bot.pages.dev',
	envKey: 'ETHEREUM_RESEARCH_BOT_URL',
});
