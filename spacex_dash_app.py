# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

#for Task 1
# Extract unique launch sites from the 'Launch Site' column
unique_launch_sites = spacex_df['Launch Site'].unique()

# Create the options list for the dropdown, including the 'All' option
launch_sites_options = [{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in unique_launch_sites]


# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(id='site-dropdown',
                                options=launch_sites_options,  # Use the dynamically generated options
                                value='ALL',  # Default value is 'ALL'
                                placeholder="Select a Launch Site here",
                                searchable=True,
                                style={'width': '80%', 'padding': '3px', 
                                'font-size': '20px', 'text-align-last': 'center'}),
    
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',
                                min=0,  # Slider starting point
                                max=10000,  # Slider ending point
                                step=1000,  # Slider interval
                                value=[min_payload, max_payload],  # Selected range
                                marks={0: '0 Kg', 2500: '2500 Kg', 5000: '5000 Kg', 7500: '7500 Kg', 10000: '10000 Kg'},
                                tooltip={"placement": "bottom", "always_visible": True}),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('site-dropdown', 'value')]
)
def update_success_pie_chart(selected_site):
    if selected_site == 'ALL':
        # For all sites, calculate the total success count
        filtered_df = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(filtered_df, 
                     names='Launch Site', 
                     title='Total Successful Launches by Site')
    else:
        # Filter the dataframe based on the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        # Calculate success and failure counts
        success_fail_counts = filtered_df['class'].value_counts().reset_index()
        success_fail_counts.columns = ['class', 'count']
        fig = px.pie(success_fail_counts, 
                     names='class', 
                     values='count', 
                     title=f'Success vs Failure for site {selected_site}',
                     labels={0: 'Failed', 1: 'Success'})
    
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, selected_payload_range):
    # Unpack the selected payload range
    low, high = selected_payload_range
    
    # Filter the DataFrame by the selected payload range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                            (spacex_df['Payload Mass (kg)'] <= high)]
    
    # Check if the user selected "ALL" sites or a specific site
    if selected_site == 'ALL':
        # If "ALL" sites are selected, plot all data points
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title='Correlation between Payload and Success for All Sites',
                         labels={'class': 'Launch Outcome'})
    else:
        # Filter the DataFrame by the selected site
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        # Create a scatter plot for the selected site
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title=f'Correlation between Payload and Success for site {selected_site}',
                         labels={'class': 'Launch Outcome'})
    
    # Update the layout for better readability
    fig.update_layout(xaxis_title='Payload Mass (kg)',
                      yaxis_title='Launch Outcome',
                      yaxis=dict(tickvals=[0, 1], ticktext=['Failure', 'Success']))
    
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
