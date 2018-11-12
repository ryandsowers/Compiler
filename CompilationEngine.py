#
#CompilationEngine.py
#
# CS2002   Project 10 Jack Compiler (part 1)
#
# Fall 2017
# last updated 25 Oct 2016
#
# Ryan Sowers

from JTConstants import *

TT_TOKEN = 0
TT_XML = 1

class CompilationEngine(object):

############################################
# Constructor
    def __init__(self, tokenList):
        self.tokens = tokenList   #the list of tagged tokens to process (a copy was previously output as ____T.xml )

        #add and delete from this to reack left padding for XML file readability
        self.indentation = 0
        

############################################
# instance methods

    def compileTokens(self):
        ''' primary call to do the final compilation.
            returns a list of properly identified structured XML with appropriate indentation.'''

        #the compilation recursive descent always starts with the <tokens> tag, and then calls __compileClass__(),
        #  if it does not -- fail early because something is wrong, either in the tokenizing or how the file was output.
        #  **use the fail early technique throughout the compilation, you will always know which of a small number of
        #  possibilities you are looking for, if none of them are there raise the exception so you can start debugging
        
        result = []

        tokenTuple = self.__getNextEntry__()        

        if tokenTuple[TT_XML] == '<tokens>':
            result.extend( self.__compileClass__() )
            tokenTuple = self.__getNextEntry__()
            if tokenTuple[TT_XML] != '</tokens>':
                raise RuntimeError('Error, this file was not properly tokenized, missing </tokens>')
                
        else:
            raise RuntimeError('Error, this file was not properly tokenized, missing <tokens>')

        return result
    

