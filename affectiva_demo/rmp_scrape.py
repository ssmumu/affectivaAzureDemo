import urllib2
from bs4 import BeautifulSoup
import re
import pandas as pd

RMP_URL_BASE = 'http://www.ratemyprofessors.com'
CSE_FAC_URL = 'http://www.eecs.umich.edu/eecs/faculty/csefaculty.html'


def rmp_scrape():
	"""
	Scrape RMP for names, ratings, and difficulty ratings of UM CSE faculty
	Returns: pandas DataFrame
	"""
	diff_ratings = []
	with open('rmp_list.html') as page:
		soup = BeautifulSoup(page, 'lxml')
		children = []
		for item in soup.find_all('a'):
			# Check for nonzero number of ratings before appending faculty
			if int(re.search('\d+', item.find(class_='info').contents[0]).group()):
				children.append(item)

				# Open faculty member's page to get difficulty rating
				page_data = urllib2.urlopen(RMP_URL_BASE + item['href'])
				inner_soup = BeautifulSoup(page_data, 'lxml')
				diff_ratings.append(float((inner_soup.find(class_='difficulty').find(class_='grade').contents[0])))

	rmp_dict = {
		'name': [child.find(class_='name').contents[0].strip() for child in children],
		'rating': [float(child.find(class_='rating').contents[0].strip()) for child in children],
		'diff_rating': diff_ratings
	}
	return pd.DataFrame(rmp_dict)


def cse_scrape():
	"""
	Scrape UM CSE website for names and image URLs of faculty
	Returns: pandas DataFrame
	"""
	cse_fac_names = []
	cse_fac_imgs = []

	page_data = urllib2.urlopen(CSE_FAC_URL).read()
	soup = BeautifulSoup(page_data, 'lxml')
	for item in soup.find_all('tr'):
		if (item.find('img')):
			# Get rid of middle name if exists (keep '<last_name>, <first_name>' only)
			cse_fac_names.append(re.findall('[A-z]+\, [A-z]+', item.find('span').contents[0])[0])

			# Grab the source URL of image on server
			cse_fac_imgs.append(re.search('[A-z]+\.jpg', item.find('img')['src']).group(0))

	cse_fac_dict = {
		'name': cse_fac_names,
		'img_url': cse_fac_imgs
	}
	return pd.DataFrame(cse_fac_dict)


def main():
	rmp_df = rmp_scrape()
	cse_fac_df = cse_scrape()
	merged_df = cse_fac_df.merge(rmp_df, left_on='name', right_on='name', how='inner')
	merged_df[['name', 'rating', 'diff_rating', 'img_url']].to_json('merged_df.json')


if __name__ == '__main__':
	main()
