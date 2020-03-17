from GraphPolicyController import GraphPolicyController
from random_config import newconfig
import numpy as np
import boto3
import pickle
import time
import sys

#Initialize-------------------------------------------------------------------------------------------
#Generate Policy Containers
numNodes = 4 #number of graph controller nodes
alpha = 0.05 #learning rate
numTMAs = 4 #cardinality of TMA space
numObs = 12 #cardinality of observation space
N_k = 50 #number of iterations
N_r = 100 #How many times the simulation will run to get its averate.
N_s = 50 #number of samples per iteration
N_b = 5 #number of "best" samples kept from each iteration
N_agent = 1 #number of agnet
bestValue = -10000000 #best value so far

idxStart = 13

Controllers = [] #collect controllers for each agent

if idxStart == 0:
	for idxAgent in range(0,N_agent):
		mGraphPolicyController = GraphPolicyController(numNodes, alpha, numTMAs, numObs, N_s)
		Controllers.append(mGraphPolicyController)
else:
	iteration = idxStart-1
	s3 = boto3.resource('s3', region_name = 'us-west-1')
	bucket = s3.Bucket('adfproject')
	directory_name = "policy" + str(iteration)
	with open('pdump', 'wb') as data:
		bucket.download_fileobj(directory_name + '/policy', data)
	with open('pdump', 'rb') as data:
		Controllers = [pickle.load(data)]
	#Retrieve reward.
	print("Retrieving Rewards")
	rewards = np.zeros((N_s, N_r))

	db = boto3.resource("dynamodb", region_name = 'us-west-1')
	table = db.Table("ADFEval" + str(iteration))
	tableContents = table.scan()["Items"]
	for i in tableContents:
		trialNum = int(i["TrialNum"])
		col = trialNum % N_r
		row = int((trialNum - col)/N_r)
		try:
			rewards[row,col] = float(i["reward"])
		except:
			rewards[row,col] = 0
	curIterationValues = np.sum(rewards, axis=1)/N_r
	print("Rewards Retrieved")
	print(curIterationValues)

	#Process Values
	print("Processing Rewards")

	for idxSample in range(0,N_s):

		if curIterationValues[idxSample] > bestValue:
			#Record New Best Value Parameters
			bestValue = curIterationValues[idxSample]

			Controllers[0].setGraph(idxSample)
			[best_TMAs, best_Transitions] = Controllers[0].getPolicyTable();

			for idxAgent in range(1, N_agent):
				Controllers[idxAgent].setGraph(idxSample)
				[bestTMAs, bestTransitions] = Controllers[idxAgent].getPolicyTable();
				best_TMAs = np.append(best_TMAs,bestTMAs, axis = 0)
				best_Transitions = np.append(best_Transitions, bestTransitions, axis = 0)
			np.save("best_TMAs", best_TMAs)
			np.save("best_Transitions", best_Transitions)

	for idxAgent in range(0,N_agent):
		Controllers[idxAgent].updateProbs(curIterationValues, N_b, iteration)

	print("Iteration " + str(iteration) + " Complete")



