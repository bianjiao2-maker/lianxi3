from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    id: Optional[int] = None
    username: str = ""
    password: str = ""
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    @classmethod
    def from_db_row(cls, row) -> 'User':
        return cls(
            id=row['id'],
            username=row['username'],
            password=row['password'],
            created_at=row['created_at'],
            last_login=row['last_login']
        )


@dataclass
class FileRecord:
    id: Optional[int] = None
    filename: str = ""
    filepath: str = ""
    file_size: int = 0
    created_at: Optional[datetime] = None
    user_id: Optional[int] = None
    
    @classmethod
    def from_db_row(cls, row) -> 'FileRecord':
        return cls(
            id=row['id'],
            filename=row['filename'],
            filepath=row['filepath'],
            file_size=row['file_size'],
            created_at=row['created_at'],
            user_id=row['user_id']
        )


@dataclass
class DataRecord:
    id: Optional[int] = None
    name: str = ""
    value: float = 0.0
    category: str = ""
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_db_row(cls, row) -> 'DataRecord':
        return cls(
            id=row['id'],
            name=row['name'],
            value=row['value'],
            category=row['category'],
            created_at=row['created_at']
        )
