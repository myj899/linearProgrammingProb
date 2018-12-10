import matplotlib
matplotlib.use("TkAgg")
matplotlib.rcParams['toolbar'] = 'None'

import matplotlib.pyplot as plt
from itertools import combinations
import math
import copy

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
#from matplotlib.figure import Figure
import tkinter as tk
from tkinter import ttk
from simplex import Simplex

import csv

import numpy as np
from sympy.solvers import solve
from sympy import Symbol


# GUI with embedded plot
LARGE_FONT= ("Calibri", 30)

''' 
adapted from 
https://pythonprogramming.net/how-to-embed-matplotlib-graph-tkinter-gui/
'''
class SolverGUI(object):

	def __init__(self, master):
		self.master = master
		self.master.configure(background='gray')
		self.master.title("Linear Programming Solver")

		self.mainNotebook = ttk.Notebook(self.master)
		self.mainF1 = ttk.Frame(self.mainNotebook)   # first page; editor
		self.mainF2 = ttk.Frame(self.mainNotebook)   # second page; workspace
		self.mainF3 = ttk.Frame(self.mainNotebook)   # third page; graph

		editor = Editor(self.mainF1, self)
		editor.pack(expand=1, fill="both")
		#workspace = Workspace(self.mainF2, self.master)
		
		#workspace.pack(expand=1, fill="both")

		self.mainNotebook.add(self.mainF1, text='Editor')
		self.mainNotebook.add(self.mainF2, text='Workspace')
		self.mainNotebook.add(self.mainF3, text="Graph")
		self.mainNotebook.pack()

		self.master.update()

	def showFrame(self, cont):
		frame = self.frames[cont]
		frame.tkraise()


class Editor(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)

		self.mainF2 = controller.mainF2
		self.mainF3 = controller.mainF3

		instruction = tk.Label(parent, 
				text="Input the linear problem you are trying to solve below.", 
				font=("Calibri",15), background="#E3E3E3",anchor=tk.W)
		instruction.pack()

		
		p = ttk.Panedwindow(parent, orient="horizontal")
		self.editF1 = tk.LabelFrame(p, background="#A8A8A8", relief=tk.FLAT)
		self.editF2 = tk.LabelFrame(p, text='Problem Summary')

		self.editing = True
		self.solved = False
		self.c = []
		self.A = []
		self.b = []
		self.equality = []

		editBox = EditBox(self.editF1, self, controller)
		editBox.pack(expand=1, fill="both")
		

		p.add(self.editF1)
		p.add(self.editF2)
		p.pack(side=tk.TOP)



