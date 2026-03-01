"""
SiagaAI Backend - Flask Application
Disaster Preparedness Platform API
BMKG Integration + All Indonesian Cities + Complete Data
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json
import random
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from datetime import timedelta

# Import auth module
from auth import register_auth_routes
from admin import register_admin_routes

# Load environment variables
load_dotenv()

# Admin secret
ADMIN_SECRET = os.getenv('ADMIN_SECRET', 'siagaAI-admin-2024-secret')

app = Flask(__name__)
CORS(app)

# All Indonesian Cities with coordinates
INDONESIAN_CITIES = [
    {"id": "jakarta", "name": "Jakarta", "lat": -6.2088, "lng": 106.8456, "province": "DKI Jakarta"},
    {"id": "surabaya", "name": "Surabaya", "lat": -7.2575, "lng": 112.7521, "province": "Jawa Timur"},
    {"id": "bandung", "name": "Bandung", "lat": -6.9175, "lng": 107.6191, "province": "Jawa Barat"},
    {"id": "medan", "name": "Medan", "lat": 3.5952, "lng": 98.6722, "province": "Sumatera Utara"},
    {"id": "semarang", "name": "Semarang", "lat": -6.9667, "lng": 110.4208, "province": "Jawa Tengah"},
    {"id": "makassar", "name": "Makassar", "lat": -5.1427, "lng": 119.4128, "province": "Sulawesi Selatan"},
    {"id": "palembang", "name": "Palembang", "lat": -2.9913, "lng": 104.7618, "province": "Sumatera Selatan"},
    {"id": "tangerang", "name": "Tangerang", "lat": -6.1781, "lng": 106.6299, "province": "Banten"},
    {"id": "depok", "name": "Depok", "lat": -6.4025, "lng": 106.7942, "province": "Jawa Barat"},
    {"id": "bogor", "name": "Bogor", "lat": -6.5950, "lng": 106.8162, "province": "Jawa Barat"},
    {"id": "yogyakarta", "name": "Yogyakarta", "lat": -7.7956, "lng": 110.3695, "province": "DI Yogyakarta"},
    {"id": "malang", "name": "Malang", "lat": -7.9785, "lng": 112.6311, "province": "Jawa Timur"},
    {"id": "solo", "name": "Solo", "lat": -7.5755, "lng": 110.8243, "province": "Jawa Tengah"},
    {"id": "bekasi", "name": "Bekasi", "lat": -6.2297, "lng": 106.9853, "province": "Jawa Barat"},
    {"id": "denpasar", "name": "Denpasar", "lat": -8.6525, "lng": 115.2192, "province": "Bali"},
    {"id": "pontianak", "name": "Pontianak", "lat": -0.0227, "lng": 109.3425, "province": "Kalimantan Barat"},
    {"id": "banjarmasin", "name": "Banjarmasin", "lat": -3.3194, "lng": 114.5908, "province": "Kalimantan Selatan"},
    {"id": "padang", "name": "Padang", "lat": -0.9484, "lng": 100.3617, "province": "Sumatera Barat"},
    {"id": "pekanbaru", "name": "Pekanbaru", "lat": 0.5071, "lng": 101.4478, "province": "Riau"},
    {"id": "jambi", "name": "Jambi", "lat": -1.4852, "lng": 103.6158, "province": "Jambi"},
]

# BMKG City Codes for weather API
BMKG_CITY_CODES = {
    "jakarta": "31.71.01.1001",
    "surabaya": "31.78.01.1001",
    "bandung": "32.73.01.1001",
    "medan": "12.71.01.1001",
    "semarang": "33.74.01.1001",
    "makassar": "73.71.01.1001",
    "palembang": "16.71.01.1001",
    "tangerang": "36.73.01.1001",
    "depok": "32.71.01.1004",
    "bogor": "32.71.01.1001",
    "yogyakarta": "34.74.01.1001",
    "malang": "31.73.01.1007",
    "solo": "33.71.01.1001",
    "bekasi": "32.71.01.1002",
    "denpasar": "51.71.01.1001",
    "pontianak": "61.71.01.1001",
    "banjarmasin": "63.71.01.1001",
    "padang": "13.71.01.1001",
    "pekanbaru": "14.71.01.1001",
}

# BMKG API Headers
BMKG_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9,id;q=0.8',
    'Referer': 'https://cuaca.bmkg.go.id/',
    'Origin': 'https://cuaca.bmkg.go.id'
}

# ==================== BMKG API Functions ====================

def fetch_bmkg_weather(city_id):
    """Fetch weather data directly from BMKG API"""
    bmkg_code = BMKG_CITY_CODES.get(city_id, "31.71.01.1001")
    url = f"https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4={bmkg_code}"
    
    try:
        response = requests.get(url, headers=BMKG_HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            result = parse_bmkg_weather_data(data)
            if result:
                return result
    except Exception as e:
        print(f"Error fetching BMKG weather: {e}")
    
    # Fallback: return simulated weather data if BMKG fails
    return get_fallback_weather(city_id)

def get_fallback_weather(city_id):
    """Return fallback weather data when BMKG is unavailable"""
    city_name = next((c['name'] for c in INDONESIAN_CITIES if c['id'] == city_id), 'Unknown')
    
    # Simulate realistic weather based on time of day
    import random
    hour = datetime.now().hour
    
    # Jakarta typical weather
    temps = [26, 27, 28, 29, 30, 31, 32]
    humidities = [70, 75, 80, 85, 90]
    wind_speeds = [5, 10, 15, 20]
    
    return {
        'source': 'Fallback',
        'temperature': random.choice(temps),
        'humidity': random.choice(humidities),
        'wind_speed': random.choice(wind_speeds),
        'wind_direction': 'SE',
        'weather_code': random.randint(0, 3),
        'weather_desc': 'Cerah berawan',
        'local_datetime': datetime.now().isoformat(),
        'visibility': '10',
        'uv_index': str(random.randint(3, 8)),
        'forecast': [],
        'city': city_name
    }

def parse_bmkg_weather_data(data):
    """Parse BMKG weather data to our format"""
    try:
        if not data or 'data' not in data or len(data['data']) == 0:
            return None
            
        data_item = data['data'][0]
        
        # Handle case where data_item might be a list instead of dict
        if isinstance(data_item, list):
            cuaca_data = data_item
        else:
            cuaca_data = data_item.get('cuaca', [])
        
        if not cuaca_data:
            return None
            
        # Get current hour forecast (first available)
        current = cuaca_data[0] if cuaca_data else {}
        
        # Handle case where current might be a list
        if isinstance(current, list):
            current = current[0] if current else {}
        
        # Safely get values from current dict
        def safe_get(d, key, default='N/A'):
            if isinstance(d, dict):
                return d.get(key, default)
            return default
        
        return {
            'source': 'BMKG',
            'temperature': safe_get(current, 't', 'N/A'),
            'humidity': safe_get(current, 'hu', 'N/A'),
            'wind_speed': safe_get(current, 'ws', 'N/A'),
            'wind_direction': safe_get(current, 'wd', 'N/A'),
            'weather_code': int(safe_get(current, 'weather_code', 0)) if safe_get(current, 'weather_code', 0) != 'N/A' else 0,
            'weather_desc': safe_get(current, 'weather_desc', 'Unknown'),
            'local_datetime': safe_get(current, 'local_datetime', ''),
            'visibility': safe_get(current, 'vs', '10'),
            'uv_index': safe_get(current, 'uv', '5'),
            'forecast': cuaca_data[:8] if len(cuaca_data) > 8 else cuaca_data
        }
    except Exception as e:
        print(f"Error parsing BMKG weather: {e}")
        return None

def fetch_bmkg_earthquake():
    """Fetch latest earthquake data from BMKG API"""
    url = "https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json"
    
    try:
        response = requests.get(url, headers=BMKG_HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return parse_bmkg_earthquake_data(data)
    except Exception as e:
        print(f"Error fetching BMKG earthquake: {e}")
    
    return None

def parse_bmkg_earthquake_data(data):
    """Parse BMKG earthquake data to our format"""
    try:
        if not data or 'Gempa' not in data:
            return None
            
        g = data['Gempa']
        coords = g.get('point', {}).get('coordinates', '0,0').split(',')
        
        return {
            'source': 'BMKG',
            'datetime': g.get('DateTime', ''),
            'date': g.get('Tanggal', ''),
            'time': g.get('Jam', ''),
            'magnitude': g.get('Magnitude', 'N/A'),
            'depth': g.get('Kedalaman', 'N/A'),
            'latitude': coords[1] if len(coords) > 1 else '0',
            'longitude': coords[0] if len(coords) > 0 else '0',
            'location': g.get('Wilayah', 'Unknown'),
            'potential': g.get('Potensi', ''),
            'felt': g.get('Dirasakan', ''),
            'shakemap': g.get('Shakemap', '')
        }
    except Exception as e:
        print(f"Error parsing BMKG earthquake: {e}")
        return None

def fetch_bmkg_earthquakes_felt():
    """Fetch recent felt earthquakes from BMKG API"""
    url = "https://data.bmkg.go.id/DataMKG/TEWS/gempadirasakan.json"
    
    try:
        response = requests.get(url, headers=BMKG_HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return parse_bmkg_earthquakes_felt_data(data)
    except Exception as e:
        print(f"Error fetching BMKG earthquakes felt: {e}")
    
    return []

def parse_bmkg_earthquakes_felt_data(data):
    """Parse BMKG felt earthquakes data"""
    earthquakes = []
    try:
        if not data or 'gempa' not in data:
            return earthquakes
            
        for g in data['gempa'][:15]:  # Max 15 earthquakes
            coords = g.get('point', {}).get('coordinates', '0,0').split(',')
            earthquakes.append({
                'datetime': g.get('DateTime', ''),
                'date': g.get('Tanggal', ''),
                'time': g.get('Jam', ''),
                'magnitude': g.get('Magnitude', 'N/A'),
                'depth': g.get('Kedalaman', 'N/A'),
                'latitude': coords[1] if len(coords) > 1 else '0',
                'longitude': coords[0] if len(coords) > 0 else '0',
                'location': g.get('Wilayah', 'Unknown'),
                'felt': g.get('Dirasakan', '')
            })
    except Exception as e:
        print(f"Error parsing BMKG felt earthquakes: {e}")
    
    return earthquakes

def fetch_bmkg_early_warnings():
    """Fetch early warning alerts from BMKG API"""
    url = "https://www.bmkg.go.id/alerts/nowcast/id/rss.xml"
    
    try:
        response = requests.get(url, headers=BMKG_HEADERS, timeout=10)
        if response.status_code == 200:
            return parse_bmkg_early_warnings(response.text)
    except Exception as e:
        print(f"Error fetching BMKG early warnings: {e}")
    
    return []

def parse_bmkg_early_warnings(xml_content):
    """Parse BMKG early warning RSS feed"""
    warnings = []
    try:
        root = ET.fromstring(xml_content)
        for item in root.findall('.//item'):
            title = item.find('title')
            description = item.find('description')
            pubDate = item.find('pubDate')
            link = item.find('link')
            
            warnings.append({
                'title': title.text if title is not None else '',
                'description': description.text if description is not None else '',
                'pubDate': pubDate.text if pubDate is not None else '',
                'link': link.text if link is not None else ''
            })
    except Exception as e:
        print(f"Error parsing BMKG early warnings: {e}")
    
    return warnings

# ==================== Risk Zones Data ====================

# Risk zones for major cities
RISK_ZONES = [
    # Jakarta zones
    {"name": "Kali Ciliwung", "lat": -6.1950, "lng": 106.8500, "radius": 800, "risk": "high", "city": "jakarta", "type": "flood", "description": "Sungai utama Jakarta, seringk flood"},
    {"name": "Kali Angke", "lat": -6.1700, "lng": 106.7500, "radius": 500, "risk": "high", "city": "jakarta", "type": "flood", "description": "Daerah prone banjir"},
    {"name": "Kali Banjir", "lat": -6.2300, "lng": 106.9000, "radius": 600, "risk": "medium", "city": "jakarta", "type": "flood", "description": "Area genangan air"},
    {"name": "Muara Baru", "lat": -6.1100, "lng": 106.7500, "radius": 700, "risk": "high", "city": "jakarta", "type": "flood", "description": "Banjir rob dari laut"},
    {"name": "Pluit", "lat": -6.1100, "lng": 106.7800, "radius": 500, "risk": "medium", "city": "jakarta", "type": "flood", "description": "Daerah rendah"},
    
    # Bandung zones
    {"name": "Kawasan Bandung Utara", "lat": -6.8500, "lng": 107.5500, "radius": 1200, "risk": "high", "city": "bandung", "type": "landslide", "description": "Area lereng gunung"},
    {"name": "Cipanjalu", "lat": -6.7800, "lng": 107.5200, "radius": 800, "risk": "high", "city": "bandung", "type": "landslide", "description": "Daerah longsor aktif"},
    {"name": "Ciwidey", "lat": -7.0500, "lng": 107.3500, "radius": 600, "risk": "medium", "city": "bandung", "type": "landslide", "description": "Kawah gunung berapi"},
    {"name": "Sungai Brantas", "lat": -6.9200, "lng": 107.6500, "radius": 500, "risk": "medium", "city": "bandung", "type": "flood", "description": "Sungai utama"},
    
    # Bogor zones
    {"name": "Gunung Gede", "lat": -6.7800, "lng": 106.9500, "radius": 1000, "risk": "high", "city": "bogor", "type": "landslide", "description": "Gunungapi aktif"},
    {"name": "Sukabaya", "lat": -6.6000, "lng": 106.7500, "radius": 800, "risk": "high", "city": "bogor", "type": "flood", "description": "Daerah banjir"},
    {"name": "Puncak", "lat": -6.7800, "lng": 106.9200, "radius": 700, "risk": "medium", "city": "bogor", "type": "landslide", "description": "Area pegunungan"},
    
    # Semarang zones
    {"name": "Kali Semarang", "lat": -6.9500, "lng": 110.4200, "radius": 600, "risk": "high", "city": "semarang", "type": "flood", "description": "Sungai melintasi kota"},
    {"name": "Semarang Utara", "lat": -6.9500, "lng": 110.3500, "radius": 800, "risk": "high", "city": "semarang", "type": "flood", "description": "Daerah rob"},
    {"name": "Banjir Kanal", "lat": -7.0000, "lng": 110.4500, "radius": 500, "risk": "medium", "city": "semarang", "type": "flood", "description": "Sistem pengendali banjir"},
    
    # Surabaya zones
    {"name": "Sungai Brantas", "lat": -7.2500, "lng": 112.7500, "radius": 700, "risk": "medium", "city": "surabaya", "type": "flood", "description": "Sungai utama"},
    {"name": "Surabaya Timur", "lat": -7.3000, "lng": 112.8000, "radius": 600, "risk": "medium", "city": "surabaya", "type": "flood", "description": "Daerah rendah"},
    
    # Palembang zones
    {"name": "Sungai Musi", "lat": -2.9900, "lng": 104.7600, "radius": 900, "risk": "high", "city": "palembang", "type": "flood", "description": "Sungai besar"},
    {"name": "Seberang Ilir", "lat": -3.0500, "lng": 104.7000, "radius": 700, "risk": "high", "city": "palembang", "type": "flood", "description": "Daerah rob"},
    
    # Makassar zones
    {"name": "Sungai Tangka", "lat": -5.1500, "lng": 119.4000, "radius": 500, "risk": "medium", "city": "makassar", "type": "flood", "description": "Sungai melintasi kota"},
    {"name": "Makassar Utara", "lat": -5.1000, "lng": 119.3500, "radius": 600, "risk": "medium", "city": "makassar", "type": "flood", "description": "Daerah rendah"},
    
    # Yogyakarta zones
    {"name": "Kali Code", "lat": -7.8100, "lng": 110.3800, "radius": 500, "risk": "high", "city": "yogyakarta", "type": "flood", "description": "Sungai melintasi kota"},
    {"name": "Merapi", "lat": -7.5400, "lng": 110.4200, "radius": 1500, "risk": "high", "city": "yogyakarta", "type": "landslide", "description": "Gunungapi aktif"},
    
    # Medan zones
    {"name": "Sungai Deli", "lat": 3.6000, "lng": 98.6800, "radius": 500, "risk": "medium", "city": "medan", "type": "flood", "description": "Sungai melintasi kota"},
    
    # Padang zones
    {"name": "Batangangan", "lat": -0.9500, "lng": 100.3700, "radius": 800, "risk": "high", "city": "padang", "type": "landslide", "description": "Daerah curam"},
    {"name": "Pantai Padang", "lat": -0.9800, "lng": 100.3600, "radius": 400, "risk": "medium", "city": "padang", "type": "flood", "description": "Daerah tsunami"},
    
    # Pontianak zones
    {"name": "Sungai Kapuas", "lat": -0.0300, "lng": 109.3400, "radius": 1000, "risk": "high", "city": "pontianak", "type": "flood", "description": "Sungai terbesar"},
    {"name": "Pontianak Utara", "lat": 0.0200, "lng": 109.3000, "radius": 600, "risk": "high", "city": "pontianak", "type": "flood", "description": "Banjir rob"},
    
    # Banjarmasin zones
    {"name": "Sungai Barito", "lat": -3.3500, "lng": 114.5900, "radius": 800, "risk": "high", "city": "banjarmasin", "type": "flood", "description": "Sungai besar"},
    {"name": "Banjarmasin Utara", "lat": -3.4500, "lng": 114.6500, "radius": 600, "risk": "medium", "city": "banjarmasin", "type": "flood", "description": "Daerah rob"},
]

# Add risk zones for cities that don't have them
ADDITIONAL_RISK_ZONES = [
    # Bekasi
    {"name": "Sungai Cikeas", "lat": -6.2300, "lng": 106.9800, "radius": 500, "risk": "medium", "city": "bekasi", "type": "flood", "description": "Sungai melintasi kota"},
    
    # Tangerang
    {"name": "Sungai Cisadane", "lat": -6.2500, "lng": 106.6500, "radius": 600, "risk": "high", "city": "tangerang", "type": "flood", "description": "Sungai melintasi kota"},
    {"name": "Tangerang Selatan", "lat": -6.3400, "lng": 106.7300, "radius": 500, "risk": "medium", "city": "tangerang", "type": "flood", "description": "Daerah rendah"},
    
    # Depok
    {"name": "Sungai Ciliwung", "lat": -6.4000, "lng": 106.8200, "radius": 700, "risk": "high", "city": "depok", "type": "flood", "description": "Sungai melintasi kota"},
    
    # Malang
    {"name": "Kota Malang Selatan", "lat": -8.0200, "lng": 112.6300, "radius": 500, "risk": "medium", "city": "malang", "type": "flood", "description": "Daerah rendah"},
    {"name": "Gunung Arjuno", "lat": -7.9200, "lng": 112.5800, "radius": 800, "risk": "medium", "city": "malang", "type": "landslide", "description": "Area pegunungan"},
    
    # Solo
    {"name": "Sungai Bengawan Solo", "lat": -7.5600, "lng": 110.7500, "radius": 800, "risk": "high", "city": "solo", "type": "flood", "description": "Sungai besar"},
    {"name": "Solo Utara", "lat": -7.5500, "lng": 110.8000, "radius": 600, "risk": "medium", "city": "solo", "type": "flood", "description": "Daerah rendah"},
    
    # Denpasar
    {"name": "Denpasar Selatan", "lat": -8.7200, "lng": 115.2000, "radius": 500, "risk": "medium", "city": "denpasar", "type": "flood", "description": "Daerah rendah"},
    {"name": "Sungai Badung", "lat": -8.6500, "lng": 115.2300, "radius": 600, "risk": "high", "city": "denpasar", "type": "flood", "description": "Sungai melintasi kota"},
    
    # Padang
    {"name": "Pantai Barat Sumatera", "lat": -1.0000, "lng": 100.3500, "radius": 400, "risk": "medium", "city": "padang", "type": "tsunami", "description": "Zona tsunami"},
    
    # Pekanbaru
    {"name": "Sungai Siak", "lat": 0.5500, "lng": 101.4500, "radius": 700, "risk": "medium", "city": "pekanbaru", "type": "flood", "description": "Sungai melintasi kota"},
    
    # Jambi
    {"name": "Sungai Batang Hari", "lat": -1.6000, "lng": 103.6000, "radius": 800, "risk": "high", "city": "jambi", "type": "flood", "description": "Sungai terbesar di Jambi"},
]

# Merge additional data with main data
RISK_ZONES = RISK_ZONES + ADDITIONAL_RISK_ZONES

# ==================== Evacuation Points Data ====================

EVACUATION_POINTS = [
    # Jakarta evacuation points
    {"name": "Stadion Gelora Bung Karno", "lat": -6.2185, "lng": 106.8028, "city": "jakarta", "type": " stadium", "capacity": 50000},
    {"name": "Jakarta International Expo", "lat": -6.0655, "lng": 106.8819, "city": "jakarta", "type": "exhibition", "capacity": 20000},
    {"name": "Monas", "lat": -6.1754, "lng": 106.8272, "city": "jakarta", "type": "monument", "capacity": 10000},
    
    # Bandung evacuation points
    {"name": "Gedung Sate", "lat": -6.9146, "lng": 107.6189, "city": "bandung", "type": "government", "capacity": 5000},
    {"name": "Lapangan Gasibu", "lat": -6.9175, "lng": 107.6191, "city": "bandung", "type": "field", "capacity": 30000},
    {"name": "Sabuga ITB", "lat": -6.8906, "lng": 107.6107, "city": "bandung", "type": "building", "capacity": 10000},
    
    # Surabaya evacuation points
    {"name": "Gelora Bung Tomo", "lat": -7.2654, "lng": 112.7424, "city": "surabaya", "type": "stadium", "capacity": 40000},
    {"name": "Convention Hall", "lat": -7.2894, "lng": 112.7345, "city": "surabaya", "type": "exhibition", "capacity": 15000},
    
    # Semarang evacuation points
    {"name": "Louis Kuhup", "lat": -6.9667, "lng": 110.4208, "city": "semarang", "type": "stadium", "capacity": 20000},
    {"name": "Object", "lat": -6.9822, "lng": 110.3608, "city": "semarang", "type": "field", "capacity": 10000},
    
    # Yogyakarta evacuation points
    {"name": "Stadion Mandala Krida", "lat": -7.7819, "lng": 110.3727, "city": "yogyakarta", "type": "stadium", "capacity": 25000},
    {"name": "Gedungбя", "lat": -7.7956, "lng": 110.3695, "city": "yogyakarta", "type": "government", "capacity": 5000},
    
    # Makassar evacuation points
    {"name": "Stadion Mattoanging", "lat": -5.1427, "lng": 119.4128, "city": "makassar", "type": "stadium", "capacity": 20000},
    {"name": "Rujabgt", "lat": -5.1555, "lng": 119.4050, "city": "makassar", "type": "government", "capacity": 8000},
    
    # Palembang evacuation points
    {"name": "Stadion Gelora Sriwijaya", "lat": -2.9913, "lng": 104.7618, "city": "palembang", "type": "stadium", "capacity": 40000},
    {"name": "JSC", "lat": -2.9756, "lng": 104.7654, "city": "palembang", "type": "exhibition", "capacity": 15000},
    
    # Medan evacuation points
    {"name": "Stadion Teladan", "lat": 3.5952, "lng": 98.6722, "city": "medan", "type": "stadium", "capacity": 20000},
    {"name": "Fields", "lat": 3.5892, "lng": 98.6735, "city": "medan", "type": "field", "capacity": 10000},
    
    # Bogor evacuation points
    {"name": "Stadion Pakansari", "lat": -6.5950, "lng": 106.8162, "city": "bogor", "type": "stadium", "capacity": 30000},
    {"name": "Lapangan Merah", "lat": -6.6000, "lng": 106.8200, "city": "bogor", "type": "field", "capacity": 10000},
    
    # Padang evacuation points
    {"name": "Stadion Haji Agus Salim", "lat": -0.9484, "lng": 100.3617, "city": "padang", "type": "stadium", "capacity": 15000},
    {"name": "Lapangan Imam Bonjol", "lat": -0.9500, "lng": 100.3650, "city": "padang", "type": "field", "capacity": 8000},
    
    # Pontianak evacuation points
    {"name": "Stadion Sultan Syarafuddin", "lat": -0.0227, "lng": 109.3425, "city": "pontianak", "type": "stadium", "capacity": 15000},
    {"name": "Alun-alun Pontianak", "lat": -0.0300, "lng": 109.3400, "city": "pontianak", "type": "plaza", "capacity": 10000},
    
    # Banjarmasin evacuation points
    {"name": "Stadion Sports Barito", "lat": -3.3194, "lng": 114.5908, "city": "banjarmasin", "type": "stadium", "capacity": 20000},
    {"name": "Sungai Martapura", "lat": -3.3500, "lng": 114.6000, "city": "banjarmasin", "type": "river", "capacity": 5000},
]

# Add more evacuation points for other cities
ADDITIONAL_EVACUATION = [
    # Tangerang
    {"name": "Stadion Benteng", "lat": -6.1781, "lng": 106.6299, "city": "tangerang", "type": "stadium", "capacity": 15000},
    
    # Depok
    {"name": "Stadion Pasar Minggu", "lat": -6.3000, "lng": 106.8200, "city": "depok", "type": "stadium", "capacity": 10000},
    
    # Bekasi
    {"name": "Stadion Patriot", "lat": -6.2297, "lng": 106.9853, "city": "bekasi", "type": "stadium", "capacity": 15000},
    
    # Solo
    {"name": "Stadion Manahan", "lat": -7.5755, "lng": 110.3695, "city": "solo", "type": "stadium", "capacity": 25000},
    
    # Malang
    {"name": "Stadion Gajayana", "lat": -7.9785, "lng": 112.6311, "city": "malang", "type": "stadium", "capacity": 20000},
    
    # Denpasar
    {"name": "Stadion Ngurah Rai", "lat": -8.6525, "lng": 115.2192, "city": "denpasar", "type": "stadium", "capacity": 15000},
    
    # Pekanbaru
    {"name": "Stadion Utama", "lat": 0.5071, "lng": 101.4478, "city": "pekanbaru", "type": "stadium", "capacity": 15000},
    
    # Jambi
    {"name": "StadionKB", "lat": -1.4852, "lng": 103.6158, "city": "jambi", "type": "stadium", "capacity": 10000},
]

EVACUATION_POINTS = EVACUATION_POINTS + ADDITIONAL_EVACUATION

# ==================== API Routes ====================

@app.route('/')
def index():
    """API Health Check"""
    return jsonify({
        "name": "SiagaAI API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "cities": "/api/cities - List semua kota Indonesia",
            "weather": "/api/weather?city={city_id} - Data cuaca BMKG",
            "earthquake": "/api/earthquake - Gempa terakhir",
            "earthquakes_felt": "/api/earthquakes-felt - Gempa dirasakan",
            "early_warnings": "/api/early-warnings - Peringatan dini",
            "evacuation": "/api/evacuation?city={city_id} - Titik evakuasi",
            "risk-zones": "/api/risk-zones?city={city_id} - Zona risiko"
        }
    })

@app.route('/api/cities', methods=['GET'])
def get_cities():
    """Get all available cities"""
    return jsonify({
        "cities": INDONESIAN_CITIES,
        "count": len(INDONESIAN_CITIES)
    })

@app.route('/api/weather', methods=['GET'])
def get_weather():
    """Get weather data for a city"""
    city = request.args.get('city', 'jakarta')
    
    weather = fetch_bmkg_weather(city.lower())
    if weather:
        return jsonify(weather)
    
    return jsonify({
        "error": "Weather data tidak tersedia",
        "source": "BMKG API"
    })

@app.route('/api/earthquake', methods=['GET'])
def get_earthquake():
    """Get latest earthquake data"""
    earthquake = fetch_bmkg_earthquake()
    if earthquake:
        return jsonify(earthquake)
    
    return jsonify({
        "error": "Gempa tidak tersedia",
        "source": "BMKG API"
    })

@app.route('/api/earthquakes-felt', methods=['GET'])
def get_earthquakes_felt():
    """Get felt earthquakes"""
    earthquakes = fetch_bmkg_earthquakes_felt()
    return jsonify({
        "earthquakes": earthquakes,
        "count": len(earthquakes)
    })

@app.route('/api/early-warnings', methods=['GET'])
def get_early_warnings():
    """Get early warning alerts"""
    warnings = fetch_bmkg_early_warnings()
    return jsonify({
        "warnings": warnings,
        "count": len(warnings)
    })

@app.route('/api/risk', methods=['GET'])
def get_risk():
    """Get risk assessment for a city"""
    city = request.args.get('city', 'jakarta')
    city_info = next((c for c in INDONESIAN_CITIES if c['id'] == city), INDONESIAN_CITIES[0])
    
    weather = fetch_bmkg_weather(city)
    
    # Get risk zones for this city
    city_zones = [z for z in RISK_ZONES if z['city'] == city.lower()]
    high_risk_count = len([z for z in city_zones if z['risk'] == 'high'])
    
    # Determine overall risk level
    if high_risk_count > 0:
        alert_level = 'red'
        flood_risk = 'high'
    elif len(city_zones) > 0:
        alert_level = 'orange'
        flood_risk = 'medium'
    else:
        alert_level = 'green'
        flood_risk = 'low'
    
    # Generate recommendations based on risk level
    recommendations = []
    if alert_level == 'red':
        recommendations = [
            "Segera evacuate ke titik pengungsian terdekat",
            "Siapkan dokumen penting dan obat-obatan",
            "Ikuti instruksi dari petugas setempat",
            "Hindari daerah aliran sungai dan lereng gunung",
            "Matikan listrik dan gas jika memungkinkan"
        ]
    elif alert_level == 'orange':
        recommendations = [
            "Waspada terhadap perubahan cuaca",
            "Siapkan tas darurat",
            "Pantau informasi dari BMKG dan pemerintah daerah",
            "Hindari aktivitas di luar ruangan",
            "Jauhi daerah rentan bencana"
        ]
    else:
        recommendations = [
            "Tetap pemantauan kondisi cuaca",
            "Simpan nomor darurat terdekat",
            "Ketahui lokasi titik evakuasi",
            "Siapkan rencana keluarga jika terjadi bencana"
        ]
    
    descriptions = {
        'red': f'Peringatan! Tingkat risiko tinggi untuk kota {city_info["name"]}. Terdapat {high_risk_count} zona risiko tinggi. Segera lakukan evacuate jika diperlukan.',
        'orange': f'Peringatan Waspada untuk kota {city_info["name"]}. Terdapat {len(city_zones)} zona risiko. Tetap waspada.',
        'green': f'Kondisi aman untuk kota {city_info["name"]}. Tidak ada zona risiko tinggi.'
    }
    
    return jsonify({
        "city": city_info["name"],
        "province": city_info["province"],
        "alert_level": alert_level,
        "flood_risk": flood_risk,
        "landslide_risk": flood_risk,
        "description": descriptions[alert_level],
        "recommendations": recommendations,
        "weather": weather,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/evacuation', methods=['GET'])
def get_evacuation():
    """Get evacuation points"""
    city = request.args.get('city', None)
    
    if city:
        points = [p for p in EVACUATION_POINTS if p['city'] == city.lower()]
    else:
        points = EVACUATION_POINTS
    
    return jsonify({
        "points": points,
        "count": len(points)
    })

@app.route('/api/risk-zones', methods=['GET'])
def get_risk_zones():
    """Get all risk zones with weather data"""
    city = request.args.get('city', None)
    
    if city:
        zones = [z for z in RISK_ZONES if z['city'] == city.lower()]
    else:
        zones = RISK_ZONES
    
    # Get weather data for the city if specified
    weather_data = None
    if city:
        weather_data = fetch_bmkg_weather(city.lower())
    
    return jsonify({
        "zones": zones,
        "count": len(zones),
        "weather": weather_data
    })

# ==================== AI Chatbot ====================

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages with AI chatbot"""
    data = request.get_json()
    user_message = data.get('message', '')
    city = data.get('city', 'jakarta')
    
    if not user_message:
        return jsonify({"error": "Message is required"}), 400
    
    response = generate_emergency_response(user_message, city)
    
    return jsonify({
        "response": response,
        "timestamp": datetime.now().isoformat()
    })

