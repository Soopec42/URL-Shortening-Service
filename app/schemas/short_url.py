from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, Field, field_validator, ConfigDict


class UrlCreateRequest(BaseModel):
    """Payload for creating a new short URL"""

    url: AnyHttpUrl = Field(..., description="The original long URL to short")

    @field_validator("url", mode="before")
    @classmethod
    def strip_spaces(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip()
        return v


class ShortUrlResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    url: str
    short_code: str = Field(alias="shortCode")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")



class ShortUrlStatsResponse(ShortUrlResponse):

    access_count: int = Field(alias="accessCount")


class ShortUrlDTO(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    short_code: str
    access_count: int
    created_at: datetime
    updated_at: datetime

    def to_response(self) -> ShortUrlResponse:
        return ShortUrlResponse(
            id=str(self.id),
            url=self.url,
            shortCode=self.short_code,
            createdAt=self.created_at,
            updatedAt=self.updated_at,
        )

    def to_stats_response(self) -> ShortUrlStatsResponse:
        return ShortUrlStatsResponse(
            id=str(self.id),
            url=self.url,
            shortCode=self.short_code,
            createdAt=self.created_at,
            updatedAt=self.updated_at,
            accessCount=self.access_count,
        )



