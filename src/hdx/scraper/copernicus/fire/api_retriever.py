import logging
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

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

    def _process_wfs(
        self,
        endpoint: str,
        layer_name: str,
        date_str: str,
        filename: str,
        out_format: str,
    ) -> tuple[Path | None, str]:
        """Downloads WFS GeoJSON exactly as the server provides it."""
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
        return self._retriever.download_file(url, filename=filename), url

    def _process_wms(
        self,
        endpoint: str,
        layer_name: str,
        time_str: str,
        filename: str,
        out_format: str,
    ) -> tuple[Path | None, str]:
        """Downloads standard WMS GeoTIFF."""
        url = (
            f"{self._base_url}/{endpoint}?"
            f"LAYERS={layer_name}&"
            f"FORMAT={out_format}&"
            "TRANSPARENT=true&SINGLETILE=false&SERVICE=WMS&"
            "VERSION=1.1.1&REQUEST=GetMap&STYLES=&SRS=EPSG:4326&"
            f"BBOX={self._bbox}&"
            f"WIDTH={self._width}&"
            f"HEIGHT={self._height}&"
            f"TIME={time_str}"
        )
        return self._retriever.download_file(url, filename=filename), url

    @staticmethod
    def get_metadata(info: dict, today: datetime, days: int, layer_key: str) -> tuple:
        forecast = info["forecast"]
        if days == 1:
            day_or_days = "day"
        else:
            day_or_days = "days"
        if forecast:
            time_desc = f"{days}_{day_or_days}_forecast"
            start_date = today
            end_date = today + timedelta(days=days)
            date_str = end_date.strftime("%Y-%m-%d")
        else:
            time_desc = f"last_{days}_{day_or_days}"
            start_date = today - timedelta(days=days)
            end_date = today
            date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            date_str = f"{date_str}/{end_date_str}"
        label = f"{layer_key}_{time_desc}"
        filename = f"{info['name']}_{layer_key}_{time_desc}.{info['ext']}"
        filename = filename.replace(f"_{day_or_days}", "d")
        return start_date, end_date, date_str, time_desc, label, filename

    def process(self, today: datetime) -> dict:
        downloaded_files = {}
        datasets = self._configuration.get("datasets", {})

        for data_type, info in datasets.items():
            downloaded_files[data_type] = {}
            method = info.get("method", "wms")

            for layer_key, layer_dict in info["layers"].items():
                all_days = info["days"]
                if isinstance(all_days, int):
                    all_days = [all_days]
                for days in all_days:
                    start_date, end_date, date_str, time_desc, label, filename = (
                        self.get_metadata(info, today, days, layer_key)
                    )
                    if method == "wfs":
                        path, url = self._process_wfs(
                            layer_dict["endpoint"],
                            layer_dict["layer"],
                            date_str,
                            filename,
                            info["format"],
                        )
                    else:
                        path, url = self._process_wms(
                            layer_dict["endpoint"],
                            layer_dict["layer"],
                            date_str,
                            filename,
                            info["format"],
                        )
                    if path:
                        downloaded_files[data_type][label] = {
                            "path": path,
                            "start_date": start_date,
                            "end_date": end_date,
                            "layer_desc": layer_dict["description"],
                            "time_desc": time_desc.replace("_", " "),
                            "ext": info["ext"],
                            "download_url": url,
                        }

        return downloaded_files
