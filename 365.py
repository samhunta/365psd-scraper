from BeautifulSoup import BeautifulSoup 
from zipfile import ZipFile
import urllib
import os
import shutil
import re

pref_url = "http://365psd.com/day/"
directory = os.path.dirname(os.path.abspath(__file__)) + "/"
psd_directory = directory + "psd/"
progress_file = directory + ".resume"

max_day = 364
cur_day = max_day
max_year = 1
cur_year = max_year

def create_dir(dir):
	if not os.path.exists(dir):
		os.mkdir(dir)

create_dir(directory)
create_dir(psd_directory)
os.chdir(directory)
	
def get_progress():
	global cur_day, max_year, cur_year
	try:
		with open(progress_file) as f:
			progress_data = f.read().split("-")
			cur_day = int(progress_data[0])
			max_year = int(progress_data[1])
			cur_year = max_year
			return True
	except:
		pass

	page = BeautifulSoup(get_webpage("http://365psd.com/"))
	link_with_year = page.find("a", href=re.compile("^http\:\/\/365psd\.com\/day\/([0-9])\-"))
	cur_day = int(page.find("div", id="breadcrumbs").findAll("strong")[1].contents[0])
	max_year = int(link_with_year['href'][len(pref_url):].split('-')[0])
	cur_year =  max_year

def save_progress():
	try:
		f = open(progress_file, 'w')
		f.write(str(cur_day) + "-" + str(cur_year))
		f.close()
		return True
	except IOError as e:
		return False

def change_ext(filename, ext):
	return (filename[0:-3] + ext)

def download_psd(url, filename):
	urllib.urlretrieve(url, os.path.join(psd_directory, filename))

def extract_psd(filename):
	zipf = ZipFile(os.path.join(psd_directory, filename), 'r')
	psd_file = {}

	for member in zipf.namelist():
		is_psd = member.endswith('.psd')
		file_size = zipf.getinfo(member).file_size
		if is_psd and (("size" not in psd_file) or (psd_file["size"] < file_size)):
			psd_file["size"] = file_size
			psd_file["name"] = member

	if not psd_file:
		return False

	m_source = zipf.open(psd_file['name'])
	m_target = file(os.path.join(psd_directory, change_ext(filename, 'psd')), 'wb')
	shutil.copyfileobj(m_source, m_target)
	m_source.close()
	m_target.close()
	zipf.close()
	os.unlink(os.path.join(psd_directory, filename))


def get_webpage(url):
	result = urllib.urlopen(url)
	html = result.read()
	result.close()
	return html

try:
	get_progress()
except:
	print "Failed retrieving current day"

while(cur_year > 0):
	link = pref_url
	if (cur_year != 1):
		link += str(cur_year) + "-"
	link += str(cur_day)

	# try:
	download_page = BeautifulSoup(get_webpage(link))
	download_link = download_page.find("div", id="item").find("a", attrs={ "class": "download" })['href']
	download_title = download_page.find("h1").text
	download_filename = re.sub("\/|\s+", "_", re.sub("\&[^\;]+\;", "", download_title)) + ".zip"

	print "Downloading %s" % download_title
	download_psd(download_link, download_filename)

	print "Extracting %s" % download_filename
	extract_psd(download_filename)

	print " "
	# except:
	# 	print "Error while downloading PSD from", link

	cur_day = cur_day - 1
	if (cur_day == 0):
		cur_day = max_day
		cur_year = cur_year - 1
	save_progress()