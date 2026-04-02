import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
df = pd.read_csv("emg_data.csv")

# Plot EMG values
plt.plot(df["emg"])

# Labels and title
plt.title("EMG Signal")
plt.xlabel("Samples")
plt.ylabel("EMG Value")

# Show graph
plt.show()
