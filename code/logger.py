# Python code Read For Me which is dedicated to visualy impaired people
# to read A4 document, based on Raspberry PI.
# Copyright 2025 Read For Me
# Contributors: see AUTHORS file
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>
"""Logger configuration
"""
import logging
import sys
from constantes import DEBUG

logger = logging.getLogger()
handler = logging.FileHandler('debug.log')
if DEBUG:
    logger.setLevel(logging.INFO)
    handler.setLevel(logging.INFO)
else:
    logger.setLevel(logging.ERROR)
    handler.setLevel(logging.ERROR)

LOG_FORMAT = '%(asctime)-6s: %(name)s - %(levelname)s - %(message)s'
handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(handler)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(stream_handler)
