def caseless_equal(stra, strb):
	return stra.casefold() == strb.casefold()

def caseless_list(str_list):
	return list(map(str.casefold,str_list))