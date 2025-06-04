import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.location_matcher import LocationMatcher
from utils.heatmap_generator import HeatmapGenerator
from utils.colorado_counties import get_city_to_county_mapping, get_colorado_counties_geojson
import json

# Page configuration
st.set_page_config(
    page_title="Colorado Job Tracker",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stSelectbox > div > div {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">🗺️ Colorado Job Tracker</h1>', unsafe_allow_html=True)
    
    # Sidebar for file upload and settings
    with st.sidebar:
        st.header("📁 Data Upload")
        uploaded_file = st.file_uploader(
            "Upload your job data CSV file",
            type=['csv'],
            help="Upload a CSV file containing job data with location information"
        )
        
        if uploaded_file is not None:
            st.success("✅ File uploaded successfully!")
        
        st.header("⚙️ Settings")
        
        # View type selection
        view_type = st.selectbox(
            "Select View Type",
            ["City Points", "County Boundaries"],
            help="Choose between individual city points or county boundary visualization"
        )
        
        # Matching threshold
        threshold = st.slider(
            "Location Matching Threshold",
            min_value=60,
            max_value=100,
            value=80,
            step=5,
            help="Higher values require more exact matches (recommended: 80-90)"
        )
        
        # Color scheme
        color_scheme = st.selectbox(
            "Color Scheme",
            ["Viridis", "Plasma", "Blues", "Reds", "YlOrRd"],
            help="Choose the color scheme for the heatmap"
        )

    # Main content area
    if uploaded_file is not None:
        try:
            # Load and process data
            with st.spinner("Processing your data..."):
                df = pd.read_csv(uploaded_file)
                
                # Initialize location matcher
                matcher = LocationMatcher(threshold=threshold)
                
                # Process locations
                processed_data = matcher.process_locations(df)
                
                # Display summary statistics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Total Jobs",
                        f"{len(df):,}",
                        help="Total number of job postings in the dataset"
                    )
                
                with col2:
                    matched_count = len(processed_data['matched'])
                    match_rate = (matched_count / len(df)) * 100 if len(df) > 0 else 0
                    st.metric(
                        "Matched Locations",
                        f"{matched_count:,}",
                        f"{match_rate:.1f}% match rate"
                    )
                
                with col3:
                    unique_locations = len(processed_data['matched']['matched_location'].unique()) if len(processed_data['matched']) > 0 else 0
                    st.metric(
                        "Unique Locations",
                        f"{unique_locations:,}",
                        help="Number of distinct Colorado locations found"
                    )
                
                with col4:
                    unmatched_count = len(processed_data['unmatched'])
                    st.metric(
                        "Unmatched",
                        f"{unmatched_count:,}",
                        help="Job postings with locations not recognized as Colorado cities"
                    )
                
                # Generate and display map
                if len(processed_data['matched']) > 0:
                    st.header("🗺️ Job Distribution Map")
                    
                    heatmap_gen = HeatmapGenerator()
                    
                    if view_type == "City Points":
                        fig = heatmap_gen.create_city_heatmap(
                            processed_data['matched'],
                            color_scheme.lower()
                        )
                    else:  # County Boundaries
                        fig = heatmap_gen.create_county_heatmap(
                            processed_data['matched'],
                            color_scheme.lower()
                        )
                    
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("Unable to generate map. Please check your data format.")
                
                # Display data tables
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("✅ Matched Locations")
                    if len(processed_data['matched']) > 0:
                        # Group by location and count
                        location_counts = processed_data['matched'].groupby('matched_location').size().reset_index(name='job_count')
                        location_counts = location_counts.sort_values('job_count', ascending=False)
                        st.dataframe(location_counts, use_container_width=True)
                        
                        # Download button for matched data
                        csv_matched = processed_data['matched'].to_csv(index=False)
                        st.download_button(
                            label="📥 Download Matched Data",
                            data=csv_matched,
                            file_name="matched_colorado_jobs.csv",
                            mime="text/csv"
                        )
                    else:
                        st.info("No locations were matched to Colorado cities.")
                
                with col2:
                    st.subheader("❌ Unmatched Locations")
                    if len(processed_data['unmatched']) > 0:
                        # Show unique unmatched locations with counts
                        unmatched_counts = processed_data['unmatched'].groupby('original_location').size().reset_index(name='count')
                        unmatched_counts = unmatched_counts.sort_values('count', ascending=False)
                        st.dataframe(unmatched_counts, use_container_width=True)
                        
                        # Download button for unmatched data
                        csv_unmatched = processed_data['unmatched'].to_csv(index=False)
                        st.download_button(
                            label="📥 Download Unmatched Data",
                            data=csv_unmatched,
                            file_name="unmatched_locations.csv",
                            mime="text/csv"
                        )
                    else:
                        st.success("All locations were successfully matched!")
                
                # County summary (for county view)
                if view_type == "County Boundaries" and len(processed_data['matched']) > 0:
                    st.subheader("📊 County Summary")
                    
                    # Get city to county mapping
                    city_to_county = get_city_to_county_mapping()
                    
                    # Add county information to matched data
                    matched_with_county = processed_data['matched'].copy()
                    matched_with_county['county'] = matched_with_county['matched_location'].map(city_to_county)
                    
                    # Group by county
                    county_summary = matched_with_county.groupby('county').size().reset_index(name='job_count')
                    county_summary = county_summary.sort_values('job_count', ascending=False)
                    county_summary = county_summary[county_summary['county'].notna()]  # Remove unmapped counties
                    
                    st.dataframe(county_summary, use_container_width=True)
                
        except Exception as e:
            st.error(f"An error occurred while processing your data: {str(e)}")
            st.info("Please ensure your CSV file has the correct format with location information.")
    
    else:
        # Welcome message and instructions
        st.markdown("""
        ## Welcome to Colorado Job Tracker! 🎯
        
        This tool helps you analyze job market data across Colorado by:
        
        ### 📊 **Key Features**
        - **Smart Location Matching**: Automatically identifies Colorado cities in your job data
        - **Interactive Maps**: Visualize job distribution with city points or county boundaries  
        - **Fuzzy Matching**: Handles variations in city names and common misspellings
        - **Data Export**: Download processed results for further analysis
        
        ### 🚀 **How to Get Started**
        1. **Upload your CSV file** using the sidebar
        2. **Choose your view type** (City Points or County Boundaries)
        3. **Adjust matching threshold** for optimal results
        4. **Explore the interactive map** and data tables
        
        ### 📋 **CSV Format Requirements**
        Your CSV should contain a column with location information such as:
        - City names (e.g., "Denver", "Colorado Springs")
        - City, State format (e.g., "Boulder, CO")
        - Full addresses containing Colorado cities
        
        ### 🎨 **Visualization Options**
        - **City Points**: Shows individual cities as circles sized by job count
        - **County Boundaries**: Displays job density across Colorado counties
        - **Multiple Color Schemes**: Choose from various color palettes
        
        Ready to explore Colorado's job market? Upload your data to begin! 📈
        """)
        
        # Sample data info
        with st.expander("📝 Sample Data Format"):
            sample_data = pd.DataFrame({
                'job_title': ['Software Engineer', 'Data Analyst', 'Marketing Manager'],
                'location': ['Denver, CO', 'Boulder', 'Colorado Springs, Colorado'],
                'company': ['Tech Corp', 'Data Inc', 'Marketing LLC']
            })
            st.dataframe(sample_data)
            st.caption("Your CSV can have any columns, but should include location information")

if __name__ == "__main__":
    main()
