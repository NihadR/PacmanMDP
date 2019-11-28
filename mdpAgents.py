# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util
from copy import copy

# A class that creates a grid that can be used as a map
#
# The map itself is implemented as a nested list, and the interface
# allows it to be accessed by specifying x, y locations.
#
class Grid:

    # Constructor
    #
    # Note that it creates variables:
    #
    # grid:   an array that has one position for each element in the grid.
    # width:  the width of the grid
    # height: the height of the grid
    #
    # Grid elements are not restricted, so you can place whatever you
    # like at each location. You just have to be careful how you
    # handle the elements when you use them.
    def __init__(self, width, height):
        self.width = width
        self.height = height
        subgrid = []
        for i in range(self.height):
            row=[]
            for j in range(self.width):
                row.append(0)
            subgrid.append(row)

        self.grid = subgrid

    # Print the grid out.
    def display(self):
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[i][j],
            # A new line after each line of the grid
            print
        # A line after the grid
        print

    # The display function prints the grid out upside down. This
    # prints the grid out so that it matches the view we see when we
    # look at Pacman.
    def prettyDisplay(self):
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[self.height - (i + 1)][j],
            # A new line after each line of the grid
            print
        # A line after the grid
        print

    # Set and get the values of specific elements in the grid.
    # Here x and y are indices.
    def setValue(self, x, y, value):
        self.grid[y][x] = value

    def getValue(self, x, y):
        return self.grid[y][x]

    # Return width and height to support functions that manipulate the
    # values stored in the grid.
    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width


