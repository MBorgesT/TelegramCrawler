import pymongo
import persistence


SERVER_URL = 'mongodb://172.17.0.2:27017/'


def most_used_words():
	word_list = dict()
	for c in persistence.get_all_channels():
		print(c['name'])
		print(len(c['messages']))
		print('-------------')


if __name__ == '__main__':
	most_used_words()