class EditBox(Editor):

	def __init__(self, parent, controller, master):
		tk.Frame.__init__(self, parent)
		editBoxAndSolution = ttk.Panedwindow(parent, orient="vertical")
		self.editBoxF1 = tk.LabelFrame(editBoxAndSolution, relief=tk.FLAT)
		self.editBoxF2 = tk.LabelFrame(editBoxAndSolution, text='Solution')

		self.solved = controller.solved # user hasn't tried to solve any problem yet
		self.c = controller.c
		self.A = controller.A
		self.b = controller.b
		self.equality = controller.equality
		self.x = None
		self.z = None
		self.varLen = 1 # before user input, assume at least 1 variable in objfun
		self.conLen = 0 # before user input, assume no constraints
		self.cChanged = False
		self.AChanged = False
		self.bChanged = False
		self.eqChanged = False

		xLabel = tk.Label(self.editBoxF1, text="1. Number of variables:", font=("Calibri", 15))
		xLabel.pack()

		probLabel = tk.Label(self.editBoxF1, text="2. Problem Type:", font=("Calibri", 15))
		probLabel.pack() 
		self.xNumEntry = tk.Entry(self.editBoxF1, validate="key",
										vcmd=(self.register(self.validateInt), 
									'%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W'))

		xNumSet = tk.Button(self.editBoxF1, text="SET", command=lambda: self.onSetXNum())
		xNumSet.pack(side="bottom")
		self.onSetXBool = False

		self.radioMaxi = tk.BooleanVar()
		self.radioMaxi.set(True) # Maxi active by default
		self.maxi = True
		maxCheck = tk.Radiobutton(self.editBoxF1, text="max", variable=self.radioMaxi, 
									value=True, command=self.onSetXNum) #True
		minCheck = tk.Radiobutton(self.editBoxF1, text="min", variable=self.radioMaxi, 
									value=False, command=self.onSetXNum) #False
		maxCheck.pack()
		minCheck.pack()

		ctLabel = tk.Label(self.editBoxF1, 
							text="3. Import or manually enter the objective function values in workspace",
							font=("Calibri", 15))
		ctLabel.pack()

		#importCt = tk.Button(self, text="IMPORT", command=self.onImportCt)
		#initCt = tk.Button(self, text="INITIALIZE", command=self.onInitCt)
		#importCt.pack()
		#initCt.pack()

		ALabel = tk.Label(self.editBoxF1, text="4. Number of constraints:", font=("Calibri", 15))
		ALabel.pack()

		self.ANumEntry = tk.Entry(self.editBoxF1, validate="key",
										vcmd=(self.register(self.validateInt), 
									'%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W'))

		ANumSet = tk.Button(self.editBoxF1, text="SET", command=self.onSetANum)
		ANumSet.pack(side="bottom")
		self.onSetABool = False

		AInitLabel = tk.Label(self.editBoxF1, 
							text="5. Import or manually enter the constraint values in workspace",
							font=("Calibri", 15))
		AInitLabel.pack()

		solveLabel = tk.Label(self.editBoxF1, 
							text="6. Check whether the problem is inputted correctly, then press: ",
							font=("Calibri", 15))
		solveLabel.pack()
		solve = tk.Button(self.editBoxF1, text="SOLVE", command=self.onSolve)
		solve.pack(side="bottom")

		# format alignment of all objects
		xLabel.grid(row=0, column=0, columnspan=5, sticky=(tk.W,tk.S), pady=10)
		self.xNumEntry.grid(row=0, column=6, columnspan=3)
		xNumSet.grid(row=0, column=9, columnspan=1)
		probLabel.grid(row=1, column=0, columnspan=5, sticky=tk.W)
		maxCheck.grid(row=1, column=6, columnspan=1, sticky=tk.W)
		minCheck.grid(row=1, column=7, columnspan=2)
		ctLabel.grid(row=2, column=0, columnspan=10,sticky=tk.W)
		ALabel.grid(row=4, column=0, columnspan=5, sticky=tk.W, pady=10)
		self.ANumEntry.grid(row=4, column=6, columnspan=3)
		ANumSet.grid(row=4, column=9, columnspan=1)
		AInitLabel.grid(row=5, column=0, columnspan=10,sticky=tk.W)
		solveLabel.grid(row=6, column=0, sticky=tk.W)
		solve.grid(row=6, column=1, columnspan=10, sticky=tk.E, pady=10)

		self.figResult, self.axResult = plt.subplots(figsize=(5,5), dpi=100)
		self.resultBox = ResultBox(self.editBoxF2, self)
		self.resultBox.pack(expand=1, fill="both", side=tk.BOTTOM)
		self.resultBox.displayResults()

		self.editF2 = controller.editF2
		self.fig, self.ax = plt.subplots(figsize=(5,7), dpi=100)
		self.summaryBox = SummaryBox(self.editF2, self)
		self.summaryBox.pack(expand=1, fill="both")
		self.summaryBox.displayProb()

		self.mainF2 = controller.mainF2
		self.master = master
		self.workspace = Workspace(self.mainF2, self)

		editBoxAndSolution.add(self.editBoxF1)
		editBoxAndSolution.add(self.editBoxF2)
		editBoxAndSolution.pack()

		self.mainF3 = controller.mainF3
		self.graph = PlotGraph(self.mainF3, self)
		self.graph.pack(expand=1, fill="both")
		self.graphResults()
		# if self.workspace.objFunTable.cSubmitted: # if user submitted c values
		# 	self.c = self.workspace.objFunTable.c
		# if self.workspace.constTable.ASubmitted: # if user submitted A values
		# 	self.A = self.workspace.constTable.A
		# print(self.c)

	def drawSummary(self):
		self.summaryBox.destroy()
		self.summaryBox = SummaryBox(self.editF2, self)
		self.summaryBox.displayProb()
		self.summaryBox.pack(expand=1, fill="both")
		
	def drawWorkspace(self):
		self.workspace.workNotebook.destroy()
		self.workspace.destroy()
		self.workspace = Workspace(self.mainF2, self)
		self.workspace.pack(expand=1, fill="both")

	def drawResults(self):
		self.resultBox.destroy()
		self.resultBox = ResultBox(self.editBoxF2, self)
		self.resultBox.displayResults()
		self.resultBox.pack(expand=1, fill="both")

	def graphResults(self):
		self.graph.destroy()
		self.graph = PlotGraph(self.mainF3, self)
		self.graph.pack(expand=1, fill="both")

	def onSolve(self):
		#update the problem display, run simplex, redraw graph
		self.solved = True
		if not (self.cChanged or self.AChanged or self.bChanged or self.eqChanged):
			self.inputTranslate()
			f = Simplex(self.cSim,self.ASim,self.bSim,self.maxi)
			self.x, self.z = f.simplex()
			self.drawResults()
			self.graphResults()
		

	def inputTranslate(self):
		'''
		if maximization, need all constraints as <=
		if minimization, need all constraints as >=
		objective function remains the same
		'''
		self.cSim = self.c
		self.ASim = copy.deepcopy(self.A)
		# flatten equality and b since they're 2 dimensional
		flatEquality = [item for row in self.equality for item in row]
		self.bSim = [item for row in self.b for item in row]

		for constraint in range(len(self.A)):
			if self.maxi and flatEquality[constraint] == 0: # >=
				for factor in range(len(self.ASim[constraint])):
					self.ASim[constraint][factor] *= -1
				self.bSim[constraint] *= -1
			elif not self.maxi and flatEquality[constraint] == 1: # <=
				for factor in range(len(self.ASim[constraint])):
					self.ASim[constraint][factor] *= -1
				self.bSim[constraint] *= -1

	def onSetXNum(self):
		self.onSetXBool = True
		if self.varLen == int(self.xNumEntry.get()): # extract the value
			self.cChanged = False
		else:
			self.varLen = int(self.xNumEntry.get())
			self.cChanged = True
		if self.varLen == 0: self.varLen = 1 # for empty input
		self.maxi = self.radioMaxi.get()
		
		self.drawSummary()
		self.drawWorkspace()
		self.drawResults()

	def onSetANum(self):
		# even if user presses the set button for constraint size, input for objfun should still work
		self.onSetXBool = True
		if not self.cChanged:
			if self.varLen == int(self.xNumEntry.get()): # extract the value
				self.cChanged = False
			else:
				self.varLen = int(self.xNumEntry.get())
				self.cChanged = True
		if self.varLen == 0: self.varLen = 1 # for empty input
		self.maxi = self.radioMaxi.get()

		self.onSetABool = True
		if self.conLen == int(self.ANumEntry.get()):
			self.AChanged, self.bChanged, self.eqChanged = False, False, False
		else: 
			self.AChanged, self.bChanged, self.eqChanged = True, True, True
			self.conLen = int(self.ANumEntry.get())
		
		self.drawSummary()
		self.drawWorkspace()
		self.drawResults()

	def validateInt(self, action, index, value_if_allowed,
						prior_value, text, validation_type, trigger_type, widget_name):
		'''
		Perform input validation. 
		Allow only an empty value, or a value that can be converted to an int
		'''
		if value_if_allowed.strip() == "":
			return True
		try:
			f = int(value_if_allowed)
			return True
		except ValueError:
			self.bell()
			return False
		return False



