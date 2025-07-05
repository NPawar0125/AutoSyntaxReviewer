import subprocess

def get_new_files():
    """Fetch newly added Python files in the current PR or commit."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=A", "origin/main..."],
        capture_output=True, text=True
    )
    files = result.stdout.strip().split('\n')
    python_files = [f for f in files if f.endswith('.py')]
    return python_files

def run_flake8(files):
    if not files:
        print("No new Python files to review.")
        return

    print(f"Running flake8 on new files: {files}")
    result = subprocess.run(['flake8'] + files, capture_output=True, text=True)

    if result.returncode != 0:
        print("Syntax issues found!\n")
        print(result.stdout)
        with open('syntax_report.txt', 'w') as report_file:
            report_file.write(result.stdout)
        exit(1)
    else:
        print("No syntax issues found. All good!")

if __name__ == "__main__":
    new_files = get_new_files()
    run_flake8(new_files)
