import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QProgressBar, QSystemTrayIcon, QMenu, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QIcon, QFont, QAction, QColor
from PyQt6.QtCore import QTimer, Qt, QSize
import qtawesome as qta

# ... (Toàn bộ stylesheet MODERN_STYLESHEET giữ nguyên như trước) ...
MODERN_STYLESHEET = """
QWidget#main_window {
    background-color: #2b2b2b;
    color: #f0f0f0;
    font-family: 'Segoe UI', Arial, sans-serif;
}

/* === Bỏ style cho màn hình chờ cũ === */
/* === Thêm style mới cho CONTAINER của màn hình chờ === */
QFrame#loading_container {
    background-color: #3c3c3c;  /* Một màu xám đậm hơn một chút */
    border: 1px solid #00aaff;  /* Viền màu xanh cyan nổi bật */
    border-radius: 12px;
}

QLabel#loading_title {
    font-size: 20px;
    font-weight: bold;
    color: #ffffff;
    padding-top: 10px;
}

QLabel#loading_status, QLabel#copyright_label, QLabel#link_label {
    color: #aaa;
    background-color: transparent; /* Đảm bảo các label bên trong trong suốt */
}

QLabel#link_label a {
    color: #00aaff;
    text-decoration: none;
    background-color: transparent;
}

QLabel#link_label a:hover {
    text-decoration: underline;
}

QProgressBar#loading_progress {
    border: none;
    background-color: #2b2b2b; /* Nền của thanh progress */
    border-radius: 4px;
    text-align: center;
    height: 8px;
}

QProgressBar#loading_progress::chunk {
    background-color: #00aaff;
    border-radius: 4px;
}


/* === Kiểu cho Cửa sổ chính (Giữ nguyên) === */
QLabel#title_label {
    font-size: 24px;
    font-weight: bold;
    color: #ffffff;
}

QLabel#countdown_label {
    font-size: 60px;
    font-weight: bold;
    color: #00aaff;
}

QLineEdit {
    background-color: #3c3c3c;
    border: 1px solid #555;
    border-radius: 8px;
    padding: 10px;
    font-size: 14px;
}

QLineEdit:focus {
    border: 1px solid #00aaff;
}

QProgressBar#main_progress {
    border: 1px solid #555;
    border-radius: 8px;
    background-color: #3c3c3c;
    text-align: center;
    height: 16px;
}

QProgressBar#main_progress::chunk {
    background-color: #00aaff;
    border-radius: 8px;
}

QPushButton {
    border-radius: 8px;
    font-size: 12px;
    font-weight: bold;
    padding: 12px 0;
}

QPushButton:hover {
    opacity: 0.9;
}

QPushButton:pressed {
    background-color: #111;
}

QPushButton#shutdown_button, QPushButton#restart_button {
    background-color: #00aaff;
    color: #ffffff;
}
QPushButton#shutdown_button:hover, QPushButton#restart_button:hover {
    background-color: #0088cc;
}

QPushButton#cancel_button {
    background-color: #e53935;
    color: #ffffff;
}
QPushButton#cancel_button:hover {
    background-color: #b71c1c;
}

QPushButton#exit_button {
    background-color: transparent;
    border: 1px solid #777;
    color: #ccc;
}
QPushButton#exit_button:hover {
    background-color: #444;
    border: 1px solid #999;
}
"""

