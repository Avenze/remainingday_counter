import requests
import jsonpickle
from collections import OrderedDict
import re
from datetime import datetime, timedelta

from utils.helpers import (
	get_table_classes,
	get_table_teachers,
	firstDateOfWeek,
	timeToDate
)
from utils.logger import logger

def fetch_classes(school, schoolGuid):
	logger.debug("Fetching classes for school " + school)
	classes = []
	r = requests.get("http://www.skola24.se/Schemavisare/Widgets/schema/Start/Groups?schoolGuid=" + schoolGuid + "&hostName=malmo.skola24.se")
	tmp = jsonpickle.decode(r.text)
	for line in tmp:
		classes.append({'name' : line['Id'], 'id': line['Guid']})
	logger.debug("Found " + str(len(classes)) + " classes for school: " + school)
	table = get_table_classes(school)
	table.delete()
	table.insert_many(classes)


def fetch_teachers(school, schoolGuid):
	logger.debug("Fetching teachers for school " + school)
	teachers = []
	r = requests.get("https://web.skola24.se/timetable/timetable-viewer/wilhelmhaglundsgy.skola24.se/Wilhelm%20Haglunds%20Gymnasium/")
	tmp = jsonpickle.decode(r.text)['data']
	for line in tmp['teachers']:
		teachers.append({'id' : line['guid'], 'firstName': line['firstName'], 'lastName': line['lastName'], 'sign' : line['signature']})
	logger.debug("Found " + str(len(teachers)) + " teachers for school: " + school)
	table = get_table_teachers(school)
	table.delete()
	table.insert_many(teachers)

def fetch_timetables(school, schoolGuid):
	logger.debug("Fetching timetables for school " + school)
	classes = get_table_classes(school)
	week = 41
	# First go through all classes
	for clz in classes:
		# First fetch the "render" data from nova
		logger.debug("Fetch timetable for class : " + clz['name'] + " for week: " + str(week))
		reqbody = {
			"request": {
				"selectedSchool": {
					"Guid": schoolGuid
				},
				"selectedGroup": {
					"Guid": clz['id']
				},
				"selectedWeek": week,
				"domain": "malmo.skola24.se",
				"divWidth": 1138,
				"divHeight": 1000
			}
		}
		headers = {'Content-type': 'application/json'}
		r = requests.post("http://www.skola24.se/Schemavisare/Widgets/schema/Timetable/Render", data=str(reqbody),
						  headers=headers)
		data = None
		if r.status_code == 200:
			print("Successfully fetched data")
			data = r.json()
		else:
			print("Failed to fetch data")
			continue
		print(data)
		parseTimeTableRender(data, week)

def parseTimeTableRender(data, week):
	"""
	Splits the data returned from the api into a list with 5 items, one for each day. Each item is a list with some data gathered around one "box" on the timetable.
	:param data: json encoded data from nova schema
	:return:
	"""

	schema = OrderedDict()
	schema['monday'] = {'times':[],'other':[], 'divboxes':[]}
	schema['tuesday'] = {'times':[],'other':[], 'divboxes':[]}
	schema['wednesday'] = {'times':[],'other':[], 'divboxes':[]}
	schema['thursday'] = {'times':[],'other':[], 'divboxes':[]}
	schema['friday'] = {'times':[],'other':[], 'divboxes':[]}

	jsonboxlist = data['boxList']
	# First go through all the boxes and just put them into the correct day based on their x position
	for box in jsonboxlist:
		if box['type'] is not "4" or box['y'] == 0 or box['height'] == 1 or box['width'] == 14 or box['width'] == 7 or box['width'] == 1137 or box['height'] == 807:
			continue
		box['y'] = box['y'] - 42
		box['x'] = box['x'] - 69
		x = box['x']
		if x >= 0 and x < 195:
			schema['monday']['divboxes'].append(box)
		elif x >= 195 and x < 395:
			schema['tuesday']['divboxes'].append(box)
		elif x >= 395 and x < 595:
			schema['wednesday']['divboxes'].append(box)
		elif x >= 595 and x < 795:
			schema['thursday']['divboxes'].append(box)
		elif x >= 795 and x < 1000:
			schema['friday']['divboxes'].append(box)

	texts = data['textList']
	regex = "[0-9]{1,}:[0-9]{2}"

	for box in texts:
		x = box['x']
		y = box['y']
		if x < 69 or y < 36 or box['text'] is "":
			continue
		x = x - 69
		y = y - 37
		box['x'] = x
		box['y'] = y
		if re.match(regex, box['text']) is not None:
			box['isTime'] = True
		else:
			box['isTime'] = False

		if x >= 0 and x < 195:
			if box['isTime']:
				schema['monday']['times'].append(box)
			schema['monday']['other'].append(box)
		elif x >= 195 and x < 395:
			if box['isTime']:
				schema['tuesday']['times'].append(box)
			schema['tuesday']['other'].append(box)
		elif x >= 395 and x < 595:
			if box['isTime']:
				schema['wednesday']['times'].append(box)
			schema['wednesday']['other'].append(box)
		elif x >= 595 and x < 795:
			if box['isTime']:
				schema['thursday']['times'].append(box)
			schema['thursday']['other'].append(box)
		elif x >= 795 and x < 1000:
			if box['isTime']:
				schema['friday']['times'].append(box)
			schema['friday']['other'].append(box)

	allClasses = []
	monday_date = firstDateOfWeek(str(datetime.now().year), week)
	# Go through all the items, once for each day
	for day,boxes in schema.items():
		dayDate = monday_date + timedelta(days=list(schema.keys()).index(day))

		timeslots = []
		classes = []

		for box in boxes['divboxes']:
			clazz = {}
			starty = box['y']
			endy= starty + box['height']
			startx = box['x']
			endx = startx + box['width']

			#Find the times that are related to this class
			# (The start time is 1 px above the box start y, and
			# end time is 1 px above the end y, although - since greater
			# y means further down)
			for time in boxes['times']:
				if time['y'] == starty - 1:
					clazz['start'] = timeToDate(time['text'], dayDate)
				if time['y'] == endy - 1:
					clazz['end'] = timeToDate(time['text'], dayDate)
				if 'start' in clazz and 'end' in clazz:
					break

			# Go through all the text boxes and determine if
			# they are inside this box
			for box in boxes['other']:
				if box['isTime']:
					continue
				if box['y'] > starty and box['y'] < endy:
					if box['x'] > startx and box['x'] < endx:
						if 'text' not in clazz:
							clazz['text'] = box['text'].strip()
						else:
							clazz['text'] += " " + box['text'].strip()
			classes.append(clazz)
		allClasses.append(classes)
	return allClasses