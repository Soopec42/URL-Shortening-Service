from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base

class ShortUrl(Base):
    __tablename__ = "short_urls"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    shortCode: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True)
    accessCount: Mapped[int] = mapped_column(Integer, default=0, nullable=False, server_default="0")
    createdAt: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"<ShortUrl id={self.id} code={self.short_code!r}>"
