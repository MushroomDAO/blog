import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

// 唯一数据源是 .agents/skills/mushroom/SKILL.md（Claude Code skill 定义本身），
// 不是复制一份内容到 public/ 手动维护——那样迟早会跟真正加载的 skill 内容
// 漂移。这里在构建期直接读那个文件，/agents/ 页面的安装命令和这个端点返回的
// 永远是同一份东西。
const skillPath = fileURLToPath(new URL('../../../.agents/skills/mushroom/SKILL.md', import.meta.url));

export async function GET() {
	const content = readFileSync(skillPath, 'utf-8');
	return new Response(content, {
		headers: { 'Content-Type': 'text/markdown; charset=utf-8' },
	});
}
