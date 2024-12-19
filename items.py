import os
import sys
import traceback
import re
import mwparserfromhell as mw
import api
import util
from typing import *
import urllib.request
import json

use_cache: bool = True

def EachParamCategory(params, category):
	index = 1
	while True:
		out = {}

		filter = category + str(index)
		#print("Looking for [{}] in {}".format(filter, params))

		for val in params:
			if not val.startswith(filter):
				continue
			
			parts = val[len(filter) : ].split("=", 1)
			if len(parts) == 2:
				out[parts[0].strip()] = parts[1].strip()
			else:
				out[parts[0].strip()] = ""
				
		if not out:
			break

		yield out
		index += 1


def ParseFloat(dict, key, default):
	try:
		return float(dict[key].strip().replace(",", ""))
	except:
		return default

def ParseInt(dict, key, default):
	try:
		return int(dict[key].strip().replace(",", ""))
	except:
		return default

def ParseRecipe(pageName, recipeNode, context, nameToIdLookup, methodSink):
	verb = "???"
	suffix = ""
	
	category = ""

	takes = {}
	makes = {}
	requires = {}

	for skill in EachParamCategory(recipeNode.params, "skill"):
		#print("Skill: {}".format(skill))
		if "" not in skill or skill[""] == "":
			continue

		name = skill[""]
		level = ParseInt(skill, "lvl", 1)
		xp = ParseFloat(skill, "exp", 0.0)
		boostable = "boostable" in skill and skill["boostable"] == "yes"

		if level > 1:
			requires["level." + name] = level

		if xp > 0.0:
			makes["xp." + name] = xp

		match name:
			case "Crafting":
				verb = "Craft"
			case "Smithing":
				verb = "Smith"
			case "Fletching":
				verb = "Fletch" 
			case "Herblore":
				verb = "Mix" 
			case "Magic":
				verb = "Enchant" 
			case "Construction":
				verb = "Build"
			case "Cooking":
				if xp > 0:
					verb = "Cook" 
				else:
					verb = "Prepare"
			case "Farming":
				verb = "Plant" 
			case "Runecraft":
				verb = "Infuse"
			case "Prayer":
				verb = "Bless"
		
		category = name + "/"

	for mat in EachParamCategory(recipeNode.params, "mat"):
		if not "" in mat:
			continue
		name = mat[""]
		quantity = ParseInt(mat, "quantity", 1)

		if not name in nameToIdLookup:
			print("Material {} in {} does not have an id".format(name, pageName));
			continue

		takes[nameToIdLookup[name]] = quantity

	for output in EachParamCategory(recipeNode.params, "output"):
		name = output[""]
		quantity = ParseInt(output, "quantity", 1)

		if not name in nameToIdLookup:
			print("Output {} in {} does not have an id".format(name, pageName));
			continue

		makes[nameToIdLookup[name]] = quantity

	simple = util.DictFromAssignments(recipeNode.params)

	if "tools" in simple:
		for tool in simple["tools"].split(","):
			name = tool.strip()

			if name == "Needle":
				verb = "Sew"
				category += "Sewing/"

			if name == "Gardening trowel":
				verb = "Plant"
				category += "Planting/"

			if name == "Pestle and mortar" or name == "Pestle and mortar (The Gauntlet)":
				verb = "Crush"
				category += "Crushing/"

			if name == "Knife":
				verb = "Cut"
				category += "Cutting/"

			if name == "Chisel":
				verb = "Chisel"
				category += "Chisel/"

			if name == "Sieve":
				verb = "Sieve"
				category += "Sieve/"

			if name == "Pirate hat":
				verb = "minigame"
				category += "Trouble_Brewing/"

			if name == "Hammer" and verb != "Smith" and verb != "Build":
				verb = "Break"
				category += "Break/"
			
			if not name in nameToIdLookup:
				print("Tool {} in {} does not have an id".format(name, pageName));
				continue
			requires[nameToIdLookup[name]] = 1

	if "facilities" in simple:
		faciliy = ""
		for facility in simple["facilities"].split(","):
			name = facility.strip()

			if name == "":
				continue

			if name == "Singing bowl":
				verb = "Sing"
				category = "Singing/"
				requires["quest.song_of_the_elves"] = 1
			
			if name == "Woodcutting stump":
				verb = "Chop"

			if name == "Taxidermist":
				verb = "Taxidermi"

			if name == "Monument":
				verb = "Replace for"

			if name == "Exposed altar":
				verb = "Bless"

			if name == "Bone grinder":
				verb = "Grind"

			if name in [ "Ghommal", "Zooknock", "Dampe", "Peer the seer", "Nigel", "Ned", "Aggie", "Wizard Jalarast", "Fancy clothes store", "Alrena", "Zaff", "Wizard Mizgog", "Watchtower Wizard", "Turael", "Abbot Langley", "Apothecary" ]:
				verb = "Commission"
			
			suffix = " at " + name
			facility = util.SafeName(name)

		if facility != "":
			if category == "":
				category = "Facility/"

			category += facility + "/"

	if not requires and takes and makes and category == "":
		verb = "Make"
		category += "Make/"

	if "item.5418" in takes or "item.5376" in takes: # Empty sack, Basket
		verb = "Fill"
		category += "Fill/"

	if "item.11740" in takes: # Scroll of redirection
		Verb = "Redirect"
		category = "Make/"

	method = {}

	method["takes"] = takes
	method["makes"] = makes
	method["requires"] = requires
	method["name"] = verb + " " + pageName + suffix

	if verb == "???":
		print("{}/{}: Unkown verb".format(category, pageName))
		category = "Failed/" + category

	if not makes:
		print("{}/{}: Doesnt make anything".format(category, pageName))
		category = "Failed/" + category

	method["category"] = category

	methodSink.append(method)


