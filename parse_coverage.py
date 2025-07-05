import sys

coverage_file = sys.argv[1]

with open(coverage_file, 'r') as f:
    lines = f.readlines()

# The last line typically contains the total coverage
for line in reversed(lines):
    if 'TOTAL' in line:
        total_line = line.strip()
        break
else:
    total_line = "Coverage data not found."

# Example line: TOTAL  100  10  90% 
try:
    coverage_percent = total_line.split()[-1]
except:
    coverage_percent = "N/A"

# Write coverage summary to a file
with open('coverage_summary.txt', 'w') as f:
    f.write(f"Code Coverage: {coverage_percent}") 