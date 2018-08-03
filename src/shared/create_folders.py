#!usr/bin/env python3
#-*- coding: utf-8 -*-
"""
'create_folders.py'

Create the necessary folders for storing CyTag output.

Developed at Cardiff University as part of the CorCenCC project (www.corcencc.org).

2016-2018 Steve Neale <steveneale3000@gmail.com, NealeS2@cardiff.ac.uk>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses>.
"""

import sys
import os

def create_folders(output_name, directory):
	""" Given an output name and a directory name, create the necessary folders to store CyTag output """
	directory = output_name if directory == None else directory
	if not os.path.exists("{}/../../{}/{}".format(os.path.dirname(os.path.abspath(__file__)), "outputs", directory)):
		os.makedirs("{}/../../{}/{}".format(os.path.dirname(os.path.abspath(__file__)), "outputs", directory))