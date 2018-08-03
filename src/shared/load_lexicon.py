#!usr/bin/env python3
#-*- coding: utf-8 -*-
"""
'load_lexicon.py'

A script for loading a CorCenCC-formatted Welsh lexicon.

Returns:
	--- A dictionary containing information from the CorCenCC lexicon.

Developed at Cardiff University as part of the CorCenCC project (www.corcencc.org).

2016-2018 Steve Neale <steveneale3000@gmail.com, NealeS2@cardiff.ac.uk>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses>.
"""

import sys
import os

def load_lexicon():
	""" Load Welsh lexical information into a dictionary, and return it """
	lexicon = {}
	with open("{}/../../lexicon/{}".format(os.path.dirname(os.path.abspath(__file__)), "corcencc_lexicon_2017-09-29"), encoding="utf-8") as loaded_lexicon:
		entries = loaded_lexicon.read().splitlines()
		for entry in entries:
			if entry[:1] != "#":
				entry_parts = entry.split("\t")
				if entry_parts[0] not in lexicon.keys():
					lexicon[entry_parts[0]] = [{"lemma": entry_parts[1], "lemma_en": entry_parts[2], "pos_basic": entry_parts[3], "pos_enriched": entry_parts[4]}]
				else:
					lexicon[entry_parts[0]].append({"lemma": entry_parts[1], "lemma_en": entry_parts[2], "pos_basic": entry_parts[3], "pos_enriched": entry_parts[4]})
	return(lexicon)					