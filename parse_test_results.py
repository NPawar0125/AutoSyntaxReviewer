import sys
import xml.etree.ElementTree as ET
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_junit_xml(xml_file):
    """Parse JUnit XML file and extract test statistics"""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        logger.info(f"Parsing XML file: {xml_file}")
        logger.info(f"Root element: {root.tag}")
        logger.info(f"Root attributes: {root.attrib}")
        
        # Try different ways to get test statistics
        total = 0
        failures = 0
        errors = 0
        skipped = 0
        
        # Method 1: Check if attributes are on root element
        if 'tests' in root.attrib:
            total = int(root.attrib['tests'])
            failures = int(root.attrib.get('failures', 0))
            errors = int(root.attrib.get('errors', 0))
            skipped = int(root.attrib.get('skipped', 0))
            logger.info("Found test statistics in root attributes")
        else:
            # Method 2: Count test elements
            logger.info("Counting test elements manually")
            testsuites = root.findall('.//testsuite')
            if not testsuites:
                testsuites = [root]  # If no testsuite elements, use root
            
            for testsuite in testsuites:
                total += int(testsuite.attrib.get('tests', 0))
                failures += int(testsuite.attrib.get('failures', 0))
                errors += int(testsuite.attrib.get('errors', 0))
                skipped += int(testsuite.attrib.get('skipped', 0))
            
            # If still no tests found, try counting testcase elements
            if total == 0:
                testcases = root.findall('.//testcase')
                total = len(testcases)
                logger.info(f"Counted {total} testcase elements")
                
                # Count failures and errors
                for testcase in testcases:
                    if testcase.find('failure') is not None:
                        failures += 1
                    if testcase.find('error') is not None:
                        errors += 1
                    if testcase.find('skipped') is not None:
                        skipped += 1
        
        passed = total - failures - errors - skipped
        
        logger.info(f"Parsed results: Total={total}, Passed={passed}, Failures={failures}, Errors={errors}, Skipped={skipped}")
        
        return {
            'total': total,
            'passed': passed,
            'failures': failures,
            'errors': errors,
            'skipped': skipped
        }
        
    except FileNotFoundError:
        logger.error(f"XML file not found: {xml_file}")
        return {'total': 0, 'passed': 0, 'failures': 0, 'errors': 0, 'skipped': 0}
    except ET.ParseError as e:
        logger.error(f"Error parsing XML file: {e}")
        return {'total': 0, 'passed': 0, 'failures': 0, 'errors': 0, 'skipped': 0}
    except Exception as e:
        logger.error(f"Unexpected error parsing XML: {e}")
        return {'total': 0, 'passed': 0, 'failures': 0, 'errors': 0, 'skipped': 0}

def main():
    if len(sys.argv) < 2:
        logger.error("Usage: python parse_test_results.py <xml_file>")
        sys.exit(1)
    
    xml_file = sys.argv[1]
    results = parse_junit_xml(xml_file)
    
    summary = f"Total: {results['total']}, Passed: {results['passed']}, Failures: {results['failures']}, Errors: {results['errors']}, Skipped: {results['skipped']}"
    
    # Write summary to a text file to be read later
    with open('test_summary.txt', 'w') as f:
        f.write(summary)
    
    logger.info(f"Test summary written to test_summary.txt: {summary}")

if __name__ == "__main__":
    main() 