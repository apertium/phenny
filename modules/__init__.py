def caseless_equal(str_a, str_b):
	return str_a.casefold() == str_b.casefold()

def caseless_list(str_list):
	return list(map(str.casefold,str_list))