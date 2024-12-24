import regex as re
import json
INFO_REGEX_CURLY = r'\{(?:[^{}]|(?R))*\}'

def extract_json(text, which):
    # Find all matches in the text
    matches = re.findall(INFO_REGEX_CURLY, text, flags=re.DOTALL)
    counter = 0
    for match in matches:
        if counter == which:
            return match
        counter += 1

def escape_curly_braces(s):
    return s.replace("{", "{{").replace("}", "}}")

def de_escape_curly_braces(s):
    return s.replace("{{", "{").replace("}}", "}")