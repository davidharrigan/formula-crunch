import pytest

from scrape.core import get_drivers, get_session


@pytest.fixture(scope="class")
def austria_2022():
    import fastf1

    fastf1.Cache.enable_cache("test/test_cache/")
    session = get_session(2022, "Austria", "R")
    session.load()
    drivers = get_drivers(2022)
    return session, drivers
