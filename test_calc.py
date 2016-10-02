import unittest
from calc import Interpreter


class TestArithmeticOperations(unittest.TestCase):

    def _pass_to_interpreter(self, text: str):
        """ this method passes the text to the interpreter and returns the result"""
        interpreter = Interpreter(text)
        return interpreter.ar_expr()

    def test_addition(self):
        result = self._pass_to_interpreter("4+4+1+0")
        self.assertEqual(result, 9)

    def test_subtraction(self):
        result = self._pass_to_interpreter("4-4-1")
        self.assertEqual(result, -1)

    def test_multiplication(self):
        result = self._pass_to_interpreter("4*4*4")
        self.assertEqual(result, 64)

    def test_integer_division(self):
        result = self._pass_to_interpreter("4/3")
        self.assertEqual(result, 1)

    def test_mix(self):
        result = self._pass_to_interpreter("4-1*4+12/5+2*2")
        self.assertEqual(result, 6)

unittest.main()