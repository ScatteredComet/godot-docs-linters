"""
from here https://www.py4u.org/blog/python-script-to-tqdm.write-all-function-definitions-of-a-c-c-file/#step-5-implementing-the-full-script
"""

from pathlib import Path
import re
import sys

from tqdm import tqdm

from z_linters.enum_linter import cached_simple_found_in_xml
 
def remove_comments(text):
    """Remove line and block comments from C/C++ code."""
    # Remove block comments /* ... */ (non-greedy)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    # Remove line comments // ...
    text = re.sub(r'//.*$', '', text, flags=re.MULTILINE)
    return text

import re

def extract_functions_with_scope(file_content):
    cleaned_content = remove_comments(file_content)
    
    # 1. Combined Regex: Matches visibility keywords OR function patterns
    # We use named groups (?P<name>...) to easily distinguish what we hit
    combined_pattern = re.compile(
        r'(?P<scope>\b(?:public|private|protected)\s*:) |' # Visibility keywords
        r'(?:template\s*<[^>]+>\s*)?' 
        r'(?P<ret>[\w:<>]+\s+[\w:*&]+|[\w:*&]+)\s+' 
        r'(?P<func>[\w:]+)\s*' 
        r'\((?P<args>[^)]*)\)'
        r'(?:\s+const|volatile)?'
    , re.VERBOSE)

    current_scope = "private" # Default C++ class scope is private
    results = []

    for match in combined_pattern.finditer(cleaned_content):
        # If we hit a scope keyword, update our "state"
        if match.group('scope'):
            current_scope = match.group('scope').strip(':').strip()
            continue
        
        # If we hit a function pattern
        func_name = match.group('func')
        if func_name and '*' not in func_name and '=' not in func_name:
            results.append({
                "name": func_name,
                "scope": current_scope
            })
            
    return results

def extract_functions(file_content):
    """Extract function names from cleaned C/C++ code using regex."""
    # Preprocess: remove comments
    cleaned_content = remove_comments(file_content)
    
    # Regex pattern to match C/C++ functions (adjusted for readability)
    FUNCTION_PATTERN = re.compile(
        r'(?:template\s*<[^>]+>\s*)?'  # Optional template header (e.g., template<typename T>)
        r'([\w:<>]+\s+[\w:*&]+|[\w:*&]+)\s+'  # Return type (supports templates, pointers, references)
        r'([\w:]+)\s*'  # Function name (supports Class::func or Namespace::func)
        r'\([^)]*\)'  # Parameters (any characters except ')' inside parentheses)
        r'(?:\s+const|volatile)?'  # Optional const/volatile qualifier
    )
    
    # Find all matches and extract function names
    matches = FUNCTION_PATTERN.findall(cleaned_content)
    function_names = [match[1] for match in matches]  # match[1] is the function name group
    
    # Filter out false positives (e.g., function pointers, variables)
    filtered_names = [name for name in function_names if '*' not in name and '=' not in name]
    return filtered_names
 
def read_file(file_path):
    """Read the content of a file."""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        tqdm.write(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        tqdm.write(f"Error reading file: {e}")
        sys.exit(1)
 
def main(file_path : str):
    if len(sys.argv) != 2:
        tqdm.write("Usage: python extract_functions.py <path_to_cpp_file>")
        sys.exit(1)
    
    file_content = read_file(file_path)
    functions = extract_functions_with_scope(file_content)
    hit = False
    # tqdm.write(f"Found {len(functions)} functions:")
    for i, funcname in enumerate(functions, 1):
        if not funcname["name"].startswith("_") and funcname["scope"] == "public" and not cached_simple_found_in_xml(funcname["name"], False):
            if not hit:
                tqdm.write("---")
                tqdm.write(str(file_path))

            hit = True
            tqdm.write(f"   {i}. {funcname['name']}")
 
search_path = Path("scene/")
files = list(search_path.rglob("*.h"))

if __name__ == "__main__":
    file_path = sys.argv[1]

    for p in tqdm(files, desc="Extracting Functions"):
        main(p)