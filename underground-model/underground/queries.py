"""Possible questions that can be asked of the model."""

from typing import *

from collections import defaultdict

import attr

from .model import Model


def most_interchanges(model: Model) -> Tuple[int, List[str]]:
    """The station(s) with the most interchanges in the Model."""

    counts = defaultdict(list)

    for station in model.stations():
        counts[len(model.station(station).lines)].append(station)

    max_count = max(counts.keys())

    return (max_count, counts[max_count])


def longest_line(model: Model) -> Tuple[int, List[str]]:
    """The line(s) with the most stations in the Model."""

    counts = defaultdict(list)

    for line in model.lines():
        counts[len(model.line(line).stations)].append(line)

    max_count = max(counts.keys())

    return (max_count, counts[max_count])


@attr.s(auto_attribs=True)
class JourneySegment:
    """A section of a journey.

    e.g. "ride the Piccadilly line from Green Park to Arsenal."
    """

    start: str
    """The name of the station to start at"""

    destination: str
    """The name of the station to finish at"""

    line: str
    """The line to take"""


def shortest_route(
    model: Model,
    start: str,
    destination: str
) -> List[JourneySegment]:
    """Get the recommended journey to take from one station to another.

    Raises ValueError if a route cannot be found.
    Raises KeyError if either station does not exist.
    """

    # We're going to calculate this using a modified Dijkstra's algorithm
    # to deduce the best journey to the station. In Dijkstras's algorithm
    # we process shortest links first.
    #
    # The dataset doesn't actually have any information on real travel times
    # and distances between stations but we can try to infer it from the
    # districts and zones the stations lie in.
    #
    # This will obviously be flawed in situations like the branches of the
    # northern line, but it's hopefully not too shabby for a first basic
    # effort.
    #
    # Hence in this instance we will work on lines at a time:
    #   - Lines in the initial station have a "cost" of zero. Then, repeat:
    #     - If the destination has a cost and it's lower than the cost of
    #       any unprocessed lines, stop. The route to the station is
    #       the best one.
    #     - For the lowest line cost line accessible and the station to
    #       access that line (chosen at random if there are multiple)
    #       assign an additional travel cost to all stations on that line
    #       according to the following formula:
    #         - Cost is the zone of the station, as this will encourage
    #           the algorithm to go through the center
    #         - Subtract 0.5 from the cost if they're in the same district,
    #           (as stations in the same line & district are likely closer
    #           together)
    #       - Record on each station the line, and cost. If that station is
    #         an interchange and gives a new "cheaper" way to access another
    #         line, update that line's cost.
    #       - Record the station used to access that line.
    #
    # Once we reach the stop condition we should be able to work backwards to
    # declare the route.

    # Lines which we have processed, recording the cost and the best station
    # to get onto that line.
    processed_lines: Dict[str, Tuple[float, str]] = {}

    # Unprocessed lines: the cost and the station to access them.
    line_weights: Dict[str, Tuple[float, str]] = {}

    # Processed stations: the cost and the best line to get to it
    processed_stations: Dict[str, Tuple[float, str]] = {}

    def item_cost(item: Tuple[str, Tuple[float, str]]):
        """Get cost from dict item from the dicts above"""
        return item[1][0]

    # Check the stations exist
    model.station(start)
    model.station(destination)

    # Initial step: seed the line weights
    for line in model.station(start).lines:
        line_weights[line] = (0, start)

    while len(line_weights) > 0:
        (line, (cost, line_station)) = min(line_weights.items(), key=item_cost)

        # This line is now processed, so move it out of line_weights
        # and into processed_lines
        del line_weights[line]
        processed_lines[line] = (cost, line_station)

        line_access_district = model.station(line_station).district

        for station in model.line(line).stations:
            station = model.station(station)
            station_cost = cost + min(station.zones)

            if station.district == line_access_district:
                station_cost -= 0.5

            # Update if visiting the station for the first time or we've found
            # a new best route to the station
            if (
                station.name not in processed_stations or
                processed_stations[station.name][0] > station_cost
            ):
                processed_stations[station.name] = (station_cost, line)

                # Update all the possible interchanges from that station,
                # if that's a new best route to that line
                for next_line in station.lines:
                    if (
                        next_line not in processed_lines and
                        (next_line not in line_weights or
                         line_weights[next_line][0] > station_cost)
                    ):
                        line_weights[next_line] = (station_cost, station.name)

        # If we can't possibly find a cheaper route to the destination, stop
        if (
            destination in processed_stations and
            cost >= processed_stations[destination][0]
        ):
            break


    if destination not in processed_stations:
        # We ran out of lines to evaluate; somehow this journey is impossible
        raise ValueError(f"Cannot find a route from {start} to {destination}")


    # Work backwards to tell the best route to the user
    journey_segments = []

    station = destination
    while station != start:
        line = processed_stations[station][1]
        line_start = processed_lines[line][1]
        journey_segments.append(JourneySegment(
            start=line_start,
            destination=station,
            line=line
        ))
        station = line_start

    # Reverse this and we have our journey!
    return journey_segments[::-1]
