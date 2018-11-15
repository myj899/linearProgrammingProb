import numpy as np
import math

# simplex algorithm
'''
Need a super class that takes constants into account in objFun
'''
class Simplex(object):
	'''
	max 3x+2y 
	s.t. x+2y <=4
		 x-y <= 1
		 x,y >= 0

	with slack variables, translated into
	c = [3, 2]
	A = [[1,  2],
		 [1, -1]]
	b = [4, 1]

	For now, assume proper c, A, b inputs

	for min f(x), use duality of simplex
	'''
	'''
	method based on multiple sources:
	https://www.youtube.com/watch?v=XK26I9eoSl8
	https://hubpages.com/technology/Simplex-Algorithm-in-Python
	https://jeremykun.com/2014/12/01/
					linear-programming-and-the-simplex-algorithm/
	https://www.cs.cmu.edu/afs/cs/academic/
					class/15780-s16/www/slides/linear_prog.pdf
	MAIN SOURCE: https://www.youtube.com/watch?v=BdtdYlUIXak
	MAIN SOURCE: http://web.mit.edu/15.053/www/AMP-Chapter-04.pdf

	tableu from above example should look like 
	x  y  s1  s2  P  b
	------------------
	1  2   1   0  0  4   Constraint Rows
	1  -1  0   1  0  1
	------------------
	-3 -2  0   0  1  0   ObjFun row
	'''
	'''
	Things to Consider:
	- objective function has constant number
	- infeasible solution
	- infinite solution

	Currently only handles feasible single point solution
	'''
	def __init__(self, c, A, b, maxi):
		self.varLen = len(c) # number of variables
		self.conLen = len(b) # number of slack variables(aka # of constraints)
		#np.concatenate((x, np.identity(len(x))),axis=1)
		self.maxi = maxi

		bCol = np.array([b + [0]], dtype=float) # assumes no constant val in objfun
		varTable = np.array(A+[c], dtype=float)
		mainTable = np.concatenate((varTable, bCol.T),axis=1)
		if not self.maxi: # minimization prob as dual prob
			mainTable = mainTable.T

		# split mainTable into table with factors and table with constants
		bCol = np.array([mainTable[:,-1]])
		if self.maxi:
			factorTable = mainTable[:,:self.varLen]
			slckAndP = np.identity(self.conLen+1) #num of slack = num of constraints
		else: 
			factorTable = mainTable[:,:self.conLen]
			slckAndP = np.identity(self.varLen+1)
		# multiply -1 to objfun row
		factorTable[-1,:] *= -1

		self.tableu = np.concatenate((factorTable,slckAndP,bCol.T),axis=1)


	# if any variable with negative factor, can improve
	def canImprove(self):
		for varFactor in self.tableu[-1]: #objFun
			if varFactor < 0:
				return True
		return False

	# find pivRow & pivCol; same method for both maxi and mini
	def findPivot(self):
		# pivotCol is col with most negative factor in objfun
		minFact = 0 # minimum factor of objfun
		objFun = self.tableu[-1]
		for col in range(len(objFun)-2): # exclude P and b col 
			if objFun[col] < minFact:
				minFact = objFun[col]
				self.pivCol = col
				#self.pivColSet = (self.pivColSet).union([col])

		ratios = []
		for row in range(len(self.tableu)-1): # exclude objfun row
			if (abs(self.tableu[row][self.pivCol]) > 0 
				and self.tableu[row][-1]/self.tableu[row][self.pivCol] > 0):
				constant = self.tableu[row][-1]
				ratios.append(constant/self.tableu[row][self.pivCol])
			else: ratios.append(float("inf")) #just a place holder
		# pick row index minimizing the quotient
		self.pivRow = ratios.index(min(ratios))


	#destructively change tableu
	def pivot(self):
		pivR, pivC = self.pivRow, self.pivCol
		# divide whole pivRow so factor @ pivRow&Col = 1
		self.tableu[pivR] = np.divide(self.tableu[pivR], float(self.tableu[pivR][pivC]))
		
		# subtract the rest with pivRow*factor
		notPivRows = set(list(range(len(self.tableu)))).difference(set([pivR]))
		for row in notPivRows:
			factor = self.tableu[row][pivC]
			self.tableu[row] -= np.dot(self.tableu[pivR], factor)
		
	def primalSolution(self):
		# initialize values of all variables
		primal = [0]*self.varLen
		# find basic variable solutions and record them
		for col in range(self.varLen):
			oneFound = False
			varI = 0
			varRow = 0
			for row in range(len(self.tableu)):
				if self.tableu[row][col] == 1:
					if not oneFound: oneFound, varI, varRow = True, col, row
					else: 
						oneFound = False
						break
			if oneFound: primal[varI] = self.tableu[varRow][-1]
		return primal

	def dualSolution(self):
		dual = [0]*self.varLen
		# for every "slack variables" in dual problem
		for col in range(self.conLen, self.conLen+self.varLen):
			objFunRow = self.tableu[-1]
			# solution of primal problem is the number at objfunrow
			newVal = objFunRow[col]
			dual[col-self.conLen] = newVal
		return dual


	def objectiveValue(self):
		return self.tableu[-1][-1]

	def simplex(self):
		#np.set_printoptions(precision=2)
		#print(self.tableu)
		while self.canImprove():
			self.findPivot()
			self.pivot()
			#print(self.tableu)
		if self.maxi: solution = self.primalSolution()
		else: solution = self.dualSolution()
		return solution, self.objectiveValue()