for idxIter in range(idxStart,N_k):

	#Sample and Save------------------------------------------------------------------------------------
	s3 = boto3.client('s3')
	bucket = "adfproject"

	#Sample Policy
	directory_name = "policy" + str(idxIter)
	s3.put_object(Bucket=bucket, Key=(directory_name + '/'))
	print("Uploading Policy")
	for idxAgent in range(0,N_agent):
		Controllers[idxAgent].sample(N_s)
		s3.put_object(Body = pickle.dumps(Controllers[idxAgent]),Bucket=bucket, Key=(directory_name + '/policy'))

	#Sample Configuration
	directory_name = "config" + str(idxIter)
	s3.put_object(Bucket=bucket, Key=(directory_name + '/'))
	print("Uploading Configurations")
	for idxRun in range(0,N_r):
		newconfig(idxRun)
		s3.upload_file(Filename = ("./configuration/rc" + str(idxRun) +".xml"), Bucket=bucket, Key = directory_name + '/rc' + str(idxRun) + ".xml")


	#Propogate to table-------------------------------------------------------------------------------
	#Create table
	print("Making Table")
	db = boto3.client('dynamodb')
	tablename = "ADFEval" + str(idxIter)

	existing_tables = db.list_tables()['TableNames']

	if tablename in existing_tables:
		print("Deleteing Old Table")
		db.delete_table(TableName=tablename)
		waiter = db.get_waiter('table_not_exists')
		waiter.wait(TableName=tablename)
		print ("Old Table Deleted")

	db.create_table(
		TableName = tablename,
		KeySchema = [
			{
				'AttributeName': 'TrialNum',
				'KeyType': 'HASH'
			}
		],
		AttributeDefinitions = [
			{
				'AttributeName': 'TrialNum',
				'AttributeType': 'N'
			}
		],
		ProvisionedThroughput={
			'ReadCapacityUnits': 10,
			'WriteCapacityUnits': 10
		}
	)


	waiter = db.get_waiter('table_exists')
	waiter.wait(TableName=tablename)
	print("New table " + tablename + " created.")

	print("Filling table with " + str(N_s*N_r) + " entries.")
	dbr = boto3.resource('dynamodb')
	table = dbr.Table(tablename)
	with table.batch_writer() as batch:
		for idxSample in range(0,N_s):
			for idxRun in range(0,N_r):
				batch.put_item(
					Item = {
						'TrialNum': idxSample*N_r+idxRun,
						'PolicyNum': idxSample,
						'Configuration': idxRun
					}
				)
	print("Table filled.")


	#Assign Jobs
	print("Generating Jobs")
	batch = boto3.client('batch')

	for idxJob in range(0, N_s*N_r):
		batch.submit_job(
			jobName='adf-trial-' + str(idxJob) + '-itr-' + str(idxIter), # use your HutchNet ID instead of 'jdoe'
			jobQueue='adf-job0queue', # sufficient for most jobs
			jobDefinition='adf-job', # use a real job definition
			containerOverrides={
				"environment": [ # optionally set environment variables
					{"name": "TRIAL", "value": str(idxJob)},
					{"name": "ITERATION", "value": str(idxIter)}
				]
			})
	print("Jobs Generated")
	#)


	#Wait till finished
	print("Monitoring Job Completion")
	while True:
		batch = boto3.client('batch')
		sub = len(batch.list_jobs(jobQueue = "adf-job0queue", jobStatus = 'SUBMITTED')["jobSummaryList"])
		pen = len(batch.list_jobs(jobQueue = "adf-job0queue", jobStatus = 'PENDING')["jobSummaryList"])
		runnable = len(batch.list_jobs(jobQueue = "adf-job0queue", jobStatus = 'RUNNABLE')["jobSummaryList"])
		sta = len(batch.list_jobs(jobQueue = "adf-job0queue", jobStatus = 'STARTING')["jobSummaryList"])
		running = len(batch.list_jobs(jobQueue = "adf-job0queue", jobStatus = 'RUNNING')["jobSummaryList"])
		if (sub+pen+runnable+sta+running) == 0:
			print("Jobs done.")
			break
		else:
			print("-")
			print("Jobs still going.")
			print("Submitted: " + str(sub))
			print("Pending: " + str(pen))
			print("Runnable: " + str(runnable))
			print("Starting: " + str(sta))
			print("Running: " + str(running))
			print("-")
			time.sleep(10)
			sys.stdout.write("\033[F \033[F \033[F \033[F \033[F \033[F \033[F \033[F")

	#Retrieve reward.
	print("Retrieving Rewards")
	rewards = np.zeros((N_s, N_r))

	tableContents = table.scan()["Items"]
	for i in tableContents:
		trialNum = int(i["TrialNum"])
		col = trialNum % N_r
		row = int((trialNum - col)/N_r)
		try:
			rewards[row,col] = float(i["reward"])
		except:
			rewards[row,col] = 0
	curIterationValues = np.sum(rewards, axis=1)/N_r
	print("Rewards Retrieved")
	print(curIterationValues)

	#Process Values
	print("Processing Rewards")

	for idxSample in range(0,N_s):

		if curIterationValues[idxSample] > bestValue:
			#Record New Best Value Parameters
			bestValue = curIterationValues[idxSample]

			Controllers[0].setGraph(idxSample)
			[best_TMAs, best_Transitions] = Controllers[0].getPolicyTable();

			for idxAgent in range(1, N_agent):
				Controllers[idxAgent].setGraph(idxSample)
				[bestTMAs, bestTransitions] = Controllers[idxAgent].getPolicyTable();
				best_TMAs = np.append(best_TMAs,bestTMAs, axis = 0)
				best_Transitions = np.append(best_Transitions, bestTransitions, axis = 0)
			np.save("best_TMAs", best_TMAs)
			np.save("best_Transitions", best_Transitions)

	for idxAgent in range(0,N_agent):
		Controllers[idxAgent].updateProbs(curIterationValues, N_b, idxIter)

	print("Iteration " + str(idxIter) + " Complete")
	#Repeat
