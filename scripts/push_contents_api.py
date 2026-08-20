#!/usr/bin/env python3
"""Push files via GitHub Contents API (one at a time, more reliable than Git Data API)."""

import os, sys, json, base64, subprocess, time, requests

REPO = "yigenfeng0707-netizen/yiwu-global-ai-agent"
WORK_DIR = r"D:\YiWuInternetCompetition"
API = f"https://api.github.com/repos/{REPO}/contents"

def get_token():
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()

def upload_file(filepath, content_b64, commit_msg, sha=None, retries=5):
    """Upload a single file via Contents API."""
    for attempt in range(retries):
        token = get_token()
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
        }
        data = {
            "message": commit_msg,
            "content": content_b64,
        }
        if sha:
            data["sha"] = sha

        r = requests.put(
            f"{API}/{filepath}",
            data=json.dumps(data),
            headers=headers,
            timeout=60,
        )
        if r.status_code in (200, 201):
            return r.json()
        if r.status_code == 401:
            print(f"  401 retry {attempt+1}", flush=True)
            time.sleep(5)
            continue
        if r.status_code == 403:
            # Rate limit or abuse limit
            print(f"  403 wait 30s", flush=True)
            time.sleep(30)
            continue
        if r.status_code == 409:
            # Conflict - file might already exist, try to get its SHA
            print(f"  409 conflict, getting SHA...", flush=True)
            get_r = requests.get(f"{API}/{filepath}", headers=headers, timeout=30)
            if get_r.status_code == 200:
                existing_sha = get_r.json()["sha"]
                data["sha"] = existing_sha
                r2 = requests.put(f"{API}/{filepath}", data=json.dumps(data), headers=headers, timeout=60)
                if r2.status_code in (200, 201):
                    return r2.json()
            time.sleep(3)
            continue
        if r.status_code == 422:
            print(f"  422: {r.text[:200]}", flush=True)
            return None
        print(f"  Error {r.status_code}: {r.text[:150]}", flush=True)
        time.sleep(5)
    return None

# Get all tracked files
result = subprocess.run(["git", "ls-files", "-z"], capture_output=True, cwd=WORK_DIR)
files = [f.decode("utf-8") for f in result.stdout.split(b"\x00") if f]
files = [f for f in files if f.strip()]
# README.md already uploaded
files = [f for f in files if f != "README.md"]
print(f"Files to upload: {len(files)}", flush=True)

success = 0
failed = []
for idx, fp in enumerate(files):
    full = os.path.join(WORK_DIR, fp.replace("/", os.sep))
    if not os.path.exists(full):
        print(f"[{idx+1}/{len(files)}] SKIP: {fp}", flush=True)
        continue

    # Contents API has 100MB limit per file
    file_size = os.path.getsize(full)
    if file_size > 100 * 1024 * 1024:
        print(f"[{idx+1}/{len(files)}] SKIP (too large): {fp}", flush=True)
        continue

    with open(full, "rb") as f:
        content_b64 = base64.b64encode(f.read()).decode("utf-8")

    result = upload_file(fp, content_b64, f"Add {fp}")
    if result:
        success += 1
        print(f"[{idx+1}/{len(files)}] OK: {fp}", flush=True)
    else:
        failed.append(fp)
        print(f"[{idx+1}/{len(files)}] FAIL: {fp}", flush=True)

    # Small delay to avoid rate limiting
    time.sleep(0.5)

print(f"\nUploaded: {success}/{len(files)}", flush=True)
if failed:
    print(f"Failed: {failed}", flush=True)
print(f"\nView at: https://github.com/{REPO}", flush=True)
print("\n=== PUSH COMPLETE ===", flush=True)
