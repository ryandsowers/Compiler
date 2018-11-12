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
from SymbolTable import *
from VMWriter import *

TT_TOKEN = 0
TT_XML = 1

class CompilationEngine(object):

    labelID = 0

############################################
# Constructor
    def __init__(self, tokenList):
        self.tokens = tokenList   #the list of tagged tokens to process (a copy was previously output as ____T.xml )

        #add and delete from this to reack left padding for XML file readability
        self.indentation = 0

        self.vmList = [] 


############################################
# static class methods
#    these methods are owned by the Class not one instance
#    note they do not have self as the first argument and they have the @staticmethod tag

    @staticmethod
    def __getSimpleLabel__():
        ''' a static utility method to access the class variable '''
        
        # creates a unique label for flow of control statements
        result = str(CompilationEngine.labelID)
        CompilationEngine.labelID += 1
        
        return result


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


    def compileVM(self):

        return self.vmList
    

############################################
# private/utility methods


    def __getNextEntry__(self):
        ''' removes and returns the next token from the list of tokens as a tuple of the form
            (token, <tag> token </tag>).
            TT_TOKEN and TT_XML should be used for accessing the tuple components '''
        
        # updated to handle output of stringConstant token; previously would split string constants at spaces (' ')
        if self.tokens:
            nextToken = self.tokens.pop(0)
            nextToken = nextToken.strip()
            tokenList = nextToken.split()
            if len(tokenList) > 1:
                leftSplit = nextToken.split('> ', 1)
                # print(leftSplit)
                rightSplit = leftSplit[1].split(' <', 1)
                token = rightSplit[0]
                if 'stringConstant' not in nextToken:
                    token = token.strip()
                nextEntry = (token, nextToken)
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
        
        self.st = SymbolTable()

        result = []
        result.append( '<class>' ) #structure label for class   <class>
        self.indentation += 2      #indentation level adjustment.  it will be paired at the bottom with a negative re-adjustment

        tokenTuple = self.__getNextEntry__()
        if tokenTuple[TT_TOKEN] == 'class':
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML]) # keyword class   
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML]) # classname identifier 

            self.className = tokenTuple[TT_TOKEN]
            
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML]) # <symbol> { </symbol>
            
            peekedTuple = self.__peekAtNextEntry__()
            while (peekedTuple[TT_TOKEN] == 'static' or peekedTuple[TT_TOKEN] == 'field'):  # if 'static' or 'field' present:
                result.extend( self.__compileClassVarDec__() )            # 'classVarDec' call 
                peekedTuple = self.__peekAtNextEntry__()

            peekedTuple = self.__peekAtNextEntry__()
            while (peekedTuple[TT_TOKEN] in SUBROUTINES):     # if 'constructor' or 'function' or 'method' present:
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
        
        kind = tokenTuple[TT_TOKEN]                 # 'static' or 'field'
        
        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # <keyword> 'type' </keyword> OR <identifier> 'className' </indentifier>
        
        idType = tokenTuple[TT_TOKEN]               # type (keyword or className)
        
        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # <identifier> 'varName' </identifier>
        
        name = tokenTuple[TT_TOKEN]                 # variable name
        self.st.Define(name, idType, kind)          # define variable in symbol table
        result.append( (self.indentation * ' ') + '<SYMBOL-Defined> class.' + name + ' (' + kind + ' ' + idType + ') = ' + str(self.st.IndexOf(name)) + ' </SYMBOL-Defined>')        
        
        peekedTuple = self.__peekAtNextEntry__()
        while peekedTuple[TT_TOKEN] == ',':      # 0 or more times (if ',' present or until ';' reached):
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # symbol ','
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # 'varName' indentifier 
            
            name = tokenTuple[TT_TOKEN]             # variable name
            self.st.Define(name, idType, kind)      # define variable in symbol table
            result.append( (self.indentation * ' ') + '<SYMBOL-Defined> class.' + name + ' (' + kind + ' ' + idType + ') = ' + str(self.st.IndexOf(name)) + ' </SYMBOL-Defined>')        
            
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
        
        self.st.startSubroutine()

        result = []
        result.append( (self.indentation * ' ') + '<subroutineDec>' ) #structure label for class   <subroutineDec>
        self.indentation += 2      #indentation level adjustment.  it will be paired at the bottom with a negative re-adjustment

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # keyword 'constructor' OR 'function' OR 'method' 
        
        self.subKeyword = tokenTuple[TT_TOKEN]
        if self.subKeyword == 'method':                 # if compiling a method, need to add 'this' to symbol table
            idType = self.className
            kind = 'arg'
            name = 'this'
            self.st.Define(name, idType, kind)

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # keyword 'void' OR ('type' keyword OR 'className' identifier)
        
        self.subroutineType = tokenTuple[TT_TOKEN]      # used to identify 'void' methods

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # 'subroutineName' identifier
       
        name = tokenTuple[TT_TOKEN]                     # variable name
                
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
        
        funcName = self.className + '.' + name          # write the function name declared
        self.vmList.append( writeFunction(funcName, self.st.VarCount('var')) )
        if self.subKeyword == 'constructor':            # handle a constructor declaration
            self.vmList.append( writePush('constant', self.st.VarCount('field')) )
            self.vmList.append( writeCall('Memory.alloc', 1) )
            self.vmList.append( writePop('pointer', 0) )            
        elif self.subKeyword == 'method':               # handle a method declaration
            self.vmList.append( writePush(self.st.KindOfVM('this'), self.st.IndexOf('this')) )
            self.vmList.append( writePop('pointer', 0) ) 

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
            
            kind = 'arg'                            # arguments declared
            
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # 'type' keyword OR 'className' identifier
            
            idType = tokenTuple[TT_TOKEN]           # 'type' or 'className' of argument
            
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # 'varName' identifier
            
            name = tokenTuple[TT_TOKEN]             # name of argument
            self.st.Define(name, idType, kind)      # define argument
            result.append( (self.indentation * ' ') + '<SYMBOL-Defined> subroutine.' + name + ' (' + kind + ' ' + idType + ') = ' + str(self.st.IndexOf(name)) + ' </SYMBOL-Defined>')            
            
            peekedTuple = self.__peekAtNextEntry__()
            while peekedTuple[TT_TOKEN] == ',':      # 0 or more times (if ',' present):
                tokenTuple = self.__getNextEntry__()
                result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # symbol ','
                tokenTuple = self.__getNextEntry__()
                result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # 'type' keyword OR 'className' identifier
                
                idType = tokenTuple[TT_TOKEN]       # 'type' or 'className' of argument
                
                tokenTuple = self.__getNextEntry__()
                result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # 'varName' indentifier 
                
                name = tokenTuple[TT_TOKEN]         # name of argument
                self.st.Define(name, idType, kind)  # define argument
                result.append( (self.indentation * ' ') + '<SYMBOL-Defined> subroutine.' + name + ' (' + kind + ' ' + idType + ') = ' + str(self.st.IndexOf(name)) + ' </SYMBOL-Defined>')            
                
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

        kind = 'var'                                # local variables declared

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # 'type' keyword OR 'className' identifier

        idType = tokenTuple[TT_TOKEN]               # type of local variable

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # 'varName' identifier

        name = tokenTuple[TT_TOKEN]                 # name of local variable
        self.st.Define(name, idType, kind)          # define local varialbe
        result.append( (self.indentation * ' ') + '<SYMBOL-Defined> subroutine.' + name + ' (' + kind + ' ' + idType + ') = ' + str(self.st.IndexOf(name)) + ' </SYMBOL-Defined>')
        
        peekedTuple = self.__peekAtNextEntry__()
        while peekedTuple[TT_TOKEN] == ',':      # 0 or more times (if ',' present):
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # symbol ','
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # 'varName' indentifier 

            name = tokenTuple[TT_TOKEN]             # name of local variable
            self.st.Define(name, idType, kind)      # define local varialbe
            result.append( (self.indentation * ' ') + '<SYMBOL-Defined> subroutine.' + name + ' (' + kind + ' ' + idType + ') = ' + str(self.st.IndexOf(name)) + ' </SYMBOL-Defined>')
            
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

        if self.functionName:               # if there was a two-part functionName declared (with object) in the subroutineCall
            if self.st.tableLookup(self.st.TypeOf(self.callerName)) not in ('int', 'char', 'boolean') and self.st.tableLookup(self.callerName) in ('subroutine', 'class'):      # and if the object has been defined
                self.vmList.append( writeCall(self.st.TypeOf(self.callerName) + '.' + self.functionName, self.args + 1) )       # call the type of the object and the functionName
            else:
                self.vmList.append( writeCall(self.callerName + '.' + self.functionName, self.args) )       # otherwise, just call the function as written
        else:
            self.vmList.append( writeCall(self.className + '.' + self.callerName, self.args + 1) )          # if no object, just call the written function

        self.vmList.append( writePop('temp', 0) )           # pop the result to 'temp 0'
            
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

        name = tokenTuple[TT_TOKEN]         # identifier to be used
        result.append( (self.indentation * ' ') + '<SYMBOL-Used> ' + self.st.tableLookup(name) + '.' + name + ' (' + self.st.KindOf(name) + ' ' + self.st.TypeOf(name) + ') = ' + str(self.st.IndexOf(name)) + ' </SYMBOL-Used>')

        arrayDeclared = False               # no array declared yet

        peekedTuple = self.__peekAtNextEntry__()
        if peekedTuple[TT_TOKEN] == '[':    # 0 or 1 times (if '[' present):
            arrayDeclared = True            # we have entered an array declaration

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

        if arrayDeclared:               # if an array has been declared, get the correct memory address and store the value
            self.vmList.append( writePop('temp', 0) )
            self.vmList.append( writePush(self.st.KindOfVM(name), self.st.IndexOf(name)) )
            self.vmList.append( 'add' )
            self.vmList.append( writePop('pointer', 1) )
            self.vmList.append( writePush('temp', 0) )
            self.vmList.append( writePop('that', 0) )
        else:
            self.vmList.append(writePop(self.st.KindOfVM(name), self.st.IndexOf(name)))     # otherwise, pop the value to the variable
            
        self.indentation -= 2     #indentation level re-adjustment. 
        result.append( (self.indentation * ' ') + '</letStatement>' )    # </letStatement>

        return result
            


    def __compileWhile__(self):
        ''' compiles a while loop.
            returning a list of VM commands. '''
        
        result = []
        result.append( (self.indentation * ' ') + '<whileStatement>' ) #structure label   <whileStatement> 
        self.indentation += 2      #indentation level adjustment.  it will be paired at the bottom with a negative re-adjustment

        scopeLabel = CompilationEngine.__getSimpleLabel__()             # get a number to make the label unique
        self.vmList.append( writeLabel('WHILE_TOP_' + scopeLabel) )     # while entry label

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # keyword 'while'
        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # symbol '('
        
        result.extend( self.__compileExpression__() )    # call to 'expression'

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # symbol ')'

        self.vmList.append( 'not' )                 # negate the expression
        self.vmList.append( writeIf('WHILE_EXIT_' + scopeLabel) )   # if-goto statement to allow exit

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # symbol '{'

        result.extend( self.__compileStatements__() )    # call to 'statements'

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # symbol '}'

        self.vmList.append( writeGoto('WHILE_TOP_' + scopeLabel) )      # go-to start of while to evaluate
        self.vmList.append( writeLabel('WHILE_EXIT_' + scopeLabel) )    # while exit label

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

        if self.subroutineType == 'void':
            self.vmList.append( writePush('constant', 0) )
        self.vmList.append('return')

        self.indentation -= 2     #indentation level re-adjustment. 
        result.append( (self.indentation * ' ') + '</returnStatement>' ) # </returnStatement>

        return result



    def __compileIf__(self):
        ''' compiles an if(else)? statement block. 
            returning a list of VM commands. '''
        
        result = []
        result.append( (self.indentation * ' ') + '<ifStatement>' ) #structure label   <ifStatement>
        self.indentation += 2      #indentation level adjustment.  it will be paired at the bottom with a negative re-adjustment

        scopeLabel = CompilationEngine.__getSimpleLabel__()         # get a number to make the label unique

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # keyword 'if'
        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # symbol '('

        result.extend( self.__compileExpression__() )    # call to 'expression'

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # symbol ')'

        self.vmList.append( 'not' )             # negate the expression
        self.vmList.append( writeIf('DO_ELSE_' + scopeLabel) )      # if-goto 'else'

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # sybmol '{'

        result.extend( self.__compileStatements__() )       # call to 'statements'
            
        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # symbol '}'

        self.vmList.append( writeGoto('IF_THEN_COMPLETE_' + scopeLabel) )       # go-to end of if-then

        self.vmList.append( writeLabel('DO_ELSE_' + scopeLabel) )               # 'else' label

        peekedTuple = self.__peekAtNextEntry__()
        if peekedTuple[TT_TOKEN] == 'else':     # 0 or 1 times (if 'else' present):
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # keyword 'else'
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # symbol '{'

            result.extend( self.__compileStatements__() )   # call to 'statements'

            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # symbol '}'

        self.vmList.append( writeLabel('IF_THEN_COMPLETE_' + scopeLabel) )      # end of if-then

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

            operator = tokenTuple[TT_TOKEN]             # get the operator

            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])    # 'op' symbol
            result.extend( self.__compileTerm__() )    # call to 'term'

            if operator in ('*', '/'):          # we need to call the function
                self.vmList.append( writeCall( writeArithmetic(operator), 2) )
            else:
                self.vmList.append( writeArithmetic(operator) )         # place the operator

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

            self.vmList.append( UNARY_OPERATORS[tokenTuple[TT_TOKEN]])      # add the unary operator

        else:
            peekedTuple = self.__peekAtNextEntry__()
            if (peekedTuple[TT_TOKEN] == '(' or peekedTuple[TT_TOKEN] == '.'):      # if 'identifier' followed immediately by '(' or '.': 
                self.__replaceEntry__(tokenTuple)
                result.extend( self.__compileSubroutineCall__() )       # 'subroutineCall'

                if self.functionName:                   # if there was a two-part functionName declared (with object) in the subroutineCall
                    if self.st.tableLookup(self.st.TypeOf(self.callerName)) not in ('int', 'char', 'boolean') and self.st.tableLookup(self.callerName) in ('subroutine', 'class'):  # and if the object has been defined
                        self.vmList.append( writeCall(self.st.TypeOf(self.callerName) + '.' + self.functionName, self.args + 1) )       # call the type of the object and the functionName
                    else:
                        self.vmList.append( writeCall(self.callerName + '.' + self.functionName, self.args) )       # otherwise, just call the function as written

            else:
                if tokenTuple[TT_TOKEN] in KEYWORDS:
                    result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # keywordConstant

                    if tokenTuple[TT_TOKEN] in ('true', 'false'):
                        self.vmList.append( writePush('constant', 0) )      # 'push constant 0'
                        if tokenTuple[TT_TOKEN] == 'true':
                            self.vmList.append('not')                       # negate if 'true'
                    elif tokenTuple[TT_TOKEN] == 'this':
                        self.vmList.append( writePush('pointer', 0) )       # 'push pointer 0'
                    elif tokenTuple[TT_TOKEN] == 'null':
                        self.vmList.append( writePush('constant', 0) )      # 'push constant 0'

                elif 'Constant' in tokenTuple[TT_XML]:
                    segment = 'constant'                # 'constant' segment
                    if 'integerConstant' in tokenTuple[TT_XML]:
                        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # integerConstant

                        index = tokenTuple[TT_TOKEN]    # constant number
                        self.vmList.append( writePush(segment, index) )     # 'push constant #'
                    elif 'stringConstant' in tokenTuple[TT_XML]:
                        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   #  stringConstant

                        index = len(tokenTuple[TT_TOKEN])       # number of characters in string
                        self.vmList.append( writePush(segment, index) )     # push constant # of chars
                        self.vmList.append( writeCall('String.new', 1) )    # call new string fucntion
                        for ch in tokenTuple[TT_TOKEN]:
                            self.vmList.append( writePush('constant', ord(ch)) )    # get the ASCII values of the characters
                            self.vmList.append( writeCall('String.appendChar', 2) ) # call the appendChar string function on each char
                else:
                    result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # varName

                    name = tokenTuple[TT_TOKEN]     # varName identifier
                    arrayDeclared = False           # no array declared
                    result.append( (self.indentation * ' ') + '<SYMBOL-Used> ' + self.st.tableLookup(name) + '.' + name + ' (' + self.st.KindOf(name) + ' ' + self.st.TypeOf(name) + ') = ' + str(self.st.IndexOf(name)) + ' </SYMBOL-Used>')
                    
                    if peekedTuple[TT_TOKEN] == '[':        # if expression
                        arrayDeclared = True        # entering array declaration

                        tokenTuple = self.__getNextEntry__()
                        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # symbol '['
                        result.extend( self.__compileExpression__() )       # call to expression
                        tokenTuple = self.__getNextEntry__()
                        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # symbol ']'

                    self.vmList.append( writePush(self.st.KindOfVM(name), self.st.IndexOf(name)) )      # push the variable name
                    if arrayDeclared:       # if the variable was an array, address the memory offset and store the value
                        self.vmList.append('add')
                        self.vmList.append( writePop('pointer', 1) )
                        self.vmList.append( writePush('that', 0) )
            
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

            self.args += 1              # argument encountered

            peekedTuple = self.__peekAtNextEntry__()
            while peekedTuple[TT_TOKEN] == ',':      # 0 or more times (if ',' present):
                tokenTuple = self.__getNextEntry__()
                result.append( (self.indentation * ' ') + tokenTuple[TT_XML])      # symbol ','
                result.extend( self.__compileExpression__() )   # 'expression' call 
                self.args += 1          # argument encountered
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

        self.callerName = tokenTuple[TT_TOKEN]      # funciton to be called or className or objectName
        self.args = 0                               # check the number of arguments
        self.functionName = None                    # do we have a method or function name

        if self.st.KindOfVM(self.callerName) != 'NONE':         # if the symbol has been defined
            result.append( (self.indentation * ' ') + '<SYMBOL-Used> ' + self.st.tableLookup(self.callerName) + '.' + self.callerName + ' (' + self.st.KindOf(self.callerName) + ' ' + self.st.TypeOf(self.callerName) + ') = ' + str(self.st.IndexOf(self.callerName)) + ' </SYMBOL-Used>')

        peekedTuple = self.__peekAtNextEntry__() 
        if peekedTuple[TT_TOKEN] == '.':            # if 'identifier' followed by '.':
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])       # 'symbol '.'
            tokenTuple = self.__getNextEntry__()
            result.append( (self.indentation * ' ') + tokenTuple[TT_XML])       # 'subroutineName' identifier
            
            self.functionName = tokenTuple[TT_TOKEN]    # we have a method or function name

        if self.functionName:               # if there was a two-part functionName declared (with object) in the subroutineCall
            if self.st.tableLookup(self.st.TypeOf(self.callerName)) not in ('int', 'char', 'boolean') and self.st.tableLookup(self.callerName) in ('subroutine', 'class'):      # and if the object has been defined
                self.vmList.append( writePush(self.st.KindOfVM(self.callerName), self.st.IndexOf(self.callerName)) )        # call the type of the object and the functionName
        else:
            self.vmList.append( writePush('pointer', 0) )       # otherwise we're operating on current object

        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # symbol '('
        result.extend( self.__compileExpressionList__() )               # 'expressionList' call
        tokenTuple = self.__getNextEntry__()
        result.append( (self.indentation * ' ') + tokenTuple[TT_XML])   # symbol ')'

        return result
    