class SummaryBox(EditBox):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.maxi = controller.maxi
		self.onSetXBool = controller.onSetXBool
		if self.onSetXBool: 
			self.varLen = controller.varLen
		self.onSetABool = controller.onSetABool
		if self.onSetABool:
			self.conLen = controller.conLen
		self.fig = controller.fig
		self.ax = controller.ax
		self.c = controller.c
		self.A = controller.A
		self.b = controller.b
		self.equality = controller.equality
		self.controller = controller

		self.canvas = FigureCanvasTkAgg(self.fig, self)
		self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
		self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

	def displayProb(self):
		self.ax.clear()
		if self.onSetXBool:
			self.drawMinMax()
			self.drawObjFun()
		if self.onSetABool:
			self.ax.text(0,0.9, "$\\ s.t.$",horizontalalignment='center', fontsize=11)
			self.drawConstraints()
		self.ax.axis('off')

	def drawMinMax(self):
		if self.varLen == 2: variables = "x_1,x_2"
		else: variables = "x_1,...,x_{%d}"%self.varLen
		
		if self.maxi:	
			text = "$\max_{%s}$"%variables
		else:
			text = "$\min_{%s}$"%variables
		self.ax.text(0,1,text,horizontalalignment='center', fontsize=11)

	def drawObjFun(self):
		print(self.controller.cChanged, self.controller.AChanged, self.controller.bChanged, self.controller.eqChanged)
		print(not (self.controller.AChanged
					or self.controller.cChanged
					or self.controller.bChanged
					or self.controller.eqChanged))
		if (self.varLen < 6 and self.c != [] and not self.controller.cChanged): # c inputted and only 5 variables to show
			if self.almostEqual(self.c[0],1): eq = 'x_{1}'
			elif self.almostEqual(self.c[0],-1): eq = '-x_{1}'
			else: eq = str(self.c[0])+'x_{1}'
			for i in range(1, int(self.varLen)):
				if self.almostEqual(abs(self.c[i]),1): 
						if self.c[i] < 0: eq += '-'+'x_{'+str(i+1) + '}'
						else: eq += '+'+'x_{'+str(i+1) + '}'
				elif self.c[i] < 0: eq += str(self.c[i]) + 'x_{'+str(i+1) + '}'
				elif self.c[i] > 0: eq += '+' + str(self.c[i]) + 'x_{'+str(i+1) + '}'
			eq = '$'+eq+'$'
		else: # cT set but too many variables, or c not set
			eq = '$\sum_{i=1}^{%d}c_ix_i$' %int(self.varLen)
		self.ax.text(0.5,1, eq, horizontalalignment='center', fontsize=11)

	def drawConstraints(self):
		# if number of constraints and variables small enough to display
		# and A, b, equality inputted by user
		if (self.conLen < 10 and self.varLen < 6 and self.A != [] 
					and self.b != [] and self.equality != [] 
					and not self.controller.cChanged 
					and not self.controller.AChanged
					and not self.controller.bChanged
					and not self.controller.eqChanged): 
			for row in range(len(self.A)):
				eq = ''
				print(self.equality)
				if self.equality[row][0]:
					equality = "\leq"
				else: equality = "\geq"		
				if self.almostEqual(self.A[row][0],1): eq = 'x_{1}'
				elif self.almostEqual(self.A[row][0],-1): eq = '-x_{1}'
				elif self.almostEqual(self.A[row][0],0): eq = ''
				else: eq = str(self.A[row][0])+'x_{1}'
				for i in range(1, int(self.varLen)):
					if self.almostEqual(abs(self.A[row][i]),1): 
						if self.A[row][i] < 0: eq += '-'+'x_{'+str(i+1) + '}'
						elif eq == '': eq += 'x_{'+str(i+1) + '}'
						else: eq += '+'+'x_{'+str(i+1) + '}'
					elif self.almostEqual(self.A[row][i], 0): continue
					elif self.A[row][i] < 0  or eq == '': eq += str(self.A[row][i]) + 'x_{'+str(i+1) + '}'
					elif self.A[row][i] > 0: eq += '+'+str(self.A[row][i])+'x_{'+str(i+1)+'}'
				eq = '$' + eq + equality + str(self.b[row][0]) + '$'
				self.ax.text(0.5,0.9-0.05*(row), eq, horizontalalignment='center', fontsize=11)
			self.ax.text(0.5,0.9-0.05*(row+1), '$x_i\geq0 \ \ \ \  \\forall{i}$', 
							horizontalalignment='center', fontsize=11)
		else:
			eq = '\sum_{i=1}^{%d}A_{i,j}x_i' %int(self.varLen)
			if self.maxi: equality = " \leq"
			else: equality = " \geq"
			eq = '$' + eq + equality + ' b_j \ \ \ \  \\forall{j}$'

			self.ax.text(0.5,0.9, eq, horizontalalignment='center', fontsize=11)
			self.ax.text(0.5,0.8, '$x_i\geq0 \ \ \ \   \\forall{i}$', 
							horizontalalignment='center', fontsize=11)

	# code taken from 15-112 notes from S17 semester
	def almostEqual(self,d1, d2, epsilon=10**-7):
		return abs(d2 - d1) < epsilon

