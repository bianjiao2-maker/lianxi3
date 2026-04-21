import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'file_manager.db')

STYLES_PATH = os.path.join(BASE_DIR, 'resources', 'styles.qss')

WINDOW_TITLE = "文件管理器"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

SUPPORTED_FILE_TYPES = {
    '文本文件': '*.txt',
    'Excel文件': '*.xlsx *.xls',
    'CSV文件': '*.csv',
    '所有文件': '*.*'
}
