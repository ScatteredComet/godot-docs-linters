import re
from pathlib import Path
from tqdm import tqdm

from z_linters.enum_linter import cached_simple_found_in_xml

# This regex looks for:
# 1. A word (return type)
# 2. Optional pointers/references (* or &)
# 3. The Function Name (Captured in Group 1)
# 4. Parentheses with anything inside
# 5. Optional 'const' or 'override' keywords
FUNC_PATTERN = re.compile(r'[\w:>]+[\s*&]+(\w+)\s*\([^)]*\)\s*(?:const|override|final)?\s*[;{]')

def get_function_names(filepath):
    names = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # findall returns all captured groups (the names)
            names = FUNC_PATTERN.findall(content)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    
    # Optional: Filter out common C++ keywords that might look like functions
    keywords = {'if', 'while', 'for', 'switch', 'return'}
    return [n for n in names if n not in keywords]

# Execution
search_path = Path("")
files = list(search_path.rglob("*.h"))

for p in tqdm(files, desc="Extracting Functions"):
    functions = get_function_names(p)
    if functions:
        print(f"\nFile: {p.name}")
        for name in functions:
            if not cached_simple_found_in_xml(name, False):
                print(f"  - {name}")