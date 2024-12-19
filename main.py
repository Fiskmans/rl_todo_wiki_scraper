import api

import items
import quests
import json
import os

api.use_cache = True

allMethods = []

itemNameToId = items.run(allMethods)
quests.run(itemNameToId, allMethods)

with open("methods.json", "w+") as fi:
	json.dump(allMethods, fi, indent=2)
	
def ClumpWarnings(path: str):
    files = 0
    for node in os.listdir(path):
        nodePath = os.path.join(path, node)
        if os.path.isfile(nodePath):
            files += 1
        elif os.path.isdir(nodePath):
            ClumpWarnings(nodePath)
    
    if files > 30:
        print("Warning {} has {} methods in it, consider splitting it up".format(path, files))

ClumpWarnings("Baked")