import os
import sys

here = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(here)

import unittest
from src.greeting import greeting

class TestGreeting(unittest.TestCase):
    def test_greeting(self):
        """
        Test the syntax of the greeting.
        """
        try:
            # Try to evaluate the prompt as a valid string
            eval(f'"""{greeting}"""')
        except (SyntaxError, ValueError):
            self.fail("Greeting has invalid syntax.")

if __name__ == '__main__':
    unittest.main()
