import pytest

from collections import namedtuple

from scrape.core.timing import get_timing_data


class TestAustria2022:
    def test_sainz(self, austria_2022):
        session, drivers = austria_2022

        lap_53_segments = {
            # Sector 1
            "1.1": "Yellow",
            "1.2": "Yellow",
            "1.3": "Yellow",
            "1.4": "Yellow",
            "1.5": "Yellow",
            "1.6": "Yellow",
            # Sector 2
            "2.1": "Yellow",
            "2.2": "Yellow",
            "2.3": "Yellow",
            "2.4": "Yellow",
            "2.5": "Green",
            "2.6": "Yellow",
            "2.7": "Purple",
            # Sector 3
            "3.1": "Green",
            "3.2": "Green",
            "3.3": "Yellow",
            "3.4": "Green",
            "3.5": "Yellow",
            "3.6": "Yellow",
            "3.7": "Yellow",
        }
        pass
