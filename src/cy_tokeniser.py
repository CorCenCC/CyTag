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

with open("cy_gazetteers/corcencc.other_proper".format(os.path.dirname(os.path.abspath(__file__)))) as GeirEraill:
	trade_names = set(GeirEraill.read().splitlines())

def remove_markup(tokens):
	""" Remove markup tags (opening, closing, or both) from tokens """
	for i, token in enumerate(tokens):
		if token[:3] == "<D>":
			tokens[i] = tokens[i][3:]
		if token[-4:] == "</D>":
			tokens[i] = tokens[i][:-4]
		if token in ["<D>", "</D>", "<saib>", "<=>", "</=>", "<aneglur>", "<aneglur?>"]:
			tokens[i] = ""
		if token == "<N>":
			tokens[i] = "["
		if token[:3] == "<N>":
			tokens[i] = "[" + tokens[i][3:]
		if token == "</N>":
			tokens[i] = "["
		if token[-4:] == "</N>":
			tokens[i] = tokens[i][:-4] + "]"
		if token[:7] == "<rhegi>":
			tokens[i] = tokens[i][7:]
		if token[-8:] == "</rhegi>":
			tokens[i] = tokens[i][:-8]
	for i,tok in enumerate(tokens):
		tokens[i] = (re.sub(r"<ym>", "ymm", tok))
	final_tokens = []
	for token in tokens:
		tok_split = re.split(r"(<[sS](?:\d+|\?)>)", token)
		final_tokens += list(filter(None, tok_split))
	return final_tokens

def en_tag_check(sentence):
	""" Ensure that content in <en> tags is kept together """
	if sentence.find("<en") != -1:
		sentence = re.sub(r'<en gair="[^"]+">', '<en>', sentence)
		split_tags = re.split(r'(</?en>)', sentence)
		en_split = list(filter(None, split_tags))
		if len(en_split) < 3:
			sentence = (re.sub(r"</?en>", "", sentence))
		elif sentence.count("<en>") != sentence.count("</en>"):
			sentence = (re.sub(r'(</?en>)', "", sentence))
		else:
			tag_close = en_split.index("</en>")
			tag_open = tag_close - 2
			tag_contents = en_split[tag_open+1]
			tag_items = tag_contents.split(" ")
			tag_items = list(filter(None, tag_items))
			all_tagged = []
			for item in tag_items:
				split_punct = re.split(r"(\W+)", item)
				split_punct = list(filter(None, split_punct))
				if len(split_punct) == 1:
					individually_tagged = "<en>" + item + "</en>"
					all_tagged.append(individually_tagged)
				else:
					for x in split_punct:
						if x.isalpha():
							individually_tagged = "<en>" + x + "</en>"
							all_tagged.append(individually_tagged)
						else:
							all_tagged.append(x)
			sentence = " ".join(all_tagged)
			if tag_close != len(en_split)-1:
				if "<en>" in en_split[tag_close+1:]:
					post_tags = en_tag_check("".join(en_split[tag_close+1:]))
				else:
					post_tags = "".join(en_split[tag_close+1:])
				sentence += post_tags	
	return sentence

def token_split(sent, total_tokens):
	""" Use regular expressions to split a sentence into a list of tokens, before handling more complex cases """
	tokens = []
	if sent != "":
		""" Normalize different kinds of potential apostrophe/single quotation and dash/hyphen characters """
		sent_apos = (re.sub(r"[’‘`]", "'", sent))
		sentence = (re.sub(r"[‑—–]", "-", sent_apos))
		sentence = en_tag_check(sentence)
		token_list = list(filter(None, re.split(r"\s", sentence)))
		token_list = remove_markup(token_list)
		for i, token in enumerate(token_list):
			if token not in ['', ' ']:
				tokens = tokens + check_token(token)
	return(tokens)

