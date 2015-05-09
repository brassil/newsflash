import math

R = 3959 # radius of earth, in miles

# bounding box for continental US
# SW = (24.9493, -125.0011)
# NE = (49.5904, -66.9326)

# bounding box for manhattan (same as API call)
SW = (40.63, -74.12)
NE = (40.94, -73.68)

# format = [[latmin, latmax], [lngmin, lngmax]]


def get_corners(box):
	'''
	takes in a box, in the format used by trending_location,
	and returns the 4 corners as a list (each corner is a duple)
	in the order SW, NW, NE, SE
	'''
	return [(box[0][0],box[1][0]),(box[0][1],box[1][0]),
			(box[0][1],box[1][1]),(box[0][0],box[1][1])]


def inside_box(p,box):
	if p[0] < box[0][0] or p[0] > box[0][1]: return False
	if p[1] < box[1][0] or p[1] > box[0][1]: return False
	return True

def trending_location(points, corners=False):
	'''
	ugh it's not gonna work bc what if a split happens through the middle
	of the cluster? well, at least if we do the entire united states,
	it's less likely to happen? nah it still is bad

	Ok so we're going to resolve the issue of when a split happens through
	the middle of the cluster in the following way: if you split and
	one half isn't >2x as big as the other one, try to split one more time
	in the other direction (i.e. ignore this split and try the other way).
	If that still doesn't work, then break & return. We use 'end' as a flag
	so that we know if this loop is a 2nd try to reduce the size of the box.


	This will fix the issue in all cases EXCEPT if the cluster is at 
	the exact centroid. 

	Also maybe we should update it so that it tries both latitudinal and 
	longitudinal splits at each iteration and chooses the better one. idk.

	also note that the extra corner that isn't used in the split will still happen
	'''
	box = [[SW[0], NE[0]], [SW[1], NE[1]]]
	i = 1 # split on longitude first (0 is lat)
	end = False

	# get rid of this eventually, we only need it for intermediate bounding box visualization
	corners = []

	# ignore points not contained in the original bounding box
	points = [p for p in points if inside_box(p,box)]



	# only run while the bounding box is > 1 square mile
	while (box[0][1]-box[0][0])*(box[1][1]-box[1][0]) > .0001:
		# print the bounding box
		# print [(box[0][0],box[1][0]),(box[0][1],box[1][1])]
		if corners: corners.append(get_corners(box))


		mid = box[i][0] + (box[i][1] - box[i][0]) / 2 

		# less than vs. greater than the mid point
		l = []
		g = []

		for x in points:
			if x[i] < mid:
				l.append(x)
			else:
				g.append(x)

		# now figure out which side has more and if it's a lot more
		# the 2* thing is just a basic idea, prob not what we should
		# use in the end. 
		if len(g) > 2*len(l):
			end = False
			box[i][0] = mid
			i = (1 if i==0 else 0)
			points = g

		elif len(l) > 2*len(g):
			end = False
			box[i][1] = mid
			i = (1 if i==0 else 0)
			points = l

		else:
			if not end:
				end = True
				i = (1 if i==0 else 0)
			else:
				break # it's not a significant change so end it

	# you get here either if the bounding box has become too small,
	# or if we split the box and there was no significant change
	# in size between one and the other side
	return box, get_dist(box), len(points), corners



def get_dist(box):
	'''
	Calculate the distance between two coordinates by latitude and longitude
	answer from http://stackoverflow.com/a/365853
	'''
	d_lat = math.radians((box[0][1]-box[0][0]))
	d_lon = math.radians((box[1][1]-box[1][0]))
	lat1 = math.radians(box[0][0])
	lat2 = math.radians(box[0][1])

	a = math.sin(d_lat/2)**2 + math.sin(d_lon/2)**2 * math.cos(lat1) * math.cos(lat2)

	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

	return R * c
