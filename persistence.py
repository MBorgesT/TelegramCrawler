import pymongo


def persist(channel_infos):
	client = pymongo.MongoClient('mongodb://172.17.0.2:27017/')
	db = client['telegram']

	channels = db['channels']
	channels.insert_many(channel_infos)
