"""Tests for Copernicus Fire Pipeline"""

from datetime import datetime
from pathlib import Path

from hdx.utilities.downloader import Download
from hdx.utilities.path import temp_dir
from hdx.utilities.retriever import Retrieve

from hdx.scraper.copernicus.fire.api_retriever import APIRetriever
from hdx.scraper.copernicus.fire.pipeline import Pipeline


class TestCopernicusFire:
    def test_pipeline(self, configuration, input_dir):
        """Test the API Retriever and Pipeline logic end-to-end."""
        with temp_dir("TestCopernicusFire") as temp_folder:
            with Download() as downloader:
                # Initialize Retriever to read from local input_dir instead of making web requests
                retriever = Retrieve(
                    downloader=downloader,
                    fallback_dir=temp_folder,
                    saved_dir=input_dir,
                    temp_dir=temp_folder,
                    save=False,
                    use_saved=True,
                )

                # 1. Lock the date for deterministic testing
                today = datetime(2026, 4, 1)

                # 2. Test APIRetriever
                api_retriever = APIRetriever(configuration, retriever)
                downloaded_files = api_retriever.process(today=today)

                assert "burnt_area" in downloaded_files
                assert "fire_forecast" in downloaded_files

                burnt_area_files = downloaded_files["burnt_area"]
                assert burnt_area_files == {
                    "modis_last_1_days": {
                        "download_url": "https://maps.effis.emergency.copernicus.eu/effis?service=WFS&request=getfeature&typename=ms:modis.ba.poly&version=1.1.0&outputformat=geojson&FILTER=%3CFilter%3E%3CPropertyIsGreaterThanOrEqualTo%3E%3CPropertyName%3ELASTUPDATE%3C/PropertyName%3E%3CLiteral%3E2026-03-31%3C/Literal%3E%3C/PropertyIsGreaterThanOrEqualTo%3E%3C/Filter%3E",
                        "end_date": datetime(2026, 4, 1, 0, 0),
                        "ext": "geojson",
                        "layer_desc": "MODIS Burnt Area Polygons",
                        "path": Path(
                            "tests/fixtures/input/copernicus-burnt-areas_modis_1d.geojson"
                        ),
                        "start_date": datetime(2026, 3, 31, 0, 0),
                        "time_desc": "last 1 days",
                    },
                    "modis_last_30_days": {
                        "download_url": "https://maps.effis.emergency.copernicus.eu/effis?service=WFS&request=getfeature&typename=ms:modis.ba.poly&version=1.1.0&outputformat=geojson&FILTER=%3CFilter%3E%3CPropertyIsGreaterThanOrEqualTo%3E%3CPropertyName%3ELASTUPDATE%3C/PropertyName%3E%3CLiteral%3E2026-03-02%3C/Literal%3E%3C/PropertyIsGreaterThanOrEqualTo%3E%3C/Filter%3E",
                        "end_date": datetime(2026, 4, 1, 0, 0),
                        "ext": "geojson",
                        "layer_desc": "MODIS Burnt Area Polygons",
                        "path": Path(
                            "tests/fixtures/input/copernicus-burnt-areas_modis_30d.geojson"
                        ),
                        "start_date": datetime(2026, 3, 2, 0, 0),
                        "time_desc": "last 30 days",
                    },
                    "modis_last_7_days": {
                        "download_url": "https://maps.effis.emergency.copernicus.eu/effis?service=WFS&request=getfeature&typename=ms:modis.ba.poly&version=1.1.0&outputformat=geojson&FILTER=%3CFilter%3E%3CPropertyIsGreaterThanOrEqualTo%3E%3CPropertyName%3ELASTUPDATE%3C/PropertyName%3E%3CLiteral%3E2026-03-25%3C/Literal%3E%3C/PropertyIsGreaterThanOrEqualTo%3E%3C/Filter%3E",
                        "end_date": datetime(2026, 4, 1, 0, 0),
                        "ext": "geojson",
                        "layer_desc": "MODIS Burnt Area Polygons",
                        "path": Path(
                            "tests/fixtures/input/copernicus-burnt-areas_modis_7d.geojson"
                        ),
                        "start_date": datetime(2026, 3, 25, 0, 0),
                        "time_desc": "last 7 days",
                    },
                }

                fire_forecast_files = downloaded_files["fire_forecast"]
                assert len(fire_forecast_files) == 17

                assert fire_forecast_files["ecmwf_anomaly_forecast"] == {
                    "download_url": "https://maps.effis.emergency.copernicus.eu/gwis?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS=ecmwf.anomaly&STYLES=&FORMAT=image/tiff&TRANSPARENT=true&SRS=EPSG:4326&BBOX=-180,-90,180,90&WIDTH=3600&HEIGHT=1800&TIME=2026-04-02",
                    "end_date": datetime(2026, 4, 2, 0, 0),
                    "ext": "tif",
                    "layer_desc": "ECMWF Anomaly",
                    "path": Path(
                        "tests/fixtures/input/copernicus-fire-danger-forecast_ecmwf_anomaly.tif"
                    ),
                    "start_date": datetime(2026, 4, 1, 0, 0),
                    "time_desc": "forecast",
                }

                assert fire_forecast_files["ecmwf_mark5_df_forecast"] == {
                    "download_url": "https://maps.effis.emergency.copernicus.eu/gwis?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS=ecmwf.mark5.df&STYLES=&FORMAT=image/tiff&TRANSPARENT=true&SRS=EPSG:4326&BBOX=-180,-90,180,90&WIDTH=3600&HEIGHT=1800&TIME=2026-04-02",
                    "end_date": datetime(2026, 4, 2, 0, 0),
                    "ext": "tif",
                    "layer_desc": "ECMWF MARK-5 Drought Factor (DF)",
                    "path": Path(
                        "tests/fixtures/input/copernicus-fire-danger-forecast_ecmwf_mark5_df.tif"
                    ),
                    "start_date": datetime(2026, 4, 1, 0, 0),
                    "time_desc": "forecast",
                }

                assert fire_forecast_files["ecmwf_nfdrs_sc_forecast"] == {
                    "download_url": "https://maps.effis.emergency.copernicus.eu/gwis?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS=ecmwf.nfdrs.sc&STYLES=&FORMAT=image/tiff&TRANSPARENT=true&SRS=EPSG:4326&BBOX=-180,-90,180,90&WIDTH=3600&HEIGHT=1800&TIME=2026-04-02",
                    "end_date": datetime(2026, 4, 2, 0, 0),
                    "ext": "tif",
                    "layer_desc": "ECMWF NFDRS Spread Component (SC)",
                    "path": Path(
                        "tests/fixtures/input/copernicus-fire-danger-forecast_ecmwf_nfdrs_sc.tif"
                    ),
                    "start_date": datetime(2026, 4, 1, 0, 0),
                    "time_desc": "forecast",
                }
                # 3. Test Pipeline Dataset Generation
                pipeline = Pipeline(configuration, downloaded_files)

                # --- Test Burnt Area Dataset ---
                burnt_area_dataset = pipeline.generate_dataset(
                    "burnt_area", today=today
                )

                assert burnt_area_dataset == {
                    "dataset_date": "[2026-03-02T00:00:00 TO 2026-04-01T23:59:59]",
                    "groups": [{"name": "world"}],
                    "name": "copernicus-burnt-areas",
                    "notes": "Raw vector polygons of recently updated global burnt areas from "
                    "MODIS. Provided as GeoJSON.",
                    "subnational": "1",
                    "tags": [
                        {
                            "name": "climate hazards",
                            "vocabulary_id": "b891512e-9516-4bf5-962a-7a289772a2a1",
                        },
                        {
                            "name": "damage assessment",
                            "vocabulary_id": "b891512e-9516-4bf5-962a-7a289772a2a1",
                        },
                        {
                            "name": "hazards and risk",
                            "vocabulary_id": "b891512e-9516-4bf5-962a-7a289772a2a1",
                        },
                    ],
                    "title": "Burnt Areas (MODIS)",
                }

                # Verify windows [1, 7, 30] created exactly 3 resources
                ba_resources = burnt_area_dataset.get_resources()
                assert ba_resources == [
                    {
                        "description": "GeoJSON representing MODIS Burnt Area Polygons last 1 days "
                        "(31 Mar 2026-1 Apr 2026)",
                        "format": "geojson",
                        "name": "copernicus-burnt-areas_modis_1d.geojson",
                    },
                    {
                        "description": "GeoJSON representing MODIS Burnt Area Polygons last 7 days "
                        "(25 Mar 2026-1 Apr 2026)",
                        "format": "geojson",
                        "name": "copernicus-burnt-areas_modis_7d.geojson",
                    },
                    {
                        "description": "GeoJSON representing MODIS Burnt Area Polygons last 30 days "
                        "(2 Mar 2026-1 Apr 2026)",
                        "format": "geojson",
                        "name": "copernicus-burnt-areas_modis_30d.geojson",
                    },
                ]

                # --- Test Fire Forecast Dataset ---
                fire_forecast_dataset = pipeline.generate_dataset(
                    "fire_forecast", today=today
                )

                assert fire_forecast_dataset == {
                    "dataset_date": "[2026-04-01T00:00:00 TO 2026-04-02T23:59:59]",
                    "groups": [{"name": "world"}],
                    "name": "copernicus-fire-danger-forecast",
                    "notes": "Daily global forecast predicting fire danger conditions from the "
                    "ECMWF model. Provided as continuous raster GeoTIFFs.",
                    "subnational": "1",
                    "tags": [
                        {
                            "name": "climate hazards",
                            "vocabulary_id": "b891512e-9516-4bf5-962a-7a289772a2a1",
                        },
                        {
                            "name": "forecasting",
                            "vocabulary_id": "b891512e-9516-4bf5-962a-7a289772a2a1",
                        },
                        {
                            "name": "hazards and risk",
                            "vocabulary_id": "b891512e-9516-4bf5-962a-7a289772a2a1",
                        },
                    ],
                    "title": "Fire Danger Forecast",
                }

                # Verify 17 ECMWF layers are processed
                ff_resources = fire_forecast_dataset.get_resources()
                assert len(ff_resources) == 17

                for res in ff_resources:
                    assert res["format"] == "geotiff"
                    assert "GeoTIFF representing ECMWF" in res["description"]

                assert ff_resources[0] == {
                    "description": "GeoTIFF representing ECMWF Fire Weather Index (FWI) forecast "
                    "(1 Apr 2026-2 Apr 2026)",
                    "format": "geotiff",
                    "name": "copernicus-fire-danger-forecast_ecmwf_fwi.tif",
                }
                assert ff_resources[8] == {
                    "description": "GeoTIFF representing ECMWF Keetch-Byron Drought Index (KBDI) "
                    "forecast (1 Apr 2026-2 Apr 2026)",
                    "format": "geotiff",
                    "name": "copernicus-fire-danger-forecast_ecmwf_kbdi.tif",
                }
                assert ff_resources[16] == {
                    "description": "GeoTIFF representing ECMWF NFDRS Ignition Probability (IC) "
                    "forecast (1 Apr 2026-2 Apr 2026)",
                    "format": "geotiff",
                    "name": "copernicus-fire-danger-forecast_ecmwf_nfdrs_ic.tif",
                }
