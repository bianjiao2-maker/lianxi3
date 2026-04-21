from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QComboBox, QPushButton, QGroupBox,
    QScrollArea
)
from PyQt5.QtCore import Qt
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


class ChartCanvas(FigureCanvas):
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.patch.set_facecolor('#f8f9fa')
        super().__init__(self.fig)
        self.setParent(parent)
        self.axes = None
    
    def plot_bar(self, data, title="柱状图"):
        self.fig.clear()
        self.axes = self.fig.add_subplot(111)
        
        names = [d['name'] for d in data]
        values = [d['value'] for d in data]
        
        bars = self.axes.bar(names, values, color='#2196F3', edgecolor='#1976D2', linewidth=1.5)
        
        for bar, value in zip(bars, values):
            self.axes.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                          f'{value:.1f}', ha='center', va='bottom', fontsize=10)
        
        self.axes.set_title(title, fontsize=14, fontweight='bold', pad=15)
        self.axes.set_xlabel('名称', fontsize=12)
        self.axes.set_ylabel('数值', fontsize=12)
        self.axes.grid(axis='y', alpha=0.3, linestyle='--')
        self.axes.set_facecolor('#fafafa')
        
        self.fig.tight_layout()
        self.draw()
    
    def plot_pie(self, data, title="饼图"):
        self.fig.clear()
        self.axes = self.fig.add_subplot(111)
        
        names = [d['name'] for d in data]
        values = [d['value'] for d in data]
        
        colors = ['#2196F3', '#4CAF50', '#FF9800', '#E91E63', '#9C27B0', '#00BCD4']
        
        wedges, texts, autotexts = self.axes.pie(
            values, labels=names, autopct='%1.1f%%',
            colors=colors[:len(data)], startangle=90,
            explode=[0.02] * len(data),
            shadow=True
        )
        
        for text in texts:
            text.set_fontsize(11)
        for autotext in autotexts:
            autotext.set_fontsize(10)
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        self.axes.set_title(title, fontsize=14, fontweight='bold', pad=15)
        
        self.fig.tight_layout()
        self.draw()
    
    def plot_line(self, data, title="折线图"):
        self.fig.clear()
        self.axes = self.fig.add_subplot(111)
        
        names = [d['name'] for d in data]
        values = [d['value'] for d in data]
        
        self.axes.plot(names, values, marker='o', markersize=8, 
                      color='#2196F3', linewidth=2, markerfacecolor='white',
                      markeredgewidth=2, markeredgecolor='#2196F3')
        
        for i, (name, value) in enumerate(zip(names, values)):
            self.axes.annotate(f'{value:.1f}', (name, value), 
                             textcoords="offset points", xytext=(0, 10),
                             ha='center', fontsize=10)
        
        self.axes.set_title(title, fontsize=14, fontweight='bold', pad=15)
        self.axes.set_xlabel('名称', fontsize=12)
        self.axes.set_ylabel('数值', fontsize=12)
        self.axes.grid(True, alpha=0.3, linestyle='--')
        self.axes.set_facecolor('#fafafa')
        
        self.fig.tight_layout()
        self.draw()
    
    def plot_scatter(self, data, title="散点图"):
        self.fig.clear()
        self.axes = self.fig.add_subplot(111)
        
        names = [d['name'] for d in data]
        values = [d['value'] for d in data]
        
        scatter = self.axes.scatter(range(len(names)), values, 
                                   c='#2196F3', s=100, alpha=0.7,
                                   edgecolors='#1976D2', linewidths=2)
        
        self.axes.set_xticks(range(len(names)))
        self.axes.set_xticklabels(names, rotation=45, ha='right')
        
        self.axes.set_title(title, fontsize=14, fontweight='bold', pad=15)
        self.axes.set_xlabel('名称', fontsize=12)
        self.axes.set_ylabel('数值', fontsize=12)
        self.axes.grid(True, alpha=0.3, linestyle='--')
        self.axes.set_facecolor('#fafafa')
        
        self.fig.tight_layout()
        self.draw()


class ChartDialog(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self._init_ui()
    
    def _init_ui(self):
        self.setWindowTitle("数据图表")
        self.setMinimumSize(900, 700)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        control_group = QGroupBox("图表设置")
        control_layout = QHBoxLayout(control_group)
        
        chart_type_label = QLabel("图表类型:")
        control_layout.addWidget(chart_type_label)
        
        self.chart_combo = QComboBox()
        self.chart_combo.addItems(["柱状图", "饼图", "折线图", "散点图"])
        self.chart_combo.currentTextChanged.connect(self._on_chart_type_changed)
        control_layout.addWidget(self.chart_combo)
        
        control_layout.addStretch()
        
        refresh_btn = QPushButton("刷新图表")
        refresh_btn.clicked.connect(self._refresh_chart)
        control_layout.addWidget(refresh_btn)
        
        export_btn = QPushButton("导出图片")
        export_btn.clicked.connect(self._export_chart)
        control_layout.addWidget(export_btn)
        
        layout.addWidget(control_group)
        
        self.canvas = ChartCanvas(self, width=10, height=8)
        layout.addWidget(self.canvas)
        
        self._refresh_chart()
        
        self._apply_styles()
    
    def _apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QComboBox {
                padding: 8px 12px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                min-width: 120px;
            }
            QComboBox:focus {
                border-color: #2196F3;
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
        """)
    
    def _on_chart_type_changed(self, chart_type):
        self._refresh_chart()
    
    def _refresh_chart(self):
        chart_type = self.chart_combo.currentText()
        
        if chart_type == "柱状图":
            self.canvas.plot_bar(self.data, "数据柱状图")
        elif chart_type == "饼图":
            self.canvas.plot_pie(self.data, "数据饼图")
        elif chart_type == "折线图":
            self.canvas.plot_line(self.data, "数据折线图")
        elif chart_type == "散点图":
            self.canvas.plot_scatter(self.data, "数据散点图")
    
    def _export_chart(self):
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出图表", "chart.png",
            "PNG图片;;JPEG图片;;PDF文件;;SVG矢量图"
        )
        if file_path:
            self.canvas.fig.savefig(file_path, dpi=150, bbox_inches='tight',
                                   facecolor='white', edgecolor='none')
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "导出成功", f"图表已保存到:\n{file_path}")
