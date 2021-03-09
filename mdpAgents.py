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

#
# A class that creates a grid that can be used as a map
#
# The map itself is implemented as a nested list, and the interface
# allows it to be accessed by specifying x, y locations.
# Taked from keats week 5
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
        # Holds utilities
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

    # Returns the max width of the map
    def getGridWidth(self, state):
        xValues = []
        for i in range(len(api.corners(state))):
            xValues.append(api.corners(state)[i][0])
        return max(xValues) + 1

    # Returns the max height of the map
    def getGridHeight(self, state):
        yValues = []
        for i in range(len(api.corners(state))):
            yValues.append(api.corners(state)[i][1])
        return max(yValues) +1

    # Adds all walls to a dictionary with the coordinates stored as keys assigning them the value W
    def addGridDict(self, state):
        walls = api.walls(state)
        wallDict = {}
        for i in range(len(walls)):
            wallDict.update({walls[i]:"W"})
        return wallDict

    # Adds all the ghosts to a dictionary assigning them a value
    def assignGhostValue(self, state):
        ghost = api.ghosts(state)
        ghostDict = {}
        for i in range(len(ghost)):
            ghostDict.update({ghost[i]:-1.5})
        return ghostDict

    # Adds all the food to a dictionary assigning them a value
    def assignFoodValue(self, state):
        food = api.food(state)
        foodDict = {}
        for i in range(len(food)):
            foodDict.update({food[i]:0.1})
        return foodDict

    # Creates a dictionary which stores all the capsules on the map while assinging values to them
    def assignCapsuleValue(self, state):
        capsule = api.capsules(state)
        capsuleDict= {}
        for i in range(len(capsule)):
            capsuleDict.update({capsule[i]:0.4})
        return capsuleDict

    # This method returns all the space on the map which is empty, as in there is no food, capsule, or ghost on it, and
    # then assigns it a value. It first returns a list of coordinates which does not have the walls which is then used
    # to check if it is free of other items
    def assignSpaceValue(self, state):
        freeSpace= []
        for x in range(self.getGridWidth(state)):
            for y in range(self.getGridHeight(state)):
                freeSpace.append((x,y))
        for value in self.addGridDict(state):
            freeSpace.remove(value)
        # Returns all coordinates which does not have a wall
        moveableBlocks= {}
        for i in range(len(freeSpace)):
            # Checks whether a space does is not in any other dictionary, if it isnt it assigns a value to it
            if freeSpace[i] not in self.foodDict and freeSpace[i] not in self.capsuleDict and freeSpace[i] not in self.ghostDict:
                moveableBlocks.update({freeSpace[i]:-0.05})
        return moveableBlocks

    # A dictionary which stores all other initialised dictionaries with their values.
    def map(self, state):
        pacloc = api.whereAmI(state)
        walls = api.walls(state)
        ghost = api.ghosts(state)
        food = api.food(state)
        capsule = api.capsules(state)
        visitedStates = []

        # Adds other dictionaries and their values to this one
        map = {}
        # Assigns every empty space intially as 0 before other dictionries are added
        map.update(self.assignSpaceValue(state))
        map.update(self.assignFoodValue(state))
        map.update(self.assignGhostValue(state))
        map.update(self.addGridDict(state))
        map.update(self.assignCapsuleValue(state))

        # Checks to see whether pacman has visited a location, if it has then it is added to this list
        if pacloc not in self.visitedStates:
           self.visitedStates.append(pacloc)

        # Checks whether pacman has eaten a piece of food by comparing the coordinates in the list
        # with the coordinates in the food dictionary, if it had then it updates the value
        for i in self.visitedStates:
            if i in self.foodDict:
                map[i] = 0

        # Same as the previous one, just checks for capsules
        for i in self.visitedStates:
            if i in self.capsuleDict:
                map[i] = 0


        return map

    # Calculates the maximum expected utility of a coordinate on the map
    # this is then later passed into the value iteration
    def calcUtility(self, xAxis, yAxis, state, vMap):
        self.vMap = vMap

        # Checks whether a given direction is a wall, if it isn't it stores the position in a variable
        # Else it stores the current state pacman is in
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

        # mutiplies the utilities of positions depending on whether there is a wall or not and
        # stores it in the dictionary
        self.util["north_util"] = ((0.8 * northCoord) + (0.1 * westCoord) + (0.1 * eastCoord))
        self.util["east_util"]  = ((0.8 * eastCoord) + (0.1 * northCoord) + (0.1 * southCoord))
        self.util["south_util"] = ((0.8 * southCoord) + (0.1 * westCoord) + (0.1 * eastCoord))
        self.util["west_util"] = ((0.8 * westCoord) + (0.1 * northCoord) + (0.1 * southCoord))

        self.vMap[xAxis, yAxis] = max(self.util.values())
        # returns a map with the transtion values
        return self.vMap[xAxis, yAxis]

    # Returns a list of coordinates which is surrounding the ghost at a given point
    def avoidGhost(self, state):
        ghostRange = 2
        death = []
        ghost = api.ghosts(state)
        for x in range(ghostRange):
            for y in range(len(ghost)):
                # Creates variables which access the ghosts x and y position, then used to appened
                # all possible coordinates in a range of 2 from that position to a list
                ghostX = ghost[y][0]
                ghostY = ghost[y][1]
                death.append((int(ghostX + x), int(ghostY)))
                death.append((int(ghostX - x), int(ghostY)))
                death.append((int(ghostX), int(ghostY + 1)))
                death.append((int(ghostX), int(ghostY - 1)))

        return death

    # this does value iteration for both maps with different variations of the formulas depending on the size of the map
    # gamma is the discount function and vMap and is the map
    def valueIteration(self, gamma, vMap, state):
        foodLocation = self.assignFoodValue(state)
        capsuleLocation = self.assignCapsuleValue(state)
        ghostLocation = self.assignGhostValue(state)
        walls = self.addGridDict(state)
        width = self.getGridWidth(state) -1
        height = self.getGridHeight(state) -1
        ghost = self.avoidGhost(state)
        # Sets the reward as the current state it is in
        initReward = vMap.copy()
        # Checks whether the map is medium or small, depending on that it can run a different value iteration
        if width >= 10 and height>= 10:
            #medium grid
            loop = 25
            while loop > 0:
                # Stores old values
                temp = vMap.copy()
                for x in range(width):
                    for y in range(height):
                        if (x,y) not in walls and (x,y) not in ghostLocation and (x,y) not in capsuleLocation:
                            # Checks whether pacman is currently in the surrounding coordinates of the ghost
                            # depending on the result will change the reward value
                            if (x,y) not in ghost:
                                vMap[(x,y)] = initReward[(x, y)] + gamma * self.calcUtility(x, y, state, temp)
                            else:
                                vMap[(x,y)] = -2 + gamma * self.calcUtility(x, y, state, temp)

                loop -= 1
        else:
            #small grid
            # Food is excluded for the small grid as it is a terminal state
            loop = 20
            while loop > 0:
                temp = vMap.copy()
                for x in range(width):
                    for y in range(height):
                        if (x,y) not in walls and (x,y) not in ghostLocation and (x,y) not in foodLocation and (x,y) not in capsuleLocation:
                            # Checks whether pacman is currently in the surrounding coordinates of the ghost
                            # depending on the result will change the reward value
                            if (x,y) not in ghost:
                                vMap[(x,y)] = initReward[(x, y)] + gamma * self.calcUtility(x, y, state, temp)
                            else:
                                vMap[(x,y)] = -2 + gamma * self.calcUtility(x, y, state, temp)

                loop -= 1

    # Calculates the movement policy for pacmans locations at a given state
    # using the value iteration map
    def getPolicy(self, state, itrMap):
        self.vMap = itrMap
        pacloc = api.whereAmI(state)
        xAxis = pacloc[0]
        yAxis = pacloc[1]

        # Checks whether going a direction from pacmans current location will lead to a wall
        # else it'll return pacmans current position
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

        # calculates the utilities for each possible move and stores them in the dictionary
        self.util["north_util"] = ((0.8 * northCoord) + (0.1 * westCoord) + (0.1 * eastCoord))
        self.util["east_util"]  = ((0.8 * eastCoord) + (0.1 * northCoord) + (0.1 * southCoord))
        self.util["south_util"] = ((0.8 * southCoord) + (0.1 * westCoord) + (0.1 * eastCoord))
        self.util["west_util"] = ((0.8 * westCoord) + (0.1 * northCoord) + (0.1 * southCoord))

        # retieves the maximum utility
        maxU = max(self.util.values())
        # returns the move with the highest utility
        return  self.util.keys()[self.util.values().index(maxU)]






    def getAction(self, state):

            legal = api.legalActions(state)
            vMap = self.map(state)
            # Calls value iteration with the given gamma value
            self.valueIteration(0.72, vMap, state)

            # Calls get policy to return the next best move, if it is legal then move is carried out
            if self.getPolicy(state, vMap) == "north_util":
                return api.makeMove('North', legal)
            elif self.getPolicy(state, vMap) == "south_util":
		              return api.makeMove('South', legal)
            elif self.getPolicy(state, vMap) == "east_util":
	               return api.makeMove('East', legal)
            elif self.getPolicy(state, vMap) == "west_util":
                return api.makeMove('West', legal)
