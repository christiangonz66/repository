import streamlit as st
import pandas as pd
import plotly.express as px
from fuzzywuzzy import fuzz, process
import re

# Page config
st.set_page_config(
    page_title="Colorado Job Tracker",
    page_icon="🗺️",
    layout="wide"
)

# Colorado cities to counties mapping (simplified)
CITY_TO_COUNTY = {
    'denver': 'Denver', 'aurora': 'Arapahoe', 'colorado springs': 'El Paso',
    'fort collins': 'Larimer', 'lakewood': 'Jefferson', 'thornton': 'Adams',
    'arvada': 'Jefferson', 'westminster': 'Adams', 'greeley': 'Weld',
    'pueblo': 'Pueblo', 'centennial': 'Arapahoe', 'boulder': 'Boulder',
    'longmont': 'Boulder', 'castle rock': 'Douglas', 'loveland': 'Larimer',
    'broomfield': 'Broomfield', 'grand junction': 'Mesa', 'commerce city': 'Adams',
    'parker': 'Douglas', 'littleton': 'Arapahoe', 'northglenn': 'Adams',
    'brighton': 'Adams', 'wheat ridge': 'Jefferson', 'fountain': 'El Paso',
    'lafayette': 'Boulder', 'erie': 'Boulder', 'englewood': 'Arapahoe',
    'evans': 'Weld', 'golden': 'Jefferson', 'montrose': 'Montrose',
    'aspen': 'Pitkin', 'vail': 'Eagle', 'steamboat springs': 'Routt',
    'durango': 'La Plata', 'glenwood springs': 'Garfield', 'telluride': 'San Miguel',
    'breckenridge': 'Summit', 'crested butte': 'Gunnison'
}

# Default Colorado cities data
DEFAULT_CITIES = pd.DataFrame({
    'City': ['Denver', 'Colorado Springs', 'Aurora', 'Fort Collins', 'Lakewood', 'Boulder'],
    'Latitude': [39.74, 38.83, 39.73, 40.59, 39.71, 40.02],
    'Longitude': [-104.99, -104.82, -104.83, -105.08, -105.08, -105.27]
})

@st.cache_data
def load_cities():
    """Load Colorado cities data with fallback"""
    try:
        return pd.read_csv('data/colorado_cities_over_50000.csv')
    except FileNotFoundError:
        # Fallback: use default cities data
        return DEFAULT_CITIES

def clean_location(location):
    """Clean and normalize location string"""
    if pd.isna(location):
        return ""
    location = str(location).lower().strip()
    location = re.sub(r'\b(co|colorado|usa|us)\b', '', location)
    location = re.sub(r'[^\w\s]', ' ', location)
    return re.sub(r'\s+', ' ', location).strip()

def match_location(location, cities, threshold=80):
    """Match location to Colorado city using fuzzy matching"""
    if not location:
        return None, 0
    
    cleaned = clean_location(location)
    city_part = cleaned.split(',')[0].strip()
    
    # Try exact match first
    if city_part in CITY_TO_COUNTY:
        return city_part.title(), 100
    
    # Fuzzy match against city list
    city_names = cities['City'].str.lower().tolist()
    match = process.extractOne(city_part, city_names, scorer=fuzz.token_sort_ratio)
    
    if match and match[1] >= threshold:
        return cities[cities['City'].str.lower() == match[0]]['City'].iloc[0], match[1]
    
    return None, 0

def process_job_data(df, cities, threshold=80):
    """Process job data and match locations"""
    # Find location column
    location_columns = [col for col in df.columns if 'location' in col.lower()]
    if not location_columns:
        st.error("CSV must contain a column with 'location' in the name")
        return None
    
    location_col = location_columns[0]
    
    results = []
    for _, row in df.iterrows():
        matched_city, confidence = match_location(row[location_col], cities, threshold)
        
        result = row.to_dict()
        result['matched_city'] = matched_city
        result['confidence'] = confidence
        
        if matched_city:
            city_data = cities[cities['City'] == matched_city].iloc[0]
            result['latitude'] = city_data['Latitude']
            result['longitude'] = city_data['Longitude']
            result['county'] = CITY_TO_COUNTY.get(matched_city.lower())
        
        results.append(result)
    
    return pd.DataFrame(results)

def create_city_map(data, color_scheme='Viridis'):
    """Create city points map"""
    matched = data[data['matched_city'].notna()]
    if len(matched) == 0:
        return None
    
    city_counts = matched.groupby(['matched_city', 'latitude', 'longitude']).size().reset_index(name='job_count')
    
    fig = px.scatter_mapbox(
        city_counts,
        lat='latitude',
        lon='longitude',
        size='job_count',
        color='job_count',
        hover_name='matched_city',
        color_continuous_scale=color_scheme,
        size_max=50,
        zoom=6,
        title='Colorado Job Distribution by City'
    )
    
    fig.update_layout(
        mapbox_style='carto-positron',
        mapbox=dict(center=dict(lat=39.5, lon=-105.5)),
        height=600
    )
    
    return fig

