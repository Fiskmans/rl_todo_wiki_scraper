import api

import items
import npcs
import quests

api.use_cache = True

itemNameToId = items.run()
quests.run(itemNameToId)

