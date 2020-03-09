from collections import namedtuple
import numpy
import math
import re

#########################################################################################
# Place

fields = ['id',
'key',
'name',
'county',
'area_land',
'area_water',
'area_land_sqmi',
'area_water_sqmi',
'coor_lat',
'coor_long',
'pop',
'race_nhol_total',
'race_nhol_white',
'race_nhol_black',
'race_nhol_aian',
'race_nhol_asian',
'race_nhol_nhpi',
'race_nhol_other',
'race_nhol_torm',
'race_hol_total',
'race_hol_white',
'race_hol_black',
'race_hol_aian',
'race_hol_asian',
'race_hol_nhpi',
'race_hol_other',
'race_hol_torm',
'inc_pci',
'inc_mhi',
'inc_mfi',
'hs_mv',
'hs_mgr',
'hs_mysb',
'us_ahs',
'us_afs',
'edu_pop_otf',
'edu_hs_om',
'edu_ba_om',
'edu_gd_om',
'edu_pd',
'ucr_pop',
'ucr_vc_total',
'ucr_vc_mu',
'ucr_vc_ra_rd',
'ucr_vc_ra_ld',
'ucr_vc_ro',
'ucr_vc_aa',
'ucr_pc_total',
'ucr_pc_bu',
'ucr_pc_lt',
'ucr_pc_mvt',
'ucr_pc_ar',
'vr_total',
'vr_dem',
'vr_rep',
'vr_ai',
'vr_gr',
'vr_li',
'vr_pf',
'vr_other',
'vr_npp']

class Place(namedtuple('Place', fields)):
	pass

#########################################################################################
# Places

class Places(list):
	def column(self, column_name_str):
		return [eval('i.' + column_name_str) for i in self]
		
	def column_notstr(self, column_name_str):
		return [eval('i.' + column_name_str) for i in self\
		if not isinstance(eval('i.' + column_name_str), str)]
	
	def attr(self, attribute_str, value):
		return [i for i in self if eval(attribute_str) == value]
		
	def search(self, keyword_str):
		return [i for i in self if re.search(keyword_str, str(i), re.IGNORECASE)]
		
	def __repr__(self):
		return 'Places(' + ', '.join([str(i) for i in self]) + ')'
		
	def __str__(self):
		return self.__repr__()

from Place.places import places

#########################################################################################
# PlaceVector, PlaceVectorFull, and PlaceVectorApp

#
# Determination of scores
#
# Scores are determined as follows:
#
# Values greater than or equal to two standard deviations above the median (or mean) get scores of 100.
# Lower values are graded based on based on the proportion the value that's two standard deviations
# above the mean with a maximum of 100.
#

# Thresholds for scores of 100.

subcomponents = ['id',
'key',
'name',
'county',
'pop',
'pop_density',
'race_white',     # *25% # race component
'race_hispanic',  # *25% #
'race_asian',     # *25% #
'race_black',     # *25% #
'inc_pci',
'hs_mysb',
'edu_ba_om',      # *50% # edu component
'edu_gd_om',      # *50% #
'ucr_vcr',        # *75% # ucr component
'ucr_pcr',        # *25% #
'vr_dem',         # *33% # vr component
'vr_rep',         # *33% # 
'vr_other']       # *33% #

numerical_subcomponents = subcomponents[4:]

pvf_subcomponents = ['id',
'key',
'name',
'county',
'pop',
'pop_density',
'race_white',
'race_hispanic',
'race_asian',
'race_black',
'inc_pci',
'edu_ba_om',
'edu_gd_om',
'ucr_vcr',
'ucr_pcr',
'vr_dem',
'vr_rep',
'vr_other']

pv_subcomponents = ['id',
'key',
'name',
'county',
'pop',
'pop_density',
'race_white',
'race_hispanic',
'race_asian',
'race_black',
'inc_pci',
'edu_ba_om',
'edu_gd_om']

pva_subcomponents = ['id',
'key',
'name',
'county',
'pop_density',
'inc_pci',
'hs_mysb']

