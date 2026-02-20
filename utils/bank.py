class Bank:

    accounts = {}

    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

        # добавляем счёт владельцу
        if owner in Bank.accounts:
            Bank.accounts[owner].append(self)
        else:
            Bank.accounts[owner] = [self]

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
        else:
            print("Сумма должна быть положительной")

    def withdraw(self, amount):
        if amount > self.balance:
            print("Недостаточно средств")
        elif amount <= 0:
            print("Сумма должна быть положительной")
        else:
            self.balance -= amount

    def __str__(self):
        return f"Владелец: {self.owner}, Баланс: {self.balance}"

    @classmethod
    def owner_info(cls, owner):
        if owner in cls.accounts:
            print(f"Владелец: {owner}")
            print(f"Количество счетов: {len(cls.accounts[owner])}")
            print("Суммы счетов:")
            for acc in cls.accounts[owner]:
                print(acc.balance)
        else:
            print("У владельца нет счетов")




