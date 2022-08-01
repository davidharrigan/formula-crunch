import pytest

from collections import namedtuple

from scrape.race import get_driver_overtakes

ExpectedOvertake = namedtuple("ExpectedOvertake", ["lap", "passed", "position"])


def assert_driver_overtakes(drivers, overtakes, expected: list[ExpectedOvertake]):
    overtakes = overtakes[overtakes["PassingStatus"] == "OK"]
    # TODO: fix position to str?
    for lap, passed, position in expected:
        number = drivers[drivers["Code"] == passed].iloc[0]["DriverNumber"]
        check = overtakes.query(
            f'LapNumber == "{lap}" and DriverNumberAgainst == "{number}" and Position == {position}'
        )
        assert not check.empty, f"Missing overtake L{lap} on {passed} for {position}"
    assert len(overtakes) == len(expected), "Extra overtakes detected"


class TestAustria2022:
    def test_tsunoda(self, austria_2022):
        session, drivers = austria_2022
        overtakes = get_driver_overtakes(session, "22")
        expected = [
            ExpectedOvertake("2", "ZHO", "14"),
            ExpectedOvertake("13", "ZHO", "10"),  # This is wrong. Position regained.
            ExpectedOvertake("32", "LAT", "16"),
        ]
        assert_driver_overtakes(drivers, overtakes, expected)

    def test_alonso(self, austria_2022):
        session, drivers = austria_2022
        overtakes = get_driver_overtakes(session, "14")
        expected = [
            ExpectedOvertake("2", "VET", "17"),
            ExpectedOvertake("32", "LAT", "17"),
            ExpectedOvertake("33", "TSU", "16"),
            ExpectedOvertake("40", "STR", "13"),
            ExpectedOvertake("61", "STR", "13"),
            ExpectedOvertake("62", "GAS", "12"),
            ExpectedOvertake("67", "ALB", "11"),
            ExpectedOvertake("70", "BOT", "10"),
        ]
        assert_driver_overtakes(drivers, overtakes, expected)

    def test_zhou(self, austria_2022):
        session, drivers = austria_2022
        overtakes = get_driver_overtakes(session, "24")
        expected = [
            ExpectedOvertake("32", "LAT", "18"),
            ExpectedOvertake("37", "TSU", "17"),
            ExpectedOvertake("50", "VET", "17"),
            ExpectedOvertake("54", "TSU", "16"),
            ExpectedOvertake("67", "GAS", "14"),
        ]
        assert_driver_overtakes(drivers, overtakes, expected)

    def test_schumacher(self, austria_2022):
        session, drivers = austria_2022
        overtakes = get_driver_overtakes(session, "47")
        expected = [
            ExpectedOvertake("4", "HAM", "7"),
            ExpectedOvertake("19", "RIC", "13"),
            ExpectedOvertake("24", "ZHO", "11"),
            ExpectedOvertake("25", "ALO", "10"),
            ExpectedOvertake("27", "NOR", "8"),
            ExpectedOvertake("32", "MAG", "6"),
            ExpectedOvertake("45", "STR", "8"),
            ExpectedOvertake("47", "STR", "8"),
        ]
        assert_driver_overtakes(drivers, overtakes, expected)

    def test_norris(self, austria_2022):
        session, drivers = austria_2022
        overtakes = get_driver_overtakes(session, "4")
        expected = [
            ExpectedOvertake("5", "RIC", "9"),
            ExpectedOvertake("24", "ALO", "9"),
            ExpectedOvertake("24", "ZHO", "10"),
            ExpectedOvertake("41", "MAG", "7"),
            ExpectedOvertake("46", "TSU", "12"),
            ExpectedOvertake("62", "MAG", "7"),
        ]
        assert_driver_overtakes(drivers, overtakes, expected)

    def test_leclerc(self, austria_2022):
        session, drivers = austria_2022
        overtakes = get_driver_overtakes(session, "16")
        expected = [
            ExpectedOvertake("12", "VER", "1"),
            ExpectedOvertake("33", "VER", "1"),
            ExpectedOvertake("53", "VER", "1"),
        ]
        assert_driver_overtakes(drivers, overtakes, expected)

    def test_bottas(self, austria_2022):
        session, drivers = austria_2022
        overtakes = get_driver_overtakes(session, "77")
        expected = [
            # ExpectedOvertake("13", "GAS", "16"), passed on pit exit
            ExpectedOvertake("64", "ALB", "10"),
        ]
        assert_driver_overtakes(drivers, overtakes, expected)

    def test_hamilton(self, austria_2022):
        session, drivers = austria_2022
        overtakes = get_driver_overtakes(session, "44")
        expected = [
            ExpectedOvertake("14", "MSC", "5"),
            ExpectedOvertake("15", "MAG", "4"),
            ExpectedOvertake("30", "OCO", "4"),
        ]
        assert_driver_overtakes(drivers, overtakes, expected)

    def test_gasly(self, austria_2022):
        session, drivers = austria_2022
        overtakes = get_driver_overtakes(session, "10")
        expected = [
            ExpectedOvertake("15", "BOT", "16"),
        ]
        assert_driver_overtakes(drivers, overtakes, expected)

    def test_russel(self, austria_2022):
        session, drivers = austria_2022
        overtakes = get_driver_overtakes(session, "63")
        expected = [
            ExpectedOvertake("15", "LAT", "18"),
            ExpectedOvertake("17", "BOT", "17"),
            ExpectedOvertake("21", "GAS", "15"),
            ExpectedOvertake("24", "ALB", "14"),
            ExpectedOvertake("29", "RIC", "10"),
            ExpectedOvertake("42", "ZHO", "11"),
            ExpectedOvertake("44", "STR", "8"),
            ExpectedOvertake("44", "MSC", "9"),
            ExpectedOvertake("54", "ALO", "6"),
            ExpectedOvertake("61", "OCO", "4"),
        ]
        assert_driver_overtakes(drivers, overtakes, expected)

    def test_verstappen(self, austria_2022):
        session, drivers = austria_2022
        overtakes = get_driver_overtakes(session, "1")
        expected = [ExpectedOvertake("16", "MSC", "5"), ExpectedOvertake("18", "HAM", "3")]
        assert_driver_overtakes(drivers, overtakes, expected)

    def test_ocon(self, austria_2022):
        session, drivers = austria_2022
        overtakes = get_driver_overtakes(session, "31")
        expected = [
            ExpectedOvertake("20", "VET", "9"),
            ExpectedOvertake("21", "ALO", "8"),  # maybe team order
            ExpectedOvertake("22", "ZHO", "7"),
            ExpectedOvertake("23", "TSU", "6"),
            ExpectedOvertake("52", "ALO", "5"),
        ]
        assert_driver_overtakes(drivers, overtakes, expected)

    def test_magnussen(self, austria_2022):
        session, drivers = austria_2022
        overtakes = get_driver_overtakes(session, "20")
        expected = [
            ExpectedOvertake("22", "NOR", "10"),  # This is wrong, position regained
            ExpectedOvertake("24", "ZHO", "8"),
            ExpectedOvertake("24", "ALO", "8"),
            ExpectedOvertake("24", "NOR", "8"),  # This is wrong, position regained
            ExpectedOvertake("26", "TSU", "7"),
            ExpectedOvertake("44", "ZHO", "11"),
            ExpectedOvertake("47", "STR", "9"),
        ]
        assert_driver_overtakes(drivers, overtakes, expected)

    def test_vettel(self, austria_2022):
        session, drivers = austria_2022
        overtakes = get_driver_overtakes(session, "5")
        expected = [
            ExpectedOvertake("2", "ALO", "17"),
            ExpectedOvertake("29", "LAT", "15"),
            ExpectedOvertake("37", "BOT", "13"),
            ExpectedOvertake("67", "TSU", "16"),
        ]
        assert_driver_overtakes(drivers, overtakes, expected)

    def test_albon(self, austria_2022):
        session, drivers = austria_2022
        overtakes = get_driver_overtakes(session, "23")
        expected = [ExpectedOvertake("44", "VET", "15")]
        assert_driver_overtakes(drivers, overtakes, expected)

    def test_stroll(self, austria_2022):
        session, drivers = austria_2022
        overtakes = get_driver_overtakes(session, "18")
        expected = [
            ExpectedOvertake("30", "LAT", "15"),  # wrong?
            ExpectedOvertake("44", "RUS", "8"),  # wrong?
            ExpectedOvertake("45", "MSC", "8"),
            ExpectedOvertake("48", "LAT", "12"),  # wrong?
            ExpectedOvertake("48", "TSU", "12"),  # wrong?
            ExpectedOvertake("48", "GAS", "12"),  # wrong?
            ExpectedOvertake("64", "GAS", "13"),
        ]
        assert_driver_overtakes(drivers, overtakes, expected)
