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

2018-2020 Bethan Tovey-Walsh <bytheway@linguacelta.com>

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
from shared.load_lexicon import *
from shared.reference_lists import *

gazetteers = load_gazetteers()
cy_lexicon = load_lexicon()

contractions_and_prefixes = {}
with open("{}/../cy_gazetteers/contractions_and_prefixes.json".format(os.path.dirname(os.path.abspath(__file__)))) as contractionsprefixes_json:
	contractions_and_prefixes = json.load(contractionsprefixes_json) 

def remove_markup(tokens):
	""" Remove markup tags (opening, closing, or both) from tokens """
	for i, token in enumerate(tokens):
		if token[:3] in ["<D>", "<N>"]:
			tokens[i] = tokens[i][3:]
		if token[-4:] in ["</D>", "</N>"]:
			tokens[i] = tokens[i][:-4]	
		if token[:7] == "<rhegi>":
			tokens[i] = tokens[i][7:]
		if token[-8:] == "</rhegi>":
			tokens[i] = tokens[i][:-7]		
	return(tokens)

def token_split(sent, total_tokens):
	""" Use regular expressions to split a sentence into a list of tokens, before handling more complex cases """
	tokens = []
	if sent != "":
		""" Normalize different kinds of potential apostrophe/single quotation and dash/hyphen characters """
		sent_apos = (re.sub(r"[’‘`]", "'", sent))
		sentence = (re.sub(r"[‑—–]", "-", sent_apos))
		regexed_tokens = re.split(r"\s(?!\S[.])|(?<!\S[.])\s", sentence)
		token_list = list(filter(None, regexed_tokens))
		token_list = remove_markup(token_list)
		for i, token in enumerate(token_list):
			if token != '':
				tokens = tokens + check_token(token)
	return(tokens)