def check_token(token):
	### Words tagged as English (<en>point</en>) should be
	### returned with their tagging so that the postagger
	### can tag them correctly.
	if len(token) == 1:
		return [token]
	match_english = re.match(r"^(<en( gair=\"[a-zA-Z]+\")?>([\w'\-]+)</en>)(.*)$", token)
	if match_english is not None:
		no_gair = (re.sub(r"<en gair=\"[a-zA-Z]+\" ?>", "<en>", match_english.group(1)))
		if match_english.group(4) != "":
			return [no_gair] + check_token(match_english.group(4))
		else:
			return [no_gair]
	match_anon = re.match(r"^(<anon>[\w'\-]+</anon>)(.*)$", token)
	if match_anon is not None:
		if match_anon.group(2) != "":
			return [match_anon.group(1)] + check_token(match_anon.group(2))
		else:
			return [match_anon.group(1)]
	match_speaker_tag = re.match(r"^<[sS](\d+|\?)>$", token)
	if match_speaker_tag is not None:
		return [token]
	if token in ["<=>", "</=>", "<saib>", "<aneglur>", "<aneglur?>"]:
		return [token]
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
	### !!!!?:!! => ! !!!?:!! 
	if token[0] in ["\\", ",", ".", ",", ":", ";", '"', "!", "?", "<", ">", "{", "}", "[", "]", "(", ")", "*", "…", "¶", "+"]:
		return [token[0]] + check_token(token[1:])
	if token[-1] in ["\\", ",", ".", ",", ":", ";", '"', "!", "?", "<", ">", "{", "}", "[", "]", "(", ")", "*", "…", "¶", "+"]:
		return check_token(token[0:-1]) + [token[-1]]
	### !!!! aaaaa Ffffff 
	if len(set(token.lower())) == 1:
		return [token]
	### gair 100
	if token.isalpha() or token.isnumeric():
		return [token]
	### B.B.C.
	match_initialism = re.match(r"^([a-zA-Z]\.)+$", token)
	if match_initialism is not None:
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
		if re.match(r"#\w+$", token):
			return [token]
		hashtag_front = re.match(r"^(#\w+)(\W.*)$", token)
		if hashtag_front is not None:
			return [hashtag_front.group(1)] + check_token(hashtag_front.group(2))
		hashtag_end = re.match(r"^(.*)(#\w+)$", token)
		if hashtag_end is not None:
			return check_token(hashtag_end.group(1)) + [hashtag_end.group(2)]
		hashtag_mid = re.match(r"^(.+)(#\w+)(\W.*)$", token)
		if hashtag_mid is not None:
			return check_token(hashtag_mid.group(1)) + [hashtag_mid.group(2)] + check_token(hashtag_mid.group(3))
	### hyphens
	if len(re.findall("-", token)) != 0:
		if token.lower() in cy_lexicon:
			return [token]
		elif token[0] == "-":
			return ["-"] + check_token(token[1:])
		elif token[-1] == "-":
			return ["-"] + check_token(token[:-1])
		elif token.count("-") == 1:
			hyph_index = token.index("-")
			if token[:hyph_index+1] in cy_lexicon:
				return [token[:hyph_index+1]] + check_token(token[hyph_index+1:])
			else:
				return check_token(token[:hyph_index]) + ["-"] + check_token(token[hyph_index+1:])
		else:
			return [token]
	### word;word => word ; word
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
	match_mid = re.match(r"^([A-Za-zÂÊÎÔÛŴŶÄÏÖËÁÉÍÓÚẂÝÀÈÌÒÙẀỲâêîôûŵŷäïöëáéíóúẃýàèìòùẁỳ']+)([^A-Za-zÂÊÎÔÛŴŶÄÏÖËÁÉÍÓÚẂÝÀÈÌÒÙẀỲâêîôûŵŷäïöëáéíóúẃýàèìòùẁỳ']+)([A-Za-zÂÊÎÔÛŴŶÄÏÖËÁÉÍÓÚẂÝÀÈÌÒÙẀỲâêîôûŵŷäïöëáéíóúẃýàèìòùẁỳ]+)$", token)
	if match_mid is not None:
		return check_token(match_mid.group(1)) + check_token(match_mid.group(2)) + check_token(match_mid.group(3))
	### apostrophes
	if len(re.findall("'", token)) != 0:
		if token.lower() in cy_lexicon:
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
			if len(split) == 3 and split[0].isalpha() and split[2].isalpha:
				if split[1] + split[2] in cy_lexicon:
					return [split[0], (split[1] + split[2])]
				else:
					return [token]
			else:
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
	#if sentence[-1:] == "." and sentence[-2:] != " .":
		#sentence = "{}{}".format(sentence[:-1], " .")
	tokens = token_split(sentence, total_tokens)
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

