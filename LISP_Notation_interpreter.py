"""
This is an interpreter for LISP style arithmetic notations like:
+ 2 * 3 5, which is 2 + 3 * 5
"""

# Token types
#
# EOF (end-of-file) token is used to indicate that
# there is no more input left for lexical analysis
INTEGER, PLUS, MINUS, MULTIPLICATION, DIVISION, EOF, OPEN_BRACKET, CLOSING_BRACKET\
    = 'INTEGER', 'PLUS', 'MINUS', 'MULTIPLICATION', 'DIVISION','EOF', 'OPEN_BRACKET', 'CLOSING_BRACKET'


class Token():
    def __init__(self, type, value):
        # token type: INTEGER, PLUS, MINUS or EOF
        self.type = type
        # token value: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, '+', or None
        self.value = value

    def __str__(self):
        """
        Examples:
            Token(INTEGER, 3)
            Token(PLUS '+')
        """
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=self.value
        )


class Lexer(object):
    def __init__(self, text):
        # client string input, e.g. "4 + 2 * 3 - 6 / 2"
        self.text = text
        # self.pos is an index into self.text
        self.pos = len(text) - 1
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception('Invalid character')

    def advance(self):
        """Advance the `pos` pointer and set the `current_char` variable."""
        self.pos -= 1
        if self.pos < 0:
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self):
        """Return a (multidigit) integer consumed from the input."""
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def get_next_token(self):
        """Lexical analyzer (also known as scanner or tokenizer)

        This method is responsible for breaking a sentence
        apart into tokens. One token at a time.
        """
        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token(INTEGER, self.integer())

            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')

            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '-')

            if self.current_char == '*':
                self.advance()
                return Token(MULTIPLICATION, '*')

            if self.current_char == '/':
                self.advance()
                return Token(DIVISION, '/')

            if self.current_char == '(':
                self.advance()
                return Token(OPEN_BRACKET, '(')

            if self.current_char == ')':
                self.advance()
                return Token(CLOSING_BRACKET, ')')

            self.error()

        return Token(EOF, None)


###############################################################################
#                                                                             #
#  PARSER                                                                     #
#                                                                             #
###############################################################################

class AST(object):
    pass


class BinaryOperation(AST):
    def __init__(self, left, operator, right):
        self.left = left  # left operand Num/BinaryOperation node
        self.token = self.operator = operator  # operator token
        self.right = right  # right operand Num/BinaryOperation node

class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        # set current token to the first token taken from the input
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self):
        """factor : INTEGER"""
        token = self.current_token
        if token.type == INTEGER:
            self.eat(INTEGER)
            return Num(token)

    def expr(self):
        """
        expr   : factor (factor (PLUS | MINUS | MULTIPLICATION | DIVISION) )*
        factor : INTEGER
        meaning it takes the first number (or expression with greater priority/parentheses)'s result
        and continues with the operations of least priority (PLUS and MINUS)
        """
        node = self.factor()
        rightNode = self.factor()

        token = self.current_token  # operator
        if token.type == PLUS:
            self.eat(PLUS)
        elif token.type == MINUS:
            self.eat(MINUS)
        elif token.type == MULTIPLICATION:
            self.eat(MULTIPLICATION)
        elif token.type == DIVISION:
            self.eat(DIVISION)

        node = BinaryOperation(left=node, operator=token, right=rightNode)

        while self.current_token.type == INTEGER:
            rightNode = self.factor()
            token = self.current_token  # operator

            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)
            elif token.type == MULTIPLICATION:
                self.eat(MULTIPLICATION)
            elif token.type == DIVISION:
                self.eat(DIVISION)

            node = BinaryOperation(left=node, operator=token, right=rightNode)


        return node

    def parse(self):
        return self.expr()


class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser

    def visit_BinaryOperation(self, node):
        if node.operator.type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.operator.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.operator.type == MULTIPLICATION:
            return self.visit(node.left) * self.visit(node.right)
        elif node.operator.type == DIVISION:
            return self.visit(node.left) / self.visit(node.right)

    def visit_Num(self, node):
        return node.value

    def interpret(self):
        tree = self.parser.parse()  # create an AST (Abstract Syntax Tree) of the expression
        return self.visit(tree)  # visit that tree and return the result


def main():
    while True:
        try:
            try:
                text = input('spi> ')
            except NameError:  # Python3
                text = input('spi> ')
        except EOFError:  # we've read the input
            break
        if not text:
            continue

        lexer = Lexer(text)
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        result = interpreter.interpret()
        print(result)


if __name__ == '__main__':
    main()