import os
import sys
sys.path.insert(1, os.path.join(os.path.dirname(__file__), ".."))

import argparse

from underground import make_standard_model
from underground.server import make_app

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    app = make_app(make_standard_model())

    # Should really use a package like gunicorn to deploy
    # a production webserver, but this'll do for the toy example.
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=args.debug
    )
