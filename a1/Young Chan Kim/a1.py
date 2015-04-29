# April 24, 2015
# Young Chan Kim

import requests
import json
import time


def getJSONData(url):
	"""Return the dictionary containing the JSON data corresponding to this url.
	Precondition: url is a string of a valid url.
	"""
	# reddit requires user-agent for rate limiting
	header = {'user-agent': 'Young user agent'}
	response = requests.get(url, headers=header)
	data = response.json()
	return data


def isMod(a):
	"""Return True if this author is a moderator in any subreddit.
	Precondition: a is a string of the author's name.
	"""
	url = 'http://www.reddit.com/user/' + a + '/about.json'
	d = getJSONData(url)
	return d['data']['is_mod']


def isVerified(a):
	"""Return True if this author is linked to a verified email address.
	Precondition: a is a string of the author's name.
	"""
	url = 'http://www.reddit.com/user/' + a + '/about.json'
	d = getJSONData(url)
	return d['data']['has_verified_email']


def isGold(a):
	"""Return True if this author is gold.
	Precondition: a is a string of the author's name.
	"""
	url = 'http://www.reddit.com/user/' + a + '/about.json'
	d = getJSONData(url)
	return d['data']['is_gold']


def getCreatedUTC(a):
	"""Return the date this author's account was created (Unix timestamp in seconds)
	Precondition: a is a string of the author's name.
	"""
	url = 'http://www.reddit.com/user/' + a + '/about.json'
	d = getJSONData(url)
	return d['data']['created_utc']


def getListOfCommentsChildren(a):
	"""Return a list containing all children (dictionaries) for this author's comments data.
	This list must be sorted according each child's 'created_utc' field.
	Precondition: a is a string of the author's name.
	"""
	# store author's comments' json data
	url = 'http://www.reddit.com/user/' + a + '/comments.json?sort=new'
	d = getJSONData(url)

	thelist = []

	while (not (d['data']['after'] is None)):
		thelist.extend(d['data']['children'])

		# store author's comments' json data
		theurl = 'http://www.reddit.com/user/' + a + '/comments.json?sort=new&count=25&after=' + d['data']['after']
		d = getJSONData(theurl)

	thelist.extend(d['data']['children'])
	thelist = sorted(thelist, key= lambda k : k['data']['created_utc'])

	return thelist


def getListOfThreadsChildren(a):
	"""Return a list containing all children (dictionaries) for this author's threads data.
	This list must be sorted according each child's 'created_utc' field.
	Precondition: a is a string of the author's name.
	"""
	# store author's threads' json data
	url = 'http://www.reddit.com/user/' + a + '/submitted.json?sort=new'
	d = getJSONData(url)

	thelist = []

	while (not (d['data']['after'] is None)):
		thelist.extend(d['data']['children'])

		# store author's threads' json data
		theurl = 'http://www.reddit.com/user/' + a + '/submitted.json?sort=new&count=25&after=' + d['data']['after']
		d = getJSONData(theurl)

	thelist.extend(d['data']['children'])
	thelist = sorted(thelist, key= lambda k : k['data']['created_utc'])

	return thelist


def haveAllComments(a):
	"""Return True if there are less than 950 comments collected for this author.
	Precondition: a is a string of the author's name.
	"""
	commentsList = getListOfCommentsChildren(a)
	return getNumComments(commentsList) < 950


def haveAllThreads(a):
	"""Return True if there are less than 950 threads collected for this author.
	Precondition: a is a string of the author's name.
	"""
	threadsList = getListOfThreadsChildren(a)
	return getNumThreads(threadsList) < 950


def getNumComments(children):
	"""Return the number of comments the author corresponding to this children has. This is a
	helper function for haveAllComments().
	Precondition: children is a list of dictionaries containing information about an author's 
	comments (all of them).	
	"""
	numComments = 0

	for child in children:
		if (child['kind'] == 't1'):
			numComments += 1

	return numComments


def getNumThreads(children):
	"""Return the number of threads the author corresponding to this children has. This is a
	helper function for haveAllThreads().
	Precondition: children is a list of dictionaries containing information about an author's 
	threads (all of them).	
	"""
	numThreads = 0

	for child in children:
		if (child['kind'] == 't3'):
			numThreads += 1

	return numThreads


def getFirstObservedPost(a):
	"""Return the Unix time of the first observed post of this author, -1 if there are
	no posts for this author.
	Precondition: a is a string of the author's name.
	"""
	commentsList = getListOfCommentsChildren(a)
	threadsList = getListOfThreadsChildren(a)
	if (commentsList == [] and threadsList == []):
		return -1
	elif (commentsList == []):
		return threadsList[-1]['data']['created_utc']
	elif (threadsList == []):
		return commentsList[-1]['data']['created_utc']
	else:
		return max(commentsList[-1]['data']['created_utc'], threadsList[-1]['data']['created_utc'])


def getLastObservedPost(a):
	"""Return the Unix time of the last observed post of this author. -1 if there are
	no posts for this author.
	Precondition: a is a string of the author's name.
	"""
	commentsList = getListOfCommentsChildren(a)
	threadsList = getListOfThreadsChildren(a)
	if (commentsList == [] and threadsList == []):
		return -1
	elif (commentsList == []):
		return threadsList[0]['data']['created_utc']
	elif (threadsList == []):
		return commentsList[0]['data']['created_utc']
	else:
		return min(commentsList[0]['data']['created_utc'], threadsList[0]['data']['created_utc'])









#Tester

#input the name of the file containing all authors
filename = raw_input('Type the name of the file containing all authors: ')

# Process text file
file = open(filename)
authorlist = []    
for line in file:
    if ('\n' in line):
        authorlist.append(line[:-1])
    else:
        authorlist.append(line)
file.close()

# Collect only the authors who were snoped
snopedlist = []
for a in authorlist:
	author = a.split()
	if (int(author[1]) > 0):
		snopedlist.append(author[0])

# print the fields for each snoped author
for snoped in snopedlist:
	is_mod = isMod(snoped)
	is_verified = isVerified(snoped)
	is_gold = isGold(snoped)
	created_utc = getCreatedUTC(snoped)
	
	have_all_comments = haveAllComments(snoped)
	have_all_threads = haveAllThreads(snoped)

	first_observed_post = getFirstObservedPost(snoped)
	last_observed_post = getLastObservedPost(snoped)

	print snoped + '- is_mod: ' + str(is_mod) +'\n'
	print snoped + '- is_verified: ' + str(is_verified) + '\n'
	print snoped + '- is_gold: ' + str(is_gold) + '\n'
	print snoped + '- created_utc: ' + str(created_utc) + '\n'
	print snoped + '- have_all_comments: ' + str(have_all_comments) + '\n'
	print snoped + '- have_all_threads: ' + str(have_all_threads) + '\n'
	print snoped + '- first_observed_post: ' + str(first_observed_post) + '\n'
	print snoped + '- last_observed_post: ' + str(last_observed_post) + '\n\n'


