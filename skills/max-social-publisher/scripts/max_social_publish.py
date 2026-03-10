#!/usr/bin/env python3

import argparse
import base64
import json
import mimetypes
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


BASE_URL = os.environ.get("LATE_API_BASE_URL", "https://getlate.dev/api/v1").rstrip("/")
DEFAULT_IMAGE_MODEL = os.environ.get("GOOGLE_IMAGE_MODEL", "imagen-4.0-fast-generate-001")
DEFAULT_DRAFT_MODEL = os.environ.get("OPENAI_DRAFT_MODEL", "gpt-5")
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
PLATFORM_ALIASES = {
    "x": "twitter",
    "twitter/x": "twitter",
    "tweet": "twitter",
    "tweets": "twitter",
    "linkedin-company": "linkedin",
    "linkedin-page": "linkedin",
    "gmb": "googlebusiness",
    "google-business": "googlebusiness",
    "google_business": "googlebusiness",
}


def fail(message: str, code: int = 1) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(code)


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if value:
        return value
    fail(f"Missing required env var: {name}")


def require_any_env(*names: str) -> str:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    fail(f"Missing required env var. Tried: {', '.join(names)}")


def get_secret_value(name: str, doppler_project: str | None, doppler_config: str | None) -> str | None:
    value = os.environ.get(name)
    if value:
        return value
    if not doppler_project or not doppler_config:
        return None
    cmd = [
        "doppler",
        "--no-verify-tls",
        "secrets",
        "get",
        name,
        "--project",
        doppler_project,
        "--config",
        doppler_config,
        "--plain",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    secret = result.stdout.strip()
    return secret or None


def require_any_secret(
    names: tuple[str, ...],
    doppler_project: str | None,
    doppler_config: str | None,
) -> str:
    for name in names:
        value = get_secret_value(name, doppler_project, doppler_config)
        if value:
            return value
    fail(f"Missing required secret. Tried: {', '.join(names)}")


def request_json(method: str, url: str, headers: dict[str, str] | None = None, payload: Any | None = None) -> Any:
    data = None
    final_headers = dict(headers or {})
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        final_headers.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=data, headers=final_headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        fail(f"{method} {url} failed with {exc.code}: {body}")
    return json.loads(body) if body else {}


def request_bytes(method: str, url: str, headers: dict[str, str] | None = None, data: bytes | None = None) -> bytes:
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        fail(f"{method} {url} failed with {exc.code}: {body}")


def late_headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def load_content(args: argparse.Namespace) -> str:
    if args.content and args.content_file:
        fail("Use either --content or --content-file, not both.")
    if args.content:
        return args.content.strip()
    if args.content_file:
        return pathlib.Path(args.content_file).read_text(encoding="utf-8").strip()
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    fail("Provide post text via --content, --content-file, or stdin.")


def prompt_input(label: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    try:
        value = input(f"{label}{suffix}: ").strip()
    except EOFError:
        return default or ""
    return value or (default or "")


def prompt_yes_no(label: str, default: bool = True) -> bool:
    default_label = "Y/n" if default else "y/N"
    try:
        value = input(f"{label} [{default_label}]: ").strip().lower()
    except EOFError:
        return default
    if not value:
        return default
    return value in {"y", "yes"}


def parse_csv(values: str | None) -> list[str]:
    if not values:
        return []
    return [normalize_platform_name(item) for item in values.split(",") if item.strip()]


def normalize_platform_name(value: str) -> str:
    platform = value.strip().lower()
    return PLATFORM_ALIASES.get(platform, platform)


def parse_account_mappings(items: list[str]) -> dict[str, str]:
    mappings: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            fail(f"Invalid --account value: {item}. Expected platform=accountId")
        platform, account_id = item.split("=", 1)
        mappings[normalize_platform_name(platform)] = account_id.strip()
    return mappings


def parse_platform_configs(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    payload = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    return {normalize_platform_name(str(key)): value for key, value in payload.items()}


def try_fetch_text(url: str) -> str | None:
    try:
        return request_bytes("GET", url).decode("utf-8", errors="replace")
    except SystemExit:
        return None


def github_readme_from_repo_url(repo_url: str) -> str | None:
    match = re.match(r"https://github\.com/([^/]+)/([^/]+?)(?:\.git|/)?$", repo_url.strip())
    if not match:
        return None
    owner, repo = match.groups()
    candidates = [
        f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md",
        f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md",
        f"https://raw.githubusercontent.com/{owner}/{repo}/main/readme.md",
        f"https://raw.githubusercontent.com/{owner}/{repo}/master/readme.md",
    ]
    for candidate in candidates:
        text = try_fetch_text(candidate)
        if text:
            return text
    return None


def load_rule_text(name: str) -> str:
    path = SKILL_DIR / "rules" / name
    return path.read_text(encoding="utf-8")


def build_context_summary(args: argparse.Namespace) -> str:
    parts: list[str] = []
    if args.repo_url:
        parts.append(f"Repo URL: {args.repo_url}")
        readme = github_readme_from_repo_url(args.repo_url)
        if readme:
            parts.append("README excerpt:")
            parts.append(readme[:6000])
    if args.live_url:
        parts.append(f"Live URL: {args.live_url}")
    if args.demo_url:
        parts.append(f"Demo URL: {args.demo_url}")
    if args.project_notes:
        parts.append(f"Project notes: {args.project_notes}")
    return "\n\n".join(parts).strip()


def generate_drafts_with_openai(
    args: argparse.Namespace,
    doppler_project: str | None,
    doppler_config: str | None,
) -> list[str]:
    api_key = require_any_secret(
        ("OPENAI_API_KEY", "CHATGPT_API_KEY"),
        doppler_project,
        doppler_config,
    )
    prompt = f"""You write social posts for Max Petrusenko.

Follow these rules:
{load_rule_text('voice.md')}

Style anchors:
{load_rule_text('examples.md')}

Platform formatting:
{load_rule_text('platform-formatting.md')}

Project context:
{build_context_summary(args)}

Task:
Generate {args.draft_count} candidate posts for platform {', '.join(parse_csv(args.platforms) or ['twitter'])}.
Keep them high-signal, product-outcome first, technical-proof second.
Return JSON only with this schema:
{{"drafts":[{{"label":"...", "text":"...", "why":"..."}}]}}
"""
    payload = {
        "model": args.draft_model,
        "input": prompt,
        "text": {"verbosity": "low"},
    }
    response = request_json(
        "POST",
        "https://api.openai.com/v1/responses",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        payload=payload,
    )
    text = response.get("output_text", "")
    if not text:
        fail(f"Draft generation returned no output: {json.dumps(response)[:2000]}")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            fail(f"Could not parse draft output: {text}")
        parsed = json.loads(match.group(0))
    drafts = parsed.get("drafts", [])
    if not isinstance(drafts, list) or not drafts:
        fail(f"Draft output missing drafts: {parsed}")
    return [str(item.get("text", "")).strip() for item in drafts if str(item.get("text", "")).strip()]


def print_drafts(drafts: list[str]) -> None:
    for idx, draft in enumerate(drafts, start=1):
        print(f"\n[{idx}]\n{draft}\n")


def choose_draft_interactively(drafts: list[str]) -> str:
    print_drafts(drafts)
    choice = prompt_input("Select draft number or type custom")
    if choice.isdigit():
        index = int(choice) - 1
        if 0 <= index < len(drafts):
            return drafts[index]
    if choice:
        return choice
    fail("No draft selected.")


def interactive_collect(
    args: argparse.Namespace,
    api_key: str,
    doppler_project: str | None,
    doppler_config: str | None,
) -> None:
    if not args.repo_url:
        args.repo_url = prompt_input("Repo URL", args.repo_url)
    if not args.live_url:
        args.live_url = prompt_input("Live URL", args.live_url)
    if not args.demo_url:
        args.demo_url = prompt_input("Demo URL", args.demo_url)
    if not args.platforms:
        args.platforms = prompt_input("Platforms (comma-separated)", "x")

    if not args.profile_id:
        profiles = list_profiles(api_key)
        if len(profiles) == 1:
            args.profile_id = str(profiles[0].get("_id", ""))
            print(f"Using profile: {profiles[0].get('name')} ({args.profile_id})")
        elif profiles:
            print(json.dumps({"profiles": profiles}, indent=2))
            args.profile_id = prompt_input("Profile id")

    if not (args.content or args.content_file):
        drafts = generate_drafts_with_openai(args, doppler_project, doppler_config)
        args.content = choose_draft_interactively(drafts)

    if not args.media_file and not args.media_url:
        media_choice = prompt_input("Media file path, public media URL, or blank for none")
        if media_choice.startswith("http://") or media_choice.startswith("https://"):
            args.media_url = [media_choice]
        elif media_choice:
            args.media_file = [media_choice]

    if not args.publish_now and not args.scheduled_for:
        if prompt_yes_no("Publish now?", True):
            args.publish_now = True
        else:
            args.scheduled_for = prompt_input("Scheduled time (ISO 8601)")
            args.timezone = prompt_input("Timezone", args.timezone or "UTC")

    print("\nFinal draft:\n")
    print(args.content)
    if not prompt_yes_no("Publish this?", True):
        fail("Publish cancelled.")


def extract_items(payload: Any, key: str) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        candidate = payload.get(key)
        if isinstance(candidate, list):
            return [item for item in candidate if isinstance(item, dict)]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []


def list_profiles(api_key: str) -> list[dict[str, Any]]:
    payload = request_json("GET", f"{BASE_URL}/profiles", headers=late_headers(api_key))
    return extract_items(payload, "profiles")


def list_accounts(api_key: str, profile_id: str) -> list[dict[str, Any]]:
    query = urllib.parse.urlencode({"profileId": profile_id})
    payload = request_json("GET", f"{BASE_URL}/accounts?{query}", headers=late_headers(api_key))
    return extract_items(payload, "accounts")


def resolve_accounts(
    api_key: str,
    platforms: list[str],
    explicit_accounts: dict[str, str],
    profile_id: str | None,
) -> dict[str, str]:
    resolved = dict(explicit_accounts)
    missing = [platform for platform in platforms if platform not in resolved]
    if not missing:
        return resolved
    if not profile_id:
        fail(f"Missing account mappings for {', '.join(missing)} and no --profile-id provided.")

    accounts = list_accounts(api_key, profile_id)
    by_platform: dict[str, list[dict[str, Any]]] = {}
    for account in accounts:
        platform = str(account.get("platform", "")).lower()
        if platform:
            by_platform.setdefault(platform, []).append(account)

    for platform in missing:
        matches = by_platform.get(platform, [])
        if not matches:
            fail(f"No Late account found for platform '{platform}' in profile {profile_id}.")
        if len(matches) > 1:
            print(
                f"Warning: multiple accounts found for {platform}; using the first one. "
                f"Pass --account {platform}=... to select a different account.",
                file=sys.stderr,
            )
        account = matches[0]
        resolved[platform] = str(account.get("_id") or account.get("id") or "")
        if not resolved[platform]:
            fail(f"Late account for {platform} is missing an id field.")
    return resolved


def infer_mime(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    if mime:
        return mime
    return "application/octet-stream"


def infer_media_type(name: str, mime: str) -> str:
    if mime.startswith("image/"):
        return "image"
    if mime.startswith("video/"):
        return "video"
    if mime == "application/pdf" or name.lower().endswith(".pdf"):
        return "document"
    fail(f"Unsupported media type for {name} ({mime})")


def presign_upload(api_key: str, file_name: str, mime: str) -> tuple[str, str]:
    headers = late_headers(api_key)
    attempts = [
        {"filename": file_name, "contentType": mime},
        {"fileName": file_name, "fileType": mime},
    ]
    last_error = None
    for payload in attempts:
        try:
            response = request_json("POST", f"{BASE_URL}/media/presign", headers=headers, payload=payload)
            upload_url = response.get("uploadUrl")
            public_url = response.get("publicUrl") or response.get("fileUrl")
            if upload_url and public_url:
                return str(upload_url), str(public_url)
            last_error = f"Incomplete presign response: {response}"
        except SystemExit as exc:
            last_error = str(exc)
    fail(f"Unable to get Late presigned upload URL. Last error: {last_error}")


def upload_local_media(api_key: str, file_path: str) -> dict[str, str]:
    path = pathlib.Path(file_path)
    if not path.exists():
        fail(f"Media file does not exist: {file_path}")
    mime = infer_mime(path.name)
    media_type = infer_media_type(path.name, mime)
    upload_url, public_url = presign_upload(api_key, path.name, mime)
    request_bytes("PUT", upload_url, headers={"Content-Type": mime}, data=path.read_bytes())
    return {"type": media_type, "url": public_url}


def looks_like_base64(value: str) -> bool:
    if len(value) < 128:
        return False
    if not re.fullmatch(r"[A-Za-z0-9+/=\s_-]+", value):
        return False
    compact = re.sub(r"\s+", "", value).replace("-", "+").replace("_", "/")
    try:
        base64.b64decode(compact + "=" * (-len(compact) % 4), validate=False)
    except Exception:
        return False
    return True


def find_base64_blob(payload: Any) -> str | None:
    preferred_keys = ["bytesBase64Encoded", "b64_json", "imageBytes", "data"]
    if isinstance(payload, dict):
        for key in preferred_keys:
            value = payload.get(key)
            if isinstance(value, str) and looks_like_base64(value):
                return value
        for value in payload.values():
            found = find_base64_blob(value)
            if found:
                return found
    elif isinstance(payload, list):
        for item in payload:
            found = find_base64_blob(item)
            if found:
                return found
    elif isinstance(payload, str) and looks_like_base64(payload):
        return payload
    return None


def generate_image_with_google(prompt: str, model: str, aspect_ratio: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        fail("Missing GEMINI_API_KEY or GOOGLE_API_KEY for image fallback.")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:predict?key={api_key}"
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1, "aspectRatio": aspect_ratio},
    }
    response = request_json("POST", url, headers={"Content-Type": "application/json"}, payload=payload)
    blob = find_base64_blob(response)
    if not blob:
        fail(f"Google image response did not include an image payload: {json.dumps(response)[:1000]}")
    compact = re.sub(r"\s+", "", blob).replace("-", "+").replace("_", "/")
    image_bytes = base64.b64decode(compact + "=" * (-len(compact) % 4))
    out_dir = pathlib.Path(tempfile.mkdtemp(prefix="max-social-image-"))
    out_path = out_dir / "generated.png"
    out_path.write_bytes(image_bytes)
    return str(out_path)


def build_media_items(api_key: str, media_urls: list[str], media_files: list[str]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for url in media_urls:
        mime = infer_mime(url)
        items.append({"type": infer_media_type(url, mime), "url": url})
    for file_path in media_files:
        items.append(upload_local_media(api_key, file_path))
    return items


def list_mode(args: argparse.Namespace, api_key: str) -> None:
    if args.list_profiles:
        print(json.dumps({"profiles": list_profiles(api_key)}, indent=2))
        raise SystemExit(0)
    if args.list_accounts:
        if not args.profile_id:
            fail("--list-accounts requires --profile-id")
        print(json.dumps({"accounts": list_accounts(api_key, args.profile_id)}, indent=2))
        raise SystemExit(0)


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish or schedule social posts via Late API.")
    parser.add_argument("--content")
    parser.add_argument("--content-file")
    parser.add_argument("--interactive", action="store_true")
    parser.add_argument("--platforms", help="Comma-separated platform names.")
    parser.add_argument("--account", action="append", default=[], help="Explicit account mapping: platform=accountId")
    parser.add_argument("--platform-config-file", help="JSON file mapping platform -> platformSpecificData")
    parser.add_argument("--profile-id", help="Late profile id used to auto-resolve accounts.")
    parser.add_argument("--repo-url")
    parser.add_argument("--live-url")
    parser.add_argument("--demo-url")
    parser.add_argument("--project-notes")
    parser.add_argument("--draft-count", type=int, default=5)
    parser.add_argument("--draft-model", default=DEFAULT_DRAFT_MODEL)
    parser.add_argument("--draft-only", action="store_true")
    parser.add_argument("--doppler-project", default=os.environ.get("DOPPLER_PROJECT", "api_keys"))
    parser.add_argument("--doppler-config", default=os.environ.get("DOPPLER_CONFIG", "dev"))
    parser.add_argument("--publish-now", action="store_true")
    parser.add_argument("--scheduled-for", help="ISO 8601 schedule timestamp.")
    parser.add_argument("--timezone", help="Optional IANA timezone for scheduled posts.")
    parser.add_argument("--media-url", action="append", default=[], help="Public media URL to attach.")
    parser.add_argument("--media-file", action="append", default=[], help="Local media file to upload.")
    parser.add_argument("--image-prompt", help="Generate an image if no media is attached.")
    parser.add_argument("--image-model", default=DEFAULT_IMAGE_MODEL)
    parser.add_argument("--image-aspect-ratio", default="1:1")
    parser.add_argument("--list-profiles", action="store_true")
    parser.add_argument("--list-accounts", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    api_key = require_any_secret(
        ("LATE_API_KEY", "GETLATE_API_KEY", "GETLATE_DEV_API_KEY_LIFETIME", "GETLATE_DEV_API_KEY_FREE"),
        args.doppler_project,
        args.doppler_config,
    )
    list_mode(args, api_key)

    if args.publish_now and args.scheduled_for:
        fail("Use either --publish-now or --scheduled-for, not both.")

    if args.interactive:
        interactive_collect(args, api_key, args.doppler_project, args.doppler_config)

    if args.draft_only:
        drafts = generate_drafts_with_openai(args, args.doppler_project, args.doppler_config)
        print_drafts(drafts)
        return

    content = load_content(args)
    explicit_accounts = parse_account_mappings(args.account)
    platform_configs = parse_platform_configs(args.platform_config_file)
    platforms = parse_csv(args.platforms) or list(explicit_accounts.keys())
    if not platforms:
        fail("Provide --platforms or at least one --account mapping.")

    media_files = list(args.media_file)
    if not args.media_url and not media_files and args.image_prompt:
        media_files.append(generate_image_with_google(args.image_prompt, args.image_model, args.image_aspect_ratio))

    media_items = build_media_items(api_key, list(args.media_url), media_files)
    accounts = resolve_accounts(api_key, platforms, explicit_accounts, args.profile_id)

    payload: dict[str, Any] = {
        "content": content,
        "platforms": [],
    }

    for platform in platforms:
        entry: dict[str, Any] = {"platform": platform, "accountId": accounts[platform]}
        if platform in platform_configs:
            entry["platformSpecificData"] = platform_configs[platform]
        payload["platforms"].append(entry)

    if media_items:
        payload["mediaItems"] = media_items
    if args.publish_now:
        payload["publishNow"] = True
    elif args.scheduled_for:
        payload["scheduledFor"] = args.scheduled_for
        if args.timezone:
            payload["timezone"] = args.timezone

    if args.dry_run:
        print(json.dumps({"baseUrl": BASE_URL, "payload": payload}, indent=2))
        return

    response = request_json("POST", f"{BASE_URL}/posts", headers=late_headers(api_key), payload=payload)
    print(json.dumps(response, indent=2))


if __name__ == "__main__":
    main()
