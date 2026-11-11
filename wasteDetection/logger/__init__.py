import os
import sys
import logging
from datetime import datetime

# Create timestamp for current run
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")

# Create logs/<timestamp>/ directory
log_dir = os.path.join("logs", RUN_ID)

os.makedirs(log_dir, exist_ok=True)

# Log file inside the run folder
log_filepath = os.path.join(
    log_dir,
    f"{RUN_ID}.log"
)

logging_str = "[%(asctime)s: %(levelname)s: %(module)s: %(message)s]"

logging.basicConfig(
    level=logging.INFO,
    format=logging_str,
    handlers=[
        logging.FileHandler(log_filepath),
        logging.StreamHandler(sys.stdout)
    ]
)

logging = logging.getLogger("wasteDetectionLogger")

# logger.info("Logger initialized successfully.")