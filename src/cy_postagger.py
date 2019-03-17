#!usr/bin/env python3
#-*- coding: utf-8 -*-
"""
'cy_postagger.py'

A part-of-speech (POS) tagger for Welsh texts.

Accepts as arguments:
	--- REQUIRED: A string of Welsh language text.
	or:
	--- REQUIRED: One or more Welsh input text files (raw text).
	--- OPTIONAL: A name to describe the corpus and its output files.
	--- OPTIONAL: A directory in which output files will be saved.
	--- OPTIONAL: A flag ('print') to let cy_postagger know whether to write CG-formatted readings files to the output folder or not.

Returns:
	--- POS tagged tokens as tab-separated values

Developed at Cardiff University as part of the CorCenCC project (www.corcencc.org).

2016-2018 Steve Neale <steveneale3000@gmail.com, NealeS2@cardiff.ac.uk>, Kevin Donnelly <kevin@dotmon.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses>.
"""

import sys
import os
import argparse
import re
import subprocess
import time
import json

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

stats = {"pre-cg": 
			{"untagged": 0, "definite_tag": 0, "with_readings": 0, "single_reading": 0, "multiple_readings": 0, "without_readings": 0, "no_readings": 0, "assumed_proper": 0},
		 "post-cg":
		 	{"one_reading": 0, "multiple_readings": 0, "unknown": 0, "disambiguated": 0, "unknown_gazetteer": 0, "pns_gazetteer": 0, "neutral_pns": 0, "same_tag": 0, "in_coverage": 0, "ambiguous_gazetteer": 0, "undisambiguated": 0, "still_ambiguous": 0}
		}

pre_cg_reading_counts = {}

output = {"directory": None, "readings": None, "readingsPostCG": None, "unknown_words": None, "tsv": None, "xml": None, "tree": None}

sentence_lengths = []

vislcg3_location = subprocess.Popen(["which", "vislcg3"], stdout=subprocess.PIPE).communicate()[0].strip()

existing_unknown_words = []
new_unknown_words = []

gazetteers = load_gazetteers()
cy_lexicon = load_lexicon()

contractions_and_prefixes = {}
with open("{}/../cy_gazetteers/contractions_and_prefixes.json".format(os.path.dirname(os.path.abspath(__file__)))) as contractionsprefixes_json:
	contractions_and_prefixes = json.load(contractionsprefixes_json)

""" A simple swith to use the 'check_coverage' options when tagging (i.e. guess untagged words using entries in the tag-token coverage and tag-sequence dictionaries)
	--- NOTE: Leave this as True, unless producing tagged output for making new tag-token coverage and tag-sequence dictionaries
"""
check_coverage = True
#check_coverage = False

""" Load the CyTag tag-token coverage dictionary from an external .json file """
cy_coverage = {}
with open("{}/../lexicon/{}".format(os.path.dirname(os.path.abspath(__file__)), "CyTag_tag-token_coverage")) as coverage_file:
	cy_coverage = json.load(coverage_file)

""" The appropriate rich POS tags that collapse into each basic POS tag """
tag_categories = [["E", ["Egu", "Ebu", "Egll", "Ebll", "Egbu", "Egbll", "Ep", "Epg", "Epb"]],
					["Ar", ["Arsym", "Ar1u", "Ar2u", "Ar3gu", "Ar3bu", "Ar1ll", "Ar2ll", "Ar3ll"]],
					["Cys", ["Cyscyd", "Cysis"]],
					["Rhi", ["Rhifol", "Rhifold", "Rhifolt", "Rhitref", "Rhitrefd", "Rhitreft"]],
					["Ans", ["Anscadu", "Anscadbu", "Anscadll", "Anscyf", "Anscym", "Anseith"]],
					["B", ["Be", "Bpres1u", "Bpres2u", "Bpres3u", "Bpres1ll", "Bpres2ll", "Bpres3ll", "Bpresamhers", "Bpres3perth", "Bpres3amhen",
							"Bdyf1u", "Bdyf2u", "Bdyf3u", "Bdyf1ll", "Bdyf2ll", "Bdyf3ll", "Bdyfamhers",
							"Bgorb1u", "Bgorb2u", "Bgorb3u", "Bgorb1ll", "Bgorb2ll", "Bgorb3ll", "Bgorbamhers",
							"Bamherff1u", "Bamherff2u", "Bamherff3u", "Bamherff1ll", "Bamherff2ll", "Bamherff3ll", "Bamherffamhers",
							"Bgorff1u", "Bgorff2u", "Bgorff3u", "Bgorff1ll", "Bgorff2ll", "Bgorff3ll", "Bgorffamhers", "Bgorffsef",
							"Bgorch2u", "Bgorch3u", "Bgorch1ll", "Bgorch2ll", "Bgorch3ll", "Bgorchamhers",
							"Bdibdyf1u", "Bdibdyf2u", "Bdibdyf3u", "Bdibdyf1ll", "Bdibdyf2ll", "Bdibdyf3ll", "Bdibdyfamhers",
							"Bamod1u", "Bamod2u", "Bamod3u", "Bamod1ll", "Bamod2ll", "Bamod3ll", "Bamodamhers"]],
					["Rha", ["Rhapers1u", "Rhapers2u", "Rhapers3gu", "Rhapers3bu", "Rhapers1ll", "Rhapers2ll", "Rhapers3ll",
							"Rhadib1u", "Rhadib2u", "Rhadib3gu", "Rhadib3bu", "Rhadib1ll", "Rhadib2ll", "Rhadib3ll",
							"Rhamedd1u", "Rhamedd2u", "Rhamedd3gu", "Rhamedd3bu", "Rhamedd1ll", "Rhamedd2ll", "Rhamedd3ll",
							"Rhacys1u", "Rhacys2u", "Rhacys3gu", "Rhacys3bu", "Rhacys1ll", "Rhacys2ll", "Rhacys3ll",
							"Rhagof", "Rhadangg", "Rhadangb", "Rhadangd", "Rhaperth", "Rhaatb", "Rhacil"]],
					["U", ["U", "Uneg", "Ucad", "Ugof", "Utra", "Uberf"]],
					["Gw", ["Gwest", "Gwfform", "Gwsym", "Gwacr", "Gwtalf", "Gwdig", "Gwllyth", "Gwann"]],
					["Atd", ["Atdt", "Atdcan", "Atdchw", "Atdde", "Atdcys", "Atddyf"]],
					["YFB", ["YFB"]],
					["Adf", ["Adf"]],
					["Ebych", ["Ebych"]]]