class ResultBox(EditBox):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller=controller
		self.fig = controller.figResult
		self.ax = controller.axResult
		self.x = controller.x
		self.z = controller.z

		self.canvas = FigureCanvasTkAgg(self.fig, self)
		self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
		self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

	def displayResults(self):
		self.ax.clear()
		if self.x != None and self.z != None:
			if not (self.controller.cChanged or self.controller.AChanged 
					or self.controller.bChanged or self.controller.eqChanged):
				zResult = "Optimal Solution = " + str(round(self.z,3))
				self.ax.text(0.5,1, zResult,horizontalalignment='center', fontsize=11)
				for i in range(len(self.x)):
					xResult = "$x_%d = $"%(i+1) + str(round(self.x[i],3)) #round to the nearest 3rd digit
					self.ax.text(0.5,0.9-i*0.05, xResult,horizontalalignment='center', fontsize=11)
			else: self.x, self.z = None, None
		self.ax.axis('off')


class Workspace(EditBox):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)

		self.varLen = controller.varLen
		self.conLen = controller.conLen
		self.onSetXBool = controller.onSetXBool
		self.mainF2 = controller.mainF2
		self.workNotebook = None
		self.controller = controller

		self.drawWorkFrms()


	def drawWorkFrms(self):
		self.workNotebook = ttk.Notebook(self.mainF2)
		self.workF1 = ttk.Frame(self.workNotebook)   # first page; objective function table
		self.workF2 = ttk.Frame(self.workNotebook)   # second page; constraints functions table
		# container = ttk.Frame(self.workNotebook)
		# container.pack(fill=BOTH, expand=True)
		# self.workNotebook.add(container, text='Mode A')

		# canvasF1 = tk.Canvas(self.workF1)
		# canvasF2 = tk.Canvas(self.workF2)
		# scrollF1X = ttk.Scrollbar(self.workF1, command=canvasF1.xview)
		# scrollF2Y = ttk.Scrollbar(self.workF2, command=canvasF2.yview)
		# scrollF2X = ttk.Scrollbar(self.workF2, command=canvasF2.xview)
		# canvasF1.config(xscrollcommand=scrollF1X.set, scrollregion=(0,0,100,1000))
		# canvasF2.config(xscrollcommand=scrollF2X.set, scrollregion=(0,0,100,1000))
		# canvasF2.config(yscrollcommand=scrollF2Y.set, scrollregion=(0,0,100,1000))
		# canvasF1.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
		# canvasF2.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
		# scrollF1X.pack(side=tk.BOTTOM, fill=tk.X)
		# scrollF2Y.pack(side=tk.RIGHT, fill=tk.Y)
		# scrollF2X.pack(side=tk.BOTTOM, fill=tk.X)


		# scroll = ttk.Scrollbar(container, command=canvas.yview)
		# canvas.config(yscrollcommand=scroll.set, scrollregion=(0,0,100,1000))
		# canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		# scroll.pack(side=RIGHT, fill=Y)
		
		self.workABWindow = ttk.Panedwindow(self.workF2, orient="horizontal")
		self.ABleft = tk.LabelFrame(self.workABWindow, text="A")
		self.workABWindow.add(self.ABleft)

		self.ABmid = tk.LabelFrame(self.workABWindow, text=">= (0) or <= (1)")
		self.workABWindow.add(self.ABmid)

		self.ABright = tk.LabelFrame(self.workABWindow, text="b")
		self.workABWindow.add(self.ABright)

		self.objFunTable = ObjFunDataPage(self.workF1, self)
		self.constTable = ConstDataPage(self.ABleft, self)
		self.objFunTable.pack(expand=1, fill="both")
		self.constTable.pack(expand=1, fill="both")
		self.workNotebook.add(self.workF1, text='Objective Function')
		self.workNotebook.add(self.workF2, text='Constraints')
		self.workNotebook.pack()	
		self.workABWindow.pack(side=tk.TOP)


	'''
	Adapted from http://stackoverflow.com/questions/9239514/filedialog-tkinter-and-opening-files
	'''
	def load_fileA(self):
		self.load_file("A")

	def load_fileB(self):
		self.load_file("b")

	def load_fileEq(self):
		self.load_file("eq")

	def load_fileC(self):
		self.load_file("objfun")

	def load_file(self, dataType):
		fileName = tk.filedialog.askopenfilename(filetypes=[("CSV Files",".csv")])						
		if fileName:
			try:
				data = self.csvToMatrix(fileName)
				print(data)
				print(len(data))
				if (dataType == "objfun" 
							and (len(data) == self.varLen or len(data[0]) == self.varLen)):
					print("passed")
					for col in range(self.varLen):
						if len(data) == self.varLen:
							dataToAdd = str(data[col][0])
						elif len(data[0]) == self.varLen:
							dataToAdd = str(data[0][col])
						print(dataToAdd)
						self.table._entry[(0, col)].insert(0, dataToAdd)
				elif dataType == "A" and len(data) == self.conLen and len(data[0]) == self.varLen:
					for row in range(self.conLen):
						for col in range(self.varLen):
							self.tableA._entry[(row,col)].insert(0,str(data[row][col]))
				elif dataType == "b" and (len(data) == self.conLen or len(data[0]) == self.conLen):
					for row in range(self.conLen):
						if len(data) == self.conLen:
							dataToAdd = str(data[row][0])
						elif len(data[0]) == self.conLen: dataToAdd = str(data[0][row])
						self.tableB._entry[(row,0)].insert(0,dataToAdd)
				elif dataType == "eq" and (len(data) == self.conLen or len(data[0]) == self.conLen):
					print("passed")
					for row in range(self.conLen):
						if len(data) == self.conLen:
							print(str(int(data[row][0])))
							dataToAdd = str(int(data[row][0]))
						elif len(data[0]) == self.conLen: 
							print("here 2")
							dataToAdd = str(int(data[0][row]))
						else: print("else case")
						self.tableEquality._entry[(row,0)].insert(0,dataToAdd)


			except:                     # <- naked except is a bad idea
				print("Open Source File", "Failed to read file\n'%s'" % fileName)
			return
	# csv translation
	def csvToMatrix(self, filename):
		with open(filename) as f:
			reader = csv.reader(f, delimiter=',')
			data = []
			for row in reader:
				numrow = []
				for col in row:
					try: numrow.append(float(col))
					except: continue
				if numrow!=[]:data.append(numrow)
		matrix = np.array(data)
		return matrix

