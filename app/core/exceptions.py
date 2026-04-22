class AppError(Exception):
    pass


class NotFoundError(AppError):

    def __init__(self, short_code: str) -> None:
        self.short_code = short_code
        super().__init__(f"Short URL '{short_code}' not found.")
        

class ShortCodeCollisionError(AppError):

    def __init__(self) -> None:
        super().__init__("Failed to generate a unique short code. Please try again.")