""" The morphological elements that make up each rich POS tag """
morphological_table = [["Egu", ["E", "g", "u"]],
						["Ebu", ["E", "b", "u"]],
						["Egll", ["E", "g", "ll"]],
						["Ebll", ["E", "b", "ll"]],
						["Egbu", ["E", "gb", "u"]],
						["Egbll", ["E", "gb", "ll"]],
						["Ep", ["E", "p"]],
						["Epg", ["E", "p", "g"]],
						["Epb", ["E", "p", "b"]],
						["Arsym", ["Ar", "sym"]],
						["Ar1u", ["Ar", "1", "u"]],
						["Ar2u", ["Ar", "2", "u"]],
						["Ar3gu", ["Ar", "3", "g", "u"]],
						["Ar3bu", ["Ar", "3", "b", "u"]],
						["Ar1ll", ["Ar", "1", "ll"]],
						["Ar2ll", ["Ar", "2", "ll"]],
						["Ar3ll", ["Ar", "3", "ll"]],
						["Cyscyd", ["Cys", "cyd"]],
						["Cysis", ["Cys", "is"]],
						["Rhifol", ["Rhi", "fol"]],
						["Rhifold", ["Rhi", "fol", "d"]],
						["Rhifolt", ["Rhi", "fol", "t"]],
						["Rhitref", ["Rhi", "tref"]],
						["Rhitrefd", ["Rhi", "tref", "d"]],
						["Rhitreft", ["Rhi", "tref", "t"]],
						["Anscadu", ["Ans", "cad", "u"]],
						["Anscadbu", ["Ans", "cad", "b", "u"]],
						["Anscadll", ["Ans", "cad", "ll"]],
						["Anscyf", ["Ans", "cyf"]],
						["Anscym", ["Ans", "cym"]],
						["Anseith", ["Ans", "eith"]],
						["Be", ["B", "e"]],
						["Bpres1u", ["B", "pres", "1", "u"]],
						["Bpres2u", ["B", "pres", "2", "u"]],
						["Bpres3u", ["B", "pres", "3", "u"]],
						["Bpres1ll", ["B", "pres", "1", "ll"]],
						["Bpres2ll", ["B", "pres", "2", "ll"]],
						["Bpres3ll", ["B", "pres", "3", "ll"]],
						["Bpresamhers", ["B", "pres", "amhers"]],
						["Bpres3perth", ["B", "pres", "3", "perth"]],
						["Bpres3amhen", ["B", "pres", "3", "amhen"]],
						["Bdyf1u", ["B", "dyf", "1", "u"]],
						["Bdyf2u", ["B", "dyf", "2", "u"]],
						["Bdyf3u", ["B", "dyf", "3", "u"]],
						["Bdyf1ll", ["B", "dyf", "1", "ll"]],
						["Bdyf2ll", ["B", "dyf", "2", "ll"]],
						["Bdyf3ll", ["B", "dyf", "3", "ll"]],
						["Bdyfamhers", ["B", "dyf", "amhers"]],
						["Bgorb1u", ["B", "gorb", "1", "u"]],
						["Bgorb2u", ["B", "gorb", "2", "u"]],
						["Bgorb3u", ["B", "gorb", "3", "u"]],
						["Bgorb1ll", ["B", "gorb", "1", "ll"]],
						["Bgorb2ll", ["B", "gorb", "2", "ll"]],
						["Bgorb3ll", ["B", "gorb", "3", "ll"]],
						["Bgorbamhers", ["B", "gorb", "amhers"]],
						["Bamherff1u", ["B", "amherff", "1", "u"]],
						["Bamherff2u", ["B", "amherff", "2", "u"]],
						["Bamherff3u", ["B", "amherff", "3", "u"]],
						["Bamherff1ll", ["B", "amherff", "1", "ll"]],
						["Bamherff2ll", ["B", "amherff", "2", "ll"]],
						["Bamherff3ll", ["B", "amherff", "3", "ll"]],
						["Bamherffamhers", ["B", "amherff", "amhers"]],
						["Bgorff1u", ["B", "gorff", "1", "u"]],
						["Bgorff2u", ["B", "gorff", "2", "u"]],
						["Bgorff3u", ["B", "gorff", "3", "u"]],
						["Bgorff1ll", ["B", "gorff", "1", "ll"]],
						["Bgorff2ll", ["B", "gorff", "2", "ll"]],
						["Bgorff3ll", ["B", "gorff", "3", "ll"]],
						["Bgorffamhers", ["B", "gorff", "amhers"]],
						["Bgorffsef", ["B", "gorch", "sef"]],
						["Bgorch2u", ["B", "gorch", "2", "u"]],
						["Bgorch3u", ["B", "gorch", "3", "u"]],
						["Bgorch1ll", ["B", "gorch", "1", "ll"]],
						["Bgorch2ll", ["B", "gorch", "2", "ll"]],
						["Bgorch3ll", ["B", "gorch", "3", "ll"]],
						["Bgorchamhers", ["B", "gorch", "amhers"]],
						["Bdibdyf1u", ["B", "dibdyf", "1", "u"]],
						["Bdibdyf2u", ["B", "dibdyf", "2", "u"]],
						["Bdibdyf3u", ["B", "dibdyf", "3", "u"]],
						["Bdibdyf1ll", ["B", "dibdyf", "1", "ll"]],
						["Bdibdyf2ll", ["B", "dibdyf", "2", "ll"]],
						["Bdibdyf3ll", ["B", "dibdyf", "3", "ll"]],
						["Bdibdyfamhers", ["B", "dibdyf", "amhers"]],
						["Bamod1u", ["B", "amod", "1", "u"]],
						["Bamod2u", ["B", "amod", "2", "u"]],
						["Bamod3u", ["B", "amod", "3", "u"]],
						["Bamod1ll", ["B", "amod", "1", "ll"]],
						["Bamod2ll", ["B", "amod", "2", "ll"]],
						["Bamod3ll", ["B", "amod", "3", "ll"]],
						["Bamodamhers", ["B", "amod", "amhers"]],
						["Rhapers1u", ["Rha", "pers", "1", "u"]],
						["Rhapers2u", ["Rha", "pers", "2", "u"]],
						["Rhapers3gu", ["Rha", "pers", "3", "g", "u"]],
						["Rhapers3bu", ["Rha", "pers", "3", "b", "u"]],
						["Rhapers1ll", ["Rha", "pers", "1", "ll"]],
						["Rhapers2ll", ["Rha", "pers", "2", "ll"]],
						["Rhapers3ll", ["Rha", "pers", "3", "ll"]],
						["Rhadib1u", ["Rha", "dib", "1", "u"]],
						["Rhadib2u", ["Rha", "dib", "2", "u"]],
						["Rhadib3gu", ["Rha", "dib", "3", "g", "u"]],
						["Rhadib3bu", ["Rha", "dib", "3", "b", "u"]],
						["Rhadib1ll", ["Rha", "dib", "1", "ll"]],
						["Rhadib2ll", ["Rha", "dib", "2", "ll"]],
						["Rhadib3ll", ["Rha", "dib", "3", "ll"]],
						["Rhamedd1u", ["Rha", "medd", "1", "u"]],
						["Rhamedd2u", ["Rha", "medd", "2", "u"]],
						["Rhamedd3gu", ["Rha", "medd", "3", "g", "u"]],
						["Rhamedd3bu", ["Rha", "medd", "3", "b", "u"]],
						["Rhamedd1ll", ["Rha", "medd", "1", "ll"]],
						["Rhamedd2ll", ["Rha", "medd", "2", "ll"]],
						["Rhamedd3ll", ["Rha", "medd", "3", "ll"]],
						["Rhacys1u", ["Rha", "cys", "1", "u"]],
						["Rhacys2u", ["Rha", "cys", "2", "u"]],
						["Rhacys3gu", ["Rha", "cys", "3", "g", "u"]],
						["Rhacys3bu", ["Rha", "cys", "3", "b", "u"]],
						["Rhacys1ll", ["Rha", "cys", "1", "ll"]],
						["Rhacys2ll", ["Rha", "cys", "2", "ll"]],
						["Rhacys3ll", ["Rha", "cys", "3", "ll"]],
						["Rhagof", ["Rha", "gof"]],
						["Rhadangg", ["Rha", "dang", "g"]],
						["Rhadangb", ["Rha", "dang", "b"]],
						["Rhadangd", ["Rha", "dang", "d"]],
						["Rhaperth", ["Rha", "perth"]],
						["Rhaatb", ["Rha", "atb"]],
						["Rhacil", ["Rha", "cil"]],
						["Uneg", ["U", "neg"]],
						["Ucad", ["U", "cad"]],
						["Ugof", ["U", "gof"]],
						["Utra", ["U", "tra"]],
						["Uberf", ["U", "berf"]],
						["Gwest", ["Gw", "est"]],
						["Gwfform", ["Gw", "fform"]],
						["Gwsym", ["Gw", "sym"]],
						["Gwacr", ["Gw", "acr"]],
						["Gwtalf", ["Gw", "talf"]],
						["Gwdig", ["Gw", "dig"]],
						["Gwllyth", ["Gw", "llyth"]],
						["Gwann", ["Gw", "ann"]],
						["Atdt", ["Atd", "t"]],
						["Atdcan", ["Atd", "can"]],
						["Atdchw", ["Atd", "chw"]],
						["Atdde", ["Atd", "de"]],
						["Atdcys", ["Atd", "cys"]],
						["Atdyf", ["Atd", "dyf"]]]