############################################
# private/utility methods


    def __getNextEntry__(self):
        ''' removes and returns the next token from the list of tokens as a tuple of the form
            (token, <tag> token </tag>).
            TT_TOKEN and TT_XML should be used for accessing the tuple components '''
        
        if self.tokens:
            nextToken = self.tokens.pop(0)
            nextToken = nextToken.strip()
            tokenList = nextToken.split()
            if len(tokenList) == 3:
                nextEntry = (tokenList[1], nextToken)
            else:
                nextEntry = ("", nextToken)  
        else:
            raise RuntimeError("No more tokens to process")      

        return nextEntry

 
 
    def __peekAtNextEntry__(self):
        ''' copies, but does not remove the next token from the list of tokens as a tuple of the form
            (token, <tag> token </tag>).
            TT_TOKEN and TT_XML should be used for accessing the tuple components '''
        
        peekedToken = self.tokens[0]
        tokenList = peekedToken.split()
        peekedTokenTuple = (tokenList[1], peekedToken)

        return peekedTokenTuple

 
 
    def __replaceEntry__(self, entry):
        ''' returns a token to the head of the list.
            entry must properly be in the form <tag> token </tag> (in other words the TT_XML part) '''
        
        self.tokens.insert(0, entry[TT_XML])

 
 
    def __compileClass__(self):
        ''' compiles a class declaration.
            returning a list of VM commands. '''
        
        result = []
        result.append( '<class>' ) #structure label for class   <class>
        self.indentation += 2      #indentation level adjustment.  it will be paired at the bottom with a negative re-adjustment

        tokenTuple = self.__getNextEntry__()
        if tokenTuple[TT_TOKEN] == 'class':
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML]) # keyword class   
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML]) # classname identifier 
            
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML]) # <symbol> { </symbol>
            
            peekedTuple = self.__peekAtNextEntry__()
            while (peekedTuple[TT_TOKEN] == 'static' or peekedTuple[TT_TOKEN] == 'field'):  # if 'static' or 'field' present:
                result.extend( self.__compileClassVarDec__() )            # 'classVarDec' call 
                peekedTuple = self.__peekAtNextEntry__()

            peekedTuple = self.__peekAtNextEntry__()
            while (peekedTuple[TT_TOKEN] in ('constructor', 'function', 'method')):     # if 'constructor' or 'function' or 'method' present:
                result.extend( self.__compileSubroutine__() )             # 'subroutineDec' call 
                peekedTuple = self.__peekAtNextEntry__()

            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML]) # <symbol> } </symbol>

        else:
            raise RuntimeError('Error, token provided:', tokenTuple[TT_TOKEN], ', is not class')
        
        self.indentation -= 2       #indentation level re-adjustment. 
        result.append( '</class>' ) #keyword class
            
        return result



    def __compileClassVarDec__(self):
        ''' compiles a class variable declaration statement.
            returning a list of VM commands. '''
        
        result = []
        result.append( (self.indentation * ' ') + '<classVarDec>' ) #structure label for class  <classVarDec>
        self.indentation += 2      #indentation level adjustment.  it will be paired at the bottom with a negative re-adjustment

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # <keyword> 'static' OR 'field' </keyword>         
        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # <keyword> 'type' </keyword> OR <identifier> 'className' </indentifier>
        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # <identifier> 'varName' </identifier>
        peekedTuple = self.__peekAtNextEntry__()

        while peekedTuple[TT_TOKEN] == ',':      # 0 or more times (if ',' present or until ';' reached):
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # symbol ','
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # 'varName' indentifier 
            peekedTuple = self.__peekAtNextEntry__()

        tokenTuple = self.__getNextEntry__()
        if tokenTuple[TT_TOKEN] == ';':
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # symbol ';'
        else:
            raise RuntimeError("classVarDec did not close properly")

        self.indentation -= 2     #indentation level re-adjustment. 
        result.append( (self.indentation * ' ') + '</classVarDec>' ) #keyword classVarDec

        return result



    def __compileSubroutine__(self):
        ''' compiles a function/method.
            returning a list of VM commands. '''
        
        result = []
        result.append( (self.indentation * ' ') + '<subroutineDec>' ) #structure label for class   <subroutineDec>
        self.indentation += 2      #indentation level adjustment.  it will be paired at the bottom with a negative re-adjustment

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # keyword 'constructor' OR 'function' OR 'method' 
        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # keyword 'void' OR ('type' keyword OR 'className' identifier)
        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # 'subroutineName' identifier
        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # sybmol '('  
            
        result.extend( self.__compileParameterList__() )       # call to 'parameterList' 
            
        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # sybmol ')'

        result.append( (self.indentation * ' ') + '<subroutineBody>' )   # <subroutineBody>
        self.indentation += 2      #indentation level adjustment.  it will be paired at the bottom with a negative re-adjustment

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # symbol '{'
                
        peekedTuple = self.__peekAtNextEntry__()
        while (peekedTuple[TT_TOKEN] == 'var'):         # 0 or more times (if keyword 'var' present):
            result.extend( self.__compileVarDec__() )   # call to 'varDec' 
            peekedTuple = self.__peekAtNextEntry__()    
        
        result.extend( self.__compileStatements__() )       # call to 'statements' 

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])        # symbol '}'

        self.indentation -= 2     #indentation level re-adjustment. 
        result.append( (self.indentation * ' ') + '</subroutineBody>' )    # </subroutineBody>

        self.indentation -= 2     #indentation level re-adjustment. 
        result.append( (self.indentation * ' ') + '</subroutineDec>' )     # </subroutineDec>

        return result



    def __compileParameterList__(self):
        ''' compiles a parameter list from a function/method.
            returning a list of VM commands. '''
        
        result = []
        result.append( (self.indentation * ' ') + '<parameterList>' ) #structure label for class   <parameterList>
        self.indentation += 2      #indentation level adjustment.  it will be paired at the bottom with a negative re-adjustment

        peekedTuple = self.__peekAtNextEntry__()
        if peekedTuple[TT_TOKEN] != ')':            # 0 or 1 times (if 'type' given):
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # 'type' keyword OR 'className' identifier
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # 'varName' identifier
            
            peekedTuple = self.__peekAtNextEntry__()
            while peekedTuple[TT_TOKEN] == ',':      # 0 or more times (if ',' present):
                tokenTuple = self.__getNextEntry__()
                result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # symbol ','
                tokenTuple = self.__getNextEntry__()
                result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # 'type' keyword OR 'className' identifier
                tokenTuple = self.__getNextEntry__()
                result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # 'varName' indentifier 
                peekedTuple = self.__peekAtNextEntry__()
                
        self.indentation -= 2     #indentation level re-adjustment. 
        result.append( (self.indentation * ' ') + '</parameterList>' )    # </parameterList>  

        return result  



    def __compileVarDec__(self):
        ''' compiles a single variable declaration line. 
            returning a list of VM commands. '''
        
        result = []
        result.append( (self.indentation * ' ') + '<varDec>' ) #structure label for class   <varDec>
        self.indentation += 2      #indentation level adjustment.  it will be paired at the bottom with a negative re-adjustment

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # keyword 'var'
        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # 'type' keyword OR 'className' identifier
        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # 'varName' identifier
        
        peekedTuple = self.__peekAtNextEntry__()
        while peekedTuple[TT_TOKEN] == ',':      # 0 or more times (if ',' present):
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # symbol ','
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # 'varName' indentifier 
            peekedTuple = self.__peekAtNextEntry__()    
                
        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # symbol ';'
        self.indentation -= 2     #indentation level re-adjustment. 
        result.append( (self.indentation * ' ') + '</varDec>' )    # </varDec>  

        return result


    def __compileStatements__(self):
        ''' compiles statements.
            returning a list of VM commands. 
            assumes any leading and trailing braces are be consumed by the caller'''
        
        result = []
        result.append( (self.indentation * ' ') + '<statements>' ) #structure label for class   <statements>
        self.indentation += 2      #indentation level adjustment.  it will be paired at the bottom with a negative re-adjustment

        peekedTuple = self.__peekAtNextEntry__()        # if '__Statement' present, call it 0 or more times:
        while peekedTuple[TT_TOKEN] in ('let', 'if', 'while', 'do', 'return'):
            if peekedTuple[TT_TOKEN] == 'let':              # if letStatement:
                result.extend( self.__compileLet__() )      # call to 'compileLet'
            elif peekedTuple[TT_TOKEN] == 'if':             # OR if ifStatement:
                result.extend( self.__compileIf__() )       # call to 'compileIf'
            elif peekedTuple[TT_TOKEN] == 'while':          # OR if whileStatement:
                result.extend( self.__compileWhile__() )    # call to 'compileWhile'
            elif peekedTuple[TT_TOKEN] == 'do':             # OR if doStatement:
                result.extend( self.__compileDo__() )       # call to 'compileDo'
            elif peekedTuple[TT_TOKEN] == 'return':         # OR if returnStatement:
                result.extend( self.__compileReturn__() )   # call to 'compileReturn'
            peekedTuple = self.__peekAtNextEntry__()
                 
        self.indentation -= 2     #indentation level re-adjustment. 
        result.append( (self.indentation * ' ') + '</statements>' )    # </statements> 

        return result
   


    def __compileDo__(self):
        ''' compiles a function/method call.
            returning a list of VM commands. '''

        result = []
        result.append( (self.indentation * ' ') + '<doStatement>' ) #structure label   <doStatement>
        self.indentation += 2      #indentation level adjustment.  it will be paired at the bottom with a negative re-adjustment

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # keyword 'do'

        result.extend( self.__compileSubroutineCall__() )               # call to 'subroutineCall'

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # sybmol ';'
            
        self.indentation -= 2     #indentation level re-adjustment. 
        result.append( (self.indentation * ' ') + '</doStatement>' )    # </doStatement>     

        return result
            


    def __compileLet__(self):
        ''' compiles a variable assignment statement.
            returning a list of VM commands. '''
        
        result = []
        result.append( (self.indentation * ' ') + '<letStatement>' ) #structure label   <letStatement>
        self.indentation += 2      #indentation level adjustment.  it will be paired at the bottom with a negative re-adjustment

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # keyword 'let'

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # identifier 'varName'

        peekedTuple = self.__peekAtNextEntry__()
        if peekedTuple[TT_TOKEN] == '[':                      # 0 or 1 times (if '[' present):
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])       # sybmol '['
            result.extend( self.__compileExpression__() )           # call to 'expression'
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # symbol ']'

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])       # sybmol '='

        result.extend( self.__compileExpression__() )           # call to 'expression'

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])       # sybmol ';'
            
        self.indentation -= 2     #indentation level re-adjustment. 
        result.append( (self.indentation * ' ') + '</letStatement>' )    # </letStatement>

        return result
            


    def __compileWhile__(self):
        ''' compiles a while loop.
            returning a list of VM commands. '''
        
        result = []
        result.append( (self.indentation * ' ') + '<whileStatement>' ) #structure label   <whileStatement> 
        self.indentation += 2      #indentation level adjustment.  it will be paired at the bottom with a negative re-adjustment

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # keyword 'while'
        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # symbol '('
        
        result.extend( self.__compileExpression__() )    # call to 'expression'

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # symbol ')'
        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # symbol '{'

        result.extend( self.__compileStatements__() )    # call to 'statements'

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # symbol '}'

        self.indentation -= 2     #indentation level re-adjustment. 
        result.append( (self.indentation * ' ') + '</whileStatement>' )  # </whileStatement>

        return result



    def __compileReturn__(self):
        ''' compiles a function return statement. 
            returning a list of VM commands. '''
        
        result = []
        result.append( (self.indentation * ' ') + '<returnStatement>' ) #structure label   <returnStatement>
        self.indentation += 2      #indentation level adjustment.  it will be paired at the bottom with a negative re-adjustment

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # keyword 'return'

        peekedTuple = self.__peekAtNextEntry__()
        if peekedTuple[TT_TOKEN] != ';':                     # 0 or 1 times (until ';' reached)
            result.extend( self.__compileExpression__() )    # call to 'expression' 

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # symbol ';'

        self.indentation -= 2     #indentation level re-adjustment. 
        result.append( (self.indentation * ' ') + '</returnStatement>' ) # </returnStatement>

        return result



    def __compileIf__(self):
        ''' compiles an if(else)? statement block. 
            returning a list of VM commands. '''
        
        result = []
        result.append( (self.indentation * ' ') + '<ifStatement>' ) #structure label   <ifStatement>
        self.indentation += 2      #indentation level adjustment.  it will be paired at the bottom with a negative re-adjustment

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # keyword 'if'
        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # symbol '('

        result.extend( self.__compileExpression__() )    # call to 'expression'

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # symbol ')'
        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # sybmol '{'

        result.extend( self.__compileStatements__() )       # call to 'statements'
            
        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # symbol '}'

        peekedTuple = self.__peekAtNextEntry__()
        if peekedTuple[TT_TOKEN] == 'else':     # 0 or 1 times (if 'else' present):
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # keyword 'else'
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # symbol '{'

            result.extend( self.__compileStatements__() )   # call to 'statements'
                
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # symbol '}'

        self.indentation -= 2     #indentation level re-adjustment. 
        result.append( (self.indentation * ' ') + '</ifStatement>' )    # </ifStatement>

        return result



    def __compileExpression__(self):
        ''' compiles an expression.
            returning a list of VM commands. '''

        result = []
        result.append( (self.indentation * ' ') + '<expression>' ) #structure label   <expression>
        self.indentation += 2      #indentation level adjustment.  it will be paired at the bottom with a negative re-adjustment
 
        result.extend ( self.__compileTerm__() )    # call to 'term'

        peekedTuple = self.__peekAtNextEntry__()
        while (peekedTuple[TT_TOKEN] in BINARY_OPERATORS or peekedTuple[TT_TOKEN] in UNARY_OPERATORS):    # 0 or more times (if 'op' present):
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # 'op' symbol

            result.extend( self.__compileTerm__() )    # call to 'term'

            peekedTuple = self.__peekAtNextEntry__()

        self.indentation -= 2     #indentation level re-adjustment. 
        result.append( (self.indentation * ' ') + '</expression>' )    # </expression>

        return result



    def __compileTerm__(self):
        ''' compiles a term. 
            returning a list of VM commands. '''
        
        result = []
        result.append( (self.indentation * ' ') + '<term>' ) #structure label   <term>
        self.indentation += 2      #indentation level adjustment.  it will be paired at the bottom with a negative re-adjustment

        tokenTuple = self.__getNextEntry__()
        if tokenTuple[TT_TOKEN] == '(':         # if '(':
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])       # symbol '('
            result.extend( self.__compileExpression__() )       # call to 'expression'
            tokenTuple = self.__getNextEntry__()       
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])       # symbol ')'

        elif (tokenTuple[TT_TOKEN] in BINARY_OPERATORS or tokenTuple[TT_TOKEN] in UNARY_OPERATORS):    # if item in OPERATORS dict:
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # 'unaryOp' symbol
            result.extend( self.__compileTerm__() )    # call to 'term'

        else:
            peekedTuple = self.__peekAtNextEntry__()
            if (peekedTuple[TT_TOKEN] == '(' or peekedTuple[TT_TOKEN] == '.'):      # if 'identifier' followed immediately by '(' or '.': 
                self.__replaceEntry__(tokenTuple)
                result.extend( self.__compileSubroutineCall__() )       # 'subroutineCall'
            else:
                if tokenTuple[TT_TOKEN] in KEYWORDS:
                    result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # keywordCosntant
                elif 'Constant' in tokenTuple[TT_XML]:
                    result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # integerConstant or stringConstant
                else:
                    result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # varName
                    if peekedTuple[TT_TOKEN] == '[':        # if expression
                        tokenTuple = self.__getNextEntry__()
                        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # symbol '['
                        result.extend( self.__compileExpression__() )       # call to expression
                        tokenTuple = self.__getNextEntry__()
                        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # symbol ']'
            
        self.indentation -= 2     #indentation level re-adjustment. 
        result.append( (self.indentation * ' ') + '</term>' )    # </term>

        return result        



    def __compileExpressionList__(self):
        ''' compiles a list of expressions. 
            returning a list of VM commands. '''
        
        result = [] 
        result.append( (self.indentation * ' ') + '<expressionList>' ) #structure label   <expressionList>
        self.indentation += 2      #indentation level adjustment.  it will be paired at the bottom with a negative re-adjustment

        peekedTuple = self.__peekAtNextEntry__()
        if peekedTuple[TT_TOKEN] != ')':            # 0 or 1 times (if 'expression' present):
            result.extend( self.__compileExpression__() )       # 'expression' call
            peekedTuple = self.__peekAtNextEntry__()
            while peekedTuple[TT_TOKEN] == ',':      # 0 or more times (if ',' present):
                tokenTuple = self.__getNextEntry__()
                result.append( (self.indentation * ' ') + tokenTuple[TT_XML])      # symbol ','
                result.extend( self.__compileExpression__() )   # 'expression' call 
                peekedTuple = self.__peekAtNextEntry__()
                
        self.indentation -= 2     #indentation level re-adjustment. 
        result.append( (self.indentation * ' ') + '</expressionList>' )    # </expressionList>   

        return result



    def __compileSubroutineCall__(self):
        ''' compiles a subroutine call.
            returning a list of VM commands. '''
        
        result = []
        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # 'subroutineName' identifier OR 'className' identifier OR 'varName' identifier

        peekedTuple = self.__peekAtNextEntry__() 
        if peekedTuple[TT_TOKEN] == '.':            # if 'identifier' followed by '.'):
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])       # 'symbol '.'
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])       # 'subroutineName' identifier

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # symbol '('
        result.extend( self.__compileExpressionList__() )               # 'expressionList' call
        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # symbol ')'

        return result
    

