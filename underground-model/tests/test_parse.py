import context
import unittest

from underground.model import Model
from underground.parse import parse_underground, parse_dlr

class TestParseUnderground(unittest.TestCase):
    """Regression testing for the parsing of underground.html

    For stability I would normally save test data in a separate
    folder as e.g. sample_underground.html, but for clarity in
    this toy example I'm going to write the tests directly on
    top of the live data file.
    """

    def test_parse(self):
        model = parse_underground("underground.html")

        #
        # General properties of the network:
        #   - 270 stations (but 3 are duplicates that we merge)
        #   - 11 lines
        #   - 31 districts
        #   - 9 zones
        #

        self.assertEqual(len(model.stations()), 267)
        self.assertEqual(len(model.lines()), 11)
        self.assertEqual(len(model.districts()), 31)
        self.assertEqual(len(model.zones()), 9)


        #
        # Check a few of the stations according to the table
        # currently on wikipedia.
        #
        acton_town = model.station("Acton Town")
        self.assertEqual(acton_town.name, "Acton Town")
        self.assertEqual(acton_town.lines, ["District", "Piccadilly"])
        self.assertEqual(acton_town.district, "Ealing")
        self.assertEqual(acton_town.zones, (3,))

        # Edgware Road is one of the stations that should have merged
        # the list of lines
        edgware_road = model.station("Edgware Road")
        self.assertEqual(edgware_road.name, "Edgware Road")
        self.assertEqual(
            sorted(edgware_road.lines),
            ["Bakerloo", "Circle", "District", "Hammersmith & City"]
        )
        self.assertEqual(edgware_road.district, "City of Westminster")
        self.assertEqual(edgware_road.zones, (1,))

        hendon_central = model.station("Hendon Central")
        self.assertEqual(hendon_central.name, "Hendon Central")
        self.assertEqual(hendon_central.lines, ["Northern"])
        self.assertEqual(hendon_central.district, "Barnet")
        self.assertEqual(hendon_central.zones, (3, 4))


class TestParseDLR(unittest.TestCase):
    """Regression testing for the parsing of dlr.html

    For stability I would normally save test data in a separate
    folder as e.g. sample_underground.html, but for clarity in
    this toy example I'm going to write the tests directly on
    top of the live data file.
    """

    def test_parse(self):
        model = parse_dlr("dlr.html")

        #
        # General properties of the network:
        #   - 45 stations
        #   - 1 line (DLR)
        #   - 5 districts
        #   - 4 zones
        #

        self.assertEqual(len(model.stations()), 45)
        self.assertEqual(len(model.lines()), 1)
        self.assertEqual(len(model.districts()), 5)
        self.assertEqual(len(model.zones()), 4)


        #
        # Check a few of the stations according to the table
        # currently on wikipedia.
        #
        abbey_road = model.station("Abbey Road")
        self.assertEqual(abbey_road.name, "Abbey Road")
        self.assertEqual(abbey_road.lines, ["Docklands Light Railway"])
        self.assertEqual(abbey_road.district, "Newham")
        self.assertEqual(abbey_road.zones, (3,))

        # Canning town had two entries, but hopefully they've been merged
        canning_town = model.station("Canning Town")
        self.assertEqual(canning_town.name, "Canning Town")
        self.assertEqual(canning_town.lines, ["Docklands Light Railway"])
        self.assertEqual(canning_town.district, "Newham")
        self.assertEqual(canning_town.zones, (3,))

        bank = model.station("Bank")
        self.assertEqual(bank.name, "Bank")
        self.assertEqual(bank.lines, ["Docklands Light Railway"])
        self.assertEqual(bank.district, "City of London")
        self.assertEqual(bank.zones, (1,))


class TestParseBoth(unittest.TestCase):
    """Regression testing for joining both datasets."""

    def test_parse(self):
        model = Model()

        parse_underground("underground.html", model)
        parse_dlr("dlr.html", model)

        # General properties of the combined model
        self.assertEqual(len(model.stations()), 307)
        self.assertEqual(len(model.lines()), 12)
        self.assertEqual(len(model.districts()), 32)
        self.assertEqual(len(model.zones()), 9)

        # Just check a station merged cleanly
        bank = model.station("Bank")
        self.assertEqual(bank.name, "Bank")
        self.assertEqual(
            sorted(bank.lines),
            ['Central', 'Docklands Light Railway', 'Northern',
             'Waterloo & City']
        )
        self.assertEqual(bank.district, "City of London")
        self.assertEqual(bank.zones, (1,))