def find_definite_tags(token):
	""" Find and return definitely identifiable tags for a token, including:
		--- punctuation
		--- symbols
		--- digits
		--- acronynms or abbreviations (from gazetteers)
	"""
	pos = ""
	if re.match(r"[.,:;\"\'!?\-\—<>{}\[\]()]", token):
		if re.match(r"[.!?]", token):
			pos = "Atd:Atdt"
		if re.match(r"[,;:—]", token):
			pos = "Atd:Atdcan"
		if re.match(r"[<{\[(]", token):
			pos = "Atd:Atdchw"
		if re.match(r"[>}\])]", token):
			pos = "Atd:Atdde"
		if token is "-":
			pos = "Atd:Atdcys"
		if token is "\'" or token is "\"":
			pos = "Atd:Atdyf"	
	if re.match(r"[^\s^.,:;!?\-\—\'\"<>{}\[\]()^\w]", token):
		pos = "Gw:Gwsym"
	if re.match(r"^-?[0-9]+$", token):
		pos = "Gw:Gwdig"
	if pos == "" and token in gazetteers["acronyms"]:
		pos = "Gw:Gwacr"
	if pos == "" and token.lower() in gazetteers["abbreviations"]:
		pos = "Gw:Gwtalf"
	return pos

def lookup_readings(token):
	""" Lookup readings for a given token in the lexicon, and return them """
	readings = []
	if token in cy_lexicon:
		readings = [[token, [tag_morphology(x["pos_enriched"])], x["lemma"], [x["lemma_en"]], ""] for x in cy_lexicon[token]]
	elif token.lower() in cy_lexicon:
		readings = [[token.lower(), [tag_morphology(x["pos_enriched"])], x["lemma"], [x["lemma_en"]], ""] for x in cy_lexicon[token.lower()]]
	possible_mutations = lookup_mutation(token)
	if len(possible_mutations) > 0:
		for mutation in possible_mutations:
			if mutation[0] in cy_lexicon:
				mutation_readings = [[mutation[0], [tag_morphology(x["pos_enriched"])], x["lemma"], [x["lemma_en"]], mutation[1]] for x in cy_lexicon[mutation[0]]]
				readings = readings + mutation_readings
	return readings

def lookup_multiple_readings(tokens):
	""" Lookup readings for multiple tokens in the lexicon at the same time, and return them """
	readings = []
	for token in tokens:
		if token in cy_lexicon:
			readings = readings + [[token, [x["pos_enriched"]], x["lemma"], [x["lemma_en"]], ""] for x in cy_lexicon[token]]
		elif token.lower() in cy_lexicon:
			readings = readings + [[token.lower(), [x["pos_enriched"]], x["lemma"], [x["lemma_en"]], ""] for x in cy_lexicon[token.lower()]]
		possible_mutations = lookup_mutation(token) # NOTE - It looks like this needs finishing, nothing appears to be done with the list of possible mutations...
	return(readings)

