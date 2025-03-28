import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Set the page title
st.set_page_config(page_title="Basic Dashboard", # Title that appears on the browser tab
                   layout="centered") # "wide" makes use of full browser width; alternative: "centered"

#### GENERATING A SIMPLE DATASET ####
# Create a sample dataset
np.random.seed(42)  # For reproducibility

data_db = pd.DataFrame({
    "Category": np.random.choice(["A", "B", "C", "D"], size=100),
    "Value": np.random.randint(10, 100, size=100),
    "Date": pd.date_range(start="2024-01-01", periods=100, freq="D")
})
data_db.head()

#### SETTING UP DASHBOARD LAYOUT ####

# Title and description
st.title("Basic Streamlit Dashboard") # Displays a large title at the top of the app
st.markdown("This is a very rudimentary dashboard that uses Plotly plots. You can add additional text here...") # Displays a markdown text description

# Sidebar filters 
# (1) Creates a multi-select dropdown to filter data based on category
category_filter = st.sidebar.multiselect(
    "Select Category", # Label shown in sidebar
    options=data_db["Category"].unique(), # Unique categories from the dataset
    default=data_db["Category"].unique()) # Default selection includes all categories

# (2) Creates a date range selector to filter data based on date
date_range = st.sidebar.date_input(
    "Select Date Range", # Label for the date input
    [data_db["Date"].min(), data_db["Date"].max()], # Default selection is full range
    min_value=data_db["Date"].min(), # Minimum selectable date
    max_value=data_db["Date"].max() # Maximum selectable date
)

# Filter the dataset based on sidebar inputs
filtered_data = data_db[
    (data_db["Category"].isin(category_filter)) & # Filters rows where category is in the selected list
    (data_db["Date"] >= pd.to_datetime(date_range[0])) & # Filters rows where date is greater than or equal to start date
    (data_db["Date"] <= pd.to_datetime(date_range[1])) # Filters rows where date is less than or equal to end date
]

#### PLOTS WITH PLOTLY ####

# Plot 1: bar chart to show the average value for each category
fig_bar = px.bar(filtered_data.groupby("Category")["Value"].mean().reset_index(),
                 x="Category", y="Value", title="Average Value by Category",
                 color="Category", text_auto=True)
st.plotly_chart(fig_bar, theme="streamlit", use_container_width=True) # Display the bar chart with full width

#Plot 2: line chart to show the trend of values over time
fig_line = px.line(filtered_data, x="Date", y="Value", title="Value Trend Over Time", markers=True)
st.plotly_chart(fig_line, theme="streamlit", use_container_width=True) # Display the line chart

#Plot 3: box plot to show the distribution of values by category
fig_box = px.box(filtered_data, x="Category", y="Value", title="Value Distribution by Category")
st.plotly_chart(fig_box, theme="streamlit", use_container_width=True) # Display the box plot

#Plot 4: scatter plot to show value distribution over time
fig_scatter = px.scatter(filtered_data, x="Date", y="Value", color="Category",
                         title="Scatter Plot of Value Over Time", size_max=10)
st.plotly_chart(fig_scatter, theme="streamlit", use_container_width=True) # Display the box plot