class ObjFunDataPage(Workspace):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.varLen = controller.varLen
		self.importButton = tk.Button(parent, text="Import", command=self.load_fileC)
		self.table = SimpleTableInput(parent, 1, int(self.varLen))
		self.submit = tk.Button(parent, text="Submit", command=self.onSubmit)
		

		self.controller = controller
		if self.controller.controller.c != [] and not self.controller.controller.cChanged:
			for col in range(self.table.columns):
				self.table._entry[(0, col)].insert(0, str(self.controller.controller.c[col]))

		
		self.submit.pack(side="bottom")
		self.importButton.pack(side="top")
		self.table.pack(side="top", fill="both", expand=True)
		#self.table.grid(row=0, column =0)
		#self.importButton.grid(row=1, column=0, sticky=tk.W)
		#self.submit.grid(row=1,column=1,sticky=tk.E)
		
		#self.cSubmitted = False
		
	def onSubmit(self):
		#self.cSubmitted = True
		self.c = self.table.get()[0] # it gets a 2D list, so just need it as 1D lst
		self.controller.controller.c = self.c
		self.controller.controller.cChanged = False
		self.controller.controller.drawSummary()
		


class ConstDataPage(Workspace):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.varLen = controller.varLen
		self.conLen = controller.conLen
		self.controller=controller
		self.ABleft = controller.ABleft
		self.ABmid = controller.ABmid
		self.ABright = controller.ABright

		self.importA = tk.Button(self.ABleft, text="Import", command=self.load_fileA)
		self.importB = tk.Button(self.ABright, text="Import", command=self.load_fileB)
		self.importEq = tk.Button(self.ABmid, text="Import", command=self.load_fileEq)
		self.tableA = SimpleTableInput(self.ABleft, int(self.conLen), int(self.varLen))
		self.tableB = SimpleTableInput(self.ABright, int(self.conLen), 1)
		self.tableEquality = BoolTableInput(self.ABmid, int(self.conLen),1)

		if not (self.controller.controller.AChanged 
				or self.controller.controller.bChanged 
				or self.controller.controller.eqChanged
				or self.controller.controller.cChanged): # if A dimension didn't change, redraw the old values
			if self.controller.controller.A != []:
				for row in range(self.tableA.rows):
					for col in range(self.tableA.columns):
						self.tableA._entry[(row, col)].insert(0,str(self.controller.controller.A[row][col]))
			if self.controller.controller.b != []:
				for row in range(self.tableB.rows):
					self.tableB._entry[(row, 0)].insert(0,str(self.controller.controller.b[row][0]))
			if self.controller.controller.equality != []:
				for row in range(self.tableEquality.rows):
					self.tableEquality._entry[(row, 0)].insert(0,str(self.controller.controller.equality[row][0]))


		self.submitA = tk.Button(parent, text="Submit", command=self.onSubmitA)
		self.submitB = tk.Button(self.ABright, text="Submit", command=self.onSubmitB)
		self.submitEquality = tk.Button(self.ABmid, text="Submit", command=self.onSubmitEq)
		self.importA.pack(side="top")
		self.importB.pack(side="top")
		self.importEq.pack(side="top")
		self.tableA.pack(side="top", fill="both", expand=True)
		self.tableB.pack(side="top", fill="both", expand=True)
		self.tableEquality.pack(side="top", fill="both", expand=True)
		self.submitA.pack(side="top")
		self.submitB.pack(side="top")
		self.submitEquality.pack(side="top")
		
	def onSubmitA(self):
		#self.ASubmitted = True
		self.A = self.tableA.get()
		self.controller.controller.A = self.A
		self.controller.controller.AChanged = False
		self.controller.controller.drawSummary()
		

	def onSubmitB(self):
		self.b = self.tableB.get()
		self.controller.controller.b = self.b
		self.controller.controller.bChanged = False
		self.controller.controller.drawSummary()
		

	def onSubmitEq(self):
		self.equality = self.tableEquality.get()
		self.controller.controller.equality = self.equality
		self.controller.controller.eqChanged = False
		self.controller.controller.drawSummary()
		


