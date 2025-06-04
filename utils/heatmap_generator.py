import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class HeatmapGenerator:
    """
    Utility class for generating interactive heatmaps of job distribution across Colorado cities
    """

    def __init__(self, cities_df):
        """
        Initialize the HeatmapGenerator with Colorado cities data

        Args:
            cities_df (pd.DataFrame): DataFrame containing city names, coordinates, and population
        """
        self.cities_df = cities_df

        # Colorado state boundaries (approximate)
        self.colorado_bounds = {
            'lat_min': 37.0,
            'lat_max': 41.0,
            'lon_min': -109.1,
            'lon_max': -102.0
        }

    def create_heatmap(self, matched_data, map_style='carto-positron'):
        """
        Create an interactive heatmap showing job distribution across Colorado cities

        Args:
            matched_data (pd.DataFrame): DataFrame with matched job locations and coordinates
            map_style (str): Mapbox style for the background map

        Returns:
            plotly.graph_objects.Figure: Interactive heatmap figure
        """
        # Filter out unmatched locations
        valid_data = matched_data[matched_data['matched_city'].notna()].copy()

        if len(valid_data) == 0:
            # Return empty map if no valid data
            fig = go.Figure()
            fig.update_layout(
                title="No valid job locations found",
                annotations=[{
                    'text': 'No job locations could be matched to Colorado cities',
                    'showarrow': False,
                    'xref': 'paper',
                    'yref': 'paper',
                    'x': 0.5,
                    'y': 0.5,
                    'font': {'size': 16}
                }]
            )
            return fig

        # Aggregate job counts by city
        city_job_counts = valid_data.groupby(['matched_city', 'latitude', 'longitude']).size().reset_index(name='job_count')

        # Add population data
        city_job_counts = city_job_counts.merge(
            self.cities_df[['City', 'Population']], 
            left_on='matched_city', 
            right_on='City', 
            how='left'
        )

        # Calculate jobs per capita (jobs per 10,000 residents)
        city_job_counts['jobs_per_capita'] = (city_job_counts['job_count'] / city_job_counts['Population'] * 10000).round(2)

        # Create the scatter map
        fig = px.scatter_mapbox(
            city_job_counts,
            lat='latitude',
            lon='longitude',
            size='job_count',
            color='job_count',
            hover_name='matched_city',
            hover_data={
                'job_count': True,
                'Population': ':,',
                'jobs_per_capita': ':.1f',
                'latitude': ':.4f',
                'longitude': ':.4f'
            },
            color_continuous_scale='YlOrRd',
            size_max=50,
            zoom=6,
            title='Colorado Job Distribution Heatmap'
        )

        # Update map layout
        fig.update_layout(
            mapbox_style=map_style,
            mapbox=dict(
                center=dict(lat=39.0, lon=-105.5),  # Center of Colorado
                zoom=6
            ),
            height=600,
            title={
                'text': 'Colorado Job Distribution Heatmap',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            }
        )

        # Update hover template
        fig.update_traces(
            hovertemplate='<b>%{hovertext}</b><br>' +
                         'Jobs: %{customdata[0]}<br>' +
                         'Population: %{customdata[1]:,}<br>' +
                         'Jobs per 10K residents: %{customdata[2]:.1f}<br>' +
                         'Coordinates: (%{customdata[3]:.4f}, %{customdata[4]:.4f})<br>' +
                         '<extra></extra>'
        )

        # Add colorbar title
        fig.update_coloraxes(colorbar_title_text="Number of Jobs")

        return fig

    def create_detailed_heatmap(self, matched_data):
        """
        Create a more detailed heatmap with additional visualizations

        Args:
            matched_data (pd.DataFrame): DataFrame with matched job locations and coordinates

        Returns:
            plotly.graph_objects.Figure: Detailed heatmap with subplots
        """
        # Filter valid data
        valid_data = matched_data[matched_data['matched_city'].notna()].copy()

        if len(valid_data) == 0:
            return self.create_heatmap(matched_data)

        # Aggregate data
        city_job_counts = valid_data.groupby(['matched_city', 'latitude', 'longitude']).size().reset_index(name='job_count')
        city_job_counts = city_job_counts.merge(
            self.cities_df[['City', 'Population']], 
            left_on='matched_city', 
            right_on='City', 
            how='left'
        )
        city_job_counts['jobs_per_capita'] = (city_job_counts['job_count'] / city_job_counts['Population'] * 10000).round(2)

        # Sort by job count for better visualization
        city_job_counts = city_job_counts.sort_values('job_count', ascending=False)

        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=['Job Distribution Map', 'Top Cities by Job Count', 
                          'Jobs vs Population', 'Jobs per Capita'],
            specs=[[{"type": "mapbox", "colspan": 2}, None],
                   [{"type": "bar"}, {"type": "scatter"}]],
            row_heights=[0.6, 0.4]
        )

        # Main heatmap
        scatter_map = go.Scattermapbox(
            lat=city_job_counts['latitude'],
            lon=city_job_counts['longitude'],
            mode='markers',
            marker=dict(
                size=city_job_counts['job_count'],
                color=city_job_counts['job_count'],
                colorscale='YlOrRd',
                sizemode='diameter',
                sizeref=2.*max(city_job_counts['job_count'])/(50.**2),
                sizemin=4,
                showscale=True,
                colorbar=dict(title="Jobs", x=1.02)
            ),
            text=city_job_counts['matched_city'],
            hovertemplate='<b>%{text}</b><br>' +
                         'Jobs: %{marker.color}<br>' +
                         'Population: %{customdata[0]:,}<br>' +
                         'Jobs per 10K: %{customdata[1]:.1f}<br>' +
                         '<extra></extra>',
            customdata=city_job_counts[['Population', 'jobs_per_capita']].values
        )

        fig.add_trace(scatter_map, row=1, col=1)

        # Top cities bar chart
        top_cities = city_job_counts.head(10)
        bar_chart = go.Bar(
            x=top_cities['job_count'],
            y=top_cities['matched_city'],
            orientation='h',
            marker_color='rgba(255, 99, 71, 0.7)',
            hovertemplate='<b>%{y}</b><br>Jobs: %{x}<extra></extra>'
        )
        fig.add_trace(bar_chart, row=2, col=1)

        # Jobs vs Population scatter
        scatter_plot = go.Scatter(
            x=city_job_counts['Population'],
            y=city_job_counts['job_count'],
            mode='markers+text',
            text=city_job_counts['matched_city'],
            textposition='top center',
            marker=dict(
                size=10,
                color='rgba(70, 130, 180, 0.7)',
                line=dict(width=1, color='white')
            ),
            hovertemplate='<b>%{text}</b><br>' +
                         'Population: %{x:,}<br>' +
                         'Jobs: %{y}<br>' +
                         '<extra></extra>'
        )
        fig.add_trace(scatter_plot, row=2, col=2)

        # Update layout
        fig.update_layout(
            height=800,
            title={
                'text': 'Colorado Job Distribution Analysis',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            mapbox=dict(
                style='open-street-map',
                center=dict(lat=39.0, lon=-105.5),
                zoom=6
            ),
            showlegend=False
        )

        # Update axes labels
        fig.update_xaxes(title_text="Number of Jobs", row=2, col=1)
        fig.update_yaxes(title_text="City", row=2, col=1)
        fig.update_xaxes(title_text="Population", row=2, col=2)
        fig.update_yaxes(title_text="Number of Jobs", row=2, col=2)

        return fig

    def create_density_heatmap(self, matched_data, resolution=50):
        """
        Create a density-based heatmap using hexagonal binning

        Args:
            matched_data (pd.DataFrame): DataFrame with matched job locations and coordinates
            resolution (int): Resolution for the density calculation

        Returns:
            plotly.graph_objects.Figure: Density heatmap figure
        """
        # Filter valid data
        valid_data = matched_data[matched_data['matched_city'].notna()].copy()

        if len(valid_data) == 0:
            return self.create_heatmap(matched_data)

        # Create density map using hexbin
        fig = go.Figure()

        # Add hexbin density layer
        fig.add_trace(go.Histogram2d(
            x=valid_data['longitude'],
            y=valid_data['latitude'],
            nbinsx=resolution,
            nbinsy=resolution,
            colorscale='YlOrRd',
            hovertemplate='Longitude: %{x:.4f}<br>Latitude: %{y:.4f}<br>Density: %{z}<extra></extra>'
        ))

        # Add city markers on top
        city_job_counts = valid_data.groupby(['matched_city', 'latitude', 'longitude']).size().reset_index(name='job_count')

        fig.add_trace(go.Scatter(
            x=city_job_counts['longitude'],
            y=city_job_counts['latitude'],
            mode='markers+text',
            text=city_job_counts['matched_city'],
            textposition='top center',
            marker=dict(
                size=city_job_counts['job_count'].apply(lambda x: min(max(x/5, 8), 25)),
                color='white',
                line=dict(width=2, color='black')
            ),
            hovertemplate='<b>%{text}</b><br>Jobs: %{customdata}<extra></extra>',
            customdata=city_job_counts['job_count'],
            name='Cities'
        ))

        # Update layout
        fig.update_layout(
            title={
                'text': 'Colorado Job Density Heatmap',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            xaxis_title='Longitude',
            yaxis_title='Latitude',
            height=600,
            showlegend=False
        )

        # Set aspect ratio to match Colorado's geography
        fig.update_yaxes(scaleanchor="x", scaleratio=1)

        return fig