def generate_emergency_response(message, city):
    """Generate contextual emergency response"""
    message_lower = message.lower()
    city_info = next((c for c in INDONESIAN_CITIES if c['id'] == city), INDONESIAN_CITIES[0])
    city_name = city_info['name']
    
    if any(k in message_lower for k in ['evakuasi', 'rute', 'keluar', 'lari']):
        points = [p for p in EVACUATION_POINTS if p['city'] == city.lower()]
        if points:
            points_list = "\n".join([f"- {p['name']} (Kapasitas: {p['capacity']})" for p in points[:5]])
            return f"🚑 Titik evakuasi di {city_name}:\n{points_list}\n\nSegera evacuate menggunakan jalur teraman!"
        return f"Belum ada data titik evakuasi untuk {city_name}"
    
    if any(k in message_lower for k in ['banjir', 'air', 'genangan']):
        zones = [z for z in RISK_ZONES if z['city'] == city.lower() and z['type'] == 'flood']
        if zones:
            high_risk = [z for z in zones if z['risk'] == 'high']
            if high_risk:
                return f"⚠️ Peringatan Banjir!\n\nZona banjir berbahaya di {city_name}:\n" + "\n".join([f"- {z['name']}: {z['description']}" for z in high_risk[:3]])
            return f"Ada {len(zones)} zona banjir di {city_name}. Tetap waspadai perubahan cuaca!"
        return f"Tidak ada informasi banjir khusus untuk {city_name}"
    
    if any(k in message_lower for k in ['gempa', '地震', 'quake']):
        earthquake = fetch_bmkg_earthquake()
        if earthquake:
            return f"🌍 Info Gempa Terbaru:\n\n📍 {earthquake.get('location')}\n💪 Magnitude: {earthquake.get('magnitude')}\n📏 Kedalaman: {earthquake.get('depth')}\n🕐 Waktu: {earthquake.get('time')}\n\n{earthquake.get('potential', '')}"
        return "Tidak ada informasi gempa terkini"
    
    if any(k in message_lower for k in ['cuaca', 'hujan', 'weather']):
        weather = fetch_bmkg_weather(city)
        if weather:
            return f"🌤️ Cuaca di {city_name}:\n\nSuhu: {weather.get('temperature')}°C\nKelembaban: {weather.get('humidity')}%\nAngin: {weather.get('wind_speed')} km/j\n\n{weather.get('weather_desc', 'Cuaca normal')}"
        return f"Cuaca untuk {city_name} tidak tersedia"
    
    if any(k in message_lower for k in ['longsor', 'gunung', 'lereng']):
        zones = [z for z in RISK_ZONES if z['city'] == city.lower() and z['type'] == 'landslide']
        if zones:
            high_risk = [z for z in zones if z['risk'] == 'high']
            if high_risk:
                return f"⚠️ Peringatan Longsor!\n\nZona longsor berbahaya di {city_name}:\n" + "\n".join([f"- {z['name']}: {z['description']}" for z in high_risk[:3]])
        return f"Tidak ada informasi longsor khusus untuk {city_name}"
    
    if any(k in message_lower for k in ['bantuan', 'help', 'darurat']):
        return f"📞 Kontak Darurat {city_name}:\n\n🚑 Ambulans: 118\n🚒 Pemadam: 113\n🏥 RS Terdekat: Hubungi dinas kesehatan kota\n\nTetten tenang dan ikuti instruksi petugas!"
    
    return f"""Halo! Saya SiagaAI, asisten tanggap darurat untuk {city_name}.

Saya bisa membantu Anda dengan:
🌧️ Info Cuaca terkini
🌍 Gempa terbaru
⚠️ Zona Risiko Banjir & Longsor
🚑 Titik Evakuasi
📞 Kontak Darurat

Silakan tanyakan sesuatu!"""

