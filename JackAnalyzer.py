#
#JackAnalyzer.py
#
# CS2002   Project 10 & 11 Jack Compiler 
#
# Fall 2017
# last updated 13 DEC 2017
#
# Ryan Sowers


import sys  #for grading server
from pathlib import *

from JackTokenizer import *
from CompilationEngine import *
from JTConstants import *



class JackAnalyzer(object):

##########################################
#Constructor

    def __init__(self, target):
        self.targetPath = Path(target)



##########################################
#public methods
        
    def process(self):
        ''' iterates over a directory causing each .jack file to be processed.
            returns the pathname of the directory upon successful completion. '''
        
        if self.targetPath.is_dir():
            for eachFile in sorted(self.targetPath.iterdir()):  # added 'sorted' because my files weren't being compiled in alphabetical order
                if eachFile.suffix == '.jack':
                    # print(eachFile)
                    self.__processFile__(eachFile)  #file as a pathlib object
                    
        else:
            raise RuntimeError("Error, " + target.name + " is not a directory ")
        
        return str(self.targetPath)


##########################################
#private methods
    
    def __processFile__(self, filePath):
        ''' processes a single file, first feeding the file to JackTokenizer to generate a list of tokens
            (output as T.xml files for debugging use) and that token list is fed through
            CompilationEngine to generate a final result list of XML tokens which is output into an .xml file. '''
        
        tokenizedCodeList = []

        tknzr = JackTokenizer(filePath)
        token = tknzr.advance() 
        tokenizedCodeList.append("<tokens>")
        while (token):
            tokenizedCodeList.append('  ' + self.__wrapTokenInXML__(token))
            token = tknzr.advance()
        tokenizedCodeList.append("</tokens>")

        index = str(filePath).find('.jack')
        if (index < 1):
            raise RuntimeError("Error, cannot use the filename: " + str(filePath))
        tokenizedOutput = str(filePath)[:index] + 'T.xml'

        self.__output__(tokenizedOutput, tokenizedCodeList)     # output __T.xml file

    
        finalCodeList = []

        cmplEng = CompilationEngine(tokenizedCodeList)      # built with __T.xml list
        finalTokenList = cmplEng.compileTokens()
        finalCodeList.extend(finalTokenList)
        finalOutput = str(filePath)[:index] + '.xml'

        self.__output__(finalOutput, finalCodeList)         # output .xml file


        vmOutputFilePath = str(filePath)[:index] + '.vm'

        self.__output__(vmOutputFilePath, cmplEng.compileVM())  # output .vm file



    def __output__(self, filePath, codeList):
        ''' outputs the VM code codeList into a file and returns the file path'''
            
        file = open(str(filePath), 'w')
        file.write("\n".join(codeList))
        file.close()
 


    def __wrapTokenInXML__(self, token):
        ''' returns an XML tag pair with the token properly sandwiched.
             conducts proper substitutions and quotation mark removals. ''' 

        if token in KEYWORDS:
            flavor = "keyword"
        elif token in SYMBOLS:
            flavor = "symbol"
            if token in glyphSubstitutes:
                token = glyphSubstitutes[token]
        elif token[0].isdigit():
            flavor = "integerConstant"
        elif token.startswith('"'):
            flavor = "stringConstant"
            parts = token.split('"')
            token = parts[1]
        elif token[0] in IDENTIFIER_START_CHARS:
            flavor = "identifier"
        else:
            flavor = 'unknown'

        return '<' + flavor + '> ' + token + ' </' + flavor + '>'








#################################
#################################
#################################
#this kicks off the program and assigns the argument to a variable
#
if __name__=="__main__":

    target = sys.argv[1]     # use this one for final deliverable

    #project 10 tests
##    target = 'ExpressionlessSquare'
##    target = 'ArrayTest'
##    target = 'Square'


    #project 11 tests
##    target = 'Seven'            # .xml and T.xml comparison match; .vm passes comparison
##    target = 'ConvertToBin'     # .xml and T.xml comparison match; .vm passes comparison
##    target = 'Square'           # .xml and T.xml comparison match; .vm passes comparison
##    target = 'Average'          # .xml and T.xml comparison match; .vm passes comparison
##    target = 'Pong'             # .xml and T.xml comparison match; .vm passes comparison
##    target = 'ComplexArrays'    # .xml and T.xml comparison match; .vm passes comparison
    
    analyzer = JackAnalyzer(target)
    print('\n' + analyzer.process() + ' has been translated.')







    
