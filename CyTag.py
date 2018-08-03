#!usr/bin/env python3
#-*- coding: utf-8 -*-
"""
'CyTag.py'

A surface-level natural language processing pipeline for Welsh texts (text segmentation -> sentence splitting -> tokenisation -> part-of-speech (POS) tagging).

CyTag can either process Welsh text via standard input, or accepts the following sequences of arguments:
	--- REQUIRED: A string of Welsh language text.
	or:
	--- REQUIRED: One or more Welsh input text files (raw text).
	--- OPTIONAL: A name to describe the corpus and its output files.
	--- OPTIONAL: A directory in which output files will be saved.
	--- OPTIONAL: A specific component to run the pipeline to, should running the entire pipeline not be required ('seg', 'sent', 'tok', 'pos').
	--- OPTIONAL: A format to write the pipeline's output to ('tsv', 'xml', 'vrt', 'db' or 'all')
	or:
	--- REQUIRED: 'evaluate'
	--- OPTIONAL: 'soft' (for a more lenient evaluation of CyTag output).
	--- REQUIRED: A gold standard (CyTag XML-formatted) dataset. 
	--- REQUIRED: XML-formatted CyTag output to be evaluated.

Developed at Cardiff University as part of the CorCenCC project (www.corcencc.org).

2016-2018 Steve Neale <steveneale3000@gmail.com, NealeS2@cardiff.ac.uk>, Kevin Donnelly <kevin@dotmon.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses>.
"""

import sys
import os

sys.path.insert(0, "{}/src/".format(os.path.dirname(os.path.abspath(__file__))))

import argparse

from cy_textsegmenter import *
from cy_sentencesplitter import *
from cy_tokeniser import *
from cy_postagger import *

#from evaluate_cytag import *

def process(input_text, output_name=None, directory=None, component=None, output_format=None):
	""" Process the input text/file(s) """
	if input_text == "" or input_text == []:
		raise ValueError("Input text must either be: a string, or; the names of one or more raw text files")
	elif component != None and component not in ["seg", "sent", "tok", "pos"]:
		raise ValueError("An invalid pipeline component ('{}') was given. Valid components: 'seg', 'sent', 'tok', 'pos'".format(component))
	elif output_format != None and output_format not in ["tsv", "xml", "all"]:
		raise ValueError("An invalid output format ('{}') was given. Valid formats: 'tsv', 'xml', 'all'".format(output_format))
	else:
		if [output_name, directory, component, output_format] == [None, None, None, None]:
			output = pos_tagger(input_text)
			print(output)
		else:
			if component != None:
				if component == "seg":
					pass#output = 
				elif component == "sent":
					pass#output = 
				elif component == "tok":
					output = tokeniser(input_text)
					print(output)
				elif component == "pos":
					output = pos_tagger(input_text, output_name, directory, output_format)
			else:
				output = pos_tagger(input_text, output_name, directory, output_format)

def parse_evaluation_arguments(arguments):
	""" Parse command line arguments (when evaluating CyTag) """
	parser = argparse.ArgumentParser(description="CyTag.py - A surface-level natural language processing pipeline for Welsh texts")
	optional = parser._action_groups.pop()
	required = parser.add_argument_group("required arguments")
	parser.add_argument("evaluate", help="Evaluate CyTag")
	required.add_argument("-g", "--gold", help="Gold standard (CyTag XML-formatted) dataset", required=True)
	required.add_argument("-c", "--cytag", help="XML-formatted CyTag output to be evaluated", required=True)
	optional.add_argument("-s", "--soft", help="'Softer' (more lenient) evaluation", action="store_true")
	parser._action_groups.append(optional)
	return(parser.parse_args())

def parse_processing_arguments(arguments):
	""" Parse command line arguments (when processing input files) """
	parser = argparse.ArgumentParser(description="CyTag.py - A surface-level natural language processing pipeline for Welsh texts")
	optional = parser._action_groups.pop()
	required = parser.add_argument_group("required arguments")
	required.add_argument("-i", "--input", help="Input file path(s)", nargs="+", required=True)
	optional.add_argument("-n", "--name", help="Output file name")
	optional.add_argument("-d", "--dir", help="Output directory")
	optional.add_argument("-c", "--component", help="Component to run the pipeline to ('seg', 'sent', 'tok', 'pos')")
	optional.add_argument("-f", "--format", help="Output file format ('tsv', 'xml', 'all')")
	parser._action_groups.append(optional)
	return(parser.parse_args())

if __name__ == "__main__":
	""" Process input (standard input, text as a string, or files) or evaluate CyTag """
	args = sys.argv[1:]
	if len(args) == 0 and not sys.stdin.isatty():
		process(input_text=sys.stdin.read())
	else:
		if args[0] == "evaluate":
			arguments = parse_evaluation_arguments(args)
			#evaluate(arguments.gold, arguments.cytag, soft_evaluation=arguments.soft)
		elif len(args) == 1 and os.path.isfile(args[0]) != True and args[0].startswith("-") != True:
			process(input_text=args[0])
		else:
			arguments = parse_processing_arguments(args)
			process(arguments.input, output_name=arguments.name, directory=arguments.dir, component=arguments.component, output_format=arguments.format)
