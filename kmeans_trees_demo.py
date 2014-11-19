# A simple demo of K-Means Trees for big data with synthetic data
# (c) 2014 by Luis Argerich
# Any kind of educational/research use of this code is allowed

from __future__ import division
import random
import math
import zlib
from pprint import *
import csv
import numpy as np

print "A simple demo of K-Means Trees"

# A large distance constant
LARGE_DISTANCE = 999999999

# Number of points
N = 50
# Number of dimensions
dims = 2
# The amount of points in each cluster, this is the 
# maximum number of distances that need to be calculated
k = 10

# An internal count for the number of distances computed
computed_distances = 0

# Create the root of the tree
root = {"c":[0 for _ in range(0,dims)],"n":0,"points":[]}

# Online update of centroid proportional to the number of points in the cluster
def update_centroid(centroid,point,num):
	for i in range(0,len(centroid)):
		centroid[i]=centroid[i]+(1/num*(point[i]-centroid[i]))
	return centroid

# This is simple a euclidean distance
# No need for square root since we only use it to compare distances
# Max is a threshold beyond that we don't need the distance at all
def compute_distance(p1,p2,max):
	global computed_distances
	distance = 0
	computed_distances+=1
	for i in range(0,len(p1)):
		distance = distance + math.pow((p1[i]-p2[i]),2)
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
	max_distance = 999999
	for i in range(0,len(node['points'])):
		new_point = node['points'][i]['c']
		distance = compute_distance(point,new_point,max_distance)
		if distance<max_distance or len(heap)<k:
			heap.append((distance,new_point,i))
			# Sort and keep the k minimum distances
			heap = sorted(heap)
			heap = heap[:k]
			(max_distance,max_point,i) = heap[len(heap)-1]
	if len(heap)>0:
		(di,pt,best_i)=heap[0]
		heap.extend(find_k_nearest_neighbors(point,node['points'][best_i],k))
		heap = sorted(heap)
		heap = heap[:k]
	return heap

# Inserts a point in the node
# if the node has space then we just add the point and adjust the centroid
# if the node is full (n==k) then we look for the closest child node
# and insert there (recursively)
def insert(point,node):
	# Convert the point to a node
	node_point = {"c":point,"n":0,"points":[]}
	if node['n']<k:
		node['points'].append(node_point)
		node['n']+=1
		node['c']=update_centroid(node['c'],point,node['n'])
	else:
		index = find_closest_centroid(point,node['points'])
		# The magic recursive call
		insert(point,node['points'][index])

for i in range(0,N):
	# Create a random point
	point = [random.random() for _ in range(0,dims)]
	insert(point,root)

print "----------------------"
pprint(root)
print "Done!"
print "Computed distances:"+str(computed_distances)

for i in range(0,10):
	some_point = [random.random() for _ in range(0,dims)]
	print "Now searching for:"
	pprint(some_point)
	l = find_k_nearest_neighbors(some_point,root,3)
	pprint(l)