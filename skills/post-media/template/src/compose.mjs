// post.json -> HyperFrames project (one self-contained index.html per format).
// Used by bin/post-media.mjs. Pure generation: no rendering here.
import { execFileSync } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { basename, dirname, extname, isAbsolute, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
export const templateRoot = join(here, "..");

export const FORMATS = {
  feed: { w: 1080, h: 1350, kind: "video", note: "X and LinkedIn feed" },
  story: { w: 1080, h: 1920, kind: "video", note: "shorts and reels" },
  wide: { w: 1920, h: 1080, kind: "video", note: "landscape" },
  "still-feed": { w: 1080, h: 1350, kind: "still", note: "PNG, image-only post" },
  "still-wide": { w: 1600, h: 900, kind: "still", note: "PNG, link card" },
};
export const formatByDims = (s) => Object.entries(FORMATS).find(([k, f]) => f.kind === "video" && `${f.w}x${f.h}` === s)?.[0];

const FONT_FAMILIES = {
  newsreader: "Newsreader",
  fraunces: "Fraunces",
  "source-sans-3": "Source Sans 3",
  "dm-sans": "DM Sans",
  "ibm-plex-mono": "IBM Plex Mono",
};
const BANNED_FONTS = /^(inter|roboto|arial|helvetica|system-ui|sans-serif)/i;

export const DEFAULTS = {
  palette: { paper: "#faf7f2", paperDeep: "#f1ebdd", ink: "#1b1b18", muted: "#5b5a52", rule: "#ddd5c3", accent: "#1f6f5c", accentSoft: "#e3efe9", card: "#fffdf8", glowWarm: "#efe6d2", glowCool: "#e6efe9" },
  font: { display: "newsreader", body: "source-sans-3", mono: "ibm-plex-mono" },
  pace: { hook: 2.6, beat: 3.6, end: 3.2, xfade: 0.4 },
};

// ---------- helpers ----------
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const hex = (h) => { const n = parseInt(h.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; };
const lum = (h) => { const [r, g, b] = hex(h).map((v) => v / 255); return 0.2126 * r + 0.7152 * g + 0.0722 * b; };
function hue(h) {
  const [r, g, b] = hex(h).map((v) => v / 255);
  const mx = Math.max(r, g, b), mn = Math.min(r, g, b), d = mx - mn;
  if (!d) return 0;
  const k = mx === r ? ((g - b) / d) % 6 : mx === g ? (b - r) / d + 2 : (r - g) / d + 4;
  return (k * 60 + 360) % 360;
}
function probe(file, entries) {
  const out = execFileSync("ffprobe", ["-v", "error", "-show_entries", entries, "-of", "json", file]).toString();
  return JSON.parse(out);
}
const audioLen = (f) => Number(probe(f, "format=duration").format.duration);
const imgDims = (f) => { const s = probe(f, "stream=width,height").streams[0]; return { w: s.width, h: s.height }; };

export function resolveAsset(projectDir, p) {
  const q = p.startsWith("~") ? join(homedir(), p.slice(1)) : p;
  const abs = isAbsolute(q) ? q : resolve(projectDir, q);
  if (!existsSync(abs)) throw new Error(`asset not found: ${p} (looked at ${abs})`);
  return abs;
}

// ---------- validation (Max style rules) ----------
export function validate(post) {
  const errs = [], warns = [];
  const pal = { ...DEFAULTS.palette, ...(post.palette || {}) };
  if (lum(pal.paper) < 0.75) errs.push(`palette.paper ${pal.paper} is dark: light mode only`);
  const h = hue(pal.accent);
  if (h >= 255 && h <= 310 && lum(pal.paper) > 0.85) errs.push(`palette.accent ${pal.accent} is purple on a light page: pick another accent`);
  const font = { ...DEFAULTS.font, ...(post.font || {}) };
  for (const [role, f] of Object.entries(font)) {
    if (BANNED_FONTS.test(f)) errs.push(`font.${role} "${f}" is banned (Inter, Roboto, Arial, system)`);
    else if (!FONT_FAMILIES[f]) errs.push(`font.${role} "${f}" not bundled; choose one of ${Object.keys(FONT_FAMILIES).join(", ")}`);
  }
  const texts = [["hook", post.hook], ["hookSub", post.hookSub], ["end.name", post.end?.name], ["end.tag", post.end?.tag], ["end.url", post.end?.url]];
  (post.beats || []).forEach((b, i) => { texts.push([`beats[${i}].text`, b.text], [`beats[${i}].sub`, b.sub]); (b.images || []).forEach((im, j) => texts.push([`beats[${i}].images[${j}].label`, im.label])); (b.terminal?.lines || []).forEach((l, j) => texts.push([`beats[${i}].terminal.lines[${j}]`, l])); });
  const emoji = /\p{Extended_Pictographic}/u, dash = /[–—]/, slop = /\b(game-?chang\w*|unlock\w*|seamless\w*|elevate\w*|revolutioni\w*|delve\w*|leverag\w*|supercharg\w*)\b/i;
  for (const [k, v] of texts) {
    if (!v) continue;
    if (emoji.test(v)) errs.push(`${k}: emoji`);
    if (dash.test(v)) errs.push(`${k}: en/em dash (unslop)`);
    if (slop.test(v)) warns.push(`${k}: AI-tell word "${v.match(slop)[0]}" (unslop)`);
    if (/^status\b|\bbadge\b/i.test(v)) warns.push(`${k}: looks like a status badge`);
  }
  if (!post.hook) errs.push("hook is required");
  const nb = (post.beats || []).length;
  if (nb < 1 || nb > 4) errs.push(`beats: need 1 to 4, got ${nb}`);
  if (!post.end?.name || !post.end?.url) errs.push("end.name and end.url are required");
  return { errs, warns };
}

// ---------- geometry ----------
function geometry(W, H) {
  const portrait = H >= W;
  return portrait
    ? { portrait, W, H, m: Math.round(W * 0.07), txtTop: Math.round(H * 0.075), txtW: Math.round(W * 0.86), fs: Math.round(W * 0.078), subFs: Math.round(W * 0.034), mediaTop: Math.round(H * 0.4), mediaLeft: Math.round(W * 0.07), mediaW: Math.round(W * 0.86), hookFs: Math.round(W * 0.105), termFs: Math.round(W * 0.027) }
    : { portrait, W, H, m: Math.round(H * 0.09), txtTop: 0, txtW: Math.round(W * 0.4), fs: Math.round(H * 0.105), subFs: Math.round(H * 0.036), mediaTop: Math.round(H * 0.11), mediaLeft: Math.round(W * 0.52), mediaW: Math.round(W * 0.42), hookFs: Math.round(H * 0.13), termFs: Math.round(H * 0.026) };
}

const reserve_ = (o) => (o.footer ? " closed" : "");
// ---------- scene markup ----------
// Returns { html, anims(timeline code), audio[] } for a text + media scene.
function mediaScene(ctx, id, scene, start, dur, opts = {}) {
  const { g, assetUrl } = ctx;
  const { W, H } = g;
  const imgs = scene.images || [];
  const n = imgs.length;
  let html = "", js = "";
  const long = (scene.text || "").length > 44;
  const fs = Math.round(g.fs * (long ? 0.86 : 1));
  const hasMedia = n > 0 || scene.terminal;
  const txtStyle = g.portrait
    ? `left:${g.m}px;top:${hasMedia ? g.txtTop : Math.round(H * 0.3)}px;width:${g.txtW}px;`
    : `left:${g.m}px;top:0;bottom:0;width:${g.txtW}px;display:flex;flex-direction:column;justify-content:center;`;
  html += `<div class="txt" style="${txtStyle}"><h2 class="display" style="font-size:${fs}px">${esc(scene.text || "")}</h2>${scene.sub ? `<p class="sub" style="font-size:${g.subFs}px">${esc(scene.sub)}</p>` : ""}</div>`;
  js += `tl.fromTo("#${id} .txt", { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.5, ease: E }, ${start + 0.35});\n`;

  const frame = scene.frame || "phone";
  const labelH = imgs.some((i) => i.label) ? Math.round(W * 0.05) + 18 : 0;
  // portrait: media starts just under the measured-by-estimate text block, not at a fixed height
  let mediaTop = g.mediaTop;
  if (g.portrait) {
    const lines = Math.max(1, Math.ceil(((scene.text || "").length * fs * 0.5) / g.txtW));
    const subLines = scene.sub ? Math.max(1, Math.ceil((scene.sub.length * g.subFs * 0.48) / g.txtW)) : 0;
    mediaTop = Math.round(g.txtTop + lines * fs * 1.1 + (scene.sub ? subLines * g.subFs * 1.35 + H * 0.012 : 0) + H * 0.045);
  }
  const top = mediaTop + labelH;
  const regionW = g.mediaW, gap = Math.round(W * 0.03);
  if (n > 0) {
    const perW = Math.floor((regionW - gap * (n - 1)) / n);
    const phoneMax = g.portrait ? Math.round(W * 0.62) : Math.round(H * 0.5);
    const boxW = frame === "phone" ? Math.min(perW, phoneMax) : perW;
    const totalW = boxW * n + gap * (n - 1);
    const left0 = g.mediaLeft + Math.round((regionW - totalW) / 2);
    imgs.forEach((im, k) => {
      const d = imgDims(im.abs);
      const left = left0 + k * (boxW + gap);
      const pad = frame === "phone" ? 12 : 2;
      const innerW = boxW - pad * 2;
      const sh = Math.round((innerW * d.h) / d.w);
      let boxH, visible;
      const reserve = opts.footer ? Math.round(H * 0.1) : 0;
      if (frame === "phone" && !reserve) { boxH = H - top + 40; visible = H - top - pad; }
      else if (frame === "phone") { boxH = H - top - reserve; visible = boxH - pad * 2; }
      else { boxH = Math.min(sh + pad * 2, H - top - g.m); visible = boxH - pad * 2; }
      const dist = Math.max(0, sh - visible);
      const mid = `${id}m${k}`;
      html += `<div class="media ${frame}${reserve_(opts)}" id="${mid}" style="left:${left}px;top:${top}px;width:${boxW}px;height:${boxH}px;" data-layout-allow-overflow data-layout-allow-overlap>`;
      html += `<div class="shot" style="top:${pad}px;left:${pad}px;right:${pad}px;height:${boxH - pad * 2}px" data-layout-allow-overflow data-layout-allow-overlap><img id="${mid}i" src="${assetUrl(im.abs)}" alt="" style="width:${innerW}px;height:${sh}px"></div></div>`;
      if (im.label) html += `<div class="lbl display" id="${mid}l" style="left:${left}px;width:${boxW}px;top:${mediaTop}px;font-size:${Math.round(W * 0.036)}px">${esc(im.label)}</div>`;
      js += `tl.fromTo("#${mid}", { opacity: 0, y: 70 }, { opacity: 1, y: 0, duration: 0.8, ease: E }, ${start + 0.6 + k * 0.15});\n`;
      if (im.label) js += `tl.fromTo("#${mid}l", { opacity: 0 }, { opacity: 1, duration: 0.4, ease: "none" }, ${start + 0.9 + k * 0.15});\n`;
      if (dist > 8 && !opts.footer) js += `tl.to("#${mid}i", { y: -${dist}, duration: ${Math.max(1, dur - 2.2).toFixed(2)}, ease: "power2.inOut" }, ${start + 1.5});\n`;
    });
  }
  if (scene.terminal) {
    const t = scene.terminal;
    const lines = t.lines.map((l, i) => `<div class="tl${i === t.highlight ? " hl" : ""}" data-layout-allow-overlap>${esc(l)}</div>`).join("");
    html += `<div class="term" id="${id}t" style="left:${g.mediaLeft}px;top:${mediaTop}px;width:${g.mediaW}px;" data-layout-allow-overflow><div class="term-bar"><i></i><i></i><i></i><span class="mono">${esc(t.title || "terminal")}</span></div><div class="term-body mono" style="font-size:${g.termFs}px">${lines}</div></div>`;
    js += `tl.fromTo("#${id}t", { opacity: 0, y: 50 }, { opacity: 1, y: 0, duration: 0.7, ease: E }, ${start + 0.6});\n`;
    js += `tl.fromTo("#${id}t .tl", { opacity: 0 }, { opacity: 1, duration: 0.2, stagger: ${Math.min(0.25, (dur - 2) / Math.max(1, t.lines.length)).toFixed(2)} }, ${start + 1.1});\n`;
    if (t.highlight != null) js += `tl.fromTo("#${id}t .hl", { scale: 0.97 }, { scale: 1, duration: 0.4, ease: E, transformOrigin: "left center" }, ${start + Math.max(1.6, dur - 1.4)});\n`;
  }
  if (opts.footer) {
    html += `<div class="foot mono" style="left:${g.m}px;right:${g.m}px;bottom:${Math.round(g.m * 0.55)}px;font-size:${Math.round(W * (g.portrait ? 0.03 : 0.02))}px">${esc(opts.footer)}</div>`;
  }
  return { html, js };
}

function css(ctx) {
  const { g, pal, fontCss, family } = ctx;
  const { W, H } = g;
  return `
${fontCss}
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: ${W}px; height: ${H}px; overflow: hidden; background: ${pal.paper}; }
#root { --paper:${pal.paper}; --ink:${pal.ink}; --muted:${pal.muted}; --rule:${pal.rule}; --accent:${pal.accent}; --soft:${pal.accentSoft}; --card:${pal.card}; --deep:${pal.paperDeep};
  position: relative; width: ${W}px; height: ${H}px; overflow: hidden; color: var(--ink); font-family: "${family.body}", Georgia, serif;
  background: radial-gradient(${Math.round(W * 1.0)}px ${Math.round(H * 0.45)}px at 88% -10%, ${pal.glowWarm} 0%, rgba(255,255,255,0) 70%), radial-gradient(${Math.round(W * 0.85)}px ${Math.round(H * 0.42)}px at -8% 108%, ${pal.glowCool} 0%, rgba(255,255,255,0) 70%), var(--paper); }
.scene { position: absolute; inset: 0; }
.display { font-family: "${family.display}", Georgia, serif; font-weight: 500; letter-spacing: -0.015em; line-height: 1.08; text-wrap: balance; }
.mono { font-family: "${family.mono}", ui-monospace, monospace; }
.txt { position: absolute; }
.sub { color: var(--muted); line-height: 1.35; margin-top: ${Math.round(H * 0.012)}px; }
.media { position: absolute; overflow: hidden; }
.media.phone { background: #1b1b18; border-radius: ${Math.round(W * 0.06)}px ${Math.round(W * 0.06)}px 0 0; }
.media.phone .shot { border-radius: ${Math.round(W * 0.05)}px ${Math.round(W * 0.05)}px 0 0; }
.media.phone.closed { border-radius: ${Math.round(W * 0.06)}px; }
.media.phone.closed .shot { border-radius: ${Math.round(W * 0.05)}px; }
.media.card { background: var(--card); border: 2px solid var(--rule); border-radius: 22px; box-shadow: 0 24px 60px rgba(60,50,20,0.10); }
.media.card .shot { border-radius: 20px; }
.shot { position: absolute; overflow: hidden; background: var(--paper); }
.shot img { position: absolute; left: 0; top: 0; display: block; }
.lbl { position: absolute; text-align: center; color: var(--accent); }
.term { position: absolute; background: var(--card); border: 2px solid var(--rule); border-radius: 22px; box-shadow: 0 24px 60px rgba(60,50,20,0.10); overflow: hidden; }
.term-bar { height: 52px; border-bottom: 2px solid var(--rule); background: var(--deep); display: flex; align-items: center; gap: 10px; padding: 0 22px; }
.term-bar i { width: 14px; height: 14px; border-radius: 50%; background: #cfc6b0; display: block; }
.term-bar span { margin-left: 14px; color: var(--muted); font-size: 20px; }
.term-body { padding: 28px 34px; line-height: 1.5; overflow-wrap: anywhere; }
.tl { margin-bottom: 8px; color: var(--muted); }
.tl:first-child { color: var(--ink); font-weight: 500; }
.tl.hl { margin-top: 18px; padding: 14px 20px; border-radius: 14px; background: var(--soft); border: 2px solid var(--accent); color: var(--accent); font-weight: 500; }
.foot { position: absolute; color: var(--accent); font-weight: 500; }
.hook { position: absolute; left: 0; right: 0; top: 0; bottom: 0; display: flex; flex-direction: column; justify-content: center; align-items: ${g.portrait ? "flex-start" : "center"}; padding: 0 ${g.m}px; text-align: ${g.portrait ? "left" : "center"}; }
.hook h1 { font-size: ${g.hookFs}px; line-height: 1.06; }
.hook .rule { width: ${Math.round(W * (g.portrait ? 0.3 : 0.18))}px; height: 8px; background: var(--accent); border-radius: 4px; margin-top: ${Math.round(H * 0.035)}px; transform-origin: left center; }
.hook p { margin-top: ${Math.round(H * 0.025)}px; font-size: ${g.subFs}px; color: var(--muted); }
.end { position: absolute; inset: 0; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 0 ${g.m}px; }
.end .name { font-size: ${Math.round(Math.min(W * 0.2, (W * 0.86) / Math.max(4, ctx.endName.length * 0.52)))}px; letter-spacing: -0.03em; }
.end .tag { margin-top: ${Math.round(H * 0.012)}px; font-size: ${Math.round(g.subFs * 1.35)}px; color: var(--muted); }
.end .url { margin-top: ${Math.round(H * 0.05)}px; font-size: ${Math.round(W * (g.portrait ? 0.036 : 0.024))}px; color: var(--accent); font-weight: 500; }
`;
}

function fontSetup(projectBuildDir, font) {
  const out = join(projectBuildDir, "assets/fonts");
  mkdirSync(out, { recursive: true });
  const weights = { display: [500], body: [400, 600], mono: [400, 500] };
  let fontCss = "";
  const family = {};
  for (const role of ["display", "body", "mono"]) {
    const slug = font[role];
    family[role] = FONT_FAMILIES[slug];
    for (const w of weights[role]) {
      const f = `${slug}-latin-${w}-normal.woff2`;
      const src = join(templateRoot, "node_modules/@fontsource", slug, "files", f);
      if (!existsSync(src)) throw new Error(`font file missing: ${f}. Run npm install in ${templateRoot}`);
      copyFileSync(src, join(out, f));
      fontCss += `@font-face { font-family: "${family[role]}"; font-weight: ${w}; src: url("assets/fonts/${f}") format("woff2"); }\n`;
    }
  }
  return { fontCss, family };
}

// ---------- main entry ----------
// kind: "video" (feed, story, wide) or "still". Writes <projectDir>/build/<fmtName>/{index.html,assets,hyperframes.json}.
export function compose(projectDir, post, fmtName) {
  const fmt = FORMATS[fmtName];
  if (!fmt) throw new Error(`unknown format ${fmtName}; use ${Object.keys(FORMATS).join(", ")}`);
  const { W, H } = { W: fmt.w, H: fmt.h };
  const { errs, warns } = validate(post);
  if (errs.length) throw new Error("post.json invalid:\n  " + errs.join("\n  "));
  const pal = { ...DEFAULTS.palette, ...(post.palette || {}) };
  const font = { ...DEFAULTS.font, ...(post.font || {}) };
  const pace = { ...DEFAULTS.pace, ...(post.pace || {}) };
  const g = geometry(W, H);
  const dir = join(projectDir, "build", fmtName);
  rmSync(dir, { recursive: true, force: true });
  mkdirSync(join(dir, "assets"), { recursive: true });
  copyFileSync(join(templateRoot, "node_modules/gsap/dist/gsap.min.js"), join(dir, "assets/gsap.min.js"));
  writeFileSync(join(dir, "hyperframes.json"), JSON.stringify({ $schema: "https://hyperframes.heygen.com/schema/hyperframes.json", paths: { blocks: "compositions", components: "compositions/components", assets: "assets" } }, null, 2));
  const { fontCss, family } = fontSetup(dir, font);

  const copied = new Map();
  const assetUrl = (abs) => {
    if (!copied.has(abs)) {
      const name = `m${copied.size}-${basename(abs).replace(/[^A-Za-z0-9._-]/g, "_")}`;
      copyFileSync(abs, join(dir, "assets", name));
      copied.set(abs, `assets/${name}`);
    }
    return copied.get(abs);
  };
  const ctx = { g, pal, fontCss, family, assetUrl, endName: post.end.name };
  const normImages = (b) => (b.images || (b.image ? [{ src: b.image }] : [])).map((i) => (typeof i === "string" ? { src: i } : i)).map((i) => ({ ...i, abs: resolveAsset(projectDir, i.src) }));

  let body = "", js = "", audioTags = "", total;
  if (fmt.kind === "still") {
    const st = post.still || {};
    const firstBeat = post.beats.find((b) => b.image || b.images) || {};
    const scene = { text: st.headline ?? post.hook, sub: st.sub, frame: st.frame || firstBeat.frame, terminal: st.terminal, images: normImages(st.image || st.images ? st : firstBeat) };
    const r = mediaScene(ctx, "s0", scene, 0, 1.0, { footer: st.footer ?? post.end.url });
    body = `<div id="s0" class="scene clip" data-start="0" data-duration="1">${r.html}</div>`;
    js = r.js.replace(/, (\d+\.?\d*)\);/g, (m, t) => `, ${Math.min(0.3, Number(t))});`).replace(/duration: ([\d.]+)/g, (m, d) => `duration: ${Math.min(0.35, Number(d))}`);
    total = 1;
  } else {
    // timeline
    const xf = pace.xfade;
    const scenes = [];
    scenes.push({ kind: "hook", dur: pace.hook });
    post.beats.forEach((b, i) => {
      const images = normImages(b);
      let dur = b.dur ?? pace.beat;
      let audioAbs = null, aLen = 0;
      if (b.audio) { audioAbs = resolveAsset(projectDir, b.audio); aLen = audioLen(audioAbs); if (!b.dur) dur = Math.max(dur, aLen + 1.0); }
      scenes.push({ kind: "beat", dur, b: { ...b, images }, audioAbs, aLen });
    });
    scenes.push({ kind: "end", dur: pace.end });
    let voAbs = null, voLen = 0;
    if (post.voiceover) { voAbs = resolveAsset(projectDir, post.voiceover); voLen = audioLen(voAbs); }
    const sumT = () => scenes.reduce((a, s) => a + s.dur, 0) - xf * (scenes.length - 1);
    if (voAbs && voLen + 0.8 > sumT()) { const extra = (voLen + 0.8 - sumT()) / scenes.length; scenes.forEach((s) => (s.dur += extra)); }
    let t = 0;
    scenes.forEach((s, i) => {
      s.start = Number(t.toFixed(3)); s.dur = Number(s.dur.toFixed(3)); t = s.start + s.dur - xf; s.id = `s${i}`;
    });
    total = Number((scenes[scenes.length - 1].start + scenes[scenes.length - 1].dur).toFixed(3));
    scenes.forEach((s, i) => {
      const last = i === scenes.length - 1;
      let inner = "", sj = "";
      if (s.kind === "hook") {
        inner = `<div class="hook"><h1 class="display">${esc(post.hook)}</h1><div class="rule" id="rule"></div>${post.hookSub ? `<p>${esc(post.hookSub)}</p>` : ""}</div>`;
        sj = `tl.fromTo("#rule", { scaleX: 0 }, { scaleX: 1, duration: 0.8, ease: "power2.inOut" }, 0.4);\n`;
      } else if (s.kind === "beat") {
        const r = mediaScene(ctx, s.id, s.b, s.start, s.dur);
        inner = r.html; sj = r.js;
        if (s.audioAbs) audioTags += `<audio id="a${i}" src="${assetUrl(s.audioAbs)}" data-start="${(s.start + 0.5).toFixed(2)}" data-duration="${Math.min(s.aLen, s.dur - 0.6).toFixed(2)}" data-track-index="${10 + i}" data-volume="1" data-fade-out="0.3"></audio>\n`;
      } else {
        inner = `<div class="end"><div class="name display" id="en">${esc(post.end.name)}</div>${post.end.tag ? `<div class="tag display" id="et">${esc(post.end.tag)}</div>` : ""}<div class="url mono" id="eu">${esc(post.end.url)}</div></div>`;
        sj = `tl.fromTo("#en", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.7, ease: E }, ${s.start + 0.3});\n` +
          (post.end.tag ? `tl.fromTo("#et", { opacity: 0 }, { opacity: 1, duration: 0.5, ease: "none" }, ${s.start + 1.0});\n` : "") +
          `tl.fromTo("#eu", { opacity: 0 }, { opacity: 1, duration: 0.5, ease: "none" }, ${s.start + 1.5});\n`;
      }
      body += `<div id="${s.id}" class="scene clip" data-start="${s.start}" data-duration="${s.dur}">${inner}</div>\n`;
      if (i > 0) js += `tl.set("#${s.id}", { opacity: 0 }, 0);\ntl.fromTo("#${s.id}", { opacity: 0 }, { opacity: 1, duration: ${xf}, ease: "none" }, ${s.start});\n`;
      if (!last) js += `tl.to("#${s.id}", { opacity: 0, duration: ${xf}, ease: "none" }, ${(s.start + s.dur - xf).toFixed(3)});\n`;
      js += sj;
    });
    if (voAbs) audioTags += `<audio id="vo" src="${assetUrl(voAbs)}" data-start="0.3" data-duration="${voLen.toFixed(2)}" data-track-index="9" data-volume="1" data-fade-out="0.4"></audio>\n`;
  }

  const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=${W}, height=${H}" />
<script src="assets/gsap.min.js"></script>
<style>${css(ctx)}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="${total}" data-width="${W}" data-height="${H}">
${body}
${audioTags}
</div>
<script>
window.__timelines = window.__timelines || {};
const tl = gsap.timeline({ paused: true });
const E = "power3.out";
${js}
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body>
</html>
`;
  writeFileSync(join(dir, "index.html"), html);
  return { dir, total, warns, W, H, kind: fmt.kind };
}
