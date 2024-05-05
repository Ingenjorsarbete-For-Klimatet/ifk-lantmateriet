"""CLI module."""

import typer
from lantmateriet.api import Lantmateriet
from lantmateriet.extract import extract
from tqdm import tqdm

app = typer.Typer()


@app.callback()
def callback():
    """Lantmäteriet CLI client."""


@app.command()
def download_all(order_id: str, save_path: str):
    """Download files.

    Args:
        order_id: lantmäteriet order id
        save_path: path to save files to
    """
    client = Lantmateriet(order_id, save_path)
    all_files = client.available_files
    for file in tqdm(all_files):
        client.download(file)


@app.command()
def extract_all(source_path: str, target_path):
    """Extract geojson from gpkg files.

    Args:
        source_path: path to search for files
        target_path: path to save extracted files to
    """
    extract(source_path, target_path)
