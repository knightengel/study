"""
PyQt6 приложение для управления банковскими счетами.
Основано на классе Bank из utils/bank.py
"""

import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QFormLayout,
    QSplitter,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from utils import Bank


class BankApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Банковское приложение")
        self.setMinimumSize(600, 500)
        self.resize(700, 550)

        # Храним ссылки на счета для отображения
        self.account_items: dict[int, QListWidgetItem] = {}
        self.account_id = 0

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # === Создание счёта ===
        create_group = QGroupBox("Создать новый счёт")
        create_layout = QFormLayout(create_group)
        self.owner_input = QLineEdit()
        self.owner_input.setPlaceholderText("Имя владельца")
        self.balance_input = QLineEdit()
        self.balance_input.setPlaceholderText("Начальный баланс (0)")
        self.balance_input.setText("0")
        create_layout.addRow("Владелец:", self.owner_input)
        create_layout.addRow("Баланс:", self.balance_input)
        create_btn = QPushButton("Создать счёт")
        create_btn.clicked.connect(self.create_account)
        create_layout.addRow("", create_btn)
        layout.addWidget(create_group)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # === Список счетов ===
        accounts_group = QGroupBox("Счета")
        accounts_layout = QVBoxLayout(accounts_group)
        self.accounts_list = QListWidget()
        self.accounts_list.itemSelectionChanged.connect(self.on_account_selected)
        accounts_layout.addWidget(self.accounts_list)
        splitter.addWidget(accounts_group)

        # === Операции с выбранным счётом ===
        ops_group = QGroupBox("Операции")
        ops_layout = QVBoxLayout(ops_group)

        self.selected_info = QLabel("Выберите счёт")
        self.selected_info.setFont(QFont("", 11, QFont.Weight.Bold))
        ops_layout.addWidget(self.selected_info)

        amount_layout = QHBoxLayout()
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Сумма")
        amount_layout.addWidget(self.amount_input)
        ops_layout.addLayout(amount_layout)

        btn_layout = QHBoxLayout()
        deposit_btn = QPushButton("Пополнить")
        deposit_btn.clicked.connect(self.deposit)
        withdraw_btn = QPushButton("Снять")
        withdraw_btn.clicked.connect(self.withdraw)
        btn_layout.addWidget(deposit_btn)
        btn_layout.addWidget(withdraw_btn)
        ops_layout.addLayout(btn_layout)

        # === Информация о владельце ===
        owner_group = QGroupBox("Информация о владельце")
        owner_layout = QVBoxLayout(owner_group)
        self.owner_search = QLineEdit()
        self.owner_search.setPlaceholderText("Введите имя владельца")
        owner_layout.addWidget(self.owner_search)
        owner_btn = QPushButton("Показать счета владельца")
        owner_btn.clicked.connect(self.show_owner_info)
        owner_layout.addWidget(owner_btn)
        self.owner_result = QLabel("")
        self.owner_result.setWordWrap(True)
        owner_layout.addWidget(self.owner_result)

        ops_layout.addWidget(owner_group)
        splitter.addWidget(ops_group)

        splitter.setSizes([250, 350])
        layout.addWidget(splitter)

        # Отображаем счета, созданные в main.py
        self._refresh_list()

    def _add_account_to_list(self, account: Bank):
        item = QListWidgetItem(str(account))
        item.setData(Qt.ItemDataRole.UserRole, id(account))
        self.accounts_list.addItem(item)
        self.account_items[id(account)] = (item, account)

    def _refresh_list(self):
        self.accounts_list.clear()
        self.account_items.clear()
        for owner, accounts in Bank.accounts.items():
            for acc in accounts:
                item = QListWidgetItem(str(acc))
                item.setData(Qt.ItemDataRole.UserRole, id(acc))
                self.accounts_list.addItem(item)
                self.account_items[id(acc)] = (item, acc)

    def _get_selected_account(self) -> Bank | None:
        item = self.accounts_list.currentItem()
        if not item:
            return None
        acc_id = item.data(Qt.ItemDataRole.UserRole)
        if acc_id in self.account_items:
            return self.account_items[acc_id][1]
        return None

    def create_account(self):
        owner = self.owner_input.text().strip()
        if not owner:
            QMessageBox.warning(self, "Ошибка", "Введите имя владельца")
            return
        try:
            balance = float(self.balance_input.text() or "0")
            if balance < 0:
                raise ValueError("Баланс не может быть отрицательным")
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
            return
        acc = Bank(owner, balance)
        self._add_account_to_list(acc)
        self.owner_input.clear()
        self.balance_input.setText("0")
        QMessageBox.information(self, "Успех", f"Счёт создан: {acc}")

    def on_account_selected(self):
        acc = self._get_selected_account()
        if acc:
            self.selected_info.setText(str(acc))
        else:
            self.selected_info.setText("Выберите счёт")

    def deposit(self):
        acc = self._get_selected_account()
        if not acc:
            QMessageBox.warning(self, "Ошибка", "Выберите счёт")
            return
        try:
            amount = float(self.amount_input.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректную сумму")
            return
        success, msg = self._deposit_with_status(acc, amount)
        if success:
            self._refresh_list()
            self.amount_input.clear()
            self.selected_info.setText(str(acc))
            QMessageBox.information(self, "Успех", msg)
        else:
            QMessageBox.warning(self, "Ошибка", msg)

    def _deposit_with_status(self, acc: Bank, amount: float) -> tuple[bool, str]:
        if amount <= 0:
            return False, "Сумма должна быть положительной"
        acc.deposit(amount)
        return True, f"Пополнено на {amount}. Новый баланс: {acc.balance}"

    def withdraw(self):
        acc = self._get_selected_account()
        if not acc:
            QMessageBox.warning(self, "Ошибка", "Выберите счёт")
            return
        try:
            amount = float(self.amount_input.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректную сумму")
            return
        success, msg = self._withdraw_with_status(acc, amount)
        if success:
            self._refresh_list()
            self.amount_input.clear()
            self.selected_info.setText(str(acc))
            QMessageBox.information(self, "Успех", msg)
        else:
            QMessageBox.warning(self, "Ошибка", msg)

    def _withdraw_with_status(self, acc: Bank, amount: float) -> tuple[bool, str]:
        if amount <= 0:
            return False, "Сумма должна быть положительной"
        if amount > acc.balance:
            return False, "Недостаточно средств"
        acc.withdraw(amount)
        return True, f"Снято {amount}. Новый баланс: {acc.balance}"

    def show_owner_info(self):
        owner = self.owner_search.text().strip()
        if not owner:
            QMessageBox.warning(self, "Ошибка", "Введите имя владельца")
            return
        if owner not in Bank.accounts:
            self.owner_result.setText("У владельца нет счетов")
            return
        accounts = Bank.accounts[owner]
        lines = [
            f"Владелец: {owner}",
            f"Количество счетов: {len(accounts)}",
            "Балансы:",
        ]
        for acc in accounts:
            lines.append(f"  • {acc.balance}")
        self.owner_result.setText("\n".join(lines))


def main():
    app = QApplication(sys.argv)
    window = BankApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