def check_token(token):
	### Words tagged as English (<en>point</en>) should be
	### returned with their tagging so that the postagger
	### can tag them correctly.
	match_english = re.match(r"^(<en( gair=\"[a-zA-Z]+\")?>([\w'\-]+)</en>)(.*)$", token)
	if match_english is not None:
		if match_english.group(4) != "":
			return [match_english.group(1)] + check_token(match_english.group(4))
		else:
			return [match_english.group(1)]
	match_anon = re.match(r"^(<anon>[\w'\-]+</anon>)(.*)$", token)
	if match_anon is not None:
		if match_anon.group(2) != "":
			return [match_anon.group(1)] + check_token(match_anon.group(2))
		else:
			return [match_anon.group(1)]
	if len(re.findall(r"[\\/]", token)) > 0:
		if len(set(token)) == 1:
			return [token]
		result = []
		split = list(filter(None, re.split(r"([\\/])", token)))
		for s in split:
			if set(s) in ["\\", "/"]:
				result.append(s)
			else:
				result += check_token(s)
		return result
	### !!!! aaaaa Ffffff 
	if len(set(token.lower())) == 1:
		return [token]
	### gair 100
	if token.isalpha() or token.isnumeric():
		return [token]
	### word09:!!!!!!() => word09  :!!!!!!()
	match_end = re.match(r"^([\w']+)([^\w'\-¢%]+)$", token)
	if match_end is not None:
		return check_token(match_end.group(1)) + check_token(match_end.group(2))
	### !!!!!!()word_90 => !!!!!!() word_90
	match_start = re.match(r"^([^\w\-'#@¥£€$]+)([\w']+)$", token)
	if match_start is not None:
		return check_token(match_start.group(1)) + check_token(match_start.group(2))
	### hashtags
	if len(re.findall(r"#", token)) > 0:
		if re.match(r"#\w+", token):
			return [token]
		hashtag_front = re.match(r"^(#\w+)([^\w].*)$", token)
		if hashtag_front is not None:
			return [hashtag_front.group(1)] + check_token(hashtag_front.group(2))
		hashtag_end = re.match(r"^(.*)(#[\w]+)$", token)
		if hashtag_end is not None:
			return check_token(hashtag_end.group(1)) + [hashtag_end.group(2)]
		hashtag_mid = re.match(r"^(.+)(#\w+)([^\w].*)$", token)
		if hashtag_mid is not None:
			return check_token(hashtag_mid.group(1)) + [hashtag_mid.group(2)] + check_token(hashtag_mid.group(3))
	### apostrophes
	if len(re.findall("'", token)) != 0:
		if token in contractions_and_prefixes or token.lower() in contractions_and_prefixes or token.lower() in cy_lexicon:
			return [token]
		if token[0] == "'" and token[-1] == "'" and len(token) > 2:
			return ["'"] + check_token(token[1:-1]) + ["'"]
		elif token[0] == "'":
			### 'em-all => 'em - all
			if not token[1:].isalpha():
				result = []
				split = check_token(token[1:])
				if len(split) > 1:
					split[0] = "'" + split[0]
					for sp in split:
						result = result + check_token(sp)	
					return result	
			return ["'"] + check_token(token[1:])
		elif token[-1] == "'":
			###os-f' => os - f'
			if not token[:-1].isalpha():
				result = []
				split = check_token(token[:-1])
				if len(split) > 1:
					split[-1] = split[-1] + "'"
					for sp in split:
						result = result + check_token(sp)	
					return result	
			return ["'"] + check_token(token[:-1])
		else:
			apos = "'"
			split = list(filter(None, re.split(r"(')", token)))
			result = []
			for i, s in enumerate(split):
				before = apos + s
				after = s + apos
				if s not in ["'", ""]:
					if i == 1 and len(split) == 3 and split[i-1] == "'" and split[i+1] == "'":
							result = result + [apos] + check_token(s) + [apos]
					if i == 0:
						if split[i+1] == "'":
							if after in contractions_and_prefixes:
								result.append(after)
								split[i+1] = ""
							else:
								result = result + check_token(s)
						else:
							result = result + check_token(s)
					if i != 0 and i != len(split)-1:
						if split[i-1] == "'" and (before in contractions_and_prefixes):
							result.append(before)
						elif split[i-1] == "'":
							if split[i+1] == "'" and (after in contractions_and_prefixes):
								result.append(after)
								split[i+1] == ""
							else:
								result = result + [apos] + check_token(s)
						else:
							result = result + check_token(s)
					elif i == len(split)-1:
						if split[i-1] == "'" and (before in contractions_and_prefixes):
							result.append(before)
						elif split[i-1] == "'":
							result = result + ["'"] + check_token(s)
						else:
							result = result + check_token(s)
			return result
	### hyphens
	if token.find("-") != -1:
		result = []
		if token.lower() in cy_lexicon or token.lower() in gazetteers:
			return [token]
		token_parts = re.split("(-)", token)
		if len(token_parts) == 3:
			result = check_token(token_parts[0]) + check_token(token_parts[1])
			return result
		for i, tok in enumerate(token_parts):
			if not tok.isalpha() and tok != "-":
				if i == 0:
					first_part = token_parts[0]
					last_part = "".join(token_parts[2:])
					result = check_token(first_part) + ["-"] + check_token(last_part)
				elif i == len(token_parts) - 1:
					first_part = "".join(token_parts[:-2])
					last_part = token_parts[i]
					result = check_token(first_part) + ["-"] + check_token(last_part)
				else:
					first_part = "".join(token_parts[:i-2])
					middle_part = token_parts[i]
					last_part = "".join(token_parts[i+2:])
					result = check_token(first_part) + ["-"] + check_token(middle_part) + ["-"] + check_token(last_part)
				return result
		token_parts_nohyphens = token.lower().split("-")
		if "".join(token_parts_nohyphens) in cy_lexicon or "".join(token_parts_nohyphens) in gazetteers or " ".join(token_parts_nohyphens) in cy_lexicon or " ".join(token_parts_nohyphens) in gazetteers:
			return [token]
		elif token_parts_nohyphens[0] + "-" in contractions_and_prefixes:
			first = "".join(token_parts[0:3])
			rest = "".join(token_parts[3:])
			result = [first]
			if rest != "":
				result += check_token(rest)
			return result
		elif token[0] == "-":
			if not token[1:].isalpha():
				result = []
				split = check_token(token[1:])
				if len(split) > 1:
					split[0] = "-" + split[0]
					for sp in split:
						result = result + check_token(sp)	
					return result	
			return ["-"] + check_token(token[1:])
		elif token[-1] == "-":
			### -pa-un6 => - pa - un 6
			if not token[:-1].isalpha():
				result = []
				split = check_token(token[:-1])
				if len(split) > 1:
					split[-1] = split[-1] + "-"
					for sp in split:
						result = result + check_token(sp)	
					return result	
			return ["-"] + check_token(token[1:])
		else:
			hyph = "-"
			split = list(filter(None, re.split(r"(-)", token)))
			result = []
			for i, s in enumerate(split):
				before = hyph + s
				after = s + hyph
				if s not in ["-", ""]:
					if i == 1 and len(split) == 3 and split[i-1] == "-" and split[i+1] == "-":
							return [hyph] + check_token(s) + [hyph]
					if i == 0:
						if split[i+1] == "-":
							if after in contractions_and_prefixes:
								result.append(after)
								split[i+1] = ""
							else:
								result = result + check_token(s)
						else:
							result = result + check_token(s)
					if i != 0 and i != len(split)-1:
						if split[i-1] == "-" and (before in contractions_and_prefixes):
							result.append(before)
						elif split[i-1] == "-":
							if split[i+1] == "-" and (after in contractions_and_prefixes):
								result.append(after)
								split[i+1] == ""
							else:
								result = result + [hyph] + check_token(s)
						else:
							result = result + check_token(s)
					elif i == len(split)-1:
						if split[i-1] == "-" and (before in contractions_and_prefixes):
							result.append(before)
						elif split[i-1] == "-":
							result = result + ["-"] + check_token(s)
						else:
							result = result + check_token(s)
			return result
	### word!word => word ! word
	match_semic = re.match(r"^([\w]+);([\w]+)$", token)
	if match_semic is not None:
		apos_replace1 = (match_semic.group(1))
		apos_replace2 = "'" + (match_semic.group(2))
		if apos_replace2.lower() in cy_lexicon:
			split2 = ";" + apos_replace2[1:]
			return [(match_semic.group(1)), split2]
		else:
			return [(match_semic.group(1)), ";", (match_semic.group(2))]
	### word!word => word ! word
	match_mid = re.match(r"^([\w]+)([^\w\*]+)([\w]+)$", token)
	if match_mid is not None:
		return check_token(match_mid.group(1)) + check_token(match_mid.group(2)) + check_token(match_mid.group(3))
	### !!!!?:!! => ! !!!?:!! 
	if token[0] in ["\\", ",", ".", ",", ":", ";", "“", "”", '"', "!", "?", "<", ">", "{", "}", "[", "]", "(", ")", "*", "…", "¶", "+"]:
		return [token[0]] + check_token(token[1:])
	if token[-1] in ["\\", ",", ".", ",", ":", ";", "“", "”", '"', "!", "?", "<", ">", "{", "}", "[", "]", "(", ")", "*", "…", "¶", "+"]:
		return check_token(token[0:-1]) + [token[-1]]
	### numerical strings
	if token[0].isnumeric():
		### 1990au 1990s 90s 90's 90au
		if re.match(r"^['’]?([12]?\d)?[0-9][0-9][']?(au|s)?$", token):
			return [token]
		### 90c 75p 99K
		if re.match(r"^[\$€£¥][0-9]+([,\.]?[0-9]+)?[p¢ckKmM]?$", token):
			return [token]
		### 6pm 7yh 9a.m.
		if re.match(r"^([012]?[0-9][:\.]?)?[012345][0-9](yh|am|yb|pm|y\.h\.|a\.m\.|y\.b\.|p\.m\.|ybore|yrhwyr|yp)?$", token):
			return [token]
		### 654BC
		if re.match(r"^[123]?\d(\d\d)?(oc|cc|bc|bce|ce|ad|a\.\d\.|b\.c\.|b\.c\.e\.|o\.c\.|c\.c\.|c\.e\.)", token.lower()):
			return [token]
		### 09\07\2007
		if re.match(r"^[0123]?\d[\\\-\.\/–][0123]?\d[\\\-\.\/–][12]\d\d\d", token) or re.match(r"^[12]\d\d\d[\\\-\.\/–][0123]?\d[\\\-\.\/–][0123]?\d", token):
			return [token]
		if re.match(r"^-?[0-9]+[,\.]\d+%?$", token) or re.match(r"^-?\d+\:?[0-9]+[,\.]\d+%?$", token):
			return [token]
	### 100people => 100 people
	match_num1 = re.match(r"^([0-9\.,]+)([^0-9\.,]+)$", token)
	if match_num1 is not None:
		return check_token(match_num1.group(1)) + check_token(match_num1.group(2))
	match_num2 = re.match(r"^([^0-9\.,]+)([0-9\.,]+)$", token)
	if match_num2 is not None:
		return check_token(match_num2.group(1)) + check_token(match_num2.group(2))
	match_num3 = re.match(r"^([0-9\.,]+)(.+)$", token)
	if match_num3 is not None:
		return check_token(match_num3.group(1)) + check_token(match_num3.group(2))		
	### 90c 75p 99K
	if token[0] in ["$", "€", "£", "¥"] and re.match(r"[0-9\.,]+[¢cpMmkK]?$", token[1:]):
		return [token]
	return [token]

def tokenise(sentence, total_sentences=None, total_tokens=None):
	""" Split an input sentence into tokens, and return them as tab-separated values """
	split_tokens = ""
	if sentence[-1:] == "." and sentence[-2:] != " .":
		sentence = "{}{}".format(sentence[:-1], " .")

	tokens = token_split(sentence, total_tokens)
#	tokens = remove_markup(tokens)
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
	print("Tokeniser...\n")
	args = sys.argv[1:]
	if len(args) == 1 and os.path.isfile(args[0]) != True:
		tokeniser(args[0])
	else:
		tokeniser(args)

