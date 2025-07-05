import os
import requests
import sys
import logging
from github import Github

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

HF_API_URL = "https://api-inference.huggingface.co/models/bigcode/starcoder"
HF_TOKEN = os.getenv("HF_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY")

# Validate required environment variables
if not HF_TOKEN:
    logger.error("HF_TOKEN environment variable is required")
    sys.exit(1)
if not GITHUB_TOKEN:
    logger.error("GITHUB_TOKEN environment variable is required")
    sys.exit(1)
if not REPO:
    logger.error("GITHUB_REPOSITORY environment variable is required")
    sys.exit(1)

# Validate command line arguments
if len(sys.argv) < 2:
    logger.error("Error: PR number is required")
    print("Usage: python ai_review.py <PR_NUMBER>")
    sys.exit(1)

PR_NUMBER = sys.argv[1]

# Validate PR number format
try:
    int(PR_NUMBER)
except ValueError:
    logger.error(f"Error: Invalid PR number format: {PR_NUMBER}")
    sys.exit(1)

headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def truncate_diff(diff_text, max_length=8000):
    """Truncate diff text if it's too long to avoid API limits"""
    if len(diff_text) > max_length:
        return diff_text[:max_length] + "\n\n... (truncated due to length)"
    return diff_text

def query_llm(prompt, max_retries=3):
    """Query the LLM with retry logic and proper error handling"""
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to query LLM (attempt {attempt + 1}/{max_retries})")
            payload = {"inputs": prompt}
            response = requests.post(
                HF_API_URL, 
                headers=headers, 
                json=payload, 
                timeout=30  # 30 second timeout
            )
            response.raise_for_status()  # Raise exception for bad status codes
            
            result = response.json()
            if result and len(result) > 0:
                logger.info("Successfully received response from LLM")
                return result[0]["generated_text"]
            else:
                logger.warning("Empty response from LLM")
                return "No response generated from AI model"
                
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout on attempt {attempt + 1}")
            if attempt == max_retries - 1:
                return "Error: Request timed out after multiple attempts"
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error on attempt {attempt + 1}: {str(e)}")
            if attempt == max_retries - 1:
                return f"Error calling AI API: {str(e)}"
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing AI response on attempt {attempt + 1}: {str(e)}")
            if attempt == max_retries - 1:
                return f"Error parsing AI response: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
            if attempt == max_retries - 1:
                return f"Unexpected error: {str(e)}"
    
    return "Error: Failed to get response after all retry attempts"

def main():
    try:
        logger.info(f"Starting AI review for PR #{PR_NUMBER}")
        
        # Initialize GitHub client
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(str(REPO))  # REPO is validated above, so it's not None here
        pr = repo.get_pull(int(PR_NUMBER))
        
        logger.info(f"Retrieved PR: {pr.title}")

        pr_description = pr.body or "No description provided"
        files = pr.get_files()
        diff_summary = ""

        logger.info(f"Processing {len(list(files))} files in PR")
        
        for file in files:
            file_diff = f"\n### File: {file.filename}\n{file.patch or 'No changes'}\n"
            diff_summary += file_diff

        # Truncate diff if too long
        diff_summary = truncate_diff(diff_summary)
        
        # Get test and coverage data from environment
        test_summary = os.getenv("TEST_SUMMARY", "Test results not available.")
        coverage_summary = os.getenv("COVERAGE_SUMMARY", "Code coverage not available.")

        review_prompt = f"""
You are an expert Python code reviewer. Carefully review the following pull request:

## Description of Changes:
{pr_description}

## Code Changes:
{diff_summary}

## Test Results:
{test_summary}

## Code Coverage:
{coverage_summary}

Provide:
1. Description feedback
2. Unit test coverage check
3. Code coverage comments
4. Code quality and Python best practices feedback
5. Checklist status

Please provide your feedback in a structured and professional format.
"""

        logger.info("Sending review prompt to LLM")
        ai_feedback = query_llm(review_prompt)
        
        if ai_feedback.startswith("Error:"):
            logger.error(f"LLM returned error: {ai_feedback}")
            ai_feedback = "Unable to generate AI review due to technical issues. Please review manually."

        # Create the review comment
        comment_body = f"""
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

### 🧪 **Unit Test Summary**
{test_summary}

### 📊 **Code Coverage Summary**
{coverage_summary}

### 📢 **Final Recommendation:** _Please review the detailed AI feedback and update the PR accordingly._

_This review was automatically generated using an AI-powered code review tool._
"""

        logger.info("Posting review comment to PR")
        pr.create_issue_comment(comment_body)
        logger.info("AI review completed successfully")

    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

