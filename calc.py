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


class Lexer():
    def __init__(self, text):
        # client string input, e.g. "3+5"
        self.text = text
        # self.pos is an index into self.text
        self.pos = 0
        # current token instance
        self.current_token = None

    def get_next_token(self):
        """Scanner
        This method is responsible for breaking a sentence
        apart into tokens. One token at a time.
        """
        text = self.text

        # is self.pos index past the end of the self.text ?
        # if so, then return EOF token because there is no more input to process
        if self.pos > len(text) - 1:
            return Token(EOF, None)

        # get a character at the position self.pos and decide what token to create based on the single character
        current_char = text[self.pos]

        # if the character is a digit then convert it to integer using the read_integer func, create an INTEGER token,
        if current_char.isdigit():
            return Token(INTEGER, self.read_integer(text))
        elif current_char == '+':
            token = Token(PLUS, current_char)
            self.advance_pos()
            return token
        elif current_char == '-':
            token = Token(MINUS, current_char)
            self.advance_pos()
            return token
        elif current_char == '/':
            token = Token(DIVISION, current_char)
            self.advance_pos()
            return token
        elif current_char == '*':
            token = Token(MULTIPLICATION, current_char)
            self.advance_pos()
            return token
        elif current_char in '()':
            if current_char == '(':
                token = Token(OPEN_BRACKET, current_char)
            else:
                token = Token(CLOSING_BRACKET, current_char)

            self.advance_pos()
            return token
        elif current_char == ' ':
            # we skip whitespaces
            self.advance_pos()
            return self.get_next_token()  # recursion until we get to a character that's not a whitespace

        self.error()

    def read_integer(self, text):
        """ Reads a multidigit integer from the input """
        current_char = '0'  # '0' so as to pass the isdigit() test to get in the while loop,
        # the 0 will be removed once casted to an int

        while current_char.isdigit() and text[self.pos].isdigit():
            current_char += text[self.pos]
            self.advance_pos()
            if self.pos == len(text):
                break

        return int(current_char)

    def advance_pos(self):
        """ increments the pos variable that points where we are in the text"""
        self.pos += 1

    def error(self):
        raise Exception('Error parsing input!')


class Interpreter():
    def __init__(self, text):
        # current token instance
        self.current_token = None
        self.lexer = Lexer(text)
        self.open_brackets = 0
        self.closed_brackets = 0

    def validate_and_advance_token(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def error(self):
        raise Exception('Error parsing input!')

    def ar_expr(self):
        """ar_expr -> INTEGER PLUS INTEGER
            Interprets the arithmetic expression and returns a result
        """
        # set current token to the first token taken from the input
        self.current_token = self.lexer.get_next_token()

        # we expect the current token to be an integer
        left = self.current_token
        if left.type == OPEN_BRACKET:
            self.open_brackets += 1
            return self.ar_expr()
        self.validate_and_advance_token(INTEGER)

        result = self.continue_ar_expr(left)

        if self.open_brackets != self.closed_brackets:
            self.error()

        return result

    def continue_ar_expr(self, left: Token):
        """
        This function continues the arithmetic expression with a given left token, what we're left to do is
        get the operator and the right token. We also use recursion to further continue the expression if it's not as
        simple as 3 + 3
        """
        operation = self.current_token.type  # 'PLUS, MINUS, MULTIPLICATION, DIVISION, EOF'
        
        if operation == EOF:
            # we've reached the end of the expression, there's no further math to do
            return left.value
        elif operation == PLUS:
            self.validate_and_advance_token(PLUS)
        elif operation == MINUS:  # operation == MINUS
            self.validate_and_advance_token(MINUS)
        elif operation == MULTIPLICATION:
            self.validate_and_advance_token(MULTIPLICATION)
        elif operation == DIVISION:  # operation == DIVISION
            self.validate_and_advance_token(DIVISION)

        right = self.current_token
        if right.type == INTEGER:
            self.validate_and_advance_token(INTEGER)
        elif right.type == OPEN_BRACKET:
            #self.validate_and_advance_token(OPEN_BRACKET)
            self.open_brackets += 1
            right_value = self.ar_expr()  # evaluate the expression in the brackets as a new expression altogether
            right = Token(INTEGER, right_value)
        elif right.type == CLOSING_BRACKET:
            self.validate_and_advance_token(CLOSING_BRACKET)
            self.closed_brackets += 1
            return left.value
        # after the above call, the token might be set to EOF (end of file) or another operator

        if operation == PLUS:
            # we use recursion
            result = left.value + self.continue_ar_expr(Token(INTEGER, right.value))
        elif operation == MINUS:
            result = left.value + self.continue_ar_expr(Token(INTEGER, -right.value))
        elif operation == MULTIPLICATION:
            result = left.value * right.value
        else:  # operation == DIVISION
            # we're processing integers so we'll use integer division
            result = left.value // right.value

        return self.continue_ar_expr(Token(INTEGER, result))


def main():
    while True:
        try:
            text = input('calc> ')
        except EOFError:
            break
        if not text:
            continue
        interpreter = Interpreter(text)
        result = interpreter.ar_expr()
        print(result)


if __name__ == '__main__':
    main()