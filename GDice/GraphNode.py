import numpy as np
from discretesample import discretesample

#A single Graph Node

class GraphNode:
    def __init__(self, numNodesInFullGraph, idxNode, numTMAs, numObs, numSamples):
        self.myTMA = None #TMA to be executed in this node
        self.nextNode = None #1-by-numObs vector for outgoing edges, indicating which node idx to connect to next
        self.TMAs = None #vector of sampled TMAS
    
        self.idxNode = idxNode
        self.numTMAs = numTMAs
        self.numObs = numObs
        self.numNodesInFullGraph = numNodesInFullGraph
        self.transitions = np.zeros((numSamples, numObs)).astype(int) #matrix of sampled next-node transitions
        self.pVectorTMA = np.ones((numTMAs, 1))/numTMAs #numTMAs-by-1 vector, representing probability of choosing a TMA
        self.pTableNextNode = np.ones((numNodesInFullGraph, numObs))/numNodesInFullGraph #numNodesInFullGraph-by-numObs matrix, representing probability of choosing the next graph node based on observation received
        
    def sampleTMAs(self, numSamples):
        self.TMAs = discretesample(self.pVectorTMA, numSamples)
    
    def sampleTrans(self, idxObs, numSamples):
        self.transitions[:,idxObs] = discretesample(self.pTableNextNode[:,idxObs], numSamples)
        
    def setToSampleNumber(self, idxSample):
        self.myTMA = self.TMAs[idxSample]
        self.nextNode = self.transitions[idxSample,:]
        
    def setTMA(self, TMA):
        self.myTMA = TMA
        
    def setNextNode(self, obsIdx, nextNodeIdx):
        #obsIdx corresponds to those defined in properties above
        self.nextNode[obsIdx] = nextNodeIdx