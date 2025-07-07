import os
from pathlib import Path
from utils.size_utils import format_size, get_folder_size

class FileManager:
    def __init__(self):
        self.temp_data_dir = Path("temp_data")
        self.temp_data_dir.mkdir(exist_ok=True)
        self.config_path = self.temp_data_dir / "config.txt"
        self.folder_contents_path = self.temp_data_dir / "folder_contents.txt"
        self.files_to_delete_path = self.temp_data_dir / "files_to_delete.txt"
        self.folder_paths = []
        self.all_files = {}
        self.all_items = []

    def set_folder_paths(self, folder_paths):
        self.folder_paths = [Path(path) for path in folder_paths]
        self.save_config()

    def save_config(self):
        config_content = "\n".join(str(path) for path in self.folder_paths)
        self.config_path.write_text(config_content, encoding="utf-8")

    def load_config(self):
        if self.config_path.exists():
            lines = self.config_path.read_text(encoding="utf-8").splitlines()
            self.folder_paths = [Path(line.strip()) for line in lines if line.strip()]
            return True
        return False

    def gather_folder_contents(self):
        if not self.folder_paths:
            raise ValueError("No folder paths configured. Please select folders first.")

        results = []
        self.all_files = {}
        self.all_items = []

        for folder in self.folder_paths:
            if not folder.exists() or not folder.is_dir():
                results.append(f"[ERROR] Folder not found: {folder}")
                continue

            results.append(f"[Contents of folder: {folder}]")

            try:
                items = list(folder.iterdir())
            except PermissionError:
                results.append(f"[ERROR] Permission denied: {folder}")
                continue

            folders, files = [], []
            for item in items:
                try:
                    if item.is_dir():
                        folders.append(item)
                    elif item.is_file():
                        files.append(item)
                except (PermissionError, OSError):
                    continue

            folders.sort(key=lambda x: x.name.lower())
            files.sort(key=lambda x: x.name.lower())

            for item in folders:
                item_name = f"{item.name}[folder]"
                full_path = item.resolve()
                results.append(item_name)
                self.all_items.append(item_name)
                self.all_files.setdefault(item_name, []).append(full_path)

            for item in files:
                item_name = item.name
                full_path = item.resolve()
                results.append(item_name)
                self.all_items.append(item_name)
                self.all_files.setdefault(item_name, []).append(full_path)

            results.append("")

        self.folder_contents_path.write_text("\n".join(results), encoding="utf-8")
        print(f"Folder contents saved to: {self.folder_contents_path.resolve()}")
        return self.folder_contents_path

    def get_not_deletable_files(self, deletable_files):
        not_deletable = []
        if not self.folder_contents_path.exists():
            return not_deletable

        folder_contents = self.folder_contents_path.read_text(encoding="utf-8")
        all_items_from_file = [
            line.strip() for line in folder_contents.splitlines()
            if line.strip() and not line.startswith('[') and not line.startswith('ERROR')
        ]

        deletable_set = set(deletable_files)
        for item in all_items_from_file:
            if item not in deletable_set:
                not_deletable.append(item)

        return not_deletable

    def save_deletable_files_list(self, gpt_response):
        self.files_to_delete_path.write_text(gpt_response, encoding="utf-8")
        print(f"GPT response saved to: {self.files_to_delete_path.resolve()}")

    def delete_files(self, selected_files):
        import shutil
        deleted_count = 0
        errors = []
        for file_name in selected_files:
            if file_name in self.all_files:
                for file_path in self.all_files[file_name]:
                    try:
                        if file_path.exists():
                            if file_path.is_file():
                                os.remove(file_path)
                                deleted_count += 1
                                print(f"Deleted file: {file_path}")
                            elif file_path.is_dir():
                                try:
                                    file_path.rmdir()
                                    deleted_count += 1
                                    print(f"Deleted empty folder: {file_path}")
                                except OSError:
                                    shutil.rmtree(file_path)
                                    deleted_count += 1
                                    print(f"Deleted folder: {file_path}")
                        else:
                            errors.append(f"File/folder not found: {file_path}")
                    except Exception as e:
                        errors.append(f"Error deleting {file_path}: {str(e)}")
            else:
                errors.append(f"File/folder not found in index: {file_name}")

        return deleted_count, errors

    def get_file_info(self, file_name):
        if file_name not in self.all_files:
            return "File/folder not found"

        info = []
        total_size = 0

        for file_path in self.all_files[file_name]:
            if file_path.exists():
                if file_path.is_file():
                    try:
                        size = file_path.stat().st_size
                        total_size += size
                        info.append(f"FILE: {file_path} ({format_size(size)})")
                    except (PermissionError, OSError) as e:
                        info.append(f"FILE: {file_path} (Error accessing: {e})")
                elif file_path.is_dir():
                    folder_size = get_folder_size(file_path)
                    total_size += folder_size
                    info.append(f"FOLDER: {file_path} ({format_size(folder_size)})")
            else:
                info.append(f"NOT FOUND: {file_path}")

        return f"Total size: {format_size(total_size)}\n" + "\n".join(info)