def lookup_mutation(input_token):
	""" Return a list of all possible Welsh mutations of a given token """
	token = input_token.lower()
	unmutated = []
	if token[:2] == "ch":
		unmutated.append(("c{}".format(token[2:]), "am"))
	if token[:2] == "ph":
		unmutated.append(("p{}".format(token[2:]), "am"))
	if token[:2] == "th":
		unmutated.append(("t{}".format(token[2:]), "am"))
	if token[:3] == "ngh":
		unmutated.append(("c{}".format(token[3:]), "nm"))
	if token[:2] == "mh":
		unmutated.append(("p{}".format(token[2:]), "nm"))
	if token[:2] == "nh":
		unmutated.append(("t{}".format(token[2:]), "nm"))
	if token[:2] == "ng":
		unmutated.append(("g{}".format(token[2:]), "nm"))
	if token[:1] == "m":
		unmutated.append(("b{}".format(token[1:]), "nm"))
	if token[:1] == "n":
		unmutated.append(("d{}".format(token[1:]), "nm"))
	if token[:1] == "g":
		unmutated.append(("c{}".format(token[1:]), "sm"))
	if token[:1] == "b":
		unmutated.append(("p{}".format(token[1:]), "sm"))
	if token[:1] == "d":
		unmutated.append(("t{}".format(token[1:]), "sm"))
	if token[:1] == "f":
		unmutated.append(("b{}".format(token[1:]), "sm"))
		unmutated.append(("m{}".format(token[1:]), "sm"))
	if token[:1] == "l":
		unmutated.append(("ll{}".format(token[1:]), "sm"))
	if token[:1] == "r":
		unmutated.append(("rh{}".format(token[1:]), "sm"))
	if token[:2] == "dd":
		unmutated.append(("d{}".format(token[2:]), "sm"))
	if token[:2] == "ha":
		unmutated.append(("a{}".format(token[2:]), "hm"))
	if token[:2] == "he":
		unmutated.append(("e{}".format(token[2:]), "hm"))
	if token[:2] == "hi":
		unmutated.append(("i{}".format(token[2:]), "hm"))
	if token[:2] == "ho":
		unmutated.append(("o{}".format(token[2:]), "hm"))
	if token[:2] == "hu":
		unmutated.append(("u{}".format(token[2:]), "hm"))
	if token[:2] == "hw":
		unmutated.append(("w{}".format(token[2:]), "hm"))
	if token[:2] == "hy" and token != "hyn":
		unmutated.append(("y{}".format(token[2:]), "hm"))
	unmutated.append(("g{}".format(token), "sm"))
	if input_token[0].isupper():
		capitals = []
		for mutation in unmutated:
			capitals.append(("{}{}".format(mutation[0][:1].upper(), mutation[0][1:]), mutation[1]))
		unmutated = unmutated + capitals
	return(unmutated)

def tag_morphology(tag):
	""" For a given (rich) POS tag, split it into a list of its morphological elements and return it """
	morphology = []
	if tag in [x[0] for x in morphological_table]:
		location = [x[0] for x in morphological_table].index(tag)
		morphology = morphological_table[location][1]
	else:
		morphology = [tag]
	return morphology

def format_en_lemmas(lemmas):
	""" Format a list of English lemmas as a string can be included as part of a single Welsh CG reading """
	en_lemma_string = ""
	formatted_lemmas = []
	for lemma in lemmas:
		formatted_lemmas.append(":{}:".format(lemma.replace(" ", "_")))
	en_lemma_string = " ".join(formatted_lemmas)
	return en_lemma_string

def format_multireading_lookup(readings, token, token_position):
	""" Format the results of a multi-reading lookup as the 'contents' string(s) of a single Welsh CG reading """
	reading_string = ""
	if len(readings) > 0:
		for reading in readings:
			en_lemmas = format_en_lemmas(reading[3])
			morphology = tag_morphology(reading[1][0])
			tags = " ".join(tag_morphology(reading[1][0]))
			reading_string += "\t\"{}\" {{{}}} [cy] {} {}\n".format(reading[2], token_position, tags, en_lemmas)
		stats["pre-cg"]["with_readings"] += 1
	else:
		reading_string += "\t\"{}\" {{{}}} {}\n".format(token, token_position, "unk")
		stats["pre-cg"]["without_readings"] += 1
	return(reading_string)

def handle_empty_lookup(token):
	""" Produce readings for tokens that didn't return anything during a regular lookup, focusing on:
		---	Tokens that are capitalised (that we assume to be proper nouns)
		--- Tokens that we know to be common contractions
		--- Tokens that end with an apostrophe (last letter may have been cut off)
		--- Tokens that end in a vowel (and may have had 'f' cut off the end)
		--- Tokens that end in a consonant (and may have had 'r' or 'l' cut off the end)
	"""
	count_readings = False
	reading_string = "" 
	if token[0][0].isupper():
		reading_string += "\t\"{}\" {{{}}} [cy] {} :{}:\n".format(token[0], token[1], "E p g", token[0])
		reading_string += "\t\"{}\" {{{}}} [cy] {} :{}:\n".format(token[0], token[1], "E p b", token[0])
		stats["pre-cg"]["with_readings"] += 1
		stats["pre-cg"]["assumed_proper"] += 1
	elif token[0] in contractions_and_prefixes.keys():
		if contractions_and_prefixes[token[0]][0] == "contraction":
			readings = lookup_multiple_readings(contractions_and_prefixes[token[0]][1])						
			reading_string += format_multireading_lookup(readings, token[0], token[1])
			if len(readings) > 0:
				count_readings = True
	elif token[0][-1:] == "'":
		readings = lookup_multiple_readings(["{}f".format(token[0][:-1]), "{}r".format(token[0][:-1]), "{}l".format(token[0][:-1])])
		reading_string += format_multireading_lookup(readings, token[0], token[1])
		if len(readings) > 0:
			count_readings = True
	elif token[0][-1:] in ["a", "â", "e", "ê", "i", "î", "o", "ô", "u", "û", "w", "ŵ", "y", "ŷ"]:
		readings = lookup_multiple_readings(["{}f".format(token[0])])
		reading_string += format_multireading_lookup(readings, token[0], token[1])
		if len(readings) > 0:
			count_readings = True
	elif token[0][-1:] in ["b", "c", "d", "f", "g", "h", "j", "l", "m", "n", "p", "r", "s", "t"] or token[0][-2:] in ["ch", "dd", "ff", "ng", "ll", "ph", "rh", "th"]:
		readings = lookup_multiple_readings(["{}r".format(token[0]), "{}l".format(token[0])])
		reading_string += format_multireading_lookup(readings, token[0], token[1])
		if len(readings) > 0:
			count_readings = True
	else:
		reading_string += "\t\"{}\" {{{}}} {}\n".format(token[0], token[1], "unk")
		stats["pre-cg"]["without_readings"] += 1
	return(reading_string, count_readings)

