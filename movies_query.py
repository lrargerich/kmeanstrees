from __future__ import division
import random
import math
import zlib
from pprint import *
import csv
import copy
import pickle
import numpy as np
import sys

computed_distances=0

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


with open('movies_kmeans.pickle', 'rb') as handle:
  root = pickle.load(handle)

with open('movies_dic', 'rb') as handle2:
  movies = pickle.load(handle2)

print "Doing a search"
a_movie = movies[int(sys.argv[1])]
results = find_k_nearest_neighbors(a_movie,root,int(sys.argv[2]))
for (distance,point,id) in results:
	print "Movie_id:"+str(id)+" distance:"+str(distance)