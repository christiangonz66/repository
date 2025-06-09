import streamlit as st
import pandas as pd
import plotly.express as px
from fuzzywuzzy import fuzz, process
import re
import json
from streamlit_plotly_events import plotly_events
import numpy as np  # Added for robust type handling

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

DEFAULT_CITIES = pd.DataFrame({
    'City': ['Denver', 'Colorado Springs', 'Aurora', 'Fort Collins', 'Lakewood', 'Boulder'],
    'Latitude': [39.74, 38.83, 39.73, 40.59, 39.71, 40.02],
    'Longitude': [-104.99, -104.82, -104.83, -105.08, -105.08, -105.27]
})

@st.cache_data
def load_county_geojson():
    with open("data/colorado_counties.geojson", "r") as f:
        return json.load(f)

def load_cities():
    try:
        return pd.read_csv('data/colorado_cities_over_50000.csv')
    except FileNotFoundError:
        return DEFAULT_CITIES

def clean_location(location):
    if pd.isna(location):
        return ""
    location = str(location).strip()
    city_part = location.split(',')[0].lower()
    city_part = re.sub(r'[^\w\s]', ' ', city_part)
    return re.sub(r'\s+', ' ', city_part).strip()

def match_location(location, cities, threshold=80):
    if not location:
        return None, 0
    cleaned = clean_location(location)
    city_part = cleaned.split(',')[0].strip()
    if city_part in CITY_TO_COUNTY:
        return city_part.title(), 100
    city_names = cities['City'].str.lower().tolist()
    match = process.extractOne(city_part, city_names, scorer=fuzz.token_sort_ratio)
    if match and match[1] >= threshold:
        mask = cities['City'].str.lower() == match[0]
        if mask.any():
            return cities.loc[mask, 'City'].iloc[0], match[1]
    return None, 0

def process_job_data(df, cities, threshold):
    df['location'] = df['location'].astype(str)
    df['cleaned_location'] = df['location'].apply(clean_location)
    matches = df['cleaned_location'].apply(lambda loc: match_location(loc, cities, threshold))
    df['matched_city'] = matches.apply(lambda x: x[0] if x else None)
    city_lookup = cities.set_index('City')[['Latitude', 'Longitude']].to_dict('index')
    df['latitude'] = df['matched_city'].apply(lambda city: city_lookup.get(city, {}).get('Latitude'))
    df['longitude'] = df['matched_city'].apply(lambda city: city_lookup.get(city, {}).get('Longitude'))
    df['county'] = df['matched_city'].str.lower().map(CITY_TO_COUNTY).str.title()
    df['industry'] = df['jobs[0].function'].astype(str) if 'jobs[0].function' in df.columns else None
    return df

def create_city_map(data, color_scheme='Viridis'):
    matched = data[data['matched_city'].notna()]
    if matched.empty:
        return None, []

    city_counts = matched.groupby(['matched_city', 'latitude', 'longitude']).size().reset_index(name='job_count')

    # Group by city and industry, count jobs
    industry_summary = matched.groupby(['matched_city', 'industry']).size().reset_index(name='count')
    industry_pivot = industry_summary.pivot(index='matched_city', columns='industry', values='count').fillna(0)

    # Merge industry data into city_counts
    city_counts = city_counts.merge(industry_pivot, on='matched_city', how='left')

    industries = industry_pivot.columns.tolist()
    custom_data_fields = ['matched_city'] + industries  # 👈 Include industry counts in custom_data

    fig = px.scatter_mapbox(
        city_counts,
        lat='latitude',
        lon='longitude',
        size='job_count',
        color='job_count',
        hover_name='matched_city',
        hover_data=industries,
        custom_data=custom_data_fields,
        color_continuous_scale=color_scheme,
        size_max=50,
        zoom=6,
        title='Colorado Job Distribution by City'
    )

    fig.update_layout(
        mapbox_style='carto-positron',
        mapbox_center=dict(lat=39.5, lon=-105.5),
        height=600
    )

    return fig, industries

def create_county_map(data, color_scheme='Viridis'):
    matched = data[data['county'].notna()]
    if matched.empty:
        return None
    county_counts = matched.groupby('county').size().reset_index(name='job_count')
    geojson = load_county_geojson()
    for feature in geojson["features"]:
        feature["id"] = feature["properties"]["NAME"]
    fig = px.choropleth_mapbox(
        county_counts,
        geojson=geojson,
        locations='county',
        color='job_count',
        featureidkey="properties.NAME",
        color_continuous_scale=color_scheme,
        mapbox_style="carto-positron",
        zoom=6,
        center={"lat": 39.5, "lon": -105.5},
        opacity=0.6,
        hover_name="county",
        title='Colorado Job Distribution by County'
    )
    fig.update_layout(height=600)
    return fig