class PlotGraph(EditBox):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		# if user pressed the solve button

		self.x = controller.x

		self.xLoBound = 0
		self.xHiBound = float('inf')

		self.solved = controller.solved
		if self.solved:
			self.c = controller.c
			self.A = controller.A
			self.b = controller.b
			self.equality = controller.equality
			# plot only if 2D prob
			if len(self.c) == 2: self.eqTranslate()



		self.fig, self.ax = plt.subplots(figsize=(7,7), dpi=100)
		self.finalPlot()

		canvas = FigureCanvasTkAgg(self.fig, self)
		#canvas.show()
		canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
		canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
	'''
	Translate data from this form
	c = [3, 2]
	A = [[1,  2],
		 [1, -1]]
	b = [4, 1]

	x+2y <=4 --> y <= -0.5x + 2
	x-y <= 1 --> y >= x - 1

	to this form
	eqs = [[(-0.5, 2)],[(1, -1)]]
	eqs[0] --> the top curves
	eqs[1] --> bottom curves

	regardless of minimization or maximization problem, translate constraints
	in terms of y to figure out <= or >=
	'''
	def eqTranslate(self):
		topLst = []
		botLst = []
		self.vertLineLst = []
		for row in range(len(self.A)):
			eqLabel = self.eqLabelTranslate(row)
			if self.A[row][1] > 0: #x2 positive
				x1 = self.A[row][0]*-1/self.A[row][1]
				b =	self.b[row][0]/self.A[row][1]
				if self.equality[row][0] == 0: # >=
					botLst.append((x1,b,eqLabel))
				else: # <=
					topLst.append((x1,b, eqLabel))
			elif self.A[row][1] < 0: #x2 negative
				x1 = self.A[row][0]/abs(self.A[row][1])
				b = -self.b[row][0]/abs(self.A[row][1])
				if self.equality[row][0] == 0: # >=
					topLst.append((x1,b,eqLabel))
				else: # <=
					botLst.append((x1,b,eqLabel))

			elif (self.A[row][1] == 0 and self.A[row][0] > 0): # vertical line
				if (self.equality[row][0] == 0 
						and self.xLoBound < (self.b[row][0]/self.A[row][0])):
					self.xLoBound = (self.b[row][0]/self.A[row][0])
				elif self.xHiBound > (self.b[row][0]/self.A[row][0]): 
					self.xHiBound = (self.b[row][0]/self.A[row][0])
				self.vertLineLst.append((self.b[row][0]/self.A[row][0], eqLabel))
			elif self.A[row][1] == 0 and self.A[row][0] < 0: # vertical line
				if (self.equality[row][0] == 1 and self.xHiBound > (self.b[row][0]/self.A[row][0])):
					self.xHiBound = (self.b[row][0]/self.A[row][0])
				elif self.xLoBound < (self.b[row][0]/self.A[row][0]): 
					self.xLoBound = (self.b[row][0]/self.A[row][0])
				self.vertLineLst.append((self.b[row][0]/self.A[row][0], eqLabel))
		return [topLst, botLst]


	def eqLabelTranslate(self, row):
		if self.almostEqual(self.A[row][0],1): eq = 'x_{1}'
		elif self.almostEqual(self.A[row][0],-1): eq = '-x_{1}'
		elif self.almostEqual(self.A[row][0],0): eq = ''
		else: eq = str(self.A[row][0])+'x_{1}'

		if self.almostEqual(abs(self.A[row][1]),1): 
			if self.A[row][1] < 0: eq += '-'+'x_{2}'
			elif eq == '': eq += 'x_{2}'
			else: eq += '+'+'x_{2}'
		elif self.almostEqual(self.A[row][1],0): eq += ''
		elif self.A[row][1] < 0: eq += str(self.A[row][1]) + 'x_{2}'
		else: eq += '+' + str(self.A[row][1]) + 'x_{2}'

		if self.equality[row][0] == 0: # >=
			equality = '\geq '
		else: equality = '\leq '
		eqLabel = '$' + eq + equality + str(self.b[row][0]) +'$'

		return eqLabel

	# graphical representation
	def finalPlot(self):
		# create the plot object
		if self.solved and len(self.c) == 2:
			#eqLst = [[(4,-2),(-0.3,7)],[(0.5,2)]]
			eqLst = self.eqTranslate()
			print(eqLst)
			'''
			made them into lambda functions for future flexibility;
			like zoom in and out of standard view so xVals can change
			'''
			topEqs = []
			botEqs = []
			# top line
			for i in range(len(eqLst[0])):
				topEqs.append(lambda x, z=i: eqLst[0][z][0]*x + eqLst[0][z][1])
			# bottom line
			for i in range(len(eqLst[1])):
				botEqs.append(lambda x, z=i: eqLst[1][z][0]*x + eqLst[1][z][1])

			x = Symbol('x')
			# find all roots between different functions to estimate the default upperbound
			xLst, yLst = [], []
			eqs = topEqs + botEqs
			for combo in combinations(list(range(len(eqs))),2):
				xRoot = solve(eqs[combo[0]](x) - eqs[combo[1]](x))
				if len(xRoot)==1:
					yRoot = eqs[combo[0]](xRoot[0]) 
					#plt.plot(xRoot,yRoot,'go',markersize=10)
					xLst.append(xRoot[0])
					yLst.append(yRoot)

			# 25% more than maximum intercept amongst all combinations of functions
			# to have better viewability
			upBound = max(int(max(self.x)*1.25),int(max(xLst+yLst)*1.25))
			loBound = 0

			# initialize x values; xVals is an array
			xVals = np.linspace(loBound,upBound,100)

			# draw contour plot of obj fun
			yVals = xVals
			X, Y = np.meshgrid(xVals, yVals)
			Z = self.c[0]*X + self.c[1]*Y
			CS = self.ax.contour(X, Y, Z, linestyles='--', colors='#525252')
			self.ax.clabel(CS, inline=1, fontsize=10)

			for verLine in self.vertLineLst:
				plt.plot([verLine[0]]*len(xVals), xVals, label=verLine[1])

			# matrix of y values for every top and bottom equations
			if len(topEqs) > 0: 
				topLines = [topEqs[0](xVals)]
				plt.plot(xVals, topLines[0], label=eqLst[0][0][2])
				# plot top functions
				for i in range(1,len(topEqs)):
					yVals = np.array([topEqs[i](xVals)])
					topLines = np.append(topLines, yVals, axis=0)
					plt.plot(xVals, yVals[0], label=eqLst[0][i][2])
				# find all y1 points that's greather than 0
				topY = np.append(topLines, [[upBound]*len(xVals)],axis=0)
				# find minimum points of top curves
				top = np.amin(topY, axis=0)
			else: top = np.array([upBound]*len(xVals))

			if len(botEqs) > 0: 
				botLines = [botEqs[0](xVals)]
				plt.plot(xVals, botLines[0], label=eqLst[1][0][2])
				# plot bottom functions
				for i in range(1, len(botEqs)):
					yVals = botEqs[i](xVals)
					botLines = np.append(botLines, [yVals], axis=0)
					plt.plot(xVals, yVals, label=eqLst[1][i][2])	
				print(len(botLines),len([[loBound]*len(xVals)]))
				botY = np.append(botLines, [[loBound]*len(xVals)],axis=0)
				# find maximum points of bottom curves
				bottom = np.amax(botY, axis=0)
			else: bottom = np.array([loBound]*len(xVals))

			# fill in feasible area
			plt.fill_between(xVals, bottom, top, where=(xVals>self.xLoBound) & (top>bottom) & 
														(xVals<self.xHiBound),
														interpolate=True, color='#A8A8A8', alpha=0.5)

			plt.xlim(loBound,upBound) #same limit as linspace parameters, but int() not float()
			plt.ylim(loBound,upBound) 
			# formatting
			plt.xlabel('$x_1$', fontsize=12)
			plt.ylabel('$x_2$', fontsize=12)
			#self.eqLabels=self.eqLabelTranslate()
			self.ax.legend(fontsize=12)
		#plt.show()
		elif self.solved: 
			self.ax.text(0.5, 0.5, "Can't visualize a problem involving less or more than two variables", 
							horizontalalignment='center', fontsize=15)
			self.ax.axis('off')
		else: 
			self.ax.text(0.5, 0.5, "Please input the problem", 
							horizontalalignment='center', fontsize=18)
			self.ax.axis('off')

	# code taken from 15-112 notes from S17 semester
	def almostEqual(self,d1, d2, epsilon=10**-7):
		return abs(d2 - d1) < epsilon