# ==================== Admin Routes ====================

# Simple in-memory admin storage (in production, use database)
ADMINS = {
    "admin": {"password": "siagaai2024", "role": "admin"},
    "operator": {"password": "siagaop2024", "role": "operator"}
}

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Admin login"""
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    
    if username in ADMINS and ADMINS[username]['password'] == password:
        return jsonify({
            "success": True,
            "user": {"username": username, "role": ADMINS[username]['role'], "secret": ADMIN_SECRET},
            "token": f"token_{username}_{datetime.now().timestamp()}"
        })
    
    return jsonify({"success": False, "error": "Invalid credentials"}), 401

@app.route('/api/reports', methods=['GET'])
def get_reports():
    """Get all damage reports"""
    try:
        from admin import reports_collection, users_collection
        
        city_count = len(INDONESIAN_CITIES)
        risk_zone_count = len(RISK_ZONES)
        evacuation_count = len(EVACUATION_POINTS)
        
        # Get user count from MongoDB
        user_count = 1  # Default admin
        try:
            if users_collection is not None:
                user_count += users_collection.count_documents({})
        except:
            pass
        
        # Get report count
        report_count = 0
        try:
            if reports_collection is not None:
                report_count = reports_collection.count_documents({})
        except:
            pass
        
        if reports_collection is not None:
            reports = list(reports_collection.find().sort('created_at', -1).limit(50))
            for r in reports:
                r['_id'] = str(r['_id'])
            return jsonify({
                "reports": reports,
                "count": len(reports),
                "stats": {
                    "cities": city_count,
                    "risk_zones": risk_zone_count,
                    "evacuation_points": evacuation_count,
                    "users": user_count,
                    "reports_count": report_count
                }
            })
    except Exception as e:
        print(f"Error getting reports: {e}")
    
    return jsonify({
        "reports": [],
        "count": 0,
        "stats": {
            "cities": len(INDONESIAN_CITIES),
            "risk_zones": len(RISK_ZONES),
            "evacuation_points": len(EVACUATION_POINTS),
            "users": 1,
            "reports_count": 0
        }
    })

# ==================== Stats API ====================

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get platform statistics"""
    try:
        from admin import users_collection, reports_collection
        
        city_count = len(INDONESIAN_CITIES)
        risk_zone_count = len(RISK_ZONES)
        evacuation_count = len(EVACUATION_POINTS)
        
        # Get user count from MongoDB (include admin = 1)
        user_count = 1  # Default admin
        try:
            if users_collection is not None:
                user_count += users_collection.count_documents({})
        except:
            pass
        
        # Get report count
        report_count = 0
        try:
            if reports_collection is not None:
                report_count = reports_collection.count_documents({})
        except:
            pass
        
        return jsonify({
            "cities": city_count,
            "risk_zones": risk_zone_count,
            "evacuation_points": evacuation_count,
            "users": user_count,
            "reports": report_count
        })
    except Exception as e:
        print(f"Error getting stats: {e}")
        return jsonify({
            "cities": len(INDONESIAN_CITIES),
            "risk_zones": len(RISK_ZONES),
            "evacuation_points": len(EVACUATION_POINTS),
            "users": 1,
            "reports": 0
        })

