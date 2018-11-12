#
#SymbolTable.py
#
# CS2002   Project 11 Jack Compiler (part 2)
#
# Fall 2017
# last updated 13 DEC 2017
#
# Ryan Sowers


TYPE = 0
KIND = 1
INDEX = 2

class SymbolTable(object):

############################################
# Constructor
    def __init__(self):

        self.classLevel = { }        # dict of class-level identifiers and properties (name, type, kind, index) 


        self.subroutineLevel = { }   # dict of subroutine-level identifiers and properties (name, type, kind, index)


        self.nextIndex = {           # dict of indexes based on 'kind'
            'static' : 0,
             'field' : 0,
               'arg' : 0,
               'var' : 0
        }


    def startSubroutine(self):

        self.subroutineLevel.clear()
        self.nextIndex['arg'] = 0
        self.nextIndex['var'] = 0


    def Define(self, name, idType, kind):

        # define variable name
        if kind in ('static', 'field'):
            self.classLevel[name] = (idType, kind, self.nextIndex[kind])

        elif kind in ('arg', 'var'):
            self.subroutineLevel[name] = (idType, kind, self.nextIndex[kind])

        else:
            raise RuntimeError("Kind ", kind, " not recognized!")

        self.nextIndex[kind] += 1   # track number of 'kind' defined


    def VarCount(self, kind):

        # get number of variables of that 'kind' that have been defined
        return self.nextIndex[kind]


    def KindOf(self, name):
        
        # get the kind of 'name' as defined
        if name in self.subroutineLevel:
            return self.subroutineLevel[name][KIND]

        elif name in self.classLevel:
            return self.classLevel[name][KIND]

        else:
            return 'NONE'


    def TypeOf(self, name):

        # get the type of 'name'
        if name in self.classLevel:
            return self.classLevel[name][TYPE]

        elif name in self.subroutineLevel:
            return self.subroutineLevel[name][TYPE]


    def IndexOf(self, name):

        # get the index of 'name'
        if name in self.classLevel:
            return self.classLevel[name][INDEX]

        elif name in self.subroutineLevel:
            return self.subroutineLevel[name][INDEX]


    def tableLookup(self, name):

        # check which table 'name' is in
        if name in self.classLevel:
            return 'class'

        elif name in self.subroutineLevel:
            return 'subroutine'


    def KindOfVM(self, name):
        
        # get the 'kind' that will be output into VM
        if name in self.subroutineLevel:
            return self.subroutineLevel[name][KIND]

        elif name in self.classLevel:
            if self.classLevel[name][KIND] == 'field':
                return 'this'
            else:
                return self.classLevel[name][KIND]

        else:
            return 'NONE'
















