import time
import sys
import os
import argparse

PYTHON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(PYTHON_PATH)

from housinginsights.tools.logger import HILogger

logger = HILogger(name=__file__, logfile="ingestion.log")

for idx, value in enumerate(range(4)):
    logger.warning("Hi!")
    time.sleep(1)
