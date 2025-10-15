def get_loc():
	import json
	with open("settings/loc.json", "r", encoding="utf-8") as f:
		data = json.load(f)
	return data

def get_settings():
	import json
	with open("settings/general.json", "r", encoding="utf-8") as f:
		data = json.load(f)
	return data

loc = get_loc()
settings = get_settings()