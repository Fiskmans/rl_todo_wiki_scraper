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
linkFinder:str = r"\[\[[^\[\]]+\]\]" # "[[<something>]]" where <something> doesn't contain any [ or ] characters

def GetindentAndCleanLine(rawLine) -> (int, str):
	trimmed = rawLine.lstrip("*")
	return ((len(rawLine) - len(trimmed)), trimmed.strip())

def ParseQuestRequirement(requires, line, questNameToId, itemNameToId) -> bool: # returns True if subnodes in a list should be skipped
	if line.startswith("'''"): # sometimes there are headers bundled in for organization  
		return
	if line.startswith("The Ability") or line.startswith("The ability"):
		return
	if line.startswith("Must be able"):
		return
	if line.startswith("Be able"):
		return
	if line.startswith("Able to"):
		return
	if line.startswith("It is beneficial"):
		return

	code = mw.parse(line, skip_style_tags=True)

	requirementOnLine = False

	if line.startswith("{{"):
		boostable = len(util.Templates(code, "Boostable", False)) > 0
		for scp in util.Templates(code, "SCP", False):
			if len(scp.params) < 2:
				continue
			
			type = str(scp.get(1).value)
			amount = int(str(scp.get(2).value).replace(",", ""))
			
			id = "unkown"

			match type:
				case "Quest":
					id = "progression.quest_points"
				case "Combat":
					id = "level.combat"
				case "Total":
					id = "level.total"
				case "Diary":
					print("I dont know what to do with this")
				case "Combatachievement":
					print("I dont know what to do with this")
				case "Combatstyle":
					print("I dont know what to do with this")
				case "Dd":
					print("I dont know what to do with this")
				case "Favour":
					print("I dont know what to do with this")
				case "Minigame":
					print("I dont know what to do with this")
				case "Music":
					print("I dont know what to do with this")
				case "Raid":
					print("I dont know what to do with this")
				case "Time":
					print("I dont know what to do with this")
				
				case _:
					id = "level." + type

			
			if id == "unkown":
				print("unkown id for {}.".format(type))
				continue
			
			requires[id] = amount
			requirementOnLine = True

	if not requirementOnLine:
		match = re.search(linkFinder, line)

		if match:
			requiredName = match.group()[2:-2]
			if requiredName not in questNameToId:
				if requiredName in itemNameToId:
					requires[itemNameToId[requiredName]]
				else:
				print("Quest {} of line [{}] does not have an id".format(requiredQuestName, line))
				return False
			requires[questNameToId[requiredName]] = 1
			requirementOnLine = True
#		else:
#			print("No match on: {}".format(line))

#	if not requirementOnLine:
#		print("No requirement on: {}".format(line))

	return requirementOnLine

def ParseQuestItem(requires, line, itemNameToId) -> bool: # returns True if subnodes in a list should be skipped
	if line.startswith("'''"): # sometimes there are headers bundled in for organization  
		return
	if line.startswith("None"):
		return
	if line.startswith("Food"):
		return
	if line.startswith("Combat equipment"):
		return
	if "inventory" in line: # warnings about slot counts for uim's mostly
		return

	match = re.search(linkFinder, line)
	if match:
		itemName = match.group()[2:-2]
		if itemName not in itemNameToId:
#			print("{} in {} does not have an id".format(itemName, line))
			return
		requires[itemNameToId[itemName]] = 1 # TODO figure out amount
		return

	print("unkown item: {}".format(line))

def ParseQuestReward(makes, line, itemNameToId):
	if line.startswith("{{"):

		code = mw.parse(line)
		for scp in util.Templates(code, "SCP", False):
			if len(scp.params) < 2:
				continue
			
			type = str(scp.get(1).value)
			amount = float(str(scp.get(2).value).replace(",", ""))
			
			id = "unkown"

			match type:
				case "Quest":
					print("I dont know what to do with this")
				case "Combat":
					print("I dont know what to do with this")
				case "Total":
					print("I dont know what to do with this")
				case "Diary":
					print("I dont know what to do with this")
				case "Combatachievement":
					print("I dont know what to do with this")
				case "Combatstyle":
					print("I dont know what to do with this")
				case "Dd":
					print("I dont know what to do with this")
				case "Favour":
					print("I dont know what to do with this")
				case "Minigame":
					print("I dont know what to do with this")
				case "Music":
					print("I dont know what to do with this")
				case "Raid":
					print("I dont know what to do with this")
				case "Time":
					print("I dont know what to do with this")
				
				case _:
					id = "xp." + type

			
			if id == "unkown":
				print("unkown id for {}.".format(type))
				continue
			
			makes[id] = amount
			return
	
	match = re.search(linkFinder, line)
	if match and match.start() == 0:
		itemName = match.group()[2:-2]
		if itemName not in itemNameToId:
