#!/usr/bin/env node
// post-media: scaffold, render and verify post videos/stills with HyperFrames.
//   post-media new <slug> [--from post.json]
//   post-media render <slug> [--formats feed,story,wide]
//   post-media stills <slug> [--formats still-feed,still-wide]
import { execFileSync, spawnSync } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync, readFileSync, readdirSync, realpathSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const self = realpathSync(fileURLToPath(import.meta.url));
const skillDir = resolve(dirname(self), "..");
const tpl = join(skillDir, "template");
const HOME = process.env.POST_MEDIA_HOME || join(homedir(), "Desktop/Projects/media");
const HF = join(tpl, "node_modules/.bin/hyperframes");

const die = (m) => { console.error(`post-media: ${m}`); process.exit(1); };
const args = process.argv.slice(2);
const cmd = args.shift();
const flag = (name) => { const i = args.indexOf(name); if (i < 0) return null; const v = args[i + 1]; args.splice(i, 2); return v; };
const from = flag("--from");
const formatsArg = flag("--formats");
const slug = args[0];
const log = (...a) => console.log(...a);

function ensureDeps() {
  if (existsSync(HF)) return;
  log("installing template deps (one time)...");
  const r = spawnSync("npm", ["install", "--no-audit", "--no-fund"], { cwd: tpl, stdio: "inherit" });
  if (r.status !== 0) die("npm install failed in " + tpl);
}
function projectDir() {
  if (!slug || !/^[a-z0-9][a-z0-9-]*$/.test(slug)) die("slug must match [a-z0-9-]+");
  const d = join(HOME, slug);
  if (!existsSync(join(d, "post.json"))) die(`no project at ${d}; run: post-media new ${slug}`);
  return d;
}
const t0 = () => process.hrtime.bigint();
const secs = (a) => Number(process.hrtime.bigint() - a) / 1e9;
const run = (bin, a, cwd) => spawnSync(bin, a, { cwd, encoding: "utf8", maxBuffer: 64 * 1024 * 1024 });
const probeJson = (f) => JSON.parse(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,duration", "-of", "json", f]).toString());

async function loadCompose() { return import(pathToFileURL(join(tpl, "src/compose.mjs")).href); }
function readPost(d) { try { return JSON.parse(readFileSync(join(d, "post.json"), "utf8")); } catch (e) { die(`bad post.json: ${e.message}`); } }

function check(buildDir) {
  const r = run(HF, ["check", "--json"], buildDir);
  let j = null; try { j = JSON.parse(r.stdout); } catch {}
  const bad = r.status !== 0 || (j && (j.ok === false || j.errors?.length > 0 || j.summary?.errors > 0));
  return { ok: !bad, raw: j, out: (r.stdout + r.stderr).trim() };
}

function normalizeFormats(C, list, kind) {
  return list.map((f) => { const k = C.FORMATS[f] ? f : C.formatByDims(f); if (!k || C.FORMATS[k].kind !== kind) die(`bad ${kind} format "${f}"`); return k; });
}

async function doNew() {
  if (!slug || !/^[a-z0-9][a-z0-9-]*$/.test(slug)) die("usage: post-media new <slug> [--from post.json]");
  const d = join(HOME, slug);
  if (existsSync(join(d, "post.json"))) die(`${d}/post.json exists; not overwriting`);
  mkdirSync(join(d, "assets"), { recursive: true });
  copyFileSync(from ? resolve(from) : join(tpl, "post.example.json"), join(d, "post.json"));
  log(`created ${d}`);
  log(`next: put proof assets in ${d}/assets, edit post.json, then: post-media render ${slug}`);
}

async function doRender() {
  ensureDeps();
  const d = projectDir(), C = await loadCompose(), post = readPost(d);
  const wanted = normalizeFormats(C, (formatsArg || post.formats?.join(",") || "feed").split(","), "video");
  const report = [];
  mkdirSync(join(d, "out/frames"), { recursive: true });
  for (const fmt of wanted) {
    const row = { format: fmt };
    let t = t0();
    const c = C.compose(d, post, fmt);
    row.compose_s = +secs(t).toFixed(2);
    c.warns.forEach((w) => log(`warn: ${w}`));
    t = t0();
    const ck = check(c.dir);
    row.check_s = +secs(t).toFixed(2);
    if (!ck.ok) { log(ck.out); die(`hyperframes check failed for ${fmt} (build in ${c.dir})`); }
    const mp4 = join(d, "out", `${slug}-${c.W}x${c.H}.mp4`);
    t = t0();
    const r = run(HF, ["render", "--quality", "looks", "-o", mp4], c.dir);
    row.render_s = +secs(t).toFixed(2);
    if (r.status !== 0 || !existsSync(mp4)) { log(r.stdout + r.stderr); die(`render failed for ${fmt}`); }
    const p = probeJson(mp4);
    const v = p.streams.find((s) => s.codec_type === "video");
    row.file = mp4;
    row.ffprobe = { duration_s: +Number(p.format.duration).toFixed(2), expected_s: c.total, size: `${v.width}x${v.height}`, codec: v.codec_name, fps: v.r_frame_rate, audio: p.streams.some((s) => s.codec_type === "audio"), bytes: Number(p.format.size) };
    if (`${v.width}x${v.height}` !== `${c.W}x${c.H}`) die(`size mismatch ${v.width}x${v.height} for ${fmt}`);
    if (Math.abs(row.ffprobe.duration_s - c.total) > 0.5) die(`duration ${row.ffprobe.duration_s}s vs expected ${c.total}s for ${fmt}`);
    if (!row.ffprobe.bytes) die(`empty file ${mp4}`);
    row.frames = [];
    t = t0();
    for (const [i, frac] of [0.15, 0.5, 0.9].entries()) {
      const out = join(d, "out/frames", `${fmt}-${i + 1}.png`);
      execFileSync("ffmpeg", ["-y", "-v", "error", "-ss", String((c.total * frac).toFixed(2)), "-i", mp4, "-frames:v", "1", out]);
      row.frames.push(out);
    }
    row.frames_s = +secs(t).toFixed(2);
    report.push(row);
  }
  writeFileSync(join(d, "out/report.json"), JSON.stringify(report, null, 2));
  log(JSON.stringify(report, null, 2));
}

async function doStills() {
  ensureDeps();
  const d = projectDir(), C = await loadCompose(), post = readPost(d);
  const wanted = normalizeFormats(C, (formatsArg || "still-feed,still-wide").split(","), "still");
  mkdirSync(join(d, "stills"), { recursive: true });
  const report = [];
  for (const fmt of wanted) {
    const row = { format: fmt };
    let t = t0();
    const c = C.compose(d, post, fmt);
    c.warns.forEach((w) => log(`warn: ${w}`));
    const ck = check(c.dir);
    if (!ck.ok) { log(ck.out); die(`hyperframes check failed for ${fmt}`); }
    const r = run(HF, ["snapshot", "--at", "0.9"], c.dir);
    const m = (r.stdout + r.stderr).match(/^\s*(\/\S+\/frame-[^\s]*\.png)\s*$/m);
    if (r.status !== 0 || !m || !existsSync(m[1])) { log(r.stdout + r.stderr); die(`snapshot failed for ${fmt}`); }
    const out = join(d, "stills", `${slug}-${c.W}x${c.H}.png`);
    copyFileSync(m[1], out);
    const pr = probeJson(out).streams[0];
    if (pr.width !== c.W || pr.height !== c.H) die(`still is ${pr.width}x${pr.height}, expected ${c.W}x${c.H}`);
    row.file = out; row.size = `${pr.width}x${pr.height}`; row.total_s = +secs(t).toFixed(2);
    report.push(row);
  }
  log(JSON.stringify(report, null, 2));
}

const cmds = { new: doNew, render: doRender, stills: doStills };
if (!cmds[cmd]) {
  log(`post-media <new|render|stills>
  new <slug> [--from post.json]      scaffold ${HOME}/<slug>
  render <slug> [--formats feed,story,wide]   check, render, ffprobe, 3 frames per format
  stills <slug> [--formats still-feed,still-wide]   PNG at 1080x1350 and 1600x900`);
  process.exit(cmd ? 1 : 0);
}
await cmds[cmd]();
