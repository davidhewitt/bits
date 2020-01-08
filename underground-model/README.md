Underground
===========

A model of the London underground network as scraped from Wikipedia.

See `underground/queries.py` to see the questions the model is designed to answer.

Developed using Python 3.6. It makes use of the `typing` standard library to provide a little bit of type hinting and `attrs` external package to build dataclasses straightforwardly. (This is just for documentation purposes; the types are not checked at runtime by the Python interpreter.)

## Running

First set up an empty python virtualenv and install `requirements.txt`.

All scripts expect to be run from the project root directory, e.g. `bin/download.py`

## Testing

To run the tests, execute `tests/main.py` in a python interpreter.

## Frontend

The javascript frontend lives in the `frontend` subdirectory. Due to time constraints it is untested and poorly documented. I'm not hugely experienced with NLP so I just went for a dumb regex solution to provide a very basic sample of what a frontend might work like.
