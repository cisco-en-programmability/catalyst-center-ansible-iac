import os

def create_directory_structure(root_dir):
    """
    Creates the directory and file structure based on the provided example.

    Args:
        root_dir (str): The name of the root directory to create.
    """
    # Create the root directory
    os.makedirs(root_dir, exist_ok=True)
    # Create subdirectories
    subdirectories = ["images", "jinja_template", "playbook", "schema", "vars"]
    for subdir in subdirectories:
        os.makedirs(os.path.join(root_dir, subdir), exist_ok=True)
    # Create files
    files = {
        "images": [f"{root_dir}.png"],
        "playbook": [f"{root_dir}_playbook.yml", f"delete_{root_dir}_playbook.yml"],
        "schema": [f"{root_dir}_schema.yml"],
        "vars": [f"{root_dir}_inputs.yml", f"jinja_{root_dir}_inputs.yml"],
        ".": ["description.json", "README.md"]  # Files in the root directory
    }
    for subdir, file_list in files.items():
        for filename in file_list:
            filepath = os.path.join(root_dir, subdir, filename) if subdir != "." else os.path.join(root_dir, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            if not os.path.exists(filepath):
                # Create empty files if they do not exist
                with open(filepath, 'w') as f:
                    # Create empty files
                    pass
                print(f"Created file: {filepath}")

if __name__ == "__main__":
    while True:
        directory_name = input("Enter the directory name to create (e.g., lan_automation) or Enter to exit: ")
        if directory_name:
            create_directory_structure(directory_name)
            print(f"Directory structure for '{directory_name}' created successfully.")
        else:
            print("Directory name cannot be empty. Please try again.")
            break
# End of script