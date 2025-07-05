import sys
import xml.etree.ElementTree as ET

xml_file = sys.argv[1]

tree = ET.parse(xml_file)
root = tree.getroot()

total = int(root.attrib['tests'])
failures = int(root.attrib.get('failures', 0))
errors = int(root.attrib.get('errors', 0))
skipped = int(root.attrib.get('skipped', 0))
passed = total - failures - errors - skipped

summary = f"Total: {total}, Passed: {passed}, Failures: {failures}, Errors: {errors}, Skipped: {skipped}"

# Write summary to a text file to be read later
with open('test_summary.txt', 'w') as f:
    f.write(summary) 