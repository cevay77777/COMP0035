"""
SQLModel mappings for COMP0035 Coursework 2.

Implements:
- One SQLModel class mapped to one CW1 SQLite table.
- Two methods to provide enough testable logic for section 2.2.
"""

from __future__ import annotations

import re
from typing import Optional, List, Tuple

from sqlalchemy import func
from sqlmodel import SQLModel, Field, Session, select

_MONTH_RE = re.compile(r"^\d{4}-\d{2}$")


class CountryDepartures(SQLModel, table=True):
    """
    ORM model for the CountryDepartures table.

    month: YYYY-MM (composite primary key)
    country_id: integer (composite primary key)
    value: departures (float, nullable)
    """

    __tablename__ = "CountryDepartures"

    month: str = Field(primary_key=True)
    country_id: int = Field(primary_key=True)
    value: Optional[float] = Field(default=None)

    @staticmethod
    def validate_month(month: str) -> None:
        """Validate month string format (YYYY-MM) and month range."""
        if not _MONTH_RE.match(month):
            raise ValueError("month must be in YYYY-MM format")

        year = int(month[:4])
        mm = int(month[5:7])
        if year < 1900 or mm < 1 or mm > 12:
            raise ValueError("month must have a valid year and month (01-12)")

    @classmethod
    def create(cls, month: str, country_id: int, value: Optional[float]) -> "CountryDepartures":
        """
        Safe constructor used in tests.
        Validates month, country_id, and value.
        """
        cls.validate_month(month)

        if country_id <= 0:
            raise ValueError("country_id must be a positive integer")

        if value is not None and value < 0:
            raise ValueError("value must be >= 0")

        return cls(month=month, country_id=country_id, value=value)

    @classmethod
    def total_for_year(cls, session: Session, country_id: int, year: int) -> float:
        """
        Sum all departures for a given country in a given year.
        Returns 0.0 if no rows exist.
        """
        if country_id <= 0:
            raise ValueError("country_id must be positive")
        if year < 1900 or year > 2100:
            raise ValueError("year out of expected range")

        prefix = f"{year:04d}-"
        stmt = (
            select(func.coalesce(func.sum(cls.value), 0.0))
            .where(cls.country_id == country_id)
            .where(cls.month.startswith(prefix))
        )
        return float(session.exec(stmt).one())

    @classmethod
    def top_countries_by_year(
        cls, session: Session, year: int, limit: int = 10
    ) -> List[Tuple[int, float]]:
        """
        Return (country_id, total) for the top countries in a year.
        """
        if year < 1900 or year > 2100:
            raise ValueError("year out of expected range")
        if limit <= 0:
            raise ValueError("limit must be positive")

        prefix = f"{year:04d}-"
        stmt = (
            select(cls.country_id, func.coalesce(func.sum(cls.value), 0.0).label("total"))
            .where(cls.month.startswith(prefix))
            .group_by(cls.country_id)
            .order_by(func.sum(cls.value).desc())
            .limit(limit)
        )
        return [(int(cid), float(total)) for cid, total in session.exec(stmt).all()]

