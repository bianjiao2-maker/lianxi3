import os
from datetime import datetime


def format_file_size(size_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def get_file_info(filepath: str) -> dict:
    if not os.path.exists(filepath):
        return {}
    
    stat = os.stat(filepath)
    return {
        'filename': os.path.basename(filepath),
        'filepath': filepath,
        'file_size': stat.st_size,
        'created_at': datetime.fromtimestamp(stat.st_ctime),
        'modified_at': datetime.fromtimestamp(stat.st_mtime)
    }


def validate_username(username: str) -> tuple[bool, str]:
    if not username:
        return False, "用户名不能为空"
    if len(username) < 3:
        return False, "用户名至少3个字符"
    if len(username) > 20:
        return False, "用户名最多20个字符"
    if not username.isalnum():
        return False, "用户名只能包含字母和数字"
    return True, ""


def validate_password(password: str) -> tuple[bool, str]:
    if not password:
        return False, "密码不能为空"
    if len(password) < 6:
        return False, "密码至少6个字符"
    return True, ""
