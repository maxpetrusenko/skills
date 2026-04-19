---
name: browser-oauth-cdp
description: Verify OAuth flows with a real logged-in browser session through Chrome DevTools, without Playwright's fresh browser profile.
---

# Browser OAuth CDP

Use this skill when an OAuth flow must be tested with the user's existing logged-in browser cookies, especially X, LinkedIn, Meta, Google, TikTok, or other provider authorization screens.

## Core Rule

Do not use Playwright's default Chromium profile for logged-in OAuth tests. It starts with isolated browser state and often cannot use macOS Chrome cookies. Prefer the local `browser-use` skill with `--profile "<profile>"` for persistent real-Chrome sessions. If `browser-use` is not available, use a normal Google Chrome process with Chrome DevTools Protocol and a copied Chrome profile, then drive one existing tab with Puppeteer/CDP or the local `browser-tools` helper.

## Anti-Lockout Rules

OAuth providers flag repeated tab creation, repeated login starts, and rapid redirects. Treat provider pages like a human browser session:

- Reuse one browser session and one tab.
- Do not loop over providers in the same browser session.
- Do not open and close OAuth tabs repeatedly.
- Do not retry the same provider more than once without changing the suspected cause.
- Prefer inspecting the generated local `/api/auth/{platform}` redirect URL before navigating to the provider.
- Use provider redirects only after callback URLs and env keys are already verified.
- Pause between attempts and leave the provider page open when debugging.
- Never automate login form submission unless explicitly requested.

## Safe Workflow

1. Confirm the user is logged into the provider in normal Chrome.
2. Copy the Chrome profile into `/tmp`, including `Local State` and the relevant profile folder. Exclude caches and large storage folders.
3. Start normal Google Chrome with `--remote-debugging-port` and `--user-data-dir` pointing at the copied profile.
4. Connect with Puppeteer/CDP or `browser-tools`.
5. Verify cookie presence by cookie names only. Never print cookie values.
6. First call the local start route or inspect the app link to confirm the exact `redirect_uri`, `state.next`, scopes, and provider URL. Do this without visiting the provider when possible.
7. Start one OAuth flow from the app and capture provider page text, final URL, and provider API error bodies. Sanitize `client_id`, `state`, `code`, `code_challenge`, tokens, and secrets before reporting.
8. Only click final authorization buttons when the user explicitly wants the account connected.

## Commands

Install temporary CDP tooling if the repo does not already have it:

```bash
npm install --prefix /tmp/browser-tools-deps commander puppeteer-core tsx --silent
```

Create a lightweight copied Chrome profile:

```bash
rm -rf /tmp/oauth-chrome-profile
mkdir -p /tmp/oauth-chrome-profile
cp "$HOME/Library/Application Support/Google/Chrome/Local State" /tmp/oauth-chrome-profile/
for profile in Default 'Profile 1'; do
  mkdir -p "/tmp/oauth-chrome-profile/$profile"
  rsync -a \
    --exclude='Cache' \
    --exclude='Code Cache' \
    --exclude='GPUCache' \
    --exclude='Service Worker/CacheStorage' \
    --exclude='Service Worker/ScriptCache' \
    --exclude='GrShaderCache' \
    --exclude='GraphiteDawnCache' \
    --exclude='DawnCache' \
    --exclude='IndexedDB' \
    --exclude='Storage' \
    --exclude='File System' \
    "$HOME/Library/Application Support/Google/Chrome/$profile/" \
    "/tmp/oauth-chrome-profile/$profile/"
done
```

Start Chrome with CDP:

```bash
open -na "Google Chrome" --args \
  --remote-debugging-port=9223 \
  --user-data-dir=/tmp/oauth-chrome-profile \
  --no-first-run \
  --disable-popup-blocking
```

Preferred `browser-use` path when available:

```bash
browser-use profile list
browser-use --session social-oauth --profile "Person 1" --headed open http://127.0.0.1:3006/dashboard/workspace-settings/social-accounts
browser-use --session social-oauth state
```

Keep using the same tab with `browser-use state`, `browser-use click`, and `browser-use open`. Do not close and reopen provider tabs during one investigation.

Verify X login without printing cookies:

```bash
NODE_PATH=/tmp/browser-tools-deps/node_modules node - <<'NODE'
const puppeteer = require('puppeteer-core');
(async () => {
  const browser = await puppeteer.connect({ browserURL: 'http://127.0.0.1:9223' });
  const pages = await browser.pages();
  const page = pages.find((item) => item.url().startsWith('https://x.com')) || pages[0] || await browser.newPage();
  await page.goto('https://x.com/home', { waitUntil: 'domcontentloaded' });
  const cookies = await page.cookies('https://x.com');
  console.log({
    hasAuthToken: cookies.some((cookie) => cookie.name === 'auth_token'),
    hasCt0: cookies.some((cookie) => cookie.name === 'ct0'),
  });
  // Keep the tab open; repeated provider tab churn can trigger safety checks.
  await browser.disconnect();
})();
NODE
```

## Provider Notes

X OAuth 2.0 uses exact redirect URI matching. Current X docs require `http://127.0.0.1` for local development, not `localhost`. If X shows `Value passed for the redirect uri did not match the uri of the authorization code`, add the exact callback URI that the app sent, including protocol, host, port, path, and no extra trailing slash.

For local Social Poster on port `3006`, X must allow:

```text
http://127.0.0.1:3006/api/auth/callback
```

Production should allow:

```text
https://social.maxpetrusenko.com/api/auth/callback
```

LinkedIn and Meta also require exact callback matching. If testing locally from `localhost`, register the localhost callback. If testing from `127.0.0.1`, register the 127 callback.

## Reporting

Report only:

- Whether the provider saw the logged-in session.
- The exact redirect URI sent.
- The provider error message.
- Whether the app callback inserted a connection row.

Never report cookie values, access tokens, refresh tokens, auth codes, client secrets, or full unsanitized OAuth URLs.
