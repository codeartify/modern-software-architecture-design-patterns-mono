# Python Code Snippets (Converted from Java)

```python
def find_book_by_title(title: str):
    query = "SELECT * FROM books WHERE title = ?"
    cursor = connection.cursor()
    cursor.execute(query, (title,))
    row = cursor.fetchone()

    if row:
        return Book(
            id=row["id"],
            title=row["title"],
            is_borrowed=row["is_borrowed"],
        )

    return None
```

---

```python
def borrow_book(book_title: str, member_id: str) -> bool:
    book = find_book_by_title(book_title)

    if book is not None and not book.is_borrowed:
        member = find_member_by_id(member_id)

        if member is not None:
            book.is_borrowed = True
            return True

    return False
```

---

```python
from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.post("/book/borrow")
def borrow_book_endpoint(title: str = Form(...), member_id: int = Form(...)):
    success = library_service.borrow_book(title, member_id)

    if not success:
        return {"error": "Failed to borrow the book"}

    return RedirectResponse(url="/library")
```

---

```python
def register_member():
    name = input("Enter member name: ")
    member = Member(name)
    library.register_member(member)
    print("Member registered.")
```

---

```python
def enroll_student_in_course(student_id, course_id) -> bool:
    student = student_repository.find_by_id(student_id)
    course = course_repository.find_by_id(course_id)

    if student and course:
        enrollment = Enrollment()
        enrollment.student = student
        enrollment.course = course
        enrollment_repository.save(enrollment)
        return True

    return False
```

---

```python
def process_payment(payment: Payment):
    if is_duplicate_transaction(payment):
        raise ValueError("Duplicate transaction detected.")

    transaction_fee = calculate_transaction_fee(payment.amount)

    updated_payment = Payment(
        amount=payment.amount,
        currency=payment.currency,
        payment_method=payment.payment_method,
        status="Processed",
        transaction_fee=transaction_fee,
    )

    updated_payment.id = payment.id

    return payment_repository.save(updated_payment)
```

---

```python
import requests


def create_payment(payment: Payment):
    response = requests.post(
        f"{payment_service_url}/payments",
        json=payment.__dict__,
    )
    return response.json()
```

---

```python
import random
from datetime import date


def place_bet(player_id, amount, game):
    player = player_repository.find_by_id(player_id)
    if not player:
        raise ValueError("Player not found.")

    if amount > MAX_BET_LIMIT:
        raise ValueError("Bet amount exceeds the maximum limit.")

    new_balance = player.balance - amount
    if new_balance < MIN_BALANCE_REQUIRED:
        raise ValueError("Insufficient balance.")

    total_daily = bet_repository.find_total_amount_by_player_and_date(
        player_id, date.today().isoformat()
    )

    if total_daily + amount > DAILY_BET_LIMIT:
        raise ValueError("Daily bet limit exceeded.")

    result = random.random() > 0.5

    player.balance = new_balance
    player_repository.save(player)

    bet = Bet(None, player, amount, game, result)
    bet_repository.save(bet)

    return bet
```

---

```python
def process_payout(bet_id):
    bet = bet_repository.find_by_id(bet_id)
    if not bet:
        raise ValueError("Bet not found.")

    if not bet.result:
        raise ValueError("Bet did not win.")

    player = bet.player
    payout_amount = bet.amount * 2

    total_bets = bet_repository.find_total_amount_by_player_and_date(
        player.id, date.today().isoformat()
    )

    bonus = total_bets * 0.05
    payout_amount += bonus

    player.balance += payout_amount
    player_repository.save(player)

    payout = Payout(None, player, payout_amount)
    payout_repository.save(payout)

    return payout
```

---

```python
def borrow(self):
    if self.is_borrowed:
        raise ValueError("Book is already borrowed.")
    if self.borrow_count >= MAX_BORROW_COUNT:
        raise ValueError("Max borrow limit reached.")

    self.is_borrowed = True
    self.borrow_count += 1
```

---

```python
def return_book(self):
    if self.borrowed_books_count == 0:
        raise ValueError("No books to return.")

    self.borrowed_books_count -= 1
```

---

```python
def get_enrollment_details(self):
    return f"Student ID: {self.student_id}, Course ID: {self.course_id}, Status: {self.get_enrollment_status()}"
```

---

```python
def validate(self):
    if self.amount <= 0:
        raise ValueError("Payment amount must be greater than zero.")
    if not self.currency:
        raise ValueError("Currency cannot be empty.")
    if not self.payment_method:
        raise ValueError("Payment method cannot be empty.")
```
