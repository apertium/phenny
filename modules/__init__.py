from __init__ import all_modules
__all__ = all_modules(__file__)


def caseless_equal(str_a, str_b):
	return str_a.casefold() == str_b.casefold()

def caseless_list(str_list):
	return list(map(str.casefold, str_list))
