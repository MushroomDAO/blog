import { createSubsiteProxy } from './subsite-proxy.js';

export const handleJidanProxy = createSubsiteProxy({
	prefix: 'jidan',
	defaultTarget: 'https://daily-jidan-ai.pages.dev',
	envKey: 'DAILY_JIDAN_AI_URL',
});
