import os
import sys
from PyInstaller import __main__ as pyi

def build():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    main_script = os.path.join(base_dir, 'main.py')
    
    args = [
        '--name=FileManager',
        '--windowed',
        '--onefile',
        '--clean',
        '--noconfirm',
        f'--add-data={os.path.join(base_dir, "resources")};resources',
        f'--add-data={os.path.join(base_dir, "config.py")};.',
        f'--hidden-import=PyQt5',
        f'--hidden-import=matplotlib',
        f'--hidden-import=pandas',
        f'--hidden-import=openpyxl',
        f'--icon=resources/icon.ico' if os.path.exists(os.path.join(base_dir, 'resources', 'icon.ico')) else '',
        main_script
    ]
    
    args = [arg for arg in args if arg]
    
    pyi.run(args)
    
    print("\n构建完成！可执行文件位于: dist/FileManager.exe")

if __name__ == '__main__':
    build()
