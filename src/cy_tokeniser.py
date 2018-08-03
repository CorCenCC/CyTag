#!usr/bin/env python3
#-*- coding: utf-8 -*-
"""
'cy_tokeniser.py'

A tokeniser for Welsh texts.

Accepts as arguments:
	--- REQUIRED: A string of Welsh language text.
	or:
	--- REQUIRED: One or more Welsh input text files (raw text).

Returns:
	--- Tokens as tab-separated values

Developed at Cardiff University as part of the CorCenCC project (www.corcencc.org).

2016-2018 Steve Neale <steveneale3000@gmail.com, NealeS2@cardiff.ac.uk>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses>.
"""

import sys
import os
import re

import json

from cy_textsegmenter import *
from cy_sentencesplitter import *
from shared.load_gazetteers import *

gazetteers = load_gazetteers()

contractions_and_prefixes = {}
with open("{}/../cy_gazetteers/contractions_and_prefixes.json".format(os.path.dirname(os.path.abspath(__file__)))) as contractionsprefixes_json:
	contractions_and_prefixes = json.load(contractionsprefixes_json) 

def remove_markup(tokens):
	""" Remove markup tags (opening, closing, or both) from tokens """
	for i, token in enumerate(tokens):
		if token[:6] == "<anon>":
			tokens[i] = token[6:]
		if token[-7:] == "</anon>":
			tokens[i] = token[:-7]
	return(tokens)

def check_punctuation(token, total_tokens, token_id):
	""" Separate punctuation from tokens """
	try:
		if token[:6] == "<anon>" or token[-7:] == "</anon>":
			return(complex_split_anon(token, total_tokens, token_id, 1))
		if len(re.findall(r"(^[.,:;\"\'!?<>{}()\]\[]|[.,:;\"\'!?<>{}()\]\[]$)", token)) < 1 or token in re.findall("(^[.,:;\"\'!?<>{}()\]\[]|[.,:;\"\'!?<>{}()\]\[]$)", token) or (len(re.findall("(?<![A-Z0-9_])([A-Z0-9_][.](\s*[A-Z0-9_][.])*)", token)) > 0 and (re.findall("(?<![A-Z0-9_])([A-Z0-9_][.](\s*[A-Z0-9_][.])*)", token)[0][0] == token)) or token in gazetteers["abbreviations"] or token in contractions_and_prefixes.keys():
			return([token])
		elif len(re.findall(r"[.]{2,}", token)) > 0:
			if re.findall(r"[.]{2,}", token)[0] == token:
				return([token])
			else:
				ellipsis = re.findall(r"[.]{2,}", token)[0]
				return([token[:-len(ellipsis)], ellipsis])
		else:
			tokens = re.split(r"(^[.,:;\"\'!?<>{}()\]\[]|[.,:;\"\'!?<>{}()\]\[]$)", token)
			tokens = list(filter(None, tokens))
			for i, new_token in enumerate(tokens):
				if new_token not in gazetteers["acronyms"]:
					del tokens[i]
					tokens[i:i] = check_punctuation(new_token, total_tokens, token_id)
			return(tokens)
	except:
		print("Error checking punctuation for token:", token)

def separate_elisions(token, total_tokens, token_id):
	""" Separate tokens containing elisions """
	if token[:6] == "<anon>" or token[-7:] == "</anon>":
		return(complex_split_anon(token, total_tokens, token_id, 2))
	for term in contractions_and_prefixes.keys():
		if contractions_and_prefixes[term][0] == "contraction":
			if term[-1:] == "'" and len(re.findall(r"^("+term+")", token)) > 0:
				separated = re.split(r"^("+term+")", token)
				separated = list(filter(None, separated))
				return(separated)
			if term[:1] == "'" and len(re.findall(r"("+term+")$", token)) > 0:
				separated = re.split(r"("+term+")$", token)
				separated = list(filter(None, separated))
				return(separated)
	else:
		return([token])

def split_dashes(token):
	""" Separate tokens containing dashes """
	separated = [token]
	if "-" in token and token != "-" and not re.match(r"\d+(-)\d+", token):
		prefixes = [prefix for prefix in contractions_and_prefixes.keys() if contractions_and_prefixes[prefix][0] == "prefix"]
		if token[0:token.index("-")+1] not in prefixes and token[0:token.index("-")+1].lower() not in prefixes:
			if len(re.findall("(-)", token)) == 1:
				token_parts = token.split("-")
				if token_parts[0] != "" and token_parts[1] != "":
					if token_parts[0][0].isupper() and token_parts[1][0].isupper():
						separated = re.split("(-)", token)
	return(separated)


