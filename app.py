import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from policyengine_core.charts import format_fig

# Load the data
@st.cache_data
def load_data():
    data = pd.read_csv("or_rebate.csv")
    data['year'] = data['year'].astype(int)
    return data

data = load_data()

st.title("Oregon Rebate Impact on Poverty")

# Add toggles for taxability and flat tax offset
taxability = st.toggle("Federally taxable", value=False)
flat_tax_offset = st.toggle("Offset by flat tax*", value=False)

# Define colors for age groups
colors = {
    "0-17": "#003366",     # Dark blue
    "18-64": "#0066cc",    # Medium blue
    "65+": "#4d94ff",      # Light blue
    "Overall": "#99ccff",  # Very light blue
}

# Determine which reform to use based on toggle states
def get_reform_name(taxable, flat_tax):
    if taxable and flat_tax:
        return 'reform_taxable_flat_tax'
    elif taxable and not flat_tax:
        return 'reform_taxable'
    elif not taxable and flat_tax:
        return 'reform_flat_tax'
    else:
        return 'reform'

reform_name = get_reform_name(taxability, flat_tax_offset)

# Filter data for the selected reform
filtered_data = data[data['reform'] == reform_name]

# Create the plot
fig = go.Figure()

# Store final y-values for label positioning
final_y_values = {}

# Add traces for each age group
for age_group in colors.keys():
    age_data = filtered_data[filtered_data['age_group'] == age_group]
    
    trace = go.Scatter(
        x=age_data['year'], 
        y=age_data['relative_poverty_reduction'],
        mode='lines',
        name=age_group,
        line=dict(color=colors[age_group], width=2),
        showlegend=False,
        hovertemplate='Year: %{x}<br>' +
                      'Age Group: %{data.name}<br>' +
                      'Poverty Reduction: %{y:.2%}<br>' +
                      'Baseline Poverty Rate: %{customdata[0]:.2%}<br>' +
                      'Reformed Poverty Rate: %{customdata[1]:.2%}<br>' +
                      '<extra></extra>',
        customdata=age_data[['baseline_poverty_rate', 'reform_poverty_rate']]
    )
    fig.add_trace(trace)
    final_y_values[age_group] = age_data['relative_poverty_reduction'].iloc[-1]

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
scenario_description = f"{'Federally taxable' if taxability else 'Not taxable'}, {'Offset by flat tax' if flat_tax_offset else 'Not offset by flat tax'}"
fig.update_layout(
    title=f'Oregon Rebate Impact on Poverty by Age Group Over Time<br><sub>{scenario_description}</sub>',
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

# Update y-axis with fixed range from -55% to 5%, with 5% at the top
fig.update_yaxes(
    tickformat='.0%',
    range=[-0.55, 0.05],  # Fixed range from -55% to 5%, with 5% at the top
    tickvals=[0.05, 0, -0.1, -0.2, -0.3, -0.4, -0.5],
    ticktext=['', '0%', '-10%', '-20%', '-30%', '-40%', '-50%']
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

# Add flat tax rates as a note at the bottom
st.markdown("""
<small>
* Flat Tax Rates
- 2025: 1.98%
- 2026: 2.53%
- 2027: 2.55%
</small>
""", unsafe_allow_html=True)