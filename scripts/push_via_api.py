#!/usr/bin/env python3
"""Push all files to GitHub via Git Data API - Step 2: Create tree, commit, and update ref."""

import os
import sys
import json
import base64
import subprocess
import time
import requests

REPO = "yigenfeng0707-netizen/yiwu-global-ai-agent"
WORK_DIR = r"D:\YiWuInternetCompetition"
API_BASE = f"https://api.github.com/repos/{REPO}/git"

def get_token():
    result = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True)
    return result.stdout.strip()

TOKEN = get_token()
session = requests.Session()
session.headers.update({
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json",
})

def api_request(method, url, data=None, max_retries=5):
    for attempt in range(max_retries):
        try:
            if method == "GET":
                resp = session.get(url, timeout=30)
            elif method == "POST":
                resp = session.post(url, data=json.dumps(data), timeout=60)
            elif method == "PATCH":
                resp = session.patch(url, data=json.dumps(data), timeout=30)
            else:
                raise ValueError(f"Unknown method: {method}")

            if resp.status_code in (200, 201):
                return resp.json()
            elif resp.status_code == 401:
                print(f"  401 - refreshing token (attempt {attempt+1})...")
                new_token = get_token()
                session.headers["Authorization"] = f"token {new_token}"
                time.sleep(2 * (attempt + 1))
                continue
            elif resp.status_code == 403:
                reset = resp.headers.get("X-RateLimit-Reset")
                if reset:
                    wait = max(int(reset) - int(time.time()) + 1, 5)
                    print(f"  Rate limited, waiting {wait}s...")
                    time.sleep(wait)
                    continue
                time.sleep(5 * (attempt + 1))
                continue
            else:
                print(f"  API Error {resp.status_code}: {resp.text[:300]}")
                time.sleep(3 * (attempt + 1))
                continue
        except requests.exceptions.RequestException as e:
            print(f"  Request error: {e}")
            time.sleep(5 * (attempt + 1))
    return None

# Step 0: Get current main ref
print("Getting current main branch ref...")
ref_data = api_request("GET", f"{API_BASE}/refs/heads/main")
if not ref_data:
    print("ERROR: Cannot get main branch ref")
    sys.exit(1)

parent_sha = ref_data["object"]["sha"]
print(f"Current main SHA: {parent_sha}")

commit_data = api_request("GET", f"{API_BASE}/commits/{parent_sha}")
base_tree_sha = commit_data["tree"]["sha"]
print(f"Base tree SHA: {base_tree_sha}")

# Step 1: Get all tracked files
result = subprocess.run(["git", "ls-files", "-z"], capture_output=True, cwd=WORK_DIR)
all_files = [f.decode('utf-8') for f in result.stdout.split(b'\x00') if f]
all_files = [f for f in all_files if f.strip()]
files = [f for f in all_files if f != "README.md"]
print(f"Files to upload: {len(files)}")

# Step 2: Create blobs for all files
blob_shas = {}
failed_files = []
for i, filepath in enumerate(files):
    full_path = os.path.join(WORK_DIR, filepath.replace("/", os.sep))
    print(f"[{i+1}/{len(files)}] Creating blob: {filepath}", flush=True)

    if not os.path.exists(full_path):
        print(f"  SKIP: File not found", flush=True)
        continue

    file_size = os.path.getsize(full_path)
    if file_size > 50 * 1024 * 1024:
        print(f"  SKIP: File too large ({file_size} bytes)", flush=True)
        continue

    with open(full_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    blob_data = api_request("POST", f"{API_BASE}/blobs", {
        "content": content,
        "encoding": "base64"
    })

    if blob_data:
        blob_shas[filepath] = blob_data["sha"]
        print(f"  OK: {blob_data['sha'][:12]}", flush=True)
    else:
        print(f"  FAILED after retries", flush=True)
        failed_files.append(filepath)

print(f"\nBlobs created: {len(blob_shas)}/{len(files)}", flush=True)
if failed_files:
    print(f"Failed files: {failed_files}", flush=True)

if not blob_shas:
    print("No blobs created, aborting.")
    sys.exit(1)

# Step 3: Create tree
print(f"\nCreating tree with {len(blob_shas)} items...", flush=True)
tree_items = []
for filepath, sha in blob_shas.items():
    tree_items.append({
        "path": filepath,
        "mode": "100644",
        "type": "blob",
        "sha": sha
    })

tree_data = api_request("POST", f"{API_BASE}/trees", {
    "base_tree": base_tree_sha,
    "tree": tree_items
})

if not tree_data:
    print("ERROR: Failed to create tree")
    sys.exit(1)

tree_sha = tree_data["sha"]
print(f"Tree SHA: {tree_sha}", flush=True)

# Step 4: Create commit
print("\nCreating commit...", flush=True)
commit_msg = "feat: 义乌小商品出海智能体-OPC V2.0冠军版 - 7大AI Agent全链路 - 义乌发展经验国家战略 - 39城1039模式复制推广 - OPC模式1人+7Agent - DashScope LLM集成 - GitHub Actions CI/CD"

commit_data = api_request("POST", f"{API_BASE}/commits", {
    "message": commit_msg,
    "tree": tree_sha,
    "parents": [parent_sha]
})

if not commit_data:
    print("ERROR: Failed to create commit")
    sys.exit(1)

commit_sha = commit_data["sha"]
print(f"Commit SHA: {commit_sha}", flush=True)

# Step 5: Update main branch ref
print("\nUpdating main branch ref...", flush=True)
ref_update = api_request("PATCH", f"{API_BASE}/refs/heads/main", {
    "sha": commit_sha,
    "force": True
})

if ref_update:
    print(f"\nSUCCESS! Main branch updated to: {commit_sha}", flush=True)
    print(f"View at: https://github.com/{REPO}", flush=True)
else:
    print("ERROR: Failed to update ref")
    sys.exit(1)

print("\n=== PUSH COMPLETE ===", flush=True)