def separate_symbols(token, total_tokens, token_id):
	""" Seperate tokens containing symbols """
	if token[:6] == "<anon>" or token[-7:] == "</anon>":
		return(complex_split_anon(token, total_tokens, token_id, 3))
	if len(re.findall(r"([^\s^.,:;!?\-\'\"<>{}()\[\]^\w])", token)) > 0 and "http" not in token and "www." not in token: 
		separated = re.split(r"([^\s^.,;:!?\-\'\"<>{}()\[\]^\w])", token)
		separated = list(filter(None, separated))
		return(separated)
	else:
		return([token])

def complex_split_anon(token, total_tokens, token_id, process):
	""" Split apart complicated tokens when they're enclosed within some kind of markup tags (opening, closing, or both) """
	anon_separated = []
	stripped_token = ""
	if token[:6] == "<anon>" and token[-7:] == "</anon>":
		stripped_token = token[6:-7]
	elif token[:6] == "<anon>" and token[-7:] != "</anon>":
		stripped_token = token[6:]
	elif token[:6] != "<anon>" and token[-7:] == "</anon>":
		stripped_token = token[:-7]
	separated_tokens = []
	if process == 1:
		separated_tokens = check_punctuation(stripped_token, total_tokens, token_id)
	elif process == 2:
		separated_tokens = separate_elisions(stripped_token, total_tokens, token_id)
	elif process == 3:
		separated_tokens = separate_symbols(stripped_token, total_tokens, token_id)
	if len(separated_tokens) > 1:
		if token[:6] == "<anon>" and token[-7:] == "</anon>":
			anon_separated = ["<anon>{}</anon>".format(x) for x in separated_tokens]
		elif token[:6] == "<anon>" and token[-7:] != "</anon>":
			anon_separated = ["<anon>{}".format(x) for x in separated_tokens]
		elif token[:6] != "<anon>" and token[-7:] == "</anon>":
			anon_separated = ["{}</anon>".format(x) for x in separated_tokens]
	if len(anon_separated) > 1:
		return(anon_separated)
	else:
		return([token])

def complex_split(tokens, total_tokens):
	""" Split complicated tokens, such as those containing punctuation, elision, dashes, and symbols """
	for i in range(1, 5):
		for j, token in enumerate(tokens):
			separated_tokens = []
			if i == 1:
				separated_tokens = check_punctuation(token, total_tokens, j)
			elif i == 2:
				separated_tokens = separate_elisions(token, total_tokens, j)
			elif i == 3:
				separated_tokens = split_dashes(token)
			elif i == 4:
				separated_tokens = separate_symbols(token, total_tokens, j)
			if len(separated_tokens) > 1:
				del tokens[j]
				tokens[j:j] = separated_tokens
	return(tokens)

def token_split(sentence, total_tokens):
	""" Use regular expressions to split a sentence into a list of tokens, before handling more complex cases """
	tokens = []
	if sentence != "":
		regexed_tokens = re.split(r"\s(?!\S[.])|(?<!\S[.])\s", sentence)
		token_list = list(filter(None, regexed_tokens))
		tokens = complex_split(token_list, total_tokens)
	return(tokens)

def tokenise(sentence, total_sentences=None, total_tokens=None):
	""" Split an input sentence into tokens, and return them as tab-separated values """
	split_tokens = ""
	if sentence[-1:] == "." and sentence[-2:] != " .":
		sentence = "{}{}".format(sentence[:-1], " .")
	tokens = token_split(sentence, total_tokens)
	tokens = remove_markup(tokens)
	for token_id, token in enumerate(tokens):
		split_tokens += "{}\t{}\t{}\n".format(total_tokens+token_id+1, token, "{},{}".format(total_sentences, token_id+1))
	return(split_tokens)

def tokeniser(input_data):
	""" Segment, sentence split, and then tokenise the input files/text """
	tokenised = ""
	total_sentences, total_tokens = 0, 0
	if isinstance(input_data, list):
		for file_id, file in enumerate(input_data):
			with open(file, encoding="utf-8") as file_text:
				for segment_id, segment in enumerate(segment_text(file_text.read())):
					for sentence_id, sentence in enumerate(split_sentences(segment)):
						total_sentences += 1
						split_tokens = tokenise(sentence, total_sentences, total_tokens)
						tokenised += split_tokens
						total_tokens += len(split_tokens.splitlines())
	elif isinstance(input_data, str):
		for segment_id, segment in enumerate(segment_text(input_data.replace("\\n", "\n"))):
			for sentence_id, sentence in enumerate(split_sentences(segment)):
				total_sentences += 1
				split_tokens = tokenise(sentence, total_sentences, total_tokens)
				tokenised += split_tokens
				total_tokens += len(split_tokens.splitlines())
	return(tokenised.strip())

if __name__ == "__main__":
	""" Split the provided input into tokens (text as a string, or files) """
	args = sys.argv[1:]
	if len(args) == 1 and os.path.isfile(args[0]) != True:
		tokeniser(args[0])
	else:
		tokeniser(args)
