import logging
from datetime import datetime, timedelta
from pathlib import Path

from hdx.api.configuration import Configuration
from hdx.data.dataset import Dataset
from hdx.data.resource import Resource
from hdx.data.showcase import Showcase
from hdx.utilities.dateparse import default_date, default_enddate

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
        elif ext_lower == "geotiff":
            resource.set_format("geotiff")
        elif ext_lower == "zip":
            resource.set_format("zipped shapefile")

        resource.set_file_to_upload(file_path)
        return resource

    def generate_dataset_and_showcase(
        self, data_type: str, today: datetime
    ) -> tuple[Dataset, Showcase | None] | None:
        dataset_info = self._configuration["datasets"].get(data_type)
        if not dataset_info:
            return None

        logger.info(f"{data_type}: Generating dataset...")
        files = self._downloaded_files.get(data_type, {})

        if not files:
            logger.error(f"{data_type}: No data available!")
            return None

        min_start_date = default_enddate
        max_end_date = default_date
        for layer in iter(files.values()):
            start_date = layer["start_date"]
            if start_date < min_start_date:
                min_start_date = start_date
                url = layer["download_url"]
            end_date = layer["end_date"]
            if end_date > max_end_date:
                max_end_date = end_date
                url = layer["download_url"]
        start_date = min_start_date.strftime("%Y-%m-%d")
        end_date = max_end_date.strftime("%Y-%m-%d")
        logger.info(
            f"Using dates {start_date} to {end_date} for {data_type}. Example url {url}."
        )

        dataset = Dataset(
            {
                "name": dataset_info["name"],
                "title": dataset_info["title"],
                "notes": dataset_info.get("notes", ""),
            }
        )
        dataset.set_time_period(start_date, end_date)

        tags = dataset_info["tags"]
        dataset.add_tags(tags)
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
            elif ext.lower() == "geotiff":
                res_desc = f"GeoTIFF representing {layer_desc} {time_desc} {date_range}"
            else:
                res_desc = f"Data representing {layer_desc} {time_desc} {date_range}"

            dataset.add_update_resource(
                self.generate_resource(file_path.name, res_desc, file_path, ext)
            )

        showcase = None
        showcase_info = dataset_info.get("showcase")
        if showcase_info:
            forecast_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
            today_str = today.strftime("%Y-%m-%d")
            map_url = (
                "https://forest-fire.emergency.copernicus.eu/apps/effis.csv/"
                f"?c=373272.64,2379485.23&z=5&t=sentinel2&tiles="
                f"&forecastActive=true&sourceId=ecmwf&indexId=fdf.ecmwf007.fwi"
                f"&forecastDate={forecast_date}&rdaFrom={today_str}&rdaTo={forecast_date}"
                f"&rdaDateRange=today&layerInfoPoint&fdcPoint&fdcDate"
            )
            showcase = Showcase(
                {
                    "name": f"{dataset_info['name']}-showcase",
                    "title": f"{dataset_info['title']} Interactive Map",
                    "notes": showcase_info["notes"],
                    "url": map_url,
                    "image_url": showcase_info["image_url"],
                }
            )
            showcase.add_tags(tags)

        dataset.preview_off()
        return dataset, showcase
