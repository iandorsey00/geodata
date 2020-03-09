import codecs
import re

def readin(file):
	with codecs.open(file, 'r', 'utf-8') as infile:
		return [i.strip().split('|') for i in infile]
		
def writeout(list, file):
	with codecs.open(file, 'w', 'utf-8') as outfile:
		for i in list:
			outfile.write('|'.join(i) + "\n")

def inner_join(first_list, second_list, first_index=0, second_index=0, first_slice_index=0, second_slice_index=1):
	out = []
	
	for fl_item in first_list:
		for sl_item in second_list:
			if(fl_item[first_index] == sl_item[second_index]):
				out.append(fl_item[first_slice_index:] + sl_item[second_slice_index:])
				
	return out
	
def create_key(census_string):
	out = ""
	
	census_string = re.sub(r'ñ', 'n', census_string)
	
	def ct_strip(entire_string):
		return re.sub(r'( city,| town,| CDP[,| ]).*?$', '', entire_string)
		
	if(re.search(r' CDP[,| ]', census_string)): # CDP
		if(census_string == "Green Acres CDP, California"):
			out = "greenacres/cdp/riverside"
		elif(census_string == "Greenacres CDP, California"):
			out = "greenacres/cdp/kern"
		else:
			out = ct_strip(census_string) + '/cdp'
			
			if(re.search(r'\([^\)]+ County\)', census_string)):
				county_pt = re.sub(r'^.*\(([^\)]+) County\).*$', r'\1', census_string)
				out = out + '/' + county_pt
				
	else: # city or town
		if(census_string == "San Buenaventura (Ventura) city, California"):
			out = 'ventura'
		elif(census_string == "El Paso de Robles (Paso Robles) city, California"):
			out = 'pasorobles'
		else:
			out = ct_strip(census_string)
			
	out = re.sub(r'[ \(\)\-.]', '', out).lower()
	
	return out

def destring(final_array):
	out = list(final_array)
	for i in range(len(out)):
		for j in range(len(out[0])):
			try:
				if '.' in out[i][j]:
					out[i][j] = float(out[i][j])
				else:
					out[i][j] = int(out[i][j])
			except ValueError:
				pass
	return out
	
def restring(final_array):
	out = list(final_array)
	for i in range(len(out)):
		for j in range(len(out[0])):
			out[i][j] = str(out[i][j])
	return out