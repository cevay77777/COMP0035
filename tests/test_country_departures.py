import pytest
from sqlmodel import SQLModel, Session, create_engine

from comp0035_air_passenger_departures.models import CountryDepartures


@pytest.fixture()
def session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


# ----------------------------
# total_for_year tests
# ----------------------------

def test_total_for_year_basic(session):
    rows = [
        CountryDepartures.create("2020-01", 1, 100.0),
        CountryDepartures.create("2020-02", 1, 200.0),
        CountryDepartures.create("2021-01", 1, 999.0),
    ]
    session.add_all(rows)
    session.commit()

    total = CountryDepartures.total_for_year(session, country_id=1, year=2020)
    assert total == 300.0


def test_total_for_year_no_data(session):
    total = CountryDepartures.total_for_year(session, country_id=99, year=2020)
    assert total == 0.0


def test_total_for_year_multiple_countries(session):
    rows = [
        CountryDepartures.create("2020-01", 1, 100.0),
        CountryDepartures.create("2020-01", 2, 500.0),
    ]
    session.add_all(rows)
    session.commit()

    total = CountryDepartures.total_for_year(session, country_id=1, year=2020)
    assert total == 100.0


def test_total_for_year_ignores_other_years(session):
    rows = [
        CountryDepartures.create("2019-12", 1, 100.0),
        CountryDepartures.create("2020-01", 1, 200.0),
    ]
    session.add_all(rows)
    session.commit()

    total = CountryDepartures.total_for_year(session, country_id=1, year=2020)
    assert total == 200.0


def test_total_for_year_invalid_year_raises(session):
    with pytest.raises(ValueError):
        CountryDepartures.total_for_year(session, country_id=1, year=-2020)


# ----------------------------
# top_countries_by_year tests
# ----------------------------

def test_top_countries_by_year_basic(session):
    rows = [
        CountryDepartures.create("2020-01", 1, 300.0),
        CountryDepartures.create("2020-02", 1, 200.0),
        CountryDepartures.create("2020-01", 2, 1000.0),
        CountryDepartures.create("2020-02", 2, 500.0),
    ]
    session.add_all(rows)
    session.commit()

    result = CountryDepartures.top_countries_by_year(session, year=2020, limit=2)

    assert result[0][0] == 2
    assert result[0][1] == 1500.0
    assert result[1][0] == 1
    assert result[1][1] == 500.0


def test_top_countries_by_year_limit_one(session):
    rows = [
        CountryDepartures.create("2020-01", 1, 100.0),
        CountryDepartures.create("2020-01", 2, 200.0),
    ]
    session.add_all(rows)
    session.commit()

    result = CountryDepartures.top_countries_by_year(session, year=2020, limit=1)

    assert len(result) == 1
    assert result[0][0] == 2


def test_top_countries_by_year_limit_exceeds_count(session):
    rows = [
        CountryDepartures.create("2020-01", 1, 100.0),
    ]
    session.add_all(rows)
    session.commit()

    result = CountryDepartures.top_countries_by_year(session, year=2020, limit=10)

    assert len(result) == 1

def test_top_countries_by_year_no_data(session):
    result = CountryDepartures.top_countries_by_year(session, year=2020, limit=5)
    assert result == []


def test_top_countries_by_year_invalid_limit_raises(session):
    with pytest.raises(ValueError):
        CountryDepartures.top_countries_by_year(session, year=2020, limit=0)

# ----------------------------
# create() validation tests
# ----------------------------

def test_create_invalid_month_format_raises():
    with pytest.raises(ValueError):
        CountryDepartures.create("2020/01", 1, 100.0)


def test_create_negative_country_id_raises():
    with pytest.raises(ValueError):
        CountryDepartures.create("2020-01", -1, 100.0)