def get_reading(token_id, token):
	""" Get CG-formatted readings for a given token """
	readings_string = ""
	readings = []
	pos = find_definite_tags(token[0])
	if pos != "" and (pos[:pos.index(":")] == "Atd" or pos[pos.index(":")+1:] in ["Gwsym", "Gwdig", "Gwacr", "Gwtalf"]):
		readings.append("definite")
		readings_string = "\"<{}>\"\n\t\"{}\" {{{}}} [cy] {} :{}:\n".format(token[0], token[0], token[1], " ".join(tag_morphology(pos[pos.index(":")+1:])), token[0])
		stats["pre-cg"]["with_readings"] += 1
		stats["pre-cg"]["definite_tag"] += 1
	else:
		readings_string += "\"<{}>\"\n".format(token[0])
		readings = lookup_readings(token[0])
		if len(readings) == 0:
			empty_lookup, count_readings  = handle_empty_lookup(token)
			if empty_lookup != "":
				readings_string += empty_lookup
				if count_readings == True:
					readings.append(["empty" for x in empty_lookup.splitlines() if x != ""])
		else:
			to_remove = []
			for reading_id, reading in enumerate(readings):
				if reading_id > 0 and (reading[0].lower() == readings[reading_id-1][0].lower()) and (reading[1] == readings[reading_id-1][1]) and (reading[2] == readings[reading_id-1][2]) and (reading[3] != readings[reading_id-1][3]):
					readings[reading_id-1][3].append(reading[3][0])
					to_remove.append(reading_id)
			to_remove.reverse()
			if len(to_remove) > 0:
				for index in to_remove:
					del readings[index]
			for reading in readings:
				en_lemmas = format_en_lemmas(reading[3])
				tags = " ".join(reading[1][0])
				mutation_desc = " + {}".format(reading[4]) if reading[4] != "" else ""
				readings_string += "\t\"{}\" {{{}}} [cy] {} {}{}\n".format(reading[2], token[1], tags, en_lemmas, mutation_desc)
			stats["pre-cg"]["with_readings"] += 1
	if len(readings) == 1:
		stats["pre-cg"]["single_reading"] += 1
	if len(readings) > 1:
		stats["pre-cg"]["multiple_readings"] += 1
	if len(readings) == 0:
		stats["pre-cg"]["no_readings"] += 1
	pre_cg_reading_counts[token_id] = len(readings)
	return(readings_string)

def check_gazetteers(token):
	""" Check whether a given token is present in the CyTag gazetteers """
	tags = []
	if token in gazetteers["givennames_m"] or token in gazetteers["givennames_f"] or token in gazetteers["surnames"] or token in gazetteers["places"]:
		tags.append("E")
		if token in gazetteers["givennames_m"] and token not in gazetteers["givennames_f"]:
			tags.append("Epg")
		elif token in gazetteers["givennames_f"] and token not in gazetteers["givennames_m"]:
			tags.append("Epb")
		elif token in gazetteers["givennames_f"] and token in gazetteers["givennames_m"]:
			tags.append("Ep")
		elif token in gazetteers["surnames"] or token in gazetteers["places"]:
			tags.append("Ep")
	else:
		tags = ["unk", "unk"]
	return(tags)

def list_readings(readings):
	""" Convert readings in string (VISL CG-3 output) format to a list of reading and their component parts """
	processed_readings = []
	for reading in readings:
		for lemma in re.findall(r'\"(.+?)\"', reading):
			reading = reading.replace(lemma, lemma.replace(" ", "_"))
		mutation = None
		info = re.split(r"\s+", reading.strip())
		if info[-2] == "+":
			mutation = "\t+{}".format(info[-1])
			info = info[:-2]
		i = len(info)-1
		while len(info[i]) > 1 and info[i][:1] == ":" and info[i][-1:] == ":":
			info = info[:-1]
			i = i - 1
		pos_tag = " ".join(info[3:])
		processed_readings.append([info[1][1:-1], info[0][1:-1], pos_tag, mutation])
	return(processed_readings)

def process_still_ambiguous(token_id, token, readings, token_position):
	""" Return an appropriate string of tab-separated values for a token that couldn't be disambiguated """
	processed_readings = list_readings(readings)
	possible_lemmas = [x[1].replace("_", " ") for x in processed_readings]
	possible_tags = [x[2].replace(" ", "") for x in processed_readings]
	possible_basics = []
	for tag in possible_tags:
		basic = [x[0] for x in tag_categories if tag in x[1]][0] if len([x[0] for x in tag_categories if tag in x[1]]) > 0 else tag
		possible_basics.append(basic)
	processed_token = "{}\t{}\t{}\t{}\t{}\t{}\t".format(token_id, token, processed_readings[0][0], " | ".join(possible_lemmas), " | ".join(possible_basics), " | ".join(possible_tags))
	return(processed_token)

