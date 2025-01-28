import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error

# 1. Function to calculate marine POC ratio based on band ratios
def calculate_marine_poc_ratio(Rrs443, Rrs492, Rrs704, Rrs665, method=1):
    """
    Calculates the marine POC ratio based on the equation:
    marine_ratio = (Rrs(443)/Rrs(492)) / (Rrs(704)/Rrs(665))
    """
    
    marine_ratio = (Rrs443 / Rrs492) / (Rrs704 / Rrs665)
    return marine_ratio

# 2. Function to estimate POC sources using the retrieval algorithm
def estimate_poc_sources(Rrs443, Rrs492, Rrs704, Rrs665):
    """
    Estimates the proportion of marine POC using the model:
    y = 1.8549 * x - 0.8781
    Where x = calculate_marine_poc_ratio(...)
    """
    marine_ratio = calculate_marine_poc_ratio(Rrs443, Rrs492, Rrs704, Rrs665)
    marine_poc = 1.8549 * marine_ratio - 0.8781
    # Ensure values are bounded between 0 and 1
    return np.clip(marine_poc, 0, 1)

# 3. Function to evaluate the algorithm's performance
def evaluate_algorithm(estimated, measured):
    """
    Compares estimated values with measured values using MAPE and RMSE.
    """
    mape = mean_absolute_percentage_error(measured, estimated) * 100
    rmse = np.sqrt(mean_squared_error(measured, estimated))
    return mape, rmse

# 4. Function to visualize the results
def plot_results(measured, estimated):
    """
    Plots measured vs. estimated values to visualize accuracy.
    """
    plt.figure(figsize=(8, 6))
    plt.scatter(measured, estimated, c="blue", label="Estimation")
    plt.plot([0, 1], [0, 1], "r--", label="Ideal Fit")
    plt.xlabel("Measured Marine POC Ratio")
    plt.ylabel("Estimated Marine POC Ratio")
    plt.title("Measured vs Estimated Marine POC Ratios")
    plt.legend()
    plt.grid()
    plt.show()

# Example usage
if __name__ == "__main__":
    # Example data (Rrs values and measured ratios for testing)
    Rrs443 = np.array([0.01, 0.015, 0.012])
    Rrs492 = np.array([0.02, 0.018, 0.017])
    Rrs704 = np.array([0.03, 0.033, 0.031])
    Rrs665 = np.array([0.025, 0.022, 0.024])

    # Measured marine POC ratios (for comparison)
    measured_ratios = np.array([0.7, 0.6, 0.65])

    # Calculate estimated ratios
    estimated_ratios = estimate_poc_sources(Rrs443, Rrs492, Rrs704, Rrs665)

    # Evaluate the algorithm
    mape, rmse = evaluate_algorithm(estimated_ratios, measured_ratios)
    print(f"MAPE: {mape:.2f}%")
    print(f"RMSE: {rmse:.4f}")

    # Plot the results
    plot_results(measured_ratios, estimated_ratios)
