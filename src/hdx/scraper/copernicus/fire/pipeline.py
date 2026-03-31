import logging
from datetime import datetime, timedelta
from pathlib import Path

from hdx.api.configuration import Configuration
from hdx.data.dataset import Dataset
from hdx.data.resource import Resource
from hdx.utilities.dateparse import parse_date

logger = logging.getLogger(__name__)


class Pipeline:
    def __init__(self, configuration: Configuration, downloaded_files: dict):
        self._configuration = configuration
        self._downloaded_files = downloaded_files

    @staticmethod
    def generate_resource(
        resource_name: str, resource_description: str, file_path: Path, extension: str
    ) -> Resource:
        resource = Resource(
            {
                "name": resource_name,
                "description": resource_description,
            }
        )

        ext_lower = extension.lower()
        if ext_lower == "geojson":
            resource.set_format("geojson")
        elif ext_lower in ["tif", "tiff"]:
            resource.set_format("geotiff")
        elif ext_lower == "zip":
            resource.set_format("zipped shapefile")

        resource.set_file_to_upload(file_path)
        return resource

    def generate_dataset(
        self, data_type: str, today: datetime | None = None
    ) -> Dataset | None:
        if today is None:
            today = datetime.now()

        dataset_info = self._configuration["datasets"].get(data_type)
        if not dataset_info:
            return None

        logger.info(f"{data_type}: Generating dataset...")
        files = self._downloaded_files.get(data_type, {})

        if not files:
            logger.error(f"{data_type}: No data available!")
            return None

        dataset = Dataset(
            {
                "name": dataset_info["name"],
                "title": dataset_info["title"],
                "notes": dataset_info.get("notes", ""),
            }
        )

        start_date = today
        end_date = today

        if "windows" in dataset_info:
            max_window = max(dataset_info["windows"])
            start_date = today - timedelta(days=max_window)
        elif "forecast_days" in dataset_info:
            f_days = dataset_info["forecast_days"]
            max_f = max(f_days) if isinstance(f_days, list) else f_days
            end_date = today + timedelta(days=max_f)

        dataset.set_time_period(
            parse_date(start_date.strftime("%Y-%m-%d")),
            parse_date(end_date.strftime("%Y-%m-%d")),
        )

        dataset.add_tags(dataset_info.get("tags", []))
        dataset.set_subnational(True)
        dataset.add_other_location("world")

        for label, resource_info in files.items():
            file_path = resource_info["path"]
            res_start_date = resource_info["start_date"]
            res_end_date = resource_info["end_date"]
            layer_desc = resource_info["layer_desc"]
            time_desc = resource_info["time_desc"]
            ext = resource_info["ext"]

            start_str = res_start_date.strftime("%d %b %Y").lstrip("0")
            end_str = res_end_date.strftime("%d %b %Y").lstrip("0")
            date_range = (
                f"({start_str})" if start_str == end_str else f"({start_str}-{end_str})"
            )

            if ext.lower() == "geojson":
                res_desc = f"GeoJSON representing {layer_desc} {time_desc} {date_range}"
            elif ext.lower() in ["tif", "tiff"]:
                res_desc = f"GeoTIFF representing {layer_desc} {time_desc} {date_range}"
            else:
                res_desc = f"Data representing {layer_desc} {time_desc} {date_range}"

            dataset.add_update_resource(
                self.generate_resource(file_path.name, res_desc, file_path, ext)
            )

        return dataset
