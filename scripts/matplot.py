import gi
import matplotlib.pyplot as plt

gi.require_version("Gtk", "4.0")

# Sample data
x = [1, 2, 3, 4, 5]
y = [2, 3, 5, 7, 11]

# Create a new figure
plt.figure()

# Plot the data
plt.plot(x, y, marker="o")

# Add a title and labels
plt.title("Simple Line Plot")
plt.xlabel("X-axis")
plt.ylabel("Y-axis")

# Show the plot
plt.show()