class MDPAgent(Agent):

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"
        self.visitedStates = []
        self.foodDict = {}
        self.ghostDict = {}
        self.capsuleDict = {}
        self.wallDict = {}
        self.moveableBlocks= {}
        self.util = {
        "north_util" : 0.0, "east_util" : 0.0, "south_util" : 0.0, "west_util" : 0.0
        }

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
        print "I'm at:"
        print api.whereAmI(state)

    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"


    def getGridWidth(self, state):
        xValues = []
        for i in range(len(api.corners(state))):
            xValues.append(api.corners(state)[i][0])
        return max(xValues) + 1

    def getGridHeight(self, state):
        yValues = []
        for i in range(len(api.corners(state))):
            yValues.append(api.corners(state)[i][1])
        return max(yValues) +1

    def addGridDict(self, state):
        walls = api.walls(state)
        wallDict = {}
        for i in range(len(walls)):
            wallDict.update({walls[i]:"W"})
        return wallDict


    def assignGhostValue(self, state):
        ghost = api.ghosts(state)
        ghostDict = {}
        for i in range(len(ghost)):
            ghostDict.update({ghost[i]:-1.5})
        return ghostDict

    def assignFoodValue(self, state):
        food = api.food(state)
        foodDict = {}
        for i in range(len(food)):
            foodDict.update({food[i]:0.2})
        return foodDict

    def assignCapsuleValue(self, state):
        capsule = api.capsules(state)
        capsuleDict= {}
        for i in range(len(capsule)):
            capsuleDict.update({capsule[i]:0.8})
        return capsuleDict

    def assignSpaceValue(self, state):
        freeSpace= []
        for x in range(self.getGridWidth(state)):
            for y in range(self.getGridHeight(state)):
                freeSpace.append((x,y))
        for value in self.addGridDict(state):
            freeSpace.remove(value)
        moveableBlocks= {}
        for i in range(len(freeSpace)):
            if freeSpace[i] not in self.foodDict and freeSpace[i] not in self.capsuleDict and freeSpace[i] not in self.ghostDict:
                moveableBlocks.update({freeSpace[i]:-0.05})
        return moveableBlocks

    def map(self, state):
        pacloc = api.whereAmI(state)
        walls = api.walls(state)
        ghost = api.ghosts(state)
        food = api.food(state)
        capsule = api.capsules(state)
        visitedStates = []

        map = {}
        map.update(self.assignSpaceValue(state))
        map.update(self.assignFoodValue(state))
        map.update(self.assignGhostValue(state))
        map.update(self.addGridDict(state))
        map.update(self.assignCapsuleValue(state))


        if pacloc not in self.visitedStates:
           self.visitedStates.append(pacloc)

        for i in self.visitedStates:
            if i in self.foodDict:
                map[i] = 0

        for i in self.visitedStates:
            if i in self.capsuleDict:
                map[i] = 0


        return map

    def calcUtility(self, xAxis, yAxis, state, vMap):
        self.vMap = vMap


        if self.vMap[(xAxis, yAxis +1)] != "W":
            northCoord = self.vMap[(xAxis, yAxis +1)]
        else:
            northCoord = self.vMap[(xAxis, yAxis)]

        if self.vMap[(xAxis, yAxis - 1)] != "W":
            southCoord = self.vMap[(xAxis, yAxis-1)]
        else:
            southCoord = self.vMap[(xAxis, yAxis)]

        if self.vMap[(xAxis -1, yAxis)] != 'W':
            westCoord = self.vMap[(xAxis -1, yAxis)]
        else:
            westCoord = self.vMap[(xAxis, yAxis)]

        if self.vMap[(xAxis +1, yAxis)] != "W":
            eastCoord = self.vMap[(xAxis +1, yAxis)]
        else:
            eastCoord = self.vMap[(xAxis, yAxis)]


        self.util["north_util"] = ((0.8 * northCoord) + (0.1 * westCoord) + (0.1 * eastCoord))
        self.util["east_util"]  = ((0.8 * eastCoord) + (0.1 * northCoord) + (0.1 * southCoord))
        self.util["south_util"] = ((0.8 * southCoord) + (0.1 * westCoord) + (0.1 * eastCoord))
        self.util["west_util"] = ((0.8 * westCoord) + (0.1 * northCoord) + (0.1 * southCoord))

        self.vMap[xAxis, yAxis] = max(self.util.values())

        return self.vMap[xAxis, yAxis]

    def avoidGhost(self, state):
        ghostRange = 1
        death = []
        ghost = api.ghosts(state)
        for x in range(ghostRange):
            for y in range(len(ghost)):
                ghostX = ghost[y][0]
                ghostY = ghost[y][1]
                death.append((int(ghostX + x), int(ghostY)))
                death.append((int(ghostX - x), int(ghostY)))
                death.append((int(ghostX), int(ghostY + i)))
                death.append((int(ghostX), int(ghostY - i)))

        return death


    def valueIteration(self, gamma, vMap, state):
        foodLocation = self.assignFoodValue(state)
        capsuleLocation = self.assignCapsuleValue(state)
        ghostLocation = self.assignGhostValue(state)
        walls = self.addGridDict(state)
        width = self.getGridWidth(state) -1
        height = self.getGridHeight(state) -1
        ghost = self.avoidGhost(state)
        initReward = vMap.copy()
        if width >= 10 and height>= 10:
            #medium grid
            loop = 20
            while loop > 0:
                temp = vMap.copy()
                for x in range(width):
                    for y in range(height):
                        if (x,y) not in walls and (x,y) not in ghostLocation and (x,y) not in capsuleLocation:
                            if (x,y) not in ghost:
                                vMap[(x,y)] = initReward[(x, y)] + gamma * self.calcUtility(x, y, state, temp)
                            else:
                                vMap[(x,y)] = initReward[(x, y)] + gamma * self.calcUtility(x, y, state, temp)

                loop -= 1
        else:
            #small grid
            loop = 10
            while loop > 0:
                temp = vMap.copy()
                for x in range(width):
                    for y in range(height):
                        if (x,y) not in walls and (x,y) not in ghostLocation and (x,y) not in foodLocation and (x,y) not in capsuleLocation:
                            if (x,y) not in ghost:
                                vMap[(x,y)] = initReward[(x, y)] + gamma * self.calcUtility(x, y, state, temp)
                            else:
                                vMap[(x,y)] = initReward[(x, y)] + gamma * self.calcUtility(x, y, state, temp)

                loop -= 1

    def getPolicy(self, state, itrMap):
        self.vMap = itrMap
        pacloc = api.whereAmI(state)
        xAxis = pacloc[0]
        yAxis = pacloc[1]

        if self.vMap[(xAxis, yAxis +1)] != "W":
            northCoord = self.vMap[(xAxis, yAxis +1)]
        else:
            northCoord = self.vMap[(xAxis, yAxis)]

        if self.vMap[(xAxis, yAxis - 1)] != "W":
            southCoord = self.vMap[(xAxis, yAxis-1)]
        else:
            southCoord = self.vMap[(xAxis, yAxis)]

        if self.vMap[(xAxis -1, yAxis)] != 'W':
            westCoord = self.vMap[(xAxis -1, yAxis)]
        else:
            westCoord = self.vMap[(xAxis, yAxis)]

        if self.vMap[(xAxis +1, yAxis)] != "W":
            eastCoord = self.vMap[(xAxis +1, yAxis)]
        else:
            eastCoord = self.vMap[(xAxis, yAxis)]

        self.util["north_util"] = ((0.8 * northCoord) + (0.1 * westCoord) + (0.1 * eastCoord))
        self.util["east_util"]  = ((0.8 * eastCoord) + (0.1 * northCoord) + (0.1 * southCoord))
        self.util["south_util"] = ((0.8 * southCoord) + (0.1 * westCoord) + (0.1 * eastCoord))
        self.util["west_util"] = ((0.8 * westCoord) + (0.1 * northCoord) + (0.1 * southCoord))

        maxU = max(self.util.values())
        legal = api.legalActions(state)

        return  self.util.keys()[self.util.values().index(maxU)]





    # For now I just move randomly
    def getAction(self, state):


            #print "map", self.map(state)
            # print "util", self.calcUtility(xAxis, yAxis, state)
            # nextpol = self.getPolicy(state)
            # print nextpol

            # Get the actions we can try, and remove "STOP" if that is one of them.
            legal = api.legalActions(state)
            vMap = self.map(state)
            # print "first", vMap
            # if Directions.STOP in legal:
            #     legal.remove(Directions.STOP)
            # #
            self.valueIteration(0.7, vMap, state)
            # print "second",  vMap
        # Random choice between the legal options.
            # print "val it is ", self.valueIteration(state)
            # print "next move is", self.getPolicy(xAxis, yAxis, state)
            # for i in range(self.getGridWidth(state)):
            #     for j in range(self.getGridHeight(state)):
            #         if self.getValue(i,j) != "W":
            #             self.setValue(i, j, vMap[(i,j)])
                    # if vMap[(i, j)] != "W":
                    #     vMap.update[vMap[(i, j)]]
            # nextMove = self.getPolicy(xAxis, yAxis, state)
            # for i in nextMove:
            # #     if i is legal:
            # print "best move"
            # print self.getPolicy(state, vMap)
            #
            if self.getPolicy(state, vMap) == "north_util":
                return api.makeMove('North', legal)
            elif self.getPolicy(state, vMap) == "south_util":
		              return api.makeMove('South', legal)
            elif self.getPolicy(state, vMap) == "east_util":
	               return api.makeMove('East', legal)
            elif self.getPolicy(state, vMap) == "west_util":
                return api.makeMove('West', legal)

            # return api.makeMove(random.choice(legal), legal)
