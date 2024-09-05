import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from policyengine_core.charts import format_fig

# Load the data
@st.cache_data
def load_data():
    return pd.read_csv("or_rebate.csv")

data = load_data()

st.title("Oregon Rebate Impact on Poverty")

# Add a toggle for taxability
taxability = st.toggle("Show taxable scenario", value=False)

# Define colors for age groups
colors = {
    "0-17": "#003366",     # Dark blue
    "18-64": "#0066cc",    # Medium blue
    "65+": "#4d94ff",      # Light blue
    "Overall": "#99ccff",  # Very light blue
}

# Create the plot
fig = go.Figure()

# Store final y-values for label positioning
final_y_values = {}

# Initialize min and max y values
y_min, y_max = float('inf'), float('-inf')

# Add traces for each age group
for age_group in colors.keys():
    age_data = data[data['age_group'] == age_group]
    
    y_column = 'relative_poverty_reduction_taxable' if taxability else 'relative_poverty_reduction'
    
    trace = go.Scatter(
        x=age_data['year'], 
        y=age_data[y_column],
        mode='lines',
        name=age_group,
        line=dict(color=colors[age_group], width=2),
        showlegend=False
    )
    fig.add_trace(trace)
    final_y_values[age_group] = trace.y[-1]
    
    # Update y_min and y_max
    y_min = min(y_min, min(trace.y))
    y_max = max(y_max, max(trace.y))

# Add some padding to the y-axis range
y_range = y_max - y_min
y_min -= 0.1 * y_range
y_max += 0.1 * y_range

# Function to adjust label positions
def adjust_label_positions(positions, min_gap=0.02):
    sorted_items = sorted(positions.items(), key=lambda x: x[1])
    adjusted = {}
    for i, (key, value) in enumerate(sorted_items):
        if i == 0:
            adjusted[key] = value
        else:
            prev_key = sorted_items[i-1][0]
            if value - adjusted[prev_key] < min_gap:
                adjusted[key] = adjusted[prev_key] + min_gap
            else:
                adjusted[key] = value
    return adjusted

# Adjust label positions
adjusted_positions = adjust_label_positions(final_y_values)

# Update layout
fig.update_layout(
    title='Oregon Rebate Impact on Poverty by Age Group Over Time',
    xaxis_title='Year',
    yaxis_title='Poverty Reduction (%)',
    height=650,
    width=750,
    margin=dict(r=80, l=50, b=70, t=100),
    legend=dict(
        orientation="v",
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=1.02
    )
)

# Update x-axis
fig.update_xaxes(
    tickvals=[2025, 2026, 2027],
    ticktext=["2025", "2026", "2027"],
    range=[2024.8, 2027.15]
)

# Update y-axis
fig.update_yaxes(tickformat='.0%', range=[y_min, y_max])

# Update hover template
fig.update_traces(
    hovertemplate='Year: %{x}<br>Age Group: %{data.name}<br>Poverty Reduction: %{y:.2%}<extra></extra>'
)

# Add labels closer to the lines with adjusted positions
for label, y_pos in adjusted_positions.items():
    fig.add_annotation(
        x=2027.05,
        y=y_pos,
        text=label,
        showarrow=False,
        xanchor="left",
        yanchor="middle",
        font=dict(size=8, color=colors[label])
    )

# Apply the format_fig function
fig = format_fig(fig)

# Display the plot in Streamlit
st.plotly_chart(fig)

# Display the data table
st.subheader("Data Table")
st.dataframe(data)
