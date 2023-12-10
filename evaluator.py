# Name: Bang Ngoc Pham
# Phase: 3.1

import re
import sys
dir(re)

number = "[0-9]+"
identifier = "([a-z]|[A-Z])([a-z]|[A-Z]|[0-9])*"
symbol = "[+]|[-]|[*]|[/]|[(]|[)]|:=|[;]"
keyword = "if|then|else|endif|while|do|endwhile|skip"

def Scanner(line, token_list):
    if re.match(number, line):
        token = re.match(number, line).group()
        token_list.append((token, "NUMBER"))
    elif re.match(identifier, line):
        token = re.match(identifier, line).group()
        kw = re.match(keyword, token)
        if kw and len(kw.group()) == len(token):
            token_list.append((token, "KEYWORD"))
        else: token_list.append((token, "IDENTIFIER"))
    elif re.match(symbol, line):
        token = re.match(symbol, line).group()
        token_list.append((token, "SYMBOL"))
    elif re.match(" ", line) or re.match("  ", line):
        token = line[0]
    elif line == "\n" or line == "":
        return
    else:
        token = line[0]
        token_list.append((token, "ERROR"))
    Scanner(line.replace(token, "", 1), token_list)

class Tree:
    def __init__(self):
        self.data = None
        self.regex = None
        self.left = None
        self.middle = None
        self.right = None
        self.AST = True

    def getData(self): return self.data
    def getRegex(self): return self.regex
    def getLeftSubTree(self): return self.left
    def getMiddleSubTree(self): return self.middle
    def getRightSubTree(self): return self.right
    def getAST(self): return self.AST


class Interior(Tree):
    def __init__(self, d, reg, l, r):
        self.data = d
        self.regex = reg
        self.left = l
        self.middle = None
        self.right = r
        self.AST = True
class InteriorIF(Tree):
    def __init__(self, d, reg, l, m, r):
        self.data = d
        self.regex =reg
        self.left = l
        self.middle = m
        self.right = r
        self.AST = True

class Leaf(Tree):
    def __init__(self, d, reg, a):
        self.data = d
        self.regex = reg
        self.AST = a
        self.left = None
        self.middle = None
        self.right = None

def consume_token(token_list):
    if token_list: token_list.pop(0)

def parseStat(token_list):
    tree = parseBase(token_list)
    while token_list and token_list[0][0] == ';':
        d = token_list[0][0]
        reg = token_list[0][1]
        consume_token(token_list)
        if not token_list: return Leaf(None, None, False)
        tree = Interior(d, reg, tree, parseBase(token_list))
    return tree
def parseBase(token_list):
    if token_list:
        if token_list[0][1] == "IDENTIFIER":
            if token_list[1][0] == ":=": return parseAss(token_list)
            else: return parseExpr(token_list)
        elif token_list[0][1] == "KEYWORD":
            if token_list[0][0] == "if":
                return parseIf(token_list)
            elif token_list[0][0] == "while":
                return parseWhile(token_list)
            elif token_list[0][0] == "skip":
                d = token_list[0][0]
                reg = token_list[0][1]
                consume_token(token_list)
                return Leaf(d, reg, True)
            else: return Leaf(None, False)
        else: return parseExpr(token_list)
def parseAss(token_list):
    dl = token_list[0][0]
    regl = token_list[0][1]
    l = Leaf(dl, regl, True)
    consume_token(token_list)
    d = token_list[0][0]
    reg = token_list[0][1]
    consume_token(token_list)
    r = parseExpr(token_list)
    if not r: return Leaf(None, None, False)
    return Interior(d, reg, l, r)

def parseIf(token_list):
    consume_token(token_list)
    if token_list:
        l = parseExpr(token_list)
    else: return Leaf(None, None, False)

    if token_list:
        if token_list[0][0] == "then":
            consume_token(token_list)
            if token_list:
                m = parseStat(token_list)
            else: return Leaf(None, None, False)
        else: return Leaf(None, None, False)
    else: return Leaf(None, None, False)

    if token_list:
        if token_list[0][0] == "else":
            consume_token(token_list)
            if token_list:
                r = parseStat(token_list)
            else: return Leaf(None, None, False)
        else: return Leaf(None, None, False)
    else: return Leaf(None, None, False)

    if token_list:
        if token_list[0][0] == "endif":
            consume_token(token_list)
            return InteriorIF("IF-STATEMENT", "", l, m, r)
        else: return Leaf(None, None, False)
    else: return Leaf(None, None, False)

def parseWhile(token_list):
    consume_token(token_list)
    if token_list:
        l = parseExpr(token_list)
    else: l = Leaf(None, None, False)

    if token_list:
        if token_list[0][0] == "do":
            consume_token(token_list)
            if token_list:
                r = parseStat(token_list)
            else: r = Leaf(None, None, False)
        else: r = Leaf(None, None, False)
    else: r = Leaf(None, None, False)

    if token_list:
        if token_list[0][0] == "endwhile":
            consume_token(token_list)
            return Interior("WHILE_LOOP", "", l, r)
        else: return Leaf(None, None, False)
    else: return Leaf(None, None, False)

