

import json
from Suite import Suite

suite = Suite("suites/bubblewrap")

import json

f = open("EasyLightshow.dat", "r+")
bsMap = None
try:
    bsMap = json.loads(f.read())
except json.decoder.JSONDecodeError:
    bsMap = {"_time": 11, "_notes": [], "_BPMChanges": [], "_events": [], "_obstacles": []}

bsMap["_obstacles"] = suite.json()

f.seek(0, 0)
f.truncate()
f.write(json.dumps(bsMap))
f.close()
