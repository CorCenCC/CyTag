#!usr/bin/env python3
#-*- coding: utf-8 -*-
"""
'cy_sentencesplitter.py'

A sentence splitter for Welsh texts.

Accepts as arguments:
	--- REQUIRED: A string of Welsh language text.
	or:
	--- REQUIRED: One or more Welsh input text files (raw text).

Returns:
	--- A list of input text split into sentences (separated by file if files were passed)

Developed at Cardiff University as part of the CorCenCC project (www.corcencc.org).

2016-2018 Steve Neale <steveneale3000@gmail.com, NealeS2@cardiff.ac.uk>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses>.

"""

import sys
import os
import re

from cy_textsegmenter import segment_text
from shared.load_gazetteers import *


""" Load prerequisites """

gazetteers = load_gazetteers()


""" Primary functions """

def split_sentences(input_text):
	""" Split a string of text into sentences, and return them as a list """

	# Split the given input text into sentences based on a regex pattern - whitespace preceded by certain punctuation marks, but not by certain combinations of letters and punctuation marks or by any of the negative lookbehind assertions created for the 'abbreviations' gazetteer
	pattern = gazetteers["abbreviations_regex"] + r"(?<=[.|!|?])(?<!\s[A-Z][.])(?<![A-Z][.][A-Z][.])(?<![.]\s[.])(?<![.][.])[\s]"
	sentences = re.split(pattern, input_text)
	# Iterate through the split sentences
	k = 0
	while k < len(sentences):
		# If an empty sentence is encountered, delete it
		if sentences[k] == "":
			del sentences[k]
		else:
			# If this is not the last sentence...
			if k < len(sentences)-1:
				# If the next sentence splits according to the regex pattern...
				if re.match(pattern, sentences[k+1]):
					# Append the next sentence to the current one, and delete it
					sentences[k] = sentences[k] + sentences[k+1].strip()
					del sentences[k+1]
			k+=1
	return(sentences)

def sentence_splitter(input_data):
	""" Take an input string or a list of files, and return a list of sentences (file separated if applicable) """

	sentences = []
	# If a list of files was given as input data, loop through them
	if isinstance(input_data, list):
		for file_id, file in enumerate(input_data):
			# Create a list containing the file name, and an empty list to hold the sentences
			sentences.append([file, []])
			# Segment each file, and loop through its segments
			with open(file) as file_text:
				for segment in segment_text(file_text.read()):
					# Split each segment into sentences, and add them to appropriate file in the 'sentences' list
					sentences[file_id][1].append(split_sentences(segment))
	# If a string was given as input data, split it into segments, and then split each segment into a list of sentences
	elif isinstance(input_data, str):
		segments = segment_text(input_data.replace("\\n", "\n"))
		for segment in segments:
			sentences.append(split_sentences(segment))
	return(sentences)


""" Main function (called when 'cy_sentencesplitter.py' is run from the command line) """

if __name__ == "__main__":
	""" Run the sentence splitter, depending on whether a string or file(s) were given """
	
	args = sys.argv[1:]
	if len(args) == 1 and os.path.isfile(args[0]) != True:
		sentence_splitter(args[0])
	else:
		sentence_splitter(args)
