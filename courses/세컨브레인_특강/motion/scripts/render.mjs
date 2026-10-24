// 영상 4편 렌더: node scripts/render.mjs [code|mcp|rag|obsidian ...]
// 출력: ../sessions/1주차/자료/video/<id>.mp4 + <id>.png(마지막 프레임 포스터)
import {spawnSync} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const outDir = path.resolve(root, '..', 'sessions', '1주차', '자료', 'video');
const cli = path.join(root, 'node_modules', '@remotion', 'cli', 'remotion-cli.js');

// id → 프레임 수 (30fps) · src/*.tsx의 *_DURATION과 같아야 한다
const COMPS = {code: 1260, mcp: 510, rag: 540, obsidian: 330};

const ids = process.argv.slice(2).length ? process.argv.slice(2) : Object.keys(COMPS);
fs.mkdirSync(outDir, {recursive: true});

let failed = 0;
for (const id of ids) {
  if (!(id in COMPS)) {
    console.error(`알 수 없는 영상: ${id}`);
    failed++;
    continue;
  }
  const mp4 = path.join(outDir, `${id}.mp4`);
  const png = path.join(outDir, `${id}.png`);
  const r1 = spawnSync(
    process.execPath,
    [cli, 'render', 'src/index.ts', id, mp4, '--codec=h264', '--crf=23', '--pixel-format=yuv420p', '--overwrite'],
    {cwd: root, stdio: 'inherit'},
  );
  console.log(`render ${id} exit=${r1.status}`);
  const r2 = spawnSync(
    process.execPath,
    [cli, 'still', 'src/index.ts', id, png, `--frame=${COMPS[id] - 1}`, '--overwrite'],
    {cwd: root, stdio: 'inherit'},
  );
  console.log(`still ${id} exit=${r2.status}`);
  if (r1.status !== 0 || r2.status !== 0) failed++;
}
process.exit(failed ? 1 : 0);
