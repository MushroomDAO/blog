import { createSubsiteProxy } from './subsite-proxy.js';

export const handleAgentProxy = createSubsiteProxy({
	prefix: 'agent',
	defaultTarget: 'https://agent-research-bot.pages.dev',
	envKey: 'AGENT_RESEARCH_BOT_URL',
});
