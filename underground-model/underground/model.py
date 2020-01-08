from typing import *

import attr


@attr.s(auto_attribs=True)
class Station:
    """A representation of a parsed station"""

    name: str
    """The name of the station"""

    district: str
    """The name of the district the station is in"""

    zones: Tuple[int, ...]
    """The zones the station is in (1-9)"""

    lines: List[str] = attr.Factory(list)
    """A list of the names of the lines the station is on"""


@attr.s(auto_attribs=True)
class Line:
    """A line of stations"""

    name: str
    """The name of the line"""

    stations: List[str] = attr.Factory(list)
    """The stations on the line"""


@attr.s(auto_attribs=True)
class District:
    """A local authority"""

    name: str
    """The name of the local authority"""

    stations: List[str] = attr.Factory(list)
    """Stations within the local authority"""


@attr.s(auto_attribs=True)
class Zone:
    """A local authority"""

    id: int
    """The id of the zone"""

    stations: List[str] = attr.Factory(list)
    """Stations within the zone"""


class Model:
    """A representation of the TFL underground network.

    The datastructure is in effect a graph - each of the
    stations has a number of relationships to lines, a zone
    and some districts.

    A full general graph solution would be overkill for this
    toy problem, so we're using a hard-coded structure here
    instead. (Can't add arbitrary properties or relationships.)
    """

    # Private backing values
    _stations: Dict[str, Station]
    _lines: Dict[str, Line]
    _districts: Dict[str, District]
    _zones: Dict[int, Zone]

    def __init__(self):
        """Initialise empty model"""
        self._stations = {}
        self._lines = {}
        self._districts = {}
        self._zones = {}

    #
    # Methods to access data from the model
    #

    def stations(self) -> KeysView[str]:
        """Iterable of station names"""
        return self._stations.keys()

    def lines(self) -> KeysView[str]:
        """Iterable of line names"""
        return self._lines.keys()

    def districts(self) -> KeysView[str]:
        """Iterable of district names"""
        return self._districts.keys()

    def zones(self) -> KeysView[int]:
        """Iterable of zone ids"""
        return self._zones.keys()

    def station(self, name: str) -> Station:
        """Get named station from the model.

        Users should not attempt to modify the Station object
        returned as it will corrupt the model. Use the methods
        on the Model instance to change model contents.

        Raises KeyError if the Station does not exist.
        """
        return self._stations[name]

    def line(self, name: str) -> Line:
        """Get named line from the model.

        Users should not attempt to modify the Line object
        returned as it will corrupt the model. Use the methods
        on the Model instance to change model contents.

        Raises KeyError if the Line does not exist.
        """
        return self._lines[name]

    def district(self, name: str) -> District:
        """Get named district from the model.

        Users should not attempt to modify the District object
        returned as it will corrupt the model. Use the methods
        on the Model instance to change model contents.

        Raises KeyError if the District does not exist.
        """
        return self._districts[name]

    def zone(self, id: int) -> Zone:
        """Get zone from the model.

        Users should not attempt to modify the Zone object
        returned as it will corrupt the model. Use the methods
        on the Model instance to change model contents.

        Raises KeyError if the Zone does not exist.
        """
        return self._zones[id]

    #
    # Methods to alter model content
    #

    def add_station(self, name: str, district: str, zones: Tuple[int, ...]):
        """Add a new station to the model.

        Districts and Zones will be created as necessary.
        """

        if name in self.stations():
            raise ValueError(f"Station {name} already exists")

        self._stations[name] = \
            Station(name=name, district=district, zones=tuple(zones))

        if district not in self.districts():
            self._districts[district] = District(name=district)

        self._districts[district].stations.append(name)

        for zone in zones:
            if zone not in self.zones():
                self._zones[zone] = Zone(id=zone)

            self._zones[zone].stations.append(name)


    def add_station_to_line(self, station_name: str, line: str):
        """Associate a station to a line.

        Lines will be created as necessary.

        Raises KeyError if the station does not exist.
        Raises ValueError if line has already been added to the station.
        """
        if line in self._stations[station_name].lines:
            raise ValueError(f"{station_name} already on {line}")

        if line not in self.lines():
            self._lines[line] = Line(name=line)

        self._lines[line].stations.append(station_name)
        self._stations[station_name].lines.append(line)
