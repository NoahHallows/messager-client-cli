from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox, QLineEdit, QVBoxLayout, QPushButton, QLabel, QGridLayout, QListWidget, QMessageBox, QFormLayout, QFrame, QScrollArea, QWidget, QHBoxLayout, QStackedWidget, QSizePolicy, QVBoxLayout
from PySide6.QtCore import Slot, Qt, Signal
import sys
from client_backend import ChatClient
import threading

class MessageBubble(QFrame):
    DEFAULT_HEIGHT = 40
    def __init__(self, text, sender, is_sender=False):
        
        super().__init__()
        # 1) Minimum height for single-line bubbles
        self.setMinimumHeight(self.DEFAULT_HEIGHT)
        # 2) No hard cap on maximum height
        self.setMaximumHeight(16777215)  # Qt’s “infinite” default
        
        # 3) SizePolicy: expand horizontally, but only use as much vertical as needed
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.setStyleSheet(
            "background-color: {}; border-radius: 10px; padding: 5px;".format(
                "#4CAF50" if is_sender else "#2196F3"
            )
        )
        layout = QHBoxLayout()
        label = QLabel(text)
        label.setWordWrap(True)
        sender_label = QLabel(sender)
        sender_label.setWordWrap(True)

        layout.addWidget(sender_label)
        layout.addWidget(label)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.setAlignment(Qt.AlignRight if is_sender else Qt.AlignLeft)
        layout.setContentsMargins(8, 4, 8, 4)
        self.setLayout(layout)

class Login_window(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Quackmessage - Login")
        self.resize(450, 500)
        login_grid = QFormLayout()
        # Declare widgets
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login_btn_func)
        
        create_account_btn = QPushButton("Create Account")
        
        create_account_btn.clicked.connect(self.create_account_btn_func)
        login_grid.addRow(QLabel("Welcome to Quackmessage"))

        # Add these to layout
        login_grid.addRow(self.tr("Username:"), self.username_input)
        login_grid.addRow(self.tr("Password:"), self.password_input)
        login_grid.addRow(create_account_btn, login_btn)
        
        # Set this new layout to be used
        self.setLayout(login_grid)

    @Slot()
    def create_account_btn_func(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if self.parent() and hasattr(self.parent(), 'on_login'):
            self.parent().on_login(username, password, True)


    @Slot()
    def login_btn_func(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if self.parent() and hasattr(self.parent(), 'on_login'):
            self.parent().on_login(username, password, False)


class Main_Window(QWidget):

    # define a signal that carries the new message text
    message_received = Signal(str, str)

    def __init__(self, username, password, create_account_var, parent=None):
        super().__init__(parent=parent)
        self.username = username
        self.password = password

        self.setWindowTitle("Quackmessage")
        self.resize(450, 500)

        # connect signal to a slot that actually updates the UI
        self.message_received.connect(self._append_message)

        # Initalize messager backend
        self.client = ChatClient()
        
        if not self.client.connect():
            self.showMsgBox("Error connecting to server")
            self.exit_app()

        if not self.client.version_check():
            self.showMsgBox("Update client")
            self.exit_app

        
        self.main_layout = QVBoxLayout()
        # Scroll area for messages
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.scroll_area.setWidget(self.messages_widget)
        self.main_layout.addWidget(self.scroll_area)

        if create_account_var == False:
            self.authenticated = self.login(username, password)
        else:
            self.authenticated = self.create_account(username, password)

        header = QLabel(f"Logged in as: {self.username}")
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

        # set up backend callback to emit the signal
        self.client.set_message_callback(lambda msg, sender: self.message_received.emit(msg, sender))
        self.client.start_receiving()

        #if not self.authenticated:
        #    self.showMsgBox("Authentication cancelled. Exiting")
        #    self.exit_app()

       
    def exit_app(self):
        self.close()
        self.client.disconnect()
        exit()

    def showMsgBox(self, text):
        msgBox = QMessageBox()
        msgBox.setText(text)
        msgBox.exec()
    
    def login(self, username, password):
        try:
            success, message = self.client.login(username, password)
            if success:
                return True
            else:
                self.showMsgBox("Incorrect username or password")
                self.exit_app()
#                if self.parent() and hasattr(self.parent(), 'login_screen'):
#                    self.parent().login_screen()

        except Exception as e:
            self.showMsgBox(f"Error logging in: {e}")

    def create_account(self, username, password):
        try:
            success, message = self.client.create_account(username, password)
            if success:
                return True
            else:
                self.showMsgBox(message)
                self.exit_app()
#                if self.parent() and hasattr(self.parent(), 'login_screen'):
#                    self.parent.login_screen()
        except Exception as e:
            self.showMsgBox(f"Error logging in: {e}")
            

    @Slot(str, str)
    def _append_message(self, message, sender):
        if message:
            if sender == self.username:
                is_sender = True
            else:
                is_sender = False
            bubble = MessageBubble(message, sender, is_sender)
            self.messages_layout.addWidget(bubble)
            self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
    @Slot()
    def send_message(self):
        text = self.input.text()
        # Send message
        if not self.client.send_message(text):
            self.showMsgBox("Error sending message")            
        if text:
            bubble = MessageBubble(text, self.username, is_sender=True)
            self.messages_layout.addWidget(bubble)
            self.input.clear()
            # Scroll to bottom
            self.scroll_area.verticalScrollBar().setValue(
                self.scroll_area.verticalScrollBar().maximum()
            )


class meta_window(QStackedWidget):

    def __init__(self):
        super().__init__()
        # Create login widget and add to stack
        self.login_widget = Login_window(parent=self)
        self.addWidget(self.login_widget)
        self.setWindowTitle("Quackmessage - Login")
        self.resize(500, 500) 
        self.Main_Window = None

        # Show login first
        self.setCurrentWidget(self.login_widget)

    def login_screen(self):
        print("in correct function")
        if self.login_widget:
            self.removeWidget(self.login_widget)
            self.login_widget.deleteLater()
        self.login_widget = Login_window(parent=self)
        self.addWidget(self.login_widget)
        self.setWindowTitle("Quackmessage - Login")
        self.setCurrentWidget(self.login_widget)


    def on_login(self, username, password, create_account_var):
        # Always recreate to reflect the new user
        if self.Main_Window:
            self.removeWidget(self.Main_Window)
            self.Main_Window.deleteLater()

        self.Main_Window = Main_Window(username=username, password=password, create_account_var=create_account_var, parent=self)
        self.addWidget(self.Main_Window)
        self.setCurrentWidget(self.Main_Window)



if __name__ == "__main__":
    app = QApplication([])
    window = meta_window()
    window.show()
    sys.exit(app.exec())
