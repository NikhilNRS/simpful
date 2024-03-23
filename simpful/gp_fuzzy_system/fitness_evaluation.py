import numpy as np

def weighted_rmse(actual, predicted):
    """Calculate the Root Mean Squared Error."""
    return np.sqrt(np.mean((predicted - actual) ** 2))

def prediction_stability(predicted):
    """Evaluate prediction stability over time."""
    # Example: Use standard deviation as a measure of stability
    return np.std(predicted)

def financial_utility(actual, predicted):
    """Estimate the financial utility of the predictions."""
    # Placeholder for financial utility calculation
    # Example: Calculate the return on investment (ROI) based on predictions
    roi = np.sum((predicted - actual) / actual)
    return roi

def evaluate_fitness(system, historical_prices, predictions, weights={'rmse': 0.5, 'stability': 0.3, 'utility': 0.2}):
    """
    A complex fitness function that considers predictive accuracy (RMSE), 
    stability of predictions over time, and financial utility.
    """
    rmse_score = weighted_rmse(historical_prices, predictions)
    stability_score = prediction_stability(predictions)
    utility_score = financial_utility(historical_prices, predictions)

    # Normalize or standardize scores if necessary
    # Placeholder for normalization: Assume scores are already comparable

    # Calculate the weighted sum of scores as the final fitness
    fitness = (weights['rmse'] * rmse_score) + \
              (weights['stability'] * (1 - stability_score)) + \
              (weights['utility'] * utility_score)

    return fitness
