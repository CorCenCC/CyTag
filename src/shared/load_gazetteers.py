#!usr/bin/env python3
#-*- coding: utf-8 -*-
"""
'load_gazetteers.py'

A script for loading Welsh gazetteers for use in CyTag.

Returns:
	--- A dictionary containing various gazetteers.

Developed at Cardiff University as part of the CorCenCC project (www.corcencc.org).

2016-2018 Steve Neale <steveneale3000@gmail.com, NealeS2@cardiff.ac.uk>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses>.
"""

import sys
import os

def load_gazetteers():
	""" Load Welsh gazetteers into a dictionary, and return it """
	gazetteers = {}
	for gaz in os.listdir("{}/../../cy_gazetteers".format(os.path.dirname(os.path.abspath(__file__)))):
		if gaz.rpartition(".")[-1] not in ["py", "json"] and gaz.startswith("._") == False: 
			with open("{}/../../cy_gazetteers/{}".format(os.path.dirname(os.path.abspath(__file__)), gaz), encoding="utf-8") as loaded_gazetteer:
				exclude_string = ""
				terms = loaded_gazetteer.read().splitlines()
				for term in terms:
					term = term.replace(".", "[.]")
					exclude_string = exclude_string + "(?<!" + term + ")"
				gaz_name, gaz_ext = os.path.splitext(gaz)
				gazetteers[gaz_ext[1:]] = terms
				gazetteers["{}_regex".format(gaz_ext[1:])] = exclude_string
	return(gazetteers)