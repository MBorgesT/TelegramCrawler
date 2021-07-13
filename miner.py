from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime
from time import time
import persistence


CHANNEL_MINE_TIME = 3


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
		while time() - clock < CHANNEL_MINE_TIME:
			# message bubbles
			bs = BeautifulSoup(self.driver.page_source, 'lxml')
			bubbles = bs.find_all('div', {'class': 'bubble'})

			iterator = iter(bubbles)
			next(iterator)

			# treat first bubble
			bubble = next(iterator)
			current_data_mid_checker = next_data_mid_checker
			next_data_mid_checker = bubble['data-mid']
			aux = self.get_bubble_info(bubble)
			if aux:
				info.append(aux)

			flag = False
			for bubble in iterator:
				try:
					if bubble['data-mid'] == current_data_mid_checker:
						break
				except:
					pass
				try:
					aux = self.get_bubble_info(bubble)
					if aux:
						flag = True
						info.append(aux)
				except Exception as e:
					print('data-mid:', bubble['data-mid'])
					raise e

			# no more messages
			if not flag:
				break

			self.driver.execute_script("arguments[0].scrollTop = 0", scroll_elem)

		print('Len: ', len(info))
		print('- - - - - - - - - - -')

		info_dict = dict(zip(range(len(info)), info))
		channel_info['messages'] = info_dict

		return channel_info

	def get_bubble_info(self, bubble):
		content_elem = bubble.find('div', {'class': 'bubble-content'})

		header_elem = content_elem.find('div', {'class': 'name'})
		if not header_elem:
			return
		forwarded_from = None
		if header_elem.find('span', {'class': 'i18n'}):
			try:
				forwarded_from = header_elem.find('span', {'class': 'peer-title'}).text
			except:
				return None

		message_elem = content_elem.find('div', {'class': 'message'})
		message = message_elem.text[:-10]
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
		bio = second_part.find('div', {'class': 'row-title tgico tgico-info pre-wrap'})

		return {
			'name': name,
			'member_count': member_count,
			'username': username,
			'bio': bio
		}

	def mine(self):
		self.driver.get('https://web.telegram.org/')
		sleep(5)

		bs = BeautifulSoup(self.driver.page_source, 'lxml')
		chatlist_elements = bs.find('ul', {'class': 'chatlist'}).findChildren('li', recursive=False)
		channel_infos = []
		i = 0
		for channel in chatlist_elements:
			self.driver.find_element_by_css_selector('li[data-peer-id="' + channel['data-peer-id'] + '"').click()
			aux = self.mine_channel()
			channel_infos.append(aux)
			i += 1
			if i == 3:
				break

		persistence.persist(dict(zip(range(len(channel_infos)), channel_infos)))
