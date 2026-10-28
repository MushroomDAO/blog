const fs = require('node:fs/promises');
const path = require('node:path');
const crypto = require('node:crypto');
const sharp = require('sharp');

const root = path.resolve(__dirname, '../..');
const generationDirectory = '/Users/jason/.codex/generated_images/01a180f3-5a45-7742-b7c2-b13bbdc4abf1';
const generatedFiles = [
  'exec-c1d7cbf9-a780-49b1-8d9f-b8e031cb091d.png',
  'exec-cd7bb28d-cddd-437f-8162-fdaa3908f8c1.png',
  'exec-11e9a1dd-56b7-4f86-a58d-926a245cb5f9.png',
];
const themes = [
  'Chief of staff routes user tasks to specialist seats with local CLI tools.',
  'MCP default deny; explicit authorization per seat; not a sandbox guarantee.',
  'Skill improvement proposal passes tests and human review before adoption.',
];
const hash = data => crypto.createHash('sha256').update(data).digest('hex');

async function main() {
  const records = [];
  for (const [index, filename] of generatedFiles.entries()) {
    const number = String(index + 1).padStart(2, '0');
    const source = path.join(generationDirectory, filename);
    const original = await fs.readFile(source);
    const originalPath = path.join(__dirname, `illustration-${number}.original.png`);
    await fs.writeFile(originalPath, original, { flag: 'wx' });
    let selected;
    for (const width of [1280, 1152, 1024, 960]) {
      for (const colours of [128, 96, 64, 48]) {
        const data = await sharp(original)
          .flatten({ background: '#ffffff' })
          .resize(width, width * 9 / 16, { fit: 'contain', background: '#ffffff' })
          .png({ palette: true, colours, dither: 0, compressionLevel: 9, effort: 10 })
          .toBuffer();
        if (data.length < 90000) {
          selected = { data, width, height: width * 9 / 16, colours };
          break;
        }
      }
      if (selected) break;
    }
    if (!selected) throw new Error(`Cannot meet byte limit: figure ${number}`);
    const destination = path.join(root, 'src/assets/images', `archonos-local-agent-workbench-fig-${number}.png`);
    await fs.writeFile(destination, selected.data, { flag: 'wx' });
    const saved = await fs.readFile(destination);
    const metadata = await sharp(saved).metadata();
    if (metadata.format !== 'png' || metadata.width * 9 !== metadata.height * 16 || saved.length >= 90000)
      throw new Error(`Final artifact validation failed: ${destination}`);
    records.push({
      figure: index + 1, theme: themes[index], generated_source: source,
      original_copy: path.relative(root, originalPath), original_bytes: original.length,
      original_sha256: hash(original), original_dimensions: await sharp(original).metadata().then(m => [m.width, m.height]),
      final_path: path.relative(root, destination), bytes: saved.length,
      dimensions: [metadata.width, metadata.height], sha256: hash(saved),
      processing: { resize: 'contain on pure white, no cropping', palette_colours: selected.colours, dither: 0, compression_level: 9 },
      visual_review: 'Pass: current red cap / white spots / pale stem XiaoM participates in core action; sparse legible Chinese labels; white background; requested conceptual boundary visible.',
    });
  }
  const provenance = {
    created_at: new Date().toISOString(), generator: 'image_gen.imagegen', generation_calls: 3,
    model: 'Tool default; exact backend model not exposed',
    skill: '/Users/jason/.codex/skills/mycelium-mushroom-illustrations/SKILL.md',
    prompt_file: 'source/20261028-archonos/illustration-prompts.json',
    input: 'Three themes supplied directly by user; no reference image inputs.',
    records,
  };
  await fs.writeFile(path.join(__dirname, 'illustration-provenance.json'), JSON.stringify(provenance, null, 2) + '\n', { flag: 'wx' });
  console.log(JSON.stringify(records.map(({ final_path, bytes, dimensions, sha256 }) => ({ final_path, bytes, dimensions, sha256 })), null, 2));
}
main().catch(error => { console.error(error); process.exitCode = 1; });
