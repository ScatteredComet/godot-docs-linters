"""
find enum ENUMNAME {

for each next line until } search *.xml for line without comma

if none found, print to terminal
"""

from itertools import chain
import re
import os
from pathlib import Path
from typing import AnyStr

from tqdm import tqdm

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
LIGHT_BLUE = "\033[94m"
RESET = "\033[0m"  # Very important: resets color to default

doc_path = Path("../")

xml_content = ""
for p in doc_path.rglob("*.xml"):
    with open(p, 'r', encoding='utf-8') as f:
        xml_content += f.read()

def cached_found_in_xml(pattern : re.Pattern[AnyStr]) -> bool:
    return bool(pattern.search(xml_content))

def cached_simple_found_in_xml(phrase : str, debug_mode : bool) -> bool:
    return phrase in xml_content

def found_in_xml(pattern : re.Pattern[AnyStr]) -> bool:
    for p in doc_path.rglob("*.xml"):
        with open(p) as file:
            for line in file:
                if pattern.search(line):
                    return True

    return False

# match for public enum="[enumname]"
enum_line = re.compile(r"enum\s+(\w+)\s*\{")

matches : int = 0

def simple_find_in_xml(phrase : str, debug_mode : bool) -> bool:
    for p in doc_path.rglob("*.xml"):
        if debug_mode:
            print(p)
        with open(p) as file:
            for line in file:
                if phrase in line:
                    return True

    return False

violation_number : int = 0

paths = [Path("../core/"), Path("../modules/"), Path("../scene/"), Path("../servers/")]
# paths = [Path("../servers/")]
to_chain = []

for path in paths:
    to_chain.append(list(path.rglob("*.cpp")))
    to_chain.append(list(path.rglob("*.h")))

for p in tqdm(chain(*to_chain), total=sum(len(x) for x in to_chain)):

    enum_started : bool = False
    enum_name_found : bool = False
    debug_mode = False
    enum_name : str = ""

    if "modules/gdscript" in str(p) or "extensions" in str(p):
        continue

    with open(p) as file:
        for line_number, line in enumerate(file):
            if enum_started:
                if "}" in line: # end of enum definition
                    enum_started = False
                    continue
                
                if enum_name_found: # only check if we know there is documentation for this enum
                    # strip last comma from line and leading whitespace; then try to find that string in a *.xml.
                    stripped = line.strip()
                    if stripped:
                        # remove leading whitespace and take the first word only (the enum value name) minus any special characters, and minus any lower case letters (this means we don't lint e.g. ifndef as being enum values etc)
                        enum_value_name = re.sub(r'[^A-Z0-9_]', '', stripped.split()[0])  

                        if not cached_found_in_xml(re.compile(rf"{enum_value_name}")):
                            type_val = f"Type: value        {enum_value_name}"
                            if "MAX" in enum_value_name:
                                tqdm.write(f"{violation_number:<10} {GREEN}Documentation missing for enum:{RESET} {enum_name:<50} {YELLOW}{type_val:<100}{RESET} {p}")
                            else:
                                tqdm.write(f"{violation_number:<10} {GREEN}Documentation missing for enum:{RESET} {enum_name:<50} {type_val:<100} {p}")
                            violation_number += 1
            
            match = enum_line.search(line)

            if match:
                enum_started = True
                enum_name = match.group(1)

                if not cached_simple_found_in_xml(rf'enum="{enum_name}"', debug_mode):
                    enum_name_found = False
                    type_all = "Type: all"
                    tqdm.write(f"{violation_number:<10} {LIGHT_BLUE}Documentation missing for enum:{RESET} {enum_name:<50} {type_all:<100} {p}")
                    violation_number += 1
                else:
                    enum_name_found = True

