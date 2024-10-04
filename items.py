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

FacilityMappings: Dict[str, str] = {
	"Blast furnace":				"Smelt",
	"Blast Furnace":				"Smelt",
	"Volcanic Forge":				"Smelt",
	"Cooking range":				"Cook",
	"Clay oven":					"Cook",
	"Fire":							"Cook",
	"Brewery":						"Brew",
	"Furnace":						"Cast",
	"Singing Bowl": 				"Sing", 
	"Singing bowl": 				"Sing", 
	"Singing Bowl (The Gauntlet)":	"Sing", 
	"Singing Bowl (The Corrupted Gauntlet){{!}}Singing Bowl":	"Sing", 
	"Woodcutting stump": 			"Chop", 
	"Taxidermist": 					"Taxideri", 
	"Monument": 					"Replace for", 
	"Exposed altar": 				"Bless", 
	"Bone grinder": 				"Grind", 
	"Windmill": 					"Grind", 
	"Sawmill":						"Saw",
	"Water":						"Fill",
	"Water Pump (The Gauntlet)":	"Fill",
	"Sand pit":						"Fill",
	"Sandstrom":					"Fill",
	"Potter's Wheel":				"Spin",
	"Spinning wheel":				"Spin",
	"Loom":							"Weave",
	"Pottery Oven":					"Fire",
	"Dairy churn":					"Churn",
	"Swampy sink":					"Dip",
	"Ectofuntus":					"Dip",
	"Preparation Table":			"Cut open",
	"Obelisk of Air":				"Infuse",
	"Obelisk of Water":				"Infuse",
	"Obelisk of Earth":				"Infuse",
	"Obelisk of Fire":				"Infuse",
	"Air Altar":					"Infuse",
	"Water Altar":					"Infuse",
	"Earth Altar":					"Infuse",
	"Fire Altar":					"Infuse",
	"Body Altar":					"Infuse",
	"Mind Altar":					"Infuse",
	"Law Altar":					"Infuse",
	"Nature Altar":					"Infuse",
	"Chaos Altar":					"Infuse",
	"Death Altar":					"Infuse",
	"Blood Altar":					"Infuse",
	"Soul Altar":					"Infuse",
	"Wrath Altar":					"Infuse",
	"Extract orifice":				"Extract",
	"Shield easel":					"Paint",
	"Banner easel":					"Paint",
	"Pluming stand":				"Plume",
	"Crafting table 1":				"Craft",
	"Crafting table 2":				"Craft",
	"Crafting table 3":				"Craft",
	"Crafting table 4":				"Craft",
	"Elnock Inquisitor": 			"Exchange", 
	"Sbott": 						"Tan", 
	"Tannery": 						"Tan", 
	"Eodan": 						"Tan", 
	"Wooden workbench":				"Build",
	"Oak workbench":				"Build",
	"Steel framed workbench":		"Build",
	"Bench with vice":				"Build",
	"Bench with lathe":				"Build",
	"Bank": 						"Exchange", 
	"Fossegrimen":					"Enchant",
	"Refiner":						"Refine",
	"Oak lectern":					"Infuse",
	"Lectern (Lunar)":				"Infuse",
	"Lectern (Arceus)":				"Infuse",
	"Lectern (Ancient)":			"Infuse",
	"Spirit of Scorpius":			"Bless",
	"Adros Mai":					"Commission",
	"Oziach":						"Commission",
	"Madam Sikaro":					"Commission",
	"Elite Void Knight":			"Commission",
	"Dunstan": 						"Commission", 
	"Ghommal": 						"Commission", 
	"Skulgrimen": 					"Commission", 
	"Zooknock": 					"Commission", 
	"Dampe": 						"Commission", 
	"Peer the Seer": 				"Commission", 
	"Nigel": 						"Commission", 
	"Ned": 							"Commission", 
	"Aggie": 						"Commission", 
	"Wizard Jalarast": 				"Commission", 
	"Fancy Clothes Store": 			"Commission", 
	"Alrena": 						"Commission", 
	"Zaff": 						"Commission", 
	"Wizard Mizgog": 				"Commission", 
	"Watchtower Wizard": 			"Commission", 
	"Turael": 						"Commission", 
	"Abbot Langley": 				"Commission", 
	"Apothecary": 					"Commission",
	"Gita Prymes": 					"Commission",
	"Sigli the Huntsman": 			"Commission",
	"Lava trough": 					"Fill", #['A stone bowl']
	"The Overseer": 				"Assemble", #['Abyssal bludgeon']
	"Rewards Guardian": 			"Infuse", #['Abyssal needle']
	"Phabelle Bile": 				"Commission", #['Accursed sceptre']
	"Barbarian anvil": 				"Smith", #['Adamant hasta', 'Adamant spear', 'Bronze hasta', 'Bronze spear', 'Iron spear', 'Iron hasta', 'Mithril hasta', 'Mithril spear', 'Rune hasta', 'Rune spear', 'Steel hasta', 'Steel spear']
	"Crystal ball space": 			"Change element to", #['Air battlestaff', 'Air battlestaff', 'Air battlestaff', 'Earth battlestaff', 'Earth battlestaff', 'Earth battlestaff', 'Fire battlestaff', 'Fire battlestaff', 'Fire battlestaff', 'Mystic air staff', 'Mystic air staff', 'Mystic air staff', 'Mystic fire staff', 'Mystic fire staff', 'Mystic fire staff', 'Mystic earth staff', 'Mystic earth staff', 'Mystic earth staff', 'Mystic water staff', 'Mystic water staff', 'Mystic water staff', 'Staff of earth', 'Staff of earth', 'Staff of earth', 'Staff of fire', 'Staff of fire', 'Staff of fire', 'Staff of air', 'Staff of air', 'Staff of air', 'Staff of water', 'Staff of water', 'Staff of water', 'Water battlestaff', 'Water battlestaff', 'Water battlestaff']
	"Mixing vessel":				"Mix", #['Alco-augmentator', 'Anti-leech lotion', 'Aqualux amalgam', 'Azure aura mix', 'Liplack liquor', 'Mammoth-might mix', "Marley's moonlight", 'Megalite liquid', 'Mixalot', 'Mystic mana amalgam']
	"Strange Machine (wyvern shield){{!}}Strange Machine": "Assemble", #['Ancient wyvern shield']
	"Eblis": 						"Commission", #['Ancient sceptre']
	"Friendly Forester": 			"Sell for", #['Anima-infused bark', 'Anima-infused bark', 'Anima-infused bark', 'Anima-infused bark', 'Anima-infused bark']
	"Apple Press": 					"Press", #['Apple mush']
	"Lectern (Arceuus)": 			"Infuse", #['Ape atoll teleport (tablet)', 'Arceuus library teleport (tablet)', 'Barrows teleport (tablet)', 'Battlefront teleport (tablet)', 'Cemetery teleport (tablet)', 'Draynor manor teleport (tablet)', "Fenkenstrain's castle teleport (tablet)", 'Harmony island teleport (tablet)', 'Mind altar teleport (tablet)', 'Salve graveyard teleport (tablet)', 'West ardougne teleport (tablet)']
	"Teak eagle lectern": 			"Infuse", #['Ardougne teleport (tablet)', 'Camelot teleport (tablet)', 'Kourend castle teleport (tablet)']
	"Dom Onion's Reward Shop": 		"Infuse", #['Archers ring (i)', 'Berserker ring (i)', 'Black mask (i)', 'Granite ring (i)', 'Ring of the gods (i)', 'Ring of suffering (i)', 'Salve amulet(i)', 'Salve amulet(ei)', 'Salve amulet(ei)', 'Seers ring (i)', 'Slayer helmet (i)', 'Slayer helmet (i)', 'Treasonous ring (i)', 'Tyrannical ring (i)', 'Warrior ring (i)']
	"Soul Wars Reward Shop": 		"Infuse", #['Archers ring (i)', 'Berserker ring (i)', 'Black mask (i)', 'Granite ring (i)', 'Ring of the gods (i)', 'Ring of suffering (i)', 'Salve amulet(i)', 'Salve amulet(ei)', 'Salve amulet(ei)', 'Seers ring (i)', 'Slayer helmet (i)', 'Slayer helmet (i)', 'Treasonous ring (i)', 'Tyrannical ring (i)', 'Warrior ring (i)']
	"Altar (Catacombs of Kourend)": "Infuse", #['Arclight']
	"Fermentation Vat": 			"Ferment", #['Arder-musca poison']
	"Astral Altar": 				"Infuse", #['Astral rune', 'Astral rune']
	"Patchy": 						"Sew", #['Bandana eyepatch (red)', 'Bandana eyepatch (brown)', 'Bandana eyepatch (blue)', 'Bandana eyepatch (white)', 'Beret mask', 'Cavalier mask', 'Crabclaw hook', 'Dark flippers', 'Double eye patch', 'Hat eyepatch', 'Partyhat & specs', 'Pirate hat & patch', 'Top hat & monocle']
	"Ancient Forge": 				"Smelt", #['Bandosian components', 'Bandosian components']
	"Smith": 						"Fix", #['Barrelchest anchor']
	"Barronite Crusher": 			"Crush", #['Barronite shards']
	"Ramarno": 						"Fix", #['Barronite mace', 'Imcando hammer']
	"Candle maker": 				"Make", #['Black candle']
	"Shrine of Ralos": 				"Bless", #["Blessed dizana's quiver", 'Sunfire rune', 'Sunfire rune', 'Sunfire rune']
	"Gujuo": 						"Bless", #['Blessed gold bowl']
	"Drezel": 						"Bless", #['Blessed water']
	"Blood Altar (Kourend)": 		"Infuse", #['Blood rune']
	"Ali the dyer": 				"Trade", #['Blue dye', 'Red dye', 'Yellow dye']
	"Thurgo": 						"Commission", #['Blurite sword']
	"Mahogany demon lectern": 		"Infuse", #['Bones to peaches (tablet)', 'Enchant onyx', 'Enchant dragonstone']
	"Demon lectern": 				"Infuse", #['Bones to bananas (tablet)', 'Enchant emerald or jade']
	"Historian Aldo": 				"Commission", #['Bone mace', 'Bone shortbow', 'Bone staff']
	"Sulphur Vent (Mount Karuulm)": "Collect", #['Bottled dragonbreath']
	"Dark Altar": 					"Infuse", #['Broken glass', 'Dark essence block']
	"Leela": 						"Collect", #['Bronze key (Prince Ali Rescue)']
	"Sandstorm": 					"Fill", #['Bucket of sand', 'Bucket of sand', 'Bucket of sand', 'Bucket of sand']
	"Dairy cow": 					"Milk", #['Bucket of milk']
	"Pool of Slime": 				"Fill", #['Bucket of slime']
	"Tree": 						"Tap", #['Bucket of sap']
	"Lamp oil still": 				"Fill", #['Bullseye lantern', 'Impling jar']
	"Runic altar{{!}}Catalytic runic altar": "Infuse", #['Catalytic tiara']
	"Forestry Shop": 				"Buy", #['Clothes pouch blueprint', 'Forestry hat', 'Forestry top', 'Forestry legs', 'Forestry boots', 'Funky shaped log', 'Log brace']
	"Mahogany eagle lectern": 		"Infuse", #['Civitas illa fortis teleport (tablet)', 'Teleport to house (tablet)', 'Watchtower teleport (tablet)']
	"Compost Bin": 					"Compost", #['Compost', 'Rotten tomato', 'Supercompost', 'Supercompost', 'Ultracompost', 'Ultracompost']
	"Big Compost Bin": 				"Compost", #['Compost', 'Rotten tomato', 'Supercompost', 'Supercompost', 'Ultracompost', 'Ultracompost']
	"Ogre spit-roast": 				"Cook", #['Cooked chicken', 'Cooked chompy', 'Cooked jubbly']
	"Cosmic Altar": 				"Infuse", #['Cosmic tiara', 'Cosmic rune', 'Cosmic rune', 'Cosmic rune', 'Medium cell']
	"Workbench (Elemental Workshop)": "Smith", #['Crane claw', 'Elemental helmet', 'Elemental shield', 'Elemental shield', 'Mind helmet', 'Mind shield']
	"Ilfeen": 						"Sing", #['Crystal bow', 'Crystal halberd', 'Crystal shield']
	"Islwyn": 						"Sing", #['Crystal halberd']
	"Thakkrad Sigmundson": 			"Cure", #['Cured yak-hide']
	"Dragon forge": 				"Smith", #['Dragon kiteshield', 'Dragon key', 'Dragon platebody']
	"Nurmof": 						"Fix", #['Dragon pickaxe']
	"Furnace (Elemental Workshop)": "Smelt", #['Elemental metal', 'Elemental metal']
	"Runic altar{{!}}Any elemental rune altar": "Infuse", #['Elemental tiara']
	"Teak demon lectern": 			"Infuse", #['Enchant diamond', 'Enchant ruby or topaz']
	"Cauldron of Thunder": 			"Enchant", #['Enchanted bear', 'Enchanted chicken', 'Enchanted beef', 'Enchanted rat']
	"Belona": 						"Commission", #['Expert mining gloves']
	"Eagle lectern": 				"Infuse", #['Falador teleport (tablet)', 'Lumbridge teleport (tablet)']
	"Farming patch": 				"Fill", #['Filled plant pot']
	"Machinery": 					"Make", #['Ferocious gloves']
	"Rack (Mourner Headquarters)#Gnome{{!}}Gnome on a rack": "Fix", #['Fixed device']
	"Workbench (Guardians of the Rift)": "Make", #['Guardian essence']
	"Hay bale": 					"Search for", #['Hay sack']
	"Haystack": 					"Search for", #['Hay sack']
	"Shrine (Tempoross Cove)": 		"Cook", #['Harpoonfish']
	"Brother Jered": 				"Bless", #['Holy symbol']
	"Dark Mage": 					"Upgrade", #["Iban's staff (u)"]
	"Altar (Zalcano)": 				"Imbue", #['Imbued tephra']
	"Metal Press": 					"Press", #['Iron sheet']
	"Fountain (wine)": 				"Fill", #['Jug of wine']
	"Charcoal furnace": 			"Cook", #['Juniper charcoal']
	"Lady Keli": 					"Imprint", #['Key print']
	"Mycelium pool": 				"Enrich", #['Large enriched bone', 'Large enriched bone', 'Large enriched bone', 'Large enriched bone', 'Large enriched bone', 'Large enriched bone', 'Medium enriched bone', 'Medium enriched bone', 'Medium enriched bone', 'Medium enriched bone', 'Medium enriched bone', 'Medium enriched bone', 'Rare enriched bone', 'Rare enriched bone', 'Rare enriched bone', 'Rare enriched bone', 'Rare enriched bone', 'Rare enriched bone', 'Rare enriched bone', 'Small enriched bone', 'Small enriched bone', 'Small enriched bone', 'Small enriched bone', 'Small enriched bone', 'Small enriched bone']
	"Wall of flame": 				"Fuse", #["M'speak amulet (unstrung)", 'Uncut zenyte']
	"Lovakite furnace": 			"Smelt", #['Lovakite bar', 'Lovakite bar']
	"Bunsen burner": 				"Burn", #['Metal spade', 'Tin (Recruitment Drive)']
	"Well (Paterdomus)": 			"Dip", #['Murky water', 'Rod of ivandis']
	"Thormac": 						"Enchant", #['Mystic air staff', 'Mystic air staff', 'Mystic air staff', 'Mystic fire staff', 'Mystic fire staff', 'Mystic fire staff', 'Mystic earth staff', 'Mystic earth staff', 'Mystic earth staff', 'Mystic dust staff', 'Mystic dust staff', 'Mystic dust staff', 'Mystic water staff', 'Mystic water staff', 'Mystic water staff', 'Mystic lava staff', 'Mystic lava staff', 'Mystic lava staff', 'Mystic steam staff', 'Mystic steam staff', 'Mystic steam staff', 'Mystic mud staff', 'Mystic mud staff', 'Mystic mud staff', 'Mystic smoke staff', 'Mystic smoke staff', 'Mystic smoke staff', 'Mystic steam staff (or)', 'Mystic steam staff (or)', 'Mystic steam staff (or)', 'Mystic mist staff', 'Mystic mist staff', 'Mystic mist staff', 'Mystic lava staff (or)', 'Mystic lava staff (or)', 'Mystic lava staff (or)']
	"Suntrap": 						"Dry", #['Pile of salt']
	"An experimental anvil": 		"Experiment with", #['Prototype dart tip']
	"Uncooking pot": 				"Uncook", #['Raw fishlike thing']
	"Furnace (Zalcano)": 			"Refine", #['Refined tephra']
	"Murky Matt (runes)": 			"Enchant", #['Ring of forging']
	"Fire altar (Flamtaer)": 		"Putify", #['Sacred oil', 'Sacred oil', 'Sacred oil', 'Sacred oil', 'Serum 208', 'Serum 208', 'Serum 208', 'Serum 208']
	"Altar of nature": 				"Bless", #['Silver sickle (b)']
	"Doric's Whetstone": 			"Grind", #['Slender blade']
	"Solztun": 						"Infuse", #['Skull sceptre (i)']
	"Key Master": 					"Fix", #['Soul bearer']
	"Juna": 						"Build", #['Staff of balance']
	"Rock (snake cooker)": 			"Cook", #['Stuffed snake']
	"Rimae Sirsalis": 				"Tan", #['Suqah leather']
	"Eluned": 						"Sing", #['Teleport crystal']
	"Lieve McCracken": 				"Enchant", #['Trident of the seas (e)', 'Trident of the swamp (e)']
	"Andros Mai": 					"Combine", #['Ursine chainmace']
	"Derse Venator": 				"Combine", #['Webweaver bow']
	"Otto Godblessed": 				"Convert to" #['Zamorakian hasta', 'Zamorakian hasta']
}

