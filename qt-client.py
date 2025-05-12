from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox, QLineEdit, QVBoxLayout, QPushButton, QLabel, QGridLayout, QListWidget, QMessageBox, QFormLayout, QFrame, QScrollArea, QWidget, QHBoxLayout
from PySide6.QtCore import Slot, Qt
import sys
from client_backend import ChatClient
import threading

class MessageBubble(QFrame):
    def __init__(self, text, is_sender=False):
        super().__init__()
        self.setStyleSheet(
            "background-color: {}; border-radius: 10px; padding: 5px;".format(
                "#DCF8C6" if is_sender else "#E5E5EA"
            )
        )
        layout = QHBoxLayout()
        label = QLabel(text)
        label.setWordWrap(True)
        layout.addWidget(label)
        layout.setAlignment(Qt.AlignRight if is_sender else Qt.AlignLeft)
        self.setLayout(layout)

class Login_window(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quackmessage - Login")
        self.resize(300, 200)
        login_grid = QFormLayout()
        # Declare widgets
        self.username_input = QLineEdit()
        self.passwd_input = QLineEdit()
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login_btn_func)
        
        create_account_btn = QPushButton("Create Account")
        
        login_grid.addRow(QLabel("Welcome to Quackmessage"))

        # Add these to layout
        login_grid.addRow(self.tr("Username:"), self.username_input)
        login_grid.addRow(self.tr("Password:"), self.passwd_input)
        login_grid.addRow(login_btn, create_account_btn)
        
        # Set this new layout to be used
        self.setLayout(login_grid)

    @Slot()
    def login_btn_func(self):
        username = self.username_input.text()
        passwd = self.passwd_input.text()
        self.close()
        Main_Window.login(username, passwd)

class Main_Window(QWidget):

    def __init__(self):
        super().__init__(parent=None)
        self.setWindowTitle("Quackmessage")
        self.resize(350, 400)
       
        self.authenticated = False
        # Initalize messager backend
        self.client = ChatClient()
        self.input_lock = threading.Lock()
        
        if not self.client.connect():
            msgBox = QMessageBox()
            msgBox.setText("Connection to server failed")
            msgBox.exec()
            self.exit_app()
        
        self.main_layout = QVBoxLayout()
        # Scroll area for messages
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.scroll_area.setWidget(self.messages_widget)
        self.main_layout.addWidget(self.scroll_area)

        header = QLabel(f"Logged in as: Noah")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-weight: bold; padding: 5px;")
        self.main_layout.addWidget(header)


         # Input field and send button
        self.input_layout = QHBoxLayout()
        self.input = QLineEdit()
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.input_layout.addWidget(self.input)
        self.input_layout.addWidget(self.send_button)
        self.main_layout.addLayout(self.input_layout)
        self.setLayout(self.main_layout)

        if not self.authenticated:
            msgBox = QMessageBox()
            msgBox.setText("Authentication cancelled. Exiting")
            self.client.disconnect()
            return

       
    def exit_app(self):
        self.close()
        self.client.disconnect()

    def login(username, passwd):
        print(f"Username = {username}, password = {passwd}")
        success, message = Main_Window.client.login(username, password)
        Main_Window.authenticated = True


    def send_message(self):
        text = self.input.text()
        if text:
            bubble = MessageBubble(text, is_sender=True)
            self.messages_layout.addWidget(bubble)
            self.input.clear()
            # Scroll to bottom
            self.scroll_area.verticalScrollBar().setValue(
                self.scroll_area.verticalScrollBar().maximum()
            )




if __name__ == "__main__":
    app = QApplication([])
    window = Main_Window()
    window.show()
    form = Login_window()
    form.show()
    sys.exit(app.exec())
