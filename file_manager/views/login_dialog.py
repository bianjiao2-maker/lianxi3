from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from database.db_manager import DatabaseManager
from models.user import User
from utils.helpers import validate_username, validate_password


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user = None
        self.db = DatabaseManager()
        self._init_ui()
    
    def _init_ui(self):
        self.setWindowTitle("用户登录")
        self.setFixedSize(400, 350)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        title_label = QLabel("文件管理器")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        title_label.setStyleSheet("color: #1976D2; margin: 10px;")
        layout.addWidget(title_label)
        
        subtitle_label = QLabel("请登录以继续")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(subtitle_label)
        
        login_group = QGroupBox("登录信息")
        form_layout = QFormLayout(login_group)
        form_layout.setSpacing(15)
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("请输入用户名")
        self.username_edit.setMinimumHeight(35)
        form_layout.addRow("用户名:", self.username_edit)
        
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("请输入密码")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setMinimumHeight(35)
        form_layout.addRow("密码:", self.password_edit)
        
        layout.addWidget(login_group)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.login_btn = QPushButton("登录")
        self.login_btn.setMinimumHeight(40)
        self.login_btn.clicked.connect(self._on_login)
        btn_layout.addWidget(self.login_btn)
        
        self.register_btn = QPushButton("注册")
        self.register_btn.setMinimumHeight(40)
        self.register_btn.clicked.connect(self._on_register)
        btn_layout.addWidget(self.register_btn)
        
        layout.addLayout(btn_layout)
        
        hint_label = QLabel("默认账号: admin / admin123")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet("color: #999; font-size: 11px;")
        layout.addWidget(hint_label)
        
        self.username_edit.returnPressed.connect(self._on_login)
        self.password_edit.returnPressed.connect(self._on_login)
        
        self._apply_styles()
    
    def _apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #333;
            }
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #2196F3;
                border-width: 2px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
            QPushButton:pressed {
                background-color: #1B5E20;
            }
        """)
    
    def _on_login(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        valid, msg = validate_username(username)
        if not valid:
            QMessageBox.warning(self, "输入错误", msg)
            self.username_edit.setFocus()
            return
        
        valid, msg = validate_password(password)
        if not valid:
            QMessageBox.warning(self, "输入错误", msg)
            self.password_edit.setFocus()
            return
        
        row = self.db.fetch_one(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        
        if row:
            self.user = User.from_db_row(row)
            self.db.update(
                'users',
                {'last_login': 'CURRENT_TIMESTAMP'},
                'id = ?',
                (self.user.id,)
            )
            QMessageBox.information(self, "登录成功", f"欢迎回来, {username}!")
            self.accept()
        else:
            QMessageBox.warning(self, "登录失败", "用户名或密码错误")
            self.password_edit.clear()
            self.password_edit.setFocus()
    
    def _on_register(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        valid, msg = validate_username(username)
        if not valid:
            QMessageBox.warning(self, "输入错误", msg)
            self.username_edit.setFocus()
            return
        
        valid, msg = validate_password(password)
        if not valid:
            QMessageBox.warning(self, "输入错误", msg)
            self.password_edit.setFocus()
            return
        
        existing = self.db.fetch_one(
            "SELECT id FROM users WHERE username = ?",
            (username,)
        )
        
        if existing:
            QMessageBox.warning(self, "注册失败", "用户名已存在")
            self.username_edit.setFocus()
            return
        
        try:
            self.db.insert('users', {
                'username': username,
                'password': password
            })
            QMessageBox.information(self, "注册成功", "账号注册成功，请登录!")
            self.password_edit.clear()
        except Exception as e:
            QMessageBox.warning(self, "注册失败", f"注册失败: {str(e)}")
    
    def get_user(self) -> User:
        return self.user
