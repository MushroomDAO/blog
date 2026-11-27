/** Shared local Game Studio service. HTTP and MCP operate on the same projects. */
import { randomUUID, createHash } from 'node:crypto';
import { mkdir, readdir, readFile, writeFile, rename, rm, lstat, realpath, copyFile, access, rmdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
import vm from 'node:vm';
// Vendored so packaged builds, which ship without node_modules, can still parse game logic.
import { parse as parseModule } from './shared/vendor/acorn.mjs';
import { createServer, type IncomingMessage, type ServerResponse, type Server } from 'node:http';
import { tmpdir } from 'node:os';
import { mkdtemp } from 'node:fs/promises';
import { browserExecutable, browserAutomation } from './browser.ts';
import type { Page, Browser, KeyInput } from 'puppeteer-core';
import { assetHttp } from './gateway/asset-http.ts';
import { buildMediaSettingsHandoff } from './gateway/media-use.ts';
import { buildPublishBundle } from './gateway/web-publish-bundle.ts';
import { WorkspaceStore } from './workspace.ts';
import { ensureRuntime, execute, pluginRoot, HYPERFRAMES_VERSION } from './hyperframes.ts';
import { verificationBinaries } from './scripts/verify-export.ts';
import type { Duplex } from 'node:stream';
import { injectPreviewBridgeHtml, injectViewportGuardHtml, isValidPreviewBridgeToken } from './shared/preview-bridge.ts';
import { attachmentDisposition } from './shared/http-header.ts';
import { HostedGameTemplates } from './shared/hosted-game-templates.ts';
import { lfsPointer } from './shared/repository-template-catalog.ts';
import { zip } from './scripts/zip.mjs';
import { escapeHtml } from './shared/scenario-content.ts';
import { compareGameCatalogOrder, formatGameBriefPrompt, gameAssetInstructions, gameGenreLabels, gameGenres, gameStyles, gameSettings, isReadyBuiltInTemplate, type GameBrief, type GameCard, type GameCatalog, type GameCatalogIssue, type GameCreated, type GameHandoff, type GameRemixOptions, type GameStyle, type RoomServerMessage, type GameTrailer, type GameTrailerStatus } from './shared/game-contract.ts';

const templatesRoot = fileURLToPath(new URL('./templates/games/', import.meta.url));
const kitsRoot = fileURLToPath(new URL('./templates/game-kits/', import.meta.url));
const LIMIT = 8 * 1024 * 1024;
const gameCdnHosts = ['cdnjs.cloudflare.com', 'cdn.jsdelivr.net', 'unpkg.com'];
const gameCdnOrigins = gameCdnHosts.map(host => `https://${host}`).join(' ');
const adStoreHosts = ['apps.apple.com', 'itunes.apple.com', 'play.google.com'];
const xmlNamespaces = new Set(['http://www.w3.org/1999/xhtml','http://www.w3.org/2000/svg','http://www.w3.org/1999/xlink','http://www.w3.org/1998/Math/MathML','http://www.w3.org/XML/1998/namespace','http://www.w3.org/2000/xmlns/']);
const textExtensions = /\.(html|htm|css|js|mjs|cjs|json|map|txt|md|svg|csv|yaml|yml|glsl|vert|frag)$/i;
const mime: Record<string, string> = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.gif': 'image/gif', '.ico': 'image/x-icon', '.woff': 'font/woff', '.woff2': 'font/woff2', '.mp3': 'audio/mpeg', '.ogg': 'audio/ogg', '.wav': 'audio/wav', '.mp4': 'video/mp4', '.webm': 'video/webm', '.wasm': 'application/wasm', '.htm': 'text/html; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8', '.cjs': 'text/javascript; charset=utf-8', '.txt': 'text/plain; charset=utf-8', '.md': 'text/markdown; charset=utf-8', '.csv': 'text/csv; charset=utf-8', '.avif': 'image/avif', '.ttf': 'font/ttf', '.otf': 'font/otf', '.m4a': 'audio/mp4', '.map': 'application/json', '.glb': 'model/gltf-binary', '.gltf': 'model/gltf+json' };
export class GameError extends Error {
  status: number;
  constructor(message: string, status = 400) { super(message); this.status = status; }
}
function idPart(value: unknown): string {
  if (typeof value !== 'string' || !/^[a-zA-Z0-9][a-zA-Z0-9_-]{0,100}$/.test(value)) throw new GameError('Invalid game or room id');
  return value;
}
export function cleanGamePath(value: unknown): string {
  if (typeof value !== 'string' || value.length > 240 || /[\\\x00-\x1f]/.test(value) || value.split('/').some(p => !p || p.startsWith('.') || p.includes(':'))) throw new GameError('Unsafe game file path');
  return value;
}
async function jsonFile<T>(file: string, fallback?: T): Promise<T> {
  try { return JSON.parse(await readFile(file, 'utf8')); }
  catch (e) { if ((e as NodeJS.ErrnoException).code === 'ENOENT' && fallback !== undefined) return fallback; throw e; }
}
async function saveJson(file: string, data: unknown) {
  await mkdir(path.dirname(file), { recursive: true });
  const temp = file + '.' + randomUUID() + '.tmp';
  try { await writeFile(temp, JSON.stringify(data, null, 2)); await rename(temp, file); }
  finally { await rm(temp, { force: true }); }
}
// Every existing path component is checked, including the root. Never follow project symlinks.
async function safeFile(root: string, relative: string, writing = false) {
  const parts = cleanGamePath(relative).split('/');
  let current = root;
  for (const part of ['', ...parts]) {
    if (part) current = path.join(current, part);
    try { if ((await lstat(current)).isSymbolicLink()) throw new GameError('Symlinks are not game files'); }
    catch (e) { if ((e as NodeJS.ErrnoException).code !== 'ENOENT' || !writing) throw e; }
  }
  const parent = await realpath(root);
  if ((await lstat(path.dirname(root))).isSymbolicLink() || parent !== path.join(await realpath(path.dirname(root)), path.basename(root))) throw new GameError('Symlink game root');
  return current;
}

async function gameEntryDependencies(html: string, dir: string, game: GameCard, runtimeRoot: string) {
  // Resolve the same installed DOM parser used by the Hyperframes source tools.
  const runtimeRequire = createRequire(path.join(runtimeRoot, 'package.json'));
  const parserRequire = createRequire(runtimeRequire.resolve('@hyperframes/parsers/package.json'));
  const { parseHTML } = parserRequire('linkedom') as typeof import('linkedom');
  const { document } = parseHTML(html);
  const playPath = `/games/${game.id}/play/`;
  const entry = new URL(`http://game.local/api${playPath}index.html`);
  const authoredBase = document.querySelector('base[href]')?.getAttribute('href');
  const base = (authoredBase && URL.parse(authoredBase, entry)) || entry;
  const errors = new Set<string>();
  const entryScripts: string[] = [];
  const inlineScripts: string[] = [];

  for (const element of document.querySelectorAll('script:not([src])')) {
    if (element.closest('template, noscript')) continue;
    const type = element.getAttribute('type')?.trim().toLowerCase();
    if (type && type !== 'module' && !/^(?:text|application)\/(?:x-)?(?:java|ecma)script(?:\s*;|$)/.test(type)) continue;
    if (element.textContent?.trim()) inlineScripts.push(element.textContent);
  }

  for (const element of document.querySelectorAll('script[src], link[href]')) {
    if (element.closest('template, noscript')) continue;
    const script = element.localName === 'script';
    if (!script && !element.getAttribute('rel')?.toLowerCase().split(/\s+/).includes('stylesheet')) continue;
    const type = element.getAttribute('type')?.trim().toLowerCase();
    if (script && type && type !== 'module' && !/^(?:text|application)\/(?:x-)?(?:java|ecma)script(?:\s*;|$)/.test(type)) continue;
    const kind = script ? 'script' : 'stylesheet';
    const reference = element.getAttribute(script ? 'src' : 'href')?.trim();
    const url = reference ? URL.parse(reference, base) : null;
    if (!url) {
      errors.add(`Invalid ${kind} reference: ${reference || '(empty)'}`);
      continue;
    }
    if (url.origin !== entry.origin) {
      if (game.playableAd || !script || url.protocol !== 'https:' || !gameCdnHosts.includes(url.hostname)) {
        errors.add(`External ${kind} is not allowed in ${game.playableAd ? 'a playable ad' : 'the game preview'}: ${reference}`);
      }
      continue;
    }
    const prefix = [`/api${playPath}`, `/motion-api${playPath}`].find(candidate => url.pathname.startsWith(candidate));
    if (!prefix) {
      errors.add(`The ${kind} must point to a file inside this game: ${reference}`);
      continue;
    }
    try {
      const relative = url.pathname.slice(prefix.length).split('/').map(decodeURIComponent).join('/');
      const file = await safeFile(dir, relative);
      if (!(await lstat(file)).isFile()) {
        errors.add(`Referenced ${kind} is not a file: ${reference}`);
      } else if (!mime[path.extname(file).toLowerCase()]?.startsWith(script ? 'text/javascript' : 'text/css')) {
        errors.add(`Referenced ${kind} has an unsupported file type: ${reference}`);
      } else if (script) {
        entryScripts.push(relative);
      }
    } catch (error) {
      const reason = (error as NodeJS.ErrnoException).code === 'ENOENT' ? 'not found' : 'not readable as a game file';
      errors.add(`Referenced ${kind} ${reason}: ${reference}`);
    }
  }
  return { errors: [...errors], entryScripts, inlineScripts };
}

function extractStaticModuleSpecifiers(source: string): { specifiers: string[]; syntaxError?: string } {
  let ast: any;
  try {
    ast = parseModule(source, { ecmaVersion: 'latest', sourceType: 'module' });
  } catch (error) {
    try {
      ast = parseModule(source, { ecmaVersion: 'latest', sourceType: 'script' });
    } catch {
      return { specifiers: [], syntaxError: (error as Error).message };
    }
  }
  const specifiers: string[] = [];
  const walk = (node: any): void => {
    if (!node || typeof node !== 'object') return;
    if ((node.type === 'ImportDeclaration' || node.type === 'ExportNamedDeclaration' || node.type === 'ExportAllDeclaration')
      && typeof node.source?.value === 'string') {
      specifiers.push(node.source.value);
    } else if (node.type === 'ImportExpression' && node.source?.type === 'Literal' && typeof node.source.value === 'string') {
      specifiers.push(node.source.value);
    }
    for (const value of Object.values(node)) {
      if (Array.isArray(value)) value.forEach(walk);
      else if (value && typeof value === 'object') walk(value);
    }
  };
  walk(ast);
  return { specifiers };
}

function findDisallowedHostDiagnostics(relative: string, source: string, allowedHosts: string[]): { path: string; message: string }[] {
  const diagnostics: { path: string; message: string }[] = [];
  for (const match of source.matchAll(/(?:[a-z][a-z0-9+.-]*:\/\/|(?<=["'`(=])\/\/)[^\s"'<>`\\)]+/gi)) {
    // XML namespace URIs are identifiers, never requested: allow them only where markup declares one or code passes one
    // to a namespace-aware DOM call (bundled libraries such as Three.js create XHTML elements this way).
    if (xmlNamespaces.has(match[0])
      && /(?:\sxmlns(?::[a-z]+)?\s*=\s*["']|\b(?:create(?:Element|Attribute)NS|(?:get|set|has|remove)AttributeNS)\s*\(\s*["'])$/i.test(source.slice(0, match.index))) continue;
    const host = new URL(match[0].startsWith('//') ? 'https:' + match[0] : match[0]).hostname;
    if (!allowedHosts.includes(host)) diagnostics.push({ path: relative, message: `External network host is not allowed: ${host}` });
  }
  return diagnostics;
}

async function inspectLocalModuleGraph(
  dir: string,
  entryScripts: string[],
  inlineScripts: string[],
  allowedHosts: string[],
): Promise<{ diagnostics: { path: string; message: string }[]; importsLogic: boolean; visitedModules: string[]; moduleSources: Map<string, string>; importsThree: boolean }> {
  const diagnostics: { path: string; message: string }[] = [];
  const visited = new Set<string>();
  const moduleSources = new Map<string, string>();
  const queue: string[] = [];
  let importsLogic = false;
  let importsThree = false;

  const enqueueSpecifier = async (fromPath: string, specifier: string) => {
    const clean = specifier.replace(/[?#].*$/, '');
    if (/^(?:https?:)?\/\//i.test(clean)) {
      try {
        const host = new URL(clean.startsWith('//') ? 'https:' + clean : clean).hostname;
        if (!allowedHosts.includes(host)) diagnostics.push({ path: fromPath, message: `External network host is not allowed: ${host}` });
      } catch {
        diagnostics.push({ path: fromPath, message: `Invalid external module URL: ${specifier}` });
      }
      return;
    }
    if (!clean.startsWith('./') && !clean.startsWith('../')) return;
    const baseDir = fromPath === 'index.html' ? '' : path.posix.dirname(fromPath);
    const resolved = path.posix.normalize(baseDir && baseDir !== '.' ? `${baseDir}/${clean}` : clean);
    if (resolved === 'logic.js') importsLogic = true;
    if (/^vendor\/(?:three\.module(?:\.min)?|GLTFLoader|SkeletonUtils|HumanoidRigController)\.js$/i.test(resolved)) importsThree = true;
    try {
      const target = await safeFile(dir, resolved);
      if (!(await lstat(target)).isFile()) {
        diagnostics.push({ path: fromPath, message: `Imported module is not a file: ${specifier}` });
        return;
      }
      if (/\.(?:m?js|cjs)$/i.test(resolved) && !resolved.startsWith('vendor/') && !visited.has(resolved)) {
        queue.push(resolved);
      }
    } catch (error) {
      if (resolved === 'logic.js') return; // logic.js missing is reported under path 'logic.js' below.
      const reason = (error as NodeJS.ErrnoException).code === 'ENOENT' ? 'not found' : 'not readable';
      diagnostics.push({ path: fromPath, message: `Imported module ${reason}: ${specifier}` });
    }
  };

  for (const script of inlineScripts) {
    const { specifiers } = extractStaticModuleSpecifiers(script);
    for (const specifier of specifiers) await enqueueSpecifier('index.html', specifier);
  }
  for (const entry of entryScripts) {
    if (entry === 'logic.js') importsLogic = true;
    if (!entry.startsWith('vendor/') && !visited.has(entry)) queue.push(entry);
  }

  while (queue.length > 0 && visited.size < 200) {
    const relative = queue.shift()!;
    if (visited.has(relative)) continue;
    visited.add(relative);
    let source: string;
    try {
      source = await readFile(await safeFile(dir, relative), 'utf8');
    } catch {
      continue;
    }
    moduleSources.set(relative, source);
    if (relative !== 'client.js') {
      diagnostics.push(...findDisallowedHostDiagnostics(relative, source, allowedHosts));
    }
    const { specifiers, syntaxError } = extractStaticModuleSpecifiers(source);
    if (syntaxError) {
      diagnostics.push({ path: relative, message: `JavaScript syntax error: ${syntaxError}` });
      continue;
    }
    for (const specifier of specifiers) await enqueueSpecifier(relative, specifier);
  }
  return { diagnostics, importsLogic, visitedModules: [...visited], moduleSources, importsThree };
}

function stripJsComments(source: string): string {
  return source.replace(/\/\*[\s\S]*?\*\//g, '').replace(/(^|[^:\\])\/\/[^\n]*/g, '$1');
}

/** Advisory static audit for high-frequency 3D humanoid kinematics anti-patterns. */
export function inspect3dKinematicsWarnings(
  moduleSources: Map<string, string>,
  options: { hasFixedLogicTick: boolean },
): string[] {
  const warnings: string[] = [];
  const allNonVendorCode = [...moduleSources.entries()]
    .filter(([rel]) => rel !== 'logic.js' && !rel.startsWith('vendor/'))
    .map(([, raw]) => stripJsComments(raw))
    .join('\n');
  const usesAnyClipPlayback = /\.(?:playClip|playOnce|addClips|retargetClipsFrom)\s*\(|\bAnimationMixer\b/.test(allNonVendorCode);

  for (const [relative, raw] of moduleSources.entries()) {
    if (relative === 'logic.js' || relative.startsWith('vendor/')) continue;
    const code = stripJsComments(raw);
    const usesSharedRig = /HumanoidRigController|createHumanoidRig/.test(code);
    if (usesSharedRig) {
      const drivesManualArmIk = /\b(?:rightHand|leftHand)\s*:/.test(code);
      if (drivesManualArmIk && !usesAnyClipPlayback) {
        warnings.push(
          `3D motion advisory in ${relative}: HumanoidRigController drives manual arm IK without any skeletal clip playback (playClip/playOnce/retargetClipsFrom). Attach native Mixamo clips via 3d-asset (rig_retarget or 1-step retarget on an existing rigTaskId with multi-clip rigPreset "mixamo-combat"/"mixamo-locomotion") or rig.retargetClipsFrom(...) for full-body locomotion, attacks, hit reactions, and defeat poses.`,
        );
      }
      continue;
    }

    const touchesBones = /\bisBone\b|mixamorig|\bsk\s*\[|\bbones\s*\[/.test(code);
    const copiesRestQuat = /\.quaternion\.copy\s*\(/.test(code);
    const hasSmoothing = /\.slerp\s*\(|\bAnimationMixer\b/.test(code);
    if (touchesBones && copiesRestQuat && !hasSmoothing) {
      warnings.push(
        `3D kinematics risk in ${relative}: bone quaternions are reset via .quaternion.copy() without Quaternion.slerp, AnimationMixer, or vendor/HumanoidRigController.js — state switches will snap in 1 frame. Use vendor/HumanoidRigController.js or slerp persistent per-bone quaternions.`,
      );
    }

    const usesFrameDeltaGait =
      options.hasFixedLogicTick
      && /Math\.hypot\s*\([^)]*-[^)]*,[^)]*-[^)]*\)/.test(code)
      && /\b(?:walking|moving|isWalking|isMoving)\s*=\s*[a-zA-Z_$][\w$]*\s*>/.test(code)
      && !/Math\.exp\s*\(|smoothWalk|walkBlend/.test(code);
    if (usesFrameDeltaGait) {
      warnings.push(
        `3D kinematics risk in ${relative}: walking/gait state is derived from raw render-frame displacement against a fixed-tick simulation without exponential smoothing — non-tick frames on 60/120 Hz displays drop delta to 0 and cause 30 Hz leg flicker. Use vendor/HumanoidRigController.js (syncTransform) or low-pass filter continuous velocity.`,
      );
    }

    const diyHumanoidSkinning =
      /(?:GLTFLoader|loadModel)/.test(code)
      && /setAttribute\s*\(\s*['"]skin(?:Index|Weight)['"]/.test(code)
      && /mixamorig|RightArm|LeftArm|RightUpLeg|LeftUpLeg|Spine/.test(code);
    if (diyHumanoidSkinning) {
      warnings.push(
        `3D rigging risk in ${relative}: manual runtime skinIndex/skinWeight synthesis detected on humanoid geometry. Use real Mixamo auto-rigging (3d-asset operation="rig_retarget") and vendor/HumanoidRigController.js instead of DIY bounding-box skinning.`,
      );
    }
  }
  return warnings;
}
async function inventory(root: string, prefix = ''): Promise<{ path: string; bytes: number }[]> {
  const result: { path: string; bytes: number }[] = [];
  for (const entry of await readdir(path.join(root, prefix), { withFileTypes: true })) {
    if (entry.name.startsWith('.') || (!prefix && ['game.json','trailer'].includes(entry.name.toLowerCase()))) continue;
    const relative = prefix + entry.name;
    const file = await safeFile(root, relative);
    if (entry.isDirectory()) result.push(...await inventory(root, relative + '/'));
    else if (entry.isFile()) result.push({ path: relative, bytes: (await lstat(file)).size });
    if (result.length > 5000) throw new GameError('Too many game files');
  }
  return result.sort((a, b) => a.path.localeCompare(b.path));
}
const NEGATED_3D_PROMPT_RE = /(?:(?:非|不要|不用|别用|别做|不做|无需)\s*(?:用|使用|做|采用)?\s*(?:(?:3d|three\.?js|webgl)(?![A-Za-z0-9])|三维)|(?<![A-Za-z0-9])(?:(?:not|no|without|avoid|skip|don['’]t\s+use|do\s+not\s+use)\s+|non-?\s*)(?:3d|three\.?js|webgl)(?![A-Za-z0-9]))/i;
const POSITIVE_3D_PROMPT_RE = /(?<![A-Za-z0-9])(?:3d|three\.?js|webgl)(?![A-Za-z0-9])|三维/i;

function inferStyleFromPrompt(prompt: string): GameStyle | null {
  if (NEGATED_3D_PROMPT_RE.test(prompt)) return null;
  return POSITIVE_3D_PROMPT_RE.test(prompt) ? '3d' : null;
}
function briefInput(raw: any): GameBrief {
  if (!raw || typeof raw.prompt !== 'string' || !raw.prompt.trim() || raw.prompt.length > 20000) throw new GameError('prompt is required and must be at most 20000 characters');
  if (typeof raw.multiplayer !== 'boolean') throw new GameError('Invalid multiplayer value');
  for (const [key, choices] of [['genre', gameGenres], ['style', gameStyles], ['setting', gameSettings]] as const) {
    if (raw[key] != null && !(choices as readonly string[]).includes(raw[key])) throw new GameError(`Invalid ${key}`);
  }
  if (raw.orientation != null && raw.orientation !== 'landscape' && raw.orientation !== 'portrait') throw new GameError('Invalid orientation');
  if (raw.playableAd != null && typeof raw.playableAd !== 'boolean') throw new GameError('Invalid playableAd');
  // A playable ad is a single-player portrait build; the flag is ignored for landscape or multiplayer briefs.
  const playableAd = raw.playableAd === true && raw.orientation === 'portrait' && !raw.multiplayer;
  const prompt = raw.prompt.trim();
  const style: GameStyle | null = raw.style ?? inferStyleFromPrompt(prompt);
  return { playableAd, prompt, multiplayer: raw.multiplayer, genre: raw.genre ?? null, style, setting: raw.setting ?? null, orientation: raw.orientation ?? 'landscape' };
}
function remixOverridesInput(raw: any): GameRemixOptions {
  if (raw == null) return {};
  if (typeof raw !== 'object' || Array.isArray(raw)) throw new GameError('Invalid remix options');
  for (const [key, choices] of [['genre', gameGenres], ['style', gameStyles], ['setting', gameSettings]] as const) {
    if (raw[key] != null && !(choices as readonly string[]).includes(raw[key])) throw new GameError(`Invalid ${key}`);
  }
  if (raw.orientation != null && raw.orientation !== 'landscape' && raw.orientation !== 'portrait') throw new GameError('Invalid orientation');
  return {
    ...(raw.genre != null ? { genre: raw.genre } : {}),
    ...(raw.style != null ? { style: raw.style } : {}),
    ...(raw.setting != null ? { setting: raw.setting } : {}),
    ...(raw.orientation != null ? { orientation: raw.orientation } : {}),
  };
}
function assertSinglePlayerAuthoring(multiplayer: boolean) {
  if (multiplayer) throw new GameError('Game Studio authoring is available for single-player games only');
}
function createSinglePlayerGame(service: GameProjects, raw: any) {
  assertSinglePlayerAuthoring(raw?.multiplayer !== undefined && raw.multiplayer !== false);
  return service.create({ ...raw, multiplayer: false });
}
type TemplateInstructionContext = {
  readyBuiltInTemplate?: boolean;
  templateOverrides?: string[];
};
function templateOverrideSummary(
  original: Pick<StoredGame, 'genre' | 'style' | 'setting' | 'orientation' | 'playableAd'>,
  next: Pick<StoredGame, 'genre' | 'style' | 'setting' | 'orientation' | 'playableAd'>,
): string[] {
  const changes: string[] = [];
  if (next.genre !== original.genre) changes.push(`genre=${next.genre} (template: ${original.genre})`);
  if (next.style !== original.style) changes.push(`style=${next.style ?? 'none'} (template: ${original.style ?? 'none'})`);
  if (next.setting !== original.setting) changes.push(`setting=${next.setting ?? 'none'} (template: ${original.setting ?? 'none'})`);
  const origOrientation = original.orientation ?? 'landscape';
  const nextOrientation = next.orientation ?? 'landscape';
  if (nextOrientation !== origOrientation) changes.push(`orientation=${nextOrientation} (template: ${origOrientation})`);
  if (Boolean(next.playableAd) !== Boolean(original.playableAd)) {
    changes.push(`playableAd=${Boolean(next.playableAd)} (template: ${Boolean(original.playableAd)})`);
  }
  return changes;
}
function instruction(game: GameCard, brief: GameBrief, remix = false, templateContext?: TemplateInstructionContext) {
  const summary = [brief.style && `${brief.style} style`, brief.genre && gameGenreLabels[brief.genre].toLowerCase(), brief.setting && `${brief.setting} setting`].filter(Boolean).join(', ');
  const prompt = formatGameBriefPrompt(brief.prompt, { orientation: brief.orientation, playableAd: brief.playableAd });
  const assetInstructions = brief.playableAd
    ? `Follow the playable-ad recipe in references/game-playable-ad.md. ${gameAssetInstructions}`
    : gameAssetInstructions;
  if (remix && templateContext?.readyBuiltInTemplate) {
    const overrides = templateContext.templateOverrides ?? [];
    const overrideLine = overrides.length > 0
      ? `\nExplicit parameter overrides vs template defaults: ${overrides.join(', ')} (treat these as requested custom modifications).`
      : '';
    return [
      `This workspace game ${game.id} is a remix game copied from a complete, playable built-in template (code, assets, cover, controls, and metadata are already in place). Brief: ${summary ? summary + '. ' : ''}${prompt}${overrideLine}`,
      `First, infer from the user's message in this turn, any parameter overrides, and any attached resources whether the user asks for ANY custom modifications to this game (gameplay, mechanics, rules, theme, visuals/art, audio, language/UI copy, difficulty, layout/orientation, genre/style/setting, or new features).`,
      `- If NO custom modifications are requested (e.g. empty message, unchanged game description, or generic requests like "build/make/remix this game" as-is, with no parameter overrides and no custom assets to integrate): deliver immediately with zero rebuild. Do NOT read openmotion://workflow/game/start or skill docs, do NOT edit files (openmotion_game_write_files), and do NOT run openmotion_game_validate, openmotion_game_playtest, openmotion_game_simulate, or openmotion_game_capture_cover. Call openmotion_game_set_status(id="${game.id}", status="ready") and openmotion_present_artifact(kind="game-project", projectId="${game.id}") silently right away without a pre-tool "opening preview" filler message (only call openmotion_game_get(id="${game.id}") first if you still need the game's controls or details to describe it).`,
      `- If custom modifications ARE requested: read openmotion://workflow/game/start, inspect the copied project with openmotion_game_get(id="${game.id}") and openmotion_game_read_file(id="${game.id}", path=...), and modify the existing project files in place rather than rewriting from scratch. Build a single-player game. Ask for local-market publication consent only when missing. ${assetInstructions} Follow the skill workflow: openmotion_game_set_status("building"), update files via openmotion_game_write_files, verify via openmotion_game_validate, openmotion_game_playtest (and openmotion_game_simulate when using logic.js), refresh cover/metadata with openmotion_game_capture_cover and openmotion_game_update_meta when visuals or title/controls changed, then set ready (and openmotion_game_publish only when authorized), and present via openmotion_present_artifact(kind="game-project", projectId="${game.id}"). Never operate the user's visible browser or desktop.`,
      `- User-facing voice (applies to BOTH paths above): whether delivered as-is or customized in place, always open your final reply in the user's language as the builder who just coded and finished this game for them (e.g. "《<title>》已为你制作完成……" / "I've built <title> for you — ..."), summarize the gameplay highlights, any customized features, and real controls, invite them to play, and offer follow-up tweaks. Never open with passive "opened the preview" / "updated the existing game" wording, never mention templates, copying source files, reusing existing project files, internal skills/tools, or skipping build/test steps, and never fabricate checks you did not run.`,
    ].join('\n');
  }
  return `Use the openmotion-game Skill to ${remix ? 'remix' : 'build'} game ${game.id} in this workspace. Read openmotion://workflow/game/start and openmotion_game_get(id=${game.id}). Brief: ${summary ? summary + '. ' : ''}${prompt}\nBuild a single-player game. Ask for local-market publication consent only when missing. ${assetInstructions} Follow the skill workflow: openmotion_game_set_status("building"), author files via openmotion_game_write_files, verify via openmotion_game_validate, openmotion_game_playtest (and openmotion_game_simulate when using logic.js), capture a game-only cover with openmotion_game_capture_cover, update metadata via openmotion_game_update_meta, then set ready (and openmotion_game_publish only when authorized). Never operate the user's visible browser or desktop.`;
}
export const starterLogic = `export const meta = { minPlayers: 1, maxPlayers: 4, tickRate: 20, serverTick: true };
export function setup(ctx, players) { return { scores: Object.fromEntries(players.map(id => [id, 0])) }; }
export function validateAction(state, playerId, action, ctx) { return Object.hasOwn(state.scores, playerId) && action?.type === 'score'; }
export function applyAction(state, playerId, action, ctx) { if (playerId === null && action?.type === 'membership') { if (action.expired) delete state.scores[action.player]; else if (action.connected && !Object.hasOwn(state.scores, action.player)) state.scores[action.player]=0; } else if (action?.type === 'score' && Object.hasOwn(state.scores, playerId)) state.scores[playerId]++; return state; }
export function isGameOver(state, ctx) { return { over: false }; }
export function viewFor(state, playerId, ctx) { return state; }
`;
function starter(multiplayer: boolean): { path: string; content: string }[] {
  const canvas = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Game draft</title><canvas id="game" width="800" height="600"></canvas>';
  if (!multiplayer) return [{ path: 'index.html', content: canvas + `<script>const c=document.querySelector('canvas'),g=c.getContext('2d');function draw(t){g.clearRect(0,0,c.width,c.height);g.fillRect(200+100*Math.sin(t/1000),250,30,30);requestAnimationFrame(draw)}requestAnimationFrame(draw);</script></html>` }];
  return [{ path: 'index.html', content: canvas + '<p>Room: <span id="room-code"></span></p><button id="invite">Copy invite link</button><button id="start">Start</button><script src="./client.js"></script></html>' }, { path: 'logic.js', content: starterLogic }, { path: 'client.js', content: `const inviteUrl=new URL(location.href);
const room=inviteUrl.searchParams.get('room')||crypto.randomUUID().replaceAll('-','').slice(0,8);
inviteUrl.searchParams.set('room',room);
try{history.replaceState(null,'',inviteUrl.href);}catch{}
document.querySelector('#room-code').textContent=room;
document.querySelector('#invite').onclick=()=>navigator.clipboard.writeText(inviteUrl.href).catch(error=>console.warn('Invite copy failed',error));
const roomUrl=new URL(location.href);
roomUrl.protocol=location.protocol==='https:'?'wss:':'ws:';
roomUrl.pathname=location.pathname.split('/play/')[0]+'/rooms/'+encodeURIComponent(room);
roomUrl.search='';roomUrl.hash='';
const tokenKey='openmotion-room:'+location.pathname+':'+room;
let socket,stopped=false,retry;
function token(){try{return sessionStorage.getItem(tokenKey)||undefined;}catch{return undefined;}}
function connect(){
socket=new WebSocket(roomUrl.href);
socket.onopen=()=>socket.send(JSON.stringify({type:'join',reconnectToken:token()}));
socket.onclose=()=>{if(!stopped)retry=setTimeout(connect,1000);};
socket.onmessage=onMessage;
}
addEventListener('pagehide',()=>{stopped=true;clearTimeout(retry);socket?.close();});
const canvas=document.querySelector('canvas'),g=canvas.getContext('2d');
function onMessage(e){const m=JSON.parse(e.data);if(m.type==='joined'){try{sessionStorage.setItem(tokenKey,m.reconnectToken);}catch{}}else if(m.type==='state'){g.clearRect(0,0,800,600);g.fillText(JSON.stringify(m.view),20,40);}else if(m.type==='error'){console.error(m.message);if(m.message.startsWith('Reconnect token expired')){try{sessionStorage.removeItem(tokenKey);}catch{}socket.send(JSON.stringify({type:'join'}));}}}
connect();
document.querySelector('#start').onclick=()=>socket.send(JSON.stringify({type:'start'}));
canvas.onclick=()=>socket.send(JSON.stringify({type:'input',action:{type:'score'}}));
` }];
}

export type GameBrowserAction =
  | { type: 'key'; key: string; event?: 'down' | 'up' | 'press' }
  | { type: 'mouse'; event: 'move' | 'down' | 'up' | 'click'; x?: number; y?: number; selector?: string; button?: 'left' | 'middle' | 'right' }
  | { type: 'wait'; ms: number }
  | { type: 'screenshot'; label?: string }
  | { type: 'burst'; count: number; intervalMs?: number; label?: string }
  | { type: 'action'; action: Record<string, unknown> };

export function validateGameScript(value: unknown): GameBrowserAction[] {
  if (!Array.isArray(value) || value.length > 100) throw new GameError('Use at most 100 input actions per client');
  let waits = 0;
  let screenshots = 0;
  for (const a of value) {
    if (!a || typeof a !== 'object') throw new GameError('Invalid playtest action');
    if (a.type === 'key') {
      if (typeof a.key !== 'string' || !/^(?:[a-zA-Z0-9]|Arrow(?:Up|Down|Left|Right)|Enter|Escape|Tab|Space|Shift|Control)$/.test(a.key) || !['down','up','press'].includes(a.event ?? 'press')) throw new GameError('Invalid scripted key');
    } else if (a.type === 'mouse') {
      if (!['move','down','up','click'].includes(a.event) || !['left','middle','right'].includes(a.button ?? 'left')) throw new GameError('Invalid scripted mouse action');
      if (a.selector !== undefined) { if (a.event !== 'click' || typeof a.selector !== 'string' || !/^#[a-zA-Z][\w-]{0,79}$/.test(a.selector)) throw new GameError('Click selectors must be simple element ids'); }
      else if (![a.x,a.y].every(Number.isFinite) || a.x < 0 || a.x > 1280 || a.y < 0 || a.y > 720) throw new GameError('Mouse coordinates must be inside 1280x720');
    } else if (a.type === 'wait') {
      if (!Number.isInteger(a.ms) || a.ms < 0 || a.ms > 10000) throw new GameError('Each wait must be 0–10000 ms');
      waits += a.ms;
    } else if (a.type === 'screenshot') {
      if (a.label !== undefined && (typeof a.label !== 'string' || !/^[a-zA-Z0-9_-]{1,40}$/.test(a.label))) throw new GameError('Screenshot labels must be 1–40 ASCII alphanumeric/dash/underscore characters');
      if (++screenshots > 8) throw new GameError('Use at most 8 screenshot actions per client');
    } else if (a.type === 'burst') {
      if (!Number.isInteger(a.count) || a.count < 2 || a.count > 6) throw new GameError('Burst count must be an integer 2–6');
      const intervalMs = a.intervalMs ?? 100;
      if (!Number.isInteger(intervalMs) || intervalMs < 50 || intervalMs > 500) throw new GameError('Burst intervalMs must be an integer 50–500');
      if (a.label !== undefined && (typeof a.label !== 'string' || !/^[a-zA-Z0-9_-]{1,32}$/.test(a.label))) throw new GameError('Burst labels must be 1–32 ASCII alphanumeric/dash/underscore characters');
      screenshots += a.count;
      if (screenshots > 8) throw new GameError('Use at most 8 screenshot actions per client');
      waits += (a.count - 1) * intervalMs;
    } else if (a.type === 'action') {
      if (!a.action || typeof a.action !== 'object' || Array.isArray(a.action)) throw new GameError('Action payload must be a JSON object');
      let serialized = '';
      try { serialized = JSON.stringify(a.action); } catch { throw new GameError('Action payload must be JSON-serializable'); }
      if (!serialized || serialized.length > 16384) throw new GameError('Action payload must be at most 16 KiB');
    } else throw new GameError('Only key, mouse, wait, screenshot, burst and action actions are supported');
  }
  if (waits > 60000) throw new GameError('Script waits must total at most 60000 ms');
  return value;
}

/** Composite 2–8 playtest diagnostic captures into one labeled row-major contact sheet when ffmpeg is available. */
export async function buildPlaytestContactSheet(
  shots: Array<{ label: string; path: string }>,
  outputPath: string,
  options: { ffmpeg?: string } = {},
): Promise<{ path: string; legend: string; grid: { cols: number; rows: number } } | null> {
  if (shots.length < 2) return null;
  const cols = shots.length <= 4 ? 2 : 3;
  const rows = Math.ceil(shots.length / cols);
  const cellW = cols === 2 ? 640 : 480;
  const cellH = cols === 2 ? 360 : 270;
  const pad = 6;
  const margin = 6;
  const ffmpegBin = options.ffmpeg ?? verificationBinaries().ffmpeg;
  const args: string[] = ['-v', 'error', '-nostdin'];
  const filters: string[] = [];
  for (let idx = 0; idx < shots.length; idx++) {
    args.push('-i', shots[idx].path);
    filters.push(
      `[${idx}:v]format=rgba,scale=w=${cellW}:h=${cellH}:force_original_aspect_ratio=decrease,pad=${cellW}:${cellH}:(ow-iw)/2:(oh-ih)/2:color=0x1c1e24,setpts=PTS-STARTPTS[c${idx}]`,
    );
  }
  const inputs = shots.map((_, idx) => `[c${idx}]`).join('');
  filters.push(`${inputs}concat=n=${shots.length}:v=1:a=0,tile=${cols}x${rows}:padding=${pad}:margin=${margin}:color=0x111318[out]`);
  args.push('-filter_complex', filters.join(';'), '-map', '[out]', '-frames:v', '1', '-y', outputPath);
  try {
    await mkdir(path.dirname(outputPath), { recursive: true });
    const res = await execute(ffmpegBin, args, path.dirname(outputPath), 20_000);
    if (res.code !== 0) return null;
    const info = await lstat(outputPath).catch(() => null);
    if (!info?.isFile() || info.size <= 0) return null;
    const legend = `Grid ${cols}x${rows} (row-major): ` + shots.map((s, idx) => {
      const r = Math.floor(idx / cols) + 1;
      const c = (idx % cols) + 1;
      return `[${idx + 1}] r${r}c${c}=${s.label}`;
    }).join(', ');
    return { path: outputPath, legend, grid: { cols, rows } };
  } catch {
    return null;
  }
}

export function gameCoverDimensions(bytes: Buffer, extension: string): { width: number; height: number } {
  let width = 0, height = 0;
  if (bytes.length >= 24 && bytes.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10]))) { width=bytes.readUInt32BE(16);height=bytes.readUInt32BE(20); }
  else if (bytes.length >= 10 && /^GIF8[79]a/.test(bytes.toString('ascii',0,6))) {width=bytes.readUInt16LE(6);height=bytes.readUInt16LE(8);}
  else if (bytes.length >= 30 && bytes.toString('ascii',0,4)==='RIFF' && bytes.toString('ascii',8,12)==='WEBP') {
    const kind=bytes.toString('ascii',12,16);
    if(kind==='VP8X'){width=1+bytes.readUIntLE(24,3);height=1+bytes.readUIntLE(27,3);}
    else if(kind==='VP8 ' && bytes[23]===0x9d && bytes[24]===1 && bytes[25]===0x2a){width=bytes.readUInt16LE(26)&0x3fff;height=bytes.readUInt16LE(28)&0x3fff;}
    else if(kind==='VP8L' && bytes[20]===0x2f){const bits=bytes.readUInt32LE(21);width=1+(bits&0x3fff);height=1+((bits>>>14)&0x3fff);}
  } else if(bytes.length>4 && bytes[0]===255 && bytes[1]===216) {
    for(let i=2;i+4<bytes.length;){
      if(bytes[i++]!==255) continue;while(bytes[i]===255)i++;const marker=bytes[i++];
      if(marker===0xd9||marker===0xda)break;if(marker===0xd8||marker===0x01||(marker>=0xd0&&marker<=0xd7))continue;
      if(i+2>bytes.length)break;const length=bytes.readUInt16BE(i);if(length<2||i+length>bytes.length)break;
      if([0xc0,0xc1,0xc2,0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf].includes(marker)&&length>=7){height=bytes.readUInt16BE(i+3);width=bytes.readUInt16BE(i+5);break;}i+=length;
    }
  } else if(extension.toLowerCase()==='.svg') {
    const svg=/<svg\b[^>]*>/i.exec(bytes.toString('utf8'))?.[0]??'';
    width=Number(/\bwidth\s*=\s*["']([\d.]+)(?:px)?["']/i.exec(svg)?.[1]);
    height=Number(/\bheight\s*=\s*["']([\d.]+)(?:px)?["']/i.exec(svg)?.[1]);
    if(!width||!height){const box=/\bviewBox\s*=\s*["']([^"']+)["']/i.exec(svg)?.[1].trim().split(/[\s,]+/).map(Number);if(box?.length===4){width=box[2];height=box[3];}}
  }
  if(!Number.isFinite(width+height)||width<=0||height<=0)throw new GameError('Cannot read cover dimensions; use a PNG/JPEG/WebP/GIF/SVG image or openmotion_game_capture_cover');
  return {width,height};
}
export function assertGameCoverSize(size: {width:number;height:number}) {
  if(size.width<960||size.height<540||Math.abs(size.width/size.height/(16/9)-1)>.05) throw new GameError('Cover must be at least 960x540 and 16:9 ±5%; use openmotion_game_capture_cover');
}
/** Approximate changed lines, ignoring whitespace and line ordering; advisory, never a quality score. */
export function gameChangedLines(source: string, kit: string) {
  const counts=new Map<string,number>();
  for(const line of kit.split(/\r?\n/).map(s=>s.trim()).filter(Boolean))counts.set(line,(counts.get(line)??0)+1);
  let added=0;for(const line of source.split(/\r?\n/).map(s=>s.trim()).filter(Boolean)){const n=counts.get(line)??0;if(n)counts.set(line,n-1);else added++;}
  return Math.max(added,[...counts.values()].reduce((a,b)=>a+b,0));
}

export type GameSimulationStep = {fromTick:number;toTick:number;action:Record<string,unknown>};
export type GameSimulationScripts = 'idle'|'reference'|('idle'|'reference'|GameSimulationStep[])[];
export function validateSimulationRoute(value: unknown): GameSimulationStep[] {
  if(!Array.isArray(value)||value.length>1000)throw new GameError('Simulation route must contain at most 1000 steps');
  for(const step of value){
    if(!step||!Number.isInteger(step.fromTick)||!Number.isInteger(step.toTick)||step.fromTick<1||step.toTick<step.fromTick||step.toTick>10000)throw new GameError('Route ticks must be inclusive integers within 1–10000');
    if(!step.action||typeof step.action!=='object'||Array.isArray(step.action))throw new GameError('Simulation action must be a JSON object');
    const json=JSON.stringify(step.action);if(!json||json.length>8192)throw new GameError('Simulation actions must be JSON objects under 8 KiB');
  }
  const edges=new Map<number,number>();for(const step of value){edges.set(step.fromTick,(edges.get(step.fromTick)??0)+1);edges.set(step.toTick+1,(edges.get(step.toTick+1)??0)-1);}
  let active=0;for(const [,delta] of [...edges].sort((a,b)=>a[0]-b[0])){active+=delta;if(active>16)throw new GameError('At most 16 simulation actions per player per tick');}
  return JSON.parse(JSON.stringify(value));
}
function simulationMilestone(state: any) {return JSON.stringify([state?.phase,state?.wave,state?.result,state?.over]);}
export function gameNextSteps(plan: string): string[] {
  const section=/^#{1,3}\s+Follow-up opportunities[^\n]*\n([\s\S]*?)(?=^#{1,3}\s|$(?![\s\S]))/im.exec(plan)?.[1]??'';
  const candidates=section.split('\n').filter(line=>/^\s*[-*]\s+/.test(line)).map(line=>line.replace(/^\s*[-*]\s+(?:\[[ x]\]\s*)?/i,'').trim().slice(0,200)).filter(Boolean);
  const suggestions=[...new Set(candidates)];
  const title=(/^#\s+(.+)$/m.exec(plan)?.[1]??'this game').trim().slice(0,60);
  for(const text of [`Add a boss wave to ${title}, with a readable attack pattern.`,`Tune ${title}'s difficulty using reference-win and idle-loss simulations.`,`Add a new skill to ${title}, with clear cooldown and touch controls.`])if(suggestions.length<3&&!suggestions.includes(text))suggestions.push(text);
  return [...new Set(suggestions)].slice(0,3);
}

/** Advisory static inspection cannot replace the no-input browser join assertion. */
export function gameRoomEntryErrors(source:string):string[] {
  const errors:string[]=[],room=/(?:room|房间)/i;
  const attr=(tag:string,name:string)=>new RegExp(String.raw`\b${name}\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))`,'i').exec(tag)?.slice(1).find(v=>v!==undefined)??'';
  const labels=[...source.matchAll(/<label\b([^>]*)>([\s\S]*?)<\/label\s*>/gi)];
  for(const input of source.matchAll(/<input\b[^>]*>/gi)){
    const tag=input[0],type=attr(tag,'type').toLowerCase();
    if(type&&!['text','search','tel','number','password','email','url'].includes(type))continue;
    const id=attr(tag,'id');
    const associated=labels.some(label=>room.test(label[2].replace(/<[^>]*>/g,' '))&&((id&&attr(label[1],'for')===id)||label[0].includes(tag)));
    if(room.test(['id','name','placeholder','label','aria-label'].map(key=>attr(tag,key)).join(' '))||associated){errors.push('Room-code input is forbidden: join automatically from ?room= on load.');break;}
  }
  if([...source.matchAll(/<button\b[^>]*>([\s\S]*?)<\/button\s*>/gi)].some(button=>/(?:join\s+room|加入房间)/i.test(button[1].replace(/<[^>]*>/g,' ')))||/<input\b[^>]*\btype\s*=\s*["']?(?:button|submit)[^>]*(?:join\s+room|加入房间)/i.test(source)||/(?:textContent|innerText)\s*=\s*["'`](?:join\s+room|加入房间)["'`]/i.test(source))errors.push('Join room button is forbidden: the lobby may only offer Copy invite link and one primary Start action.');
  return errors;
}
function readsRoomQuery(source:string) {return /(?:URLSearchParams|searchParams)/.test(source)&&/(?:\.get\s*\(\s*["'`]room["'`]|\broom\s*[:},])/.test(source);}

export function normalizeSelfTestAssertions(raw: unknown): Array<{ name: string; passed: boolean; expected: string; actual: unknown; reason?: string }> {
  if (!raw || typeof raw !== 'object') return [];
  const obj = raw as Record<string, unknown>;
  if (typeof obj.__error === 'string') {
    return [{ name: 'selfTest', passed: false, expected: 'window.__omGame.runSelfTests() succeeds', actual: obj.__error, reason: obj.__error }];
  }
  const rows: Array<{ name: string; passed: boolean; expected: string; actual: unknown; reason?: string }> = [];
  const pushItem = (name: string, entry: unknown) => {
    const cleanName = String(name || 'check').slice(0, 80);
    if (typeof entry === 'boolean') {
      rows.push({ name: `selfTest:${cleanName}`, passed: entry, expected: 'self-test passes', actual: entry, ...(entry ? {} : { reason: 'Self-test returned false' }) });
    } else if (entry && typeof entry === 'object') {
      const rec = entry as Record<string, unknown>;
      const passed = typeof rec.pass === 'boolean' ? rec.pass : typeof rec.passed === 'boolean' ? rec.passed : Boolean(rec.ok);
      const detail = rec.detail ?? rec.reason ?? rec.message;
      rows.push({
        name: `selfTest:${cleanName}`,
        passed,
        expected: 'self-test passes',
        actual: detail ?? passed,
        ...(passed ? {} : { reason: typeof detail === 'string' && detail ? detail : 'Self-test failed' }),
      });
    }
  };
  if (Array.isArray(raw)) {
    raw.forEach((entry, idx) => pushItem(String((entry as any)?.name ?? idx), entry));
  } else if (Array.isArray(obj.checks)) {
    obj.checks.forEach((entry, idx) => pushItem(String((entry as any)?.name ?? idx), entry));
  } else {
    for (const [key, value] of Object.entries(obj)) {
      if (key === 'passed' || key === 'pass') continue;
      pushItem(key, value);
    }
  }
  return rows.slice(0, 50);
}

export function normalizeKinematicsAssertions(raw: unknown): Array<{ name: string; passed: boolean; expected: string; actual: unknown; reason?: string }> {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return [];
  const obj = raw as Record<string, unknown>;
  const isSingleTelemetry = typeof obj.frames === 'number'
    || typeof obj.maxBoneRadPerSec === 'number'
    || typeof obj.maxBoneStepRad === 'number'
    || typeof obj.maxYawRadPerSec === 'number'
    || typeof obj.walkZeroFlips === 'number';
  const entries: Array<[string, Record<string, unknown>]> = isSingleTelemetry
    ? [['', obj]]
    : Object.entries(obj)
      .filter(([, value]) => value && typeof value === 'object' && !Array.isArray(value))
      .map(([key, value]) => [key, value as Record<string, unknown>]);

  const rows: Array<{ name: string; passed: boolean; expected: string; actual: unknown; reason?: string }> = [];
  for (const [label, metrics] of entries.slice(0, 8)) {
    const frames = typeof metrics.frames === 'number' ? metrics.frames : 10;
    if (frames < 5) continue;
    const prefix = label ? `kinematics:${label}:` : 'kinematics:';
    if (typeof metrics.walkZeroFlips === 'number' && Number.isFinite(metrics.walkZeroFlips)) {
      const passed = metrics.walkZeroFlips <= 1;
      rows.push({
        name: `${prefix}noWalkFlicker`,
        passed,
        expected: 'walkZeroFlips <= 1 (no 30 Hz square-wave gait flicker)',
        actual: metrics.walkZeroFlips,
        ...(passed ? {} : { reason: `Detected ${metrics.walkZeroFlips} adjacent-frame walk-blend drop-to-zero oscillations` }),
      });
    }
    if (typeof metrics.maxBoneRadPerSec === 'number' && Number.isFinite(metrics.maxBoneRadPerSec)) {
      const passed = metrics.maxBoneRadPerSec <= 22;
      rows.push({
        name: `${prefix}smoothBoneMotion`,
        passed,
        expected: 'maxBoneRadPerSec <= 22 rad/s (frame-rate independent joint-snap guard)',
        actual: +metrics.maxBoneRadPerSec.toFixed(2),
        ...(passed ? {} : { reason: `Peak bone angular rate ${metrics.maxBoneRadPerSec.toFixed(2)} rad/s exceeds 22 rad/s` }),
      });
    } else if (typeof metrics.maxBoneStepRad === 'number' && Number.isFinite(metrics.maxBoneStepRad)) {
      const passed = metrics.maxBoneStepRad <= 0.65;
      rows.push({
        name: `${prefix}smoothBoneMotion`,
        passed,
        expected: 'maxBoneStepRad <= 0.65 rad/frame (no 1-frame joint snaps)',
        actual: +metrics.maxBoneStepRad.toFixed(3),
        ...(passed ? {} : { reason: `Peak single-frame bone step ${metrics.maxBoneStepRad.toFixed(3)} rad exceeds 0.65 rad` }),
      });
    }
    if (typeof metrics.maxYawRadPerSec === 'number' && Number.isFinite(metrics.maxYawRadPerSec)) {
      const passed = metrics.maxYawRadPerSec <= 18;
      rows.push({
        name: `${prefix}smoothYaw`,
        passed,
        expected: 'maxYawRadPerSec <= 18 rad/s (frame-rate independent yaw-jitter guard)',
        actual: +metrics.maxYawRadPerSec.toFixed(2),
        ...(passed ? {} : { reason: `Peak yaw angular rate ${metrics.maxYawRadPerSec.toFixed(2)} rad/s exceeds 18 rad/s` }),
      });
    } else if (typeof metrics.maxYawStepRad === 'number' && Number.isFinite(metrics.maxYawStepRad)) {
      const passed = metrics.maxYawStepRad <= 0.45;
      rows.push({
        name: `${prefix}smoothYaw`,
        passed,
        expected: 'maxYawStepRad <= 0.45 rad/frame (no yaw spin-jitter)',
        actual: +metrics.maxYawStepRad.toFixed(3),
        ...(passed ? {} : { reason: `Peak single-frame yaw step ${metrics.maxYawStepRad.toFixed(3)} rad exceeds 0.45 rad` }),
      });
    }
    if (frames >= 10 && typeof metrics.overExtendedIkCount === 'number' && Number.isFinite(metrics.overExtendedIkCount)) {
      const ratio = metrics.overExtendedIkCount / frames;
      const passed = ratio <= 0.35;
      rows.push({
        name: `${prefix}ikReach`,
        passed,
        expected: 'overExtendedIkCount / frames <= 0.35 (IK hand targets within real arm reach)',
        actual: { overExtendedIkCount: metrics.overExtendedIkCount, frames, ratio: +ratio.toFixed(2) },
        ...(passed ? {} : { reason: `Arm IK targets exceeded real reach ${metrics.overExtendedIkCount} times across ${frames} frames (${(ratio * 100).toFixed(0)}%) — drive actions with native clips (playClip/playOnce) or keep IK targets inside rig.metrics arm maxReach` }),
      });
    }
  }
  return rows;
}

export function gamePlaytestAssertions(input: {before:any;after:any;clients:number;script:GameBrowserAction[];mobile:{width:number;height:number;scrollWidth:number;overflowElements?:string[]};movementThreshold?:number;expectedPhase?:string;autoJoin?:{joined:boolean;elapsedMs:number|null};selfTests?:unknown}) {
  const state=input.after?.state,players=state?.players;
  const count=players&&typeof players==='object'?Object.values(players).filter((p:any)=>p?.connected!==false).length:0;
  const self=state?.selfId,before=input.before?.state?.players?.[self],after=players?.[self];
  const scripted=input.script.some(a=>a.type==='key'&&/^(?:[wasdWASD]|Arrow(?:Up|Down|Left|Right))$/.test(a.key));
  const distance=before&&after&&[before.x,before.z,after.x,after.z].every(Number.isFinite)?Math.hypot(after.x-before.x,after.z-before.z):null;
  const phase=state?.result??state?.phase,expected=input.expectedPhase??'active game phase';
  return [
    ...(input.autoJoin?[{name:'autoJoin',passed:input.autoJoin.joined&&input.autoJoin.elapsedMs!==null&&input.autoJoin.elapsedMs<=5000,expected:'joined within 5000ms without clicks or typing',actual:input.autoJoin,reason:input.autoJoin.joined?undefined:'No joined socket message or authoritative self player before inputs'}]:[]),
    {name:'playerCount',passed:count===input.clients,expected:input.clients,actual:count,reason:state?undefined:'Missing authoritative __omGame state'},
    {name:'phase',passed:input.expectedPhase?phase===input.expectedPhase:['breather','combat','playing','explore','sandbox','win','loss','over'].includes(phase),expected,actual:phase??null},
    // movementThreshold 0 marks a game with no moving player (tap puzzles, pull-the-pin). Movement is then not asserted, and the
    // record says so; authoritative state is still required, so a missing hook or selfId fails instead of passing silently.
    input.movementThreshold===0
      ?{name:'scriptedMovement',passed:Boolean(state&&self),skipped:true,expected:'movement not asserted (threshold 0)',actual:distance,reason:state&&self?undefined:'Missing authoritative __omGame state or selfId'}
      :{name:'scriptedMovement',passed:scripted&&distance!==null&&distance>(input.movementThreshold??.5),expected:`net displacement > ${input.movementThreshold??.5} world units`,actual:distance,reason:scripted?(distance===null?'Missing selfId or authoritative coordinates':undefined):'No directional key input was scripted'},
    {name:'mobileHorizontalOverflow',passed:input.mobile.width===390&&input.mobile.height===844&&input.mobile.scrollWidth<=391&&!(input.mobile.overflowElements?.length),expected:'390x844 viewport without horizontal overflow',actual:input.mobile},
    ...normalizeKinematicsAssertions(input.after?.stats?.kinematics),
    ...normalizeSelfTestAssertions(input.selfTests),
  ];
}

export function gameTrailerComposition(game: Pick<GameCard,'title'|'description'|'controls'|'genre'|'multiplayer'|'i18n'>, clips: string[], cover: string) {
  if(clips.length<2||clips.length>3)throw new GameError('A trailer requires 2–3 gameplay clips');
  clips.forEach(cleanGamePath);cleanGamePath(cover);
  const escape=(text:string)=>text.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;');
  const title=game.i18n?.['zh-CN']?.title||game.title,description=game.i18n?.['zh-CN']?.description||game.description,controls=game.i18n?.['zh-CN']?.controls||game.controls||'WASD / arrows · Space · click / tap';
  const clipDuration=clips.length===3?4.5:5;
  const endStart=3+clips.length*clipDuration,duration=endStart+2.5;
  const captions=[gameGenreLabels[game.genre],description.slice(0,100),game.multiplayer?'Join the team':'Find your rhythm'];
  const composition={title,width:1280,height:720,fps:30,duration,cover,segments:[{kind:'title',start:0,duration:3},...clips.map((src,i)=>({kind:'gameplay',src,start:3+i*clipDuration,duration:clipDuration,caption:captions[i]})),{kind:'end',start:endStart,duration:2.5,caption:'Play now',controls}]};
  const videos=clips.map((src,i)=>`<video id="highlight-${i}" class="clip" src="${escape(src)}" data-start="${3+i*clipDuration}" data-duration="${clipDuration}" data-media-start="0" data-track-index="0" muted playsinline style="position:absolute;inset:0;width:1280px;height:720px;object-fit:cover"></video><div id="caption-${i}" class="clip caption" data-start="${3+i*clipDuration}" data-duration="${clipDuration}" data-track-index="2">${escape(captions[i])}</div>`).join('\n');
  // Multi-element cards are scenes. Their clocks are local to each mount, not root time.
  const card=(id:string,seconds:number,content:string,animation:string)=>`<template>
<style>
#${id}{position:absolute;inset:0;box-sizing:border-box;padding:100px;display:flex;flex-direction:column;justify-content:center;overflow:hidden;background:${id==='title-card'?'linear-gradient(90deg,#132033 0%,#132033cc 65%,#13203366 100%)':'#132033'};color:#edf4ff;font-family:system-ui,sans-serif}
#${id} h1{font-size:76px;line-height:1.1;margin:0 0 24px;max-width:1080px;overflow-wrap:anywhere}
#${id} p{font-size:28px;max-width:1080px;overflow-wrap:anywhere}
#${id} strong{font-size:68px;color:#78daff}
</style>
<div id="${id}" data-composition-id="${id}" data-width="1280" data-height="720" data-duration="${seconds}">${content}</div>
<script>const tl=gsap.timeline({paused:true});${animation}window.__timelines=window.__timelines||{};window.__timelines['${id}']=tl;</script>
</template>`;
  const titleCard=card('title-card',3,`<h1 id="title-text">${escape(title)}</h1><p>${escape(description.slice(0,160))}</p>`,"tl.fromTo('#title-text',{opacity:0,y:24},{opacity:1,y:0,duration:.4},.1);");
  const endCard=card('end-card',2.5,`<strong id="end-cta">Play now</strong><p>${escape(title)}</p><p>${escape(controls.slice(0,300))}</p>`,"tl.fromTo('#end-cta',{opacity:0},{opacity:1,duration:.3},0);");
  const mount=(id:string,start:number,seconds:number)=>`<div id="${id}" class="clip" data-composition-id="${id}" data-composition-src="compositions/${id}.html" data-start="${start}" data-duration="${seconds}" data-track-index="1" data-width="1280" data-height="720" style="position:absolute;inset:0;z-index:1"></div>`;
  const html=`<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>${escape(title)} · Trailer</title><script src="assets/gsap.min.js"></script><style>body{margin:0}#game-trailer{position:relative;width:1280px;height:720px;overflow:hidden;background:#132033;color:#edf4ff;font-family:system-ui,sans-serif}.caption{position:absolute;left:48px;bottom:48px;max-width:1100px;padding:14px 24px;background:#132033;font-size:30px;border-radius:12px;overflow-wrap:anywhere}</style></head><body><main id="game-trailer" data-composition-id="game-trailer" data-start="0" data-duration="${duration}" data-width="1280" data-height="720" data-fps="30"><img id="cover" class="clip" src="${escape(cover)}" data-start="0" data-duration="3" data-track-index="0" style="position:absolute;inset:0;width:1280px;height:720px;object-fit:cover">${mount('title-card',0,3)}${videos}${mount('end-card',endStart,2.5)}</main><script>const timeline=gsap.timeline({paused:true});${clips.map((_,i)=>`timeline.fromTo('#caption-${i}',{y:16},{y:0,duration:.2},${3+i*clipDuration});`).join('')}window.__timelines=window.__timelines||{};window.__timelines['game-trailer']=timeline;</script></body></html>`;
  const files=[{path:'index.html',content:html},{path:'compositions/title-card.html',content:titleCard},{path:'compositions/end-card.html',content:endCard},{path:'trailer.json',content:JSON.stringify(composition,null,2)}];
  return {composition,html,files};
}
const activeGameTrailers = new Map<string,{runId:string;promise:Promise<void>}>();
type StoredTrailer = GameTrailer & {runId:string;ownerPid?:number};
function trailerOwnerAlive(pid:number|undefined){if(pid===undefined||!Number.isInteger(pid)||pid<=0)return false;try{process.kill(pid,0);return true;}catch(error){return (error as NodeJS.ErrnoException).code==='EPERM';}}
const trailerRunning = (status:GameTrailerStatus)=>['recording','composing','rendering'].includes(status);
const publicTrailer = ({runId:_runId,ownerPid:_ownerPid,...job}:StoredTrailer):GameTrailer=>job;
export function trailerTransition(previous:GameTrailerStatus,next:GameTrailerStatus) {
  return next==='failed'&&trailerRunning(previous)||({recording:'composing',composing:'rendering',rendering:'ready'} as Record<string,string>)[previous]===next;
}

/** Wait for async loading screens (phase==="loading" or disabled #start) before starting play. */
async function waitForGameReady(page: Pick<Page, 'evaluate' | 'waitForFunction'>, waitForReadyMs = 10000) {
  if (waitForReadyMs <= 0) return;
  const needsWait = await page.evaluate(() => {
    const hook = (window as any).__omGame;
    if (hook?.getState?.()?.phase === 'loading') return true;
    const btn = document.querySelector('#start, #play, [data-action="start"]') as HTMLButtonElement | null;
    return Boolean(btn && btn.disabled);
  }).catch(() => false);
  if (!needsWait) return;
  await page.waitForFunction(() => {
    const hook = (window as any).__omGame;
    if (hook?.getState?.()?.phase === 'loading') return false;
    const btn = document.querySelector('#start, #play, [data-action="start"]') as HTMLButtonElement | null;
    return !(btn && btn.disabled);
  }, { timeout: waitForReadyMs }).catch(() => {});
}

/** Shared start convention for isolated playtests, covers and trailer recording. */
export async function startGameBrowserPage(page: Pick<Page, '$' | 'evaluate' | 'waitForFunction' | 'keyboard' | 'mouse'>, recording = false) {
  const initialTick = await page.evaluate(() => {
    const hook = (window as any).__omGame;
    return hook?.getState?.()?.tick ?? hook?.getStats?.()?.tick ?? null;
  });
  const start = await page.$('#start:not([disabled]), #play:not([disabled]), [data-action="start"]:not([disabled])');
  if (start) await start.click();
  else {
    const started = await page.evaluate(() => {
      const hook = (window as any).__omGame;
      if (typeof hook?.start !== 'function') return false;
      hook.start(); return true;
    });
    if (!started && recording) { await page.keyboard.press('Enter'); await page.keyboard.press('Space'); await page.mouse.click(640, 360); }
  }
  await page.waitForFunction((tick: number | null) => {
    const hook = (window as any).__omGame;
    if (!hook) return true; // Legacy games have no authoritative startup observation.
    const state = hook.getState?.(), current = state?.tick ?? hook.getStats?.()?.tick;
    if (tick !== null && typeof current === 'number') return current > tick;
    return state?.running === true || ['playing', 'running', 'explore', 'sandbox', 'win', 'loss'].includes(state?.phase);
  }, { timeout: 5000 }, initialTick);
}

type StoredGame = GameCard & { rawPrompt?: string; kit?: 'coop-3d' | 'arcade-2d' | 'starter'; pristineTemplateCopy?: boolean };
type GameMetaPatch = Pick<Partial<GameCard>, 'title' | 'description' | 'controls' | 'cover' | 'i18n'>;
type Viewer = { plays: number; reaction: -1 | 0 | 1; favorite: boolean };

function syncLocalizedTitles(game: StoredGame) {
  for (const translation of Object.values(game.i18n ?? {})) {
    if (translation.title !== undefined) translation.title = game.title;
  }
}

// A generated client can set document.title from its translations during startup.
const restoreGameTitleOnLoad = `<script data-openmotion-game-title>
(() => {
  const title = document.currentScript.previousElementSibling.textContent;
  window.addEventListener('load', () => setTimeout(() => { document.title = title; }), { once: true });
})();
</script>`;

async function setGameDocumentTitle(html: string, title: string, runtimeRoot: string) {
  const runtimeRequire = createRequire(path.join(runtimeRoot, 'package.json'));
  const manifest = runtimeRequire.resolve('@hyperframes/parsers/package.json');
  const pkg = JSON.parse(await readFile(manifest, 'utf8'));
  const source = path.join(path.dirname(manifest), pkg.exports['./html-attribute-spans'].import);
  const { scanHtmlOpeningTags } = await import(pathToFileURL(source).href) as typeof import('@hyperframes/parsers/html-attribute-spans');
  const tags = scanHtmlOpeningTags(html);
  const headEnd = tags.find(tag => ['body', 'svg', 'template', 'noscript'].includes(tag.name))?.start ?? html.length;
  const existing = tags.find(tag => tag.name === 'title' && tag.start < headEnd);
  const escaped = escapeHtml(title);
  if (existing && existing.rawTextEnd !== null) {
    const closing = /^<\/title\s*>/i.exec(html.slice(existing.rawTextEnd))?.[0];
    if (closing) {
      const suffix = html.slice(existing.rawTextEnd + closing.length);
      const authoredSuffix = suffix.startsWith(restoreGameTitleOnLoad) ? suffix.slice(restoreGameTitleOnLoad.length) : suffix;
      return html.slice(0, existing.end) + escaped + closing + restoreGameTitleOnLoad + authoredSuffix;
    }
  }
  const offset = tags.find(tag => tag.name === 'head' && tag.start < headEnd)?.end
    ?? tags.find(tag => tag.name === 'html' && tag.start < headEnd)?.end
    ?? (html.match(/^\s*<!doctype[^>]*>/i)?.[0].length ?? (html.startsWith('\uFEFF') ? 1 : 0));
  return html.slice(0, offset) + `<title>${escaped}</title>` + restoreGameTitleOnLoad + html.slice(offset);
}

export class GameProjects {
  root: string;
  templates: string;
  kits: string;
  /**
   * Where npm dependencies (puppeteer-core, hyperframes, gsap) are installed. Packaged builds ship without node_modules
   * and install them under the data directory (ensureRuntime), so callers pass that root; source checkouts fall back
   * to the plugin root. Native components stay under the plugin root either way.
   */
  runtimeRoot: string = pluginRoot;
  private pending: Promise<unknown> = Promise.resolve();
  private readonly hosted: HostedGameTemplates;
  constructor(workspace: string, templates = templatesRoot, kits = kitsRoot) {
    this.root = path.resolve(workspace, 'games'); this.templates = templates; this.kits = kits;
    this.hosted = new HostedGameTemplates(path.join(templates, '..', 'game-downloads.json'), path.resolve(workspace, 'game-template-cache'));
  }
  // Serialize mutations so concurrent requests cannot lose counts or race publication validation.
  mutate<T>(operation: () => Promise<T>): Promise<T> {
    const result = this.pending.then(async () => { await this.ensureStorage(); return operation(); }); this.pending = result.catch(() => {}); return result;
  }
  private async ensureStorage() {
    await mkdir(this.root, { recursive: true });
    if ((await lstat(this.root)).isSymbolicLink()) throw new GameError('Symlink games storage');
    const state = await lstat(path.join(this.root, '.state.json')).catch(e => { if (e.code === 'ENOENT') return null; throw e; });
    if (state?.isSymbolicLink()) throw new GameError('Symlink viewer state');
  }
  private async locateCard(id: string, mineOnly = false) {
    idPart(id);
    for (const [root, source] of [[this.root, 'mine'], [this.templates, 'template']] as const) {
      if (mineOnly && source !== 'mine') continue;
      const dir = path.join(root, id);
      try { await safeFile(dir, 'game.json'); return { dir, source }; }
      catch (e) { if ((e as NodeJS.ErrnoException).code !== 'ENOENT') throw e; }
    }
    throw new GameError('Game not found', 404);
  }
  async locate(id: string, mineOnly = false) {
    const card = await this.locateCard(id, mineOnly);
    return card.source === 'template' ? { ...card, dir: await this.hosted.directory(id, card.dir) } : card;
  }
  async get(id: string): Promise<GameCard> {
    await this.ensureStorage();
    const { dir, source } = await this.locateCard(id);
    const { rawPrompt: _rawPrompt, kit: _kit, trailer:_storedTrailer, pristineTemplateCopy: _pristineTemplateCopy, ...stored } = await jsonFile<StoredGame>(path.join(dir, 'game.json'));
    const state = await jsonFile<Record<string, Viewer>>(path.join(this.root, '.state.json'), {});
    const viewer = (Object.hasOwn(state, id) ? state[id] : undefined) ?? { plays: 0, reaction: 0, favorite: false };
    const trailer=await this.readTrailer(id);
    return { ...stored, ...(trailer?{trailer}:{}), remixOf: stored.remixOf ?? null, cover: stored.cover && !/^(?:[a-z]+:|\/)/i.test(stored.cover) ? `/api/games/${id}/play/${cleanGamePath(stored.cover)}` : stored.cover ?? null, id, source, playUrl: `/api/games/${id}/play/index.html`, plays: (stored.plays ?? 0) + viewer.plays, likes: (stored.likes ?? 0) + Number(viewer.reaction === 1), dislikes: (stored.dislikes ?? 0) + Number(viewer.reaction === -1), reaction: viewer.reaction, favorite: viewer.favorite };
  }
  async catalog(): Promise<GameCatalog> {
    const games: GameCard[] = [], issues: GameCatalogIssue[] = [];
    for (const root of [this.templates, this.root]) {
      const entries = await readdir(root, { withFileTypes: true }).catch(e => { if (e.code === 'ENOENT') return []; throw e; });
      // One unreadable folder (an interrupted create, a malformed game.json) is reported, not allowed to hide every other game.
      for (const entry of entries) if (entry.isDirectory() && !entry.name.startsWith('.')) {
        try { games.push(await this.get(entry.name)); }
        catch (error) { issues.push({ id: entry.name, message: (error as Error).message }); }
      }
    }
    games.sort(compareGameCatalogOrder);
    return issues.length ? { games, issues } : { games };
  }
  /** Run a project-creating step; a failure removes the partly written folder so it never becomes an orphan. */
  private async populate<T>(dir: string, run: () => Promise<T>): Promise<T> {
    await mkdir(dir, { recursive: true });
    try { return await run(); }
    catch (error) { await rm(dir, { recursive: true, force: true }).catch(() => undefined); throw error; }
  }
  async create(raw: GameBrief): Promise<GameCreated> { return this.mutate(async () => {
    const brief = briefInput(raw), id = randomUUID(), dir = path.join(this.root, id), now = new Date().toISOString();
    // Append canonical portrait-layout and playable-ad paragraphs; the card keeps orientation/playableAd metadata for stage & tags.
    const rawPrompt = formatGameBriefPrompt(brief.prompt, brief);
    const game: StoredGame = { rawPrompt, orientation: brief.orientation, ...(brief.playableAd ? { playableAd: true } : {}), id, title: brief.prompt.slice(0,80), description: brief.prompt, genre: brief.genre ?? 'casual', style: brief.style, setting: brief.setting, multiplayer: brief.multiplayer, maxPlayers: brief.multiplayer ? 4 : 1, status: 'draft', cover: null, playUrl: `/api/games/${id}/play/index.html`, plays: 0, likes: 0, dislikes: 0, reaction: 0, favorite: false, source: 'mine', remixOf: null, controls: '', createdAt: now, updatedAt: now };
    return this.populate(dir, async () => {
    // Multiplayer briefs with no genre ("play with friends") or a shooter/3D brief get the co-op room kit; other multiplayer
    // genres keep the room-ready starter until a matching kit exists. arcade-2d is single-player only.
    const coop = brief.multiplayer && (brief.genre === 'shooter' || brief.genre === null || brief.style === '3d');
    const arcade = !brief.multiplayer && await Promise.all(['index.html', 'logic.js'].map(async file => {
      try { return (await lstat(await safeFile(path.join(this.kits, 'arcade-2d'), file))).isFile(); }
      catch (error) { if ((error as NodeJS.ErrnoException).code === 'ENOENT') return false; throw error; }
    })).then(files => files.every(Boolean));
    game.kit = coop ? 'coop-3d' : arcade ? 'arcade-2d' : 'starter';
    if (game.kit !== 'starter') {
      const folders = coop ? ['coop-3d', 'vendor', 'characters'] : ['arcade-2d', ...(brief.style === '3d' ? ['vendor'] : [])];
      for (const folder of folders) {
        for (const file of await inventory(path.join(this.kits, folder))) {
          const relative = folder === game.kit ? file.path : folder + '/' + file.path;
          const target = path.join(dir, relative);
          await mkdir(path.dirname(target), { recursive: true });
          await writeFile(target, await readFile(await safeFile(path.join(this.kits, folder), file.path)));
        }
      }
      if (coop) game.controls = 'WASD/arrows or touch joystick; mouse aim/fire; auto-fire without aim; defend the crystal.';
    } else for (const file of starter(brief.multiplayer)) await writeFile(path.join(dir, file.path), file.content);
    await this.save(id, game);
    return { game: await this.get(id), agentInstruction: instruction(game, { ...brief, prompt: rawPrompt }) };
    });
  }); }
  private async save(id: string, game: StoredGame) {
    idPart(id);
    const { reaction: _reaction, favorite: _favorite, trailer:_trailer, ...stored } = game;
    await saveJson(await safeFile(path.join(this.root, id), 'game.json', true), { ...stored, id });
  }
  private async builtInTemplateOrigin(id: string | null | undefined): Promise<StoredGame | null> {
    if (!id) return null;
    try {
      const { dir, source } = await this.locateCard(id);
      const stored = await jsonFile<StoredGame>(path.join(dir, 'game.json'));
      return isReadyBuiltInTemplate({ ...stored, source }) ? stored : null;
    } catch {
      return null;
    }
  }
  async remix(id: string, rawOverrides?: GameRemixOptions): Promise<GameCreated> { return this.mutate(async () => {
    const overrides = remixOverridesInput(rawOverrides);
    const original = await this.get(id);
    assertSinglePlayerAuthoring(original.multiplayer);
    const { dir, source } = await this.locate(id), newId = randomUUID(), target = path.join(this.root, newId);
    return this.populate(target, async () => {
    for (const file of await inventory(dir)) { if (isPublishRecord(file.path)) continue; const dest = path.join(target, file.path); await mkdir(path.dirname(dest), { recursive: true }); await writeFile(dest, await readFile(await safeFile(dir, file.path))); }
    const originalMeta = await jsonFile<StoredGame>(path.join(dir, 'game.json'));
    const readyBuiltInTemplate = isReadyBuiltInTemplate({ ...originalMeta, source, external: original.external });
    const genre = overrides.genre ?? original.genre;
    const style = overrides.style ?? original.style;
    const setting = overrides.setting ?? original.setting;
    const orientation = overrides.orientation ?? original.orientation;
    const playableAd = orientation === 'landscape' ? false : original.playableAd;
    const hasLayoutChange = orientation !== original.orientation || playableAd !== original.playableAd;
    const rawPrompt = hasLayoutChange || originalMeta.rawPrompt
      ? formatGameBriefPrompt(originalMeta.rawPrompt ?? original.description, { orientation, playableAd })
      : originalMeta.rawPrompt;
    // A remix preserves the original brief unless explicit overrides update genre, style, setting, or screen layout.
    // Built-in templates keep their clean title so zero-edit deliveries read like a finished game without a "remix" suffix.
    const now = new Date().toISOString();
    const game: StoredGame = { ...original, genre, style, setting, orientation, playableAd, titleCustomized: undefined, tags: undefined, kit: originalMeta.kit, cover: originalMeta.cover ?? null, ...(rawPrompt ? { rawPrompt } : {}), ...(readyBuiltInTemplate ? { pristineTemplateCopy: true } : {}), id: newId, title: readyBuiltInTemplate ? original.title : `${original.title.slice(0,72)} remix`, source: 'mine' as const, status: 'draft' as const, plays: 0, likes: 0, dislikes: 0, reaction: 0 as const, favorite: false, remixOf: id, createdAt: now, updatedAt: now };
    await this.save(newId, game);
    const templateContext: TemplateInstructionContext | undefined = readyBuiltInTemplate
      ? { readyBuiltInTemplate: true, templateOverrides: templateOverrideSummary(originalMeta, game) }
      : undefined;
    return { game: await this.get(newId), agentInstruction: instruction(game, { prompt: rawPrompt ?? original.description, genre, style, setting, multiplayer: original.multiplayer, orientation, playableAd }, true, templateContext) };
    });
  }); }
  /** The complete Agent handoff for a workspace draft: game id, brief and execution steps, available at any time (not only right after creation). */
  async handoff(id: string): Promise<GameHandoff> {
    const { dir } = await this.locate(id, true);
    const stored = await jsonFile<StoredGame>(path.join(dir, 'game.json'));
    if (stored.source !== 'mine') throw new GameError('Only workspace games can be handed to an Agent');
    assertSinglePlayerAuthoring(stored.multiplayer);
    const game = await this.get(id);
    const prompt = formatGameBriefPrompt(stored.rawPrompt ?? stored.description, { orientation: stored.orientation, playableAd: stored.playableAd });
    const brief: GameBrief = { prompt, genre: stored.genre, style: stored.style, setting: stored.setting, multiplayer: stored.multiplayer, orientation: stored.orientation, playableAd: stored.playableAd };
    const templateOrigin = await this.builtInTemplateOrigin(stored.remixOf);
    const copyEligibleForFastPath = Boolean(templateOrigin)
      && ((stored.status === 'draft' && stored.pristineTemplateCopy === true)
        || stored.status === 'ready'
        || stored.status === 'published');
    const templateContext: TemplateInstructionContext | undefined = copyEligibleForFastPath && templateOrigin
      ? { readyBuiltInTemplate: true, templateOverrides: templateOverrideSummary(templateOrigin, stored) }
      : undefined;
    return { gameId: id, status: game.status, agentInstruction: instruction(game, brief, Boolean(stored.remixOf), templateContext) };
  }
  async interact(id: string, kind: 'play'|'reaction'|'favorite', value?: unknown) { return this.mutate(async () => {
    await this.get(id);
    const state = await jsonFile<Record<string, Viewer>>(path.join(this.root, '.state.json'), {});
    const viewer = (Object.hasOwn(state, id) ? state[id] : undefined) ?? { plays: 0, reaction: 0, favorite: false };
    if (kind === 'play') viewer.plays++;
    if (kind === 'reaction') { if (value !== -1 && value !== 0 && value !== 1) throw new GameError('reaction must be -1, 0 or 1'); viewer.reaction = value; }
    if (kind === 'favorite') { if (typeof value !== 'boolean') throw new GameError('favorite must be boolean'); viewer.favorite = value; }
    state[id] = viewer; await saveJson(path.join(this.root, '.state.json'), state); return this.get(id);
  }); }
  async delete(id: string) { return this.mutate(async () => {
    const { dir } = await this.locate(id, true); await rm(dir, { recursive: true });
    const state = await jsonFile<Record<string, Viewer>>(path.join(this.root, '.state.json'), {}); delete state[id]; await saveJson(path.join(this.root, '.state.json'), state); return { deleted: true, id };
  }); }
  async detail(id: string) { const game = await this.get(id); return { ...game, files: await inventory((await this.locate(id)).dir) }; }
  async exportZip(id: string): Promise<{ filename: string; data: Buffer }> {
    const offlineServeScript = `import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import zlib from 'node:zlib';
import { exec } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = path.dirname(fileURLToPath(import.meta.url));
const MIME = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8', '.json': 'application/json', '.svg': 'image/svg+xml',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.gif': 'image/gif',
  '.glb': 'model/gltf-binary', '.gltf': 'model/gltf+json', '.wasm': 'application/wasm',
  '.mp3': 'audio/mpeg', '.ogg': 'audio/ogg', '.wav': 'audio/wav', '.m4a': 'audio/mp4', '.mp4': 'video/mp4', '.webm': 'video/webm',
  '.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf',
};
const COMPRESS = new Set(['.html', '.js', '.mjs', '.css', '.json', '.svg', '.glb', '.gltf', '.wasm']);

const server = http.createServer(async (req, res) => {
  try {
    const urlPath = decodeURIComponent(new URL(req.url || '/', 'http://127.0.0.1').pathname);
    const rel = urlPath === '/' ? 'index.html' : urlPath.replace(/^\\/+/, '');
    const target = path.resolve(root, rel);
    if (!target.startsWith(root + path.sep) && target !== root) { res.writeHead(403); res.end(); return; }
    const data = await fs.readFile(target);
    const ext = path.extname(target).toLowerCase();
    const headers = { 'Content-Type': MIME[ext] || 'application/octet-stream', 'Cache-Control': ext === '.html' ? 'no-cache' : 'public, max-age=3600' };
    if (COMPRESS.has(ext) && /gzip/i.test(String(req.headers['accept-encoding'] || '')) && data.length > 1024) {
      const gz = zlib.gzipSync(data, { level: 6 });
      res.writeHead(200, { ...headers, 'Content-Encoding': 'gzip', 'Content-Length': gz.length });
      res.end(gz);
      return;
    }
    res.writeHead(200, { ...headers, 'Content-Length': data.length });
    res.end(data);
  } catch {
    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end('Not found');
  }
});

let port = Number(process.env.PORT) || 8765;
server.on('error', err => {
  if (err && err.code === 'EADDRINUSE' && port < 8799) { server.listen(++port, '127.0.0.1'); return; }
  console.error(err); process.exit(1);
});
server.listen(port, '127.0.0.1', () => {
  const url = \`http://127.0.0.1:\${port}/\`;
  console.log('Game server running at ' + url);
  if (process.argv.includes('--open')) {
    const cmd = process.platform === 'darwin' ? \`open "\${url}"\` : process.platform === 'win32' ? \`start "" "\${url}"\` : \`xdg-open "\${url}"\`;
    exec(cmd, () => {});
  }
});
`;
    const offlineMacLauncher = `#!/bin/bash\ncd "$(dirname "$0")"\nif command -v node >/dev/null 2>&1; then\n  node serve.mjs --open\nelif command -v python3 >/dev/null 2>&1; then\n  (sleep 1 && open "http://127.0.0.1:8765/") &\n  python3 -m http.server 8765 --bind 127.0.0.1\nelse\n  echo "Please install Node.js or Python 3 to run the local game server."\nfi\n`;
    const offlineWinLauncher = `@echo off\r\ncd /d "%~dp0"\r\nwhere node >nul 2>nul\r\nif %errorlevel%==0 (\r\n  node serve.mjs --open\r\n) else (\r\n  start "" "http://127.0.0.1:8765/"\r\n  py -m http.server 8765 --bind 127.0.0.1\r\n)\r\n`;
    const offlinePlayReadme = `Play this game locally\n======================\nBrowsers block ES modules and 3D assets when opening index.html directly via file://.\n\n- macOS: double-click Start-Mac.command (or run: node serve.mjs --open)\n- Windows: double-click Start-Windows.bat (or run: node serve.mjs --open)\n- Any OS: run "node serve.mjs" and open the printed http://127.0.0.1 URL.\n`;
    const game = await this.get(id);
    const { dir } = await this.locate(id);
    const maxExportBytes = 64 * 1024 * 1024;
    let entries: { name: string; data: Buffer }[];
    try {
      const bundle = await buildPublishBundle({
        dataDirectory: path.dirname(this.root),
        kind: 'game',
        targetId: id,
        sourcePath: dir,
        entryPath: 'index.html',
        maxBytes: maxExportBytes,
      });
      entries = bundle.files.map(item => ({ name: item.file, data: item.data }));
    } catch (error) {
      if (!/Entry HTML file "index\.html" does not exist/i.test((error as Error).message)) {
        if (/exceeds .* MiB limit/i.test((error as Error).message)) throw new GameError('Game export exceeds 64 MiB limit', 413);
        throw error;
      }
      const files = await inventory(dir);
      let total = 0;
      entries = [];
      for (const item of files) {
        // WeChat publish progress belongs to this computer, not to the game source.
        if (isPublishRecord(item.path)) continue;
        if (/^(?:game\.json$|(?:trailer|design|assets\/playtests|assets-raw)(?:\/|$))/i.test(item.path)) continue;
        total += item.bytes;
        if (total > maxExportBytes) throw new GameError('Game export exceeds 64 MiB limit', 413);
        entries.push({ name: item.path, data: await readFile(await safeFile(dir, item.path)) });
      }
    }
    const existing = new Set(entries.map(e => e.name.toLowerCase()));
    for (const [name, content] of [
      ['serve.mjs', offlineServeScript],
      ['Start-Mac.command', offlineMacLauncher],
      ['Start-Windows.bat', offlineWinLauncher],
      ['PLAY-README.txt', offlinePlayReadme],
    ] as const) {
      if (!existing.has(name.toLowerCase())) entries.push({ name, data: Buffer.from(content, 'utf8') });
    }
    const slug = (game.title || game.id)
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '')
      .slice(0, 60) || game.id;
    return { filename: `${slug}.zip`, data: zip(entries) };
  }
  async read(id: string, relative: string) {
    if (!textExtensions.test(relative) || relative.toLowerCase() === 'game.json' || relative.toLowerCase().startsWith('trailer/')) throw new GameError('Only game text source may be read');
    const file = await safeFile((await this.locate(id)).dir, relative);
    if ((await lstat(file)).size > LIMIT) throw new GameError('Text file exceeds 8 MiB');
    return { path: relative, content: await readFile(file, 'utf8') };
  }
  async rename(id: string, title: string) {
    return this.mutate(async () => {
      const { dir } = await this.locate(id, true);
      const entry = await this.read(id, 'index.html').catch(error => {
        if (error.code === 'ENOENT') return undefined;
        throw error;
      });
      return this.writeSourceFiles(id, dir, entry ? [entry] : [], title);
    });
  }
  async write(id: string, files: { path: string; content: string }[]) {
    return this.mutate(async () => {
      const { dir } = await this.locate(id, true);
      return this.writeSourceFiles(id, dir, files);
    });
  }
  private async writeSourceFiles(id: string, dir: string, files: { path: string; content: string }[], title?: string) {
    if (!Array.isArray(files) || (!files.length && title === undefined) || files.length > 100) throw new GameError('Write 1–100 files');
    const stored = await jsonFile<StoredGame>(path.join(dir, 'game.json'));
    if (title !== undefined) {
      stored.title = title;
      stored.titleCustomized = true;
      syncLocalizedTitles(stored);
    }
    let bytes = 0;
    const targets: { file: string; content: string; previous: boolean }[] = [];
    const names = files.map(file => cleanGamePath(file?.path).toLowerCase());
    for (let i = 0; i < names.length; i++) for (let j = 0; j < i; j++) {
      if (names[i] === names[j] || names[i].startsWith(names[j] + '/') || names[j].startsWith(names[i] + '/')) throw new GameError('Conflicting or duplicate source paths');
    }
    for (const [i, file] of files.entries()) {
      if (!file || typeof file.content !== 'string' || !textExtensions.test(file.path) || names[i] === 'game.json' || names[i] === 'trailer' || names[i].startsWith('trailer/')) throw new GameError('Only game text source may be written');
      let content = file.content;
      if (stored.titleCustomized && file.path === 'index.html') {
        const runtimeRoot = this.runtimeRoot === pluginRoot ? await ensureRuntime(path.dirname(this.root), false) : this.runtimeRoot;
        content = await setGameDocumentTitle(content, stored.title, runtimeRoot);
      }
      bytes += Buffer.byteLength(content); if (bytes > LIMIT) throw new GameError('Write exceeds 8 MiB');
      const target = await safeFile(dir, file.path, true);
      const info = await lstat(target).catch(error => { if (error.code === 'ENOENT') return null; throw error; });
      if (info && !info.isFile()) throw new GameError('Source path conflicts with an existing directory');
      targets.push({ file: target, content, previous: !!info });
    }
    stored.updatedAt = new Date().toISOString();
    if (title === undefined) {
      delete stored.pristineTemplateCopy;
      if (stored.status === 'published' || stored.status === 'ready') stored.status = 'building';
    }
    const staging = await mkdtemp(path.join(dir, '.write-')), committed: number[] = [], directories: string[] = [];
    let keepRecovery = false, metadataAttempted = false;
    try {
      await copyFile(await safeFile(dir, 'game.json'), path.join(staging, 'metadata'));
      // Stage complete source bytes and backups before changing any live file.
      for (const [i, target] of targets.entries()) {
        await writeFile(path.join(staging, 'new-' + i), target.content);
        if (target.previous) await copyFile(target.file, path.join(staging, 'old-' + i));
      }
      for (const [i, target] of targets.entries()) {
        const missing: string[] = [];
        for (let parent = path.dirname(target.file); parent !== dir; parent = path.dirname(parent)) {
          const info = await lstat(parent).catch(error => { if (error.code === 'ENOENT') return null; throw error; });
          if (info) { if (!info.isDirectory() || info.isSymbolicLink()) throw new GameError('Source directory conflict'); break; }
          missing.push(parent);
        }
        for (const parent of missing.reverse()) { await mkdir(parent); directories.push(parent); }
        await rename(path.join(staging, 'new-' + i), target.file); committed.push(i);
      }
      // Metadata is the final commit step; a failure restores the entire source batch.
      metadataAttempted = true;
      await this.save(id, stored);
      return await this.detail(id);
    } catch (error) {
      const failures: unknown[] = [];
      if (metadataAttempted) try { await rename(path.join(staging, 'metadata'), path.join(dir, 'game.json')); } catch (failure) { failures.push(failure); }
      for (const i of committed.reverse()) try {
        if (targets[i].previous) await rename(path.join(staging, 'old-' + i), targets[i].file);
        else await rm(targets[i].file, { force: true });
      } catch (failure) { failures.push(failure); }
      for (const parent of directories.reverse()) try { await rmdir(parent); } catch (failure) { failures.push(failure); }
      if (failures.length) { keepRecovery = true; throw new AggregateError([error, ...failures], 'Source rollback failed; recovery backups retained in ' + staging); }
      throw error;
    } finally { if (!keepRecovery) await rm(staging, { recursive: true, force: true }); }
  }
  async updateMeta(id: string, patch: GameMetaPatch) { return this.mutate(async () => {
    const { dir } = await this.locate(id, true);
    if (!patch || typeof patch !== 'object' || Array.isArray(patch) || Object.keys(patch).some(key => !['title','description','controls','cover','i18n'].includes(key))) throw new GameError('Invalid metadata fields');
    const text = (key: string, value: unknown) => {
      const limit = key === 'title' ? 200 : key === 'controls' ? 4000 : 20000;
      if (typeof value !== 'string' || !value.trim() || value.length > limit) throw new GameError(`Invalid metadata ${key} (1–${limit} characters)`);
      return value.trim();
    };
    const changes: GameMetaPatch = {};
    for (const key of ['title','description','controls'] as const) if (Object.hasOwn(patch,key)) changes[key] = text(key,patch[key]);
    if (Object.hasOwn(patch,'cover')) {
      const cover = cleanGamePath(patch.cover);
      if (/[?#]/.test(cover) || !/\.(?:png|jpe?g|webp|avif|gif|svg|ico)$/i.test(cover)) throw new GameError('cover must be a project-relative image path');
      if (!(await lstat(await safeFile(dir,cover))).isFile()) throw new GameError('cover must be an existing game image file');
      assertGameCoverSize(gameCoverDimensions(await readFile(await safeFile(dir,cover)),path.extname(cover)));
      changes.cover = cover;
    }
    if (Object.hasOwn(patch,'i18n')) {
      if (!patch.i18n || typeof patch.i18n !== 'object' || Array.isArray(patch.i18n) || Object.keys(patch.i18n).length > 50) throw new GameError('Invalid metadata i18n');
      changes.i18n = {};
      for (const [locale, translation] of Object.entries(patch.i18n)) {
        if (!/^[a-zA-Z]{2,8}(?:-[a-zA-Z0-9]{1,8})*$/.test(locale) || !translation || typeof translation !== 'object' || Array.isArray(translation) || Object.keys(translation).some(key => !['title','description','controls'].includes(key))) throw new GameError('Invalid metadata locale or translation');
        const result: { title?: string; description?: string; controls?: string } = {};
        for (const key of ['title','description','controls'] as const) if (Object.hasOwn(translation,key)) result[key] = text(key,translation[key]);
        changes.i18n[locale] = result;
      }
    }
    const game = await jsonFile<StoredGame>(path.join(dir,'game.json'));
    game.rawPrompt ??= game.description;
    // Merge locale fields so updating Chinese controls does not erase other translations.
    if (changes.i18n) {
      const translations = { ...game.i18n };
      for (const [locale, translation] of Object.entries(changes.i18n)) translations[locale] = { ...translations[locale], ...translation };
      changes.i18n = translations;
    }
    if (game.titleCustomized) delete changes.title;
    Object.assign(game,changes);
    if (game.titleCustomized) syncLocalizedTitles(game);
    game.updatedAt = new Date().toISOString();
    await this.save(id, game); return this.get(id);
  }); }
  async validate(id: string) {
    const game = await this.get(id), diagnostics: { path: string; message: string }[] = [], warnings: string[] = [];
    const { dir } = await this.locate(id);
    // Playable ads may name app-store destinations for a user-initiated CTA.
    const allowedHosts = game.playableAd ? adStoreHosts : gameCdnHosts;
    for(const file of ['design/plan.md','design/assets.csv','design/verification.md'])try{await this.read(id,file);}catch(error){warnings.push(`Missing or unreadable ${file}: ${(error as Error).message}`);}
    if(!game.cover) warnings.push('No cover image is set; use openmotion_game_capture_cover.');
    let entryScripts: string[] = [];
    let inlineScripts: string[] = [];
    for (const relative of ['index.html','client.js']) try {
      const source = (await this.read(id, relative)).content;
      if (relative === 'index.html') {
        const deps = await gameEntryDependencies(source, dir, game, this.runtimeRoot);
        entryScripts = deps.entryScripts;
        inlineScripts = deps.inlineScripts;
        for (const message of deps.errors) {
          diagnostics.push({ path: relative, message });
        }
      }
      if(game.multiplayer)for(const message of gameRoomEntryErrors(source))diagnostics.push({path:relative,message});
      diagnostics.push(...findDisallowedHostDiagnostics(relative, source, allowedHosts));
    } catch (e) {
      if (relative !== 'client.js' || (e as NodeJS.ErrnoException).code !== 'ENOENT') diagnostics.push({ path: relative, message: (e as Error).message });
    }
    const moduleGraph = await inspectLocalModuleGraph(dir, entryScripts, inlineScripts, allowedHosts);
    diagnostics.push(...moduleGraph.diagnostics);
    if(game.multiplayer){
      let client='';try{client=(await this.read(id,'client.js')).content;}catch{}
      if(!client)try{client=(await this.read(id,'index.html')).content;}catch{}
      if(!readsRoomQuery(client))warnings.push('Client does not read the room query parameter; auto-join from ?room= on load is required.');
    }
    const { kit } = await jsonFile<StoredGame>(path.join(dir, 'game.json'));
    // Older projects have no kit marker; preserve their multiplayer comparison.
    const baseline = kit === 'coop-3d' || kit === 'arcade-2d' ? kit : !kit && game.multiplayer ? 'coop-3d' : null;
    const hasCustomEntry = !game.multiplayer && entryScripts.length > 0 && !moduleGraph.importsLogic;
    // Adaptive logic.js check:
    // - Multiplayer games and games whose entry/module graph imports logic.js require valid deterministic logic.js.
    // - Solo games with custom modular ESM entries that do not import logic.js are allowed to omit logic.js
    //   (or leave an untouched starter logic.js unused) without false validation errors or starter warnings.
    let logic: string | null = null;
    try { logic = (await this.read(id, 'logic.js')).content; }
    catch (e) {
      const logicRequired = game.multiplayer || moduleGraph.importsLogic || (Boolean(baseline) && !hasCustomEntry);
      if (logicRequired || (e as NodeJS.ErrnoException).code !== 'ENOENT') diagnostics.push({ path: 'logic.js', message: (e as Error).message });
    }
    let isUnusedStarterLogic = false;
    if (baseline && logic !== null) try {
      const kitSource = await readFile(path.join(this.kits, baseline, 'logic.js'), 'utf8');
      const changed = gameChangedLines(logic, kitSource);
      if (hasCustomEntry && changed === 0) {
        isUnusedStarterLogic = true;
      } else if (changed < 20) {
        warnings.push('Gameplay still equals the starter kit (fewer than 20 approximate changed lines); implement and playtest the requested mechanics.');
      }
    } catch (error) {
      warnings.push(`Starter kit comparison unavailable: ${(error as Error).message}`);
    }
    if (logic !== null && !isUnusedStarterLogic) try {
      const runtime = new GameRuntime(logic, 'validation');
      const players = game.multiplayer ? ['one','two'] : Array.from({ length: Math.max(1, runtime.meta.minPlayers) }, (_, i) => 'player-' + (i + 1));
      runtime.setup(players);
      for (let tick = 0; tick < 50; tick++) { runtime.tick(tick); for (const player of players) { runtime.apply(player, { type: 'noop' }, game.multiplayer); runtime.view(player); } if (runtime.over().over) break; }
    } catch (e) { diagnostics.push({ path: 'logic.js', message: (e as Error).message }); }
    if (game.style === '3d' || moduleGraph.importsThree) {
      const hasFixedLogicTick = (logic !== null && !isUnusedStarterLogic)
        || [...moduleGraph.moduleSources.values()].some(src => /\btickRate\b|1\s*\/\s*(?:20|30)\b/.test(src));
      warnings.push(...inspect3dKinematicsWarnings(moduleGraph.moduleSources, { hasFixedLogicTick }));
    }
    return { id, passed: diagnostics.length === 0, diagnostics, warnings };
  }
  async status(id: string, status: unknown) { return this.mutate(async () => {
    if (typeof status !== 'string' || !['building','ready','failed'].includes(status)) throw new GameError('Invalid game status');
    const { dir } = await this.locate(id, true), game = await jsonFile<StoredGame>(path.join(dir,'game.json'));
    if (status === 'building' || status === 'failed') delete game.pristineTemplateCopy;
    game.status = status as GameCard['status']; game.updatedAt = new Date().toISOString(); await this.save(id, game); return this.get(id);
  }); }
  async publish(id: string) { return this.mutate(async () => {
    const { dir } = await this.locate(id, true), validation = await this.validate(id);
    if (!validation.passed) throw new GameError('Game validation failed: ' + JSON.stringify(validation.diagnostics), 409);
    const game = await jsonFile<StoredGame>(path.join(dir,'game.json'));
    const warnings: string[] = [...validation.warnings];
    const prompt = game.rawPrompt ?? game.description;
    if (game.title === prompt || game.title === prompt.slice(0,80)) warnings.push('The title still matches the raw prompt; set a concise title with openmotion_game_update_meta.');
    if (game.multiplayer) game.maxPlayers = new GameRuntime((await this.read(id,'logic.js')).content, 'publication').meta.maxPlayers;
    game.status = 'published'; game.updatedAt = new Date().toISOString(); await this.save(id, game);
    let plan='';try{plan=(await this.read(id,'design/plan.md')).content;}catch{/* Optional planning input; missing artifacts already have validation reminders. */}
    const nextSteps=gameNextSteps(plan);nextSteps[2]='Make a gameplay trailer for this game with openmotion_game_trailer.';
    const card = await this.get(id); return { game: card, playUrl: card.playUrl, warnings, nextSteps, ...(card.multiplayer ? { roomInviteUrlPattern: card.playUrl + '?room={room}' } : {}) };
  }); }
  async simulate(id: string, options: {players:number;scripts:GameSimulationScripts;maxTicks:number}) {
    const {players,maxTicks,scripts}=options;
    if(!Number.isInteger(players)||players<1||players>4)throw new GameError('players must be 1–4');
    if(!Number.isInteger(maxTicks)||maxTicks<1||maxTicks>10000)throw new GameError('maxTicks must be 1–10000');
    let logicSource: string;
    try { logicSource = (await this.read(id, 'logic.js')).content; }
    catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') throw new GameError('This game does not use a deterministic logic.js module; verify gameplay invariants through openmotion_game_playtest and window.__omGame.runSelfTests().', 400);
      throw error;
    }
    const runtime=new GameRuntime(logicSource,'game-simulation');
    if(players<runtime.meta.minPlayers||players>runtime.meta.maxPlayers)throw new GameError('Player count is outside the logic meta limits');
    const ids=Array.from({length:players},(_,i)=>'player-'+(i+1));runtime.setup(ids);
    const choices=typeof scripts==='string'?Array(players).fill(scripts):scripts;
    if(!Array.isArray(choices)||choices.length!==players)throw new GameError('Supply one simulation route per player');
    const routes=choices.map((route,i)=>validateSimulationRoute(route==='idle'?[]:route==='reference'?runtime.referenceRoute(i):route));
    const actionCount=routes.reduce((total,route)=>total+route.reduce((sum,step)=>sum+Math.max(0,Math.min(maxTicks,step.toTick)-step.fromTick+1),0),0);
    if(actionCount>100000)throw new GameError('Simulation exceeds 100000 scripted input applications');
    const timeline:{tick:number;state:unknown}[]=[{tick:0,state:runtime.summary(ids[0])}];
    let tick=0,last=JSON.stringify(timeline[0].state),lastKey=simulationMilestone(timeline[0].state);
    const sampleEvery=Math.max(1,Math.ceil(maxTicks/50));
    for(tick=1;tick<=maxTicks;tick++){
      runtime.tick(tick);
      for(let i=0;i<ids.length;i++)for(const step of routes[i])if(tick>=step.fromTick&&tick<=step.toTick)runtime.apply(ids[i],step.action);
      const over=runtime.over();
      if(tick%sampleEvery===0||over.over){const state=runtime.summary(ids[0]),serialized=JSON.stringify(state);if(serialized!==last||over.over){timeline.push({tick,state});last=serialized;lastKey=simulationMilestone(state);}}
      else {const state=runtime.summary(ids[0]),key=simulationMilestone(state);if(key!==lastKey){timeline.push({tick,state});lastKey=key;last=JSON.stringify(state);}}
      if(timeline.length>100)timeline.splice(1,1);
      if(over.over)break;
    }
    tick=Math.min(tick,maxTicks);
    if(timeline.at(-1)?.tick!==tick){if(timeline.length>=100)timeline.splice(1,1);timeline.push({tick,state:runtime.summary(ids[0])});}
    return {id,players,maxTicks,result:{...runtime.over(),tick},timeline,scope:'Deterministic logic-only simulation with ordinary validated inputs; not browser, rendering or human acceptance.'};
  }
  private async trailerStorage(id:string,create=false) {
    const located=await this.locateCard(id),workspace=path.dirname(this.root);
    const root=located.source==='mine'?located.dir:path.join(workspace,'game-trailers',id);
    if(create){
      await safeFile(located.source==='mine'?root:workspace,located.source==='mine'?'trailer/job.json':`game-trailers/${id}/trailer/job.json`,true);
      await mkdir(path.join(root,'trailer'),{recursive:true});
    }
    return root;
  }
  private async readTrailer(id:string):Promise<GameTrailer|null> {
    const root=await this.trailerStorage(id);
    let job:StoredTrailer;
    try{job=await jsonFile<StoredTrailer>(await safeFile(root,'trailer/job.json'));}
    catch(error){if((error as NodeJS.ErrnoException).code==='ENOENT')return null;throw error;}
    if(trailerRunning(job.status)&&activeGameTrailers.get(root)?.runId!==job.runId&&!trailerOwnerAlive(job.ownerPid)){
      job={...job,status:'failed',error:'Trailer interrupted by a service restart. Start again; existing clips were preserved.',updatedAt:new Date().toISOString()};
      await saveJson(await safeFile(root,'trailer/job.json',true),job);
    }
    return publicTrailer(job);
  }
  async trailer(id:string):Promise<GameTrailer> {
    const job=await this.readTrailer(id);if(!job)throw new GameError('No trailer job exists for this game',404);return job;
  }
  private async updateTrailer(id:string,runId:string,patch:Partial<GameTrailer>) {
    const root=await this.trailerStorage(id),file=await safeFile(root,'trailer/job.json');
    const job=await jsonFile<StoredTrailer>(file);
    if(job.runId!==runId||activeGameTrailers.get(root)?.runId!==runId)return;
    if(patch.status&&patch.status!==job.status&&!trailerTransition(job.status,patch.status))throw new GameError(`Invalid trailer transition: ${job.status} → ${patch.status}`);
    await saveJson(file,{...job,...patch,updatedAt:new Date().toISOString()});
  }
  async startTrailer(id:string):Promise<GameTrailer> {return this.mutate(()=>new WorkspaceStore(path.dirname(this.root)).lock(async()=>{
    const game=await this.get(id);
    if(!['ready','published'].includes(game.status))throw new GameError('The game must be ready or published before recording a trailer',409);
    if(game.external)throw new GameError('External games cannot be recorded locally. Import a playable local game first.',409);
    const validation=await this.validate(id);if(!validation.passed)throw new GameError('Game validation failed before trailer recording: '+JSON.stringify(validation.diagnostics),409);
    const root=await this.trailerStorage(id,true);
    if(game.trailer&&trailerRunning(game.trailer.status))return this.trailer(id);
    const runId=randomUUID(),job:StoredTrailer={runId,ownerPid:process.pid,status:'recording',progress:0,clips:[],updatedAt:new Date().toISOString()};
    await saveJson(await safeFile(root,'trailer/job.json',true),job);
    const promise=Promise.resolve().then(async()=>{
      try{
        const clips=await this.recordTrailer(id,root,runId,async current=>this.updateTrailer(id,runId,{progress:.1+current.length*.08,clips:current.map(file=>`/api/games/${id}/play/${file}`)}));
        await this.updateTrailer(id,runId,{status:'composing',progress:.4});
        const projectId=await this.composeTrailer(game,root,clips,async projectId=>this.updateTrailer(id,runId,{projectId}));
        await this.updateTrailer(id,runId,{status:'rendering',progress:.7,projectId});
        const rendered=await this.renderTrailer(projectId);
        const output=await safeFile(root,'trailer/trailer.mp4',true);await copyFile(rendered,output);
        await this.updateTrailer(id,runId,{status:'ready',progress:1,videoUrl:`/api/games/${id}/play/trailer/trailer.mp4`});
      }catch(error){const stage=(await this.readTrailer(id))?.status??'Trailer';await this.updateTrailer(id,runId,{status:'failed',error:(stage+' failed: '+(error instanceof Error?error.message:String(error))).slice(0,2000)});}
    }).finally(()=>{if(activeGameTrailers.get(root)?.runId===runId)activeGameTrailers.delete(root);});
    activeGameTrailers.set(root,{runId,promise});void promise.catch(()=>{});
    return publicTrailer(job);
  }));}
  protected async recordTrailer(id:string,root:string,runId:string,onClip:(clips:string[])=>Promise<void>):Promise<string[]> {
    const {ffmpeg}=verificationBinaries();
    const available=await execute(ffmpeg,['-version'],pluginRoot,10000);if(available.code)throw new GameError('Local ffmpeg is unavailable; configure FFMPEG_PATH. No download was attempted.');
    const result=await this.runBrowser(id,1,[[]],0,undefined,true,{}, {root,runId,ffmpeg,onClip});
    return result.recordedClips;
  }
  protected async composeTrailer(game:GameCard,root:string,clips:string[],onProject:(id:string)=>Promise<void>):Promise<string> {
    const {Phase1Service}=await import('./phase1.ts');
    const store=new WorkspaceStore(path.dirname(this.root));
    const phase1=new Phase1Service(store,this.runtimeRoot,{origin:()=> 'http://127.0.0.1',nativeUrl:()=>undefined,openProject:async()=>{},mutation:async task=>task(),cancel:async()=>{throw new Error('Trailer composition does not cancel exports');}});
    const title=((game.i18n?.['zh-CN']?.title||game.title)+' · Trailer').replace(/[\x00-\x1f]/g,' ').slice(0,100);
    const created=await phase1.call('openmotion_create_project',{projectType:'natural_language',title,namingLanguage:'zh-CN',requirements:`Editable gameplay trailer for local game ${game.id}. Title, gameplay highlights and Play now end card. Silent capture; no music generated.`,requestId:randomUUID()});
    const projectId=created.projectId as string;await onProject(projectId);
    const project=store.forProject(projectId),media:string[]=[];
    for(let i=0;i<clips.length;i++){
      const target=`assets/gameplay-${i+1}.mp4`,source=await safeFile(root,clips[i]);
      await project.importAsset((await project.get()).revision,source,target);media.push(target);
    }
    const located=await this.locate(game.id),stored=await jsonFile<GameCard>(path.join(located.dir,'game.json'));
    let coverSource:string,coverPath:string;
    if(stored.cover&&!/^(?:[a-z]+:|\/)/i.test(stored.cover)){
      coverSource=await safeFile(located.dir,stored.cover);coverPath='assets/cover'+path.extname(stored.cover).toLowerCase();
    }else{
      coverSource=await safeFile(root,'trailer/poster.png',true);coverPath='assets/cover.png';
      const {ffmpeg}=verificationBinaries();const poster=await execute(ffmpeg,['-y','-ss','0.5','-i',await safeFile(root,clips[0]),'-frames:v','1',coverSource],root,30000);
      if(poster.code)throw new GameError('Could not create a local gameplay poster: '+poster.stderr.slice(-500));
    }
    await project.importAsset((await project.get()).revision,coverSource,coverPath);
    const {files}=gameTrailerComposition(game,media,coverPath);
    await project.writeFiles((await project.get()).revision,files);
    return projectId;
  }
  protected async renderTrailer(projectId:string):Promise<string> {
    // Preflight existing files so exportExpectation's ensureRuntime(false) cannot install dependencies.
    const installed=JSON.parse(await readFile(path.join(this.runtimeRoot,'node_modules/hyperframes/package.json'),'utf8'));
    if(installed.version!==HYPERFRAMES_VERSION)throw new GameError('The pinned HyperFrames runtime is not installed; trailer rendering did not install anything.');
    await access(path.join(this.runtimeRoot,'node_modules/gsap/dist/gsap.min.js'));
    await access(path.join(this.runtimeRoot,'node_modules/hyperframes/dist/studio/index.html'));
    const {nativeRuntimeStatus}=await import('./scripts/npm-runtime.mjs');const native=await nativeRuntimeStatus(pluginRoot);
    if(native.managed&&!native.capabilities.export)throw new GameError('Existing native export components are unavailable. Prepare them separately; this trailer did not download or install anything.');
    const store=new WorkspaceStore(path.dirname(this.root)),project=store.forProject(projectId);
    const job=await project.requestExport((await project.get()).revision,{phase1:true,audio:'silent',requestId:randomUUID()});
    const {renderNext}=await import('./server.ts');
    const end=Date.now()+30*60*1000;
    while(Date.now()<end){
      const current=await project.job(job.id);
      if(current?.state==='completed')return project.exportPath(current);
      if(current&&['failed','cancelled'].includes(current.state))throw new GameError('Trailer export failed: '+(current.error??current.state));
      // MCP-only hosts may have no periodic server worker; drain earlier queued exports too.
      if(current?.state==='pending')await renderNext(store,this.runtimeRoot);
      await new Promise(resolve=>setTimeout(resolve,500));
    }
    throw new GameError('Trailer rendering timed out; inspect the native export job before retrying.');
  }

  private browserBusy = false;
  async captureCover(id: string, options: {room?: string;actions?:GameBrowserAction[];delayMs?:number;waitForReadyMs?:number} = {}) {
    const actions=validateGameScript(options.actions??[]),delay=options.delayMs??1000;
    const waitForReadyMs = options.waitForReadyMs ?? 10000;
    if(!Number.isInteger(delay)||delay<0||delay>10000)throw new GameError('delayMs must be 0–10000');
    if(!Number.isInteger(waitForReadyMs)||waitForReadyMs<0||waitForReadyMs>30000)throw new GameError('waitForReadyMs must be 0–30000');
    const result=await this.runBrowser(id,1,[actions],delay,options.room,true,{waitForReadyMs});
    const game=await this.updateMeta(id,{cover:'assets/cover.png'});
    return {game,cover:'assets/cover.png',screenshotPath:result.clients[0].screenshotPath,width:1280,height:720,diagnostics:result.clients[0]};
  }
  async playtest(id: string, options: {clients?:number;scripts?:GameBrowserAction[][];durationMs?:number;room?:string;movementThreshold?:number;expectedPhase?:string;waitForReadyMs?:number} = {}) {
    const clients=options.clients??1,duration=options.durationMs??3000;
    if(!Number.isInteger(clients)||clients<1||clients>4)throw new GameError('clients must be 1–4');
    if(!Number.isInteger(duration)||duration<0||duration>60000)throw new GameError('durationMs must be 0–60000');
    if(options.scripts!==undefined&&(!Array.isArray(options.scripts)||options.scripts.length>clients))throw new GameError('Supply at most one script per client');
    if(options.movementThreshold!==undefined&&(!Number.isFinite(options.movementThreshold)||options.movementThreshold<0||options.movementThreshold>100))throw new GameError('movementThreshold must be 0–100');
    if(options.expectedPhase!==undefined&&(typeof options.expectedPhase!=='string'||!options.expectedPhase||options.expectedPhase.length>64))throw new GameError('Invalid expectedPhase');
    if(options.waitForReadyMs!==undefined&&(!Number.isInteger(options.waitForReadyMs)||options.waitForReadyMs<0||options.waitForReadyMs>30000))throw new GameError('waitForReadyMs must be 0–30000');
    const defaultMove:GameBrowserAction[]=[{type:'key',key:'d',event:'down'},{type:'wait',ms:350},{type:'key',key:'d',event:'up'}];
    const scripts=Array.from({length:clients},(_,i)=>validateGameScript(options.scripts?.[i]??(options.scripts?[]:defaultMove)));
    return this.runBrowser(id,clients,scripts,duration,options.room,false,options);
  }
  private async recordGameClips(page:Page,recording:{root:string;runId:string;ffmpeg:string;onClip:(clips:string[])=>Promise<void>},drive:(page:Page,actions:GameBrowserAction[])=>Promise<void>,clips:string[],report:{consoleErrors:string[];failedRequests:{url:string;error:string}[]}) {
    if(report.consoleErrors.length||report.failedRequests.length)throw new GameError('Game failed to load for recording: '+[...report.consoleErrors,...report.failedRequests.map(r=>r.error+' '+r.url)].join('; ').slice(0,1200));
    await page.waitForSelector('canvas, #game',{timeout:5000});
    await new Promise(resolve=>setTimeout(resolve,2000));
    const keys=['w','d','s','a'];
    for(let index=0;index<3;index++){
      if(index)await new Promise(resolve=>setTimeout(resolve,2000+index*1000));
      const ended=await page.evaluate(()=>Boolean((window as any).__omGame?.getState()?.result));
      if(ended){const restart=await page.$('#restart:not([disabled])');if(restart)await restart.click();}
      const isKit=await page.evaluate(()=>Boolean((window as any).__omGame?.getState()?.rules));
      const actions:GameBrowserAction[]=[
        {type:'key',key:keys[index],event:'down'},{type:'wait',ms:900},{type:'key',key:keys[index],event:'up'},
        {type:'key',key:keys[(index+1)%4],event:'down'},{type:'wait',ms:800},{type:'key',key:'Space'},{type:'key',key:keys[(index+1)%4],event:'up'},
        {type:'key',key:'e'},{type:'key',key:keys[(index+2)%4],event:'down'},{type:'wait',ms:1000},{type:'key',key:keys[(index+2)%4],event:'up'},
        {type:'key',key:keys[(index+3)%4],event:'down'},{type:'wait',ms:900},{type:'key',key:keys[(index+3)%4],event:'up'},{type:'wait',ms:1400},
      ];
      if(!isKit){actions.unshift({type:'mouse',event:'down',x:640,y:360});actions.push({type:'mouse',event:'up',x:640,y:360});}
      const relative=`trailer/clips/${recording.runId}-${index+1}.mp4`,target=await safeFile(recording.root,relative,true);
      await mkdir(path.dirname(target),{recursive:true});
      const temp=await mkdtemp(path.join(tmpdir(),'openmotion-trailer-frames-'));
      try{
        const raw=path.join(temp,'recording.webm');let recorded=false;
        try{
          const recorder=await page.screencast({path:raw as `${string}.webm`,format:'webm',fps:30,ffmpegPath:recording.ffmpeg});
          recorder.on('error',()=>{});
          try{await drive(page,actions);}finally{await recorder.stop();}
          const converted=await execute(recording.ffmpeg,['-y','-i',raw,'-an','-vf','fps=30,scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,tpad=stop_mode=clone:stop_duration=5','-t','5','-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart',target],recording.root,60000);
          if(converted.code)throw new Error(converted.stderr.slice(-800));recorded=true;
        }catch{
          // Browser builds without screencast support still use real page frames, never placeholder video.
          let frames=0;const start=performance.now();
          await Promise.all([drive(page,actions),(async()=>{while(performance.now()-start<5000){await page.screenshot({path:path.join(temp,`frame-${String(frames++).padStart(4,'0')}.jpg`) as `${string}.jpg`,type:'jpeg',quality:85});const wait=frames*100-(performance.now()-start);if(wait>0)await new Promise(resolve=>setTimeout(resolve,wait));}})()]);
          if(frames<2)throw new GameError('Too few real gameplay frames were captured');
          const converted=await execute(recording.ffmpeg,['-y','-framerate',String(frames/5),'-i',path.join(temp,'frame-%04d.jpg'),'-an','-vf','fps=30,scale=1280:720','-t','5','-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart',target],recording.root,60000);
          if(converted.code)throw new GameError('Gameplay frame encoding failed: '+converted.stderr.slice(-800));recorded=true;
        }
        if(recorded){if(!(await lstat(target)).size)throw new GameError('Gameplay encoder produced an empty clip');clips.push(relative);await recording.onClip([...clips]);}
      }finally{await rm(temp,{recursive:true,force:true});}
    }
  }

  private async runBrowser(id: string, clients: number, scripts: GameBrowserAction[][], durationMs: number, requestedRoom: string | undefined, cover: boolean, expectations: {movementThreshold?:number;expectedPhase?:string;waitForReadyMs?:number} = {}, recording?:{root:string;runId:string;ffmpeg:string;onClip:(clips:string[])=>Promise<void>}) {
    const located=await this.locate(id,!recording),dir=recording?.root??located.dir,game=await this.get(id);
    if(clients>game.maxPlayers)throw new GameError('Requested clients exceed game capacity');
    const room=requestedRoom===undefined?'test-'+randomUUID():idPart(requestedRoom);
    if(this.browserBusy)throw new GameError('A headless game run is already active; wait for it to finish',409);
    this.browserBusy=true;
    let browser:Browser|undefined,profile:string|undefined;
    const store = new WorkspaceStore(path.dirname(this.root));
    const server=createServer((req,res)=>{
      const url=new URL(req.url??'/','http://localhost');
      if (/^\/motion-api\/assets\/[^/]+\/versions\/[^/]+\/(?:media|file)$/.test(url.pathname)) {
        if (req.method === 'OPTIONS') {
          res.writeHead(204, { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS', 'Access-Control-Allow-Headers': 'Range' });
          res.end();
          return;
        }
        if (req.method === 'GET' || req.method === 'HEAD') {
          url.pathname = url.pathname.replace(/^\/motion-api\//, '/api/');
          void assetHttp(req, res, url, store).catch((error: any) => {
            if (res.headersSent) res.destroy();
            else {
              const msg = String(error?.message ?? '');
              const notFound = error?.code === 'ENOENT' || /ASSET_VERSION_UNAVAILABLE|not found/i.test(msg);
              res.writeHead(notFound ? 404 : 500, { 'Access-Control-Allow-Origin': '*' });
              res.end();
            }
          });
          return;
        }
      }
      if(req.method==='GET'&&url.pathname==='/favicon.ico'){res.writeHead(204);res.end();return;}
      if(req.method!=='GET'||!url.pathname.startsWith(`/api/games/${id}/play/`)){res.writeHead(404);res.end();return;}
      void gameHttp(req,res,url,path.dirname(this.root),async()=>({})).catch(()=>{res.writeHead(500);res.end();});
    });
    const closeRooms=attachGameRooms(server,path.dirname(this.root));
    try {
      const puppeteer=await browserAutomation(this.runtimeRoot);
      const executablePath=await browserExecutable();
      profile=await mkdtemp(path.join(tmpdir(),'openmotion-game-chrome-'));
      await new Promise<void>((resolve,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',resolve);});
      const address=server.address();if(!address||typeof address==='string')throw new GameError('Local game server failed to listen');
      const origin=`http://127.0.0.1:${address.port}`;
      browser=await puppeteer.launch({executablePath,headless:true,pipe:true,userDataDir:profile,timeout:20000,defaultViewport:{width:1280,height:720,deviceScaleFactor:1},args:['--mute-audio','--use-gl=swiftshader','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-background-timer-throttling','--disable-renderer-backgrounding','--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run','--no-default-browser-check']});
      const pages:Page[]=[];
      const reports=await Promise.all(Array.from({length:clients},async(_,i)=>{
        const context=await browser!.createBrowserContext(),page=await context.newPage();pages[i]=page;
        const consoleErrors:string[]=[],failedRequests:{url:string;error:string}[]=[];
        page.on('console',m=>{if(m.type()==='error'&&consoleErrors.length<100)consoleErrors.push(m.text().slice(0,2000));});
        page.on('pageerror',e=>{if(consoleErrors.length<100)consoleErrors.push(String(e).slice(0,2000));});
        page.on('requestfailed',r=>{if(failedRequests.length<100)failedRequests.push({url:r.url().slice(0,2000),error:r.failure()?.errorText??'Request failed'});});
        page.on('response',r=>{if(r.status()>=400&&failedRequests.length<100)failedRequests.push({url:r.url().slice(0,2000),error:`HTTP ${r.status()}`});});
        page.on('dialog',d=>{void d.dismiss();});
        page.on('popup',p=>{void p?.close();});
        await page.setRequestInterception(true);
        page.on('request',r=>{const url=r.url();void (url.startsWith(origin+'/')||url.startsWith('data:')||url.startsWith('blob:')?r.continue():r.abort('blockedbyclient')).catch(()=>{});});
        await page.evaluateOnNewDocument(`(()=>{
          // Keep concurrent headless clients rendering; this run does not test background suspension.
          Object.defineProperty(document,'hidden',{get:()=>false,configurable:true});
          Object.defineProperty(document,'visibilityState',{get:()=>'visible',configurable:true});
          const probe=window.__openmotionGameProbe={frames:0,roomJoined:false,playerCount:0,joinedAtMs:null};
          const joined=()=>{probe.roomJoined=true;if(probe.joinedAtMs===null)probe.joinedAtMs=performance.now();};
          const Original=window.WebSocket;
          window.WebSocket=class extends Original{constructor(...args){super(...args);this.addEventListener('message',event=>{try{const m=JSON.parse(event.data);if(m.type==='joined'){joined();probe.playerCount=m.players?.length??0;}if(m.type==='state'&&m.view?.players)probe.playerCount=Object.values(m.view.players).filter(p=>p.connected!==false).length;}catch{}});}};
          function frame(){probe.frames++;try{const state=window.__omGame?.getState();if(state?.selfId&&state.players?.[state.selfId]&&state.players[state.selfId].connected!==false)joined();}catch{}requestAnimationFrame(frame);}requestAnimationFrame(frame);
        })();`);
        // Live games may keep polling while playable. Wait for document resources,
        // then use the canvas, room and startup checks instead of network silence.
        await page.goto(origin+game.playUrl+(game.multiplayer?'?room='+encodeURIComponent(room):''),{waitUntil:'load',timeout:20000});
        await page.waitForSelector('canvas, #game',{visible:true,timeout:5000});
        if(game.multiplayer)await page.waitForFunction('window.__openmotionGameProbe.roomJoined',{timeout:5000}).catch(()=>{});
        const autoJoin=await page.evaluate(()=>{const p=(window as any).__openmotionGameProbe;return {joined:p.roomJoined,elapsedMs:p.joinedAtMs as number|null};});
        return {consoleErrors,failedRequests,autoJoin};
      }));
      // Wait for every multiplayer join before starting; each solo page starts independently.
      const waitForReadyMs = expectations.waitForReadyMs ?? 10000;
      await Promise.all((game.multiplayer ? [pages[0]] : pages).map(async page => {
        await waitForGameReady(page, waitForReadyMs);
        await startGameBrowserPage(page, !!recording);
      }));
      const readHook=async(page:Page)=>{
        try{return await page.evaluate(async()=>{const hook=(window as any).__omGame;if(!hook||typeof hook.getState!=='function')return null;const value={state:await hook.getState(),stats:typeof hook.getStats==='function'?await hook.getStats():null};const json=JSON.stringify(value);if(json.length>65536)throw Error('Test hook state exceeds 64 KiB');return JSON.parse(json);});}
        catch(error){return {state:null,error:String(error)};}
      };
      const runSelfTests = async (page: Page) => {
        try {
          return await Promise.race([
            page.evaluate(async () => {
              const hook = (window as any).__omGame;
              const fn = typeof hook?.runSelfTests === 'function' ? hook.runSelfTests : typeof hook?.runSelfTest === 'function' ? hook.runSelfTest : null;
              if (!fn) return null;
              const raw = await fn();
              const json = JSON.stringify(raw);
              if (!json || json.length > 65536) throw Error('Self-test result exceeds 64 KiB');
              return JSON.parse(json);
            }),
            new Promise((_, reject) => setTimeout(() => reject(new Error('window.__omGame.runSelfTests() timed out after 10000ms')), 10000)),
          ]);
        } catch (error) {
          return { __error: String(error) };
        }
      };
      await Promise.all(pages.map(page=>page.waitForFunction('!window.__omGame || window.__omGame.getState()!==null',{timeout:5000}).catch(()=>{})));
      const before=await Promise.all(pages.map(readHook));
      const recordedClips:string[]=[];
      const clientScreenshots: Array<Array<{ label: string; path: string }>> = Array.from({ length: clients }, () => []);
      const started=performance.now();
      const initial=await Promise.all(pages.map(page=>page.evaluate('window.__openmotionGameProbe.frames') as Promise<number>));
      const execute=async(page:Page,actions:GameBrowserAction[],clientIndex = 0)=>{
        for(const a of actions){
          if(a.type==='wait')await new Promise(resolve=>setTimeout(resolve,a.ms));
          else if(a.type==='action'){
            const dispatched = await page.evaluate(async (payload) => {
              const hook = (window as any).__omGame;
              if (typeof hook?.sendAction !== 'function') return { ok: false, reason: 'window.__omGame.sendAction is not defined' };
              await hook.sendAction(payload);
              return { ok: true };
            }, a.action);
            if (!dispatched.ok) throw new Error(dispatched.reason);
            await page.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => resolve())));
          }
          else if(a.type==='screenshot'){
            const label = a.label ?? `shot-${clientScreenshots[clientIndex].length + 1}`;
            const relative = `assets/playtests/${room}-${clientIndex+1}-${label}-${randomUUID().slice(0,8)}.png`;
            const shotPath = await safeFile(dir, relative, true);
            await mkdir(path.dirname(shotPath), { recursive: true });
            await page.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => requestAnimationFrame(() => resolve()))));
            await page.screenshot({ path: shotPath as `${string}.png`, type: 'png' });
            clientScreenshots[clientIndex].push({ label, path: shotPath });
          }
          else if(a.type==='burst'){
            const baseLabel = a.label ?? 'burst';
            const intervalMs = a.intervalMs ?? 100;
            for (let frameIdx = 0; frameIdx < a.count; frameIdx++) {
              if (frameIdx > 0) await new Promise(resolve => setTimeout(resolve, intervalMs));
              const label = `${baseLabel}_${frameIdx + 1}`;
              const relative = `assets/playtests/${room}-${clientIndex+1}-${label}-${randomUUID().slice(0,8)}.png`;
              const shotPath = await safeFile(dir, relative, true);
              await mkdir(path.dirname(shotPath), { recursive: true });
              await page.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => resolve())));
              await page.screenshot({ path: shotPath as `${string}.png`, type: 'png' });
              clientScreenshots[clientIndex].push({ label, path: shotPath });
            }
          }
          else if(a.type==='key'){const key=(a.key==='Space'?'Space':a.key) as KeyInput;if(a.event==='down')await page.keyboard.down(key);else if(a.event==='up')await page.keyboard.up(key);else await page.keyboard.press(key);}
          else if(a.selector)await page.click(a.selector,{button:a.button??'left'});
          else {await page.mouse.move(a.x!,a.y!);if(a.event==='click')await page.mouse.click(a.x!,a.y!,{button:a.button??'left'});else if(a.event==='down')await page.mouse.down({button:a.button??'left'});else if(a.event==='up')await page.mouse.up({button:a.button??'left'});}
        }
      };
      await Promise.all([new Promise(resolve=>setTimeout(resolve,durationMs)),...pages.map((page,i)=>execute(page,scripts[i],i).catch(error=>{reports[i].consoleErrors.push('Input script: '+String(error));}))]);
      if(recording)await this.recordGameClips(pages[0],recording,execute,recordedClips,reports[0]);
      const elapsed=performance.now()-started;
      const output=await Promise.all(pages.map(async(page,i)=>{
        const metrics=await page.evaluate('({...window.__openmotionGameProbe})') as {frames:number;roomJoined:boolean;playerCount:number};
        const authoritative=await readHook(page);
        const selfTests = cover ? null : await runSelfTests(page);
        const target=await page.$('canvas')??await page.$('#game');
        if(!target)throw new GameError('Game has no canvas or #game root to capture');
        const originalStyle=await target.evaluate(element=>element.getAttribute('style'));
        await target.evaluate(element=>{const style=(element as HTMLElement).style;Object.assign(style,{position:'fixed',left:'0',top:'0',width:'1280px',height:'720px',maxWidth:'none',maxHeight:'none',margin:'0',border:'0',padding:'0',transform:'none',boxSizing:'border-box'});});
        await page.evaluate(()=>new Promise<void>(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>resolve()))));
        const relative=recording?'trailer/recording-preview.png':cover?'assets/cover.png':`assets/playtests/${room}-${i+1}-${randomUUID()}.png`;
        const screenshotPath=await safeFile(dir,relative,true);await mkdir(path.dirname(screenshotPath),{recursive:true});
        await target.screenshot({path:screenshotPath as `${string}.png`,type:'png'});
        await target.evaluate((element,style)=>{if(style===null)element.removeAttribute('style');else element.setAttribute('style',style);},originalStyle);
        let assertions:ReturnType<typeof gamePlaytestAssertions>=[];
        if(!cover){
          await page.setViewport({width:390,height:844,deviceScaleFactor:1});
          await page.evaluate(()=>new Promise<void>(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>resolve()))));
          const mobile=await page.evaluate(()=>({width:innerWidth,height:innerHeight,scrollWidth:Math.max(document.documentElement.scrollWidth,document.body.scrollWidth),overflowElements:[...document.querySelectorAll('body > *')].filter(e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&(r.left< -1||r.right>innerWidth+1);}).map(e=>e.id||e.tagName).slice(0,10)}));
          assertions=gamePlaytestAssertions({before:before[i],after:authoritative,clients,script:scripts[i],mobile,movementThreshold:expectations.movementThreshold,expectedPhase:expectations.expectedPhase,autoJoin:game.multiplayer?reports[i].autoJoin:undefined,selfTests});
          await page.setViewport({width:1280,height:720,deviceScaleFactor:1});
        }
        let contactSheet: { path: string; legend: string; grid: { cols: number; rows: number } } | null = null;
        if (!cover && clientScreenshots[i].length >= 2) {
          const sheetRel = `assets/playtests/${room}-${i+1}-sheet-${randomUUID().slice(0,8)}.png`;
          const sheetPath = await safeFile(dir, sheetRel, true);
          contactSheet = await buildPlaytestContactSheet(clientScreenshots[i], sheetPath);
        }
        return {...reports[i],screenshotPath,...(clientScreenshots[i].length?{screenshots:clientScreenshots[i]}:{}),...(contactSheet?{contactSheetPath:contactSheet.path,contactSheetLegend:contactSheet.legend}:{}),...(selfTests!==null?{selfTests}:{}),authoritative,assertions,metrics:{fpsEstimate:+((metrics.frames-initial[i])*1000/Math.max(1,elapsed)).toFixed(1),roomJoined:metrics.roomJoined,playerCount:metrics.playerCount,frames:metrics.frames-initial[i]}};
      }));
      return {recordedClips,room,durationMs:Math.round(elapsed),clients:output,scope:'Each run has its own temporary room server; the room name does not attach to live user rooms. Isolated server-owned headless Chrome; canvas/root screenshots only; offline requests; no user profile. Client visibility is forced for concurrent rendering; background suspension is not tested. FPS is requestAnimationFrame pacing, not GPU performance acceptance.'};
    } finally {
      try {if(browser)await browser.close();} finally {closeRooms();server.closeAllConnections();if(server.listening)await new Promise<void>(resolve=>server.close(()=>resolve()));if(profile)await rm(profile,{recursive:true,force:true});this.browserBusy=false;}
    }
  }

  async staticFile(id: string, relative: string) {
    if (relative.toLowerCase() === 'game.json' || relative.toLowerCase()==='trailer/job.json' || isPublishRecord(relative)) throw new GameError('Private game metadata', 404);
    const card = await this.locateCard(id);
    const cachedTemplateDir = card.source === 'template' ? this.hosted.cachedDirectory(card.dir) : undefined;
    const root = relative.startsWith('trailer/') ? await this.trailerStorage(id)
      : card.source === 'template' && relative === 'index.html' ? await this.hosted.directory(id, card.dir)
      : cachedTemplateDir ?? card.dir;
    let file: string;
    try { file = await safeFile(root, relative); }
    catch (error) {
      if (
        (error as NodeJS.ErrnoException).code !== 'ENOENT'
        || card.source !== 'template'
        || relative === 'index.html'
        || (root !== card.dir && root !== cachedTemplateDir)
      ) throw error;
      if (root !== card.dir) {
        const cacheExists = await access(root).then(() => true, () => false);
        if (cacheExists) throw error;
        this.hosted.invalidateCachedDirectory(card.dir);
      }
      file = await safeFile(await this.hosted.directory(id, card.dir), relative);
    }
    let data = await readFile(file);
    if (card.source === 'template' && root === card.dir && lfsPointer(data)) {
      const directory = await this.hosted.directory(id, card.dir);
      data = await readFile(await safeFile(directory, relative));
      if (lfsPointer(data)) throw new GameError(`Missing Git LFS data for ${id}/${relative}`, 503);
    }
    return { data, mime: mime[path.extname(file).toLowerCase()] ?? 'application/octet-stream' };
  }
}

/** Each call runs inside a context with no host objects, loaders, clock or random source. */
export class GameRuntime {
  private context: vm.Context;
  private optionalExports = new Set<string>();
  meta: { minPlayers: number; maxPlayers: number; tickRate: number };
  constructor(source: string, seed: string) {
    const ast = parseModule(source, { ecmaVersion: 'latest', sourceType: 'module' });
    const inspect = (node: any): void => {
      if (!node || typeof node !== 'object') return;
      const member = node.type === 'MemberExpression' && node.object?.type === 'Identifier';
      const property = node.computed ? node.property?.value : node.property?.name;
      if (node.type === 'ImportDeclaration' || node.type === 'ImportExpression' || node.type === 'Identifier' && node.name === 'require' || member && (node.object.name === 'Math' && property === 'random' || node.object.name === 'Date' && property === 'now')) throw new GameError('logic.js cannot import/require, Math.random or Date.now');
      for (const value of Object.values(node)) if (Array.isArray(value)) value.forEach(inspect); else if (value && typeof value === 'object') inspect(value);
    };
    inspect(ast);
    const replacements: { start: number; end: number; text: string }[] = [];
    const exports: string[] = [];
    for (const node of ast.body as any[]) {
      if (node.type === 'ExportNamedDeclaration') {
        if (node.source) throw new GameError('Re-exports are unavailable');
        if (node.declaration) {
          const decl = node.declaration;
          exports.push(...(decl.id ? [decl.id.name] : decl.declarations.map((d: any) => d.id.name)));
          replacements.push({ start: node.start, end: decl.start, text: '' });
        } else { exports.push(...node.specifiers.map((s: any) => s.exported.name)); replacements.push({ start: node.start, end: node.end, text: node.specifiers.map((s: any) => `const ${s.exported.name} = ${s.local.name};`).filter((_: string, i: number) => node.specifiers[i].exported.name !== node.specifiers[i].local.name).join('\n') }); }
      } else if (node.type === 'ExportDefaultDeclaration' || node.type === 'ImportDeclaration') throw new GameError('Use the six named logic exports');
    }
    this.optionalExports = new Set(exports);
    for (const name of ['meta','setup','validateAction','applyAction','isGameOver','viewFor']) if (!exports.includes(name)) throw new GameError(`Missing logic export: ${name}`);
    for (const replacement of replacements.sort((a,b) => b.start-a.start)) source = source.slice(0,replacement.start) + replacement.text + source.slice(replacement.end);
    this.context = vm.createContext(Object.create(null), { codeGeneration: { strings: false, wasm: false }, microtaskMode: 'afterEvaluate' });
    const hash = createHash('sha256').update(seed).digest().readUInt32LE();
    this.run(`"use strict"; Math.random=undefined; globalThis.Date=undefined; let seed=${hash}; const ctx={tick:0,now:0,random(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;}}; let state; ${source}\nif([setup,validateAction,applyAction,isGameOver,viewFor].some(f=>typeof f!=='function'))throw Error('Invalid logic functions');`);
    this.meta = JSON.parse(this.run('JSON.stringify(meta)'));
    if (!Number.isInteger(this.meta.minPlayers) || !Number.isInteger(this.meta.maxPlayers) || this.meta.minPlayers < 1 || this.meta.maxPlayers < this.meta.minPlayers || this.meta.maxPlayers > 32) throw new GameError('Invalid player limits');
    this.meta.tickRate ??= 20;
    if (!Number.isFinite(this.meta.tickRate) || this.meta.tickRate < 1 || this.meta.tickRate > 60) throw new GameError('tickRate must be 1–60 Hz');
  }
  private run(code: string): any { return vm.runInContext(code, this.context, { timeout: 50 }); }
  setup(players: string[]) { this.run(`state=setup(ctx,${JSON.stringify(players)}); if(state===undefined || state?.then)throw Error('setup must return synchronous state'); JSON.stringify(state);`); }
  tick(tick: number) { this.run(`ctx.tick=${tick};ctx.now=${tick * 1000 / this.meta.tickRate}; if(meta.serverTick === true) state=applyAction(state,null,{type:'tick'},ctx);`); }
  membership(player: string, connected: boolean, expired = false) { this.run(`if(meta.serverTick === true) state=applyAction(state,null,${JSON.stringify({type:'membership',player,connected,expired})},ctx);`); }
  apply(player: string, action: unknown, dryRun = false) {
    this.run(`{const action=JSON.parse(${JSON.stringify(JSON.stringify(action))}); const valid=validateAction(state,${JSON.stringify(player)},action,ctx); if(typeof valid!=='boolean')throw Error('validateAction must return boolean'); if(valid||${dryRun}) {state=applyAction(state,${JSON.stringify(player)},action,ctx); if(state===undefined || state?.then)throw Error('applyAction must return synchronous state'); JSON.stringify(state);}}`);
  }
  view(player: string) {
    const result = this.run(`(() => { const view=viewFor(state,${JSON.stringify(player)},ctx); if(view?.then)throw Error('viewFor must return synchronous JSON'); return JSON.stringify(view); })()`);
    if (typeof result !== 'string' || result.length > 1024 * 1024) throw new GameError('viewFor must return JSON under 1 MiB');
    return JSON.parse(result);
  }
  referenceRoute(index: number) {
    if(!this.optionalExports.has('referenceRoute'))throw new GameError('logic.js does not export referenceRoute(playerIndex)');
    const result=this.run(`(()=>{if(typeof referenceRoute!=='function')throw Error('logic.js does not export referenceRoute(playerIndex)');return JSON.stringify(referenceRoute(${index}));})()`);
    if(typeof result!=='string'||result.length>1024*1024)throw new GameError('referenceRoute must return a JSON route under 1 MiB');
    return JSON.parse(result);
  }
  summary(player: string) {
    const json=this.run(`JSON.stringify(${this.optionalExports.has('summarize')} && typeof summarize==='function'?summarize(JSON.parse(JSON.stringify(state))):viewFor(state,${JSON.stringify(player)},ctx))`);
    if(typeof json!=='string'||json.length>32768)throw new GameError('Simulation summary must be JSON under 32 KiB; export summarize(state) for large views');
    return JSON.parse(json);
  }
  over(): { over: boolean; winners?: string[] } {
    const result = JSON.parse(this.run('JSON.stringify(isGameOver(state,ctx))'));
    if (typeof result?.over !== 'boolean' || (result.winners !== undefined && (!Array.isArray(result.winners) || result.winners.some((id: unknown) => typeof id !== 'string')))) throw new GameError('Invalid isGameOver result');
    return result;
  }
}
const services = new Map<string, GameProjects>();
export function gameProjectsFor(workspace: string, runtimeRoot?: string) {
  const key = path.resolve(workspace); if (!services.has(key)) services.set(key,new GameProjects(key));
  const service = services.get(key)!; if (runtimeRoot) service.runtimeRoot = runtimeRoot; return service;
}
/** publish/ holds this computer's publish records (WeChat AppID, preview code): never served, exported or remixed. */
function isPublishRecord(relative: string) { return /^publish(?:\/|$)/i.test(path.posix.normalize(relative.replace(/\\/g, '/')).replace(/^(?:\.\/|\/)+/, '')); }

export async function dispatchGameTool(name: string, args: any, workspace: string, runtimeRoot?: string) {
  const service = gameProjectsFor(workspace, runtimeRoot);
  switch (name.replace(/^(?:openmotion|motion)_game_/,'')) {
    case 'create': return createSinglePlayerGame(service, args?.brief ?? args);
    case 'get': return service.detail(args.id);
    case 'read_file': return service.read(args.id,args.path);
    case 'write_files':
      assertSinglePlayerAuthoring((await service.get(args.id)).multiplayer);
      return service.write(args.id,args.files);
    case 'capture_cover': return service.captureCover(args.id,args);
    case 'trailer': if(args.action==='start')return service.startTrailer(args.id);if(args.action==='status')return service.trailer(args.id);throw new GameError('Trailer action must be start or status');
    case 'simulate': return service.simulate(args.id,args);
    case 'playtest': return service.playtest(args.id,args);
    case 'update_meta': { const { id, ...patch } = args; return service.updateMeta(id,patch); }
    case 'validate': return service.validate(args.id);
    case 'set_status':
      if (args.status === 'building') assertSinglePlayerAuthoring((await service.get(args.id)).multiplayer);
      return service.status(args.id,args.status);
    case 'publish': {
      try {
        return await service.publish(args.id);
      } catch (error) {
        const raw = error instanceof Error ? error.message : String(error);
        if (raw.startsWith('OPENDESIGN_SIGN_IN_REQUIRED') || (error as { code?: unknown })?.code === 'OPENDESIGN_SIGN_IN_REQUIRED') {
          throw Object.assign(error instanceof Error ? error : new Error(raw), {
            code: 'OPENDESIGN_SIGN_IN_REQUIRED',
            applied: false,
            settingsHandoff: buildMediaSettingsHandoff('agent_game_publish_signed_out'),
          });
        }
        throw error;
      }
    }
    case 'wechat': return (await import('./gateway/wechat-minigame.ts')).wechatMinigameFor(workspace).action(args);
    default: throw new GameError('Unknown game tool');
  }
}
async function optionalJsonInput(req: IncomingMessage, maxBytes: number): Promise<unknown> {
  if (!req.headers['content-type']?.startsWith('application/json') || req.headers['content-length'] === '0') {
    return undefined;
  }
  let size = 0;
  const chunks: Buffer[] = [];
  for await (const chunk of req) {
    const buf = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
    size += buf.length;
    if (size > maxBytes) throw new GameError('Payload too large', 413);
    chunks.push(buf);
  }
  const text = Buffer.concat(chunks).toString('utf8').trim();
  return text ? JSON.parse(text) : undefined;
}

type GameHttpOptions = {
  isolatedPreview?: boolean;
  localPreviewUrl?: (id: string, search?: string) => string;
};

// Bundled single-player games use game-relative assets. Workspace games can also depend
// on the Studio asset library, which the isolated static listener does not expose.
function canUseIsolatedPreview(game: GameCard) {
  return game.source === 'template' && !game.multiplayer && !game.external;
}

export async function gameHttp(req: IncomingMessage, res: ServerResponse, url: URL, workspace: string, input: (req: IncomingMessage, maxBytes?: number) => Promise<any>, runtimeRoot?: string, options: GameHttpOptions = {}) {
  const prefix = /^\/(?:api|motion-api)\/games(?=\/|$)/.exec(url.pathname)?.[0];
  if (!prefix) return false;
  const json = (status: number, data: unknown) => { res.writeHead(status, { 'Content-Type':'application/json', 'Cache-Control':'no-store' }); res.end(JSON.stringify(data)); return true; };
  try {
    const service = gameProjectsFor(workspace, runtimeRoot), parts = url.pathname.slice(prefix.length).split('/').filter(Boolean).map(decodeURIComponent);
    if (!parts.length) { if (req.method === 'GET') return json(200, await service.catalog()); if (req.method === 'POST') return json(201,await createSinglePlayerGame(service, await input(req, LIMIT))); }
    const [id, action, ...rest] = parts;
    if (action === 'preview-url' && !rest.length && req.method === 'GET') {
      const localPreviewUrl = options.localPreviewUrl;
      return json(200, { url: localPreviewUrl && canUseIsolatedPreview(await service.get(id)) ? localPreviewUrl(id) : null });
    }
    if (parts.length === 1) { if (req.method === 'GET') return json(200,await service.get(id)); if (req.method === 'DELETE') return json(200,await service.delete(id)); }
    if (action === 'trailer' && !rest.length && req.method==='GET')return json(200,await service.trailer(id));
    if (action === 'handoff' && !rest.length && req.method==='GET')return json(200,await service.handoff(id));
    if (action === 'files' && !rest.length && req.method==='GET')return json(200,{ files: (await service.detail(id)).files });
    if (action === 'export' && !rest.length && req.method === 'GET') {
      const archive = await service.exportZip(id);
      res.writeHead(200, {
        'Content-Type': 'application/zip',
        'Content-Length': archive.data.length,
        'Content-Disposition': attachmentDisposition(archive.filename, `${id}.zip`),
        'Cache-Control': 'no-store',
        'X-Content-Type-Options': 'nosniff',
      });
      res.end(archive.data);
      return true;
    }
    if (action === 'play' && req.method === 'GET') {
      const entry=!rest.length||(rest.length===1&&rest[0]==='index.html');
      if (options.isolatedPreview && !canUseIsolatedPreview(await service.get(id))) return json(404, { error: 'Game preview unavailable' });
      if (entry && req.headers?.['sec-fetch-dest'] === 'document' && options.localPreviewUrl && canUseIsolatedPreview(await service.get(id))) {
        res.writeHead(302, { Location: options.localPreviewUrl(id, url.search), 'Cache-Control': 'no-store' }).end();
        return true;
      }
      if(entry&&!url.searchParams.has('room')&&(await service.get(id)).multiplayer){
        const target=new URL(url);target.searchParams.set('room',randomUUID().replaceAll('-','').slice(0,8));
        res.writeHead(302,{'Location':target.pathname+target.search,'Cache-Control':'no-store','Access-Control-Allow-Origin':'*'});res.end();return true;
      }
      const studioEntry = entry && url.searchParams.get('gameStartup') === '1';
      let file;
      try {
        file = await service.staticFile(id,rest.length?rest.join('/'):'index.html');
      } catch (error) {
        if (!studioEntry) throw error;
        console.error(`[opengame] Failed to load game ${id}:`, error instanceof Error ? error.message : error);
        res.writeHead(503, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store', 'Content-Security-Policy': "default-src 'none'; script-src 'unsafe-inline'; sandbox allow-scripts" });
        res.end(`<script>parent.postMessage({type:'opengame:startup',state:'failed'}, '*')</script>`);
        return true;
      }
      if (studioEntry && file.data.includes('id="GameCanvas"') && file.data.includes('cocos-js')) {
        const startup = `<script>(() => {
          const report = state => parent.postMessage({type:'opengame:startup',state}, '*');
          const startupError = () => report('failed');
          addEventListener('error', startupError);
          addEventListener('unhandledrejection', startupError);
          report('loading');
          const waitForGameScene = setInterval(() => {
            if (!window.cc?.director?.getScene?.()) return;
            clearInterval(waitForGameScene);
            removeEventListener('error', startupError);
            removeEventListener('unhandledrejection', startupError);
            requestAnimationFrame(() => requestAnimationFrame(() => report('ready')));
          }, 100);
          addEventListener('pagehide', () => clearInterval(waitForGameScene), {once:true});
        })()</script>`;
        file.data = Buffer.from(file.data.toString('utf8').replace(/<head\b[^>]*>/i, head => head + startup));
      }
      const bridgeToken = url.searchParams.get('omBridge');
      const hasBridge = isValidPreviewBridgeToken(bridgeToken);
      const wantsViewportGuard = hasBridge
        || url.searchParams.get('omViewportGuard') === '1'
        || req.headers?.['sec-fetch-dest'] === 'iframe';
      let payload: Buffer = file.data;
      if (entry && file.mime.startsWith('text/html')) {
        if (hasBridge) payload = injectPreviewBridgeHtml(payload, bridgeToken);
        if (wantsViewportGuard) payload = injectViewportGuardHtml(payload);
      }
      const origin = new URL(url); if (req.headers?.host) origin.host = req.headers.host;
      const encodedId = encodeURIComponent(id);
      const assetOrigins = options.isolatedPreview ? '' : `${origin.origin}/api/assets/ ${origin.origin}/motion-api/assets/`;
      const playOrigins = `${origin.origin}/api/games/${encodedId}/play/ ${origin.origin}/motion-api/games/${encodedId}/play/`;
      const sockets = options.isolatedPreview ? '' : ['/api/games', '/motion-api/games'].map(prefix => `${origin.protocol === 'https:' ? 'wss:' : 'ws:'}//${origin.host}${prefix}/${id}/rooms/`).join(' ');
      const executable = /^(?:text\/html|image\/svg\+xml)/.test(file.mime);
      const sandbox = options.isolatedPreview ? ' allow-same-origin' : '';
      const isolation = options.isolatedPreview ? "; object-src 'none'; base-uri 'none'" : '';
      const csp = `sandbox allow-scripts allow-forms allow-pointer-lock allow-popups allow-modals${sandbox}; default-src 'self' data: blob: ${playOrigins} ${assetOrigins}; connect-src 'self' blob: data: ${playOrigins} ${assetOrigins} ${sockets} ${gameCdnOrigins}; script-src 'self' 'unsafe-inline' 'unsafe-eval' ${playOrigins} ${gameCdnOrigins}; style-src 'self' 'unsafe-inline' ${playOrigins}; form-action 'none'; worker-src 'none'${isolation}`;
      const originHeaders = options.isolatedPreview ? { 'Origin-Agent-Cluster': '?1', 'Referrer-Policy': 'no-referrer' } : { 'Access-Control-Allow-Origin': '*' };
      res.writeHead(200, { ...originHeaders, 'Content-Type':file.mime, 'Content-Length':payload.length, 'Cache-Control':'no-store', 'X-Content-Type-Options':'nosniff', ...(executable ? { 'Content-Security-Policy': csp } : {}) }); res.end(payload); return true;
    }
    if (parts.length === 2 && req.method === 'POST') {
      if (action === 'capture-cover') return json(200,await service.captureCover(id,await input(req, LIMIT)));
      if (action === 'trailer') return json(202,await service.startTrailer(id));
      if (action === 'simulate') return json(200,await service.simulate(id,await input(req, LIMIT)));
      if (action === 'playtest') return json(200,await service.playtest(id,await input(req, LIMIT)));
      if (action === 'update-meta') return json(200,await service.updateMeta(id,await input(req, LIMIT)));
      if (action === 'remix') {
        return json(201, await service.remix(id, await optionalJsonInput(req, LIMIT) as GameRemixOptions | undefined));
      }
      if (action === 'play') return json(200,await service.interact(id,'play'));
      if (action === 'reaction') return json(200,await service.interact(id,'reaction',(await input(req,1024))?.value));
      if (action === 'favorite') return json(200,await service.interact(id,'favorite',(await input(req,1024))?.favorite));
    }
    return json(404,{ error:'Unknown game endpoint' });
  } catch (e) { return json(e instanceof GameError ? e.status : (e as NodeJS.ErrnoException).code === 'ENOENT' ? 404 : 400,{ error:(e as Error).message }); }
}

/** Minimal RFC6455 server: masked client text, fragmentation, ping and bounded payloads. */
function frame(opcode: number, payload: Buffer) {
  const header = Buffer.alloc(payload.length < 126 ? 2 : payload.length <= 65535 ? 4 : 10); header[0] = 0x80 | opcode;
  if (header.length === 2) header[1] = payload.length;
  else if (header.length === 4) { header[1] = 126; header.writeUInt16BE(payload.length,2); }
  else { header[1] = 127; header.writeBigUInt64BE(BigInt(payload.length),2); }
  return Buffer.concat([header,payload]);
}
function peer(socket: Duplex, onMessage: (data: any) => void, onClose: () => void) {
  let buffer: Buffer = Buffer.alloc(0), fragments: Buffer[] = [], fragmentBytes = 0, fragmented = false;
  let fragmentTimer: ReturnType<typeof setTimeout> | undefined;
  const clearFragmentTimer = () => { if (fragmentTimer) clearTimeout(fragmentTimer); fragmentTimer = undefined; };
  socket.once('close', clearFragmentTimer);
  const send = (value: RoomServerMessage & { reconnectToken?: string }) => { if (!socket.destroyed) { if (socket.writableLength > 2 * LIMIT) socket.destroy(); else socket.write(frame(1,Buffer.from(JSON.stringify(value)))); } };
  socket.on('error', () => socket.destroy()); socket.once('close', onClose);
  socket.on('data', chunk => {
    if (socket.destroyed) return;
    if (buffer.length + chunk.length + fragmentBytes > 128 * 1024) { socket.destroy(); return; }
    buffer = Buffer.concat([buffer,chunk]);
    try {
      while (!socket.destroyed && buffer.length >= 2) {
        const fin = !!(buffer[0]&128), opcode = buffer[0]&15, masked = !!(buffer[1]&128); let size = buffer[1]&127, offset = 2;
        if ((buffer[0]&112) || !masked) throw new Error('Invalid frame');
        if (size === 126) { if (buffer.length < 4) break; size = buffer.readUInt16BE(2); offset = 4; }
        // else-if: a 16-bit extended length of exactly 127 must not be re-read as the 64-bit marker.
        else if (size === 127) { if (buffer.length < 10) break; const n = buffer.readBigUInt64BE(2); if (n > 65536n) throw new Error('Frame too large'); size = Number(n); offset = 10; }
        if (size > 65536 || (opcode >= 8 && (!fin || size > 125))) throw new Error('Frame too large');
        if (buffer.length < offset+4+size) break;
        const mask = buffer.subarray(offset,offset+4), payload = Buffer.from(buffer.subarray(offset+4,offset+4+size)); buffer = buffer.subarray(offset+4+size);
        for (let i=0;i<size;i++) payload[i] ^= mask[i%4];
        if (opcode === 8) { socket.end(frame(8,payload)); return; }
        if (opcode === 9) { socket.write(frame(10,payload)); continue; }
        if (opcode === 10) continue;
        if (opcode !== 1 && opcode !== 0 || opcode === 0 && !fragmented || opcode === 1 && fragmented) throw new Error('Invalid text fragmentation');
        if (opcode === 1 && !fin) { fragmentTimer = setTimeout(() => socket.destroy(), 10000); fragmentTimer.unref(); }
        fragmented = !fin; fragments.push(payload); fragmentBytes += size;
        if (fragments.length > 64) throw new Error('Too many message fragments');
        if (fragmentBytes > 65536) throw new Error('Message too large');
        if (fin) { clearFragmentTimer(); const text = new TextDecoder('utf-8',{ fatal:true }).decode(Buffer.concat(fragments)); fragments=[]; fragmentBytes=0; onMessage(JSON.parse(text)); }
      }
    } catch { socket.destroy(); }
  });
  return { send, socket };
}
type Peer = ReturnType<typeof peer> & { id: string; name: string; joined: boolean; token: string };
type Room = { runtime: GameRuntime; clients: Set<Peer>; started: boolean; ended: boolean; tick: number; queue: { player: string; action: unknown }[]; timer?: ReturnType<typeof setInterval>; maxPlayers: number; identities: Map<string, { id: string; name: string; expires: number; peer?: Peer }>; cleanup?: ReturnType<typeof setTimeout> };
export function attachGameRooms(server: Server, workspace: string) {
  const rooms = new Map<string,Room>(), sockets = new Set<Duplex>();
  let closed = false;
  const upgrade = async (req: IncomingMessage, socket: Duplex, head: Buffer) => {
    socket.on('error', () => socket.destroy());
    const url = new URL(req.url ?? '/', 'http://localhost'), match = /^\/(?:api|motion-api)\/games\/([^/]+)\/rooms\/([^/]+)$/.exec(url.pathname);
    if (!match) { socket.destroy(); return; }
    try {
      if (!req.headers.host || !['localhost','127.0.0.1','[::1]'].includes(new URL('http://' + req.headers.host).hostname)) throw new GameError('Only local room access is allowed');
      if (req.headers.origin && req.headers.origin !== 'null') {
        const origin = new URL(req.headers.origin);
        if (!['http:','https:'].includes(origin.protocol) || !['localhost','127.0.0.1','[::1]'].includes(origin.hostname) || origin.username || origin.password || origin.pathname !== '/' || origin.search || origin.hash) throw new GameError('Cross-origin room access rejected');
      }
      const id = idPart(decodeURIComponent(match[1])), roomId = idPart(decodeURIComponent(match[2])), key = id + '/' + roomId;
      const wsKey = req.headers['sec-websocket-key'];
      if (req.method !== 'GET' || req.headers.upgrade?.toLowerCase() !== 'websocket' || req.headers['sec-websocket-version'] !== '13' || typeof wsKey !== 'string' || Buffer.from(wsKey,'base64').length !== 16) throw new GameError('Invalid WebSocket handshake');
      const service = gameProjectsFor(workspace), game = await service.get(id);
      if (!game.multiplayer) throw new GameError('Not a multiplayer game');
      // Await source before the final map lookup, so simultaneous upgrades share one room.
      const source = (await service.read(id,'logic.js')).content;
      if (socket.destroyed) return;
      let room = rooms.get(key);
      if (!room) { if (rooms.size >= 100) throw new GameError('Too many active rooms'); const runtime = new GameRuntime(source,key); room = { runtime, clients:new Set(), started:false, ended:false, tick:0, queue:[], maxPlayers:runtime.meta.maxPlayers, identities:new Map() }; rooms.set(key,room); }
      if (room.clients.size >= room.maxPlayers + 8) throw new GameError('Too many pending room connections');
      socket.write('HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: ' + createHash('sha1').update(wsKey+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest('base64')+'\r\n\r\n');
      const active = room;
      const prune = () => { for (const [token, identity] of active.identities) if (!identity.peer && identity.expires <= Date.now()) { active.identities.delete(token); if(active.started) active.runtime.membership(identity.id,false,true); } };
      // An unjoined connection must not keep an abandoned room alive indefinitely.
      const joinTimeout = setTimeout(() => { if (!client.joined) socket.destroy(); }, 10000); joinTimeout.unref();
      const roster = () => [...active.clients].filter(p=>p.joined).map(p=>({ id:p.id,name:p.name }));
      const broadcastRoster = () => { for (const p of active.clients) if (p.joined) p.send({ type:'joined',playerId:p.id,room:roomId,players:roster(),maxPlayers:active.maxPlayers,reconnectToken:p.token }); };
      const client: Peer = Object.assign(peer(socket, message => {
        try {
          if (!message || typeof message !== 'object') throw new GameError('Invalid room message');
          if (message.type === 'join') {
            if (client.joined) throw new GameError('Already joined');
            prune();
            const token = typeof message.reconnectToken === 'string' ? message.reconnectToken : '';
            let identity = active.identities.get(token);
            if (token && !identity) throw new GameError('Reconnect token expired; join again without it');
            if (identity?.peer) throw new GameError('Player is already connected');
            if (!identity) {
              if (active.identities.size >= active.maxPlayers) throw new GameError('Room full (disconnected seats reserved for 30 seconds)');
              client.token=randomUUID();
              identity={id:client.id,name:typeof message.name==='string'?message.name.slice(0,60):'Player',expires:Infinity};
              active.identities.set(client.token,identity);
            } else { client.token=token; client.id=identity.id; }
            client.name=identity.name; client.joined=true; identity.peer=client; identity.expires=Infinity;
            clearTimeout(joinTimeout); clearTimeout(active.cleanup); active.cleanup=undefined;
            if(active.started) active.runtime.membership(client.id,true);
            broadcastRoster();
            if(active.started) { client.send({type:'state',view:active.runtime.view(client.id),tick:active.tick}); if(active.ended) client.send({type:'over',...active.runtime.over()}); }
          }
          else if (!client.joined) throw new GameError('Join the room first');
          else if (message.type === 'start') {
            if (active.started || active.ended) throw new GameError('Room already started');
            const players=roster().map(p=>p.id); if (players.length<active.runtime.meta.minPlayers) throw new GameError('Not enough players');
            active.runtime.setup(players); active.started=true;
            active.timer=setInterval(()=>{
              try {
                if(!active.ended) active.runtime.tick(++active.tick);
                for(const input of active.queue.splice(0)) active.runtime.apply(input.player,input.action);
                for(const p of active.clients) if(p.joined) p.send({ type:'state',view:active.runtime.view(p.id),tick:active.tick });
                const over=active.runtime.over(); if(over.over && !active.ended) for(const p of active.clients) if(p.joined) p.send({type:'over',winners:over.winners}); active.ended=over.over;
              } catch(e) { clearInterval(active.timer); active.ended=true; for(const p of active.clients) p.send({type:'error',message:(e as Error).message}); }
            },1000/active.runtime.meta.tickRate); active.timer.unref();
          } else if(message.type==='input') {
            if(!active.started || (active.ended && message.action?.type !== 'restart')) throw new GameError('Room is not running');
            if(active.queue.length>=256 || active.queue.filter(i=>i.player===client.id).length>=16) throw new GameError('Too many queued inputs');
            active.queue.push({player:client.id,action:message.action??null});
          } else throw new GameError('Unknown room message');
        } catch(e) { client.send({type:'error',message:(e as Error).message}); }
      },()=>{
        clearTimeout(joinTimeout); sockets.delete(socket); active.clients.delete(client);
        if(closed) return;
        const identity=active.identities.get(client.token);
        if(identity?.peer===client) {
          identity.peer=undefined; identity.expires=Date.now()+30000;
          active.queue=active.queue.filter(input=>input.player!==client.id);
          if(active.started) try { active.runtime.membership(client.id,false); } catch { /* simulation error is reported by the room loop */ }
        }
        if(![...active.clients].some(p=>p.joined) && !active.cleanup) {
          active.cleanup=setTimeout(()=>{clearInterval(active.timer); for(const p of active.clients) p.socket.destroy(); rooms.delete(key);},30000); active.cleanup.unref();
        }
        broadcastRoster();
      }), {id:randomUUID(),name:'Player',joined:false,token:''});
      active.clients.add(client); sockets.add(socket);
      if(head.length) socket.emit('data',head);
    } catch { if(!socket.destroyed) socket.end('HTTP/1.1 400 Bad Request\r\nConnection: close\r\n\r\n'); }
  };
  server.on('upgrade',(req,socket,head)=>{ void upgrade(req,socket,head).catch(() => socket.destroy()); });
  const close = () => { closed=true; for(const room of rooms.values()) { clearInterval(room.timer); clearTimeout(room.cleanup); } for(const socket of sockets) socket.destroy(); rooms.clear(); };
  server.on('close',close); return close;
}