needed_fields = ['pop',
'area_land_sqmi',
'race_nhol_white',
'race_hol_white',
'race_hol_total',
'race_nhol_asian',
'race_hol_asian',
'race_nhol_black',
'race_hol_black',
'inc_pci',
'hs_mysb',
'edu_ba_om',
'edu_gd_om',
'edu_pop_otf',
'ucr_pop',
'ucr_vc_total',
'ucr_pc_total',
'vr_total',
'vr_dem',
'vr_rep',
'vr_other']

#
# Field calculation process.
#

data = [dict(), dict()]

# First, extract data from needed fields.

for needed_field in needed_fields:
	data[0][needed_field] = numpy.array(places.column_notstr(needed_field))
	
# /S/afer /d/ivision to handle division by zero (replace with zeroes).
	
def sd(a, b):
	with numpy.errstate(divide='ignore', invalid='ignore'):
		c = numpy.true_divide(a, b)
		c[c == numpy.inf] = 0
		c = numpy.nan_to_num(c)
		
	return c
	
# Perform operations to obtain composite data.

data[1]['pop'] = data[0]['pop']
data[1]['pop_density'] = sd(data[0]['pop'], data[0]['area_land_sqmi'])
data[1]['race_white'] = sd(data[0]['race_nhol_white']+data[0]['race_hol_white'], data[0]['pop'])*100
data[1]['race_hispanic'] = sd(data[0]['race_hol_total'], data[0]['pop'])*100
data[1]['race_asian'] = sd(data[0]['race_nhol_asian']+data[0]['race_hol_asian'], data[0]['pop'])*100
data[1]['race_black'] = sd(data[0]['race_nhol_black']+data[0]['race_hol_black'], data[0]['pop'])*100
data[1]['inc_pci'] = data[0]['inc_pci']
data[1]['hs_mysb'] = data[0]['hs_mysb']
data[1]['edu_ba_om'] = sd(data[0]['edu_ba_om'], data[0]['edu_pop_otf'])*100
data[1]['edu_gd_om'] = sd(data[0]['edu_gd_om'], data[0]['edu_pop_otf'])*100
data[1]['ucr_vcr'] = sd(data[0]['ucr_vc_total'], data[0]['ucr_pop'])*1000
data[1]['ucr_pcr'] = sd(data[0]['ucr_pc_total'], data[0]['ucr_pop'])*1000
data[1]['vr_dem'] = sd(data[0]['vr_dem'], data[0]['vr_total'])*100
data[1]['vr_rep'] = sd(data[0]['vr_rep'], data[0]['vr_total'])*100
data[1]['vr_other'] = 100 - data[1]['vr_dem'] - data[1]['vr_rep']

#
# Determination of thresholds for which scores shall equal 100.
#
# Currently, for both proportions and values, a score of 100 is defined as the value two standard
# deviations above the median.
#

median = dict()

for ns in numerical_subcomponents:
	median[ns] = numpy.median(data[1][ns])
	
std = dict()

for ns in numerical_subcomponents:
	std[ns] = numpy.std(data[1][ns])
	
thresholds = dict()

for ns in numerical_subcomponents:
	thresholds[ns] = median[ns] + 2 * std[ns]
	
thresholds['ucr_vcr'] = median['ucr_vcr'] + 0.3 * std['ucr_vcr']
thresholds['ucr_pcr'] = median['ucr_pcr'] + 0.1 * std['ucr_pcr']
	
def _distance(subcomponents, place, other):
	differences = dict()
	
	# Assuming first four subcomponents are id, key, name, and county
	numerical_subcomponents = subcomponents[4:]
	
	for ns in numerical_subcomponents:
		differences[ns] = place._asdict()[ns] - other._asdict()[ns]
		
	# Make adjustments
	
	# Race component: 25%
	if 'race_white' in differences:
		differences['race_white'] = differences['race_white']/4
	if 'race_hispanic' in differences:
		differences['race_hispanic'] = differences['race_hispanic']/4
	if 'race_asian' in differences:
		differences['race_asian'] = differences['race_asian']/4
	if 'race_black' in differences:
		differences['race_black'] = differences['race_black']/4
	
	# Education component: 50%
	if 'edu_ba_om' in differences:
		differences['edu_ba_om'] = differences['edu_ba_om']/2
	if 'edu_gd_om' in differences:
		differences['edu_gd_om'] = differences['edu_gd_om']/2
	
	# Crime component: 75%/25%
	if 'ucr_vcr' in differences:
		differences['ucr_vcr'] = differences['ucr_vcr']*0.75
	if 'ucr_pcr' in differences:
		differences['ucr_pcr'] = differences['ucr_pcr']/4
	
	# Voter registration component: 33%
	if 'vr_dem' in differences:
		differences['vr_dem'] = differences['vr_dem']/3
	if 'vr_rep' in differences:
		differences['vr_rep'] = differences['vr_rep']/3
	if 'vr_other' in differences:
		differences['vr_other'] = differences['vr_other']/3
		
	squares = dict()
	
	for ns in numerical_subcomponents:
		squares[ns] = differences[ns]**2
		
	_sum = sum(squares.values())
	
	return round(math.sqrt(_sum))
	
