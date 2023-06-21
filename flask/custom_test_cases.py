import os
import json

ALLOWED_DOMAINS = [
    "leak.test",
    "adition.com",
    "sub.adition.com",
    "sub.sub.adition.com",
    "attack.er"
]

test_cases = {}

def load_custom_test_cases(config_folder_path: str):
    """
    Expected folder structure:
    - Project
    - Case
        - Domain
        - Subdir
    """
    folder_structure = get_folder_structure(config_folder_path)
    used_case_names = set()

    projects = [project for project in folder_structure if project["is_folder"]]
    for project in projects:
        cases = [case for case in project["subfolders"] if case["is_folder"]]
        for case in cases:
            if case["name"] in used_case_names:
                raise AttributeError(f"Case '{case['name']}' is not unique over project folders")
            used_case_names.add(case["name"])
            domains = [domain for domain in case["subfolders"] if domain["is_folder"]]
            for domain in domains:
                if domain['name'] not in ALLOWED_DOMAINS:
                    raise AttributeError(f"Domain '{domain['name']}' is not allowed ({project['name'], case['name']})")

                if domain["name"] not in test_cases:
                    test_cases[domain["name"]] = {}

                subdirs = [subdir for subdir in domain["subfolders"] if subdir["is_folder"]]
                for subdir in subdirs:
                    url_path = os.path.join(case["name"], subdir["name"])

                    test_cases[domain["name"]][url_path] = {}
                    test_cases[domain["name"]][url_path]["headers"] = get_headers(subdir["path"])

                    content, content_type_header = get_content(subdir["path"])
                    test_cases[domain["name"]][url_path]["content"] = content

                    if not headers_contain_header(test_cases[domain["name"]][url_path]["headers"], "Content-Type"):
                        test_cases[domain["name"]][url_path]["headers"].append(content_type_header)


def read_content_file(file_path) -> str:
    with open(file_path, 'r', encoding="utf-8") as file:
        return "".join(file.readlines())


def get_content(subdir_folder_path: str):
    potential_files = [
        {
            "file_name": "index.html",
            "content_type": "text/html"
        },
        {
            "file_name": "index.xml",
            "content_type": "text/xml"
        },
        {
            "file_name": "index.css",
            "content_type": "text/css"
        },
        {
            "file_name": "index.js",
            "content_type": "text/javascript"
        }
    ]
    content = None
    for file in potential_files:
        file_path = os.path.join(subdir_folder_path, file["file_name"])
        content_type = file["content_type"]
        if os.path.isfile(file_path):
            content = read_content_file(file_path)
            content_type_header = {"key": "Content-Type", "value": content_type}
            break
    if content is None:
        raise AttributeError(f"No valid file found in '{subdir_folder_path}'")
    return content, content_type_header


def get_headers(subdir_folder_path: str) -> list:
    file_path = os.path.join(subdir_folder_path, "headers.json")
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    else:
        return []


def headers_contain_header(headers: list, target_header: str) -> bool:
    for header in headers:
        if header["key"] == target_header:
            return True
    return False

def get_folder_structure(root_folder_path: str) -> list:
    folder_structure = []
    if not os.path.isdir(root_folder_path):
        raise AttributeError(f"Given root folder path does not point to a folder ({root_folder_path})")
    for subdir in os.listdir(root_folder_path):
        subdir_path = os.path.join(root_folder_path, subdir)
        is_folder = os.path.isdir(subdir_path)
        folder_structure.append({
            "name": subdir,
            "path": subdir_path,
            "is_folder": is_folder,
            "subfolders": get_folder_structure(subdir_path) if is_folder else None
        })
    return folder_structure


def get_all_subdirs(root_path: str) -> list:
    subdirs = list()
    for project_folder in os.listdir(root_path):
        project_folder_path = os.path.join(root_path, project_folder)
        if not os.path.isdir(project_folder_path):
            continue
        for case_folder in os.listdir(project_folder_path):
            case_folder_path = os.path.join(project_folder_path, case_folder)
            if os.path.isdir(case_folder_path):
                subdirs.append(case_folder_path)
    return subdirs


if __name__ == "__main__":
    load_custom_test_cases("custom_pages")
