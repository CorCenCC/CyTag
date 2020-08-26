#!usr/bin/env python3
#-*- coding: utf-8 -*-
import logging

logger = logging.getLogger("cy.reflists")

""" The appropriate rich POS tags that collapse into each basic POS tag """
tag_categories = [["Anon", ["Anon"]],
["E", ["Egu", "Ebu", "Egll", "Ebll", "Egbu", "Egbll", "Ep", "Epg", "Epb"]],
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
					["Ban", ["Banmeint", "Bandangg", "Bandangb", "Bandangd", "Banmedd1ll", "Banmedd1u", "Banmedd2ll", "Banmedd2u", "Banmedd3bu", "Banmedd3gu", "Banmedd3ll", "Bancynnar", "Banhwyr", "Bansym"]
					],
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
					["Ebych", ["Ebych"]],
					["Ymadr", ["Ymadr"]]
					]

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
						["Atdyf", ["Atd", "dyf"]],
						["Bansym", ["Ban", "sym"]],
						["Bansymmeint", ["Ban", "sym", "meint"]],
						["Banmeint", ["Ban", "meint"]],
						["Bansymcynnar", ["Ban", "sym", "cynnar"]],
						["Bancynnar", ["Ban", "cynnar"]],
					### Bancynnar = what Borsley et al (Syntax of Welsh) call "early postdeterminers"
						["Bansymhwyr", ["Ban", "sym", "hwyr"]],
						["Bansymhwyr", ["Ban", "hwyr"]],
					### Banhwyr = what Borsley et al (Syntax of Welsh) call "late postdeterminers"
						["Bandangb", ["Ban", "dang", "b"]],
						["Bandangg", ["Ban", "dang", "g"]],
						["Bandangd", ["Ban", "dang", "d"]],
						["Bandang", ["Ban", "dang"]],
					### Bandang = demonstrative determiner
						["Bangof", ["Ban", "gof"]],
					### Bangof = interrogative determiner "pa": "pa lyfr?"
						["Banmedd1ll", ["Ban", "medd", "1", "ll"]],
						["Banmedd1u", ["Ban", "medd", "1", "u"]],
						["Banmedd2ll", ["Ban", "medd", "2", "ll"]],
						["Banmedd2u", ["Ban", "medd", "2", "u"]],
						["Banmedd3bu", ["Ban", "medd", "3", "b", "u"]],
						["Banmedd3gu", ["Ban", "medd", "3", "g", "u"]],
						["Banmedd3du", ["Ban", "medd", "3", "d", "u"]],
						["Banmedd3ll", ["Ban", "medd", "3", "ll"]],
					### Ymadrodd - a tag for lemmas representing more than one part of speech, e.g. "'s'na'm" - "does yna ddim" (= "there is/are not")
						["Ymadr", ["Ymadr"]],
					### Anon - a tag for Anonymized data: the contents of <anon> tags in the CorCenCC data may range from a telephone number to a single name to a complete name (title + given name + surname) to an entire address, so part of speech is not easy to assign
						["Anon",["Anon"]]
						]

