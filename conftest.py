import pytest

from scrape.core import get_drivers


@pytest.fixture(scope="class")
def austria_2022():
    import fastf1

    fastf1.Cache.enable_cache("test/test_cache/")
    session = fastf1.get_session(2022, "Austria", "R")
    session.load()
    drivers = get_drivers(2022)
    return session, drivers


@pytest.fixture(scope="class")
def austria_2022_positions(austria_2022):
    from scrape.race.overtake import __get_position_changes
    from scrape.race.timing import get_timing_data

    session, drivers = austria_2022
    timing_data = get_timing_data(session)
    position_changes = __get_position_changes(session.laps, timing_data)

    return session, drivers, timing_data, position_changes