def parseExpr(token_list):
    tree = parseTerm(token_list)
    while token_list and token_list[0][0] == '+':
        d = token_list[0][0]
        reg = token_list[0][1]
        consume_token(token_list)
        if not token_list: return Leaf(None, None, False)
        tree = Interior(d, reg, tree, parseTerm(token_list))
    return tree

def parseTerm(token_list):
    tree = parseFactor(token_list)
    while token_list and token_list[0][0] == '-':
        d = token_list[0][0]
        reg = token_list[0][1]
        consume_token(token_list)
        if not token_list: return Leaf(None, None, False)
        tree = Interior(d, reg, tree, parseFactor(token_list))
    return tree

def parseFactor(token_list):
    tree = parsePiece(token_list)
    while token_list and token_list[0][0] == '/':
        d = token_list[0][0]
        reg = token_list[0][1]
        consume_token(token_list)
        if not token_list: return Leaf(None, None, False)
        tree = Interior(d, reg, tree, parsePiece(token_list))
    return tree

def parsePiece(token_list):
    tree = parseElement(token_list)
    while token_list and token_list[0][0] == '*':
        d = token_list[0][0]
        reg = token_list[0][1]
        consume_token(token_list)
        if not token_list: return Leaf(None, None, False)
        tree = Interior(d, reg, tree, parseElement(token_list))
    return tree

def parseElement(token_list):
    if token_list:
        if token_list[0][1] == "SYMBOL" and token_list[0][0] != '(':
            return Leaf(None, None, False)
        if token_list[0][0] == '(':
            consume_token(token_list)
            tree = parseExpr(token_list)
            if not token_list:
                return Leaf(None, None, False)
            elif token_list[0][0] == ')':
                consume_token(token_list)
                return tree
            else:
                return Leaf(None, None, False)
        elif token_list[0][1] == "NUMBER" or token_list[0][1] == "IDENTIFIER":
            d = token_list[0][0]
            reg = token_list[0][1]
            consume_token(token_list)
            return Leaf(d, reg, True)

def preorder(tree, space, file_output):
    if tree:
        file_output.write(space + str(tree.getRegex()) + " " + str(tree.getData()) + "\n")
        space = space + "   "
        preorder(tree.getLeftSubTree(), space, file_output)
        if tree.getMiddleSubTree(): preorder(tree.getMiddleSubTree(), space, file_output)
        preorder(tree.getRightSubTree(), space, file_output)

def checkTree(tree):
    if tree:
        if tree.getAST() == False: return False
        if checkTree(tree.getLeftSubTree()) == False: return False
        if tree.getMiddleSubTree() and checkTree(tree.getMiddleSubTree()) == False: return False
        if checkTree(tree.getRightSubTree()) == False: return False

def evaluator(stack, tree):
    stack.append((tree.getData(), tree.getRegex()))
    while len(stack) >= 3 and stack[-1][1] == "NUMBER" and stack[-2][1] == "NUMBER" and stack[-3][1] == "SYMBOL":
        a = int(stack[-2][0])
        b = int(stack[-1][0])
        if stack[-3][0] == "+":
            num = a + b
        elif stack[-3][0] == "-":
            num = a - b
        elif stack[-3][0] == "*":
            num = a * b
        elif stack[-3][0] == "/":
            if b == 0: return
            num = a / b
        else: return
        pop_and_push(stack, int(num))
    if tree.getLeftSubTree(): evaluator(stack, tree.getLeftSubTree())
    if tree.getRightSubTree(): evaluator(stack, tree.getRightSubTree())

def pop_and_push(stack, num):
    stack.pop()
    stack.pop()
    stack.pop()
    stack.append((num, "NUMBER"))

def main():
    test_input = sys.argv[1]
    file_input = open(test_input, "r")
    test_output = sys.argv[2]
    file_output = open(test_output, "w")
    data = file_input.readlines()
    token_list = list()

    for line in data:
        Scanner(line, token_list)

    AST = True
    file_output.write("TOKENS:\n")
    for token in token_list:
        if token[1] == "ERROR":
            AST = False
            file_output.write("ERROR READING: " + token[0] + "\n")
        else: file_output.write(token[1] + " " + token[0] + "\n")

    file_output.write("\nAST:\n")

    if not AST: file_output.write("ERROR: Cannot generate the AST")

    if AST:
        tree = parseExpr(token_list)
        if token_list or checkTree(tree) == False or not tree: AST = False
        else: preorder(tree, "", file_output)

    if not AST:
        file_output.write("ERROR: Cannot generate the AST\n")
        file_output.write("No evaluation\n")
    else:
        stack = []
        evaluator(stack, tree)
        if len(stack) == 1: file_output.write("\nOUTPUT: " + str(stack[0][0]))
        else: file_output.write("\nERROR: Cannot evaluate the AST\n")

    file_input.close()
    file_output.close()

if __name__ == "__main__":
    main()

