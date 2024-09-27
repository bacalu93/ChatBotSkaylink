import os
import sys

here = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(here)

import unittest
from src.secondary_system_prompt import secondary_system_prompt

class TestSecondarySystemPrompt(unittest.TestCase):
    def test_secondary_system_prompt(self):
        """
        Test the syntax of the secondary system prompt.
        """
        try:
            # Try to evaluate the prompt as a valid string
            eval(f'"""{secondary_system_prompt}"""')
        except (SyntaxError, ValueError):
            self.fail("Secondary system prompt has invalid syntax.")

if __name__ == '__main__':
    unittest.main()
