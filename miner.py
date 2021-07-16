from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime
from time import time
import persistence
import re


CHANNEL_MINE_TIME = 900


class Miner:

	def __init__(self):
		options = webdriver.ChromeOptions()
		options.add_argument(r'--user-data-dir=/home/matheus/.config/chromium/Default')
		self.driver = webdriver.Chrome(executable_path='selenium_stuff/chromedriver', options=options)

		self.datetime_format_code = '%d %B %Y, %H:%M:%S'

	def mine_channel(self):
		sleep(4)
		channel_info = self.get_channel_info()
		print(channel_info['name'])

		# go to bottom
		try:
			self.driver.find_element_by_xpath('//*[@id="column-center"]/div/div/div[4]/div/button[1]').click()
			sleep(4)
		except Exception as e:
			pass

		# scroll
		scroll_elem = self.driver.find_element_by_xpath('//*[@id="column-center"]/div/div/div[3]/div')
		clock = time()

		info = []
		next_data_mid_checker = None
		try:
			while time() - clock < CHANNEL_MINE_TIME:
				# message bubbles
				bs = BeautifulSoup(self.driver.page_source, 'lxml')
				bubbles = bs.find_all('div', {'class': 'bubble'})

				while len(bubbles) == 0:
					bs = BeautifulSoup(self.driver.page_source, 'lxml')
					bubbles = bs.find_all('div', {'class': 'bubble'})

				iterator = iter(bubbles)
				# treat first bubbles
				bubble = next(iterator)
				while not bubble.has_attr('data-mid'):
					bubble = next(iterator)

				current_data_mid_checker = next_data_mid_checker
				next_data_mid_checker = bubble['data-mid']

				flag = True
				while flag:
					if bubble.has_attr('data-mid'):
						if bubble['data-mid'] == current_data_mid_checker:
							break
						aux = self.get_bubble_info(bubble)
						if aux:
							info.append(aux)
					try:
						bubble = next(iterator)
					except:
						flag = False

				self.driver.execute_script("arguments[0].scrollTop = 0", scroll_elem)
		except KeyboardInterrupt:
			pass

		print('Len: ', len(info))
		print('- - - - - - - - - - -')

		channel_info['messages'] = info

		return channel_info

	def get_bubble_info(self, bubble):
		content_elem = bubble.find('div', {'class': 'bubble-content'})

		header_elem = content_elem.find('div', {'class': 'name'})
		forwarded_from = None
		if header_elem and header_elem.find('span', {'class': 'i18n'}):
			try:
				forwarded_from = header_elem.find('span', {'class': 'peer-title'}).text
			except:
				return None

		message_elem = content_elem.find('div', {'class': 'message'})
		if not message_elem:
			return None
		message = message_elem.text
		#message = self.treat_message_text(message_elem.text)
		link_url = message_elem.find('a')['href'] if message_elem.find('a') else None

		time_text = message_elem.find('span', {'class': 'time tgico'})['title'].replace('\n', '')
		time = None
		original_time = None
		edited_time = None

		found_original = time_text.find('Original:')
		found_edited = time_text.find('Edited:')

		if found_original == -1 and found_edited == -1:
			time = datetime.strptime(time_text.strip(), self.datetime_format_code)
		elif found_original != -1 and found_edited == -1:
			time = datetime.strptime(time_text[:found_original].strip(), self.datetime_format_code)
			original_time = datetime.strptime(time_text[found_original + 10:].strip(), self.datetime_format_code)
		elif found_original == -1 and found_edited != -1:
			time = datetime.strptime(time_text[:found_edited].strip(), self.datetime_format_code)
			edited_time = datetime.strptime(time_text[found_edited + 7:].strip(), self.datetime_format_code)
		else:
			time = datetime.strptime(time_text[:found_edited].strip(), self.datetime_format_code)
			edited_time = datetime.strptime(time_text[found_edited + 7:found_original].strip(),
											self.datetime_format_code)
			original_time = datetime.strptime(time_text[found_original + 10:].strip(), self.datetime_format_code)

		return {
			'fowarded_from': forwarded_from,
			'message': message,
			'link_url': link_url,
			'time': time,
			'original_time': original_time,
			'edited_time': edited_time
		}

	def get_channel_info(self):
		self.driver.find_element_by_class_name('chat-info').click()
		sleep(2)

		bs = BeautifulSoup(self.driver.page_source, 'lxml')

		first_part = bs.find('div', {'class': 'profile-avatars-container'})
		name = first_part.find('span', {'class': 'peer-title'}).text
		member_count = None
		try:
			member_count = int(''.join(c for c in first_part.find('span', {'class': 'i18n'}).text if c.isdigit()))
		except:
			pass

		second_part = bs.find('div', {'class': 'sidebar-left-section no-delimiter'})
		username = second_part.find('div', {'class': 'row-title tgico tgico-username'}).text
		bio = second_part.find('div', {'class': 'row-title tgico tgico-info pre-wrap'}).text

		return {
			'name': name,
			'member_count': member_count,
			'username': username,
			'bio': bio
		}

	def treat_message_text(self, message):
		regrex_pattern = re.compile(pattern="["
			u"\U0001F600-\U0001F64F"  # emoticons
			u"\U0001F300-\U0001F5FF"  # symbols & pictographs
			u"\U0001F680-\U0001F6FF"  # transport & map symbols
			u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
			"]+", flags=re.UNICODE)

		return regrex_pattern.sub(r'', message)

	def mine_all(self):
		self.driver.get('https://web.telegram.org/')
		sleep(5)

		bs = BeautifulSoup(self.driver.page_source, 'lxml')
		chatlist_elements = bs.find('ul', {'class': 'chatlist'}).findChildren('li', recursive=False)
		for channel in chatlist_elements:
			self.driver.find_element_by_css_selector('li[data-peer-id="' + channel['data-peer-id'] + '"').click()
			aux = self.mine_channel()
			persistence.persist_one(aux)

		self.driver.close()

	def mine_selected(self):
		self.driver.get('https://web.telegram.org/')
		input('Select the channel and press ENTER')
		print('Mining...\n')

		aux = self.mine_channel()
		persistence.persist_one(aux)
		self.driver.close()