def display_metrics(data):
    total = len(data)
    matched = len(data[data['matched_city'].notna()])
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Jobs", f"{total:,}")
    col2.metric("Matched", f"{matched:,}")
    col3.metric("Match Rate", f"{matched/total*100:.1f}%" if total > 0 else "0%")
    return matched

def display_data_tables(data):
    col1, col2 = st.columns(2)
    matched = data[data['matched_city'].notna()]
    unmatched = data[data['matched_city'].isna()]
    with col1:
        st.subheader("✅ Matched Locations")
        if not matched.empty:
            counts = matched.groupby('matched_city').size().reset_index(name='count')
            st.dataframe(counts.sort_values('count', ascending=False))
            st.download_button("📥 Download Matched Data", matched.to_csv(index=False), "matched_jobs.csv")
    with col2:
        st.subheader("❌ Unmatched Locations")
        if not unmatched.empty:
            counts = unmatched.groupby('location').size().reset_index(name='count')
            st.dataframe(counts.sort_values('count', ascending=False))

def render_sidebar():
    with st.sidebar:
        st.header("📁 Upload Data")
        uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])
        st.header("⚙️ Settings")
        view = st.selectbox("View Type", ["City Points", "County Boundaries"])
        threshold = st.slider("Matching Threshold", 60, 100, 80)
        color = st.selectbox("Color Scheme", ["Viridis", "Plasma", "Blues", "Reds"])
    return uploaded_file, view, threshold, color

def display_industry_breakdown(data):
    st.subheader("📊 Overall Industry Breakdown")
    if data['industry'].notna().any():
        industry_counts = data['industry'].value_counts(normalize=True).reset_index()
        industry_counts.columns = ['Industry', 'Percentage']
        industry_counts['Percentage'] *= 100
        fig = px.pie(
            industry_counts,
            names='Industry',
            values='Percentage',
            title="Overall Industry Breakdown",
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No industry data available.")

def main():
    st.title("🗺️ Colorado Job Tracker")
    st.markdown("Upload a CSV file with job location and industry data to visualize distribution across Colorado.")
    cities = load_cities()
    uploaded_file, view_type, threshold, color_scheme = render_sidebar()

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        data = process_job_data(df, cities, threshold)

        industry_options = sorted(data['industry'].dropna().unique())
        selected_industries = st.sidebar.multiselect("🏭 Filter by Industry", industry_options, default=industry_options)
        if selected_industries:
            data = data[data['industry'].isin(selected_industries)]

        matched = display_metrics(data)
        if matched:
            if view_type == "City Points":
                fig, industries = create_city_map(data, color_scheme)
            else:
                fig = create_county_map(data, color_scheme)
                industries = []

            if fig:
                click_data = plotly_events(fig, click_event=True, override_height=600)

                # NEW: Robust industry pie chart block using industries array
                if click_data:
                    clicked_point = click_data[0]
                    customdata = clicked_point.get("customdata", [])

                    if customdata and industries:
                        clicked_city = customdata[0]
                        st.subheader(f"🏙️ Industry Breakdown for {clicked_city}")

                        # Pair industries with respective counts, cast to int, handle missing/null
                        industry_counts = []
                        for industry, val in zip(industries, customdata[1:]):
                            try:
                                count = int(val) if val not in [None, '', 'nan', np.nan] else 0
                            except Exception:
                                count = 0
                            industry_counts.append({"Industry": industry, "Count": count})

                        industry_df = pd.DataFrame(industry_counts)
                        industry_df = industry_df[industry_df["Count"] > 0]

                        if not industry_df.empty:
                            fig_pie = px.pie(
                                industry_df,
                                names="Industry",
                                values="Count",
                                hole=0.4,
                                title=f"Industry Breakdown in {clicked_city}"
                            )
                            st.plotly_chart(fig_pie, use_container_width=True)
                        else:
                            st.info("No industry data found for this city.")
                    else:
                        st.info("No industry data found for this city.")
                else:
                    st.info("🖱️ Click a city or county on the map to view industry breakdown.")

        display_data_tables(data)
    else:
        st.info("👆 Upload a CSV file to get started")

if __name__ == "__main__":
    main()