def process_multiple_reading(token_id, token, readings):
	""" Return a token with a single reading as a string of tab-separated values """
	processed_token = ""
	processed_readings = list_readings(readings)
	position, lemma = processed_readings[0][0], processed_readings[0][1].replace("_", " ")
	checked_tags = check_gazetteers(token)
	if checked_tags != ["unk", "unk"]:
		processed_token = "{}\t{}\t{}\t{}\t{}\t{}\t".format(token_id, token, position, lemma, checked_tags[0], checked_tags[1])
		stats["post-cg"]["disambiguated"] += 1
		stats["post-cg"]["ambiguous_gazetteer"] += 1
	else:
		if check_coverage == True:
			if token in cy_coverage.keys():
				tags = cy_coverage[token].split(":")
				processed_token = "{}\t{}\t{}\t{}\t{}\t{}\t".format(token_id, token, position, lemma, tags[0], tags[1])
				stats["post-cg"]["disambiguated"] += 1
				stats["post-cg"]["in_coverage"] += 1
			else:
				stats["post-cg"]["undisambiguated"] += 1
				stats["post-cg"]["still_ambiguous"] += 1
		else:
			stats["post-cg"]["undisambiguated"] += 1
			stats["post-cg"]["still_ambiguous"] += 1
	return(processed_token)

def process_double_reading(token_id, token, readings):
	""" Return a token that has two readings as a string of tab-separated values """
	processed_token = ""
	processed_readings = list_readings(readings)
	position, lemma = processed_readings[0][0], processed_readings[0][1].replace("_", " ")
	if "E p b" in [x[2] for x in processed_readings] and "E p g" in [x[2] for x in processed_readings]:
		checked_tags = check_gazetteers(token)
		if checked_tags == ["unk", "unk"]:
			processed_token = "{}\t{}\t{}\t{}\tE\tEp\t".format(token_id, token, position, lemma)
			stats["post-cg"]["neutral_pns"] += 1
			stats["post-cg"]["disambiguated"] += 1
		else:
			processed_token = "{}\t{}\t{}\t{}\t{}\t{}\t".format(token_id, token, position, lemma, checked_tags[0], checked_tags[1])
			stats["post-cg"]["disambiguated"] += 1
			stats["post-cg"]["pns_gazetteer"] += 1
	elif [x[2] for x in processed_readings][0] == [x[2] for x in processed_readings][1]:
		rich_tag = processed_readings[0][2].replace(" ", "")
		basic_tag = [x[0] for x in tag_categories if rich_tag in x[1]][0] if len([x[0] for x in tag_categories if rich_tag in x[1]]) > 0 else rich_tag
		processed_token = "{}\t{}\t{}\t{}\t{}\t{}\t".format(token_id, token, position, lemma, basic_tag, rich_tag)
		stats["post-cg"]["disambiguated"] += 1
		stats["post-cg"]["same_tag"] += 1
	else:
		if check_coverage == True:
			if token in cy_coverage.keys():
				tags = cy_coverage[token].split(":")
				processed_token = "{}\t{}\t{}\t{}\t{}\t{}\t".format(token_id, token, position, lemma, tags[0], tags[1])
				stats["post-cg"]["disambiguated"] += 1
				stats["post-cg"]["in_coverage"] += 1
			else:
				stats["post-cg"]["undisambiguated"] += 1
				stats["post-cg"]["still_ambiguous"] += 1
		else:
			stats["post-cg"]["undisambiguated"] += 1
			stats["post-cg"]["still_ambiguous"] += 1
	return(processed_token)

def process_single_reading(token_id, token, reading):
	""" Return a token with a single reading as a string of tab-separated values """
	processed_token = ""
	position, lemma, mutation, basic_tag, rich_tag = "", "", "", "", ""
	for quoted_lemma in re.findall(r'\"(.+?)\"', reading):
		reading = reading.replace(quoted_lemma, quoted_lemma.replace(" ", "_"))
	info = re.split(r"\s+", reading.strip())
	position, lemma = info[1][1:-1], info[0][1:-1].replace("_", " ")
	if info[-1] != "unk":
		if info[-2] == "+":
			mutation = "+{}".format(info[-1])
			info = info[:-2]
		i = len(info)-1
		while len(info[i]) > 1 and info[i][:1] == ":" and info[i][-1:] == ":":
			info = info[:-1]
			i = i - 1
		pos_tag = " ".join(info[3:])
		rich_tag = pos_tag.replace(" ", "")
		basic_tag = [x[0] for x in tag_categories if rich_tag in x[1]][0] if len([x[0] for x in tag_categories if rich_tag in x[1]]) > 0 else rich_tag
		processed_token = "{}\t{}\t{}\t{}\t{}\t{}\t{}".format(token_id, token, position, lemma, basic_tag, rich_tag, mutation)
		stats["post-cg"]["disambiguated"] += 1
		stats["post-cg"]["one_reading"] += 1
	else:
		checked_tags = check_gazetteers(token)
		if checked_tags == ["unk", "unk"]:
			processed_token = "{}\t{}\t{}\t{}\tunk\tunk\t".format(token_id, token, position, lemma)
			stats["post-cg"]["undisambiguated"] += 1
			if output["unknown_words"] != None:
				new_unknown_words.append(token)
		else:
			processed_token = "{}\t{}\t{}\t{}\t{}\t{}\t".format(token_id, token, position, lemma, checked_tags[0], checked_tags[1])
			stats["post-cg"]["disambiguated"] += 1
			stats["post-cg"]["unknown_gazetteer"] += 1
		stats["post-cg"]["unknown"] += 1
	return(processed_token)

def append_xml_token(token_parts, reading_count):
	""" Format a token and append it to the XML output tree """
	token = etree.Element("token")
	token.attrib["id"] = token_parts[0]
	token.attrib["readings"] = str(pre_cg_reading_counts[int(token_parts[0])]) #str(reading_count)
	token.attrib["lemma"] = token_parts[3]
	token.attrib["basic_pos"] = token_parts[4]
	token.attrib["rich_pos"] = token_parts[5]
	if token_parts[6] != "":
		token.attrib["mutation"] = token_parts[6]
	token.attrib["position"] = token_parts[2]
	token.text = token_parts[1]
	#xml_tree = output["tree"]
	sentence = output["tree"].xpath("file/sentence[@id='{}']".format(token_parts[2].split(",")[0]))[0]
	sentence.append(token)
	#output["tree"] = xml_tree

