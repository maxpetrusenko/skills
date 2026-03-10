# Late API

## Supported Platforms

Late supports:

- twitter
- instagram
- facebook
- linkedin
- tiktok
- youtube
- pinterest
- reddit
- bluesky
- threads
- googlebusiness
- telegram
- snapchat

Useful aliases for local usage:

- `x` -> `twitter`
- `gmb` -> `googlebusiness`

## Core Publish Payload

Create a post with:

- `content`
- `platforms: [{ platform, accountId }]`
- one of:
  - `publishNow: true`
  - `scheduledFor: ISO timestamp`
  - omitted for draft

Optional:

- `mediaItems: [{ type, url }]`
- `timezone`
- `platformSpecificData` inside each platform entry

## Media

If media is already publicly accessible, pass it directly in `mediaItems`.

If media is local:

1. request `POST /v1/media/presign`
2. upload file with `PUT` to returned `uploadUrl`
3. use `publicUrl` or `fileUrl` in `mediaItems`

## Helpful Endpoints

- `GET /v1/profiles`
- `GET /v1/accounts?profileId=...`
- `POST /v1/posts`
- `POST /v1/media/presign`

## Important Constraints

- use real Late `accountId`, not profile key or username
- use ISO 8601 timestamps for scheduling
- prefer `publishNow: true` for immediate publish
- omit `publishNow` when scheduling
- platform-specific quirks matter; if a post spans multiple platforms, shorten or customize where needed

## Script Env Fallbacks

The publish helper accepts any of these env names:

- `LATE_API_KEY`
- `GETLATE_API_KEY`
- `GETLATE_DEV_API_KEY_LIFETIME`
- `GETLATE_DEV_API_KEY_FREE`
