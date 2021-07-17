import persistence
import matplotlib.pyplot as plt
import numpy as np

SERVER_URL = 'mongodb://172.17.0.2:27017/'


def get_word_list_from_channel(channel_id):
	channel = persistence.get_channel_by_id(channel_id)
	word_list = dict()
	for m in channel['messages']:
		words = treat_message(m['message'])
		for w in words:
			if w in word_list:
				word_list[w] += 1
			else:
				word_list[w] = 1
	return word_list


def treat_message(message):
	message = message[:-10]

	message = ' '.join([x for x in message.split() if not x.startswith('http')])

	wanted_chars = [' ']
	message = ''.join([x for x in message if x.isalpha() or x in wanted_chars])

	message = message.lower()

	file = open('nlp_stuff/stopwords.txt', 'r')
	stopwords = [x.strip() for x in file.readlines()]
	file.close()

	message_list = message.split()
	message_list = [x for x in message_list if x not in stopwords]

	return message_list


def plot_word_list_graph(channel_ids):
	word_list = dict()
	for c_id in channel_ids:
		channel_word_list = get_word_list_from_channel(c_id)
		for i in list(channel_word_list.items()):
			if i[0] in word_list:
				word_list[i[0]] += i[1]
			else:
				word_list[i[0]] = i[1]

	word_list = sorted(list(word_list.items()), key=lambda x: x[1], reverse=True)

	word_amount = 20
	words, amounts = zip(*(word_list[:word_amount]))
	y_pos = np.arange(len(words))

	_, ax = plt.subplots()
	ax.barh(y_pos, amounts)
	ax.set_yticks(y_pos)
	ax.set_yticklabels(words)
	ax.invert_yaxis()

	plt.show()


def plot_fowarded_from_graph(channel_ids):
	ff_dict = dict()
	for c_id in channel_ids:
		channel = persistence.get_channel_by_id(c_id)
		for m in channel['messages']:
			if m['fowarded_from'] is not None:
				if m['fowarded_from'] in ff_dict:
					ff_dict[m['fowarded_from']] += 1
				else:
					ff_dict[m['fowarded_from']] = 1

	ff_list = sorted(list(ff_dict.items()), key=lambda x: x[1], reverse=True)

	ff_amount = 20
	words, amounts = zip(*(ff_list[:ff_amount]))
	y_pos = np.arange(len(words))

	_, ax = plt.subplots()
	ax.barh(y_pos, amounts)
	ax.set_yticks(y_pos)
	ax.set_yticklabels(words)
	ax.invert_yaxis()

	plt.tight_layout()
	plt.show()


if __name__ == '__main__':
	'''
	plot_fowarded_from_graph([
		'60f1cf67aad4e2808c94e284',
		'60f228d2aa09ba05fdfb2bab'
	])
	'''
	plot_word_list_graph([
		'60f1cf67aad4e2808c94e284',
		'60f228d2aa09ba05fdfb2bab'
	])
