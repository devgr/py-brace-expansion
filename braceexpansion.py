# parser for `echo a{b,c}` expansion
"""
expression = {[symbol], [grouping]}
grouping = '{', expression, {',', expression}, '}'
symbol = '([a-z][A-Z][0-9])+'
"""
import sys
import re
import logging

logger = logging.getLogger(__name__)

class Tokens:
    StartGroup = 'StartGroup'
    EndGroup = 'EndGroup'
    ListDelimeter = 'ListDelimeter'


class Value:
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)
    def __repr__(self):
        return self.__str__()


def lex(text):
    stream = []
    symbol_pattern = re.compile(r'[A-Za-z0-9]+')
    while text:
        m = symbol_pattern.match(text)
        if m:
            stream.append(Value(m[0]))
            text = text[len(m[0]):]
            continue
        
        if text[0] == '{':
            stream.append(Tokens.StartGroup)
            text = text[1:]
            continue

        if text[0] == '}':
            stream.append(Tokens.EndGroup)
            text = text[1:]
            continue

        if text[0] == ',':
            stream.append(Tokens.ListDelimeter)
            text = text[1:]
            continue

        print('Error parsing starting at:', text)
        return False
    return stream

class Root:
    def __init__(self):
        self.items = []
    def eval(self):
        # Root is a dummy element to hold an expression.
        assert len(self.items) == 1
        return self.items[0].eval()
    def __str__(self):
        return 'Root'
    def __repr__(self):
        return self.__str__()

class Expression:
    def __init__(self, parent):
        self.items = []
        self.parent = parent

    def looper(self, la, rest):
        if len(rest) == 0:
            return la
        lb = rest[0]
        temp_results = []
        for a in la:
            for b in lb:
                temp_results.append(a + b)
        return self.looper(temp_results, rest[1:])

    def eval(self):
        inner_values = [item.eval() for item in self.items]
        assert len(inner_values) > 0

        starter = list(inner_values[0])
        results = self.looper(starter, inner_values[1:])

        return results

    def __str__(self):
        return 'Expression'
    def __repr__(self):
        return self.__str__()

class Symbol:
    def __init__(self, value):
        self.items = []
        self.value = value
    def eval(self):
        return self.value
    def __str__(self):
        return 'Symbol: ' + str(self.value)
    def __repr__(self):
        return self.__str__()

class Group:
    def __init__(self, parent):
        self.items = []
        self.parent = parent
    def eval(self):
        inner_values = [item.eval() for item in self.items]
        # Bring the results up a level
        results = []
        for l in inner_values:
            for v in l:
                results.append(v)

        return results

    def __str__(self):
        return 'Group'
    def __repr__(self):
        return self.__str__()

class SemanticAnalyzer:
    def __init__(self, token_stream):
        self.token_stream = token_stream

    def get_token(self):
        if self.token_stream:
            return self.token_stream.pop(0)
        return None

    def peek(self):
        if self.token_stream:
            return self.token_stream[0]
        return None

    def parse(self):
        self.ast = Root()
        self.expression(self.ast)
        return self.ast

    def expression(self, parent):
        node = Expression(parent)
        parent.items.append(node)
        token = self.peek()

        while type(token) is Value or token is Tokens.StartGroup:
            if type(token) is Value:
                self.get_token()
                node.items.append(Symbol(token.value))

            elif token is Tokens.StartGroup:
                self.get_token() # eat the {
                self.group(node)
            
            token = self.peek()

    def group(self, parent):
        node = Group(parent)
        parent.items.append(node)

        self.expression(node)

        token = self.peek()

        while token is Tokens.ListDelimeter:
            self.get_token() # eat the ,
            self.expression(node)
            token = self.peek()

        if token is Tokens.EndGroup:
            self.get_token() # eat the }
            return
        # else error

    def pre_order_traversal(self, node, indent):
        tabs = ''.join(['\t' for i in range(indent)])
        logger.debug('{}{}'.format(tabs, node))

        for item in node.items:
            self.pre_order_traversal(item, indent + 1)

    def debug_tree(self):
        self.pre_order_traversal(self.ast, 0)


def expand(text):
    logger.debug(text)
    token_stream = lex(text)
    logger.debug(token_stream)
    if token_stream:
        analyzer = SemanticAnalyzer(token_stream)
        ast = analyzer.parse()
        analyzer.debug_tree()
        value = ast.eval()
        return value or []
    return []

def output(result):
    print(*result)

if __name__ == '__main__':
    logging.basicConfig()
    text = sys.argv[1]
    if text == '-d':
        logger.setLevel(logging.DEBUG)
        text = sys.argv[2]
    result = expand(text)
    output(result)