class PlaceVectorFull(namedtuple('PlaceVectorFull', pvf_subcomponents)):
	#
	# distance()
	#
	# Obtain the Euclidian distance between two PlaceVectors.
	#
	
	def distance(self, other):
		return _distance(pvf_subcomponents, self, other)

class PlaceVector(namedtuple('PlaceVector', pv_subcomponents)):
	#
	# distance()
	#
	# Obtain the Euclidian distance between two PlaceVectors.
	#
	
	def distance(self, other):
		return _distance(pv_subcomponents, self, other)

class PlaceVectorApp(namedtuple('PlaceVectorApp', pva_subcomponents)):
	#
	# distance()
	#
	# Obtain the Euclidian distance between two PlaceVectors.
	#
	
	def distance(self, other):
		return _distance(pva_subcomponents, self, other)
		
#
# getPV()
#
# Convert a Place to a PlaceVector.
#

def getPVs(type, inPlaceList):
	out = list()
	
	for inPlace in inPlaceList:
		_in = dict()
		
		for field in inPlace._fields:
			_in[field] = eval('inPlace.' + field)
			
		proceed = True
		
		if type == 'PlaceVectorFull':
			if _in['ucr_pop'] == '' or _in['vr_total'] == '':
				proceed = False
				
		if proceed:
			# pop_density
			try:
				_in['pop_density'] = _in['pop']/_in['area_land_sqmi']
			except (ZeroDivisionError, TypeError):
				_in['pop_density'] = 0
			except KeyError:
				pass
			
			# race_white subcomponent (25%)
			try:
				_in['race_white'] = (_in['race_nhol_white'] + _in['race_hol_white'])/_in['pop']*100
			except (ZeroDivisionError, TypeError):
				_in['race_white'] = 0
			except KeyError:
				pass
			
			# race_hispanic subcomponent (25%)
			try:
				_in['race_hispanic'] = _in['race_hol_total']/_in['pop']*100
			except (ZeroDivisionError, TypeError):
				_in['race_hispanic'] = 0
			except KeyError:
				pass
			
			# race_asian subcomponent (25%)
			try:
				_in['race_asian'] = (_in['race_nhol_asian'] + _in['race_hol_asian'])/_in['pop']*100
			except (ZeroDivisionError, TypeError):
				_in['race_asian'] = 0
			except KeyError:
				pass
			
			# race_black subcomponent (25%)
			try:
				_in['race_black'] = (_in['race_nhol_black'] + _in['race_hol_black'])/_in['pop']*100
			except (ZeroDivisionError, TypeError):
				_in['race_black'] = 0
			except KeyError:
				pass
				
			# edu_ba_om subcomponent (50%)
			try:
				_in['edu_ba_om'] = _in['edu_ba_om']/_in['edu_pop_otf']*100
			except (ZeroDivisionError, TypeError):
				_in['edu_ba_om'] = 0
			except KeyError:
				pass
				
			# edu_gd_om subcomponent (50%)
			try:
				_in['edu_gd_om'] = _in['edu_gd_om']/_in['edu_pop_otf']*100
			except (ZeroDivisionError, TypeError):
				_in['edu_gd_om'] = 0
			except KeyError:
				pass
				
			# ucr_vcr subcomponent (75%)
			try:
				_in['ucr_vcr'] = _in['ucr_vc_total']/_in['ucr_pop']*1000
			except (ZeroDivisionError, TypeError):
				_in['ucr_vcr'] = 0
			except KeyError:
				pass
				
			# ucr_pcr subcomponent (25%)
			try:
				_in['ucr_pcr'] = _in['ucr_pc_total']/_in['ucr_pop']*1000
			except (ZeroDivisionError, TypeError):
				_in['ucr_pcr'] = 0
			except KeyError:
				pass
				
			# vr_dem subcomponent (33%)
			try:
				_in['vr_dem'] = _in['vr_dem']/_in['vr_total']*100
			except (ZeroDivisionError, TypeError):
				_in['vr_dem'] = 0
			except KeyError:
				pass
				
			# vr_rep subcomponent (33%)
			try:
				_in['vr_rep'] = _in['vr_rep']/_in['vr_total']*100
			except (ZeroDivisionError, TypeError):
				_in['vr_rep'] = 0
			except KeyError:
				pass
				
			# vr_other subcomponent (33%)
			try:
				_in['vr_other'] = 100 - _in['vr_dem'] - _in['vr_rep']
			except (ZeroDivisionError, TypeError):
				_in['vr_other'] = 0
			except KeyError:
				pass
			
			def score(key, value):
				try:
					threshold = thresholds[key]
					
					if key == 'hs_mysb':
						value = value - 1940
						threshold = threshold - 1940
					
					if(value >= threshold):
						return 100
					elif(value < 0):
						return 0
					else:
						return int(round(value/threshold*100))
				except (TypeError, ValueError):
					return 0
					
			for key in numerical_subcomponents:
				try:
					_in[key] = score(key, _in[key])
				except KeyError:
					pass
			
			if type == 'PlaceVector':
				out.append(PlaceVector(id=_in['id'], key=_in['key'], name=_in['name'],
				county=_in['county'], pop=_in['pop'], pop_density=_in['pop_density'],
				race_white=_in['race_white'], race_hispanic=_in['race_hispanic'],
				race_asian=_in['race_asian'], race_black=_in['race_black'], inc_pci=_in['inc_pci'], edu_ba_om=_in['edu_ba_om'], edu_gd_om=_in['edu_gd_om']))
			
			elif type == 'PlaceVectorFull':
				out.append(PlaceVectorFull(id=_in['id'], key=_in['key'], name=_in['name'],
				county=_in['county'], pop=_in['pop'], pop_density=_in['pop_density'],
				race_white=_in['race_white'], race_hispanic=_in['race_hispanic'],
				race_asian=_in['race_asian'], race_black=_in['race_black'], inc_pci=_in['inc_pci'],
				edu_ba_om=_in['edu_ba_om'], edu_gd_om=_in['edu_gd_om'], ucr_vcr=_in['ucr_vcr'],
				ucr_pcr=_in['ucr_pcr'], vr_dem=_in['vr_dem'], vr_rep=_in['vr_rep'],
				vr_other=_in['vr_other']))
			
			elif type == 'PlaceVectorApp':
				out.append(PlaceVectorApp(id=_in['id'], key=_in['key'], name=_in['name'],
				county=_in['county'], pop_density=_in['pop_density'], inc_pci=_in['inc_pci'],
				hs_mysb=_in['hs_mysb']))
		
	return out

#########################################################################################
# PlaceVectors

class PlaceVectors(Places):
	def closest(self, id, limit=10):
		out = []
		id = self.index([i for i in self if i.id == id][0])
		
		for i in range(len(self)):
			out.append((self[i], self[id].distance(self[i])))
			
		out = sorted(out, key=lambda result: result[1])
		
		if(limit is not None):
			return out[:limit]
		else:
			return out
		
	def furthest(self, id, limit=10):
		out = self.closest(id, limit=None)
		out = sorted(out, key=lambda result: result[1], reverse=True)
		
		if(limit is not None):
			return out[:limit]
		else:
			return out
		
	def __repr__(self):
		return 'PlaceVectors(' + ', '.join([str(i) for i in self]) + ')'
		
	def __str__(self):
		return self.__repr__()
		
pvs = PlaceVectors(getPVs('PlaceVector', places))
pvfs = PlaceVectors(getPVs('PlaceVectorFull', places))
pvas = PlaceVectors(getPVs('PlaceVectorApp', places))