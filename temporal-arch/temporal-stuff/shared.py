from dataclasses import dataclass

@dataclass
class OrderDetails:
    user_id: str

@dataclass
class NotEnoughInventoryError(Exception):
    def __init__(self, message) -> None:
        self.message: str = message
        super().__init__(self.message)

@dataclass
class InsufficientFundsError(Exception):
    def __init__(self, message) -> None:
        self.message: str = message
        super().__init__(self.message)