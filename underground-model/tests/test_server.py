import json
import unittest

import context

from underground import make_standard_model
from underground.queries import JourneySegment
from underground.server import make_app

# Just use the main underground model for regression testing server
#
# In reality we should build a mock model (or several) to test the,
# but in the interest of time we're just going to use the actual one.
model = make_standard_model()
app = make_app(model)
client = app.test_client()

class TestServer(unittest.TestCase):
    """Regression testing for the server."""

    def test_station_data(self):
        self.assertEqual(
            json.loads(client.get("/station/Acton Town").data),
            {
                "name": "Acton Town",
                "district": "Ealing",
                "zones": [3],
                "lines": ["District", "Piccadilly"]
            }
        )

        self.assertEqual(
            json.loads(client.get("/station/Foo").data),
            {"error": "No such station 'Foo'"}
        )

    def test_station_interchanges(self):
        for station in model.stations():
            self.assertEqual(
                json.loads(client.get(f"/station/{station}/interchanges").data),
                sorted(model.station(station).lines)
            )

        self.assertEqual(
            json.loads(client.get("/station/Foo/interchanges").data),
            {"error": "No such station 'Foo'"}
        )

    def test_line_stations(self):
        for line in model.lines():
            self.assertEqual(
                json.loads(client.get(f"/line/{line}/list-stations").data),
                sorted(model.line(line).stations)
            )

        self.assertEqual(
            json.loads(client.get("/line/Foo/list-stations").data),
            {"error": "No such line 'Foo'"}
        )

    def test_shortest_route(self):
        self.assertEqual(
            json.loads(client.get("/route/Marylebone/Holborn").data),
            [
                {
                    "start": "Marylebone",
                    "destination": "Oxford Circus",
                    "line": "Bakerloo"
                },
                {
                    "start": "Oxford Circus",
                    "destination": "Holborn",
                    "line": "Central"
                }
            ]
        )

        self.assertEqual(
            json.loads(client.get("/route/Marylebone/Foo").data),
            {"error": "No such station 'Foo'"}
        )

        self.assertEqual(
            json.loads(client.get("/route/Foo/Holborn").data),
            {"error": "No such station 'Foo'"}
        )
