import re
import json

# Example text containing JSON
text = """
Here is some text before the JSON:
{
    "name": "John",
    "age": 30,
    "isEmployed": true,
    "skills": ["Python", "JavaScript"],
    "address": {
        "street": "123 Main St",
        "city": "Anytown"
    }
}
And some text after the JSON.
"""

# Regex to find JSON objects (limited to one level of nesting)
INFO_REGEX_CURLY = r'\{[^{}]*\}(?:,\s*\{[^{}]*\})*'

# Find all matches in the text
matches = re.findall(INFO_REGEX_CURLY, text, flags=re.DOTALL)

# Output the matches
for match in matches:
    print("Extracted JSON:", match)
    try:
        # Attempt to parse the extracted JSON
        json_data = json.loads(match)
        print("Parsed JSON:", json_data)
    except json.JSONDecodeError as e:
        print("Error parsing JSON:", e)
