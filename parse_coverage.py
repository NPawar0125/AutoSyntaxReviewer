import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_coverage_file(coverage_file):
    """Parse coverage file and extract coverage percentage"""
    try:
        logger.info(f"Parsing coverage file: {coverage_file}")
        
        with open(coverage_file, 'r') as f:
            lines = f.readlines()
        
        logger.info(f"Read {len(lines)} lines from coverage file")
        
        # Look for coverage percentage in different formats
        coverage_percent = "N/A"
        
        # Method 1: Look for TOTAL line (most common format)
        for line in reversed(lines):
            line = line.strip()
            if 'TOTAL' in line and '%' in line:
                logger.info(f"Found TOTAL line: {line}")
                # Extract percentage from line like "TOTAL  100  10  90%"
                parts = line.split()
                for part in parts:
                    if part.endswith('%'):
                        coverage_percent = part
                        break
                break
        
        # Method 2: Look for lines with percentage
        if coverage_percent == "N/A":
            for line in reversed(lines):
                line = line.strip()
                if '%' in line and any(char.isdigit() for char in line):
                    logger.info(f"Found percentage line: {line}")
                    # Extract percentage
                    import re
                    match = re.search(r'(\d+(?:\.\d+)?)%', line)
                    if match:
                        coverage_percent = match.group(1) + '%'
                        break
        
        # Method 3: Look for specific patterns
        if coverage_percent == "N/A":
            for line in lines:
                line = line.strip()
                if 'coverage:' in line.lower() or 'total coverage:' in line.lower():
                    logger.info(f"Found coverage line: {line}")
                    import re
                    match = re.search(r'(\d+(?:\.\d+)?)%', line)
                    if match:
                        coverage_percent = match.group(1) + '%'
                        break
        
        logger.info(f"Extracted coverage: {coverage_percent}")
        return coverage_percent
        
    except FileNotFoundError:
        logger.error(f"Coverage file not found: {coverage_file}")
        return "Coverage file not found"
    except Exception as e:
        logger.error(f"Error parsing coverage file: {e}")
        return f"Error parsing coverage: {str(e)}"

def main():
    if len(sys.argv) < 2:
        logger.error("Usage: python parse_coverage.py <coverage_file>")
        sys.exit(1)
    
    coverage_file = sys.argv[1]
    coverage_percent = parse_coverage_file(coverage_file)
    
    # Write coverage summary to a file
    with open('coverage_summary.txt', 'w') as f:
        f.write(f"Code Coverage: {coverage_percent}")
    
    logger.info(f"Coverage summary written to coverage_summary.txt: Code Coverage: {coverage_percent}")

if __name__ == "__main__":
    main() 