def FindRecipes(item, code, context, nameToIdLookup, methodSink):

	index = 0;

	for recipe in code.filter_templates(matches=lambda t: t.name.matches("Recipe"), recursive=False):
		index += 1
		subcontext = context.copy()
		ParseRecipe(item, recipe, subcontext, nameToIdLookup, methodSink);

	for tabs in code.filter_templates(matches=lambda t: t.name.matches("Tabber"), recursive=False):
		index = 1;
		

	#util.write_json("stats.json", "stats.ids.min.json", stats)

def FindIds(pages) -> Dict[str, str]:
	out = {}
	cache_file_name = "item_ids.cache.json"
	if use_cache and os.path.isfile(cache_file_name):
		with open(cache_file_name, "r") as fi:
			print("Using cached item name to id table")
			return json.load(fi)
	
	print("Generating item name to id table")

	out["Pickaxe"] = "any.mining_tool"

	for name, page in pages.items():
		if name.startswith("Category:"):
			continue

		try:
			code = mw.parse(page["content"], skip_style_tags=True)

			if util.has_template("Interface items", code) or util.has_template("Unobtainable items", code):
				continue

			for (vid, version) in util.each_version("Infobox Item", code):
				if "removal" in version and not str(version["removal"]).strip().lower() in ["", "no", "n/a"]:
					continue


				if not "id" in version:
					print("{}: no id".format(name))
					continue

				if version["id"].strip() == "":
					print("{}: empty id".format(name))
					continue

				if version["id"].strip().startswith("beta"):
					continue

				if not "name" in version:
					print("{}: no name".format(name))
					continue

				id = ParseInt(version, "id", -1)
				item_name = version["name"].strip()
				if id == -1:
					print("{}: failed to parse id [{}]".format(name, version["id"].strip()))
					continue

				inserted = False;

				if not item_name in out:
					out[item_name] = "item." + str(id)
					inserted = True

				if not name in out:
					out[name] = "item." + str(id)
					inserted = True

				if not inserted:
					print("Duplicate item [{}] {} and {}".format(item_name, out[item_name], "item." + str(id)))

				if "redirects" in page:
					for redirect in page["redirects"]:
						if not redirect in out:
							out[redirect] = "item." + str(id)
					
				#print("{}: item.{}".format(name, str(id)))

		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			print("Item {} failed:".format(name))
			traceback.print_exc()

	with open(cache_file_name, "w+") as fi:
		json.dump(out, fi)

	return out

def RemoveUnsupportedFormatting(page):
	return page.replace("<tabber>","").replace("</tabber>", "")

def BuildMethods(nameToIdLookup, pages, methodSink):

	print("Building methods")

	for name, page in pages.items():
		if name.startswith("Category:"):
			continue

		try:
			code = mw.parse(RemoveUnsupportedFormatting(page["content"]), skip_style_tags=True)

			if util.has_template("Interface items", code) or util.has_template("Unobtainable items", code):
				continue

			isRemoved = False

			for info in code.filter_templates(matches=lambda t: t.name.matches("Infobox Item"), recursive=False):
				simpleView = util.DictFromAssignments(info.params)
				if "removal" in simpleView and not str(simpleView["removal"]).strip().lower() in ["", "no", "n/a"]:
					isRemoved = True

			if isRemoved:
				continue

			FindRecipes(name.strip(), code, {}, nameToIdLookup, methodSink);

		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			print("Item {} failed:".format(name))
			traceback.print_exc()

def run(methodSink):
	item_pages = api.query_category("Items")

	nameToIdLookup = FindIds(item_pages)
	BuildMethods(nameToIdLookup, item_pages, methodSink)

	return nameToIdLookup

