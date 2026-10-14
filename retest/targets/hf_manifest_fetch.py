import json, subprocess, sys
items = [("models/OpenTO/NFAE", "120c69fd08"), ("models/OpenTO/LDM", "59aca1e92d"), ("datasets/OpenTO/OpenTO", "c553a645a1")]
out = {}
for repo, short in items:
    info = json.loads(subprocess.run(["curl", "-sL", f"https://huggingface.co/api/{repo}"], capture_output=True, text=True).stdout)
    sha = info["sha"]; assert sha.startswith(short), (repo, sha)
    path = "data" if repo.startswith("datasets") else ""
    tree = json.loads(subprocess.run(["curl", "-sL", f"https://huggingface.co/api/{repo}/tree/{sha}/{path}"], capture_output=True, text=True).stdout)
    out[repo] = {"sha": sha, "files": {e["path"]: {"size": e.get("size"), "sha256": (e.get("lfs") or {}).get("oid")} for e in tree if e.get("type") == "file"}}
json.dump(out, open("hf_manifest.json", "w"), indent=2)
for repo, d in out.items():
    print(repo, d["sha"])
    for p, f in d["files"].items():
        print("   ", p, f["size"], (f["sha256"] or "")[:16])
