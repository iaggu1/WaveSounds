from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


class LeadCreateRequest(BaseModel):
    email: EmailStr = Field(max_length=255, description="E-mail do usuário")
    plan_interest: Literal["starter", "pro"] = Field(default="starter")
    company_website: str | None = Field(default=None, max_length=120)

    @field_validator("company_website")
    @classmethod
    def trim_honeypot(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else value

    model_config = {"extra": "forbid", "str_strip_whitespace": True}
