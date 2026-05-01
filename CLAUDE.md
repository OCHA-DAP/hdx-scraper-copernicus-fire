# CLAUDE.md

## Project Overview

**hdx-scraper-copernicus-fire** scrapes fire data from the Copernicus EFFIS/GWIS APIs and uploads it to the UN Humanitarian Data Exchange (HDX) platform. It produces three datasets:

- **copernicus-fire-danger-forecast** — 17 ECMWF fire index layers (WMS/GeoTIFF, 1-day forecast)
- **copernicus-burnt-areas** — MODIS burnt area polygons (WFS/GeoJSON, 1/7/30-day windows)
- **copernicus-fire-emissions** — CAMS GFAS emissions for 11 pollutants (WMS/GeoTIFF, 7-day rolling)

## Key Files

- `src/hdx/scraper/copernicus/fire/__main__.py` — orchestration entry point (`main()`)
- `src/hdx/scraper/copernicus/fire/api_retriever.py` — Copernicus WMS/WFS API client (`APIRetriever` class)
- `src/hdx/scraper/copernicus/fire/pipeline.py` — HDX dataset/resource generation (`Pipeline` class)
- `src/hdx/scraper/copernicus/fire/config/project_configuration.yaml` — datasets, layers, API endpoints
- `src/hdx/scraper/copernicus/fire/config/hdx_dataset_static.yaml` — static metadata applied to all datasets

## Running

```bash
uv run python -m hdx.scraper.copernicus.fire
```

Requires these files in `$HOME`:
- `.hdx_configuration.yaml` — HDX API key and site config
- `.useragents.yaml` — user agent config with key `hdx-scraper-copernicus-fire`

Or set environment variables: `HDX_KEY`, `HDX_SITE`, `USER_AGENT`, `EXTRA_PARAMS`.

Development flags (passed to `main()`):
- `save=True` — save downloaded API responses to `saved_data/` instead of `/tmp`
- `use_saved=True` — load from `saved_data/` instead of calling the API

## Testing

```bash
pytest
# or
uv run pytest
```

Tests live in `tests/test_pipeline.py`. The test uses `use_saved=True` with a fixed date (`2026-04-01`) for deterministic output against locally saved API responses in `saved_data/`.

To update expected outputs after intentional changes, update the assertions in `test_pipeline.py` and replace any saved input files.

## Code Style

- Formatted with `ruff` via pre-commit hooks. After changing any Python code, run:

```bash
pre-commit run --all-files
```

- Python ≥ 3.13

## Collaboration Style

- Be objective, not agreeable. Act as a partner, not a sycophant. Push back when you disagree, flag tradeoffs honestly, and don't sugarcoat problems.
- Keep explanations brief and to the point.
- Don't rely on recalled knowledge for facts that could be stale (API behaviour, library versions, external systems). Search or read the actual source first. If you lack verified information, say so rather than speculate.

## Scope of Changes

When fixing a bug or addressing PR feedback, change only what is necessary to resolve the specific issue. Do not refactor surrounding code, rename variables, adjust formatting, or make improvements in the same commit unless they are directly required by the fix. Unrelated changes obscure the intent of the fix and complicate review and blame.
