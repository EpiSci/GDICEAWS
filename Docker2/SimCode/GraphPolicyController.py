from GraphNode import GraphNode
import numpy as np

class GraphPolicyController:
    def __init__(self, numNodes, alpha, numTMAs, numObs, numSamples):
        self.nodes = []
        self.numNodes = numNodes
        self.alpha = alpha #learning rate
        self.numObs = numObs
        self.numTMAs = numTMAs
        self.numSamples = numSamples

        for idxNode in range(0,self.numNodes):
            self.appendToGraphNodes(idxNode, numTMAs, numObs, numSamples)
        
        self.sample(numSamples)
            
    def sample(self, numSamples):
        for idxNode in range(0,len(self.nodes)):
            #sample TMAs at the node, using updated pdf of best nodes 
            self.nodes[idxNode].sampleTMAs(numSamples)

            #sample node transitions, using updated pdf of best trasitions
            for idxObs in range(0,self.numObs):
                self.nodes[idxNode].sampleTrans(idxObs,numSamples)
                
    def setGraph(self, idxSample):
        for idxNode in range(0,len(self.nodes)):
            #sets both TMA to be executed at node, and next-node transition
            self.nodes[idxNode].setToSampleNumber(idxSample)
            
    def updateProbs(self, curIterationValues, N_b, iter):
        output = False;
        
        #keep best N_b samples that are non-zero (for this specific problem)
        sortedValues = np.sort(curIterationValues)
        sortingIndices = np.argsort(curIterationValues)
        maxValues = sortedValues[1:N_b]
        maxValueIdxs = sortingIndices[1:N_b]
        if (iter != 0):
            maxValueIdxs = maxValueIdxs[maxValues>0]
            
        N_b = len(maxValueIdxs)
        if (output):
            print(str(N_b) + " samples with value >0 found!")
            
        #make sure you have non-zero number of best samples
        #this allows us to avoid re-normalization of pdfs, which we'd have to do if N_b = 0
        if (N_b > 0):
            weightPerSample = 1/N_b
            
            #go through each best sample of the N_b set
            for idxNode in range(0,len(self.nodes)):
                #this weighting takes care of the filtering/learning step automatically.
                pVectorTMA_new = np.multiply(self.nodes[idxNode].pVectorTMA,(1-self.alpha))
                pTableNextNode_new = np.multiply(self.nodes[idxNode].pTableNextNode,(1-self.alpha))
                
                for idxSample in maxValueIdxs:
                    if(output):
                        print("Updating weights using \"best\" sample " + str(idxSample))
                    #update pVectorTMA pdf at "best" TMA location
                    sampleTMA = self.nodes[idxNode].TMAs[idxSample]
                    pVectorTMA_new[sampleTMA] = pVectorTMA_new[sampleTMA] + weightPerSample*self.alpha
                        
                    #update pTableNextNode pdf at "best" next node locations
                    for idxObs in range(0,self.numObs):
                        sampleNextNode = int(self.nodes[idxNode].transitions[idxSample,idxObs])
                        pTableNextNode_new[sampleNextNode, idxObs] = pTableNextNode_new[sampleNextNode, idxObs] + weightPerSample*self.alpha
            
                #update the pdfs
                self.nodes[idxNode].pVectorTMA = pVectorTMA_new
                self.nodes[idxNode].pTableNextNode = pTableNextNode_new

    def appendToGraphNodes(self, idxNode, numTMAs, numObs, numSamples):
        newGraphNode = GraphNode(self.numNodes, idxNode, numTMAs, numObs, numSamples)
        self.nodes.append(newGraphNode)
        
    def printNodes(self):
        print("GraphPolicyController nodes: " + self.nodes[:].myTMA)
        
    def getNextTMAIdx(self, curNodeIdx, curXeIdx):
        #based on current node and received observation, move to next node in policy controller
        newPolicyNodeIdx = self.nodes[curNodeIdx].nextNode[curXeIdx]
        #assign new TMA based on newly-assigned node in the policy controller
        newTMAIdx = self.nodes[newPolicyNodeIdx].myTMA
        return newPolicyNodeIdx, newTMAIdx
        
    #table getter
    def getPolicyTable(self):
        TMAs = np.zeros((self.numNodes,1))
        transitions = np.zeros((self.numNodes, self.numObs))
        
        for idxNode in range(0,self.numNodes):
            TMAs[idxNode] = self.nodes[idxNode].myTMA
            transitions[idxNode,:] = self.nodes[idxNode].nextNode
        return TMAs, transitions
            
    def setPolicyUsingTables(self, TMAs, transitions):
        for idxNode in range(0,self.numNodes):
            self.nodes[idxNode].myTMA = TMAs[idxNode]
            self.nodes[idxNode].nextNode = transitions[idxNode,:]
