import context
import unittest

from underground import make_standard_model, queries
from underground.queries import JourneySegment

# Just use the main underground model for regression testing queries
#
# In reality we should build a mock model (or several) to test the
# queries on, but in the interest of time we're just going to use
# the actual one.
model = make_standard_model()

class TestQueries(unittest.TestCase):
    """Regression testing for the queries."""

    def test_most_interchanges(self):
        self.assertEqual(
            queries.most_interchanges(model),
            (6, ["King's Cross St Pancras"])
        )

    def test_longest_line(self):
        self.assertEqual(
            queries.longest_line(model),
            (60, ["District"])
        )

    def test_shortest_route(self):
        EXPECTED_ROUTES = [
            # Straightforward one
            ("Piccadilly Circus", "King's Cross St Pancras", [
                JourneySegment(
                    start="Piccadilly Circus",
                    destination="King's Cross St Pancras",
                    line="Piccadilly"
                )
            ]),

            # With one change
            ("Marylebone", "Holborn", [
                JourneySegment(
                    start="Marylebone",
                    destination="Oxford Circus",
                    line="Bakerloo"
                ),
                JourneySegment(
                    start="Oxford Circus",
                    destination="Holborn",
                    line="Central"
                )
            ]),

            # And a bit trickier!
            ("Paddington", "Cutty Sark for Maritime Greenwich", [
                JourneySegment(
                    start="Paddington",
                    destination="Oxford Circus",
                    line="Bakerloo"
                ),
                JourneySegment(
                    start="Oxford Circus",
                    destination="Bank",
                    line="Central"
                ),
                JourneySegment(
                    start="Bank",
                    destination="Cutty Sark for Maritime Greenwich",
                    line="Docklands Light Railway"
                )
            ])
        ]

        for (start, end, journey) in EXPECTED_ROUTES:
            print(start, "->", end)
            self.assertEqual(
                queries.shortest_route(model, start, end),
                journey
            )