def process_cg_token(token_id, token_readings, token_position):
	""" Process a given token and its readings, returning it as a string of tab-separated values """
	token, readings = token_readings[0][2:-2], token_readings[1:]
	processed_token = ""
	if len(readings) == 1:
		processed_token = process_single_reading(token_id, token, readings[0])
	else:
		stats["post-cg"]["multiple_readings"] += 1
		if len(readings) == 2:
			processed_token = process_double_reading(token_id, token, readings)
		else:
			processed_token = process_multiple_reading(token_id, token, readings)
	if processed_token == "":
		processed_token = process_still_ambiguous(token_id, token, readings, token_position)
	if output["xml"] != None:
		append_xml_token(processed_token.split("\t"), len(readings))
	return("{}\n".format(processed_token))

def get_token_position(current_reading):
	""" Get the sentence position (first or last word, or somewhere in the middle) for a given token """
	current_position = re.search(r"{\d+,\d+}", current_reading).group()[1:-1]
	sentence, token = current_position.split(",")
	sentence_length = sentence_lengths[int(sentence)-1]
	if sentence_length < 3:
		return("small_sentence")
	else:
		if int(token) == 1:
			return("first")
		else:
			if int(token) == sentence_length:
				return("last")
			else:
				return("mid")

def map_cg(cg_output, mapping_bar=None):
	""" Map CG output to tokens as CyTag-formatted tab separated values """
	mapped_output = ""
	cg_readings = []
	cg_readingcount = 0
	cg_tokens = cg_output.strip().splitlines()
	for i, line in enumerate(cg_tokens):
		if line != "":
			if line[:1] != "\t":
				cg_readings.append([line])
				cg_readingcount += 1
				if cg_readingcount > 1:
					if mapping_bar != None:
						mapping_bar.next()
					mapped_output += process_cg_token(cg_readingcount-1, cg_readings[cg_readingcount-2], get_token_position(cg_readings[cg_readingcount-2][1]))
			else:
				cg_readings[cg_readingcount-1].append(line)
	if mapping_bar != None:
			mapping_bar.next()
	mapped_output += process_cg_token(cg_readingcount, cg_readings[cg_readingcount-1], get_token_position(cg_readings[cg_readingcount-1][1]))
	if mapping_bar != None:
		mapping_bar.finish()
	return(mapped_output)

