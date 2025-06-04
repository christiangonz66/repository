import pandas as pd
import re
from fuzzywuzzy import fuzz, process

class LocationMatcher:
    """
    Utility class for matching job locations to Colorado cities using fuzzy string matching
    """
    
    def __init__(self, cities_df):
        """
        Initialize the LocationMatcher with Colorado cities data
        
        Args:
            cities_df (pd.DataFrame): DataFrame containing city names
        """
        self.cities_df = cities_df
        self.city_names = cities_df['City'].tolist()
        
        # Create variations of city names for better matching
        self.city_variations = self._create_city_variations()
    
    def _create_city_variations(self):
        """
        Create variations of city names to improve matching accuracy
        
        Returns:
            dict: Dictionary mapping variations to official city names
        """
        variations = {}
        
        for city in self.city_names:
            # Add original name
            variations[city.lower()] = city
            
            # Add name without spaces
            variations[city.lower().replace(' ', '')] = city
            
            # Add common abbreviations and variations
            if city == "Colorado Springs":
                variations["colo springs"] = city
                variations["colorado spring"] = city
                variations["co springs"] = city
                variations["springs"] = city
            elif city == "Fort Collins":
                variations["ft collins"] = city
                variations["fort collin"] = city
                variations["ft collin"] = city
            elif city == "Grand Junction":
                variations["grand jct"] = city
                variations["grand jnct"] = city
                variations["gj"] = city
            elif city == "Castle Rock":
                variations["castle rock"] = city
                variations["castlerock"] = city
            elif city == "Highlands Ranch":
                variations["highlands ranch"] = city
                variations["hr"] = city
            elif city == "Security-Widefield":
                variations["security"] = city
                variations["widefield"] = city
            
        return variations
    
    def _clean_location(self, location):
        """
        Clean and normalize location strings
        
        Args:
            location (str): Raw location string
            
        Returns:
            str: Cleaned location string
        """
        if pd.isna(location) or location == "" or str(location).strip() == "":
            return ""
        
        # Convert to string and lowercase
        location = str(location).lower().strip()
        
        # Remove common suffixes and prefixes
        location = re.sub(r'\b(co|colorado|usa|us|united states)\b', '', location)
        
        # Remove special characters and extra spaces
        location = re.sub(r'[^\w\s]', ' ', location)
        location = re.sub(r'\s+', ' ', location)
        
        return location.strip()
    
    def _extract_city_from_location(self, location):
        """
        Extract city name from location string
        
        Args:
            location (str): Location string that might contain city, state, country info
            
        Returns:
            str: Extracted city name
        """
        cleaned = self._clean_location(location)
        
        # Split by common separators and take the first part (usually the city)
        parts = re.split(r'[,;]', cleaned)
        if parts:
            city_part = parts[0].strip()
            
            # Remove common words that might appear before city names
            city_part = re.sub(r'\b(remote|hybrid|onsite|office|downtown|metro|area)\b', '', city_part)
            city_part = city_part.strip()
            
            return city_part
        
        return cleaned
    
    def match_location_to_city(self, location, fuzzy_threshold=80):
        """
        Match a single location to a Colorado city
        
        Args:
            location (str): Location string to match
            fuzzy_threshold (int): Minimum fuzzy matching score (0-100)
            
        Returns:
            tuple: (matched_city, confidence_score) or (None, 0) if no match
        """
        if pd.isna(location) or location == "":
            return None, 0
        
        city_part = self._extract_city_from_location(location)
        
        # First, try exact match with variations
        if city_part in self.city_variations:
            return self.city_variations[city_part], 100
        
        # If no exact match, use fuzzy matching
        best_match = process.extractOne(
            city_part, 
            self.city_names, 
            scorer=fuzz.token_sort_ratio
        )
        
        if best_match and best_match[1] >= fuzzy_threshold:
            return best_match[0], best_match[1]
        
        # Try fuzzy matching with variations
        variation_matches = process.extractOne(
            city_part,
            list(self.city_variations.keys()),
            scorer=fuzz.token_sort_ratio
        )
        
        if variation_matches and variation_matches[1] >= fuzzy_threshold:
            matched_variation = variation_matches[0]
            return self.city_variations[matched_variation], variation_matches[1]
        
        return None, 0
    
    def match_locations(self, job_data, fuzzy_threshold=80):
        """
        Match all locations in the job data to Colorado cities
        
        Args:
            job_data (pd.DataFrame): DataFrame containing job data with 'location' column
            fuzzy_threshold (int): Minimum fuzzy matching score (0-100)
            
        Returns:
            pd.DataFrame: Original data with added columns for matched cities and confidence
        """
        # Create a copy of the data to avoid modifying the original
        result_df = job_data.copy()
        
        # Initialize new columns
        result_df['matched_city'] = None
        result_df['match_confidence'] = 0
        
        # Process each location
        for idx, row in result_df.iterrows():
            location = row['location']
            matched_city, confidence = self.match_location_to_city(location, fuzzy_threshold)
            
            result_df.loc[idx, 'matched_city'] = matched_city
            result_df.loc[idx, 'match_confidence'] = confidence
        
        return result_df
    
    def get_matching_stats(self, matched_data):
        """
        Get statistics about the matching process
        
        Args:
            matched_data (pd.DataFrame): DataFrame with matching results
            
        Returns:
            dict: Dictionary containing matching statistics
        """
        total_jobs = len(matched_data)
        matched_jobs = len(matched_data[matched_data['matched_city'].notna()])
        unmatched_jobs = total_jobs - matched_jobs
        
        match_rate = (matched_jobs / total_jobs * 100) if total_jobs > 0 else 0
        
        # Get top unmatched locations
        unmatched_locations = matched_data[matched_data['matched_city'].isna()]['location'].value_counts().head(5)
        
        # Get average confidence for matched locations
        avg_confidence = matched_data[matched_data['matched_city'].notna()]['match_confidence'].mean()
        
        return {
            'total_jobs': total_jobs,
            'matched_jobs': matched_jobs,
            'unmatched_jobs': unmatched_jobs,
            'match_rate': round(match_rate, 2),
            'average_confidence': round(avg_confidence, 2) if not pd.isna(avg_confidence) else 0,
            'top_unmatched_locations': unmatched_locations.to_dict()
        }
