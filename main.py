import sys
import requests
import binascii
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton,
    QTabWidget, QSplitter
)
from PyQt5.QtCore import Qt
from urllib.parse import urljoin

class BurpRepeater(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Repetear - aka s1or")
        self.setGeometry(100, 100, 1200, 600)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)  # ← quitar márgenes del layout general

        # Sección superior con fondo más claro para botón Send
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #2a2a2a;")
        header_widget.setFixedHeight(50)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(10, 5, 10, 5)  # ← quitar márgenes laterales

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_request)
        self.send_button.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                background-color: #a82323;
                color: white;
                border: 2px solid #a82323;
                border-radius: 5px;
                font-size: 12px;
                padding: 4px 13px;
            }
            QPushButton:hover {
                background-color: #d02d2d;
                border: 2px solid #d02d2d;
            }
        """)
        header_layout.addWidget(self.send_button)
        header_layout.addStretch()

        header_widget.setLayout(header_layout)
        main_layout.addWidget(header_widget)

        # Sección dividida entre Request y Response
        splitter = QSplitter(Qt.Horizontal)

        # --- Request ---
        request_group = QVBoxLayout()
        request_box = QWidget()
        request_box.setLayout(request_group)

        self.request_tabs = QTabWidget()
        self.request_pretty = QTextEdit()
        self.request_raw = QTextEdit()
        self.request_hex = QTextEdit()

        for tab in [self.request_pretty, self.request_raw, self.request_hex]:
            tab.setStyleSheet("background-color: #1e1e1e; color: #f0f0f0;")

        self.request_tabs.addTab(self.request_pretty, "Pretty")
        self.request_tabs.addTab(self.request_raw, "Raw")
        self.request_tabs.addTab(self.request_hex, "Hex")

        label_request = QLabel("Request")
        label_request.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom:5px")
        request_group.addWidget(label_request)
        request_group.addWidget(self.request_tabs)
        splitter.addWidget(request_box)

        # --- Response ---
        response_group = QVBoxLayout()
        response_box = QWidget()
        response_box.setLayout(response_group)

        self.response_tabs = QTabWidget()
        self.response_pretty = QTextEdit()
        self.response_raw = QTextEdit()
        self.response_hex = QTextEdit()
        self.response_render = QTextEdit()

        for tab in [self.response_pretty, self.response_raw, self.response_hex, self.response_render]:
            tab.setReadOnly(True)
            tab.setStyleSheet("background-color: #1e1e1e; color: #f0f0f0;")

        self.response_tabs.addTab(self.response_pretty, "Pretty")
        self.response_tabs.addTab(self.response_raw, "Raw")
        self.response_tabs.addTab(self.response_hex, "Hex")
        self.response_tabs.addTab(self.response_render, "Render")

        label_response = QLabel("Response")
        label_response.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom:5px")
        response_group.addWidget(label_response)
        response_group.addWidget(self.response_tabs)
        splitter.addWidget(response_box)

        splitter.setSizes([600, 600])
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

    def send_request(self):
        raw_input = self.request_pretty.toPlainText()
        lines = raw_input.splitlines()
        headers = {}
        body = b""
        path = "/"
        method = "GET"
        base_url = ""
        request_line_found = False
        reached_headers = True
        pretty_body = ""

        for i, line in enumerate(lines):
            if not request_line_found and (line.startswith("GET") or line.startswith("POST")):
                parts = line.split()
                if len(parts) >= 2:
                    method = parts[0].strip().upper()
                    path = parts[1]
                request_line_found = True
                continue
            elif line.strip() == "":
                reached_headers = False
                continue
            elif reached_headers:
                if ':' in line:
                    k, v = line.split(':', 1)
                    key = k.strip()
                    value = v.strip()
                    headers[key] = value
                    if key.lower() == "host":
                        base_url = value
            else:
                pretty_body += line + "\n"
                body += (line + "\n").encode('utf-8', errors='replace')

        if not base_url:
            error_msg = "[ERROR] No se encontró el header 'Host:'. Debes incluirlo en la solicitud."
            for tab in [self.response_pretty, self.response_raw, self.response_hex, self.response_render]:
                tab.setPlainText(error_msg)
            return

        if not base_url.startswith("http://") and not base_url.startswith("https://"):
            base_url = "https://" + base_url

        full_url = urljoin(base_url, path)

        try:
            self.request_raw.setPlainText(raw_input)
            hexed = binascii.hexlify(raw_input.encode('utf-8', errors='replace')).decode()
            self.request_hex.setPlainText(hexed)

            if method == "GET":
                response = requests.get(full_url, headers=headers, verify=False)
            else:
                response = requests.post(full_url, headers=headers, data=body, verify=False)

            content = response.content
            try:
                text = content.decode(response.encoding or 'utf-8')
            except UnicodeDecodeError:
                text = content.decode('utf-8', errors='replace')

            self.response_pretty.setPlainText(
                f"Status: {response.status_code}\n\n" + text
            )

            raw_headers = ''.join(f"{k}: {v}\n" for k, v in response.headers.items())
            self.response_raw.setPlainText(
                f"HTTP/{response.raw.version} {response.status_code} {response.reason}\n" + raw_headers + "\n" + text
            )

            hex_dump = content[:200].hex()
            self.response_hex.setPlainText(hex_dump)

            try:
                self.response_render.setHtml(text)
            except Exception:
                self.response_render.setPlainText("[!] No se pudo renderizar como HTML.")

        except Exception as e:
            error_msg = f"[ERROR] {str(e)}"
            for tab in [self.response_pretty, self.response_raw, self.response_hex, self.response_render]:
                tab.setPlainText(error_msg)

if __name__ == '__main__':
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    app = QApplication(sys.argv)

    dark_style = """
        QWidget {
            background-color: #121212;
            color: #f0f0f0;
        }
        QTextEdit {
            background-color: #1e1e1e;
            color: #f0f0f0;
            font-family: Consolas, monospace;
            font-size: 12px;
        }
        QTabBar::tab {
            background: #2d2d2d;
            color: #f0f0f0;
            width: 50px;
            height: 20px;
            border: 1px solid #444;
        }
        QTabBar::tab:selected {
            background: #3d3d3d;
            font-weight: bold;
        }
        QTabWidget::pane {
            border: none;
        }
    """
    app.setStyleSheet(dark_style)

    window = BurpRepeater()
    window.show()
    sys.exit(app.exec_())
