#!/usr/bin/env python
# Copyright 2009 Chase Johnson
# Licensable under WTFPL v2
"""
Everyone is permitted to copy and distribute verbatim or modified
copies of this license document, and changing it is allowed as long
as the name is changed.

           DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
  TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

 0. You just DO WHAT THE FUCK YOU WANT TO.
"""
try:
	import Image
except ImportError:
	print "You need to install the Python Imaging Library to run this script."
	exit()

from math import floor
from sys import setrecursionlimit, maxint
from optparse import OptionParser

setrecursionlimit(maxint)

class MazeSolve(object):
	def __init__(self):
		#initialize state
		self.outCount = 0
		self.cleaningUp = False
		self.Up, self.Down, self.Left, self.Right = range(4)
		
		#options
		self.cleanupFramePeriod = 1
		parser = OptionParser(usage="amazer.py [options] mazefile.png")
		parser.add_option("-v","--verbose", default=False, action="store_true", dest="verbose", help="Verbose output. Default is silent. Verbose slows down operation dramatically.")
		parser.add_option("-l","--out-limit", default=maxint, action="store", dest="outLimit", help="Maximum number of recursive calls to take. Limiting this may cause no solution to be found. The default is sys.maxint, " + str(maxint) + ".")
		parser.add_option("-f","--frame-period", default=1000, action="store", dest="frameperiod", help="How many moves to skip between rendering an output frame. Low values will cause the solver to take longer. 1000 is the default.")
		parser.add_option("-c", "--continue-after", default=False, action="store_true", dest="continueAfter", help="Continue evaluating paths after a solution is found.")
		(options, args) = parser.parse_args()
		self.verbose = options.verbose
		self.outLimit = options.outLimit
		self.frameperiod = int(options.frameperiod)
		if self.frameperiod == 0:
			self.frameperiod = maxint
		self.continueAfter = options.continueAfter
		if len(args) > 0:
			maze_path = args[0]
		else:
			parser.print_help()
			exit()
		
		self.process(maze_path)
		
	def process(self, name):
		im = Image.open(name)
		if im.mode != "RGB":
			if self.verbose: print "Converting to RGB from " + im.mode
			im = im.convert("RGB")
			
		data = im.getdata()
		j = 0
		col = 0
		row = 0
		whitePixelsRight = []
		whitePixelsLeft = []
		whitePixelsUp = []
		whitePixelsDown = []
		pix = im.load()
		for i, pixel in enumerate(data):
			col = col+1
			if col > im.size[0]:
				col = 1
				row = row + 1
			j = im.size[0]*row+col
			if self.isGreen(pixel):
				if self.isWhite(pix[col-2,row]):
					whitePixelsLeft.append((col-2,row))
				if self.isWhite(pix[col-1, row-1]):
					whitePixelsUp.append((col-1,row-1))
				if self.isWhite(pix[col, row]):
					whitePixelsRight.append((col,row))
				if self.isWhite(pix[col-1, row+1]):
					whitePixelsDown.append((col-1,row+1))

		leftFronts = self.collect_fronts(whitePixelsLeft)
		rightFronts = self.collect_fronts(whitePixelsRight)
		upFronts = self.collect_fronts(whitePixelsUp)
		downFronts = self.collect_fronts(whitePixelsDown)

		if self.verbose: print "Number of wavefronts found: ", str(len(rightFronts) + len(leftFronts) + len(upFronts) + len(downFronts))
		if(self.move_wavefront(im, pix, rightFronts[0], self.Right)):
			print "Found exit"
		im.save("solved_maze.png")

	def move_wavefront(self, im, pix, startFront, direction):
		self.outCount = self.outCount + 1
		if self.verbose: print "------------------- OUTPUT FRAME #" + str(self.outCount) + "-------------------"
		if self.outCount > self.outLimit:
			return False
		if self.cleaningUp and not self.continueAfter:
			return False
	
		xMotion = 0
		yMotion = 0
		if direction == self.Right: xMotion = 1
		elif direction == self.Down: yMotion = 1
		elif direction == self.Up: yMotion = -1
		elif direction == self.Left:	xMotion = -1
		
		whitePixelsRight = []
		whitePixelsLeft = []
		whitePixelsUp = []
		whitePixelsDown = []
		
		front = list(startFront)
		if self.verbose: print "Starting traversal"
		while not self.front_contains_wall(im, pix, front):
			if self.verbose: print "no wall still at " + str(front)
			tempFront = []
			for pixel in front:
				pix[pixel[0],pixel[1]] = (0,255,0)
				tempFront.append((pixel[0]+xMotion, pixel[1]+yMotion))
			front = tempFront
		
		foundRed = False	
		#start over and check for fronts
		front = list(startFront)
		if self.verbose: print "Detecting wavefronts"
		while not self.front_contains_wall(im, pix, front):
			if self.verbose: print "no wall still at " + str(front)
			tempFront = []
			for pixel in front:
				tempFront.append((pixel[0]+xMotion, pixel[1]+yMotion))
				if self.isGreen(pix[pixel[0],pixel[1]]):
					col = pixel[0]
					row = pixel[1]
					if self.isWhite(pix[col-1,row]):
						whitePixelsLeft.append((col-1,row))
						if self.verbose: print "Found white pixel Left at " + str((col-1,row))
					if self.isWhite(pix[col, row-1]):
						whitePixelsUp.append((col,row-1))
						if self.verbose: print "Found white pixel Up at " + str((col,row-1))
					if self.isWhite(pix[col+1, row]):
						whitePixelsRight.append((col+1,row))
						if self.verbose: print "Found white pixel Up at " + str((col+1,row))
					if self.isWhite(pix[col, row+1]):
						whitePixelsDown.append((col,row+1))
						if self.verbose: print "Found white pixel Up at " + str((col,row+1))
					if self.isRed(pix[col-1,row]):
						foundRed = True
						if self.verbose: print "Found red pixel Left at " + str((col-1,row))
					if self.isRed(pix[col, row-1]):
						foundRed = True
						if self.verbose: print "Found red pixel Up at " + str((col,row-1))
					if self.isRed(pix[col+1, row]):
						foundRed = True
						if self.verbose: print "Found red pixel Up at " + str((col+1,row))
					if self.isRed(pix[col, row+1]):
						foundRed = True
						if self.verbose: print "Found red pixel Up at " + str((col,row+1))	
			front = tempFront
		
		leftFronts = self.collect_fronts(whitePixelsLeft)
		rightFronts = self.collect_fronts(whitePixelsRight)
		upFronts = self.collect_fronts(whitePixelsUp)
		downFronts = self.collect_fronts(whitePixelsDown)

		numWaves = len(rightFronts) + len(leftFronts) + len(upFronts) + len(downFronts);
	
		if self.verbose: print "Number of wavefronts found: ", str(numWaves)
		if self.verbose: print "Left side fronts: "+ str(leftFronts)
		if self.verbose: print "Right side fronts: "+ str(rightFronts)
		if self.verbose: print "Up side fronts: "+ str(upFronts)
		if self.verbose: print "Down side fronts: "+ str(downFronts)
	
		trueReturned = False
		if self.outCount % self.frameperiod == 0:
			im.save("output" + str(self.outCount).rjust(5, "0")+".png")
		if self.cleaningUp and (self.outCount % self.cleanupFramePeriod ==0): 
			im.save("output" + str(self.outCount).rjust(5, "0")+".png")
		
		if foundRed:
			if self.verbose: print "========================== MAZE SOLVED =========================="
			self.cleaningUp = True
			return True
		
		for front in leftFronts:
			if self.move_wavefront(im, pix, front, self.Left):
				trueReturned = True
		for front in rightFronts:
			if self.move_wavefront(im, pix, front, self.Right):
				trueReturned = True
		for front in upFronts:
			if self.move_wavefront(im, pix, front, self.Up):
				trueReturned = True
		for front in downFronts:
			if self.move_wavefront(im, pix, front, self.Down):
				trueReturned = True
			
		if not trueReturned:
			if self.verbose: print "Re-coloring for dead path"
			front = list(startFront)
			while not self.front_contains_wall(im, pix, front):
				if self.verbose: print "no wall still at " + str(front)
				tempFront = []
				for pixel in front:
					pix[pixel[0],pixel[1]] = (128,128,128)
					tempFront.append((pixel[0]+xMotion, pixel[1]+yMotion))
				front = tempFront		
	
		if self.verbose: print "Returning " + str(trueReturned)
		return trueReturned

	def front_contains_wall(self, im, pix, front):
		blackDetected = False
		for pixel in front:
			if self.isBlack(pix[pixel[0],pixel[1]]):
				blackDetected = True
				break
		return blackDetected

	def collect_fronts(self, array):
		returnArray = []
		for pixel in array:
			added = False
			# check each array in leftFronts for one that contains an adjacent pixel to pixel
			for front in returnArray:
				for testPixel in front:
					if self.is_adjacent(testPixel, pixel):
						front.append(pixel)
						added = True
						break
			if not added:
				tempArray = [pixel]
				returnArray.append(tempArray)
		return returnArray
	
	def is_adjacent(self, tuple1, tuple2):
		x1, y1 = tuple1
		x2, y2 = tuple2
	
		if x1 == x2 and abs(y1-y2)==1: return True
		elif y1 == y2 and abs(x1-x2)==1: return True
		else: return False
	
	def compare_coordinates(self, tuple1, tuple2):
		x1, y1 = tuple1
		x2, y2 = tuple2
		return cmp(x1, x2) or (y1,y1)
		
	def isWhite(self, tuple):
		R, G, B = tuple
		return R+G+B > 600

	def isBlack(self, tuple):
		R, G, B = tuple
		return R+G+B < 40

	def isGreen(self, tuple):
		R, G, B = tuple
		return G > 0.8*(R+B)

	def isRed(self, tuple):
		R, G, B = tuple
		return R > 0.8*(G+B)

	def isBlue(self, tuple):
		R, G, B = tuple
		return B > 0.8*(R+G)

if __name__ == '__main__':
	MazeSolve()