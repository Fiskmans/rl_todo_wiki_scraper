import api

import items
import quests
import json

api.use_cache = True

allMethods = []

itemNameToId = items.run(allMethods)
quests.run(itemNameToId, allMethods)

with open("methods.json", "w+") as fi:
	json.dump(allMethods, fi, indent=2)