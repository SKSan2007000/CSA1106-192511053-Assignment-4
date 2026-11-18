
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Dict, List

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float) -> bool: ...

class CardPayment(PaymentStrategy):
    def pay(self, amount: float) -> bool:
        return amount > 0

class UpiPayment(PaymentStrategy):
    def pay(self, amount: float) -> bool:
        return amount > 0

class OrderObserver(ABC):
    @abstractmethod
    def update(self, order_id: str, status: str) -> None: ...

class EmailNotifier(OrderObserver):
    def update(self, order_id: str, status: str) -> None:
        print(f"EMAIL: order={order_id}, status={status}")

class AdminNotifier(OrderObserver):
    def update(self, order_id: str, status: str) -> None:
        print(f"ADMIN: order={order_id}, status={status}")

@dataclass
class Product:
    product_id: str
    name: str
    price: float
    stock: int

@dataclass
class Order:
    order_id: str
    product_id: str
    quantity: int
    total: float
    status: str = "PENDING"
    observers: List[OrderObserver] = field(default_factory=list, repr=False)

    def attach(self, observer: OrderObserver) -> None:
        self.observers.append(observer)

    def set_status(self, status: str) -> None:
        self.status = status
        for observer in self.observers:
            observer.update(self.order_id, status)

class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> None: ...
    @abstractmethod
    def find(self, order_id: str): ...

class InMemoryOrderRepository(OrderRepository):
    """Demo adapter only. Replace with the selected OODBMS adapter for submission."""
    def __init__(self):
        self.data: Dict[str, Order] = {}
    def save(self, order: Order) -> None:
        self.data[order.order_id] = order
    def find(self, order_id: str):
        return self.data.get(order_id)

class CheckoutService:
    def __init__(self, repo: OrderRepository, payment: PaymentStrategy):
        self.repo, self.payment = repo, payment

    def checkout(self, order_id: str, product: Product, quantity: int) -> Order:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if quantity > product.stock:
            raise ValueError("Insufficient stock")
        total = product.price * quantity
        if not self.payment.pay(total):
            raise RuntimeError("Payment declined")
        product.stock -= quantity
        order = Order(order_id, product.product_id, quantity, total)
        order.attach(EmailNotifier())
        order.attach(AdminNotifier())
        order.set_status("CONFIRMED")
        self.repo.save(order)
        return order

def run_demo():
    repo = InMemoryOrderRepository()
    service = CheckoutService(repo, UpiPayment())
    product = Product("P100", "Notebook", 50.0, 10)
    order = service.checkout("O500", product, 2)
    assert repo.find("O500") is order
    print(f"ORDER: {order.order_id} {order.status} total={order.total:.2f}")
    print(f"STOCK: {product.stock}")
    try:
        service.checkout("O501", product, 0)
    except ValueError as exc:
        print(f"VALIDATION: {exc}")

if __name__ == "__main__":
    run_demo()
