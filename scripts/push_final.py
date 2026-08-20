#!/usr/bin/env python3
"""One-shot push: create all blobs then immediately create tree, commit, and ref."""

import os, sys, json, base64, subprocess, time, requests

REPO = "yigenfeng0707-netizen/yiwu-global-ai-agent"
WORK_DIR = r"D:\YiWuInternetCompetition"
API = f"https://api.github.com/repos/{REPO}/git"

# Get token once
token = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()
HEADERS = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github+json",
}

def refresh_token():
    global token, HEADERS
    token = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()
    HEADERS["Authorization"] = f"token {token}"

def api(method, url, data=None, retries=8):
    for i in range(retries):
        try:
            if method == "GET":
                r = requests.get(url, headers=HEADERS, timeout=30)
            elif method == "POST":
                r = requests.post(url, data=json.dumps(data), headers=HEADERS, timeout=60)
            elif method == "PATCH":
                r = requests.patch(url, data=json.dumps(data), headers=HEADERS, timeout=30)
            if r.status_code in (200, 201):
                return r.json()
            if r.status_code == 401:
                refresh_token()
                time.sleep(3)
                continue
            if r.status_code == 403:
                time.sleep(30)
                continue
            if r.status_code == 404:
                time.sleep(3)
                continue
            print(f"  Error {r.status_code}: {r.text[:150]}", flush=True)
            time.sleep(3)
        except Exception as e:
            print(f"  Exc: {e}", flush=True)
            time.sleep(5)
    return None

# Step 0: Get current ref
print("Getting ref...", flush=True)
ref = api("GET", f"{API}/refs/heads/main")
parent_sha = ref["object"]["sha"]
commit = api("GET", f"{API}/commits/{parent_sha}")
base_tree = commit["tree"]["sha"]
print(f"Parent: {parent_sha}", flush=True)

# Step 1: Get files
result = subprocess.run(["git", "ls-files", "-z"], capture_output=True, cwd=WORK_DIR)
files = [f.decode("utf-8") for f in result.stdout.split(b"\x00") if f]
files = [f for f in files if f.strip() and f != "README.md"]
print(f"Files: {len(files)}", flush=True)

# Step 2: Create blobs and collect SHAs
blobs = {}
for idx, fp in enumerate(files):
    full = os.path.join(WORK_DIR, fp.replace("/", os.sep))
    if not os.path.exists(full):
        continue
    with open(full, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")
    bd = api("POST", f"{API}/blobs", {"content": content, "encoding": "base64"})
    if bd and "sha" in bd:
        blobs[fp] = bd["sha"]
        print(f"[{idx+1}/{len(files)}] OK: {fp}", flush=True)
    else:
        print(f"[{idx+1}/{len(files)}] FAIL: {fp}", flush=True)

print(f"Blobs: {len(blobs)}", flush=True)

# Step 3: Create tree (immediately after blobs, with fresh token)
print("Creating tree...", flush=True)
refresh_token()  # Fresh token for tree creation
items = [{"path": p, "mode": "100644", "type": "blob", "sha": s} for p, s in blobs.items()]
tree = api("POST", f"{API}/trees", {"base_tree": base_tree, "tree": items})
if not tree or "sha" not in tree:
    print("Tree FAILED!", flush=True)
    # Try without base_tree
    print("Retrying without base_tree...", flush=True)
    refresh_token()
    tree = api("POST", f"{API}/trees", {"tree": items})
    if not tree or "sha" not in tree:
        print("Tree still FAILED!", flush=True)
        sys.exit(1)

tree_sha = tree["sha"]
print(f"Tree: {tree_sha}", flush=True)

# Step 4: Create commit
print("Creating commit...", flush=True)
refresh_token()
cd = api("POST", f"{API}/commits", {
    "message": "feat: OPC V2.0 - 7 AI Agents - DashScope LLM - CI/CD",
    "tree": tree_sha,
    "parents": [parent_sha]
})
if not cd or "sha" not in cd:
    print("Commit FAILED!", flush=True)
    sys.exit(1)
commit_sha = cd["sha"]
print(f"Commit: {commit_sha}", flush=True)

# Step 5: Update ref
print("Updating ref...", flush=True)
refresh_token()
ru = api("PATCH", f"{API}/refs/heads/main", {"sha": commit_sha, "force": True})
if ru:
    print(f"\nSUCCESS! {commit_sha}", flush=True)
    print(f"https://github.com/{REPO}", flush=True)
else:
    print("Ref FAILED!", flush=True)
    sys.exit(1)
