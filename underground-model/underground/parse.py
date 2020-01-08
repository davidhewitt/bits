"""Parsing functions to map the HTML files into the Model.

In the interest of time there's a few special cases which have been
hard-coded into the parsing functions. (E.g. Canning Town, Edgeware Road).
These special cases would be better dealt with by more general data cleaning
stages (as that would be a more robust solution). In the interest of time I'm
simply dealing with the special cases as they come, and documenting them.
"""

from typing import *

import re

from .model import Model

from bs4 import BeautifulSoup


def parse_underground(filename: str, model: Optional[Model]=None) -> Model:
    """Parse the underground dataset.

    Returns the Model of the dataset. If a model is provided to the function
    then the stations will be added to that model rather than a new one
    created.
    """

    with open(filename) as fd:
        soup = BeautifulSoup(fd.read(), features="lxml")

    # The first table is expected to be the relevant one
    table = soup.find("table")

    # The first row is the header row.
    # A more robust system would check the header columns,
    # but in the interest of time we're going to assume
    # the table schema is stable
    (header, *rows) = table.find_all("tr")

    # Initialise empty model if needed
    model = model or Model()

    # Each row represents a station
    for row in rows:
        # First column is names (in th cells)
        name = row.find("th").find("a").text

        # The rest of the columns are td cells
        fields = row.find_all("td")

        # Lines are listed links in the third column
        # But there are some associated footnotes
        # which are superscript with text like [m] or [e]
        footnote = re.compile("\[[a-zA-Z]\]")
        lines = [
            a.text for a in fields[1].find_all("a")
            if not footnote.match(a.text)
        ]

        # District is a link in the fourth column
        district = fields[2].find("a").text

        # Zones are links in the fifth column
        zones = tuple(int(a.text) for a in fields[3].find_all("a"))

        # NB because of Edgeware Road and Hammersmith have technically
        # got two stations (on different lines), we're going to carefully
        # merge them
        try:
            model.add_station(name=name, district=district, zones=zones)
        except ValueError:
            # The only difference with these duplicate stations is the lines
            # they're on.
            station = model.station(name)
            assert station.name == name
            assert station.district == district
            assert station.zones == zones

        for line in lines:
            try:
                model.add_station_to_line(name, line)
            except ValueError:
                # This is the only exception where two stations with the
                # same name are on the same lines
                assert name == "Paddington"
                assert line == "Circle"

    return model


def parse_dlr(filename: str, model: Optional[Model]=None) -> Model:
    """Parse the dlr dataset.

    Returns the Model of the dataset. If a model is provided to the function
    then the stations will be added to that model rather than a new one
    created.
    """

    with open(filename) as fd:
        soup = BeautifulSoup(fd.read(), features="lxml")

    # The second table is expected to be the relevant one
    table = soup.find_all("table")[1]

    # The first row is the header row.
    # A more robust system would check the header columns,
    # but in the interest of time we're going to assume
    # the table schema is stable
    (header, *rows) = table.find_all("tr")

    # Initialise empty model if needed
    model = model or Model()

    # Each row represents a station
    for row in rows:
        fields = row.find_all("td")

        # First column is names
        name = fields[0].find("a").text

        # District is a link in the third column
        # NB thanks to missing <a> tag for one of the Stratford
        # rows we have to process the stripped text instead
        district = fields[2].text.strip()

        # Zones are links in the fourth column
        zones = tuple(int(a.text) for a in fields[3].find_all("a"))

        # If we're adding to an existing underground model we expect
        # the stations to already exist.
        try:
            model.add_station(name=name, district=district, zones=zones)
        except ValueError:
            # The only difference with these duplicate stations is the lines
            # they're on.
            station = model.station(name)
            assert station.name == name
            assert station.district == district

            # These named underground stations are in zone 2 & 3,
            # but the DLR stations are only in 3
            assert station.zones == zones or \
                name == "Canning Town" or name == "Stratford" or \
                name == "West Ham"

        try:
            model.add_station_to_line(name, "Docklands Light Railway")
        except ValueError:
            # These are the only two stations with two parts that are
            # technically separate but both connect to the DLR
            assert name == "Canning Town" or name == "Stratford"

    return model