def create_county_map(data, color_scheme='Viridis'):
    """Create county choropleth map"""
    matched = data[data['county'].notna()]
    if len(matched) == 0:
        return None
    
    county_counts = matched.groupby('county').size().reset_index(name='job_count')
    
    # Simple county center coordinates for visualization
    county_centers = {
        'Denver': (39.74, -104.99), 'Jefferson': (39.58, -105.14), 'Arapahoe': (39.61, -104.82),
        'Adams': (39.88, -104.77), 'Boulder': (40.02, -105.27), 'El Paso': (38.83, -104.82),
        'Larimer': (40.59, -105.08), 'Weld': (40.42, -104.71), 'Mesa': (39.06, -108.55),
        'Pueblo': (38.25, -104.61), 'Douglas': (39.37, -104.86)
    }
    
    county_counts['lat'] = county_counts['county'].map(lambda x: county_centers.get(x, (39.5, -105.5))[0])
    county_counts['lon'] = county_counts['county'].map(lambda x: county_centers.get(x, (39.5, -105.5))[1])
    
    fig = px.scatter_mapbox(
        county_counts,
        lat='lat',
        lon='lon',
        size='job_count',
        color='job_count',
        hover_name='county',
        color_continuous_scale=color_scheme,
        size_max=80,
        zoom=6,
        title='Colorado Job Distribution by County'
    )
    
    fig.update_layout(
        mapbox_style='carto-positron',
        mapbox=dict(center=dict(lat=39.5, lon=-105.5)),
        height=600
    )
    
    return fig

def display_metrics(processed_data):
    """Display summary metrics in columns"""
    total = len(processed_data)
    matched = len(processed_data[processed_data['matched_city'].notna()])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Jobs", f"{total:,}")
    with col2:
        st.metric("Matched", f"{matched:,}")
    with col3:
        st.metric("Match Rate", f"{matched/total*100:.1f}%" if total > 0 else "0%")
    
    return matched

def display_data_tables(processed_data):
    """Display matched and unmatched data tables"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Matched Locations")
        matched_data = processed_data[processed_data['matched_city'].notna()]
        if len(matched_data) > 0:
            location_counts = matched_data.groupby('matched_city').size().reset_index(name='count')
            location_counts = location_counts.sort_values('count', ascending=False)
            st.dataframe(location_counts)
            
            csv = matched_data.to_csv(index=False)
            st.download_button("📥 Download Matched Data", csv, "matched_jobs.csv", "text/csv")
    
    with col2:
        st.subheader("❌ Unmatched Locations")
        unmatched = processed_data[processed_data['matched_city'].isna()]
        if len(unmatched) > 0:
            unmatched_counts = unmatched.groupby('location').size().reset_index(name='count')
            unmatched_counts = unmatched_counts.sort_values('count', ascending=False)
            st.dataframe(unmatched_counts)

def render_sidebar():
    """Render sidebar controls and return settings"""
    with st.sidebar:
        st.header("📁 Upload Data")
        uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])
        
        st.header("⚙️ Settings")
        view_type = st.selectbox("View Type", ["City Points", "County Boundaries"])
        threshold = st.slider("Matching Threshold", 60, 100, 80)
        color_scheme = st.selectbox("Color Scheme", ["Viridis", "Plasma", "Blues", "Reds"])
    
    return uploaded_file, view_type, threshold, color_scheme

def main():
    st.title("🗺️ Colorado Job Tracker")
    st.markdown("Upload a CSV file with job location data to visualize distribution across Colorado")
    
    cities = load_cities()
    uploaded_file, view_type, threshold, color_scheme = render_sidebar()
    
    if uploaded_file:
        try:
            with st.spinner("Processing data..."):
                df = pd.read_csv(uploaded_file)
                processed_data = process_job_data(df, cities, threshold)
            
            if processed_data is not None:
                matched_count = display_metrics(processed_data)
                
                # Render map only if we have matches
                if matched_count > 0:
                    map_func = create_city_map if view_type == "City Points" else create_county_map
                    fig = map_func(processed_data, color_scheme)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                
                display_data_tables(processed_data)
        except Exception as e:
            st.error(f"Error processing data: {str(e)}")
            st.info("Please check your CSV format and try again.")
    else:
        # Show welcome message and sample format
        st.info("👆 Upload a CSV file to get started")
        with st.expander("📋 Expected CSV Format"):
            sample = pd.DataFrame({
                'location': ['Denver, CO', 'Boulder', 'Colorado Springs'],
                'job_title': ['Engineer', 'Analyst', 'Manager'],
                'company': ['Tech Corp', 'Data Inc', 'Biz LLC']
            })
            st.dataframe(sample)
        
        # Show deployment instructions
        with st.expander("🚀 Deployment Instructions"):
            st.markdown("""
            ### How to Deploy This App
            
            #### Option 1: Streamlit Cloud (Recommended)
            1. Push this code to GitHub
            2. Go to [share.streamlit.io](https://share.streamlit.io)
            3. Connect your GitHub repository
            4. Set main file path to `app.py`
            5. Click Deploy!
            
            #### Option 2: Heroku
            1. Make sure you have the `Procfile` with: `web: streamlit run app.py --server.port=$PORT`
            2. Push to Heroku with: `heroku create` and `git push heroku main`
            
            #### Option 3: Local Development
            Run: `streamlit run app.py`
            """)

if __name__ == "__main__":
    main()
