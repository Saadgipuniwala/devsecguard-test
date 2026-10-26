import re

RULES = [
    {
        "id": "SEC001",
        "title": "Hardcoded Secret / API Key",
        "pattern": r"(?i)(api[_-]?key|secret|password|auth_token|access_token)\s*=\s*['\"]([^'\"]+)['\"]",
        "severity": "CRITICAL",
    },
    {
        "id": "SEC002",
        "title": "Dangerous Dynamic Code Execution",
        "pattern": r"\b(eval|exec)\s*\(",
        "severity": "HIGH",
    },
    {
        "id": "SEC003",
        "title": "Command Injection Risk (shell=True)",
        "pattern": r"subprocess\.(Popen|call|run)\(.*shell\s*=\s*True",
        "severity": "HIGH",
    },
]


def parse_diff_lines(diff_text: str):
    """Parses diff text to extract added lines along with file paths and line numbers."""
    added_lines = []
    current_file = None
    target_line = 0

    for line in diff_text.splitlines():
        if line.startswith("+++ b/"):
            current_file = line[6:]
        elif line.startswith("@@"):
            # Extract line number from diff header like @@ -0,0 +1,5 @@
            match = re.search(r"\+(\d+)", line)
            if match:
                target_line = int(match.group(1)) - 1
        elif line.startswith("+") and not line.startswith("+++"):
            target_line += 1
            added_lines.append((current_file, target_line, line[1:]))
        elif not line.startswith("-"):
            target_line += 1

    return added_lines


def run_static_analysis(diff_text: str) -> list[dict]:
    """Scans added diff lines against SAST rules."""
    findings = []
    added_lines = parse_diff_lines(diff_text)

    for file_path, line_num, code_line in added_lines:
        for rule in RULES:
            if re.search(rule["pattern"], code_line):
                findings.append(
                    {
                        "rule_id": rule["id"],
                        "file_path": file_path or "unknown",
                        "line_number": line_num,
                        "title": rule["title"],
                        "severity": rule["severity"],
                        "snippet": code_line.strip(),
                    }
                )
    return findings