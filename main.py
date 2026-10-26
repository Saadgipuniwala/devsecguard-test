import hmac
import hashlib
import os
from fastapi import FastAPI, Request, HTTPException, Header
from dotenv import load_dotenv
from github_client import fetch_pr_diff
from scanner import run_static_analysis
from ai_engine import analyze_diff_with_llm
from publisher import post_pr_review

load_dotenv()

app = FastAPI(title="DevSecGuard AI Backend")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "super_secret_devsecguard_key_123")


def verify_signature(payload_body: bytes, signature_header: str) -> bool:
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected_hash = hmac.new(
        WEBHOOK_SECRET.encode(), payload_body, hashlib.sha256
    ).hexdigest()
    received_hash = signature_header.split("sha256=")[1]
    return hmac.compare_digest(expected_hash, received_hash)


@app.post("/webhook")
async def handle_github_webhook(
    request: Request, x_hub_signature_256: str = Header(None)
):
    body = await request.body()

    if not verify_signature(body, x_hub_signature_256):
        raise HTTPException(
            status_code=401, detail="Invalid HMAC X-Hub-Signature-256"
        )

    payload = await request.json()
    action = payload.get("action")

    if action in ["opened", "synchronize", "reopened"]:
        pr_number = payload["pull_request"]["number"]
        repo_name = payload["repository"]["full_name"]
        commit_sha = payload["pull_request"]["head"]["sha"]

        print(
            f"\n[+] Event Received: PR #{pr_number} on '{repo_name}' (Commit: {commit_sha[:7]})"
        )

        try:
            # 1. Fetch Raw Diff
            diff = fetch_pr_diff(repo_name, pr_number)
            print("[✓] Raw Code Diff Fetched.")

            # 2. Run Static SAST Engine
            static_findings = run_static_analysis(diff)
            print(f"[✓] Static Analysis Complete ({len(static_findings)} rule triggers).")

            # 3. LLM Reasoning Engine
            print("[*] Executing LLM Analysis...")
            review = analyze_diff_with_llm(diff, static_findings)
            print(f"[✓] Security Verdict: {review.verdict}")

            # 4. Post Inline Comments to GitHub
            print("[*] Publishing inline review to GitHub PR...")
            post_pr_review(repo_name, pr_number, commit_sha, review)

        except Exception as e:
            print(f"[-] Pipeline execution error: {str(e)}")

    return {"status": "accepted"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)