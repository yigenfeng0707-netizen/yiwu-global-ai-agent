#!/usr/bin/env python3
"""Push all files to GitHub via gh api (auto-handles auth)."""

import os
import sys
import json
import base64
import subprocess
import time

REPO = "yigenfeng0707-netizen/yiwu-global-ai-agent"
WORK_DIR = r"D:\YiWuInternetCompetition"

def gh_api(endpoint, method="GET", data=None, max_retries=5):
    """Call GitHub API via gh CLI (handles auth automatically)."""
    for attempt in range(max_retries):
        cmd = ["gh", "api", endpoint]
        if method != "GET":
            cmd.extend(["--method", method])

        if data is not None:
            # Write data to temp file and use --input
            tmp = os.path.join(os.environ.get("TEMP", "/tmp"), f"gh_api_{os.getpid()}.json")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            cmd.extend(["--input", tmp])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"raw": result.stdout}

        stderr = result.stderr
        if "401" in stderr or "authentication" in stderr.lower():
            print(f"  401 error, retrying ({attempt+1}/{max_retries})...")
            time.sleep(3 * (attempt + 1))
            continue
        if "403" in stderr or "rate limit" in stderr.lower():
            print(f"  Rate limited, waiting ({attempt+1}/{max_retries})...")
            time.sleep(30 * (attempt + 1))
            continue
        if "404" in stderr:
            print(f"  404 Not Found, retrying ({attempt+1}/{max_retries})...")
            time.sleep(5 * (attempt + 1))
            continue

        print(f"  API Error: {stderr[:300]}")
        time.sleep(3)

    return None

# Step 0: Get current main ref
print("Getting current main branch ref...", flush=True)
ref_data = gh_api(f"repos/{REPO}/git/refs/heads/main")
if not ref_data:
    print("ERROR: Cannot get main branch ref")
    sys.exit(1)

parent_sha = ref_data["object"]["sha"]
print(f"Current main SHA: {parent_sha}", flush=True)

commit_data = gh_api(f"repos/{REPO}/git/commits/{parent_sha}")
base_tree_sha = commit_data["tree"]["sha"]
print(f"Base tree SHA: {base_tree_sha}", flush=True)

# Step 1: Get all tracked files
result = subprocess.run(["git", "ls-files", "-z"], capture_output=True, cwd=WORK_DIR)
all_files = [f.decode('utf-8') for f in result.stdout.split(b'\x00') if f]
all_files = [f for f in all_files if f.strip()]
files = [f for f in all_files if f != "README.md"]
print(f"Files to upload: {len(files)}", flush=True)

# Step 2: Create blobs
blob_shas = {}
failed_files = []
for i, filepath in enumerate(files):
    full_path = os.path.join(WORK_DIR, filepath.replace("/", os.sep))
    print(f"[{i+1}/{len(files)}] Blob: {filepath}", flush=True)

    if not os.path.exists(full_path):
        print(f"  SKIP: not found", flush=True)
        continue

    file_size = os.path.getsize(full_path)
    if file_size > 50 * 1024 * 1024:
        print(f"  SKIP: too large", flush=True)
        continue

    with open(full_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    blob_data = gh_api(f"repos/{REPO}/git/blobs", "POST", {
        "content": content,
        "encoding": "base64"
    })

    if blob_data and "sha" in blob_data:
        blob_shas[filepath] = blob_data["sha"]
        print(f"  OK: {blob_data['sha'][:12]}", flush=True)
    else:
        print(f"  FAILED", flush=True)
        failed_files.append(filepath)

print(f"\nBlobs: {len(blob_shas)}/{len(files)}", flush=True)
if failed_files:
    print(f"Failed: {failed_files}", flush=True)

if not blob_shas:
    print("No blobs, aborting.")
    sys.exit(1)

# Step 3: Create tree
print(f"\nCreating tree ({len(blob_shas)} items)...", flush=True)
tree_items = []
for filepath, sha in blob_shas.items():
    tree_items.append({
        "path": filepath,
        "mode": "100644",
        "type": "blob",
        "sha": sha
    })

tree_data = gh_api(f"repos/{REPO}/git/trees", "POST", {
    "base_tree": base_tree_sha,
    "tree": tree_items
})

if not tree_data or "sha" not in tree_data:
    print("ERROR: Failed to create tree")
    sys.exit(1)

tree_sha = tree_data["sha"]
print(f"Tree SHA: {tree_sha}", flush=True)

# Step 4: Create commit
print("\nCreating commit...", flush=True)
commit_data = gh_api(f"repos/{REPO}/git/commits", "POST", {
    "message": "feat: OPC V2.0 - 7 AI Agents - DashScope LLM - CI/CD",
    "tree": tree_sha,
    "parents": [parent_sha]
})

if not commit_data or "sha" not in commit_data:
    print("ERROR: Failed to create commit")
    sys.exit(1)

commit_sha = commit_data["sha"]
print(f"Commit SHA: {commit_sha}", flush=True)

# Step 5: Update ref
print("\nUpdating main ref...", flush=True)
ref_update = gh_api(f"repos/{REPO}/git/refs/heads/main", "PATCH", {
    "sha": commit_sha,
    "force": True
})

if ref_update:
    print(f"\nSUCCESS! {commit_sha}", flush=True)
    print(f"https://github.com/{REPO}", flush=True)
else:
    print("ERROR: Failed to update ref")
    sys.exit(1)

print("\n=== PUSH COMPLETE ===", flush=True)
