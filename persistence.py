import pymongo


SERVER_URL = 'mongodb://172.17.0.2:27017/'


def persist_one(channel_info):
	client = pymongo.MongoClient(SERVER_URL)
	db = client['telegram']
	channels = db['channels']
	channels.insert_one(channel_info)

def get_all_channels():
	client = pymongo.MongoClient(SERVER_URL)
	db = client['telegram']
	channels = db['channels']
	return channels.find()
