import os
import logging
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

from hdx.api.configuration import Configuration
from hdx.utilities.retriever import Retrieve

logger = logging.getLogger(__name__)


class APIRetriever:
    def __init__(self, configuration: Configuration, retriever: Retrieve):
        self._configuration = configuration
        self._retriever = retriever
        self._base_url = configuration["base_url"]
        self._bbox = configuration["bbox"]
        self._width = configuration["width"]
        self._height = configuration["height"]

    def _process_wfs(self, endpoint: str, layer_name: str, target_date: datetime,
                     filename: str, out_format: str) -> Optional[Path]:
        """Downloads WFS GeoJSON exactly as the server provides it."""
        date_str = target_date.strftime('%Y-%m-%d')

        xml_filter = (
            f"<Filter><PropertyIsGreaterThanOrEqualTo>"
            f"<PropertyName>LASTUPDATE</PropertyName>"
            f"<Literal>{date_str}</Literal>"
            f"</PropertyIsGreaterThanOrEqualTo></Filter>"
        )
        encoded_filter = urllib.parse.quote(xml_filter)

        url = (
            f"{self._base_url}/{endpoint}?service=WFS&request=getfeature"
            f"&typename={layer_name}&version=1.1.0"
            f"&outputformat={out_format.lower()}&FILTER={encoded_filter}"
        )

        logger.info(f"Requesting Global WFS GeoJSON: {filename}")
        return self._retriever.download_file(url, filename=filename)

    def _process_wms(self, endpoint: str, layer_name: str, time_str: str, filename: str,
                     out_format: str) -> Optional[Path]:
        """Downloads standard WMS GeoTIFF."""
        url = (
            f"{self._base_url}/{endpoint}?"
            f"SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&"
            f"LAYERS={layer_name}&"
            f"STYLES=&"  # Required parameter for modern MapServer
            f"FORMAT={out_format}&"
            f"TRANSPARENT=true&"
            f"SRS=EPSG:4326&"
            f"BBOX={self._bbox}&"
            f"WIDTH={self._width}&"
            f"HEIGHT={self._height}&"
            f"TIME={time_str}"
        )
        return self._retriever.download_file(url, filename=filename)

    def process(self, today: Optional[datetime] = None) -> Dict:
        if today is None:
            today = datetime.now()

        downloaded_files = {}
        datasets = self._configuration.get("datasets", {})

        for data_type, info in datasets.items():
            downloaded_files[data_type] = {}
            method = info.get("method", "wms")

            for layer_key, layer_dict in info["layers"].items():
                if "windows" in info and method == "wfs":
                    for days in info["windows"]:
                        date = today - timedelta(days=days)
                        label = f"{layer_key}_last_{days}_days"
                        filename = f"{info['name']}_{layer_key}_{days}d.geojson"

                        path = self._process_wfs(layer_dict["endpoint"],
                                                 layer_dict["layer"],
                                                 date, filename, info["format"])
                        if path:
                            downloaded_files[data_type][label] = {
                                "path": path, "start_date": date, "end_date": today,
                                "layer_desc": layer_dict["description"],
                                "time_desc": f"last {days} days", "ext": "geojson"
                            }

                elif "forecast_days" in info:
                    date = today + timedelta(days=info["forecast_days"])
                    label = f"{layer_key}_forecast"
                    filename = f"{info['name']}_{layer_key}.tif"

                    path = self._process_wms(layer_dict["endpoint"],
                                             layer_dict["layer"],
                                             date.strftime('%Y-%m-%d'), filename,
                                             info["format"])
                    if path:
                        downloaded_files[data_type][label] = {
                            "path": path, "start_date": today, "end_date": date,
                            "layer_desc": layer_dict["description"],
                            "time_desc": "forecast", "ext": "tif"
                        }
        return downloaded_files