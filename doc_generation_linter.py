from pathlib import Path

import requests

generated_class_file_names = []

def get_all_github_rst_files(owner, repo, branch="master"):
    # Using the Recursive Trees API to bypass the 1,000 item limit
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    
    # Use headers={'Authorization': 'token YOUR_TOKEN'} here if you hit rate limits
    response = requests.get(url)
    
    if response.status_code == 200:
        tree = response.json().get("tree", [])
        
        # Filter for files in the 'classes/' directory that end in '.rst'
        for item in tree:
            path_str = item['path']
            if path_str.startswith("classes/") and path_str.endswith(".rst"):
                # Get just the filename (e.g., 'class_node.rst')
                filename = path_str.split('/')[-1]
                # Clean it: remove 'class_' and '.rst', then lowercase
                clean_name = filename.replace("class_", "").replace(".rst", "").lower()
                generated_class_file_names.append(clean_name)
        
        print(f"Found {len(generated_class_file_names)} .rst files on GitHub.")
            
    elif response.status_code == 403:
        print("Error: API rate limit exceeded. You likely need a GitHub Token for this many files.")
    else:
        print(f"Failed to fetch data: {response.status_code}")

def print_rst_files(owner, repo, path, branch="master"):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
    
    # It's highly recommended to use a token for this specific repo 
    # as it has hundreds of files, which can trigger rate limits.
    response = requests.get(url)
    
    if response.status_code == 200:
        contents = response.json()
        
        # Filter for files ending in .rst
        rst_files = [item['name'] for item in contents 
                     if item['type'] == 'file' and item['name'].endswith('.rst')]
        
        if rst_files:
            print(f"Found {len(rst_files)} .rst files in '{path}':\n")
            for filename in rst_files:
                clean_name = filename.replace("class_", "").replace(".rst", "")
                generated_class_file_names.append(clean_name)
        else:
            print(f"No .rst files found in '{path}'.")
            
    elif response.status_code == 403:
        print("Error: API rate limit exceeded. Try using an API token.")
    else:
        print(f"Failed to fetch data: {response.status_code}")

xml_file_names = []

def get_xml_files():
    # for p in [*Path("doc/").rglob("*.xml"), *Path("modules/").rglob("*.xml"), *Path("platform/").rglob("*.xml")]:
    for p in [*Path("").rglob("*.xml")]:
        if "doc" not in str(p):
            continue
        filename = Path(p).stem.lower()
        # clean_name = str(p).replace("doc/classes/", "").replace(".xml", "").lower()
        xml_file_names.append(filename)

# Run for the Godot classes directory
get_xml_files()
get_all_github_rst_files("godotengine", "godot-docs", "master")

unique_items = set(generated_class_file_names) ^ set(xml_file_names)

for i in xml_file_names:
    if i not in generated_class_file_names:
        print(f"{i:<50} not in generated files, but is in xml")

for i in generated_class_file_names:
    if i not in xml_file_names:
        print(f"{i:<50} not in xml files, but is generated")

print(len(unique_items))