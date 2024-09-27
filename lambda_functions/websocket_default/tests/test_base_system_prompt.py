import os
import sys

here = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(here)

import unittest
from src.base_system_prompt import base_system_prompt

class TestBaseSystemPrompt(unittest.TestCase):
    def test_base_system_prompt_syntax(self):
        """
        Test the syntax of the base_system_prompt.
        """
        try:
            # Try to evaluate the prompt as a valid string
            eval(f'"""{base_system_prompt}"""')
        except (SyntaxError, ValueError):
            self.fail("Base system prompt has invalid syntax.")

if __name__ == '__main__':
    unittest.main()

