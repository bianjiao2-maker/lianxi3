#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录对话框 - 用户认证模块
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox,
    QGroupBox, QFormLayout
)
from PyQt5.QtCore import Qt
import hashlib


class LoginDialog(QDialog):
    """登录对话框"""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user = None
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("用户登录")
        self.setFixedSize(350, 250)
        self.setWindowModality(Qt.ApplicationModal)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title_label = QLabel("🎓 学生文件管理器")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2196F3;
            padding: 10px;
        """)
        layout.addWidget(title_label)
        
        form_group = QGroupBox()
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(10)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setMinimumHeight(35)
        form_layout.addRow("👤 用户名:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(35)
        form_layout.addRow("🔒 密  码:", self.password_input)
        
        layout.addWidget(form_group)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.login_btn = QPushButton("登录")
        self.login_btn.clicked.connect(self.handle_login)
        self.login_btn.setMinimumHeight(35)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        btn_layout.addWidget(self.login_btn)
        
        self.register_btn = QPushButton("注册")
        self.register_btn.clicked.connect(self.handle_register)
        self.register_btn.setMinimumHeight(35)
        btn_layout.addWidget(self.register_btn)
        
        self.guest_btn = QPushButton("访客模式")
        self.guest_btn.clicked.connect(self.handle_guest)
        self.guest_btn.setMinimumHeight(35)
        btn_layout.addWidget(self.guest_btn)
        
        layout.addLayout(btn_layout)
        
        self.username_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
    
    def hash_password(self, password):
        """密码哈希"""
        return hashlib.md5(password.encode()).hexdigest()
    
    def handle_login(self):
        """处理登录"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "警告", "请输入用户名和密码!")
            return
        
        user = self.db_manager.verify_user(username, self.hash_password(password))
        
        if user:
            self.user = user
            QMessageBox.information(self, "成功", f"欢迎回来, {username}!")
            self.accept()
        else:
            QMessageBox.warning(self, "错误", "用户名或密码错误!")
    
    def handle_register(self):
        """处理注册"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "警告", "请输入用户名和密码!")
            return
        
        if len(username) < 3:
            QMessageBox.warning(self, "警告", "用户名至少3个字符!")
            return
        
        if len(password) < 4:
            QMessageBox.warning(self, "警告", "密码至少4个字符!")
            return
        
        if self.db_manager.create_user(username, self.hash_password(password)):
            QMessageBox.information(self, "成功", "注册成功! 请登录.")
        else:
            QMessageBox.warning(self, "错误", "用户名已存在!")
    
    def handle_guest(self):
        """访客模式"""
        self.user = {"id": 0, "username": "访客"}
        QMessageBox.information(self, "提示", "已进入访客模式")
        self.accept()
    
    def get_user(self):
        """获取登录用户"""
        return self.user
