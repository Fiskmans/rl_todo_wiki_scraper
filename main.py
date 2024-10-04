import api

import items
import quests
import os

api.use_cache = True

itemNameToId = items.run()
quests.run(itemNameToId)

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