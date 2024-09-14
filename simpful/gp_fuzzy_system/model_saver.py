import os
import pickle
import logging
from datetime import datetime
import glob

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# File handler to log to a file
file_handler = logging.FileHandler('load_populations.log')
file_handler.setLevel(logging.DEBUG)

# Stream handler to output to console
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

# Formatter for log messages
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Add handlers if not already added
if not logger.hasHandlers():
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

def load_saved_individuals(directory, num_individuals=None):
    """
    Load a specified number of individuals from the saved pickle files in the given directory.

    Parameters:
    - directory: The directory containing the saved pickle files.
    - num_individuals: The number of individuals to load. If None, loads all individuals.

    Returns:
    - A list of loaded individuals.
    """
    saved_individuals = []
    pickle_files = glob.glob(os.path.join(directory, "*.pkl"))

    for i, file in enumerate(pickle_files):
        if num_individuals is not None and i >= num_individuals:
            break
        with open(file, "rb") as f:
            individual = pickle.load(f)
            saved_individuals.append(individual)

    return saved_individuals


def save_to_timestamped_dir(obj, base_dir, filename):
    """
    Saves the given object to a timestamped directory.

    Parameters:
    - obj: The object to save (e.g., model, population)
    - base_dir: The base directory where the timestamped folder will be created
    - filename: The name of the file to save the object as

    Returns:
    - The path of the directory where the object was saved
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir_path = os.path.join(base_dir, timestamp)
    os.makedirs(dir_path, exist_ok=True)

    file_path = os.path.join(dir_path, filename)
    with open(file_path, "wb") as f:
        pickle.dump(obj, f)

    return dir_path


def load_populations_and_best_models(base_directory):
    """
    Load all populations and best models from the respective directories under the base directory.

    Parameters:
    - base_directory: The base directory containing 'population_dir' and 'best_model_dir'.

    Returns:
    - A dictionary with directory names as keys and another dictionary as values,
      which contains 'population' and 'best_model' as keys.
    """
    # Log the current working directory
    logger.debug(f"Current working directory: {os.getcwd()}")

    # Check if the base directory exists
    if not os.path.exists(base_directory):
        logger.error(f"Base directory not found: {base_directory}")
        raise FileNotFoundError(f"Base directory not found: {base_directory}")
    
    logger.info(f"Base directory being used: {base_directory}")

    data = {}

    population_dir = os.path.join(base_directory, "population_dir")
    best_model_dir = os.path.join(base_directory, "best_model_dir")

    # Check if population and best model directories exist
    if not os.path.exists(population_dir):
        logger.error(f"Population directory not found: {population_dir}. Please check that it exists and is accessible.")
        raise FileNotFoundError(f"Population directory not found: {population_dir}")
    if not os.path.exists(best_model_dir):
        logger.error(f"Best model directory not found: {best_model_dir}. Please check that it exists and is accessible.")
        raise FileNotFoundError(f"Best model directory not found: {best_model_dir}")

    population_subdirs = [
        d
        for d in os.listdir(population_dir)
        if os.path.isdir(os.path.join(population_dir, d))
    ]
    best_model_subdirs = [
        d
        for d in os.listdir(best_model_dir)
        if os.path.isdir(os.path.join(best_model_dir, d))
    ]

    for subdirectory in population_subdirs:
        population_path = os.path.join(population_dir, subdirectory, "population.pkl")
        best_model_path = os.path.join(best_model_dir, subdirectory, "best_model.pkl")

        if os.path.exists(population_path) and os.path.exists(best_model_path):
            with open(population_path, "rb") as pop_file:
                population = pickle.load(pop_file)
            with open(best_model_path, "rb") as model_file:
                best_model = pickle.load(model_file)

            data[subdirectory] = {"population": population, "best_model": best_model}
        else:
            logger.warning(f"Population or best model file not found in subdirectory: {subdirectory}")

    return data

# Example usage:
# base_dir = 'path_to_your_base_directory'
# loaded_data = load_populations_and_best_models(base_dir)
# print(loaded_data)