def NormalizeName(name):
	return name.lower().replace(" ", "_")

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

def ParseRecipe(pageName, index, recipeNode, nameToIdLookup, methodSink, missingFacilities):
	verb = "???"
	suffix = ""
	
	file_path = ""

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

		file_path = name + "/"

		match name:
			case "Crafting":
				verb = "Craft"
				firstWord = util.SafeName(pageName.split(' ', 1)[0])

				if firstWord in [ "yellow", "red", "purple", "origami", "pink", "orange", "leather", "green", "broodoo", "blue", "black" ]:
					file_path += firstWord + "/"
				
				if "Amulet" in pageName or "amulet" in pageName:
					file_path += "Amulet/"

			case "Smithing":
				verb = "Smith"
			case "Fletching":
				verb = "Fletch" 
				file_path += util.SafeName(pageName.split(' ', 1)[0]) + "/"
			case "Herblore":
				verb = "Mix" 
			case "Magic":
				verb = "Enchant" 
			case "Construction":
				verb = "Build"
			case "Cooking":
				if xp > 0:
					verb = "Cook"
					file_path += "Cook/" 
					if "pizza" in pageName or "Pizza" in pageName:
						file_path += "pizza/"
				else:
					if "Burnt" in pageName:
						verb = "Burn"
						file_path += "Burn/"
					else:
						verb = "Prepare"
						file_path += "Prepare/"
						if "pizza" in pageName or "Pizza" in pageName:
							file_path += "pizza/"
			case "Farming":
				verb = "Plant" 
			case "Runecraft":
				verb = "Infuse"
			case "Prayer":
				verb = "Bless"
			case "Firemaking":
				verb = "Burn"
		

	for mat in EachParamCategory(recipeNode.params, "mat"):
		if "" not in mat:
			print("Material in {} does not have a name".format(pageName), flush=True)
			continue

		name = NormalizeName(mat[""])
		quantity = ParseInt(mat, "quantity", 1)

		if not name in nameToIdLookup:
			print("Material [{}] in {} does not have an id".format(name, pageName), flush=True);
			continue

		takes[nameToIdLookup[name]] = quantity

	for output in EachParamCategory(recipeNode.params, "output"):
		name = NormalizeName(output[""])
		quantity = ParseInt(output, "quantity", 1)

		if not name in nameToIdLookup:
			print("Output {} in {} does not have an id".format(name, pageName));
			continue

		makes[nameToIdLookup[name]] = quantity

	simple = util.DictFromAssignments(recipeNode.params)

	if "tools" in simple:
		for tool in simple["tools"].split(","):
			name = NormalizeName(tool.strip())

			if name == "":
				continue

			if name == "needle":
				verb = "Sew"
				file_path += "Sewing/"

			if name == "gardening_trowel":
				verb = "Plant"
				file_path += "Planting/"

			if name == "pestle_and_mortar" or name == "pestle_and_mortar_(the_gauntlet)":
				verb = "Crush"
				file_path += "Crushing/"
				if "mix" in pageName or "Mix" in pageName:
					file_path += "Butterflies/"

			if name == "knife":
				verb = "Cut"
				file_path += "Cutting/"

			if name == "chisel":
				verb = "Chisel"
				file_path += "Chisel/"
				if "snelm" in pageName or "Snelm" in pageName:
					file_path += "snelms"

			if name == "sieve":
				verb = "Sieve"
				file_path += "Sieve/"

			if name == "pirate_hat":
				verb = "Minigame"
				file_path += "Trouble_Brewing/"

			if name == "Hammer" and verb != "Smith" and verb != "Build":
				verb = "Break"
				file_path += "Break/"
			if name == "glassblowing_pipe":
				verb = "Blow"
				file_path += "Blowing/"

			if name == "ogre_bellows":
				verb = "Inflate"
				file_path += "Inflating/"

			if name == "binding_book":
				verb = "Enchant"
				file_path += "Enchanting/"

			if name == "enchanted_scroll":
				verb = "Enchant"
				file_path += "Enchanting/"

			if name == "machete":
				verb = "cut"
				file_path += "Cutting/"

			if name in [ "spice", "gnome_spice" ]:
				verb = "Season"
				file_path += "Cooking/"
			
			if not name in nameToIdLookup:
				print("Tool [{}] in {} does not have an id".format(name, pageName), flush=True);
				continue
			requires[nameToIdLookup[name]] = 1

	if "facilities" in simple:
		faciliyName = ""
		for facility in simple["facilities"].split(","):
			name = facility.strip()

			if name == "":
				continue

			suffix = " at " + name

			if name == "Anvil":
				verb = "Smith"
				file_path += "Anvil/" + util.SafeName(pageName.split(' ', 1)[0]) + "/"
				continue

			if name in FacilityMappings:
				verb = FacilityMappings[name]
			else:
				if name not in missingFacilities:
					missingFacilities[name] = []

				missingFacilities[name].append(pageName)
				print("Unkown facility {} in {}".format(name, pageName), flush=True)
			
			faciliyName = util.SafeName(name)

		if faciliyName != "":
			if file_path == "":
				file_path = "Facility/"

			file_path += faciliyName + "/"

	if "item.187" in takes or "item.5937" in takes or "item.5940" in takes or "item.3152" in takes:
		verb = "Poison"
		file_path += "Poision/" + util.SafeName(pageName.split(' ', 1)[0]) + "/"

	if "item.5418" in takes or "item.5376" in takes: # Empty sack, Basket
		verb = "Fill"
		file_path += "Fill/"

	if "item.11740" in takes: # Scroll of redirection
		verb = "Redirect"
		file_path = "Redirect/"

	if "item.3436" in takes: # Sacred oil(1)
		verb = "Impregnate"

	if not requires and takes and makes and file_path == "":
		verb = "Make"
		file_path += "Make/"
		simpleName = util.SafeName(pageName);
		if "graceful" in simpleName:
			file_path += "graceful/"
		elif "max" in simpleName:
			file_path += "max_capes/"
		elif "amlodd" in simpleName:
			file_path += "crystal/amlodd/"
		elif "cadarn" in simpleName:
			file_path += "crystal/cadarn/"
		elif "crwys" in simpleName:
			file_path += "crystal/crwys/"
		elif "hefin" in simpleName: 
			file_path += "crystal/hefin/"
		elif "iorwerth" in simpleName:
			file_path += "crystal/iorwerth/"
		elif "ithell" in simpleName:
			file_path += "crystal/ithell/"
		elif "trahaearn" in simpleName:
			file_path += "crystal/trahaearn/"
		elif "meilyr" in simpleName:
			file_path += "crystal/meilyr/"
		elif "crystal" in simpleName:
			file_path += "crystal/"
		elif "dragon" in simpleName:
			file_path += "dragon/"
		elif "amulet" in simpleName:
			file_path += "amulet/"
		elif "slayer" in simpleName:
			file_path += "slayer/"

	method = {}

	method["takes"] = takes
	method["makes"] = makes
	method["requires"] = requires
	method["name"] = verb + " " + pageName + suffix

	final_path = "Baked/{}{}_{}.json".format(file_path, util.SafeName(pageName), index)

	if verb == "???":
		print("{}/{}: Unkown verb".format(file_path, pageName), flush=True)
		final_path = "Baked/Failed/{}{}_{}.json".format(file_path, util.SafeName(pageName), index)

	if not makes:
		print("{}/{}: Doesnt make anything".format(file_path, pageName), flush=True)
		final_path = "Baked/Failed/{}{}_{}.json".format(file_path, util.SafeName(pageName), index)

	os.makedirs(os.path.dirname(final_path), exist_ok=True)
	with open(final_path, "w+") as fi:
		json.dump(method, fi, indent=2)


