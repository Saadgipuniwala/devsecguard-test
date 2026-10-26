# DevSecGuard AI 🛡️

**DevSecGuard AI** is an automated Application Security (AppSec) agent designed to analyze GitHub Pull Requests for security vulnerabilities in real time. It combines a regex-based Static Application Security Testing (SAST) scanner with Gemini LLM reasoning to validate security alerts, reduce false positives, and post actionable, line-specific code fixes directly to GitHub PR diffs.

---

## Key Features

- **Automated Webhook Integration**: Listens to GitHub `pull_request` events (`opened`, `reopened`, `synchronize`).
- **Hybrid Security Engine**:
  - **Static Analysis**: Fast local regex engine detecting hardcoded API keys, JWT secrets, unsafe exec calls, and SQL injection patterns.
  - **LLM Reasoning**: Leverages `gemini-3.8-flash` via the `google-genai` SDK to evaluate diff context, filter out false positives, and recommend precise code remediations.
- **Resilient Execution**: Built-in exponential backoff retry logic using `tenacity` to handle transient API load spikes seamlessly.
- **Inline GitHub Code Annotations**: Automatically leaves targeted inline review comments directly on vulnerable lines within the Pull Request.

---

## Tech Stack

- **Framework**: Python 3.11+, FastAPI, Uvicorn
- **AI Engine**: Google GenAI SDK (`google-genai`), `gemini-3.8-flash`
- **Data Validation**: Pydantic v2
- **Resilience**: Tenacity (Exponential Backoff)
- **Integrations**: GitHub REST API & Webhooks, ngrok (Local Tunneling)

---

## System Architecture
┌─────────────────┐       ┌─────────────────┐       ┌──────────────────┐
│   GitHub PR     │ ───>  │  FastAPI Server │ ───>  │   SAST Scanner   │
│ (Webhook Event) │       │   (/webhook)    │       │ (Regex Engine)   │
└─────────────────┘       └─────────────────┘       └──────────────────┘
│
▼
┌─────────────────┐       ┌─────────────────┐       ┌──────────────────┐
│  GitHub Review  │  <─── │ Pydantic Validation     │  <─── │ Gemini LLM Engine│
│ (Inline Comments)│       │ (Structured Output) │       │(gemini-3.8-flash)│
└─────────────────┘       └─────────────────┘       └──────────────────┘
---

## Project Structure

```text
devsecguard-ai/
├── main.py            # FastAPI webhook listener & GitHub REST API driver
├── ai_engine.py        # Gemini API client with tenacity retry resilience
├── schemas.py          # Pydantic models for structured review output
├── SAST.py            # Local SAST regex rule definition scanner
├── .env               # Environment secrets (ignored by Git)
├── .gitignore         # Git ignore rules
└── requirements.txt   # Frozen Python dependencies

Setup & Installation
1. Prerequisites
Python 3.10+

ngrok installed

Personal @gmail.com Google AI Studio API Key

2. Clone and Environment Setup
PowerShell
git clone [https://github.com/Saadgipuniwala/devsecguard-test.git](https://github.com/Saadgipuniwala/devsecguard-test.git)
cd devsecguard-test

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
3. Environment Configuration
Create a .env file in the root directory:

Code snippet
WEBHOOK_SECRET=your_github_webhook_secret
GITHUB_TOKEN=ghp_your_github_personal_access_token
GEMINI_API_KEY=AIzaSy_your_gemini_api_key
Running the Application
Start the FastAPI Server:

PowerShell
.\venv\Scripts\python.exe main.py
Expose Localhost via ngrok:

PowerShell
ngrok http 8000
Configure GitHub Webhook:

Go to your GitHub Repository -> Settings -> Webhooks -> Add webhook.

Payload URL: https://<your-ngrok-subdomain>.ngrok-free.app/webhook

Content type: application/json

Secret: Value matching WEBHOOK_SECRET in .env

Events: Select Pull requests.

License
Distributed under the MIT License.


---

### Push `README.md` to GitHub

To upload this file to your repository, run these commands in PowerShell:

```powershell
git add README.md
git commit -m "docs: add project README with architecture, setup, and usage guide"
git push origin main
