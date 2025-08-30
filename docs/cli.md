# CLI

When you install ifk-lantmateriet a CLI application is also
installed which can be invoked as

```bash
ifk-lantmateriet --help
```

It is mainly provided to simplify automated worekflows, e.g.
to download and extract data periodically.

## Prerequisites

In order to use the CLI an API token is necessary, see [API](api.md) page.

## Usage

### Download all

Example of downloading data to a folder called `save_path`

```bash
ifk-lantmateriet download-all 11a2ab333-1234-12ab-12a3-1a2bce3d45ef save_path
```

### Extract all

Example of extracting located in a folder called `sourch_path` to
a folder called `target_path`

```bash
ifk-lantmateriet extract-all sourch_path target_path
```
