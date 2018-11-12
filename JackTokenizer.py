#
#JackTokenizer.py
#
# CS2002   Project 11 Jack Compiler (part 2)
#
# Fall 2017
# last updated 13 DEC 2017
#
# Ryan Sowers


from JTConstants import *

   
############################################
# Class
class JackTokenizer(object):

############################################
# Constructor

    def __init__(self, filePath):
        loadedList = self.__loadFile__(str(filePath))
        
        self.toParse = self.__filterFile__(loadedList)



# ############################################
# instance methods

    def advance(self):
        '''reads and returns the next token, returns None if there are no more tokens.'''

        #self.toParse holds lines of code, there can be multiple tokens per line
        #so strip tokens until a line is empty, then pop it off self.toParse
        #  that means every time advance is called, we are guaranteed to have at
        #  least one token in self.toParse[0], and that will work until
        #  self.toParse itself is empty 

        if self.toParse:

            if self.toParse[0][0].isdigit():
                token = self.__parseInt__(self.toParse[0])
            elif self.toParse[0][0] == '"':
                token = self.__parseString__(self.toParse[0])
            elif self.toParse[0][0] in SYMBOLS:
                token = self.toParse[0][0]
            else:
                token = self.__parseCharacters__(self.toParse[0])

            self.toParse[0] = self.toParse[0][(len(token)):]
            self.toParse[0] = self.toParse[0].strip()

            if not self.toParse[0]:
                self.toParse.pop(0)

            return token
        
        else:
            return None



#############################################
# private




    def __parseInt__(self, line):
        ''' returns an integerConstant off of the start of the line.
            assumes there are no leading spaces
            does not modify the line itself. '''

        symbolFound = False
        for character in line:
            if character in DELIMITERS:         # updated from last project to use DELIMITERS
                indexSymbol = line.find(character)
                symbolFound = True
                return line[:indexSymbol]

        if not symbolFound:
            return line
        			
        
        
    def __parseCharacters__(self, line):
        ''' returns a token off of the start of the line which could be an identifier or a keyword.
            assumes there are no leading spaces
            does not modify the line itself. '''

        symbolFound = False
        commands = line.split(' ')
        for item in commands:
        	for character in item:
        		if character in SYMBOLS:
        			indexSymbol = item.find(character)
        			symbolFound = True
        			return item[:indexSymbol]
        	if not symbolFound:
        		return item



    def __parseString__(self, line):
        ''' returns a stringConstant off of the start of the line, quotes left in place.
            assumes there are no leading spaces and that the leading double quote has not been stripped.
            does not modify the line itself. '''

        commands = line.split('"')
        if commands[0] == '':
            return('"' + commands[1] + '"')






    ############   file loading stuff below   ############   

    def __loadFile__(self, fileName):
        '''Loads the file into memory.

           -fileName is a String representation of a file name,
           returns contents as a simple List'''
        
        fileList = []
        file = open(fileName,"r")
        
        for line in file:
            fileList.append(line)
            
        file.close()
        
        return fileList



    def __filterFile__(self, fileList):
        '''Comments, blank lines and unnecessary leading/trailing whitespace are removed from the list.

           -fileList is a List representation of a file, one line per element
           returns the fully filtered List'''

        #start with your project 8 __filterFile__
        #handle single line block comments much like you did EOL comments
        #multi-line block coments are the only things on their lines, **different than single line block comments**

        filteredList = []

        for line in fileList:
            line = line.strip()
            line = self.__filterOutEOLComments__(line)
            line = self.__filterOutSingleLineBlockComments__(line)
            indexAPI = line.find('/**')
            indexEnd = line.find('*/')
            indexAPInewL = line.find('*')
            if (indexAPI >= 0):
            	line = line[:indexAPI]
            	line.strip()
            if (indexEnd >= 0):
            	line = line[indexEnd+2:]
            	line.strip()
            if (indexAPInewL == 0):
                line = line[:indexAPInewL]
                line.strip()

            if len(line) > 0:
            	filteredList.append(line)

        return filteredList




    def __filterOutEOLComments__(self, line):
        '''Removes end-of-line comments and and resulting whitespace.

           -line is a string representing single line, line endings already stripped
           returns the filtered line, which may be empty '''

        index = line.find('//')
        if index >= 0:
            line = line[0:index]

        line = line.strip()

        return line    



    def __filterOutSingleLineBlockComments__(self, line):
        '''Removes single line block comments and resulting whitespace.
           There may be valid code following a single line block comment so entire lines are not deleted.

           -line is a string representing single line, line endings already stripped
            returns the filtered line, which may be empty. '''

        indexStart = line.find('/*')
        indexEnd = line.find('*/')
        if ((indexStart >= 0) & (indexEnd >= 0)):
            line = line[indexEnd+2:]

        line = line.strip()

        return line 



