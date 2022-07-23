import pytest

from collections import namedtuple

from scrape.race import get_driver_overtakes
from scrape.race.timing import get_timing_data

ExpectedOvertake = namedtuple("ExpectedOvertake", ["lap", "passed", "position"])


def assert_driver_overtakes(drivers, overtakes, expected: list[ExpectedOvertake]):
    overtakes = overtakes[overtakes["PassingStatus"].isnull()]
    # TODO: fix position to str?
    for lap, passed, position in expected:
        number = drivers[drivers["Code"] == passed].iloc[0]["DriverNumber"]
        print(number)
        check = overtakes.query(
            f'LapNumber == "{lap}" and DriverNumberPassed == "{number}" and Position == {position}'
        )
        assert not check.empty, f"Missing overtake L{lap} on {passed} for {position}"
    assert len(overtakes) == len(expected), "Extra overtakes detected"


class TestAustria2022:
    def test_tsunoda(self, austria_2022):
        session, drivers = austria_2022
        timing = get_timing_data(session)
        overtakes = get_driver_overtakes(session, timing, "22")
        expected = [
            ExpectedOvertake("2", "ZHO", "14"),
            ExpectedOvertake("13", "ZHO", "10"),  # bad data from F1?
            ExpectedOvertake("32", "LAT", "16"),
            ExpectedOvertake("48", "VET", "15"),  # need to sort out pit exit for the driver
        ]
        assert_driver_overtakes(drivers, overtakes, expected)

    def test_alonso(self, austria_2022):
        session, drivers = austria_2022
        timing = get_timing_data(session)
        overtakes = get_driver_overtakes(session, timing, "14")
        expected = [
            ExpectedOvertake("2", "VET", "17"),
            ExpectedOvertake("24", "ZHO", "9"),
            ExpectedOvertake("32", "LAT", "17"),
            ExpectedOvertake("33", "TSU", "16"),
            ExpectedOvertake("40", "STR", "13"),
            ExpectedOvertake("61", "STR", "13"),
            ExpectedOvertake("62", "GAS", "12"),
            ExpectedOvertake("67", "ALB", "11"),
            ExpectedOvertake("70", "BOT", "10"),
        ]
        assert_driver_overtakes(drivers, overtakes, expected)

    # def test_vettel(self, austria_2022_session):
    #     pass