'''
class taken from
http://stackoverflow.com/questions/18985260/
		python-guiinput-and-output-matrices/18986884#18986884
the code was changed slightly to adapt in the context of this project
'''
class SimpleTableInput(tk.Frame):
	def __init__(self, parent, rows, columns):
		tk.Frame.__init__(self, parent)

		self._entry = {}
		self.rows = rows
		self.columns = columns

		# register a command to use for validation
		vcmd = (self.register(self._validate),'%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

		# create the table of widgets
		for row in range(self.rows):
			for column in range(self.columns):
				index = (row, column)
				e = tk.Entry(self, validate="key", validatecommand=vcmd)
				e.grid(row=row, column=column, stick="nsew")
				self._entry[index] = e
		# adjust column weights so they all expand equally
		for column in range(self.columns):
			self.grid_columnconfigure(column, weight=1)
		# designate a final, empty row to fill up any extra space
		self.grid_rowconfigure(rows, weight=1)

	def get(self):
		'''Return a list of lists, containing the data in the table'''
		result = []
		for row in range(self.rows):
			current_row = []
			for column in range(self.columns):
				index = (row, column)
				num = self._entry[index].get()
				try: current_row.append(float(num))
				except: current_row.append(0)
			result.append(current_row)
		return result

	def _validate(self, action, index, value_if_allowed,
						prior_value, text, validation_type, trigger_type, widget_name):
		'''
		Perform input validation. 
		Allow only an empty value, or a value that can be converted to a float
		'''
		if value_if_allowed.strip() == "": return True
		# action=1 -> insert
		if(action == '1'):
			try:
				float(text)
				return True
			except :
				if text in '0123456789.-+':
					if (value_if_allowed in ".-+"):
						return True
					try:
						float(value_if_allowed)
						return True
					except ValueError:
						#self.bell()
						return False
				else:
					return False
		else:
			return True	


# Creates table that accepts only 0 or 1
class BoolTableInput(tk.Frame):
	def __init__(self, parent, rows, columns):
		tk.Frame.__init__(self, parent)

		self._entry = {}
		self.rows = rows
		self.columns = columns

		# register a command to use for validation
		vcmd = (self.register(self._validate),'%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

		# create the table of widgets
		for row in range(self.rows):
			for column in range(self.columns):
				index = (row, column)
				e = tk.Entry(self, validate="key", validatecommand=vcmd)
				e.grid(row=row, column=column, stick="nsew")
				self._entry[index] = e
		# adjust column weights so they all expand equally
		for column in range(self.columns):
			self.grid_columnconfigure(column, weight=1)
		# designate a final, empty row to fill up any extra space
		self.grid_rowconfigure(rows, weight=1)

	def get(self):
		'''Return a list of lists, containing the data in the table'''
		result = []
		for row in range(self.rows):
			current_row = []
			for column in range(self.columns):
				index = (row, column)
				num = self._entry[index].get()
				try: current_row.append(float(num))
				except: current_row.append(0)
			result.append(current_row)
		return result

	def _validate(self, action, index, value_if_allowed,
						prior_value, text, validation_type, trigger_type, widget_name):
		'''
		Perform input validation. 
		Allow only an empty value, or a value that can be converted to a 0 or 1
		'''
		if value_if_allowed.strip() == "":
			return True
		if text in "01" and len(value_if_allowed) == 1:
			try:
				f = int(value_if_allowed)
				return True
			except ValueError:
				self.bell()
				return False
		return False	
		
root = tk.Tk()
app = SolverGUI(root)
root.mainloop()

def csvToMatrix(filename):
		with open(filename) as f:
			reader = csv.reader(f, delimiter=',')
			data = []
			for row in reader:
				numrow = []
				for col in row:
					try: numrow.append(float(col))
					except: continue
				if numrow!=[]:data.append(numrow)
		matrix = np.array(data)
		return matrix
