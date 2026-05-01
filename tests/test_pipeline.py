"""Tests for Copernicus Fire Pipeline"""

from pathlib import Path

from hdx.utilities.dateparse import parse_date
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
                retriever = Retrieve(
                    downloader=downloader,
                    fallback_dir=temp_folder,
                    saved_dir=input_dir,
                    temp_dir=temp_folder,
                    save=False,
                    use_saved=True,
                )

                today = parse_date("2026-04-01")
                tomorrow = parse_date("2026-04-02")
                one_day_ago = parse_date("2026-03-31")
                seven_days_ago = parse_date("2026-03-25")
                thirty_days_ago = parse_date("2026-03-02")

                # 1. Test APIRetriever
                api_retriever = APIRetriever(configuration, retriever)
                downloaded_files = api_retriever.process(today=today)

                assert "burnt_area" in downloaded_files
                assert "fire_forecast" in downloaded_files
                assert "fire_emissions" in downloaded_files

                # --- Burnt Area ---
                burnt_area_files = downloaded_files["burnt_area"]
                assert burnt_area_files == {
                    "modis_last_1_day": {
                        "download_url": (
                            "https://maps.effis.emergency.copernicus.eu/effis"
                            "?service=WFS&request=getfeature&typename=ms:modis.ba.poly"
                            "&version=1.1.0&outputformat=geojson"
                            "&FILTER=%3CFilter%3E%3CPropertyIsGreaterThanOrEqualTo%3E"
                            "%3CPropertyName%3ELASTUPDATE%3C/PropertyName%3E"
                            "%3CLiteral%3E2026-03-31/2026-04-01%3C/Literal%3E"
                            "%3C/PropertyIsGreaterThanOrEqualTo%3E%3C/Filter%3E"
                        ),
                        "end_date": today,
                        "ext": "geojson",
                        "layer_desc": "MODIS Burnt Area Polygons",
                        "path": Path(
                            "saved_data/copernicus-burnt-areas_modis_last_1d.geojson"
                        ),
                        "start_date": one_day_ago,
                        "time_desc": "last 1 day",
                    },
                    "modis_last_7_days": {
                        "download_url": (
                            "https://maps.effis.emergency.copernicus.eu/effis"
                            "?service=WFS&request=getfeature&typename=ms:modis.ba.poly"
                            "&version=1.1.0&outputformat=geojson"
                            "&FILTER=%3CFilter%3E%3CPropertyIsGreaterThanOrEqualTo%3E"
                            "%3CPropertyName%3ELASTUPDATE%3C/PropertyName%3E"
                            "%3CLiteral%3E2026-03-25/2026-04-01%3C/Literal%3E"
                            "%3C/PropertyIsGreaterThanOrEqualTo%3E%3C/Filter%3E"
                        ),
                        "end_date": today,
                        "ext": "geojson",
                        "layer_desc": "MODIS Burnt Area Polygons",
                        "path": Path(
                            "saved_data/copernicus-burnt-areas_modis_last_7d.geojson"
                        ),
                        "start_date": seven_days_ago,
                        "time_desc": "last 7 days",
                    },
                    "modis_last_30_days": {
                        "download_url": (
                            "https://maps.effis.emergency.copernicus.eu/effis"
                            "?service=WFS&request=getfeature&typename=ms:modis.ba.poly"
                            "&version=1.1.0&outputformat=geojson"
                            "&FILTER=%3CFilter%3E%3CPropertyIsGreaterThanOrEqualTo%3E"
                            "%3CPropertyName%3ELASTUPDATE%3C/PropertyName%3E"
                            "%3CLiteral%3E2026-03-02/2026-04-01%3C/Literal%3E"
                            "%3C/PropertyIsGreaterThanOrEqualTo%3E%3C/Filter%3E"
                        ),
                        "end_date": today,
                        "ext": "geojson",
                        "layer_desc": "MODIS Burnt Area Polygons",
                        "path": Path(
                            "saved_data/copernicus-burnt-areas_modis_last_30d.geojson"
                        ),
                        "start_date": thirty_days_ago,
                        "time_desc": "last 30 days",
                    },
                }

                # --- Fire Forecast (24 layers in config; ecmwf_extra_lightning has no saved file) ---
                fire_forecast_files = downloaded_files["fire_forecast"]
                assert len(fire_forecast_files) == 24

                _wms_base = (
                    "https://maps.effis.emergency.copernicus.eu/gwis?"
                    "LAYERS={layer}&FORMAT=image/tiff&TRANSPARENT=true&SINGLETILE=false"
                    "&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&STYLES=&SRS=EPSG:4326"
                    "&BBOX=-180.0,-90.0,180.0,90.0&WIDTH=3600&HEIGHT=1800&TIME=2026-04-02"
                )

                assert fire_forecast_files["ecmwf_anomaly_1_day_forecast"] == {
                    "download_url": _wms_base.format(layer="ecmwf.anomaly"),
                    "end_date": tomorrow,
                    "ext": "geotiff",
                    "layer_desc": "ECMWF Anomaly",
                    "path": Path(
                        "saved_data/copernicus-fire-danger-forecast_ecmwf_anomaly_1d_forecast.geotiff"
                    ),
                    "start_date": today,
                    "time_desc": "1 day forecast",
                }

                assert fire_forecast_files["ecmwf_mark5_df_1_day_forecast"] == {
                    "download_url": _wms_base.format(layer="ecmwf.mark5.df"),
                    "end_date": tomorrow,
                    "ext": "geotiff",
                    "layer_desc": "ECMWF MARK-5 Drought Factor (DF)",
                    "path": Path(
                        "saved_data/copernicus-fire-danger-forecast_ecmwf_mark5_df_1d_forecast.geotiff"
                    ),
                    "start_date": today,
                    "time_desc": "1 day forecast",
                }

                assert fire_forecast_files["ecmwf_nfdrs_sc_1_day_forecast"] == {
                    "download_url": _wms_base.format(layer="ecmwf.nfdrs.sc"),
                    "end_date": tomorrow,
                    "ext": "geotiff",
                    "layer_desc": "ECMWF NFDRS Spread Component (SC)",
                    "path": Path(
                        "saved_data/copernicus-fire-danger-forecast_ecmwf_nfdrs_sc_1d_forecast.geotiff"
                    ),
                    "start_date": today,
                    "time_desc": "1 day forecast",
                }

                # --- Fire Emissions ---
                fire_emissions_files = downloaded_files["fire_emissions"]
                assert len(fire_emissions_files) == 11

                _wms_emissions = (
                    "https://maps.effis.emergency.copernicus.eu/gwis?"
                    "LAYERS={layer}&FORMAT=image/tiff&TRANSPARENT=true&SINGLETILE=false"
                    "&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&STYLES=&SRS=EPSG:4326"
                    "&BBOX=-180.0,-90.0,180.0,90.0&WIDTH=3600&HEIGHT=1800"
                    "&TIME=2026-03-25/2026-04-01"
                )

                assert fire_emissions_files["gfas_bc_last_7_days"] == {
                    "download_url": _wms_emissions.format(layer="gfas.bc"),
                    "end_date": today,
                    "ext": "geotiff",
                    "layer_desc": "Emissions of Black Carbon (BC)",
                    "path": Path(
                        "saved_data/copernicus-fire-emissions_gfas_bc_last_7d.geotiff"
                    ),
                    "start_date": seven_days_ago,
                    "time_desc": "last 7 days",
                }

                # 2. Test Pipeline Dataset Generation
                pipeline = Pipeline(configuration, downloaded_files)

                # --- Burnt Area Dataset ---
                burnt_area_dataset = pipeline.generate_dataset(
                    "burnt_area", today=today
                )

                assert burnt_area_dataset == {
                    "dataset_date": "[2026-03-02T00:00:00 TO 2026-04-01T23:59:59]",
                    "dataset_preview": "no_preview",
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

                ba_resources = burnt_area_dataset.get_resources()
                assert ba_resources == [
                    {
                        "dataset_preview_enabled": "False",
                        "description": "GeoJSON representing MODIS Burnt Area Polygons last 1 day "
                        "(31 Mar 2026-1 Apr 2026)",
                        "format": "geojson",
                        "name": "copernicus-burnt-areas_modis_last_1d.geojson",
                    },
                    {
                        "dataset_preview_enabled": "False",
                        "description": "GeoJSON representing MODIS Burnt Area Polygons last 7 days "
                        "(25 Mar 2026-1 Apr 2026)",
                        "format": "geojson",
                        "name": "copernicus-burnt-areas_modis_last_7d.geojson",
                    },
                    {
                        "dataset_preview_enabled": "False",
                        "description": "GeoJSON representing MODIS Burnt Area Polygons last 30 days "
                        "(2 Mar 2026-1 Apr 2026)",
                        "format": "geojson",
                        "name": "copernicus-burnt-areas_modis_last_30d.geojson",
                    },
                ]

                # --- Fire Forecast Dataset ---
                fire_forecast_dataset = pipeline.generate_dataset(
                    "fire_forecast", today=today
                )

                assert fire_forecast_dataset == {
                    "dataset_date": "[2026-04-01T00:00:00 TO 2026-04-02T23:59:59]",
                    "dataset_preview": "no_preview",
                    "groups": [{"name": "world"}],
                    "name": "copernicus-fire-danger-forecast",
                    "notes": "Daily global forecast predicting fire danger conditions from the "
                    "ECMWF and NASA Geos-5 models. Provided as continuous raster GeoTIFFs.",
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

                ff_resources = fire_forecast_dataset.get_resources()
                assert len(ff_resources) == 24

                for res in ff_resources:
                    assert res["format"] == "geotiff"
                    assert "1 day forecast" in res["description"]

                # Layer order matches YAML: ecmwf_fwi[0], nasa_geos5_fwi[1], ..., ecmwf_dmc[8], ...
                # ecmwf_kbdi[14], ecmwf_mark5_ros[16], ecmwf_nfdrs_ic[22], ecmwf_extra_lightning[23]
                assert ff_resources[0] == {
                    "dataset_preview_enabled": "False",
                    "description": "GeoTIFF representing ECMWF Fire Weather Index (FWI) 1 day forecast "
                    "(1 Apr 2026-2 Apr 2026)",
                    "format": "geotiff",
                    "name": "copernicus-fire-danger-forecast_ecmwf_fwi_1d_forecast.geotiff",
                }
                assert ff_resources[14] == {
                    "dataset_preview_enabled": "False",
                    "description": "GeoTIFF representing ECMWF Keetch-Byron Drought Index (KBDI) "
                    "1 day forecast (1 Apr 2026-2 Apr 2026)",
                    "format": "geotiff",
                    "name": "copernicus-fire-danger-forecast_ecmwf_kbdi_1d_forecast.geotiff",
                }
                assert ff_resources[22] == {
                    "dataset_preview_enabled": "False",
                    "description": "GeoTIFF representing ECMWF NFDRS Ignition Probability (IC) "
                    "1 day forecast (1 Apr 2026-2 Apr 2026)",
                    "format": "geotiff",
                    "name": "copernicus-fire-danger-forecast_ecmwf_nfdrs_ic_1d_forecast.geotiff",
                }
                assert ff_resources[23] == {
                    "dataset_preview_enabled": "False",
                    "description": "GeoTIFF representing Lightning Forecast 1 day forecast "
                    "(1 Apr 2026-2 Apr 2026)",
                    "format": "geotiff",
                    "name": "copernicus-fire-danger-forecast_ecmwf_extra_lightning_1d_forecast.geotiff",
                }

                # --- Fire Emissions Dataset ---
                fire_emissions_dataset = pipeline.generate_dataset(
                    "fire_emissions", today=today
                )

                assert fire_emissions_dataset == {
                    "dataset_date": "[2026-03-25T00:00:00 TO 2026-04-01T23:59:59]",
                    "dataset_preview": "no_preview",
                    "groups": [{"name": "world"}],
                    "name": "copernicus-fire-emissions",
                    "notes": "Daily global fire emissions from the Copernicus Atmosphere Monitoring "
                    "Service (CAMS) Global Fire Assimilation System (GFAS). Provided as "
                    "continuous raster GeoTIFFs.",
                    "subnational": "1",
                    "tags": [
                        {
                            "name": "climate hazards",
                            "vocabulary_id": "b891512e-9516-4bf5-962a-7a289772a2a1",
                        },
                        {
                            "name": "environment",
                            "vocabulary_id": "b891512e-9516-4bf5-962a-7a289772a2a1",
                        },
                    ],
                    "title": "Fire Emissions (CAMS-GFAS)",
                }

                fe_resources = fire_emissions_dataset.get_resources()
                assert len(fe_resources) == 11

                for res in fe_resources:
                    assert res["format"] == "geotiff"
                    assert "last 7 days" in res["description"]

                assert fe_resources[0] == {
                    "dataset_preview_enabled": "False",
                    "description": "GeoTIFF representing Emissions of Black Carbon (BC) last 7 days "
                    "(25 Mar 2026-1 Apr 2026)",
                    "format": "geotiff",
                    "name": "copernicus-fire-emissions_gfas_bc_last_7d.geotiff",
                }
                assert fe_resources[10] == {
                    "dataset_preview_enabled": "False",
                    "description": "GeoTIFF representing Emissions of Total Carbon in Aerosols (TC) "
                    "last 7 days (25 Mar 2026-1 Apr 2026)",
                    "format": "geotiff",
                    "name": "copernicus-fire-emissions_gfas_tc_last_7d.geotiff",
                }
