import sys
import os
import optuna
import pandas as pd
import numpy as np
import skfuzzy as fuzz
import importlib.util
from simpful import FuzzySet, Triangular_MF, Gaussian_MF, Sigmoid_MF, LinguisticVariable
from simpful.gp_fuzzy_system.linguistic_variable_store import LocalLinguisticVariableStore
from tqdm.auto import tqdm

class FuzzyLinguisticVariableProcessor:
    def __init__(self, file_path, terms_dict_path, verbose=False, exclude_columns=None, mf_type='sigmoid'):
        self.file_path = file_path
        self.terms_dict_path = terms_dict_path
        self.verbose = verbose
        self.exclude_columns = exclude_columns if exclude_columns else []
        self.mf_type = mf_type
        self.data = pd.read_csv(self.file_path)
        self.terms_dict = self._load_terms_dict()

    def _load_terms_dict(self):
        """Load the terms dictionary from the given file path."""
        spec = importlib.util.spec_from_file_location("terms_dict", self.terms_dict_path)
        terms_dict_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(terms_dict_module)
        return terms_dict_module.terms_dict

    def create_linguistic_variable(self, column_data, column_name, terms, n_clusters, mf_type):
        """Create fuzzy linguistic variable using clustering."""
        col_data = column_data.reshape(1, -1)
        cntr, u, _, _, _, _, _ = fuzz.cluster.cmeans(
            col_data, c=n_clusters, m=2, error=0.005, maxiter=1000, init=None)
        centers = sorted(cntr.flatten())
        
        low = min(col_data.flatten())
        high = max(col_data.flatten())
        control_points = [low] + centers + [high]
        control_points = self.adjust_control_points(control_points)
        
        FS_list = self.define_fuzzy_sets(control_points, terms, mf_type)
        if FS_list:
            LV = LinguisticVariable(FS_list=FS_list, universe_of_discourse=[low, high], concept=column_name)
            return LV
        return None

    def adjust_control_points(self, control_points):
        """Adjust control points to avoid duplicates."""
        unique_points = sorted(set(control_points))
        if len(unique_points) < len(control_points):
            for i in range(1, len(unique_points)):
                if unique_points[i] - unique_points[i-1] == 0:
                    unique_points[i] += 1e-5  # Small adjustment to ensure unique points
                    if self.verbose:
                        print(f"Adjusted control point: {unique_points[i-1]} to {unique_points[i]}")
        return unique_points

    def define_fuzzy_sets(self, control_points, terms, mf_type):
        """Define fuzzy sets based on control points and membership function type."""
        FS_list = []
        for i in range(len(terms)):
            try:
                if mf_type == 'triangular':
                    FS_list.append(FuzzySet(function=Triangular_MF(control_points[i], control_points[i+1], control_points[i+2]), term=terms[i]))
                elif mf_type == 'gaussian':
                    mean = control_points[i+1]
                    sigma = (control_points[i+2] - control_points[i]) / 2
                    FS_list.append(FuzzySet(function=Gaussian_MF(mean, sigma), term=terms[i]))
                elif mf_type == 'sigmoid':
                    mean = control_points[i+1]
                    slope = (control_points[i+2] - control_points[i]) / 2
                    FS_list.append(FuzzySet(function=Sigmoid_MF(mean, slope), term=terms[i]))
            except IndexError:
                if self.verbose:
                    print(f"Skipping term '{terms[i]}' due to insufficient control points.")
                break
        return FS_list

    def process_dataset(self, trial=None):
        """Process the dataset to create linguistic variables. Optuna trial can be used for optimization."""
        store = LocalLinguisticVariableStore()
        
        for column in self.data.columns:
            if column in self.exclude_columns:
                if self.verbose:
                    print(f"Excluding column '{column}'")
                continue
            if self.data[column].dtype not in [np.float64, np.int64]:
                continue

            # Use Optuna to suggest the number of terms, default to terms_dict values if trial is None
            default_terms = self.terms_dict.get(column, ['low', 'medium', 'high'])
            num_terms = trial.suggest_int(f'num_terms_{column}', 2, len(default_terms)) if trial else len(default_terms)
            terms = default_terms[:num_terms]

            # Use Optuna to suggest the number of clusters and membership function type
            n_clusters = trial.suggest_int(f'n_clusters_{column}', 2, num_terms) if trial else num_terms
            mf_type = trial.suggest_categorical(f'mf_type_{column}', ['triangular', 'gaussian', 'sigmoid']) if trial else self.mf_type

            LV = self.create_linguistic_variable(self.data[column].values, column, terms, n_clusters, mf_type)
            if LV:
                store.add_variable(column, LV)
        
        return store

# Optuna integration for optimizing the process
def create_objective(processor):
    def objective(trial):
        # Process dataset with the Optuna trial object to suggest terms, clusters, and MF types
        variable_store = processor.process_dataset(trial)
        return len(variable_store.variables)  # Return the number of variables as the optimization metric
    return objective

# Function to run Optuna optimization
def run_optuna(processor, n_trials=50):
    """Run Optuna optimization for a specified number of trials."""
    objective_function = create_objective(processor)
    study = optuna.create_study(direction='maximize')  # Maximize the number of linguistic variables created
    with tqdm(total=n_trials, desc="Optimizing Linguistic Variables") as pbar:
        def callback(study, trial):
            pbar.update(1)
        study.optimize(objective_function, n_trials=n_trials, callbacks=[callback])
    print("Best hyperparameters:", study.best_trial.params)
