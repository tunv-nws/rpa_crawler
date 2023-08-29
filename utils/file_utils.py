import os


def check_directory_exist(dir_path: str) -> None:
    """Create directory if not exist."""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
