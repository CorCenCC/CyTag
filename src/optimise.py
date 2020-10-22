import sys
import os
import argparse
import re
import unicodedata2
import subprocess
import time
import json
import shutil

missing_libraries = []
try:
	from progress.bar import Bar
except ImportError:
	missing_libraries.append("progress")
try:
	from lxml import etree
except ImportError:
	missing_libraries.append("lxml")

from cy_textsegmenter import *
from cy_sentencesplitter import *
from cy_tokeniser import *
from shared.create_folders import *
from shared.load_gazetteers import *
from shared.load_lexicon import *
from shared.reference_lists import *

cy_lexicon = load_lexicon()

print(cy_lexicon)