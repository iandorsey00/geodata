import re

def number(in_number):
	try:
		float(in_number)
		out = "{0:,}".format(in_number)
	except (TypeError, ValueError):
		out = '<ref name="ND" />'
		
	return out
	
def currency(in_number):
	try:
		float(in_number)
		out = "$" + "{0:,}".format(in_number)
	except (TypeError, ValueError):
		out = '<ref name="ND" />'
		
	return out

def process(data_list):
	out = ''
	
	for i in data_list:
		# place
		place = i[0]
		place = re.sub(r", California$", r"", place)
		place = re.sub(r" (city|town|CDP)$", r"", place)
		place = re.sub(r" CDP \(", r" (", place)
		place = re.sub(r"^(.*)$", r"[[\1, California|\1]]", place)
	
		# county
		county = i[1]
		if ',' not in county:
			county = re.sub(r" County", r"", county)
			county = re.sub(r"^(.*?)$", r"[[\1 County, California|\1]]", county)
		else:
			first_county = re.sub(r"^(.*?),.*$", r"\1", county)
			first_county = re.sub(r" County", r"", first_county)
			first_county = re.sub(r"^(.*?)$", r"[[\1 County, California|\1]]", first_county)
			
			second_county = re.sub(r"^.*?, (.*?)$", r"\1", county)
			second_county = re.sub(r" County", r"", second_county)
			second_county = re.sub(r"^(.*?)$", r"[[\1 County, California|\1]]", second_county)
			
			county = first_county + "<br />" + second_county
		
		# pop
		pop = number(i[2])
			
		# pd
		pd = number(i[3])
		
		# ucr_vc_total
		ucr_vc_total = number(i[4])
		
		# ucr_vcr
		ucr_vcr = number(i[5])
		
		# ucr_pc_total
		ucr_pc_total = number(i[6])
		
		# ucr_pcr
		ucr_pcr = number(i[7])
		
		out = out + "|-\n"
		out = out + "| " + place + " || " + county + " || " + pop + " || " + pd + " || " + ucr_vc_total\
		+ " || " + ucr_vcr + " || " + ucr_pc_total + " || " + ucr_pcr
		out = out + "\n"
		
	return out
	
def process_co(data_list):
	out = ''
	
	for i in data_list:
	
		# county
		county = i[0]
		county = re.sub(r"^(.*?) County, California$",\
		r"[[\1 County, California|\1]]", county)
			
		# pop
		#pop = number(i[1])
			
		# pd
		#pd = number(i[2])
		
		# inc_pci
		#inc_pci = currency(i[3])
		
		# inc_mhi
		#inc_mhi = currency(i[4])
		
		# inc_mfi
		#inc_mfi = currency(i[5])
		
		out = out + "|-\n"
		out = out + "| " + county + " || " + i[1] + " || " + i[2] + " || " + i[3]\
		+ " || " + i[4] + " || " + i[5] + " || " + i[6]
		out = out + "\n"
		
	return out