cyts = ["b", "c", "d", "f", "g", "j", "k", "l", "m", "n", "p", "r", "s", "t", "v", "z"]
cyts_twp = ("b", "c", "d", "f", "g", "j", "k", "l", "m", "n", "p", "r", "s", "t", "v", "z")
llaf = ["a", "e", "i", "o", "u", "y"]
llaf_twp = ("a", "e", "i", "o", "u", "y")
oldd_cym = ("o", "ian", "a", "io", "on", "wn", "ai", "em", "ais", "iaf", "odd", "och", "ion", "iwn", "wch", "ith", "yth", "iff", "yff", "wyd", "ech", "ent", "iais", "aist", "iodd", "ioch", "iwch", "iaist", "au", "on", "od", "iau", "ion", "oedd", "yn", "en", "af", "ach", "es", "iest", "est", "an")
diw_cym = {"a" : ["Bgorch2u", "Bpres3u"],
"af" : ["Bpres1u", "Anseith"],
"ai" : ["Bamherff3u", "Ell"], 
"ais" : ["Bgorff1u", "Bgorff2u"],
"aist" : ["Bgorff2u"], 
"an" : ["Bpres3ll"], 
"ant" : ["Bpres3ll"], 
"asai" : ["Bgorb3u"], 
"asant" : ["Bgorff3ll"], 
"asech" : ["Bgorb2ll"], 
"asem" : ["Bgorb1ll"], 
"asen" : ["Bgorb3ll"], 
"asent" : ["Bgorb3ll"], 
"asid" : ["Bgorbamhers"], 
"asit" : ["Bgorb2u"], 
"asoch" : ["Bgorff2ll"], 
"asom" : ["Bgorff1ll"], 
"aswn" : ["Bgorb1u"], 
"ia" : ["Bgorch2u", "Bpres3u"],
"iaf" : ["Bpres1u", "Anseith"],
"iai" : ["Bamherff3u", "Ell"], 
"iais" : ["Bgorff1u", "Bgorff2u"],
"iaist" : ["Bgorff2u"], 
"ian" : ["Bpres3ll"], 
"iant" : ["Bpres3ll"], 
"iasai" : ["Bgorb3u"], 
"iasant" : ["Bgorff3ll"], 
"iasech" : ["Bgorb2ll"], 
"iasem" : ["Bgorb1ll"], 
"iasen" : ["Bgorb3ll"], 
"iasent" : ["Bgorb3ll"], 
"iasid" : ["Bgorbamhers"], 
"iasit" : ["Bgorb2u"], 
"iasoch" : ["Bgorff2ll"], 
"iasom" : ["Bgorff1ll"], 
"iaswn" : ["Bgorb1u"], 
"ech" : ["Bamherff2ll"], 
"ed" : ["Bgorch3u"], 
"em" : ["Bamherff1ll"], 
"en" : ["Bgorch3ll", "Eu"],
"ent" : ["Bamherff3ll", "Bgorch3ll"],
"er" : ["Bdibdyfamhers", "Bgorchamhers"],
"e" : ["Bamherff3u"], 
"es" : ["Bgorff1u", "Bgorff2u"],
"est" : ["Bgorff2u"],  
"et" : ["Bamherff2u"], 
"iech" : ["Bamherff2ll"], 
"ied" : ["Bgorch3u"], 
"iem" : ["Bamherff1ll"], 
"ien" : ["Bgorch3ll", "Eu"],
"ient" : ["Bamherff3ll", "Bgorch3ll"],
"ier" : ["Bdibdyfamhers", "Bgorchamhers"],
"ie" : ["Bamherff3u"], 
"ies" : ["Bgorff1u", "Bgorff2u"],
"iest" : ["Bgorff2u"],  
"iet" : ["Bamherff2u"], 
"i" : ["Bpres2u"], 
"ia" : ["Bgorch2u", "Bpres3u"],
"id" : ["Bamherffamhers"], 
"iff" : ["Bdyf3u"], 
"io" : ["Be"],
"ion" : ["Bgorff1ll", "Bgorff3ll", "Ell"],
"ir" : ["Bpresamhers"], 
"it" : ["Bamherff2u"], 
"ith" : ["Bdyf3u"], 
"o" : ["Be", "Bdibdyf3u"],
"och" : ["Bdibdyf2ll", "Bgorff2ll"],
"odd" : ["Bgorff3u"], 
"om" : ["Bdibdyf1ll"], 
"on" : ["Bgorff1ll", "Bgorff3ll", "Ell"],
"ont" : ["Bdibdyf3ll"],
"ioch" : ["Bdibdyf2ll", "Bgorff2ll"],
"iodd" : ["Bgorff3u"], 
"iom" : ["Bdibdyf1ll"], 
"ion" : ["Bgorff1ll", "Bgorff3ll", "Ell"],
"iont" : ["Bdibdyf3ll"],  
"soch" : ["Bgorff2ll"], 
"som" : ["Bgorff1ll"], 
"son" : ["Bgorff3ll"], 
"wch" : ["Bgorch2ll", "Bpres2ll"],
"wn" : ["Bamherff1u", "Bgorch1ll", "Bpres1ll"],
"wyd" : ["Bgorffamhers"], 
"wyf" : ["Bdibdyf1u"], 
"iwch" : ["Bgorch2ll", "Bpres2ll"],
"iwn" : ["Bamherff1u", "Bgorch1ll", "Bpres1ll"],
"iwyd" : ["Bgorffamhers"], 
"iwyf" : ["Bdibdyf1u"], 
"iych" : ["Bdibdyf2u"],
"od" : ["Ell"],
"au" : ["Ell"],
"iau" : ["Ell"],
"oedd" : ["Ell"],
"yn" : ["Eu"],
"ach" : ["Anscym"]
}

toponymau_cym = ["aber", "allt", "caer", "gaer", "aer", "ngaer", "nghaer", "bryn", "capel", "gapel", "ngapel", "nghapel", "carn", "garn", "ngarn", "ngharn", "castell", "gastell", "ngastell", "nghastell", "cefn", "gefn", "ngefn", "nghefn", "coed", "goed", "ngoed", "nghoed", "croes", "groes", "ngroes", "nghroes", "crug", "grug", "ngrug", "nghrug", "cwm", "gwm", "ngwm", "nghwm", "cymer", "gymer", "ngymer", "nghymer", "dinas", "ddinas", "ninas", "dol", "ddol", "nol", "dyffryn", "ddyffryn", "nyffryn", "eglwys", "ffos", "garth", "ngarth", "glan", "lan", "nglan", "glyn", "lyn", "nglyn", "gwaun", "waun", "ngwaun", "hafod", "hendre", "llan", "llannerch", "llyn", "maen", "faen", "merthyr", "ferthyr", "moel", "foel", "morfa", "forfa", "mynydd", "fynydd", "nant", "ogof", "pant", "mhant", "bant", "parc", "mharc", "barc", "pen", "mhen", "ben", "penrhyn", "mhenrhyn", "benrhyn", "pentre", "mhentre", "bentre", "plas", "mhlas", "blas", "pont", "mhont", "bont", "porth", "mhorth", "borth", "pwll", "mhwll", "bwll", "rhaeadr", "raeadr", "rhiw", "riw", "rhos", "ros", "rhyd", "ryd", "sarn", "traeth", "draeth", "nhraeth", "tre", "dre", "nhre", "ynys", "ystrad"]

