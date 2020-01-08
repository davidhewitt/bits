import json
import os

from flask import Flask, Response, jsonify, render_template
from flask_cors import CORS

from .model import Model
from .queries import shortest_route

FRONTEND_DIST_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "frontend",
        "dist"
    )
)


def make_error_response(reason: str) -> Response:
    """Helper to make error response"""
    return Response(json.dumps({"error": reason}), status=400)

def make_app(model: Model) -> Flask:
    """Create a flask application for the provided model"""

    print(FRONTEND_DIST_DIR)

    app = Flask(
        __name__,
        template_folder=FRONTEND_DIST_DIR,
        static_folder=FRONTEND_DIST_DIR,
        static_url_path=""
    )

    # Allow cross-origin requests
    CORS(app)

    @app.route("/")
    def frontpage():
        return render_template("index.html")

    @app.route("/station/<station>")
    def station_info(station):
        try:
            station = model.station(station)
        except KeyError:
            return make_error_response(f"No such station '{station}'")

        return jsonify({
            "name": station.name,
            "district": station.district,
            "zones": station.zones,
            "lines": station.lines
        })

    @app.route("/station/<station>/interchanges")
    def station_interchanges(station):
        try:
            station = model.station(station)
        except KeyError:
            return make_error_response(f"No such station '{station}'")

        return jsonify(sorted(station.lines))

    @app.route("/line/<line>/list-stations")
    def line_stations(line):
        try:
            line = model.line(line)
        except KeyError:
            return make_error_response(f"No such line '{line}'")

        return jsonify(sorted(line.stations))

    @app.route("/route/<start>/<destination>")
    def route(start, destination):
        try:
            route = shortest_route(model, start, destination)
        except KeyError as e:
            # NB when converting KeyError to string it will
            # include the quotes, e.g. str(e) -> "'Acton Town'"
            station = str(e)
            return make_error_response(f"No such station {station}")

        return jsonify([
            {
                "start": segment.start,
                "destination": segment.destination,
                "line": segment.line
            }
            for segment in route
        ])

    return app
