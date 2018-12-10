from simplex import Simplex

def testSimplex():
	print("Testing simplex...", end="")
	
	print()
	testf1()
	testf2()
	testf3()
	testf4()
	testf5()
	
	print("passed!")

def testf1():
	print("Testing f1...")
	'''
	max Z = 3x + 2y (objective function)
	s.t.
		x + 2y <= 4
		x - y <= 1
		x,y >= 0
	'''	
	c = [3, 2]
	A = [[1,  2],
		 [1, -1]]
	b = [4, 1]
	maxi = True
	f1 = Simplex(c, A, b, maxi)
	x1, z1 = f1.simplex()
	assert(x1 == [2,1] and z1 == 8)

def testf2():
	print("Testing f2...")
	'''
	min Z = 3x + 2y (objective function)
	s.t.
		x + 2y <= 4
		x - y <= 1
		x,y >= 0
	'''	
	c = [3, 2]
	A = [[-1,  -2],
		 [-1, 1]]
	b = [-4, -1]
	maxi = False
	f2 = Simplex(c, A, b, maxi)
	x2, z2 = f2.simplex()
	assert(x2 == [0,0] and z2 == 0)

def testf3():
	print("Testing f3...")
	'''
	max Z = 30x + 20y (objective function)
	s.t.
		2x + 1y <= 1000
		2x + 3y <= 800
		1x + 0y <= 350
		X => 0
		Y => 0
	'''
	c = [30, 20]
	A = [[2, 1],
		 [1, 1],
		 [1, 0]]
	b = [1000, 800, 350]
	maxi = True
	f3 = Simplex(c, A, b, maxi)
	x3, z3 = f3.simplex()
	assert(x3 == [200,600] and z3 == 18000)	

def testf4():
	print("Testing f4...")
	'''
	min Z = 200x + 50y (objective function)
	s.t.
		6x + 3y => 60
		2x + 3y => 36
		x => 0
		y => 0
	(make sure to translate from constraints for <= to >= for minimization prob)
	'''
	c = [200, 50]
	A = [[6, 3],
		 [2,3]]
	b = [60, 36]
	maxi = False
	f4 = Simplex(c, A, b, maxi)
	x4, z4 = f4.simplex()
	assert(almostEqual(x4[0], 0) and 
			almostEqual(x4[1],20) and 
			almostEqual(z4, 1000))		

def testf5():
	print("Testing f5...")
	'''
	min 180x + 160y
	s.t.
    	6x + y >= 12
    	3x + y >= 8
    	4x + 6y >= 24
    	x <= 5
    	y <= 5
    	x,y >= 0
	'''
	c = [180, 160]
	A = [[6, 1],
		 [3, 1],
		 [4, 6],
		 [-1, 0],
		 [-1, 0]]
	b = [12, 8, 24, -5, -5]
	maxi = False
	f = Simplex(c, A, b, maxi)
	x, z = f.simplex()
	assert(almostEqual(x[0], 12/7) and 
			almostEqual(x[1],20/7) and 
			almostEqual(z, 180*(12/7) + 160*(20/7)))

def testf6():
	print("Testing f6...")
	'''
	max:     z = x1 + x2

    s.t.:    x1 + 2x2 ≤  8        
            3x1 + 2x2 ≤ 12
             x1 + 3x2 ≥ 13
    infeasible solution
	'''
	c = [1, 1]
	A = [[1, 2],[3, 2],[-1, -3]]
	b = [8,12,-13]
	maxi = True
	f = Simplex(c,A,b,maxi)
	x, z = f.simplex()
	assert(almostEqual(x[0], ) and 
			almostEqual(x[1],) and
			almostEqual(z, ))

def almostEqual(d1, d2, epsilon=10**-7):
    # note: use math.isclose() outside 15-112 with Python version 3.5 or later
    return (abs(d2 - d1) < epsilon)

testSimplex()