# ======================================================================
# === CLASS LOADINGSCREEN ĐÃ ĐƯỢC CẬP NHẬT HOÀN CHỈNH ===
# ======================================================================
class LoadingScreen(QWidget):
    def __init__(self):
        super().__init__()
        # Cửa sổ chính vẫn là trong suốt và không có khung
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setFixedSize(420, 300) # Tăng kích thước để chứa bóng đổ
        self.progress_value = 0
        self.main_app_window = None

        self.init_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(20)

    def init_ui(self):
        # Layout chính của cửa sổ trong suốt
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10) # Tạo khoảng trống cho bóng đổ

        # Tạo container để chứa toàn bộ nội dung và áp dụng style
        self.container = QFrame(self)
        self.container.setObjectName("loading_container")
        main_layout.addWidget(self.container)

        # Layout cho nội dung bên trong container
        content_layout = QVBoxLayout(self.container)
        content_layout.setContentsMargins(20, 15, 20, 15)

        # Thêm hiệu ứng đổ bóng cho container
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.container.setGraphicsEffect(shadow)

        # === ĐẶT TẤT CẢ WIDGET VÀO BÊN TRONG content_layout ===
        icon_label = QLabel()
        app_icon = qta.icon('fa5s.power-off', color='#00aaff')
        icon_label.setPixmap(app_icon.pixmap(QSize(40, 40)))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel("Rikichi Pro 2025")
        title_label.setObjectName("loading_title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status_label = QLabel("Đang khởi tạo, vui lòng chờ...")
        self.status_label.setObjectName("loading_status")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("loading_progress")
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(False)
        
        copyright_label = QLabel("© Rikichi Pro 2025")
        copyright_label.setObjectName("copyright_label")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        link_label = QLabel('<a href="https://v3vn.eu">Dịch vụ mạng giá rẻ và miễn phí</a>')
        link_label.setObjectName("link_label")
        link_label.setOpenExternalLinks(True)
        link_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        link_label.setToolTip("Nhấp để truy cập v3vn.eu")

        content_layout.addWidget(icon_label)
        content_layout.addWidget(title_label)
        content_layout.addStretch()
        content_layout.addWidget(self.status_label)
        content_layout.addWidget(self.progress_bar)
        content_layout.addWidget(copyright_label)
        content_layout.addWidget(link_label)

    def update_progress(self):
        self.progress_value += 1
        self.progress_bar.setValue(self.progress_value)

        if self.progress_value >= 100:
            self.timer.stop()
            self.close()

            self.main_app_window = ShutdownTimerApp()
            self.main_app_window.show()

# ... (Class ShutdownTimerApp và phần if __name__ == "__main__": giữ nguyên) ...
class ShutdownTimerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("main_window")
        
        # --- Cài đặt icon hiện đại từ thư viện qtawesome ---
        self.app_icon = qta.icon('fa5s.power-off', color='#00aaff')
        self.tray_icon_widget = qta.icon('fa5s.power-off', color='white')

        self.setWindowTitle("Hẹn giờ tắt máy - Rikichi Pro 2025")
        self.setFixedSize(500, 400)
        self.setWindowIcon(self.app_icon)

        self.time_seconds = 0
        self.remaining_seconds = 0
        self.mode = ""
        
        self.timer = QTimer(self)
        self.timer.setInterval(1000)

        self.init_ui()
        self.create_tray()
        self.connect_signals()
        
        self.update_buttons_state(running=False)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(20)

        # --- TIÊU ĐỀ ---
        title_label = QLabel("Hẹn Giờ Tắt Máy")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # --- ĐƯỜNG KẺ PHÂN CÁCH ---
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)

        # --- KHU VỰC NHẬP THỜI GIAN ---
        time_layout = QHBoxLayout()
        time_label = QLabel("Nhập thời gian (phút):")
        time_label.setFont(QFont("Segoe UI", 11))
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("Ví dụ: 30")
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_input)
        main_layout.addLayout(time_layout)

        # --- ĐỒNG HỒ ĐẾM NGƯỢC ---
        self.countdown_label = QLabel("00:00:00")
        self.countdown_label.setObjectName("countdown_label")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.countdown_label)

        # --- THANH TIẾN TRÌNH ---
        self.progress = QProgressBar()
        self.progress.setObjectName("main_progress")
        self.progress.setTextVisible(False)
        self.progress.setValue(0)
        main_layout.addWidget(self.progress)
        
        main_layout.addStretch(1)

        # --- CÁC NÚT BẤM ---
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        self.btn_shutdown = QPushButton("TẮT MÁY")
        self.btn_shutdown.setObjectName("shutdown_button")
        
        self.btn_restart = QPushButton("KHỞI ĐỘNG LẠI")
        self.btn_restart.setObjectName("restart_button")

        self.btn_cancel = QPushButton("HỦY LỆNH")
        self.btn_cancel.setObjectName("cancel_button")

        self.btn_exit = QPushButton("Thoát")
        self.btn_exit.setObjectName("exit_button")
        
        for btn in [self.btn_shutdown, self.btn_restart, self.btn_cancel, self.btn_exit]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_layout.addWidget(self.btn_shutdown)
        btn_layout.addWidget(self.btn_restart)
        btn_layout.addWidget(self.btn_cancel)
        
        main_layout.addLayout(btn_layout)
        
        footer_layout = QHBoxLayout()
        copyright_label = QLabel("© Rikichi Pro 2025")
        copyright_label.setObjectName("copyright_label") # Dùng lại style cũ
        
        footer_layout.addWidget(copyright_label)
        footer_layout.addStretch()
        footer_layout.addWidget(self.btn_exit)
        main_layout.addLayout(footer_layout)

    def connect_signals(self):
        self.btn_shutdown.clicked.connect(self.start_shutdown)
        self.btn_restart.clicked.connect(self.start_restart)
        self.btn_cancel.clicked.connect(self.cancel_timer)
        self.btn_exit.clicked.connect(self.close)
        self.timer.timeout.connect(self.update_countdown)

    def start_timer_action(self, mode):
        try:
            minutes = self.time_input.text().strip()
            if not minutes or int(minutes) <= 0:
                raise ValueError
            self.time_seconds = int(minutes) * 60
        except ValueError:
            from PyQt6.QtWidgets import QMessageBox
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setText("Lỗi Nhập Liệu")
            msg_box.setInformativeText("Vui lòng nhập một số nguyên dương chỉ định số phút.")
            msg_box.setWindowTitle("Cảnh báo")
            msg_box.setStyleSheet("background-color: #3c3c3c;") # Style cho MessageBox
            msg_box.exec()
            return
            
        self.mode = mode
        self.remaining_seconds = self.time_seconds
        self.update_countdown_label()
        self.progress.setValue(0)
        self.timer.start()
        self.update_buttons_state(running=True)

        action_text = "tắt máy" if mode == "shutdown" else "khởi động lại"
        self.tray_icon.showMessage(
            "Đã lên lịch!",
            f"Máy tính sẽ {action_text} sau {self.time_seconds // 60} phút.",
            self.app_icon
        )

    def start_shutdown(self):
        self.start_timer_action("shutdown")

    def start_restart(self):
        self.start_timer_action("restart")

    def cancel_timer(self):
        self.timer.stop()
        os.system("shutdown /a")
        self.remaining_seconds = 0
        self.time_seconds = 0
        self.progress.setValue(0)
        self.countdown_label.setText("00:00:00")
        self.update_buttons_state(running=False)
        self.tray_icon.showMessage("Đã hủy", "Lệnh hẹn giờ đã được hủy thành công.", self.app_icon)

    def update_countdown(self):
        self.remaining_seconds -= 1
        self.update_countdown_label()
        
        if self.time_seconds > 0:
            progress_value = int(((self.time_seconds - self.remaining_seconds) / self.time_seconds) * 100)
            self.progress.setValue(progress_value)

        if self.remaining_seconds <= 0:
            self.timer.stop()
            self.progress.setValue(100)
            
            if self.mode == "shutdown":
                os.system("shutdown /s /t 1")
            elif self.mode == "restart":
                os.system("shutdown /r /t 1")
            
            QApplication.instance().quit()

    def update_countdown_label(self):
        h = self.remaining_seconds // 3600
        m = (self.remaining_seconds % 3600) // 60
        s = self.remaining_seconds % 60
        self.countdown_label.setText(f"{h:02d}:{m:02d}:{s:02d}")
        
    def update_buttons_state(self, running):
        self.btn_shutdown.setEnabled(not running)
        self.btn_restart.setEnabled(not running)
        self.time_input.setEnabled(not running)
        self.btn_cancel.setEnabled(running)
        self.btn_shutdown.setCursor(Qt.CursorShape.PointingHandCursor if not running else Qt.CursorShape.ForbiddenCursor)
        self.btn_restart.setCursor(Qt.CursorShape.PointingHandCursor if not running else Qt.CursorShape.ForbiddenCursor)
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor if running else Qt.CursorShape.ForbiddenCursor)

    def create_tray(self):
        self.tray_icon = QSystemTrayIcon(self.tray_icon_widget, self)
        self.tray_icon.setToolTip("Hẹn giờ tắt máy - Rikichi Pro 2025")

        tray_menu = QMenu(self)
        tray_menu.setStyleSheet("QMenu { background-color: #3c3c3c; color: #f0f0f0; border: 1px solid #555; }")
        
        show_action = QAction(qta.icon('fa5s.window-maximize', color='white'), "Hiển thị", self)
        quit_action = QAction(qta.icon('fa5s.sign-out-alt', color='white'), "Thoát", self)

        show_action.triggered.connect(self.show_normal)
        quit_action.triggered.connect(self.close)

        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_normal()

    def closeEvent(self, event):
        if self.timer.isActive():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "Đang chạy ẩn",
                "Ứng dụng vẫn đang đếm ngược dưới khay hệ thống.",
                self.app_icon
            )
        else:
            self.tray_icon.hide()
            event.accept()

    def show_normal(self):
        self.show()
        self.activateWindow()
        self.raise_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(MODERN_STYLESHEET)
    
    loading_screen = LoadingScreen()
    loading_screen.show()
    
    sys.exit(app.exec())
