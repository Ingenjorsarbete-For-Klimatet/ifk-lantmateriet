# API

The provided API functionality is currently limited in this package.
Users can

- list the order information
- list available files in the order
- download a selected file from the order

## Prerequisites

### API token

In order to access the API a token must be generated from
[here](https://apimanager.lantmateriet.se){target="\_blank"} and
set as en environment variable

```bash
export LANTMATERIET_API_TOKEN=...
```

so it can be read from Python as

```python
import os

os.environ["LANTMATERIET_API_TOKEN"]
```

### Order id

An order must also be placed through
[geotorget](https://geotorget.lantmateriet.se){target="\_blank"}
and the order id acquired which is a unique id of the form

```bash
11a2ab333-1234-12ab-12a3-1a2bce3d45ef
```

## Usage

Example usage of the API client

```python
from lantmateriet.api import Lantmateriet

client = Lantmateriet("11a2ab333-1234-12ab-12a3-1a2bce3d45ef", "save_path")

client.order
# show order information

client.available_files
# show available filed for download in order

client.download("file.zip")
# download and extract zip file to save_path
```
