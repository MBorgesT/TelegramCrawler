import pymongo
from bson.objectid import ObjectId


SERVER_URL = 'mongodb://172.17.0.2:27017/'


def persist_channel(channel_info):
	client = pymongo.MongoClient(SERVER_URL)
	db = client['telegram']
	channels = db['channels']
	return channels.insert_one(channel_info)


def add_messages_to_channel(channel_id, messages):
	client = pymongo.MongoClient(SERVER_URL)
	db = client['telegram']
	channels = db['channels']

	channel_to_update = channels.find_one({'_id': channel_id})

	channels.update_one({
		'_id': channel_id
	}, {
		'$set': {
			'messages': channel_to_update['messages'] + messages,
			'messages_len': channel_to_update['messages_len'] + len(messages)
		}
	})


def get_channel_by_id(channel_id):
	client = pymongo.MongoClient(SERVER_URL)
	db = client['telegram']
	channels = db['channels']
	return channels.find_one({'_id': ObjectId(channel_id)})


def get_all_channels():
	client = pymongo.MongoClient(SERVER_URL)
	db = client['telegram']
	channels = db['channels']
	return channels.find()
