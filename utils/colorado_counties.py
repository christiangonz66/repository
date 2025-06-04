import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

class ColoradoCounties:
    def __init__(self):
        # Comprehensive mapping of Colorado cities to their counties
        self.city_to_county = {
            # Denver Metro Area
            'denver': 'Denver',
            'aurora': 'Arapahoe',
            'lakewood': 'Jefferson',
            'thornton': 'Adams',
            'arvada': 'Jefferson',
            'westminster': 'Adams',
            'centennial': 'Arapahoe',
            'boulder': 'Boulder',
            'broomfield': 'Broomfield',
            'commerce city': 'Adams',
            'northglenn': 'Adams',
            'wheat ridge': 'Jefferson',
            'englewood': 'Arapahoe',
            'littleton': 'Arapahoe',
            'golden': 'Jefferson',
            'lafayette': 'Boulder',
            'louisville': 'Boulder',
            'superior': 'Boulder',
            'erie': 'Boulder',
            'longmont': 'Boulder',
            'brighton': 'Adams',
            'federal heights': 'Adams',
            'sheridan': 'Arapahoe',
            'edgewater': 'Jefferson',
            'mountain view': 'Jefferson',
            'glendale': 'Arapahoe',
            'cherry hills village': 'Arapahoe',
            'columbine valley': 'Arapahoe',
            'deer trail': 'Arapahoe',
            'bow mar': 'Jefferson',
            'morrison': 'Jefferson',
            'lakeside': 'Jefferson',
            
            # Colorado Springs Area
            'colorado springs': 'El Paso',
            'fountain': 'El Paso',
            'security-widefield': 'El Paso',
            'cimarron hills': 'El Paso',
            'manitou springs': 'El Paso',
            'black forest': 'El Paso',
            'gleneagle': 'El Paso',
            'air force academy': 'El Paso',
            'monument': 'El Paso',
            'palmer lake': 'El Paso',
            'green mountain falls': 'El Paso',
            'cascade-chipita park': 'El Paso',
            
            # Northern Colorado
            'fort collins': 'Larimer',
            'loveland': 'Larimer',
            'greeley': 'Weld',
            'evans': 'Weld',
            'windsor': 'Weld',
            'johnstown': 'Weld',
            'milliken': 'Weld',
            'berthoud': 'Larimer',
            'wellington': 'Larimer',
            'timnath': 'Larimer',
            'severance': 'Weld',
            'eaton': 'Weld',
            'ault': 'Weld',
            'pierce': 'Weld',
            'nunn': 'Weld',
            'kersey': 'Weld',
            'garden city': 'Weld',
            'la salle': 'Weld',
            'gilcrest': 'Weld',
            'platteville': 'Weld',
            'frederick': 'Weld',
            'firestone': 'Weld',
            'dacono': 'Weld',
            'mead': 'Weld',
            'lyons': 'Boulder',
            'niwot': 'Boulder',
            'ward': 'Boulder',
            'jamestown': 'Boulder',
            'nederland': 'Boulder',
            
            # Pueblo Area
            'pueblo': 'Pueblo',
            'pueblo west': 'Pueblo',
            'boone': 'Pueblo',
            'salt creek': 'Pueblo',
            'blende': 'Pueblo',
            'avondale': 'Pueblo',
            'beulah valley': 'Pueblo',
            
            # Grand Junction Area
            'grand junction': 'Mesa',
            'fruita': 'Mesa',
            'palisade': 'Mesa',
            'clifton': 'Mesa',
            'orchard mesa': 'Mesa',
            'redlands': 'Mesa',
            'fruitvale': 'Mesa',
            'loma': 'Mesa',
            'mack': 'Mesa',
            'collbran': 'Mesa',
            'de beque': 'Mesa',
            
            # Mountain Communities
            'aspen': 'Pitkin',
            'snowmass village': 'Pitkin',
            'basalt': 'Eagle',
            'carbondale': 'Garfield',
            'glenwood springs': 'Garfield',
            'rifle': 'Garfield',
            'silt': 'Garfield',
            'new castle': 'Garfield',
            'parachute': 'Garfield',
            'battlement mesa': 'Garfield',
            'vail': 'Eagle',
            'avon': 'Eagle',
            'beaver creek': 'Eagle',
            'eagle': 'Eagle',
            'gypsum': 'Eagle',
            'minturn': 'Eagle',
            'edwards': 'Eagle',
            'eagle-vail': 'Eagle',
            'breckenridge': 'Summit',
            'frisco': 'Summit',
            'keystone': 'Summit',
            'silverthorne': 'Summit',
            'dillon': 'Summit',
            'copper mountain': 'Summit',
            'blue river': 'Summit',
            'montezuma': 'Summit',
            'steamboat springs': 'Routt',
            'hayden': 'Routt',
            'oak creek': 'Routt',
            'yampa': 'Routt',
            'phippsburg': 'Routt',
            'telluride': 'San Miguel',
            'mountain village': 'San Miguel',
            'ophir': 'San Miguel',
            'norwood': 'San Miguel',
            'crested butte': 'Gunnison',
            'mount crested butte': 'Gunnison',
            'gunnison': 'Gunnison',
            'marble': 'Gunnison',
            'almont': 'Gunnison',
            'pitkin': 'Gunnison',
            'ouray': 'Ouray',
            'ridgway': 'Ouray',
            'silverton': 'San Juan',
            'durango': 'La Plata',
            'bayfield': 'La Plata',
            'ignacio': 'La Plata',
            'pagosa springs': 'Archuleta',
            'cortez': 'Montezuma',
            'mancos': 'Montezuma',
            'dolores': 'Montezuma',
            'dove creek': 'Dolores',
            'rico': 'Dolores',
            
            # Eastern Plains
            'sterling': 'Logan',
            'fort morgan': 'Morgan',
            'brush': 'Morgan',
            'log lane village': 'Morgan',
            'hillrose': 'Morgan',
            'wiggins': 'Morgan',
            'weldona': 'Morgan',
            'yuma': 'Yuma',
            'wray': 'Yuma',
            'eckley': 'Yuma',
            'vernon': 'Yuma',
            'holyoke': 'Phillips',
            'haxtun': 'Phillips',
            'paoli': 'Phillips',
            'julesburg': 'Sedgwick',
            'ovid': 'Sedgwick',
            'chappell': 'Deuel',
            'akron': 'Washington',
            'otis': 'Washington',
            'cope': 'Washington',
            'anton': 'Washington',
            'woodrow': 'Washington',
            'last chance': 'Washington',
            'lindon': 'Washington',
            'fleming': 'Logan',
            'peetz': 'Logan',
            'crook': 'Logan',
            'iliff': 'Logan',
            'merino': 'Logan',
            'atwood': 'Logan',
            'proctor': 'Logan',
            'sedgwick': 'Sedgwick',
            'big springs': 'Deuel',
            'chappell': 'Deuel',
            
            # Southern Colorado
            'canon city': 'Fremont',
            'florence': 'Fremont',
            'penrose': 'Fremont',
            'rockvale': 'Fremont',
            'coal creek': 'Fremont',
            'brookside': 'Fremont',
            'williamsburg': 'Fremont',
            'cotopaxi': 'Fremont',
            'salida': 'Chaffee',
            'buena vista': 'Chaffee',
            'poncha springs': 'Chaffee',
            'nathrop': 'Chaffee',
            'granite': 'Chaffee',
            'maysville': 'Chaffee',
            'alamosa': 'Alamosa',
            'monte vista': 'Rio Grande',
            'del norte': 'Rio Grande',
            'south fork': 'Rio Grande',
            'creede': 'Mineral',
            'center': 'Rio Grande',
            'la jara': 'Conejos',
            'antonito': 'Conejos',
            'manassa': 'Conejos',
            'romeo': 'Conejos',
            'sanford': 'Conejos',
            'trinidad': 'Las Animas',
            'walsenburg': 'Huerfano',
            'la veta': 'Huerfano',
            'gardner': 'Huerfano',
            'cuchara': 'Huerfano',
            'aguilar': 'Las Animas',
            'segundo': 'Las Animas',
            'cokedale': 'Las Animas',
            'starkville': 'Las Animas',
            'branson': 'Las Animas',
            'kim': 'Las Animas',
            'raton': 'Colfax',
            'springer': 'Colfax',
            'cimarron': 'Colfax',
            'maxwell': 'Colfax',
            'rayado': 'Colfax',
            'eagle nest': 'Colfax',
            'angel fire': 'Colfax',
            'red river': 'Taos',
            'questa': 'Taos',
            'taos': 'Taos',
            'espanola': 'Rio Arriba',
            'chama': 'Rio Arriba',
            'tierra amarilla': 'Rio Arriba',
            'los ojos': 'Rio Arriba',
            'dulce': 'Rio Arriba',
            'pagosa springs': 'Archuleta',
            'chromo': 'Archuleta',
            'arboles': 'Archuleta',
            'allison': 'Rio Arriba',
            'lumberton': 'Rio Arriba',
            
            # Central Colorado
            'leadville': 'Lake',
            'twin lakes': 'Lake',
            'fairplay': 'Park',
            'alma': 'Park',
            'breckenridge': 'Summit',
            'como': 'Park',
            'jefferson': 'Park',
            'hartsel': 'Park',
            'guffey': 'Park',
            'lake george': 'Park',
            'woodland park': 'Teller',
            'cripple creek': 'Teller',
            'victor': 'Teller',
            'divide': 'Teller',
            'florissant': 'Teller',
            'cascade': 'El Paso',
            'green mountain falls': 'El Paso',
            'chipita park': 'El Paso',
            'crystola': 'Teller',
            'rye': 'Pueblo',
            'colorado city': 'Pueblo',
            'beulah': 'Pueblo',
            'san isabel': 'Pueblo',
            'wetmore': 'Custer',
            'silver cliff': 'Custer',
            'westcliffe': 'Custer',
            'rosita': 'Custer',
            'querida': 'Custer',
            'hillside': 'Custer',
            'gardner': 'Huerfano',
            'redwing': 'Huerfano',
            'badito': 'Huerfano',
            'mustang': 'Huerfano',
            'farisita': 'Huerfano',
            'malachite': 'Huerfano',
            'spanish peaks': 'Huerfano',
            'stonewall': 'Las Animas',
            'valdez': 'Las Animas',
            'weston': 'Las Animas',
            'sopris': 'Las Animas',
            'berwind': 'Las Animas',
            'ludlow': 'Las Animas',
            'tabasco': 'Las Animas',
            'morley': 'Las Animas',
            'cokedale': 'Las Animas',
            'madrid': 'Las Animas',
            'primero': 'Las Animas',
            'segundo': 'Las Animas',
            'tercio': 'Las Animas',
            'cuatro': 'Las Animas',
            'jansen': 'Las Animas',
            'hoehne': 'Las Animas',
            'model': 'Las Animas',
            'thatcher': 'Las Animas',
            'tyrone': 'Las Animas',
            'van bremer': 'Las Animas',
            'vigil': 'Las Animas',
            'wootton': 'Las Animas',
        }
    
    def get_county_for_city(self, city_name):
        """Get the county for a given city name"""
        if pd.isna(city_name):
            return None
        return self.city_to_county.get(city_name.lower())
    
    def create_county_choropleth_map(self, matched_data, map_style="carto-positron"):
        """Create a choropleth map showing job distribution by county"""
        # Filter to only matched data
        matched_subset = matched_data[matched_data['matched_city'].notna()].copy()
        
        if len(matched_subset) == 0:
            # Return empty map if no matched data
            fig = go.Figure()
            fig.add_annotation(
                text="No matched data to display",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        # Add county information to matched data
        matched_subset['county'] = matched_subset['matched_city'].apply(self.get_county_for_city)
        
        # Count jobs by county
        county_counts = matched_subset.groupby('county').size().reset_index()
        county_counts.columns = ['county', 'job_count']
        county_counts = county_counts[county_counts['county'].notna()]
        
        if len(county_counts) == 0:
            fig = go.Figure()
            fig.add_annotation(
                text="No county data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        # Load Colorado counties GeoJSON
        try:
            import json
            with open("data/colorado_counties.geojson") as f:
                counties_geojson = json.load(f)
        except:
            # Fallback to scatter plot if GeoJSON not available
            return self._create_fallback_county_map(county_counts, map_style)
        
        # Create choropleth map
        fig = px.choropleth(
            county_counts,
            geojson=counties_geojson,
            locations='county',
            color='job_count',
            featureidkey="properties.NAME",
            color_continuous_scale="Viridis",
            title="Job Distribution by Colorado County",
            labels={'job_count': 'Number of Jobs', 'county': 'County'}
        )
        
        # Update layout for Colorado focus
        fig.update_geos(
            fitbounds="locations",
            visible=False
        )
        
        fig.update_layout(
            title_x=0.5,
            geo=dict(
                showframe=False,
                showcoastlines=False,
                projection_type='mercator'
            ),
            height=600
        )
        
        return fig
    
    def _create_fallback_county_map(self, county_counts, map_style):
        """Create a fallback scatter plot if GeoJSON is not available"""
        # Approximate county centers (you could expand this)
        county_centers = {
            'Denver': {'lat': 39.7392, 'lon': -104.9903},
            'Jefferson': {'lat': 39.5777, 'lon': -105.1369},
            'Arapahoe': {'lat': 39.6103, 'lon': -104.8197},
            'Adams': {'lat': 39.8764, 'lon': -104.7688},
            'Boulder': {'lat': 40.0150, 'lon': -105.2705},
            'El Paso': {'lat': 38.8339, 'lon': -104.8214},
            'Larimer': {'lat': 40.5853, 'lon': -105.0844},
            'Weld': {'lat': 40.4233, 'lon': -104.7091},
            'Mesa': {'lat': 39.0639, 'lon': -108.5506},
            'Pueblo': {'lat': 38.2544, 'lon': -104.6091}
        }
        
        # Add coordinates to county data
        county_counts['lat'] = county_counts['county'].map(lambda x: county_centers.get(x, {}).get('lat'))
        county_counts['lon'] = county_counts['county'].map(lambda x: county_centers.get(x, {}).get('lon'))
        
        # Filter out counties without coordinates
        county_counts = county_counts.dropna(subset=['lat', 'lon'])
        
        if len(county_counts) == 0:
            fig = go.Figure()
            fig.add_annotation(
                text="No geographic data available for counties",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        # Create scatter plot
        fig = px.scatter_mapbox(
            county_counts,
            lat='lat',
            lon='lon',
            size='job_count',
            color='job_count',
            hover_name='county',
            hover_data={'job_count': True, 'lat': False, 'lon': False},
            color_continuous_scale="Viridis",
            size_max=50,
            zoom=6,
            mapbox_style=map_style,
            title="Job Distribution by Colorado County"
        )
        
        fig.update_layout(
            title_x=0.5,
            height=600,
            mapbox=dict(
                center=dict(lat=39.5, lon=-105.5)
            )
        )
        
        return fig
