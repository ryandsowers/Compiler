#
#VMWriter.py
#
# CS2002   Project 11 Jack Compiler (part 2)
#
# Fall 2017
# last updated 13 DEC 2017
#
# Ryan Sowers


from JTConstants import *

def writePush(segment, index):
    if segment == 'var':
        return 'push ' + 'local' + ' ' + str(index)
    elif segment == 'arg':
        return 'push ' + 'argument' + ' ' + str(index)
    else:
        return 'push ' + segment + ' ' + str(index)


def writePop(segment, index):
    if segment == 'var':
        return 'pop ' + 'local' + ' ' + str(index)
    elif segment == 'arg':
        return 'pop ' + 'argument' + ' ' + str(index)
    else:
        return 'pop ' + segment + ' ' + str(index)


def writeArithmetic(operator):
    return BINARY_OPERATORS[operator]


def writeLabel(label):
    return 'label ' + label


def writeGoto(label):
    return 'goto ' + label


def writeIf(label):
    return 'if-goto ' + label


def writeCall(name, nArgs):
    return 'call ' + name + ' ' + str(nArgs)


def writeFunction(name, nLocals):
    return 'function ' + name + ' ' + str(nLocals)


def writeReturn():
    return 'return'

