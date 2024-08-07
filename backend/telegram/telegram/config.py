import yaml
import os
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s|%(levelname)s|%(message)s", level=logging.INFO)

YAML = dict()
for file_name in os.listdir("./../configs/"):
    if ".dockerignore" not in file_name and "src" not in file_name:
        file_path = os.path.join("./../configs", file_name)
        file_name = file_name.replace(".yaml", "")
        YAML[file_name] = yaml.safe_load(open(file_path))
        logger.info(f"Reading config: {file_path}")
        logger.info(f"{YAML[file_name]}")
logger.info(f"YAML YAML: {YAML}")
