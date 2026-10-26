import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
from schemas import ReviewResponse

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def analyze_diff_with_llm(diff: str, static_findings: list[dict]) -> ReviewResponse:
    if not GEMINI_API_KEY:
        return ReviewResponse(
            verdict="COMMENT",
            summary="Gemini API Key missing in .env. Skipping AI analysis.",
            findings=[],
        )

    client = genai.Client(api_key=GEMINI_API_KEY)

    formatted_findings = (
        json.dumps(static_findings, indent=2)
        if static_findings
        else "No static issues found."
    )

    prompt = (
        f"### Static Analysis Scanner Alerts:\n{formatted_findings}\n\n"
        f"### Raw Code Diff:\n```diff\n{diff}\n```\n\n"
        "Instructions:\n"
        "1. Review the diff and static findings for security vulnerabilities (secrets, injection, logic errors).\n"
        "2. Validate static alerts to eliminate false positives.\n"
        "3. Return line-specific findings and actionable security recommendations."
    )

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=4, max=20),
        reraise=True,
    )
    def call_gemini():
        return client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are DevSecGuard AI, an expert automated AppSec reviewer analyzing Pull Request diffs.",
                response_mime_type="application/json",
                response_schema=ReviewResponse,
                temperature=0.2,
            ),
        )

    try:
        print("[*] Querying Gemini API (gemini-3.8-flash)...")
        response = call_gemini()
        return ReviewResponse.model_validate_json(response.text)

    except Exception as e:
        print(f"[-] Gemini API Error: {str(e)}")
        return ReviewResponse(
            verdict="COMMENT",
            summary=f"Automated AI analysis encountered a temporary API capacity issue: {str(e)[:120]}",
            findings=[],
        )