#			print("{} in {} does not have an id".format(itemName, line))
			return
		makes[itemNameToId[itemName]] = 1 # TODO figure out amount
		return


def ParseQuest(name, details, rewards, itemNameToId, questNameToId):
	simpleDetails = util.DictFromAssignments(details.params)

	makes = {}
	requires = {}
	if name not in questNameToId:
		print("ERROR with " + name)

	makes[questNameToId[name]] = 1

	skipToNextIndentOf = 0
	difficulty = "unkown"

	if "difficulty" in simpleDetails:
		difficulty = simpleDetails["difficulty"]
		match difficulty:
			case "1":
				difficulty = "Novice"
			case "2":
				difficulty = "Intermediate"

	if "requirements" in simpleDetails:
		for line in simpleDetails["requirements"].split("\n"):
			indent, req = GetindentAndCleanLine(line)
			if skipToNextIndentOf > 0 and indent > skipToNextIndentOf:
				continue

			skipToNextIndentOf = 0

			if ParseQuestRequirement(requires, req, questNameToId):
				skipToNextIndentOf = indent
				continue

	if "items" in simpleDetails:
		for line in simpleDetails["items"].split("\n"):
			indent, item = GetindentAndCleanLine(line)
			ParseQuestItem(requires, item, itemNameToId)
	
	if rewards is not None:
		simpleRewards = util.DictFromAssignments(rewards.params)
		if "qp" in simpleRewards:
			makes["progression.quest_points"] = int(simpleRewards["qp"])
		
		if "rewards" in simpleRewards:
			for line in simpleRewards["rewards"].split("\n"):
				indent, reward = GetindentAndCleanLine(line)
				ParseQuestReward(makes, reward, itemNameToId)

	method = {}
	method["name"] = "Complete " + name
	method["makes"] = makes
	method["takes"] = {} # its too hard to figure out which items are consumed during a quest so they're all tracked as required
	method["requires"] = requires

	target_file = "baked/Quests/{}/{}.json".format(difficulty, util.SafeName(name))

	os.makedirs(os.path.dirname(target_file), exist_ok=True)
	with open(target_file, "w+") as fi:
		json.dump(method, fi, indent=2)

def BuildMethods(pages, itemNameToId, questNameToId):

	for name, page in pages.items():
		if name.startswith("Category"):
			continue
		if name.startswith("Quests/"):
			continue

		if "Quick guide" in name:
			continue

		try:
			code = mw.parse(page, skip_style_tags=True)

			if util.has_template("Future Content", code):
				continue

			details = None
			rewards = None

			for detailsNode in util.Templates(code, "Quest details", False):
				details = detailsNode
				break
			for rewardsNode in util.Templates(code, "Quest rewards", False):
				rewards = rewardsNode
				break
			
			if details is None:
				print("{} missing details".format(name))
				continue

			ParseQuest(name, details, rewards, itemNameToId, questNameToId)
		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			print("Quest {} failed:".format(name))
			traceback.print_exc()


def BuildIdTable(pages) -> Dict[str, str]:

	cache_file_name = "quests_id.cache.json"
	if use_cache and os.path.isfile(cache_file_name):
		with open(cache_file_name, "r") as fi:
			print("Using cached quest name to id table")
			return json.load(fi)

	out = {}

	out["Warriors' Guild"] = "access.warriors_guild"
	out["player-owned house"] = "access.poh"
	
	print("Generating quest name to id table")

	for name, page in pages.items():
		if name.startswith("Category"):
			continue
		if name.startswith("Quests/"):
			continue
		if "Quick guide" in name:
			continue

		if not name in out:
			out[name] = "quest." + util.SafeName(name)

	with open(cache_file_name, "w+") as fi:
		json.dump(out, fi)

	return out

def run(itemNameToId):
	index = []

	quest_pages = api.query_category("Quests") | api.query_category("Miniquests")


	questNameToId = BuildIdTable(quest_pages)
	BuildMethods(quest_pages, itemNameToId, questNameToId)