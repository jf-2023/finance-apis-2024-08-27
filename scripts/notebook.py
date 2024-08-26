import matplotlib.pyplot as plt
import pandas as pd

# Create a simple DataFrame
data = {
    "Year": [2010, 2011, 2012, 2013, 2014],
    "Sales": [100, 150, 200, 250, 300],
    "Profit": [10, 20, 30, 40, 50],
}

df = pd.DataFrame(data)

# Display the DataFrame
print(df)

# Set the 'Year' column as the index (optional)
df.set_index("Year", inplace=True)

# Plot the DataFrame
df.plot(kind="line")

# Customize the plot
plt.title("Sales and Profit Over Time")
plt.xlabel("Year")
plt.ylabel("Values")
plt.grid(True)

# Show the plot
plt.show()
