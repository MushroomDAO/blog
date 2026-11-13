import { createSubsiteProxy } from './subsite-proxy.js';

export const handleTopicProxy = createSubsiteProxy({
	prefix: 'topic',
	defaultTarget: 'https://topic-research.pages.dev',
	envKey: 'TOPIC_RESEARCH_URL',
});
