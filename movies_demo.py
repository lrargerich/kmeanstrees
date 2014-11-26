from __future__ import division
import random
import math
import zlib
from pprint import *
import csv
import copy
import pickle
import numpy as np
from random import shuffle


movies={}
total=0
k = 10
computed_distances=0

# Create the root of the tree
root = {"c":{},"n":0,"points":[],"id":0}

# Online update of centroid proportional to the number of points in the cluster
def update_centroid(centroid,point,num):
	centroid_dims = centroid.keys()
	point_dims = point.keys()
	all_dims = list(set(centroid_dims+point_dims))
	for dim in all_dims:
		if not dim in centroid:
			centroid_value = 0
		else:
			centroid_value = centroid[dim]

		if not dim in point:
			point_value = 0
		else:
			point_value = point[dim]

		new_value=centroid_value+(1/num*(point_value-centroid_value))
		if new_value<>0:
			centroid[dim]=new_value
	return centroid

# This is simple a euclidean distance
# No need for square root since we only use it to compare distances
# Max is a threshold beyond that we don't need the distance at all
def compute_distance(p1,p2,max):
	global computed_distances
	distance = 0
	computed_distances+=1

	p1_dims = p1.keys()
	p2_dims = p2.keys()

	all_dims = list(set(p1_dims+p2_dims))

	for dim in all_dims:
		if not dim in p1:
			p1_value = 0
		else:
			p1_value = p1[dim]
		
		if not dim in p2:
			p2_value = 0
		else:
			p2_value = p2[dim]
		
		distance = distance + math.pow((p1_value-p2_value),2)
		if distance>=max:
			return max
	return distance


# This finds the closest node to a given point
def find_closest_centroid(point,node_points):
	min_distance = 999999999999999
	for i in range(0,len(node_points)):
		candidate=node_points[i]['c']
		distance = compute_distance(point,candidate,min_distance)
		if distance < min_distance:
			min_distance = distance
			best_point = i
	return best_point

# find the k nearest neighbors of a point
# It will compute the distance to each point in the node (less than k)
# and then recursively call for the points in the closest centroid
# so in all it will not do more than levels * k. Being levels in O(log(N))
def find_k_nearest_neighbors(point,node,k):
	# Do this nicely
	# use heap with (distance,point)
	# for the nearest neighbor expand (recursively)
	# merge the results
	heap = []
	real_points = []
	max_distance = 99999999
	#print "searching for:"
	#pprint(point)
	#print "in:"
	#pprint(node)
	# if the node is full then find closest centroid
	for i in range(0,len(node['points'])):
		new_point = node['points'][i]['c']
		new_point_id = node['points'][i]['id']
		distance = compute_distance(point,new_point,999999999)
		if node['points'][i]['n']==0:
			print "Comparing with:"+str(new_point_id)+" distance:"+str(distance)
		
		if distance<max_distance or len(heap)<k:
			if node['points'][i]['n']==0:
				heap.append((distance,new_point,new_point_id))
				# Sort and keep the k minimum distances
				heap = sorted(heap)
				heap = heap[:k]
				(max_distance,max_point,new_point_id) = heap[len(heap)-1]
	#print "heap:"
	#pprint(heap)
	if len(node['points'])>0:
		best_centroid = find_closest_centroid(point,node['points'])
		#print "best_centroid:"+str(best_centroid)
		if node['points'][best_centroid]['n']>0:
			heap.extend(find_k_nearest_neighbors(point,node['points'][best_centroid],k))
			heap = sorted(heap)
			heap = heap[:k]
	return heap


# Inserts a point in the node
# if the node has space then we just add the point and adjust the centroid
# if the node is full (n==k) then we look for the closest child node
# and insert there (recursively)
def insert(id,point,node):
	# Convert the point to a node
	node_point = {"c":point,"n":0,"points":[],"id":id}
	
	# If we are inserting in a node without points, then convert the centroid to a point first
	# We deepcopy the node because we are going to change the centroid (!)
	if node['n']==0:
		node['points'].append({"c":copy.deepcopy(node['c']),"n":0,"points":[],"id":node['id']})
		node['n']+=1

	# Now if we have a centroid and less than k points  we append
	if node['n']<k:
		node['points'].append(node_point)
		node['n']+=1
		node['c']=update_centroid(node['c'],point,node['n'])
	else:
		index = find_closest_centroid(point,node['points'])
		# The magic recursive call
		insert(id,point,node['points'][index])



print "Loading movies"

f = open('Ratings.dat', 'rb')
reader=csv.reader(f)
for row in reader:
	total+=1
	user_id = row[0]
	movie_id = row[1]
	rating = row[2]
	user_id = int(user_id)
	movie_id = int(movie_id)
	rating = int(rating)
	if not movie_id in movies:
		movies[movie_id]={}
	movies[movie_id][user_id]=rating

print "All movies loaded"


print "Inserting movies"
ids = movies.keys()
shuffle(ids)
for movie_id in ids:
	insert(movie_id,movies[movie_id],root)
print "All movies inserted"

with open('movies_kmeans.pickle', 'wb') as handle:
	pickle.dump(root, handle)

with open('movies_dic', 'wb') as handle2:
	pickle.dump(movies, handle2)


print "Doing a search"
a_movie = movies[2990]
results = find_k_nearest_neighbors(a_movie,root,10)
for (distance,point,id) in results:
	print "Movie_id:"+str(id)+" distance:"+str(distance)
