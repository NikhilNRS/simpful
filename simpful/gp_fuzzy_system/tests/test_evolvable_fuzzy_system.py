import sys
from pathlib import Path
import unittest
# Add the parent directory to sys.path
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)

from evolvable_fuzzy_system import EvolvableFuzzySystem

class TestEvolvableFuzzySystem(unittest.TestCase):

    def test_initialization(self):
        # Initialize the system
        system = EvolvableFuzzySystem()
        
        # Check default mutation_rate
        self.assertEqual(system.mutation_rate, 0.01)
        
        # Verify the system starts with no rules
        self.assertEqual(len(system._rules), 0)
        
        # Check that fitness_score is None
        self.assertIsNone(system.fitness_score)

# More tests can be added here

if __name__ == '__main__':
    unittest.main()

# Run like this
# python -m unittest test_evolvable_fuzzy_system.py