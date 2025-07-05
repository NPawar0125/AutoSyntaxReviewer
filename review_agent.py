# review_agent.py
import os
import subprocess

def run_flake8():
    print("Running flake8...")
    result = subprocess.run(['flake8', '.'], capture_output=True, text=True)
    if result.returncode != 0:
        print("Syntax issues found:\n")
        print(result.stdout)
        with open('syntax_report.txt', 'w') as f:
            f.write(result.stdout)
        exit(1)  # Fail the check
    else:
        print("No syntax issues found.")

if __name__ == "__main__":
    run_flake8()
