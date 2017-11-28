import os
import json
import facebook

if __name__ == '__main__':
	# Create an environment variable - FACEBOOK_GRAPH_TOKEN before executing this script.
	token = os.environ.get('FACEBOOK_GRAPH_TOKEN') 
	print token

	with open("output/fb_data_dump_swathi.json","w") as f:
		graph = facebook.GraphAPI(token)
		profile = graph.get_object("me", fields='name,location,music')
		json.dump(profile,f, indent=2)
		print json.dumps(profile, indent=2)
		print profile.keys()
		print profile["music"]["data"][1]["name"]

		for i in profile["music"]["data"]:
			print i["name"]
