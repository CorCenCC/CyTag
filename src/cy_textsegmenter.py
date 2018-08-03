#!usr/bin/env python3
#-*- coding: utf-8 -*-
"""
'cy_textsegmenter.py'

A text segmenter for Welsh texts.

Accepts as arguments:
	--- REQUIRED: A string of Welsh language text.
	or:
	--- REQUIRED: One or more Welsh input text files (raw text).

Returns:
	--- A list of input text split into segments (separated by file if files were passed)

Developed at Cardiff University as part of the CorCenCC project (www.corcencc.org).

2016-2018 Steve Neale <steveneale3000@gmail.com, NealeS2@cardiff.ac.uk>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses>.

"""

import sys
import os


""" Primary functions """

def segment_text(input_text):
	""" Split text into segments (lines), and return them as a list """
	
	segments = input_text.splitlines()
	return(segments)


def text_segmenter(input_data):
	""" Take an input string or a list of files, and return a list of segments (file separated if applicable) """
	
	segmented_text = []
	# If a list of files was given as input data, open each file and return a list containing a nested lists of segments for each file
	if isinstance(input_data, list):
		for file_id, file in enumerate(input_data):
			with open(file) as file_text:
				segmented_text.append([file, segment_text(file_text.read())])
	# If a string was given as input data, return it as a list of segments (lines)
	elif isinstance(input_data, str):
		segmented_text = segment_text(input_data.replace("\\n", "\n"))
	return(segmented_text)


""" Main function (called when 'cy_textsegmenter.py' is run from the command line) """

if __name__ == "__main__":
	""" Run the text segmenter, depending on whether a string or file(s) were given """
	
	args = sys.argv[1:]
	if len(args) == 1 and os.path.isfile(args[0]) != True:
		segment_text(args[0])
	else:
		segment_text(args)