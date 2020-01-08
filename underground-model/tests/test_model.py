import context
import unittest

from underground.model import Model
from underground.parse import parse_underground, parse_dlr

class TestModel(unittest.TestCase):
    """Unit tests for the Model class"""

    def assertConsistent(self, model):
        """An extended test to ensure the model data is consistent"""

        for station in model.stations():
            station_obj = model.station(station)
            self.assertEqual(station_obj.name, station)

            self.assertIn(
                station,
                model.district(station_obj.district).stations
            )

            for zone in station_obj.zones:
                self.assertIn(station, model.zone(zone).stations)

            for line in station_obj.lines:
                self.assertIn(station, model.line(line).stations)

        for district in model.districts():
            district_obj = model.district(district)
            self.assertEqual(district_obj.name, district)

            for station in district_obj.stations:
                self.assertEqual(district, model.station(station).district)

        for zone in model.zones():
            zone_obj = model.zone(zone)
            self.assertEqual(zone_obj.id, zone)

            for station in zone_obj.stations:
                self.assertIn(zone, model.station(station).zones)

        for line in model.lines():
            line_obj = model.line(line)
            self.assertEqual(line_obj.name, line)

            for station in line_obj.stations:
                self.assertIn(line, model.station(station).lines)


    def test_add_stations(self):
        """Check adding stations works as expected"""
        model = Model()

        # Acessing a station before it has been added fails
        self.assertRaises(KeyError, lambda: model.station("Aldgate"))

        model.add_station("Aldgate", "City of London", (1,))
        self.assertEqual(model.station("Aldgate").name, "Aldgate")
        self.assertEqual(model.station("Aldgate").district, "City of London")
        self.assertEqual(model.station("Aldgate").zones, (1,))

        # Adding the station a second time fails
        self.assertRaises(
            ValueError,
            lambda: model.add_station("Aldgate", "City of London", (1,))
        )

        self.assertConsistent(model)

    def test_add_districts(self):
        """Check adding stations to districts works as expected"""
        model = Model()

        model.add_station("Aldgate", "City of London", (1,))
        self.assertEqual([*model.districts()], ["City of London"])

        self.assertEqual(
            model.district("City of London").stations,
            ["Aldgate"]
        )

        model.add_station("Bank", "City of London", (1,))
        self.assertEqual([*model.districts()], ["City of London"])

        self.assertEqual(
            model.district("City of London").stations,
            ["Aldgate", "Bank"]
        )

        model.add_station("Canary Wharf", "Tower Hamlets", (1,))
        self.assertEqual([*model.districts()], ["City of London", "Tower Hamlets"])

        self.assertEqual(
            model.district("City of London").stations,
            ["Aldgate", "Bank"]
        )

        self.assertEqual(
            model.district("Tower Hamlets").stations,
            ["Canary Wharf"]
        )

        self.assertConsistent(model)

    def test_add_zones(self):
        """Check adding stations to zones works as expected"""
        model = Model()

        model.add_station("Aldgate", "City of London", (1,))
        self.assertEqual([*model.zones()], [1])

        self.assertEqual(
            model.zone(1).stations,
            ["Aldgate"]
        )

        model.add_station("Earl's Court", "Kensington and Chelsea", (1, 2))
        self.assertEqual([*model.zones()], [1, 2])

        self.assertEqual(
            model.zone(1).stations,
            ["Aldgate", "Earl's Court"]
        )

        self.assertEqual(
            model.zone(2).stations,
            ["Earl's Court"]
        )

        self.assertConsistent(model)

    def test_add_lines(self):
        """Check adding stations to lines works as expected"""
        model = Model()

        self.assertRaises(
            KeyError,
            lambda: model.add_station_to_line("Aldgate", "Metropolitan")
        )

        model.add_station("Aldgate", "City of London", (1,))
        model.add_station_to_line("Aldgate", "Metropolitan")
        self.assertRaises(
            ValueError,
            lambda: model.add_station_to_line("Aldgate", "Metropolitan")
        )

        self.assertEqual(model.station("Aldgate").lines, ["Metropolitan"])
        self.assertEqual(
            model.line("Metropolitan").stations,
            ["Aldgate"]
        )

        model.add_station_to_line("Aldgate", "Circle")

        self.assertEqual(
            model.station("Aldgate").lines,
            ["Metropolitan", "Circle"]
        )
        self.assertEqual(
            model.line("Metropolitan").stations,
            ["Aldgate"]
        )
        self.assertEqual(
            model.line("Circle").stations,
            ["Aldgate"]
        )

        model.add_station("Baker Street", "City of Westminster", (1,))

        model.add_station_to_line("Baker Street", "Metropolitan")

        self.assertEqual(
            model.station("Aldgate").lines,
            ["Metropolitan", "Circle"]
        )
        self.assertEqual(
            model.station("Baker Street").lines,
            ["Metropolitan"]
        )
        self.assertEqual(
            model.line("Metropolitan").stations,
            ["Aldgate", "Baker Street"]
        )

        model.add_station_to_line("Baker Street", "Bakerloo")
        model.add_station_to_line("Baker Street", "Circle")
        model.add_station_to_line("Baker Street", "Jubilee")
        model.add_station_to_line("Baker Street", "Hammersmith & City")

        self.assertEqual(
            model.station("Baker Street").lines,
            ["Metropolitan", "Bakerloo", "Circle", "Jubilee", "Hammersmith & City"]
        )

        self.assertEqual(
            [*model.lines()],
            ["Metropolitan", "Circle", "Bakerloo", "Jubilee", "Hammersmith & City"]
        )

        self.assertConsistent(model)
