import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QAction, QToolBar, QStatusBar,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QMessageBox, QLabel, QSplitter,
    QTreeWidget, QTreeWidgetItem, QTabWidget,
    QGroupBox, QPushButton, QLineEdit, QComboBox,
    QProgressBar, QApplication
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QFont
from datetime import datetime

from database.db_manager import DatabaseManager
from views.login_dialog import LoginDialog
from views.chart_dialog import ChartDialog
from utils.helpers import format_file_size, get_file_info
import config


class FileManagerMainWindow(QMainWindow):
    login_success = pyqtSignal(str)
    logout_success = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.db = DatabaseManager()
        self.current_file_path = None
        self._init_ui()
        self._apply_styles()
        self._show_login_dialog()
    
    def _init_ui(self):
        self.setWindowTitle(config.WINDOW_TITLE)
        self.setGeometry(100, 100, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        
        self._create_menu_bar()
        self._create_tool_bar()
        self._create_status_bar()
        self._create_central_widget()
    
    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("font-size: 13px;")
        
        file_menu = menu_bar.addMenu("文件(&F)")
        
        open_action = QAction("打开文件(&O)", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._on_open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("保存文件(&S)", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._on_save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("另存为(&A)", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self._on_save_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        edit_menu = menu_bar.addMenu("编辑(&E)")
        
        add_record_action = QAction("添加记录(&A)", self)
        add_record_action.setShortcut("Ctrl+N")
        add_record_action.triggered.connect(self._on_add_record)
        edit_menu.addAction(add_record_action)
        
        delete_record_action = QAction("删除记录(&D)", self)
        delete_record_action.setShortcut("Delete")
        delete_record_action.triggered.connect(self._on_delete_record)
        edit_menu.addAction(delete_record_action)
        
        edit_menu.addSeparator()
        
        refresh_action = QAction("刷新(&R)", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._on_refresh_data)
        edit_menu.addAction(refresh_action)
        
        view_menu = menu_bar.addMenu("视图(&V)")
        
        chart_action = QAction("显示图表(&C)", self)
        chart_action.setShortcut("Ctrl+G")
        chart_action.triggered.connect(self._on_show_chart)
        view_menu.addAction(chart_action)
        
        view_menu.addSeparator()
        
        toggle_toolbar_action = QAction("显示工具栏", self)
        toggle_toolbar_action.setCheckable(True)
        toggle_toolbar_action.setChecked(True)
        toggle_toolbar_action.triggered.connect(self._toggle_toolbar)
        view_menu.addAction(toggle_toolbar_action)
        
        toggle_statusbar_action = QAction("显示状态栏", self)
        toggle_statusbar_action.setCheckable(True)
        toggle_statusbar_action.setChecked(True)
        toggle_statusbar_action.triggered.connect(self._toggle_statusbar)
        view_menu.addAction(toggle_statusbar_action)
        
        user_menu = menu_bar.addMenu("用户(&U)")
        
        self.login_action = QAction("登录(&L)", self)
        self.login_action.setShortcut("Ctrl+L")
        self.login_action.triggered.connect(self._show_login_dialog)
        user_menu.addAction(self.login_action)
        
        self.logout_action = QAction("注销(&O)", self)
        self.logout_action.setShortcut("Ctrl+W")
        self.logout_action.triggered.connect(self._on_logout)
        self.logout_action.setEnabled(False)
        user_menu.addAction(self.logout_action)
        
        user_menu.addSeparator()
        
        self.user_info_action = QAction("用户信息", self)
        self.user_info_action.triggered.connect(self._show_user_info)
        self.user_info_action.setEnabled(False)
        user_menu.addAction(self.user_info_action)
        
        help_menu = menu_bar.addMenu("帮助(&H)")
        
        about_action = QAction("关于(&A)", self)
        about_action.setShortcut("F1")
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
    
    def _create_tool_bar(self):
        self.toolbar = QToolBar("主工具栏")
        self.toolbar.setMovable(False)
        self.toolbar.setStyleSheet("spacing: 5px; padding: 5px;")
        self.addToolBar(self.toolbar)
        
        open_btn = QPushButton("打开文件")
        open_btn.clicked.connect(self._on_open_file)
        self.toolbar.addWidget(open_btn)
        
        save_btn = QPushButton("保存文件")
        save_btn.clicked.connect(self._on_save_file)
        self.toolbar.addWidget(save_btn)
        
        self.toolbar.addSeparator()
        
        chart_btn = QPushButton("显示图表")
        chart_btn.clicked.connect(self._on_show_chart)
        self.toolbar.addWidget(chart_btn)
        
        self.toolbar.addSeparator()
        
        refresh_btn = QPushButton("刷新数据")
        refresh_btn.clicked.connect(self._on_refresh_data)
        self.toolbar.addWidget(refresh_btn)
        
        self.toolbar.addSeparator()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索...")
        self.search_input.setMaximumWidth(200)
        self.search_input.textChanged.connect(self._on_search)
        self.toolbar.addWidget(self.search_input)
    
    def _create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label, 1)
        
        self.user_status_label = QLabel("未登录")
        self.status_bar.addPermanentWidget(self.user_status_label)
        
        self.time_label = QLabel()
        self.status_bar.addPermanentWidget(self.time_label)
        
        self._update_time()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_time)
        self.timer.start(1000)
    
    def _create_central_widget(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        splitter = QSplitter(Qt.Horizontal)
        
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([300, 900])
        
        main_layout.addWidget(splitter)
    
    def _create_left_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        file_tree = QTreeWidget()
        file_tree.setHeaderLabel("文件浏览器")
        file_tree.itemDoubleClicked.connect(self._on_file_double_clicked)
        
        root_item = QTreeWidgetItem(file_tree, ["我的文件"])
        root_item.setExpanded(True)
        
        documents_item = QTreeWidgetItem(root_item, ["文档"])
        QTreeWidgetItem(documents_item, ["示例文档.txt"])
        
        data_item = QTreeWidgetItem(root_item, ["数据"])
        QTreeWidgetItem(data_item, ["示例数据.csv"])
        
        layout.addWidget(file_tree)
        
        return panel
    
    def _create_right_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        tab_widget = QTabWidget()
        
        data_tab = self._create_data_tab()
        tab_widget.addTab(data_tab, "数据表格")
        
        file_info_tab = self._create_file_info_tab()
        tab_widget.addTab(file_info_tab, "文件信息")
        
        layout.addWidget(tab_widget)
        
        return panel
    
    def _create_data_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        toolbar_layout = QHBoxLayout()
        
        add_btn = QPushButton("添加记录")
        add_btn.clicked.connect(self._on_add_record)
        toolbar_layout.addWidget(add_btn)
        
        delete_btn = QPushButton("删除记录")
        delete_btn.clicked.connect(self._on_delete_record)
        toolbar_layout.addWidget(delete_btn)
        
        toolbar_layout.addStretch()
        
        layout.addLayout(toolbar_layout)
        
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(5)
        self.data_table.setHorizontalHeaderLabels(["ID", "名称", "数值", "类别", "创建时间"])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.data_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.data_table)
        
        self._load_data_to_table()
        
        return tab
    
    def _create_file_info_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        info_group = QGroupBox("当前文件信息")
        info_layout = QVBoxLayout(info_group)
        
        self.file_name_label = QLabel("文件名: 未选择")
        info_layout.addWidget(self.file_name_label)
        
        self.file_path_label = QLabel("路径: -")
        info_layout.addWidget(self.file_path_label)
        
        self.file_size_label = QLabel("大小: -")
        info_layout.addWidget(self.file_size_label)
        
        self.file_modified_label = QLabel("修改时间: -")
        info_layout.addWidget(self.file_modified_label)
        
        layout.addWidget(info_group)
        
        layout.addStretch()
        
        return tab
    
    def _apply_styles(self):
        try:
            with open(config.STYLES_PATH, 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            default_style = """
                QMainWindow {
                    background-color: #f5f5f5;
                }
                QMenuBar {
                    background-color: #ffffff;
                    border-bottom: 1px solid #e0e0e0;
                    padding: 5px;
                }
                QMenuBar::item {
                    padding: 5px 10px;
                    border-radius: 3px;
                }
                QMenuBar::item:selected {
                    background-color: #e3f2fd;
                }
                QToolBar {
                    background-color: #ffffff;
                    border-bottom: 1px solid #e0e0e0;
                    padding: 5px;
                    spacing: 5px;
                }
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
                QTableWidget {
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    gridline-color: #f0f0f0;
                }
                QTableWidget::item {
                    padding: 5px;
                }
                QTableWidget::item:selected {
                    background-color: #e3f2fd;
                    color: #333;
                }
                QHeaderView::section {
                    background-color: #fafafa;
                    padding: 8px;
                    border: none;
                    border-bottom: 2px solid #e0e0e0;
                    font-weight: bold;
                }
                QStatusBar {
                    background-color: #ffffff;
                    border-top: 1px solid #e0e0e0;
                }
                QTreeWidget {
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                }
                QLineEdit {
                    padding: 8px;
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    background-color: white;
                }
                QLineEdit:focus {
                    border-color: #2196F3;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
                QTabWidget::pane {
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    background-color: white;
                }
                QTabBar::tab {
                    background-color: #f5f5f5;
                    padding: 8px 16px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected {
                    background-color: white;
                    border-bottom: 2px solid #2196F3;
                }
            """
            self.setStyleSheet(default_style)
    
    def _update_time(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(current_time)
    
    def _show_login_dialog(self):
        dialog = LoginDialog(self)
        if dialog.exec_():
            self.current_user = dialog.get_user()
            self._on_login_success()
    
    def _on_login_success(self):
        if self.current_user:
            self.user_status_label.setText(f"用户: {self.current_user.username}")
            self.status_label.setText(f"欢迎, {self.current_user.username}!")
            self.login_action.setEnabled(False)
            self.logout_action.setEnabled(True)
            self.user_info_action.setEnabled(True)
            self.login_success.emit(self.current_user.username)
    
    def _on_logout(self):
        self.current_user = None
        self.user_status_label.setText("未登录")
        self.status_label.setText("已注销")
        self.login_action.setEnabled(True)
        self.logout_action.setEnabled(False)
        self.user_info_action.setEnabled(False)
        self.logout_success.emit()
    
    def _show_user_info(self):
        if self.current_user:
            QMessageBox.information(
                self, "用户信息",
                f"用户名: {self.current_user.username}\n"
                f"创建时间: {self.current_user.created_at or '未知'}\n"
                f"最后登录: {self.current_user.last_login or '从未登录'}"
            )
    
    def _on_open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开文件", "",
            "文本文件;;Excel文件;;CSV文件;;所有文件"
        )
        
        if file_path:
            self.current_file_path = file_path
            self._load_file(file_path)
            self.status_label.setText(f"已打开: {os.path.basename(file_path)}")
    
    def _load_file(self, file_path: str):
        file_info = get_file_info(file_path)
        
        self.file_name_label.setText(f"文件名: {file_info.get('filename', '-')}")
        self.file_path_label.setText(f"路径: {file_info.get('filepath', '-')}")
        self.file_size_label.setText(f"大小: {format_file_size(file_info.get('file_size', 0))}")
        self.file_modified_label.setText(f"修改时间: {file_info.get('modified_at', '-')}")
        
        if file_path.endswith('.csv'):
            self._load_csv_file(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            self._load_excel_file(file_path)
        else:
            self._load_text_file(file_path)
    
    def _load_csv_file(self, file_path: str):
        try:
            import pandas as pd
            df = pd.read_csv(file_path, encoding='utf-8')
            self._display_dataframe(df)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法读取CSV文件: {str(e)}")
    
    def _load_excel_file(self, file_path: str):
        try:
            import pandas as pd
            df = pd.read_excel(file_path)
            self._display_dataframe(df)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法读取Excel文件: {str(e)}")
    
    def _load_text_file(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            QMessageBox.information(self, "文件内容", content[:1000] + ("..." if len(content) > 1000 else ""))
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法读取文件: {str(e)}")
    
    def _display_dataframe(self, df):
        self.data_table.setRowCount(df.shape[0])
        self.data_table.setColumnCount(df.shape[1])
        self.data_table.setHorizontalHeaderLabels(df.columns.astype(str).tolist())
        
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                item = QTableWidgetItem(str(df.iloc[i, j]))
                self.data_table.setItem(i, j, item)
    
    def _on_save_file(self):
        if self.current_file_path:
            self._save_to_file(self.current_file_path)
        else:
            self._on_save_as()
    
    def _on_save_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存文件", "",
            "CSV文件;;Excel文件;;文本文件"
        )
        if file_path:
            self._save_to_file(file_path)
            self.current_file_path = file_path
    
    def _save_to_file(self, file_path: str):
        try:
            import pandas as pd
            
            data = []
            for row in range(self.data_table.rowCount()):
                row_data = []
                for col in range(self.data_table.columnCount()):
                    item = self.data_table.item(row, col)
                    row_data.append(item.text() if item else "")
                data.append(row_data)
            
            columns = []
            for col in range(self.data_table.columnCount()):
                columns.append(self.data_table.horizontalHeaderItem(col).text())
            
            df = pd.DataFrame(data, columns=columns)
            
            if file_path.endswith('.csv'):
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
            elif file_path.endswith(('.xlsx', '.xls')):
                df.to_excel(file_path, index=False)
            else:
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
            
            self.status_label.setText(f"已保存: {os.path.basename(file_path)}")
            QMessageBox.information(self, "成功", "文件保存成功!")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存失败: {str(e)}")
    
    def _load_data_to_table(self):
        records = self.db.fetch_all("SELECT * FROM data_records ORDER BY created_at DESC")
        
        self.data_table.setRowCount(len(records))
        
        for row, record in enumerate(records):
            self.data_table.setItem(row, 0, QTableWidgetItem(str(record['id'])))
            self.data_table.setItem(row, 1, QTableWidgetItem(record['name'] or ""))
            self.data_table.setItem(row, 2, QTableWidgetItem(str(record['value'] or 0)))
            self.data_table.setItem(row, 3, QTableWidgetItem(record['category'] or ""))
            self.data_table.setItem(row, 4, QTableWidgetItem(str(record['created_at'] or "")))
    
    def _on_add_record(self):
        from PyQt5.QtWidgets import QDialog, QFormLayout, QDoubleSpinBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("添加记录")
        dialog.setFixedSize(300, 200)
        
        layout = QFormLayout(dialog)
        
        name_edit = QLineEdit()
        layout.addRow("名称:", name_edit)
        
        value_spin = QDoubleSpinBox()
        value_spin.setRange(-999999, 999999)
        layout.addRow("数值:", value_spin)
        
        category_combo = QComboBox()
        category_combo.addItems(["类别A", "类别B", "类别C", "其他"])
        layout.addRow("类别:", category_combo)
        
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)
        
        if dialog.exec_():
            self.db.insert('data_records', {
                'name': name_edit.text(),
                'value': value_spin.value(),
                'category': category_combo.currentText()
            })
            self._load_data_to_table()
            self.status_label.setText("记录已添加")
    
    def _on_delete_record(self):
        selected_rows = self.data_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择要删除的记录")
            return
        
        row = selected_rows[0].row()
        record_id = self.data_table.item(row, 0).text()
        
        reply = QMessageBox.question(
            self, "确认删除",
            "确定要删除这条记录吗?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.db.delete('data_records', 'id = ?', (record_id,))
            self._load_data_to_table()
            self.status_label.setText("记录已删除")
    
    def _on_refresh_data(self):
        self._load_data_to_table()
        self.status_label.setText("数据已刷新")
    
    def _on_search(self, text: str):
        for row in range(self.data_table.rowCount()):
            match = False
            for col in range(self.data_table.columnCount()):
                item = self.data_table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.data_table.setRowHidden(row, not match)
    
    def _on_show_chart(self):
        data = []
        for row in range(self.data_table.rowCount()):
            if not self.data_table.isRowHidden(row):
                name_item = self.data_table.item(row, 1)
                value_item = self.data_table.item(row, 2)
                category_item = self.data_table.item(row, 3)
                if name_item and value_item:
                    data.append({
                        'name': name_item.text(),
                        'value': float(value_item.text()) if value_item.text() else 0,
                        'category': category_item.text() if category_item else ""
                    })
        
        if not data:
            QMessageBox.warning(self, "警告", "没有数据可以显示图表")
            return
        
        dialog = ChartDialog(data, self)
        dialog.exec_()
    
    def _on_file_double_clicked(self, item: QTreeWidgetItem, column: int):
        file_name = item.text(0)
        if file_name.endswith(('.txt', '.csv', '.xlsx', '.xls')):
            self.status_label.setText(f"双击文件: {file_name}")
    
    def _toggle_toolbar(self, checked: bool):
        self.toolbar.setVisible(checked)
    
    def _toggle_statusbar(self, checked: bool):
        self.status_bar.setVisible(checked)
    
    def _on_about(self):
        QMessageBox.about(
            self, "关于文件管理器",
            "<h3>文件管理器 v1.0</h3>"
            "<p>一款简单实用的文件管理工具</p>"
            "<p>功能特性:</p>"
            "<ul>"
            "<li>文件打开与保存</li>"
            "<li>数据表格展示</li>"
            "<li>图表绘制</li>"
            "<li>用户登录管理</li>"
            "</ul>"
            "<p>适用于学生学习和日常使用</p>"
        )
    
    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, "确认退出",
            "确定要退出程序吗?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.db.close()
            event.accept()
        else:
            event.ignore()
