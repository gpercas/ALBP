from itertools import islice, chain

def list_included(list_1, list_2):
	"""
	Evaluate if all the elements of list_1 are inside list_2.
	Returns True if positive

	>>> list_included([1,2,3], [1,2,3,4,5])
		True
	>>> list_included([], [1,2,3,4,5])
		True
	>>> list_included([66,1,2], [1,2,3,4,5])
		False
	"""

	set_A, set_B = set(list_1), set(list_2)
	return set_A.issubset(set_B)

def list_intersection(list_1, list_2):
	"""
	Evaluate if all the elements of list_1 are inside list_2.
	Returns True if positive

	>>> list_included([1,2,3], [1,2,3,4,5])
		True
	>>> list_included([], [1,2,3,4,5])
		True
	>>> list_included([66,1,2], [1,2,3,4,5])
		False
	"""

	set_A, set_B = set(list_1), set(list_2)
	return set_A.intersection(set_B)


def recombine_list(list_, idx):
	"""
	Rearranges a list by convenience taking the passed index as the start position

	>>> recombine_list([1,2,3,4,5,6], 0)
		[1,2,3,4,5,6]
	>>> recombine_list([1,2,3,4,5,6], 1)
		[2,3,4,5,6,1]
	>>> recombine_list([1,2,3,4,5,6], 3)
		[4,5,6,1,2,3]
	"""
	return chain(islice(list_, idx + 1, None), islice(list_, None,  idx))