import requests

UG_SRC = "https://en.wikipedia.org/wiki/List_of_London_Underground_stations"
DLR_SRC = \
    "https://en.wikipedia.org/wiki/List_of_Docklands_Light_Railway_stations"

def save_page(url, filename):
    """Download the contents of a page to a file on disk.

    This will be used just once initially to get the data files -
    processing will then be done locally on the files.
    """
    response = requests.get(url)
    with open(filename, 'wb') as fd:
        for chunk in response.iter_content(chunk_size=128):
            fd.write(chunk)

if __name__ == "__main__":
    save_page(UG_SRC, "underground.html")
    save_page(DLR_SRC, "dlr.html")
