class SafeLogger:
    def __init__(self, masked_fields=None):
        self.masked_fields = set(masked_fields or [])

    def redact(self, data: dict) -> dict:
        return {k: "***" if k in self.masked_fields else v for k, v in data.items()}

    def info(self, message: str, data: dict):
        redacted = self.redact(data)
        print(f"[INFO] {message} {redacted}")
