import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fuzzywuzzy import fuzz, process
import re
import json

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

@st.cache_data
def load_cities():
    """Load Colorado cities data"""
    return pd.read_csv('data/colorado_cities_over_50000.csv')

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
    if 'location' not in df.columns:
        st.error("CSV must contain a 'location' column")
        return None
    
    results = []
    for _, row in df.iterrows():
        matched_city, confidence = match_location(row['location'], cities, threshold)
        
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

def main():
    st.title("🗺️ Colorado Job Tracker")
    st.markdown("Upload a CSV file with job location data to visualize distribution across Colorado")
    
    # Load cities data
    cities = load_cities()
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Upload Data")
        uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])
        
        st.header("⚙️ Settings")
        view_type = st.selectbox("View Type", ["City Points", "County Boundaries"])
        threshold = st.slider("Matching Threshold", 60, 100, 80)
        color_scheme = st.selectbox("Color Scheme", ["Viridis", "Plasma", "Blues", "Reds"])
    
    if uploaded_file:
        # Process data
        with st.spinner("Processing data..."):
            df = pd.read_csv(uploaded_file)
            processed_data = process_job_data(df, cities, threshold)
        
        if processed_data is not None:
            # Stats
            total = len(processed_data)
            matched = len(processed_data[processed_data['matched_city'].notna()])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Jobs", f"{total:,}")
            with col2:
                st.metric("Matched", f"{matched:,}")
            with col3:
                st.metric("Match Rate", f"{matched/total*100:.1f}%")
            
            # Map
            if matched > 0:
                if view_type == "City Points":
                    fig = create_city_map(processed_data, color_scheme)
                else:
                    fig = create_county_map(processed_data, color_scheme)
                
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            
            # Data tables
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("✅ Matched Locations")
                if matched > 0:
                    matched_data = processed_data[processed_data['matched_city'].notna()]
                    location_counts = matched_data.groupby('matched_city').size().reset_index(name='count')
                    location_counts = location_counts.sort_values('count', ascending=False)
                    st.dataframe(location_counts)
                    
                    # Download
                    csv = matched_data.to_csv(index=False)
                    st.download_button("📥 Download Matched Data", csv, "matched_jobs.csv", "text/csv")
            
            with col2:
                st.subheader("❌ Unmatched Locations")
                unmatched = processed_data[processed_data['matched_city'].isna()]
                if len(unmatched) > 0:
                    unmatched_counts = unmatched.groupby('location').size().reset_index(name='count')
                    unmatched_counts = unmatched_counts.sort_values('count', ascending=False)
                    st.dataframe(unmatched_counts)
    
    else:
        st.info("👆 Upload a CSV file to get started")
        
        # Sample format
        with st.expander("📋 Expected CSV Format"):
            sample = pd.DataFrame({
                'location': ['Denver, CO', 'Boulder', 'Colorado Springs'],
                'job_title': ['Engineer', 'Analyst', 'Manager'],
                'company': ['Tech Corp', 'Data Inc', 'Biz LLC']
            })
            st.dataframe(sample)

if __name__ == "__main__":
    main()