def toponym(gair):
	rhif = 9
	canl = 0
	while rhif > 2:
		if len(gair) > rhif+3:
			rhannau = []
			if gair[0:rhif] in toponymau_cym:
				return(True)
		rhif -= 1

def lookup_mutation(input_token):
	""" Return a list of all possible Welsh mutations of a given token """
	token = input_token.lower()
	unmutated = []
	if len(token) > 2 and  token[:2] == "ch":
		unmutated.append(("c{}".format(token[2:]), "am"))
	if len(token) > 2 and  token[:2] == "ph":
		unmutated.append(("p{}".format(token[2:]), "am"))
	if len(token) > 2 and  token[:2] == "th":
		unmutated.append(("t{}".format(token[2:]), "am"))
	if len(token) > 3 and  token[:3] == "ngh":
		unmutated.append(("c{}".format(token[3:]), "nm"))
	if len(token) > 2 and  token[:2] == "mh":
		unmutated.append(("p{}".format(token[2:]), "nm"))
	if len(token) > 2 and token[:2] == "nh":
		unmutated.append(("t{}".format(token[2:]), "nm"))
	if len(token) > 2 and token[:2] == "ng" and token[2] != "h":
		unmutated.append(("g{}".format(token[2:]), "nm"))
	if len(token) > 1 and token[:1] == "m" and token[1] != "h":
		unmutated.append(("b{}".format(token[1:]), "nm"))
	if len(token) > 1 and  token[:1] == "n" and token[1] not in ["h", "g"]:
		unmutated.append(("d{}".format(token[1:]), "nm"))
	if len(token) > 1 and  token[:1] == "g":
		unmutated.append(("c{}".format(token[1:]), "sm"))
	if len(token) > 1 and  token[:1] == "b":
		unmutated.append(("p{}".format(token[1:]), "sm"))
	if len(token) > 1 and  token[:1] == "d" and token[1] != "d":
		unmutated.append(("t{}".format(token[1:]), "sm"))
	if len(token) > 1 and  token[:1] == "f" and token[1] != "f":
		unmutated.append(("b{}".format(token[1:]), "sm"))
		unmutated.append(("m{}".format(token[1:]), "sm"))
	if len(token) > 1 and token[:1] == "l" and not token[1] == "l":
		unmutated.append(("ll{}".format(token[1:]), "sm"))
	if len(token) > 1 and token[:1] == "r" and token[1] != "h":
		unmutated.append(("rh{}".format(token[1:]), "sm"))
	if len(token) > 2 and token[:2] == "dd":
		unmutated.append(("d{}".format(token[2:]), "sm"))
	if len(token) > 2 and token[:2] == "ha":
		unmutated.append(("a{}".format(token[2:]), "hm"))
	if len(token) > 2 and token[:2] == "he":
		unmutated.append(("e{}".format(token[2:]), "hm"))
	if len(token) > 2 and token[:2] == "hi":
		unmutated.append(("i{}".format(token[2:]), "hm"))
	if len(token) > 2 and token[:2] == "ho":
		unmutated.append(("o{}".format(token[2:]), "hm"))
	if len(token) > 2 and token[:2] == "hu":
		unmutated.append(("u{}".format(token[2:]), "hm"))
	if len(token) > 3 and token[:2] == "hw":
		unmutated.append(("w{}".format(token[2:]), "hm"))
	if len(token) > 3 and token[:2] == "hy":
		unmutated.append(("y{}".format(token[2:]), "hm"))
	if len(token) > 2 and token[:1] in ["a", "e", "i", "o", "u", "w", "y"] and len(token) > 2:
		unmutated.append(("g{}".format(token), "sm"))
	if input_token[0].isupper():
		capitals = []
		for mutation in unmutated:
			capitals.append(("{}{}".format(mutation[0][:1].upper(), mutation[0][1:]), mutation[1]))
		unmutated = unmutated + capitals
	return unmutated 

def tag_morphology(tag):
	""" For a given (rich) POS tag, split it into a list of its morphological elements and return it """
	morphology = []
	if tag in [x[0] for x in morphological_table]:
		location = [x[0] for x in morphological_table].index(tag)
		morphology = morphological_table[location][1]
	else:
		morphology = [tag]
	return morphology
