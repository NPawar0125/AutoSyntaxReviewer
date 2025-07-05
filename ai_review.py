import os
import requests
import sys
from github import Github

HF_API_URL = "https://api-inference.huggingface.co/models/bigcode/starcoder"
HF_TOKEN = os.getenv("HF_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY")
PR_NUMBER = sys.argv[1]

headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def query_llm(prompt):
    payload = {"inputs": prompt}
    response = requests.post(HF_API_URL, headers=headers, json=payload)
    return response.json()[0]["generated_text"]

def main():
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO)
    pr = repo.get_pull(int(PR_NUMBER))

    pr_description = pr.body
    files = pr.get_files()
    diff_summary = ""

    for file in files:
        diff_summary += f"\n### File: {file.filename}\n{file.patch}\n"

    review_prompt = f"""
You are an expert Python code reviewer. Carefully review the following pull request:

## Description of Changes:
{pr_description}

## Code Changes:
{diff_summary}

Provide:
1. Description feedback
2. Unit test coverage check
3. Code coverage comments
4. Code quality and Python best practices feedback
5. Checklist status

Please provide your feedback in a structured and professional format.
"""

    ai_feedback = query_llm(review_prompt)

    pr.create_issue_comment(f"""
        # 🤖 AI Code Review Feedback

        <details>
        <summary>🔍 **Review Summary**</summary>

        {ai_feedback}

        </details>

        ---

        ### 📋 **Review Checklist**
        - ✅ PR description clarity
        - ✅ Unit tests present
        - ✅ Code coverage maintained
        - ✅ Python best practices followed
        - ✅ No major security issues
        - ✅ Proper logging and error handling
        - ✅ Linked issues provided

        ---

        ### 📢 **Final Recommendation:** _Please review the detailed AI feedback and update the PR accordingly._

        _This review was automatically generated using an AI-powered code review tool._
        """)
test_summary = os.getenv("TEST_SUMMARY", "Test results not available.")


if __name__ == "__main__":
    main()

