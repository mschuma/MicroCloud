#!/usr/bin/python

import os
from os.path import expanduser

from utilities import Utilities
from moduleprocessor import ModuleProcessor

__home__ = expanduser("~")
__existing_files__ = os.listdir(os.getcwd())
__module_processor__ = ModuleProcessor("download_config")
__module_processor__.install()
Utilities.cleanup(__existing_files__)
