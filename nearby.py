#!/usr/local/bin/python
# encoding: utf-8
__author__ = "AlexChung"
__email__ = "achung@ischool.berkeley.edu"
__python_version = "2.7.2"

from kdtree import KDTree
import sys
import time

"""
Use:
On Unix, you could run this program with input file like:
(For Example) % cat sample_input.txt | python nearby.py

Description: (Near Neighbor Search)
Using kD trees (Recursively search subtrees that could have near neighbor).  
kD tree recursively partition k-dimensional space into 2 halfspaces.
This program implements 2D trees as binary search trees. At each depth of the tree, 
X and Y coordinates are used alternatively as keys to partition a list of data points.
  
1) Build a hashmap with the point's x,y-coordinates as the keys to topic IDs
2) Since more than one topic IDs could have the same location in plane, the hashmap
 	element points to a linked list containing the topic IDs
3) Build a topic array with the topic ID reflecting the array element location.    
4) Each array element points to a list of question IDs 
5) Build 2D Tree to store all the topic locations
6) Foreach query, find the nearest neighboring points using the 2D Tree
7) Foreach neighboring points, the topics hashmap reveals their respective topic IDs
8) Use the topic IDs to locate the question IDs in the topic array 

"""

#GLOBAL Variables
#create a list of topics with each element containing a list of assoc. question IDs
topicQuestion_dict = dict(); #hashmap
topic_dict = dict() #hashmap

def buildTopicMaps(T_lines):
	#Topics
	for T in T_lines:
		topicID, x, y = T.rstrip().split(' ')
		topicID = int(topicID)
		coord = (float(x), float(y)) #tuple of x,y-coord
	
		if coord not in topic_dict:
			#create a linklist of topic IDs for this coordinate b/c
			#there could be multiple topics with same coordinate
			topic_dict[coord] = list()
		#assign topic ID to this coord		
		topic_dict[coord].append(topicID)
	
		#create a set for each topic to record associated question IDs
		topicQuestion_dict[topicID] = list()

def buildQuestionMaps(Q_lines):	
	#Questions
	for Q in Q_lines:
		lineInputs = Q.rstrip().split(' ')
		questionID = int(lineInputs[0])
		Qn = int(lineInputs[1]) #number of topic IDs 
		if Qn > 0:
			topicIDs = lineInputs[2:]
			for t_id in topicIDs:
				topicQuestion_dict[int(t_id)].append(questionID)

def buildKDTree():
	#Create 2DTree with topics' coordinates
	data = topic_dict.keys() 
	tree = KDTree.construct_from_data(data) 
	return tree

def performQueries(N_lines, tree, numTopics):
	#Queries
	for N in N_lines:
		queryType, reqNum, x, y = N.rstrip().split(' ')
		reqNum = int(reqNum)  #number of results required
		coord = (float(x), float(y)) #location for query
		numNeighbors = reqNum
		
		outputList = list() #store output IDs
		if queryType == 't':
			#Topics
			nearestTopics = tree.query(query_point=coord, t=numNeighbors)
		
			for t_coord in nearestTopics:
				topic_list = topic_dict[t_coord] #get all topics with coord. == t_coord
				topic_list.sort() #sort in place (asc)
				topic_list.reverse() #highest number first
				outputList.extend(topic_list) #append all items in t_list to outputList
		
		elif queryType == 'q':
			#Questions
			stopSearch = False
			while (True):
				nearestTopics = tree.query(query_point=coord, t=numNeighbors)
				for t_coord in nearestTopics:
					t_list = topic_dict[t_coord] #get all topics with coord == t_coord
					for t_id in t_list:
						question_list = topicQuestion_dict[t_id]
						question_list.sort() #sort in place (asc)
						question_list.reverse() #highest number first
						for q in question_list:
							if q not in outputList:  #add only if questionID is not in the list
								outputList.append(q)
				
						if len(outputList) >= reqNum: #condition met, stop search
							stopSearch = True #break all outer loops
							break
					if stopSearch:
						break
				if stopSearch:
					break
					
				if numNeighbors >= numTopics:
					break
				#Number of questions condition is not met, expand search by doubling serach space
				numNeighbors = numNeighbors * 2
		else:
			pass
	
		#STDOUT: the first reqNum of nearest topics 
		print (" ".join(str(v) for v in outputList[0:reqNum]))
	
def main():
	#STDIN
	input = sys.stdin.readlines()
	
	#first line of input
	(numT, numQ, numN) = input[0].rstrip().split(' ')
	numT = int(numT)
	numQ = int(numQ)
	numN = int(numN)

	#Build hashmap from topic x,y-coords to topicIDs
	lineIndex = 1
	T_lines = input[lineIndex : numT+lineIndex]
	buildTopicMaps(T_lines)
	
	#Build hashmap from topicID to a list of questionIDs 
	lineIndex += numT
	Q_lines = input[lineIndex : numQ+lineIndex]
	buildQuestionMaps(Q_lines)
	
	#Build KD tree with topic locations
	tree = buildKDTree()  
	
	#Perform nearest neighbors search for each query location
	lineIndex += numQ
	N_lines = input[lineIndex : numN+lineIndex]
	performQueries(N_lines, tree, numT)
	
if __name__ == '__main__':
	#start = time.time()
	main()
	#print ("Elapsed time: %s" % (time.time() - start))
