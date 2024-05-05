# Welcome to ifk-lantmateriet

ifk-lantmateriet is a python package to work with geo data
from Lantmäteriet (The Swedish Mapping, Cadastral and Land
Registration Authority). The main goal of the package is
to provide reusable components for building maps.
To this end, the package currently provides

- an API client to fetch subscribed data
- a CLI interface for workflow automation
- vector data manipulation

## Install

ifk-lantmateriet can be installed as

```bash
pip install ifk-lantmateriet
```

For the latest build, install from GitHub

```bash
pip install git+https://github.com/Ingenjorsarbete-For-Klimatet/ifk-lantmateriet.git@main
```

## Guide to Lantmäteriet

Data from Lantmäteriet can be downloaded through
[geotorget](https://geotorget.lantmateriet.se){target="\_blank"}.
Possible orders are

- single
- subscribed

Both single and subscribed orders can be downloaded diretly from geotroget, but
only subscribed orders can be downloaded multiple times. Lantmäteriet's API site
can be found [here](https://apimanager.lantmateriet.se){target="\_blank"}.
Accounts are needed for both sites.
