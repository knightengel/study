import sys

from PyQt6.QtWidgets import QApplication

from gui.app import BankApp

app = QApplication(sys.argv)
window = BankApp()
window.show()
sys.exit(app.exec())