def FindRecipes(item, code, nameToIdLookup, methodSink, missingFacilities):

	index = 0;

	for recipe in code.filter_templates(matches=lambda t: t.name.matches("Recipe"), recursive=True):
		index += 1
		ParseRecipe(item, index, recipe, nameToIdLookup, methodSink, missingFacilities);

	#util.write_json("stats.json", "stats.ids.min.json", stats)

def FindIds(pages) -> Dict[str, str]:
	out = {}
	cache_file_name = "item_ids.cache.json"
	if use_cache and os.path.isfile(cache_file_name):
		with open(cache_file_name, "r") as fi:
			print("Using cached item name to id table", flush=True)
			return json.load(fi)
	
	print("Generating item name to id table", flush=True)

	out["pickaxe"] = "any.mining_tool"
	out["axe"] = "any.chopping_tool"

	out["zeal_tokens"] = "minigame.zeal"
	out["nightmare_zone_points"] = "minigame.nmz_points"
	out["void_knight_commendation_points"] = "minigame.void_points"
	
	out["magic_imbue"] = "quest.lunar_diplomacy"

	out["lamp_oil"] = "item.1939" # swamp tar

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
					print("{}: no id".format(name), flush=True)
					continue

				if version["id"].strip() == "":
					print("{}: empty id".format(name), flush=True)
					continue

				if version["id"].strip().startswith("beta"):
					continue

				if not "name" in version:
					print("{}: no name".format(name), flush=True)
					continue

				id = ParseInt(version, "id", -1)
				item_name = NormalizeName(version["name"].strip())
				if id == -1:
					print("{}: failed to parse id [{}]".format(name, version["id"].strip()), flush=True)
					continue

				finalId = "item." + str(id)

				inserted = False;

				if "version" in version:
					versionName = NormalizeName(item_name + "#" + version["version"].strip())
					if not versionName in out:
						out[versionName] = finalId
						inserted = True

				if not item_name in out:
					out[item_name] = finalId
					inserted = True

				normalizedName = NormalizeName(name)
				if not normalizedName in out:
					out[normalizedName] = finalId
					inserted = True

				if not inserted:
					print("Duplicate item [{}] {} and {}".format(item_name, out[item_name], "item." + str(id)), flush=True)
				
				if "redirects" in page:
					for redirect in page["redirects"]:
						normalizedRedirect = NormalizeName(redirect)
						if not normalizedRedirect in out:
							out[normalizedRedirect] = finalId

				#print("{}: item.{}".format(name, str(id)))

		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			print("Item {} failed:".format(name), flush=True)
			traceback.print_exc()

	with open(cache_file_name, "w+") as fi:
		json.dump(out, fi)

	return out

def RemoveUnsupportedFormatting(page):
	return page.replace("<tabber>","").replace("</tabber>", "")

def BuildMethods(nameToIdLookup, pages, methodSink):

	print("Building methods", flush=True)

	missingFacilities = {}

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

			FindRecipes(name.strip(), code, nameToIdLookup, methodSink, missingFacilities);

		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			print("Item {} failed:".format(name), flush=True)
			traceback.print_exc()


	if missingFacilities:
		print("======== Missing ========", flush=True)
		for name, makes in missingFacilities.items():
			print("\"{}\": \"\", #{}".format(name, makes), flush=True)

def run():
	index = []

	item_pages = api.query_category("Items")

	nameToIdLookup = FindIds(item_pages)
	BuildMethods(nameToIdLookup, item_pages, index)

	return nameToIdLookup

