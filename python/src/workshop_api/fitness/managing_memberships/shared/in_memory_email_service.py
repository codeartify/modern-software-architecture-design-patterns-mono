class InMemoryEmailService:
    def __init__(self) -> None:
        self._sent_emails: list[str] = []

    def send(self, email_content: str) -> None:
        self._sent_emails.append(email_content)

    def sent_emails(self) -> list[str]:
        return list(self._sent_emails)

    def clear(self) -> None:
        self._sent_emails.clear()


email_service = InMemoryEmailService()
