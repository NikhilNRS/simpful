import os
import pickle
import shutil
import unittest
from tempfile import mkdtemp

from simpful.gp_fuzzy_system.model_saver import load_populations_and_best_models  # Adjust the import according to your module path

class TestLoadPopulationsAndBestModels(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.base_dir = mkdtemp()

        # Create population_dir and best_model_dir inside the base directory
        self.population_dir = os.path.join(self.base_dir, 'population_dir')
        self.best_model_dir = os.path.join(self.base_dir, 'best_model_dir')
        os.makedirs(self.population_dir, exist_ok=True)
        os.makedirs(self.best_model_dir, exist_ok=True)

        # Create subdirectories for population and best_model
        self.subdir_name = '20240602_181742'
        os.makedirs(os.path.join(self.population_dir, self.subdir_name), exist_ok=True)
        os.makedirs(os.path.join(self.best_model_dir, self.subdir_name), exist_ok=True)

        # Create dummy population.pkl and best_model.pkl
        self.population = [{'individual': 'dummy_population'}]
        self.best_model = {'model': 'dummy_best_model'}
        
        with open(os.path.join(self.population_dir, self.subdir_name, 'population.pkl'), 'wb') as pop_file:
            pickle.dump(self.population, pop_file)

        with open(os.path.join(self.best_model_dir, self.subdir_name, 'best_model.pkl'), 'wb') as model_file:
            pickle.dump(self.best_model, model_file)

    def tearDown(self):
        # Remove the temporary directory and all its contents
        shutil.rmtree(self.base_dir)

    def test_load_populations_and_best_models(self):
        # Call the function to test
        data = load_populations_and_best_models(self.base_dir)

        # Check if the loaded data matches the expected dummy data
        self.assertIn(self.subdir_name, data)
        self.assertEqual(data[self.subdir_name]['population'], self.population)
        self.assertEqual(data[self.subdir_name]['best_model'], self.best_model)

    def test_population_dir_not_exists(self):
        # Remove population_dir to simulate the error
        shutil.rmtree(self.population_dir)
        with self.assertRaises(FileNotFoundError):
            load_populations_and_best_models(self.base_dir)

    def test_best_model_dir_not_exists(self):
        # Remove best_model_dir to simulate the error
        shutil.rmtree(self.best_model_dir)
        with self.assertRaises(FileNotFoundError):
            load_populations_and_best_models(self.base_dir)

if __name__ == '__main__':
    unittest.main()