@app.route('/api/reports', methods=['POST'])
def create_report():
    """Create damage report"""
    data = request.get_json()
    
    # Try to save to MongoDB
    try:
        from admin import reports_collection
        if reports_collection is not None:
            report_doc = {
                'lat': data.get('lat', 0),
                'lng': data.get('lng', 0),
                'city': data.get('city', ''),
                'location': data.get('location', ''),
                'type': data.get('type', 'damage'),
                'severity': data.get('severity', 'medium'),
                'description': data.get('description', ''),
                'image_url': data.get('image_url', ''),
                'reporter_name': data.get('reporter_name', 'Anonim'),
                'reporter_phone': data.get('reporter_phone', ''),
                'status': 'pending',
                'created_at': datetime.now()
            }
            result = reports_collection.insert_one(report_doc)
            return jsonify({
                "success": True,
                "report": {
                    "id": str(result.inserted_id),
                    **data,
                    "timestamp": datetime.now().isoformat(),
                    "status": "pending"
                }
            })
    except Exception as e:
        print(f"Error saving report: {e}")
    
    # Fallback to mock response
    return jsonify({
        "success": True,
        "report": {
            "id": str(datetime.now().timestamp()),
            **data,
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }
    })


@app.route('/api/assess-damage', methods=['POST'])
def assess_damage():
    """Assess damage from uploaded image using Gemini AI"""
    data = request.get_json()
    image_data = data.get('image', '')
    
    if not image_data:
        return jsonify({
            "success": False,
            "error": "No image provided"
        }), 400
    
    try:
        import google.generativeai as genai
        import base64
        import io
        
        # Configure Gemini API
        GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyCLPAGL0auXjTWPpbSW0BfsTOybLKyeIZw')
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Use gemini-2.5-flash-image for image analysis
        model = genai.GenerativeModel('gemini-2.5-flash-image')
        
        # Extract image from base64 data URL if needed
        if ',' in image_data:
            # Format: data:image/jpeg;base64,XXXXX
            image_data = image_data.split(',')[1]
        
        # Create image part
        image_part = {
            'mime_type': 'image/jpeg',
            'data': base64.b64decode(image_data)
        }
        
        # Step 1: Check if image is a disaster
        disaster_check_prompt = """Analyze this image and determine if it shows a natural disaster or emergency situation.
        
        Disaster types to look for:
        - Banjir (Flood)
        - Gempa Bumi (Earthquake)
        - Tanah Longsor (Landslide)
        - Kebakaran (Fire)
        - Badai/Angin Kuat (Storm/Strong Wind)
        - Tsunami
        - Erupsi Gunung Berapi (Volcanic Eruption)
        - Kerusakan Struktur Gedung/Rumah (Building/ House Damage)
        
        Respond ONLY with this exact JSON format (no other text):
        {
            "is_disaster": true or false,
            "disaster_type": "specific type or null",
            "confidence": 0.0 to 1.0,
            "reason": "brief explanation"
        }"""
        
        # Create the content with image
        contents = [
            disaster_check_prompt,
            image_part
        ]
        
        response = model.generate_content(contents)
        
        # Parse the response
        import re
        import json
        
        # Extract JSON from response
        response_text = response.text
        json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
        
        if json_match:
            disaster_result = json.loads(json_match.group())
        else:
            # Try to parse the whole response
            disaster_result = json.loads(response_text)
        
        # Step 2: If not a disaster, reject the upload
        if not disaster_result.get('is_disaster', False):
            return jsonify({
                "success": False,
                "error": "Gambar yang Anda upload bukan foto bencana alam. Hanya foto bencana alam yang diperbolehkan untuk diupload.",
                "disaster_type": None,
                "is_disaster": False
            }), 400
        
        # Step 3: If it is a disaster, analyze the damage
        damage_analysis_prompt = f"""Analyze this disaster image and provide detailed damage assessment.
        
        Disaster Type: {disaster_result.get('disaster_type', 'Unknown')}
        
        Provide damage assessment in this exact JSON format:
        {{
            "severity": "low" or "medium" or "high" or "critical",
            "damage_description": "detailed description of visible damage",
            "affected_areas": ["list of affected areas/structures"],
            "recommended_actions": ["actionable recommendations"],
            "estimated_impact": "brief impact assessment"
        }}"""
        
        damage_contents = [
            damage_analysis_prompt,
            image_part
        ]
        damage_response = model.generate_content(damage_contents)
        
        # Parse damage response
        damage_text = damage_response.text
        damage_json_match = re.search(r'\{[^{}]*\}', damage_text, re.DOTALL)
        
        if damage_json_match:
            damage_result = json.loads(damage_json_match.group())
        else:
            damage_result = json.loads(damage_text)
        
        # Return success with both results
        return jsonify({
            "success": True,
            "is_disaster": True,
            "disaster_type": disaster_result.get('disaster_type'),
            "disaster_confidence": disaster_result.get('confidence', 0),
            "severity": damage_result.get('severity', 'medium'),
            "damage_type": disaster_result.get('disaster_type'),
            "damage_description": damage_result.get('damage_description', ''),
            "affected_areas": damage_result.get('affected_areas', []),
            "recommended_actions": damage_result.get('recommended_actions', []),
            "estimated_impact": damage_result.get('estimated_impact', ''),
            "confidence": disaster_result.get('confidence', 0.8)
        })
        
    except Exception as e:
        import traceback
        print(f"Error analyzing image with Gemini: {e}")
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": f"Error analyzing image: {str(e)}"
        }), 500

# ==================== Run App ====================

# Register auth routes
register_auth_routes(app)

# Register admin routes
register_admin_routes(app)

if __name__ == '__main__':
    print(f"🏙️ {len(INDONESIAN_CITIES)} Indonesian cities loaded")
    print(f"⚠️ {len(RISK_ZONES)} risk zones loaded")
    print(f"🏠 {len(EVACUATION_POINTS)} evacuation points loaded")
    app.run(debug=True, host='0.0.0.0', port=5000)
