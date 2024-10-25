import numpy as np
import matplotlib.pyplot as plt

# Import custom algorithms for anomaly detection
import Algorithms.adwin_algorithm as adwin_algorithm
import Algorithms.z_score_algorithm as z_score_algorithm

# Initialize an array to store electricity rates based on data from Colombia, Latin America.
# More info: https://www.valoraanalitik.com/precio-de-energia-en-bolsa-de-colombia-cerro-2023-en-57247-kwh-asi-le-fue-a-enero/
electricity_rate = np.array([])  # Store electricity rates
anomaly_points_x = []  # X-coordinates for detected anomalies
anomaly_points_y = []  # Y-coordinates for detected anomalies

# Create instances of anomaly detection algorithms
adwin_detector = adwin_algorithm.ADWIN()  # Instantiate the ADWIN algorithm for drift detection
z_score_detector = z_score_algorithm.ZScoreDetector()  # Instantiate the Z-Score algorithm for anomaly detection

# Initial time window in months for the simulation
initial_time_window = 3
consumption_slope = 1  # Initial slope for consumption
consumption_growth = 0.0001  # Growth rate for consumption slope

# Function to generate consumption data over time
def generate_consumption_data(time_index, noise_level=0.2, seasonality=365, anomaly_factor=0.7, anomaly_probability=0.01):
    """
    Generates simulated electricity consumption data based on time index, incorporating noise,
    seasonality, and potential anomalies.

    Parameters:
    - time_index: The current time index (in hours)
    - noise_level: Standard deviation of the Gaussian noise added to the consumption
    - seasonality: Number of days that defines the seasonal pattern
    - anomaly_factor: Multiplier to create anomalies
    - anomaly_probability: Probability of generating an anomaly

    Returns:
    - instant_consumption: The generated consumption value for the current time index
    """
    global electricity_rate, consumption_slope

    noise = np.random.normal(0, noise_level)  # Generate random noise

    # Update consumption slope based on growth
    consumption_slope += consumption_slope * consumption_growth

    # Create a consumption pattern using sinusoidal functions to simulate seasonal effects
    sin_0 = time_index * consumption_slope / 1000
    sin_1 = np.sin(2 * np.pi * time_index / seasonality)
    sin_2 = np.sin(np.pi * time_index / seasonality - np.pi / 2)
    sin_3 = np.sin(np.pi * time_index / seasonality - np.pi / 10) / 2
    
    # Combine patterns to form the complete consumption pattern
    consumption_pattern = sin_0 + sin_1 + sin_2 + sin_3 + 4
    
    # Instantaneous consumption includes the consumption pattern plus noise
    instant_consumption = consumption_pattern + noise
    
    # Introduce anomalies with a certain probability
    if np.random.rand() < anomaly_probability:
        instant_consumption += anomaly_factor * np.random.choice([-1, 1]) * np.std(electricity_rate)  # Apply anomaly factor
    
    # Ensure consumption cannot be negative
    if instant_consumption < 0:
        instant_consumption = 0

    # Append the computed consumption value to the electricity rate array
    electricity_rate = np.append(electricity_rate, instant_consumption * 3)  # Scale the consumption

    return instant_consumption

# Generate initial data for the specified time window
for x in range(144 * initial_time_window):
    generate_consumption_data(x)

# Set up for real-time plotting
plt.ion()  # Enable interactive mode for live updates
fig, ax = plt.subplots(figsize=(12, 6))  # Create a new figure and axis for plotting
line, = ax.plot([], [], '-', label='Real', lw=0.5)  # Create an empty line for actual data
empty_line, = ax.plot([], [], '-', color="orange", label='Drift', markersize=4)  # Placeholder for drift detection
anomalies_line, = ax.plot([], [], 'ro', label='Anomalies', markersize=4)  # Plot for detected anomalies

# Configure plot aesthetics
ax.grid()
plt.title("Efficient Data Stream Anomaly Detection (Realtime)")
plt.xlabel("Time (Days)")
plt.ylabel("Electricity Rate (¢/kWh)")

# Initialize the time index
time_index = 144 * initial_time_window

# Main loop for real-time data generation and plotting
while True:
    time_index += 1  # Increment the time index

    # Update the data for the plot
    line.set_xdata(np.arange(len(electricity_rate)))  # X data (time points)
    line.set_ydata(electricity_rate)  # Y data (electricity rates)

    # Generate the instantaneous consumption data
    instant = generate_consumption_data(time_index)

    # Update the ADWIN detector with the new consumption data
    adwin_detector._update(instant)

    # If a drift event is detected, restart the Z-Score measure
    if adwin_detector.drift:
        print(f"Drift detected at day {time_index}")  # Log the drift event
        ax.axvline(len(electricity_rate), lw=1, alpha=1, color='orange')  # Mark the drift on the plot

        z_score_detector.reset()  # Reset the Z-Score detector
        adwin_detector.reset()  # Reset the ADWIN detector

    # Detect anomalies using the Z-Score algorithm
    if z_score_detector.detect_anomaly(instant):
        anomaly_points_x.append(len(electricity_rate) - 1)  # Append the X-coordinate of the anomaly
        anomaly_points_y.append(electricity_rate[-1])  # Append the Y-coordinate of the anomaly

    # Update anomaly points on the plot
    anomalies_line.set_xdata(anomaly_points_x)
    anomalies_line.set_ydata(anomaly_points_y)

    # Adjust the plot limits and redraw
    ax.relim()
    ax.autoscale_view()

    plt.legend(loc='upper left')  # Update the legend
    plt.draw()  # Draw the updated plot
    plt.pause(0.01)  # Pause briefly to allow for real-time visualization