def run_cg(cg_readings, vislcg3_location):
	""" Given a set of CG-formatted readings, run VISL CG-3 """
	cg_process = subprocess.Popen([vislcg3_location, '-g', '{}/../grammars/cy_grammar_2017-08-01'.format(os.path.dirname(os.path.abspath(__file__)))], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	cg_output = cg_process.communicate(input=cg_readings.encode("utf-8"))[0]
	return(cg_output.decode("utf-8"))

def sentence_readings(tokenised_sentence, total_tokens):
	""" Return a set of CG-formatted readings for a tokenised sentence """
	tokens = tokenised_sentence.splitlines()
	sentence_lengths.append(len(tokens))
	readings = ""
	for i, token in enumerate([token.split("\t") for token in tokens]):
		retrieved_readings = get_reading(total_tokens+i+1, [token[1], token[2]])
		readings += retrieved_readings
		#pre_cg_reading_counts[len(pre_cg_reading_counts.keys())+1] = len(retrieved_readings.strip().split("\n"))-1
	readings = readings.strip()
	readings += "\n"
	if output["readings"] != None:
		print(readings, file=output["readings"])
	return(readings)

def time_elapsed(started):
	""" Calculate the elapsed time, given a start time """
	now = int(time.time())
	m, s = divmod(now-started, 60)
	h, m = divmod(m, 60)
	return("{hour:02d}h, {min:02d}m, {sec:02d}s".format(hour=h, min=m, sec=s))

def save_unknown_words():
	""" Save the words CyTag didn't know to the appropriate output file """
	global new_unknown_words, existing_unknown_words
	new_unknown_words = list(set(new_unknown_words))
	all_unknown_words = list(set(existing_unknown_words+new_unknown_words))
	for word in all_unknown_words:
		print(word, file=output["unknown_words"])

def output_setup(output_name, directory, output_format):
	""" Set up the necessary folders and output files for running CyTag """
	create_folders(output_name, directory)
	output["directory"] = "{}/../outputs/{}".format(os.path.dirname(os.path.abspath(__file__)), output_name if directory == None else directory)
	for output_file in ["readings", "readingsPostCG"]:
		if output_file == "readings" and os.path.exists("{}/{}_{}".format(output["directory"], output_name, output_file)):
			os.remove("{}/{}_{}".format(output["directory"], output_name, output_file))
			output["{}".format(output_file)] = open("{}/{}_{}".format(output["directory"], output_name, output_file), "a")
		else:
			output["{}".format(output_file)] = open("{}/{}_{}".format(output["directory"], output_name, output_file), "w")
	if os.path.exists("{}/../outputs/unknown_words".format(os.path.dirname(os.path.abspath(__file__)))):
		with open("{}/../outputs/unknown_words".format(os.path.dirname(os.path.abspath(__file__)))) as loaded_unknown_words:
			existing_unknown_words = loaded_unknown_words.read().splitlines()
	output["unknown_words"] = open("{}/../outputs/unknown_words".format(os.path.dirname(os.path.abspath(__file__))), "w")
	if output_format in ["tsv", "all"]:
		output["tsv"] = open("{}/{}.tsv".format(output["directory"], output_name), "w")
	if output_format in ["xml", "all"]:
		output["xml"] = open("{}/{}.xml".format(output["directory"], output_name), "w")

def pos_tagger(input_data, output_name=None, directory=None, output_format=None):
	""" For a provided input (files, or text as a string): 
		--- Produce a set of CG-formatted readings
		--- Run VISL CG-3 to prune the readings
		--- Map the CG-3 output to tokens as CyTag-formatted tab-separated values
	"""
	if output_format != None and len(missing_libraries) > 0: 
		raise ImportError("The following libraries (required when an output format is specified) are missing: {}".format(missing_libraries))
	else:
		readings = ""
		total_sentences, total_tokens = 0, 0
		started = int(time.time())
		if output_format != None:
			print("\ncy_postagger - A part-of-speech (POS) tagger for Welsh texts\n------------------------------------------------------------\n")
			output_setup(output_name, directory, output_format)
			print("Producing readings...\n")
		if isinstance(input_data, list):
			if output["xml"] != None:
				output["tree"] = etree.Element("corpus")
				output["tree"].attrib["name"] = output_name
			for file_id, file in enumerate(input_data):
				file_element = None
				if output["xml"] != None:
					file_element = etree.Element("file")
					file_element.attrib["id"] = str(file_id+1)
					file_element.attrib["name"] = file.split("/")[-1]
				with open(file, encoding="utf-8") as file_text:
					for segment_id, segment in enumerate(segment_text(file_text.read())):
						for sentence_id, sentence in enumerate(split_sentences(segment)):
							sentence_element = None
							if output["xml"] != None:
								sentence_element = etree.Element("sentence")
								sentence_element.attrib["id"] = str(total_sentences+1)
							total_sentences += 1
							tokens = tokenise(sentence, total_sentences, total_tokens)
							readings += sentence_readings(tokens, total_tokens)
							total_tokens += len(tokens.splitlines())
							if output["xml"] != None:
								file_element.append(sentence_element)
				if output["xml"] != None:
					output["tree"].append(file_element)
		elif isinstance(input_data, str):
			for segment_id, segment in enumerate(segment_text(input_data.replace("\\n", "\n"))):
				for sentence_id, sentence in enumerate(split_sentences(segment)):
					total_sentences += 1
					tokens = tokenise(sentence, total_sentences, total_tokens)
					readings += sentence_readings(tokens, total_tokens)
					total_tokens += len(tokens.splitlines())
		if output_format != None:
			print("From {} tokens:\n--- {} tokens were given readings\n------ {} tokens only have a single reading pre-CG\n--------- {} of which were definite tags (punctuation, symbols etc.)\n------ {} tokens have multiple readings pre-CG\n------ {} tokens have no readings pre-CG\n------ {} tokens without readings were assumed to be proper nouns\n--- {} tokens are still without readings (marked as 'unknown')\n".format(total_tokens, stats["pre-cg"]["with_readings"], stats["pre-cg"]["single_reading"], stats["pre-cg"]["definite_tag"], stats["pre-cg"]["multiple_readings"], stats["pre-cg"]["no_readings"], stats["pre-cg"]["assumed_proper"], stats["pre-cg"]["without_readings"]))
		if vislcg3_location == None or vislcg3_location == "" or vislcg3_location == bytearray():
			raise ValueError("VISL CG-3 could not be found, and is required to continue using CyTag. Please follow the instructions in the README file to install it\n")
		else:
			if output_format != None:
				print("Running VISL CG-3 over {} tokens...\n".format(total_tokens))
			cg_output = run_cg(readings, vislcg3_location)
			if cg_output == "":
				raise ValueError("An empty output was returned from VISL CG-3. If details of an error were printed above this message, please try and resolve them. Otherwise, contact us via the details in the README file\n")
			elif cg_output.splitlines()[0].startswith("\"<") == False and cg_output.splitlines()[0].endswith(">\"") == False:
				raise ValueError("The returned output was not CG-formatted readings ---\n{}".format(cg_output))
			else:
				if output["readingsPostCG"] != None:
					print(cg_output.strip(), file=output["readingsPostCG"])
				mapping_bar = None if output_format == None else Bar("Mapping CG output tokens to CyTag output formats", max=total_tokens)
				cytag_output = map_cg(cg_output.strip(), mapping_bar)
				if output["unknown_words"] != None:
					save_unknown_words()
				if output["tsv"] != None:
					print(cytag_output.strip(), file=output["tsv"])
				if output["xml"] != None:
					tree = etree.ElementTree(output["tree"])
					tree.write(output["xml"].name, pretty_print=True, xml_declaration=True, encoding='UTF-8')
				if output_format == None:
					return(cytag_output.strip())
				else:
					print("\nFinal statistics from {} tokens:\n--- {} tokens disambiguated\n------ {} pruned to one reading post-CG\n------ {} ambiguous post-CG, but:\n--------- {} found to have two readings with the same POS tag\n--------- {} found to be proper nouns of ambiguous gender\n------------ {} of these came from the gazetteers\n--------- {} ambiguous, but found in the gazetteers\n--------- {} assigned a POS tag based on the coverage dictionary\n------ {} unknown, but then found in gazetteers\n--- {} tokens undisambiguated\n------ {} still ambiguous post-CG\n------ {} unknown\n".format(total_tokens, stats["post-cg"]["disambiguated"], stats["post-cg"]["one_reading"], stats["post-cg"]["multiple_readings"]-stats["post-cg"]["still_ambiguous"], stats["post-cg"]["same_tag"], stats["post-cg"]["pns_gazetteer"]+stats["post-cg"]["neutral_pns"], stats["post-cg"]["pns_gazetteer"], stats["post-cg"]["ambiguous_gazetteer"], stats["post-cg"]["in_coverage"], stats["post-cg"]["unknown_gazetteer"], stats["post-cg"]["undisambiguated"], stats["post-cg"]["still_ambiguous"], stats["post-cg"]["unknown"]))
					print("Time taken to tag {} tokens from {} sentences: {}\n".format(total_sentences, total_tokens, time_elapsed(started)))

def parse_arguments(arguments):
	""" Parse command line arguments """
	parser = argparse.ArgumentParser(description="cy_postagger.py - A part-of-speech (POS) tagger for Welsh texts")
	optional = parser._action_groups.pop()
	required = parser.add_argument_group("required arguments")
	required.add_argument("-i", "--input", help="Input file path(s)", nargs="+", required=True)
	optional.add_argument("-n", "--name", help="Output file name")
	optional.add_argument("-d", "--dir", help="Output directory")
	optional.add_argument("-f", "--format", help="Output file format ('tsv', 'xml', 'all')")
	parser._action_groups.append(optional)
	return(parser.parse_args())

if __name__ == "__main__":
	""" Split the provided input (text as a string, or files) into single tokens tagged with their appropriate part-of-speech (POS) """
	args = sys.argv[1:]
	if len(args) == 0 and not sys.stdin.isatty():
		pos_tagger(input_data=sys.stdin.read())
	else:
		if len(args) == 1 and os.path.isfile(args[0]) != True and args[0].startswith("-") != True:
			pos_tagger(input_data=args[0])
		else:
			arguments = parse_arguments(args)
			pos_tagger(arguments.input, output_name=arguments.name, directory=arguments.dir, output_format=arguments.format)
