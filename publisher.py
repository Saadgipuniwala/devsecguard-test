import os
import requests
from schemas import ReviewResponse

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def post_pr_review(
    repo_name: str, pr_number: int, commit_sha: str, review: ReviewResponse
):
    """Publishes structured AI security findings as inline PR review comments on GitHub."""
    if not GITHUB_TOKEN:
        print("[-] GITHUB_TOKEN missing in .env. Skipping GitHub review posting.")
        return

    url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}/reviews"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    # Build line-specific inline comments
    comments = []
    for finding in review.findings:
        comment_body = (
            f"### ⚠️ [{finding.severity}] {finding.title}\n\n"
            f"**Explanation:** {finding.explanation}\n\n"
            f"**Suggested Fix:**\n```python\n{finding.suggested_fix}\n```"
        )
        comments.append(
            {
                "path": finding.file_path,
                "line": finding.line_number,
                "side": "RIGHT",
                "body": comment_body,
            }
        )

    # Map AI verdict to GitHub API review event
    event_map = {
        "APPROVE": "APPROVE",
        "REQUEST_CHANGES": "REQUEST_CHANGES",
        "COMMENT": "COMMENT",
    }
    event_type = event_map.get(review.verdict.upper(), "COMMENT")

    review_payload = {
        "commit_id": commit_sha,
        "body": f"## 🛡️ DevSecGuard AI Security Review\n\n**Verdict:** `{review.verdict}`\n\n**Summary:** {review.summary}",
        "event": event_type,
        "comments": comments,
    }

    try:
        response = requests.post(url, headers=headers, json=review_payload)
        if response.status_code in [200, 201]:
            print(f"[✓] Successfully published inline review comments on GitHub PR #{pr_number}!")
        else:
            print(f"[!] Primary review post failed ({response.status_code}): {response.text}")
            # Fallback: Post main summary comment if inline line numbers mismatch diff
            if comments:
                print("[*] Retrying review summary without inline comments...")
                review_payload["comments"] = []
                fallback_res = requests.post(url, headers=headers, json=review_payload)
                if fallback_res.status_code in [200, 201]:
                    print("[✓] Fallback review summary published on GitHub!")
    except Exception as e:
        print(f"[-] Error publishing review to GitHub: {str(e)}")