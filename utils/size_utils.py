def format_size(size_bytes):
    if size_bytes == 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def get_folder_size(folder_path):
    total_size = 0
    try:
        for item in folder_path.rglob('*'):
            if item.is_file():
                try:
                    total_size += item.stat().st_size
                except (PermissionError, OSError):
                    pass
    except Exception:
        pass
    return total_size