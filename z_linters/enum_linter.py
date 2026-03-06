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

doc_path = Path("")

xml_content = ""

g = list(doc_path.rglob("*.xml"))

for p in tqdm(g, desc="Caching all *.xml files...", total=len(g)):
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

visibility_keywords = re.compile(r'(?P<scope>\b(?:public|private|protected)\s*:)')

EMPTY_HEADER : str = f"{'///':<14} {LIGHT_BLUE}{'///':<60} {'///':<60} {'///':<60}{RESET} {'///':<10} {'///'}"

HEADER : str = f"{'violation no.':<14} {LIGHT_BLUE}{'enum name':<60} {'violation type':<60} {'constant name':<60}{RESET} {'scope':<10} {'filepath'}"

MINIMUM_NUMBER_OF_CAPITALS : int = 2

def main():
    
    violation_number : int = 0
    number_of_missing_constants : int = 0
    number_of_missing_types : int = 0
    
    # paths = [Path("core/"), Path("modules/"), Path("scene/"), Path("servers/")]
    paths = [Path("core/"), Path("modules/"), Path("scene/")]
    # paths = [Path("../servers/")]
    to_chain = []

    for path in paths:
        to_chain.append(list(path.rglob("*.cpp")))
        to_chain.append(list(path.rglob("*.h")))

    # make look fancy
    tqdm.write(EMPTY_HEADER)
    tqdm.write(HEADER)
    tqdm.write(EMPTY_HEADER)
    tqdm.write("")

    for p in tqdm(chain(*to_chain), total=sum(len(x) for x in to_chain)):

        enum_started : bool = False
        enum_name_found : bool = False
        debug_mode = False
        enum_name : str = ""
        current_scope : str = ""

        if "modules/gdscript" in str(p) or "extensions" in str(p) or "profiler" in str(p):
            continue

        with open(p) as file:
            for line_number, line in enumerate(file):
                if enum_started:
                    if "}" in line: # end of enum definition
                        enum_started = False
                        continue
                    
                    uppercase_count = sum(1 for char in enum_name if char.isupper())

                    if enum_name_found and uppercase_count >= MINIMUM_NUMBER_OF_CAPITALS: # only check if we know there is documentation for this enum, and the enum name is interesting
                        # strip last comma from line and leading whitespace; then try to find that string in a *.xml.
                        stripped = line.strip()
                        if stripped:
                            # remove leading whitespace and take the first word only (the enum value name) minus any special characters, and minus any lower case letters (this means we don't lint e.g. ifndef as being enum values etc)
                            enum_value_name = re.sub(r'[^A-Z0-9_]', '', stripped.split()[0])  

                            if not cached_found_in_xml(re.compile(rf"{enum_value_name}")):
                                type = f"Enumeration constant"
                                if "MAX" in enum_value_name or "NUM_BITS" in enum_value_name:
                                    # type = f"Delimiter"
                                    # tqdm.write(f"{violation_number:<14} {YELLOW}{enum_name:<60} {type:<60} {enum_value_name:<60}{RESET} {current_scope:<10} {p}")
                                    pass
                                elif current_scope == "public":
                                    tqdm.write(f"{'':<7} {number_of_missing_constants:<7} {GREEN}{enum_name:<60} {type:<60} {enum_value_name:<60}{RESET} {current_scope:<10} {p}")
                                    violation_number += 1
                                    number_of_missing_constants += 1
                
                match = enum_line.search(line)
                scope = visibility_keywords.search(line)

                if scope:
                    current_scope = scope.group('scope').strip(':').strip()

                if match:
                    enum_started = True
                    enum_name = match.group(1)

                    if not cached_simple_found_in_xml(rf'enum="{enum_name}"', debug_mode):
                        enum_name_found = False
                        type_all = "Enumeration type"

                        uppercase_count = sum(1 for char in enum_name if char.isupper())
                        if (uppercase_count >= MINIMUM_NUMBER_OF_CAPITALS) and current_scope == "public":
                            tqdm.write(f"{number_of_missing_types:<7} {'':<7} {LIGHT_BLUE}{enum_name:<60} {type_all:<60} {'':<60}{RESET} {current_scope:<10} {p}")
                            violation_number += 1
                            number_of_missing_types += 1
                    else:
                        enum_name_found = True

if __name__ == "__main__":
    main()

