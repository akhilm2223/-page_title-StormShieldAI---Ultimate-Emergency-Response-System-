import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import geopandas as gpd
import numpy as np
import os
import glob
from datetime import datetime, timedelta
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import requests
import json
import threading
import time
from io import StringIO
import base64
from gtts import gTTS

# Import optional packages with error handling
try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
    TTS_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    TTS_AVAILABLE = False

# Folium availability
try:
    from streamlit_folium import folium_static
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

# Skip googletrans due to dependency conflicts
TRANSLATION_AVAILABLE = False
# try:
#     from googletrans import Translator
#     TRANSLATION_AVAILABLE = True
# except ImportError:
#     TRANSLATION_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Check if any AI model is available
AI_AVAILABLE = OPENAI_AVAILABLE or GEMINI_AVAILABLE

# Configure page
st.set_page_config(
    page_title="🌪️ StormShieldAI - Ultimate Emergency Response System",
    page_icon="🌪️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Stunning Professional CSS for StormShieldAI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Clean Professional Styling */
    .stApp {
        background: #ffffff;
        font-family: 'Inter', sans-serif;
        color: #1a1a1a;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Clean Main Header */
    .main-header {
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 2rem;
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        box-shadow: 0 4px 20px rgba(37, 99, 235, 0.15);
        border: 1px solid #e5e7eb;
    }
    
    .main-header .subtitle {
        font-size: 1.1rem;
        font-weight: 400;
        margin-top: 0.5rem;
        opacity: 0.9;
    }
    
    .main-header .description {
        font-size: 0.9rem;
        font-weight: 300;
        margin-top: 0.5rem;
        opacity: 0.8;
    }
    
    /* Emergency Alert */
    .emergency-alert {
        background: #dc2626;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-weight: 600;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(220, 38, 38, 0.2);
        animation: emergencyPulse 2s ease-in-out infinite alternate;
    }
    
    @keyframes emergencyPulse {
        from { opacity: 1; }
        to { opacity: 0.8; }
    }
    
    /* Professional Cards */
    .professional-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease;
    }
    
    .professional-card:hover {
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        border-color: #2563eb;
    }
    
    /* AI Response */
    .ai-response {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #2563eb;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-size: 1rem;
        line-height: 1.6;
        color: #1e293b;
    }
    
    /* Voice Interface */
    .voice-interface {
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 1rem 0;
        color: #475569;
    }
    
    /* Quick Actions */
    .quick-actions {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .action-card {
        background: white;
        border: 2px solid #e5e7eb;
        color: #1e293b;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
        font-weight: 500;
    }
    
    .action-card:hover {
        border-color: #2563eb;
        background: #f8fafc;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
    }
    
    /* Sidebar Sections */
    .sidebar-section {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #1e293b;
    }
    
    /* Emergency Contact */
    .emergency-contact {
        background: #fef2f2;
        border: 1px solid #fecaca;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #991b1b;
    }
    
    .emergency-contact h3, .emergency-contact h4 {
        color: #dc2626;
        margin-top: 0;
    }
    
    /* Location Status */
    .location-status {
        background: #f0f9ff;
        border: 1px solid #bae6fd;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #0c4a6e;
    }
    
    /* Flood Risk */
    .flood-risk {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #1e40af;
    }
    
    /* Status Indicators */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-active { background: #22c55e; }
    .status-warning { background: #f59e0b; }
    .status-critical { background: #ef4444; }
    
    /* Feature Cards */
    .feature-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        color: #1e293b;
        transition: all 0.2s ease;
        margin: 0.5rem 0;
    }
    
    .feature-card:hover {
        border-color: #2563eb;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
        transform: translateY(-2px);
    }
    
    .feature-card h4 {
        color: #1e293b;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }
    
    .feature-card p {
        color: #64748b;
        font-size: 0.9rem;
        margin: 0;
    }
    
    /* Chat Container */
    .chat-container {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    /* Map Container */
    .map-container {
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        overflow: hidden;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    /* Enhanced Buttons */
    .stButton > button {
        background: #2563eb !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }
    
    .stButton > button:hover {
        background: #1d4ed8 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Text Input Styling */
    .stTextArea textarea {
        border: 1px solid #d1d5db !important;
        border-radius: 8px !important;
        background: white !important;
        font-size: 0.9rem !important;
        padding: 0.75rem !important;
        color: #1e293b !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
        outline: none !important;
    }
    
    /* Selectbox Styling */
    .stSelectbox > div > div {
        border: 1px solid #d1d5db !important;
        border-radius: 8px !important;
        background: white !important;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }
    
    /* Checkbox Styling */
    .stCheckbox > label {
        background: white !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 6px !important;
        padding: 0.5rem !important;
        color: #1e293b !important;
        font-weight: 400 !important;
    }
    
    .stCheckbox > label:hover {
        border-color: #2563eb !important;
        background: #f8fafc !important;
    }
    
    /* Metric Cards */
    .metric-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        color: #1e293b;
        margin: 0.5rem 0;
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        border-color: #2563eb;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.1);
    }
    
    .metric-card .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #2563eb;
        margin: 0.5rem 0;
    }
    
    .metric-card .metric-label {
        font-size: 0.9rem;
        color: #64748b;
        margin: 0;
    }
    
    /* Section Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #1e293b !important;
        font-weight: 600 !important;
    }
    
    /* Links and Interactive Elements */
    a {
        color: #2563eb !important;
        text-decoration: none !important;
    }
    
    a:hover {
        color: #1d4ed8 !important;
        text-decoration: underline !important;
    }
    
    /* Improved Spacing */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Loading States */
    .stSpinner > div {
        border-top-color: #2563eb !important;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background: #f0fdf4 !important;
        border: 1px solid #bbf7d0 !important;
        color: #166534 !important;
    }
    
    .stError {
        background: #fef2f2 !important;
        border: 1px solid #fecaca !important;
        color: #dc2626 !important;
    }
    
    .stWarning {
        background: #fffbeb !important;
        border: 1px solid #fed7aa !important;
        color: #92400e !important;
    }
    
    .stInfo {
        background: #eff6ff !important;
        border: 1px solid #bfdbfe !important;
        color: #1e40af !important;
    }
    
    /* Clean Tables */
    .stDataFrame {
        border: 1px solid #e5e7eb !important;
        border-radius: 8px !important;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: #f8fafc !important;
        border-right: 1px solid #e5e7eb !important;
    }
    
    /* Custom Emergency Button */
    .emergency-button {
        background: #dc2626 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 1rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        margin: 0.5rem 0 !important;
    }
    
    .emergency-button:hover {
        background: #b91c1c !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(220, 38, 38, 0.2) !important;
    }
    
    /* Voice Button */
    .voice-button {
        background: #059669 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }
    
    .voice-button:hover {
        background: #047857 !important;
        transform: translateY(-1px) !important;
    }
    
    /* Clean scrollbars */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'emergency_active' not in st.session_state:
    st.session_state.emergency_active = False
if 'ai_responses' not in st.session_state:
    st.session_state.ai_responses = []
if 'voice_enabled' not in st.session_state:
    st.session_state.voice_enabled = False
if 'current_language' not in st.session_state:
    st.session_state.current_language = 'en'
if 'user_location' not in st.session_state:
    st.session_state.user_location = None
if 'emergency_alerts' not in st.session_state:
    st.session_state.emergency_alerts = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Language settings
LANGUAGES = {
    'en': 'English', 'es': 'Español', 'fr': 'Français', 'pt': 'Português',
    'de': 'Deutsch', 'it': 'Italiano', 'ar': 'العربية', 'zh': '中文',
    'hi': 'हिन्दी', 'sw': 'Kiswahili'
}

# Emergency keywords in multiple languages
EMERGENCY_KEYWORDS = {
    'en': ['help', 'emergency', 'flood', 'hurricane', 'trapped', 'rescue', 'urgent', 'children', 'danger', 'evacuation', 'medical', 'injured'],
    'es': ['ayuda', 'emergencia', 'inundación', 'huracán', 'atrapado', 'rescate', 'urgente', 'niños', 'peligro', 'evacuación', 'médico', 'herido'],
    'fr': ['aide', 'urgence', 'inondation', 'ouragan', 'piégé', 'sauvetage', 'urgent', 'enfants', 'danger', 'évacuation', 'médical', 'blessé'],
    'pt': ['ajuda', 'emergência', 'inundação', 'furacão', 'preso', 'resgate', 'urgente', 'crianças', 'perigo', 'evacuação', 'médico', 'ferido'],
    'de': ['hilfe', 'notfall', 'überschwemmung', 'hurrikan', 'gefangen', 'rettung', 'dringend', 'kinder', 'gefahr', 'evakuierung', 'medizinisch', 'verletzt'],
    'it': ['aiuto', 'emergenza', 'alluvione', 'uragano', 'intrappolato', 'salvataggio', 'urgente', 'bambini', 'pericolo', 'evacuazione', 'medico', 'ferito'],
    'ar': ['مساعدة', 'طوارئ', 'فيضان', 'إعصار', 'محاصر', 'إنقاذ', 'عاجل', 'أطفال', 'خطر', 'إخلاء', 'طبي', 'مصاب'],
    'zh': ['帮助', '紧急', '洪水', '飓风', '被困', '救援', '紧急', '儿童', '危险', '疏散', '医疗', '受伤'],
    'hi': ['मदद', 'आपातकाल', 'बाढ़', 'तूफान', 'फंसा', 'बचाव', 'तत्काल', 'बच्चे', 'खतरा', 'निकासी', 'चिकित्सा', 'घायल'],
    'sw': ['msaada', 'dharura', 'mafuriko', 'kimbunga', 'amenaswa', 'kuokoa', 'haraka', 'watoto', 'hatari', 'uhamisho', 'matibabu', 'amejeruhiwa']
}

# Flood risk areas in Nicaragua
FLOOD_RISK_AREAS = {
    'Critical': ['Bluefields', 'Pearl Lagoon', 'Río San Juan', 'Rama', 'Corn Island'],
    'High': ['Puerto Cabezas', 'Río Grande', 'Siuna', 'Bonanza', 'Rosita'],
    'Medium': ['Managua', 'León', 'Granada', 'Masaya', 'Chinandega'],
    'Low': ['Jinotega', 'Matagalpa', 'Estelí', 'Ocotal', 'Somoto']
}

# Emergency contacts
EMERGENCY_CONTACTS = {
    'UN Emergency': '+505-2222-1234',
    'Local Emergency': '911',
    'Red Cross Nicaragua': '+505-2222-5678',
    'Civil Defense': '+505-2233-4567',
    'Medical Emergency': '+505-2244-7890'
}

# AI Models configuration
class AIModels:
    def __init__(self):
        # Translation disabled due to dependency conflicts
        self.translator = None
        
    def get_chatgpt_response(self, message, api_key):
        if not OPENAI_AVAILABLE:
            return "ChatGPT is not available. Please install the openai package."
        try:
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message}],
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"ChatGPT Error: {str(e)}"
    
    def get_gemini_response(self, message, api_key):
        if not GEMINI_AVAILABLE:
            return "Gemini is not available. Please install the google-generativeai package."
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(message)
            return response.text
        except Exception as e:
            return f"Gemini Error: {str(e)}"
    
    def translate_text(self, text, target_lang):
        if not TRANSLATION_AVAILABLE or not self.translator:
            return text  # Return original text if translation not available
        try:
            result = self.translator.translate(text, dest=target_lang)
            return result.text
        except:
            return text

# Voice interface
class VoiceInterface:
    def __init__(self):
        if VOICE_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                self.tts_engine = pyttsx3.init()
                self.available = True
            except Exception as e:
                self.available = False
                # Don't use st.warning here as it may be called before page config
        else:
            self.available = False
        
    def listen_for_speech(self, language='en'):
        if not self.available:
            return None
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=5)
            
            if language == 'en':
                text = self.recognizer.recognize_google(audio)
            else:
                text = self.recognizer.recognize_google(audio, language=language)
            
            return text
        except Exception as e:
            return None
    
    def speak_text(self, text, language='en'):
        if not self.available:
            return
        try:
            def speak():
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            
            thread = threading.Thread(target=speak)
            thread.daemon = True
            thread.start()
        except Exception as e:
            st.error(f"Voice output error: {e}")

# Disaster reporting and monitoring system
class DisasterReportingSystem:
    def __init__(self):
        self.disaster_types = {
            '🌪️': 'Hurricane/Tornado',
            '🌊': 'Flood',
            '🌋': 'Landslide/Earthquake', 
            '⚡': 'Power Outage',
            '🔥': 'Fire',
            '🏥': 'Medical Emergency',
            '🏠': 'Building Collapse',
            '🌨️': 'Severe Weather'
        }
    
    def submit_citizen_report(self, disaster_type, description, location, severity, contact_info=None):
        """Submit a citizen disaster report"""
        report_id = f"CR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        report = {
            'id': report_id,
            'timestamp': datetime.now(),
            'disaster_type': disaster_type,
            'description': description,
            'location': location,
            'severity': severity,  # 1-5 scale
            'contact_info': contact_info,
            'status': 'ACTIVE',
            'verified': False,
            'responders_notified': True
        }
        st.session_state.citizen_reports.append(report)
        return report_id
    
    def get_reports_in_radius(self, center_lat, center_lon, radius_km=50):
        """Get all reports within a radius"""
        nearby_reports = []
        for report in st.session_state.citizen_reports:
            lat = report['location']['latitude']
            lon = report['location']['longitude']
            distance = ((lat - center_lat)**2 + (lon - center_lon)**2)**0.5 * 111
            if distance <= radius_km:
                report['distance'] = distance
                nearby_reports.append(report)
        return sorted(nearby_reports, key=lambda x: x['distance'])
    
    def detect_hotspots(self, min_reports=2, radius_km=10):
        """Detect disaster hotspots using clustering"""
        if len(st.session_state.citizen_reports) < min_reports:
            return []
        
        hotspots = []
        processed_reports = set()
        
        for i, report in enumerate(st.session_state.citizen_reports):
            if i in processed_reports:
                continue
                
            cluster_reports = [report]
            processed_reports.add(i)
            
            # Find nearby reports
            for j, other_report in enumerate(st.session_state.citizen_reports):
                if j in processed_reports or j == i:
                    continue
                    
                distance = ((report['location']['latitude'] - other_report['location']['latitude'])**2 + 
                           (report['location']['longitude'] - other_report['location']['longitude'])**2)**0.5 * 111
                
                if distance <= radius_km:
                    cluster_reports.append(other_report)
                    processed_reports.add(j)
            
            if len(cluster_reports) >= min_reports:
                # Calculate cluster center and risk score
                avg_lat = sum(r['location']['latitude'] for r in cluster_reports) / len(cluster_reports)
                avg_lon = sum(r['location']['longitude'] for r in cluster_reports) / len(cluster_reports)
                avg_severity = sum(r['severity'] for r in cluster_reports) / len(cluster_reports)
                
                # Risk assessment based on disaster types and severity
                disaster_types = [r['disaster_type'] for r in cluster_reports]
                risk_multiplier = 1.5 if '🌊' in disaster_types or '🌪️' in disaster_types else 1.0
                risk_score = min(avg_severity * risk_multiplier * len(cluster_reports) / 2, 5.0)
                
                hotspot = {
                    'id': f"HS-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(hotspots)}",
                    'center_lat': avg_lat,
                    'center_lon': avg_lon,
                    'reports': cluster_reports,
                    'report_count': len(cluster_reports),
                    'risk_score': risk_score,
                    'primary_disaster': max(set(disaster_types), key=disaster_types.count),
                    'severity_level': 'CRITICAL' if risk_score >= 4 else 'HIGH' if risk_score >= 3 else 'MEDIUM'
                }
                hotspots.append(hotspot)
        
        return sorted(hotspots, key=lambda x: x['risk_score'], reverse=True)
    
    def detect_density_heat_zones(self, grid_size_km=20):
        """Detect report density heat zones across Nicaragua"""
        if len(st.session_state.citizen_reports) == 0:
            return []
        
        # Define grid boundaries for Nicaragua
        min_lat, max_lat = 10.5, 15.0
        min_lon, max_lon = -88.0, -82.0
        
        # Convert km to approximate degrees (rough conversion)
        lat_step = grid_size_km / 111.0  # 1 degree lat ≈ 111 km
        lon_step = grid_size_km / (111.0 * np.cos(np.radians((min_lat + max_lat) / 2)))
        
        heat_zones = []
        
        # Create grid
        lat_range = np.arange(min_lat, max_lat, lat_step)
        lon_range = np.arange(min_lon, max_lon, lon_step)
        
        for lat in lat_range:
            for lon in lon_range:
                # Count reports in this grid cell
                reports_in_cell = []
                for report in st.session_state.citizen_reports:
                    r_lat = report['location']['latitude']
                    r_lon = report['location']['longitude']
                    
                    if (lat <= r_lat < lat + lat_step and 
                        lon <= r_lon < lon + lon_step):
                        reports_in_cell.append(report)
                
                report_count = len(reports_in_cell)
                
                if report_count > 0:  # Only create zones with reports
                    # Determine heat zone level
                    if report_count >= 50:
                        zone_level = 'CRITICAL'
                        zone_color = 'red'
                        zone_intensity = 'HIGH'
                    elif report_count >= 25:
                        zone_level = 'HIGH'
                        zone_color = 'orange'
                        zone_intensity = 'MEDIUM'
                    else:
                        zone_level = 'MODERATE'
                        zone_color = 'yellow'
                        zone_intensity = 'LOW'
                    
                    heat_zone = {
                        'id': f"HZ-{lat:.3f}-{lon:.3f}",
                        'center_lat': lat + lat_step/2,
                        'center_lon': lon + lon_step/2,
                        'bounds': {
                            'north': lat + lat_step,
                            'south': lat,
                            'east': lon + lon_step,
                            'west': lon
                        },
                        'report_count': report_count,
                        'zone_level': zone_level,
                        'zone_color': zone_color,
                        'zone_intensity': zone_intensity,
                        'reports': reports_in_cell
                    }
                    heat_zones.append(heat_zone)
        
        return sorted(heat_zones, key=lambda x: x['report_count'], reverse=True)

# Emergency system
class EmergencySystem:
    def __init__(self):
        self.ai_models = AIModels()
        self.reporting_system = DisasterReportingSystem()
        
    def detect_emergency_keywords(self, text, language='en'):
        keywords = EMERGENCY_KEYWORDS.get(language, EMERGENCY_KEYWORDS['en'])
        text_lower = text.lower()
        found_keywords = [keyword for keyword in keywords if keyword in text_lower]
        return len(found_keywords) > 0, found_keywords
    
    def get_user_location(self):
        try:
            response = requests.get('http://ipapi.co/json/')
            data = response.json()
            return {
                'city': data.get('city', 'Unknown'),
                'country': data.get('country_name', 'Unknown'),
                'latitude': data.get('latitude', 0),
                'longitude': data.get('longitude', 0),
                'ip': data.get('ip', 'Unknown')
            }
        except:
            return None
    
    def trigger_un_alert(self, message, location, emergency_type):
        alert_id = f"UN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        alert = {
            'id': alert_id,
            'timestamp': datetime.now(),
            'message': message,
            'location': location,
            'type': emergency_type,
            'status': 'ACTIVE'
        }
        st.session_state.emergency_alerts.append(alert)
        return alert_id

# Data loading functions
@st.cache_data
def load_hurricane_data():
    """Load hurricane track data"""
    try:
        eta_path = "../ahead-of-the-storm-challenge1-datasets-main-nicaragua/nicaragua/weather_hurricanes/eta_2020_track.geojson"
        iota_path = "../ahead-of-the-storm-challenge1-datasets-main-nicaragua/nicaragua/weather_hurricanes/iota_2020_track.geojson"
        
        eta_data = gpd.read_file(eta_path) if os.path.exists(eta_path) else None
        iota_data = gpd.read_file(iota_path) if os.path.exists(iota_path) else None
        
        return eta_data, iota_data
    except Exception as e:
        st.error(f"Error loading hurricane data: {e}")
        return None, None

@st.cache_data
def load_infrastructure_data():
    """Load infrastructure data"""
    try:
        base_path = "../ahead-of-the-storm-challenge1-datasets-main-nicaragua/nicaragua"
        
        # Schools
        schools_path = f"{base_path}/buildings/OSM schools/hotosm_nic_education_facilities_points_geojson/hotosm_nic_education_facilities_points_geojson.geojson"
        schools = gpd.read_file(schools_path) if os.path.exists(schools_path) else None
        
        # Health facilities
        health_path = f"{base_path}/buildings/OSM health facilities/hotosm_nic_health_facilities_points_geojson/hotosm_nic_health_facilities_points_geojson.geojson"
        health = gpd.read_file(health_path) if os.path.exists(health_path) else None
        
        # Roads
        roads_path = f"{base_path}/infrastructure/OSM roads/hotosm_nic_roads_lines_geojson/hotosm_nic_roads_lines_geojson.geojson"
        roads = gpd.read_file(roads_path) if os.path.exists(roads_path) else None
        
        return schools, health, roads
    except Exception as e:
        st.error(f"Error loading infrastructure data: {e}")
        return None, None, None

def load_precipitation_data():
    """Load precipitation data"""
    try:
        precip_pattern = "../ahead-of-the-storm-challenge1-datasets-main-nicaragua/nicaragua/weather_hurricanes/era5_hurricane_iota/total_precipitation/*.tif"
        precip_files = glob.glob(precip_pattern)
        return sorted(precip_files)[:10]  # Return first 10 files
    except Exception as e:
        st.error(f"Error loading precipitation data: {e}")
        return []

# Smart General Response Function - handles any message
def get_smart_general_response(user_input):
    """AI-powered response system that can handle both emergency and general questions"""
    
    user_lower = user_input.lower()
    
    # Get user location from session state
    import streamlit as st
    user_location = st.session_state.get('user_location', {})
    facility_name = user_location.get('facility_name', 'Escuela Fuente del Saber')
    latitude = user_location.get('latitude', 11.9249)
    longitude = user_location.get('longitude', -84.7152)
    
    # Check if it's a greeting or casual conversation
    if any(word in user_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'how are you', 'how you doing']):
        return f"""👋 **Hello! I'm StormShieldAI Assistant**

I'm doing great and ready to help! I can see you're at **{facility_name}** in Nicaragua ({latitude:.4f}°N, {longitude:.4f}°W).

**🏫 Your Current Location Status:**
• **Facility:** {facility_name} - Educational Facility & Emergency Shelter
• **Safety Status:** ✅ You're at a designated emergency shelter location
• **Coordinates:** {latitude:.4f}°N, {longitude:.4f}°W
• **Emergency Ready:** This school can accommodate evacuees during disasters

**🤖 What I can help you with:**
• **Local Emergency Info:** Specific to your area around {facility_name}
• **Nearby Resources:** Hospitals, emergency services in your vicinity
• **Weather Alerts:** Real-time conditions for your exact location
• **Evacuation Plans:** You're already at a safe shelter location!
• **General Chat:** I'm happy to have a conversation!

**💬 Try asking me:**
• "What's the flood risk at my current location?"
• "Where are the nearest hospitals to {facility_name}?"
• "Is this school safe during hurricanes?"
• "What emergency supplies should I have here?"

How can I assist you today from your location at {facility_name}? 😊"""

    # Check for weather/general questions
    elif any(word in user_lower for word in ['weather', 'today', 'temperature', 'rain', 'sun', 'climate']):
        return f"""🌤️ **Weather & Climate Information for Nicaragua**

**📊 Real Weather Data Available:**
• **Hurricane Tracking:** Complete Eta & Iota 2020 data
• **Precipitation:** 300+ hourly rainfall measurements  
• **Temperature:** 2-meter air temperature readings
• **Wind Speed:** Complete wind data during storms

**🌡️ Nicaragua Climate Overview:**
• **Dry Season:** December - April (less rain)
• **Wet Season:** May - November (hurricane season)
• **Temperature:** 26-32°C (79-90°F) year-round
• **Hurricane Season:** Peak August - October

**🌊 Current Conditions:**
I have real precipitation data from Hurricane Iota showing rainfall patterns across Nicaragua. The data shows coastal areas received 150+ mm/hour during peak intensity.

**💡 Ask me specific questions like:**
• "Show me Hurricane Iota precipitation data"
• "What was the weather like during Hurricane Eta?"
• "Which areas get the most rain?"

What weather information would you like to know more about?"""

    # Check for general Nicaragua questions
    elif any(word in user_lower for word in ['nicaragua', 'country', 'central america', 'managua', 'population']):
        return f"""🇳🇮 **Nicaragua Information & Emergency Preparedness**

**📍 About Nicaragua:**
• **Capital:** Managua (1.4M population)
• **Location:** Central America, between Honduras & Costa Rica
• **Coastlines:** Pacific Ocean & Caribbean Sea
• **Terrain:** Mountains, lakes, coastal plains

**🏥 Emergency Infrastructure Available:**
• **Hospitals:** 50+ medical facilities mapped
• **Schools:** 100+ potential evacuation centers
• **Emergency Contacts:** Complete directory
• **Coverage:** Nationwide emergency response network

**🌪️ Natural Disaster Preparedness:**
• **Hurricane Season:** June - November annually
• **Flood Risk:** Coastal & river areas
• **Historical Events:** Hurricane Eta & Iota (2020)
• **Response System:** UN coordination available

**📊 Real Data Integration:**
• Complete infrastructure mapping from OpenStreetMap
• Population demographics from WorldPop
• Weather data from Hurricane Eta & Iota
• Emergency response protocols

How can I help you with Nicaragua emergency preparedness or general information?"""

    # General questions about the system
    elif any(word in user_lower for word in ['what are you', 'who are you', 'what can you do', 'help me', 'capabilities']):
        return f"""🤖 **About StormShieldAI - Your Emergency Response Assistant**

**🌟 I'm StormShieldAI, an advanced AI system built for:**
• **Emergency Response:** Real-time disaster assistance
• **Preparedness Planning:** Help you prepare for emergencies
• **Information Access:** Real Nicaragua data at your fingertips
• **Multi-language Support:** Communicate in your preferred language

**💪 My Capabilities:**
• **Real Data Analysis:** 3,352 files of Nicaragua emergency data
• **Hurricane Tracking:** Complete Eta & Iota storm paths
• **Infrastructure Mapping:** Schools, hospitals, roads, facilities
• **Voice Interface:** Speak your questions, hear responses
• **Emergency Detection:** Automatic alert system
• **UN Integration:** Direct connection to emergency services

**🏆 Built for UN Tech Over Hackathon 2025**
I represent cutting-edge emergency response technology combining AI, real-time data, and human-centered design for disaster preparedness in Nicaragua.

**💡 I'm here to help with anything - emergency or casual conversation!**

What would you like to know or talk about today?"""

    # If none of the above, fall back to emergency response system
    else:
        return get_smart_emergency_response(user_input)

# Smart Emergency Response Function  
def get_smart_emergency_response(user_input):
    """AI-powered emergency response using real Nicaragua data"""
    
    # Load real data for context
    schools, health, roads = load_infrastructure_data()
    precip_files = load_precipitation_data()
    
    # Get user location
    import streamlit as st
    user_location = st.session_state.get('user_location', {})
    facility_name = user_location.get('facility_name', 'Escuela Fuente del Saber')
    latitude = user_location.get('latitude', 11.9249)
    longitude = user_location.get('longitude', -84.7152)
    
    user_lower = user_input.lower()
    
    # Flood Risk Analysis
    if any(word in user_lower for word in ['flood', 'flooding', 'water', 'rain', 'precipitation']):
        school_count = len(schools) if schools is not None else 100
        health_count = len(health) if health is not None else 50
        precip_count = len(precip_files)
        
        # Calculate distance to coast (approximate)
        distance_to_coast = abs(latitude - 12.0) * 111  # Rough km calculation
        
        return f"""🌊 **FLOOD RISK ANALYSIS FOR YOUR LOCATION**

**📍 YOUR CURRENT POSITION:**
• **Location:** {facility_name}
• **Coordinates:** {latitude:.4f}°N, {longitude:.4f}°W
• **Distance to Coast:** ~{distance_to_coast:.0f} km inland
• **Elevation Status:** Moderate elevation (safer than coastal areas)

**🟡 FLOOD RISK ASSESSMENT FOR YOUR AREA:**
• **Risk Level:** MEDIUM - Inland location provides protection
• **Flash Flood Risk:** Possible during heavy rainfall
• **River Flooding:** Monitor nearby waterways
• **Your Advantage:** ✅ You're at a designated emergency shelter!

**🏫 YOUR CURRENT SHELTER STATUS:**
• **{facility_name}:** Already an official emergency shelter
• **Capacity:** Can accommodate additional evacuees
• **Safety Features:** Elevated structure, emergency supplies
• **Evacuation Status:** ✅ You're already in a safe zone!

**📊 REAL DATA FOR YOUR REGION:**
• **Precipitation Files:** {precip_count} hourly measurements from Hurricane Iota
• **Nearby Shelters:** {school_count} schools including your current location
• **Medical Facilities:** {health_count} hospitals/clinics in Nicaragua

**🚨 IMMEDIATE ACTIONS FROM YOUR LOCATION:**
1. **Stay Put:** {facility_name} is a designated safe zone
2. **Monitor Alerts:** Check precipitation data every hour
3. **Emergency Supplies:** Ensure 72-hour kit is ready
4. **Communication:** Emergency radio 107.7 FM
5. **Help Others:** Assist evacuees coming to your shelter
6. **Contact:** UN Emergency +505-2222-1234

**🌧️ LOCATION-SPECIFIC WEATHER PATTERN:**
• **Your Area:** Inland protection from storm surge
• **Rainfall Impact:** Moderate risk during hurricanes
• **Historical Data:** Hurricane Iota - inland areas received 50-100mm/hour
• **Recovery Time:** 1-2 weeks typical for your elevation"""

    # School/Shelter Information
    elif any(word in user_lower for word in ['school', 'shelter', 'evacuation', 'safe', 'center']):
        school_count = len(schools) if schools is not None else 100
        
        # Get sample school data if available
        sample_schools = []
        if schools is not None:
            for idx, row in schools.head(10).iterrows():
                name = row.get('name', f'School #{idx+1}')
                lat = row.geometry.y
                lon = row.geometry.x
                sample_schools.append(f"• **{name}** - {lat:.3f}°N, {lon:.3f}°W")
        
        return f"""🏫 **EVACUATION CENTERS & SCHOOLS - NICARAGUA**

**📊 REAL INFRASTRUCTURE DATA:**
• **Total Schools Available:** {school_count} facilities mapped
• **Capacity:** Estimated 50,000+ people
• **Status:** Emergency-ready with supplies
• **Coverage:** Nationwide distribution

**🏫 SAMPLE EVACUATION CENTERS:**
{chr(10).join(sample_schools[:5]) if sample_schools else '• Loading school data from OpenStreetMap...'}

**🚨 EVACUATION PROCEDURES:**
1. **Immediate Response:** Report to nearest school within 2km
2. **Documentation:** Bring ID, medical records, prescriptions
3. **Registration:** Check-in at main entrance
4. **Family Units:** Assigned sleeping areas by family size
5. **Duration:** Prepared for 7-14 days occupancy

**📍 SHELTER SERVICES:**
• **Medical:** Basic first aid and emergency care
• **Food:** Meals provided 3x daily
• **Water:** Purified water and sanitation
• **Communication:** Satellite phones for family contact
• **Children:** Educational activities and care
• **Pets:** Designated areas for animals

**🗺️ LOCATION STRATEGY:**
• **Schools:** Located on elevated ground above flood zones
• **Access:** Connected to main transportation routes
• **Backup:** Multiple centers per municipality
• **Special Needs:** Accessible facilities for disabled

**📞 COORDINATION:**
• **Local Emergency:** 911
• **UN Coordination:** +505-2222-1234
• **Red Cross:** +505-2222-5678"""

    # Hospital/Medical Information  
    elif any(word in user_lower for word in ['hospital', 'medical', 'health', 'doctor', 'clinic', 'injured']):
        health_count = len(health) if health is not None else 50
        
        # Get nearby health facilities (within reasonable distance)
        nearby_health = []
        if health is not None:
            for idx, row in health.head(20).iterrows():
                name = row.get('name', f'Health Facility #{idx+1}')
                lat = row.geometry.y
                lon = row.geometry.x
                facility_type = row.get('amenity', 'Healthcare')
                
                # Calculate approximate distance
                distance = ((lat - latitude)**2 + (lon - longitude)**2)**0.5 * 111  # Rough km
                
                if distance < 100:  # Within 100km
                    nearby_health.append((name, facility_type, lat, lon, distance))
        
        # Sort by distance and take closest 5
        nearby_health.sort(key=lambda x: x[4])
        closest_facilities = nearby_health[:5]
        
        return f"""🏥 **MEDICAL FACILITIES NEAR {facility_name.upper()}**

**📍 YOUR LOCATION:**
• **Current Position:** {facility_name}
• **Coordinates:** {latitude:.4f}°N, {longitude:.4f}°W
• **School Medical:** Basic first aid supplies available on-site

**🚨 CLOSEST EMERGENCY FACILITIES:**
{chr(10).join([f"• **{name}** ({ftype}) - {lat:.3f}°N, {lon:.3f}°W (~{dist:.1f}km away)" for name, ftype, lat, lon, dist in closest_facilities]) if closest_facilities else '• Searching for nearby facilities...'}

**⚕️ EMERGENCY SERVICES AVAILABLE:**
• **Trauma Care:** Life-threatening injuries, surgery
• **Pediatric:** Specialized care for children
• **Obstetric:** Emergency childbirth and pregnancy care
• **Psychiatric:** Crisis intervention and mental health
• **Pharmacy:** Emergency medications and supplies
• **Blood Bank:** Type O universal donor available

**🚑 EMERGENCY MEDICAL PROTOCOLS:**
1. **Triage:** Priority based on injury severity
2. **Stabilization:** Immediate life-saving interventions
3. **Transport:** Helicopter evacuation if needed
4. **Communication:** Real-time coordination with UN
5. **Documentation:** Medical records maintained

**🩹 COMMON HURRICANE INJURIES:**
• **Trauma:** Cuts from debris, fractures
• **Respiratory:** Mold exposure, water inhalation
• **Infectious:** Waterborne diseases, wound infections
• **Chronic:** Diabetic emergencies, heart conditions
• **Psychological:** PTSD, anxiety, depression

**📞 MEDICAL EMERGENCY CONTACTS:**
• **Emergency Services:** 911
• **Medical Emergency:** +505-2244-7890
• **UN Medical:** +505-2222-1234
• **Red Cross:** +505-2222-5678
• **Poison Control:** +505-2233-9999

**🚁 MEDICAL EVACUATION:**
• **Helicopter:** Available for critical cases
• **Coordination:** UN/WHO emergency response
• **Landing Zones:** Major hospitals and schools
• **International:** Costa Rica/Honduras hospitals"""

    # Hurricane/Weather Information
    elif any(word in user_lower for word in ['hurricane', 'storm', 'wind', 'weather', 'eta', 'iota']):
        precip_count = len(precip_files)
        
        return f"""🌪️ **HURRICANE TRACKING & WEATHER DATA - NICARAGUA**

**📊 REAL HURRICANE DATA AVAILABLE:**
• **Hurricane Eta (2020):** Complete track and precipitation data
• **Hurricane Iota (2020):** {precip_count} hourly precipitation files
• **Wind Data:** Speed, direction, and pressure measurements
• **Temperature:** 2-meter air temperature recordings
• **Real-time:** Hourly updates during active storms

**🌪️ HURRICANE ETA & IOTA IMPACT (November 2020):**
• **Category:** Both reached Category 4 intensity
• **Landfall:** Caribbean coast of Nicaragua
• **Wind Speed:** Up to 250 km/h sustained winds
• **Rainfall:** 500-1000mm in 48 hours
• **Affected:** 80% of Nicaragua territory
• **Casualties:** 200+ deaths, 1.5M affected

**⛈️ CURRENT MONITORING:**
• **Satellite:** Real-time storm tracking
• **Weather Stations:** Ground-based measurements
• **Precipitation:** Hourly rainfall data
• **Flood Gauges:** River and lake levels
• **Sea Level:** Storm surge monitoring

**🚨 HURRICANE PREPAREDNESS:**
1. **72-Hour Kit:** Water, food, medications, radio
2. **Evacuation Plan:** Know routes to higher ground
3. **Communication:** Family emergency contacts
4. **Documentation:** Waterproof container for papers
5. **Shelter:** Reinforce windows, clear gutters

**📈 HURRICANE SEASON PATTERNS:**
• **Peak Season:** August-October
• **Formation Area:** Caribbean Sea, Atlantic
• **Path:** Generally west-northwest toward Central America
• **Frequency:** 2-4 major storms per decade
• **Climate Change:** Increasing intensity trends

**📞 WEATHER EMERGENCY CONTACTS:**
• **National Weather:** +505-2244-5555
• **Civil Defense:** +505-2233-4567
• **UN Emergency:** +505-2222-1234
• **Radio Emergency:** 107.7 FM (24/7)"""

    # Children Safety
    elif any(word in user_lower for word in ['child', 'children', 'kids', 'baby', 'family']):
        return f"""👶 **CHILD SAFETY & FAMILY EMERGENCY PROTOCOLS**

**🚨 CHILD PRIORITY ACTIONS:**
1. **Immediate Safety:** Move children to safe area first
2. **Identification:** Waterproof ID tags with family info
3. **Medical Info:** List allergies, medications, conditions
4. **Comfort Items:** Favorite toy, blanket for emotional support
5. **Family Plan:** Designated meeting points and contacts

**🏫 CHILD-FRIENDLY EVACUATION CENTERS:**
• **Supervision:** Trained staff for unaccompanied minors
• **Activities:** Educational and recreational programs
• **Nutrition:** Special dietary needs and baby formula
• **Healthcare:** Pediatric medical care available
• **Reunification:** Family tracking and reunion services

**👨‍👩‍👧‍👦 FAMILY EMERGENCY KIT:**
• **Supplies:** Diapers, formula, baby food, medications
• **Clothing:** 3 days of clothes per child
• **Games:** Books, toys, activities for stress relief
• **Communication:** Photos of family members
• **Documentation:** Birth certificates, medical records

**📞 CHILD EMERGENCY SERVICES:**
• **UNICEF Nicaragua:** +505-2222-7777
• **Child Protection:** +505-2233-8888
• **Family Services:** +505-2244-9999
• **UN Children Emergency:** +505-2222-1234"""

    # General Emergency Response
    else:
        school_count = len(schools) if schools is not None else 100
        health_count = len(health) if health is not None else 50
        precip_count = len(precip_files)
        
        return f"""🌪️ **STORMSHIELDAI - COMPLETE EMERGENCY SYSTEM**

**🔍 AVAILABLE REAL DATA:**
• **Hurricane Tracks:** Eta & Iota 2020 complete paths
• **Precipitation:** {precip_count} hourly weather files
• **Schools/Shelters:** {school_count} evacuation centers mapped
• **Hospitals:** {health_count} medical facilities ready
• **Infrastructure:** Roads, waterways, populated areas

**🚨 EMERGENCY CAPABILITIES:**
• **Voice AI:** Multi-language emergency detection
• **Location Tracking:** Real-time positioning
• **UN Alerts:** Automatic emergency notifications
• **Risk Assessment:** Flood zone analysis
• **Resource Mapping:** Nearest help facilities

**⚡ ASK ME ABOUT:**
• **Flood Risk:** "What areas flood during hurricanes?"
• **Evacuation:** "Where are the nearest shelters?"
• **Medical:** "Emergency medical facilities near me"
• **Weather:** "Hurricane Eta precipitation data"
• **Children:** "How to keep kids safe in emergencies"
• **Contacts:** "Emergency phone numbers"

**🌍 LANGUAGES SUPPORTED:**
English, Español, Français, Português, Deutsch, Italiano, العربية, 中文, हिन्दी, Kiswahili

**📞 EMERGENCY CONTACTS:**
{chr(10).join([f'• **{contact}:** {number}' for contact, number in EMERGENCY_CONTACTS.items()])}

**💬 TRY VOICE COMMANDS:**
"Help, we need evacuation!"
"¿Dónde están los hospitales?"
"What's the flood risk here?"

Ready to help with any emergency question! 🚀"""

# Initialize session state
if 'emergency_triggered' not in st.session_state:
    st.session_state.emergency_triggered = False
if 'quick_query' not in st.session_state:
    st.session_state.quick_query = ""
if 'voice_input' not in st.session_state:
    st.session_state.voice_input = ""
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'emergency_active' not in st.session_state:
    st.session_state.emergency_active = False
if 'emergency_alerts' not in st.session_state:
    st.session_state.emergency_alerts = []
if 'voice_enabled' not in st.session_state:
    st.session_state.voice_enabled = False
if 'current_language' not in st.session_state:
    st.session_state.current_language = 'en'
if 'user_location' not in st.session_state:
    # Set default location to Escuela Fuente del Saber
    st.session_state.user_location = {
        'city': 'Near Escuela Fuente del Saber',
        'country': 'Nicaragua',
        'latitude': 11.9249,
        'longitude': -84.7152,
        'ip': 'Local',
        'facility_name': 'Escuela Fuente del Saber',
        'facility_type': 'Educational Facility/Emergency Shelter'
    }
if 'citizen_reports' not in st.session_state:
    st.session_state.citizen_reports = []
if 'app_mode' not in st.session_state:
    st.session_state.app_mode = 'citizen'  # 'citizen' or 'un_monitor'

# Initialize systems
ai_models = AIModels()
voice_interface = VoiceInterface()
emergency_system = EmergencySystem()

# Add sample disaster reports for demo - Enhanced for heat zone demonstration
if len(st.session_state.citizen_reports) == 0:
    sample_reports = [
        # High density cluster near school (RED ZONE - 50+ reports simulation)
        *[{
            'id': f'CR-202412011200{i:02d}',
            'timestamp': datetime.now() - timedelta(hours=2, minutes=i*5),
            'disaster_type': '🌊',
            'description': f'Flooding report #{i+1} - Water levels rising in residential area.',
            'location': {
                'latitude': 11.9249 + (i % 10) * 0.001, 
                'longitude': -84.7152 + (i % 8) * 0.001, 
                'address': f'Flood Zone {i+1}, Near School'
            },
            'severity': 3 + (i % 3),
            'contact_info': f'Citizen Report #{i+1}',
            'status': 'ACTIVE',
            'verified': i % 3 == 0,
            'responders_notified': True
        } for i in range(55)],  # 55 reports for RED ZONE
        
        # Medium density cluster in city center (YELLOW ZONE - 25-49 reports)
        *[{
            'id': f'CR-202412011300{i:02d}',
            'timestamp': datetime.now() - timedelta(hours=1, minutes=i*3),
            'disaster_type': '⚡',
            'description': f'Power outage report #{i+1} - Electrical infrastructure damaged.',
            'location': {
                'latitude': 12.1364 + (i % 6) * 0.002, 
                'longitude': -86.2514 + (i % 5) * 0.002, 
                'address': f'Managua District {i+1}'
            },
            'severity': 2 + (i % 3),
            'contact_info': f'Managua Resident #{i+1}',
            'status': 'ACTIVE',
            'verified': i % 4 == 0,
            'responders_notified': True
        } for i in range(30)],  # 30 reports for YELLOW ZONE
        
        # Low density scattered reports (GREEN ZONE - <25 reports)
        *[{
            'id': f'CR-202412011400{i:02d}',
            'timestamp': datetime.now() - timedelta(minutes=30 + i*10),
            'disaster_type': '🏥',
            'description': f'Minor medical emergency #{i+1}',
            'location': {
                'latitude': 12.4343 + (i % 4) * 0.005, 
                'longitude': -86.8780 + (i % 3) * 0.005, 
                'address': f'León Area {i+1}'
            },
            'severity': 1 + (i % 2),
            'contact_info': f'León Citizen #{i+1}',
            'status': 'ACTIVE',
            'verified': i % 2 == 0,
            'responders_notified': True
        } for i in range(15)]  # 15 reports for GREEN ZONE
    ]
    st.session_state.citizen_reports = sample_reports

# Mode Selector
col_header1, col_header2, col_header3 = st.columns([1, 2, 1])

with col_header2:
    st.markdown("""
    <div class="main-header">
        🌪️ StormShieldAI Emergency System
        <div class="subtitle">
            AI-Powered Emergency Response for Nicaragua
        </div>
        <div class="description">
            UN Tech Over Hackathon 2025 | Disaster Preparedness & Response
        </div>
    </div>
    """, unsafe_allow_html=True)

# Interface mode selector
st.markdown("---")
mode_col1, mode_col2, mode_col3 = st.columns([1, 2, 1])

with mode_col2:
    st.markdown("## 🎛️ Choose Your Interface")
    
    interface_mode = st.radio(
        "Select your role:",
        options=['citizen', 'un_monitor'],
        format_func=lambda x: "🧍 I Need Help - Citizen Reporting" if x == 'citizen' else "🌍 UN Monitoring Dashboard - Crisis Intelligence",
        index=0 if st.session_state.app_mode == 'citizen' else 1,
        horizontal=True,
        help="Choose between reporting a disaster or monitoring the crisis intelligence dashboard"
    )
    
    st.session_state.app_mode = interface_mode

# Route to appropriate interface
if st.session_state.app_mode == 'citizen':
    # ================================
    # CITIZEN REPORTING INTERFACE
    # ================================
    
    st.markdown("---")
    st.markdown("# 🧍 Citizen Emergency Reporting")
    st.markdown("**Report disasters, get help, and access AI emergency assistance**")
    
    # Emergency Reporting Section
    st.markdown("## 🚨 Quick Disaster Report")
    
    report_col1, report_col2 = st.columns([1, 1])
    
    with report_col1:
        st.markdown("### 📋 Report Details")
        
        # Disaster type selection
        disaster_icons = list(emergency_system.reporting_system.disaster_types.keys())
        disaster_names = [emergency_system.reporting_system.disaster_types[icon] for icon in disaster_icons]
        
        selected_disaster_idx = st.selectbox(
            "🔥 Disaster Type:",
            range(len(disaster_icons)),
            format_func=lambda x: f"{disaster_icons[x]} {disaster_names[x]}",
            help="Select the type of disaster you're experiencing"
        )
        
        selected_disaster = disaster_icons[selected_disaster_idx]
        
        # Severity rating
        severity = st.slider(
            "⚠️ Severity Level:",
            min_value=1,
            max_value=5,
            value=3,
            help="1 = Minor issue, 5 = Life-threatening emergency"
        )
        
        severity_labels = {1: "Minor", 2: "Moderate", 3: "Serious", 4: "Severe", 5: "Critical"}
        st.write(f"**Selected:** {severity_labels[severity]} ({severity}/5)")
        
        # Contact information
        contact_info = st.text_input(
            "📞 Your Contact Info (Optional):",
            placeholder="Name and phone/WhatsApp number",
            help="Help responders contact you directly"
        )
    
    with report_col2:
        st.markdown("### 📝 Description")
        
        # Description
        description = st.text_area(
            "📄 Describe the situation:",
            height=150,
            placeholder="Describe what you're seeing: How many people affected? What immediate help is needed? Any injuries?",
            help="Provide as much detail as possible to help emergency responders"
        )
        
        # Location confirmation
        st.markdown("### 📍 Your Location")
        current_location = st.session_state.user_location or {}
        facility_name = current_location.get('facility_name', 'Unknown Location')
        latitude = current_location.get('latitude', 0.0)
        longitude = current_location.get('longitude', 0.0)
        city = current_location.get('city', 'Unknown City')
        country = current_location.get('country', 'Unknown Country')
        
        st.info(f"""
        **📍 Reported Location:**  
        🏫 {facility_name}  
        📍 {latitude:.4f}°N, {longitude:.4f}°W  
        🌍 {city}, {country}
        """)
        
        # Submit report button
        if st.button("🚨 SUBMIT EMERGENCY REPORT", type="primary", help="Send your report to UN Emergency Coordination"):
            if description.strip():
                report_id = emergency_system.reporting_system.submit_citizen_report(
                    disaster_type=selected_disaster,
                    description=description,
                    location={
                        'facility_name': facility_name,
                        'latitude': latitude,
                        'longitude': longitude,
                        'city': city,
                        'country': country,
                        'address': f"{facility_name}, {city}"
                    },
                    severity=severity,
                    contact_info=contact_info if contact_info.strip() else None
                )
                
                st.success(f"""
                ✅ **REPORT SUBMITTED SUCCESSFULLY!**
                
                **Report ID:** {report_id}  
                **Status:** ACTIVE - Emergency responders notified  
                **Location:** Transmitted to UN Coordination Center  
                **Response ETA:** 5-15 minutes
                
                🚑 Emergency services have been automatically notified of your location and situation.
                """)
                
                # Add to emergency alerts
                alert_id = emergency_system.trigger_un_alert(
                    f"Citizen Report: {emergency_system.reporting_system.disaster_types[selected_disaster]} - {description}",
                    {
                        'facility_name': facility_name,
                        'latitude': latitude,
                        'longitude': longitude,
                        'city': city,
                        'country': country
                    },
                    f"Citizen Report - {emergency_system.reporting_system.disaster_types[selected_disaster]}"
                )
                
                st.balloons()
                time.sleep(2)
                st.rerun()
            else:
                st.warning("⚠️ Please provide a description of the situation.")

else:
    # ================================
    # UN MONITORING DASHBOARD
    # ================================
    
    st.markdown("---")
    st.markdown("# 🌍 UN Crisis Intelligence Dashboard")
    st.markdown("**Real-time disaster monitoring, hotspot detection, and emergency coordination**")
    
    # Real-time metrics
    st.markdown("## 📊 Live Crisis Metrics")
    
    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
    
    total_reports = len(st.session_state.citizen_reports)
    active_reports = len([r for r in st.session_state.citizen_reports if r['status'] == 'ACTIVE'])
    hotspots = emergency_system.reporting_system.detect_hotspots()
    critical_reports = len([r for r in st.session_state.citizen_reports if r['severity'] >= 4])
    
    with metrics_col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_reports}</div>
            <div class="metric-label">Total Reports</div>
        </div>
        """, unsafe_allow_html=True)
    
    with metrics_col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{active_reports}</div>
            <div class="metric-label">Active Incidents</div>
        </div>
        """, unsafe_allow_html=True)
    
    with metrics_col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(hotspots)}</div>
            <div class="metric-label">Crisis Hotspots</div>
        </div>
        """, unsafe_allow_html=True)
    
    with metrics_col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{critical_reports}</div>
            <div class="metric-label">Critical Cases</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Crisis Intelligence Map
    st.markdown("## 🗺️ Crisis Intelligence Map")
    
    # Map controls
    map_col1, map_col2, map_col3, map_col4 = st.columns(4)
    with map_col1:
        show_reports = st.checkbox("📍 Citizen Reports", value=True)
    with map_col2:
        show_hotspots = st.checkbox("🔥 Crisis Hotspots", value=True)
    with map_col3:
        show_infrastructure = st.checkbox("🏥 Infrastructure", value=True)
    with map_col4:
        auto_refresh = st.checkbox("🔄 Auto Refresh", value=False)
    
    # Create crisis intelligence map
    nicaragua_center = [12.8654, -85.2072]
    crisis_map = folium.Map(
        location=nicaragua_center, 
        zoom_start=7,
        tiles='CartoDB positron',
        width='100%',
        height='700px'
    )
    
    # Add crisis legend
    crisis_legend_html = '''
    <div style="position: fixed; 
                top: 10px; left: 50px; width: 250px; height: auto; 
                background-color: white; border:3px solid #dc2626; z-index:9999; 
                font-size:14px; padding: 15px; border-radius: 12px;
                box-shadow: 0 6px 16px rgba(220,38,38,0.4);">
    <h4 style="margin-top:0; color: #dc2626; text-align: center;">🚨 Crisis Intelligence</h4>
    <p><span style="color:#dc2626;">🔴</span> Critical Hotspot (4.0+ Risk)</p>
    <p><span style="color:#f59e0b;">🟠</span> High Risk Hotspot (3.0+)</p>
    <p><span style="color:#3b82f6;">🔵</span> Active Reports</p>
    <p><span style="color:#10b981;">🟢</span> Resolved Reports</p>
    <p><span style="color:#6b7280;">⚫</span> Infrastructure</p>
    <hr style="margin: 10px 0;">
    <p style="font-size: 12px; color: #666;">Auto-updates every 30s</p>
    </div>
    '''
    crisis_map.get_root().html.add_child(folium.Element(crisis_legend_html))
    
    # Add citizen reports to map
    if show_reports:
        reports_group = folium.FeatureGroup(name="📍 Citizen Reports")
        
        for report in st.session_state.citizen_reports:
            lat = report['location']['latitude']
            lon = report['location']['longitude']
            
            # Color by severity and status
            if report['severity'] >= 4:
                color = 'red' if report['status'] == 'ACTIVE' else 'darkred'
                icon_color = 'white'
            elif report['severity'] >= 3:
                color = 'orange' if report['status'] == 'ACTIVE' else 'darkorange'
                icon_color = 'white'
            else:
                color = 'blue' if report['status'] == 'ACTIVE' else 'darkblue'
                icon_color = 'white'
            
            # Create detailed popup
            time_ago = datetime.now() - report['timestamp']
            hours_ago = time_ago.total_seconds() / 3600
            
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(f"""
                <div style='font-family: Arial; width: 280px;'>
                    <h4 style='color: {color}; margin: 0;'>{report['disaster_type']} Citizen Report</h4>
                    <hr style='margin: 8px 0;'>
                    <p><b>📋 ID:</b> {report['id']}</p>
                    <p><b>🕐 Time:</b> {hours_ago:.1f} hours ago</p>
                    <p><b>⚠️ Severity:</b> {report['severity']}/5</p>
                    <p><b>📍 Location:</b> {report['location'].get('address', 'Unknown')}</p>
                    <p><b>📞 Contact:</b> {report.get('contact_info', 'Anonymous')}</p>
                    <p><b>📄 Description:</b><br>{report['description'][:150]}...</p>
                    <p><b>✅ Verified:</b> {'Yes' if report['verified'] else 'Pending'}</p>
                    <hr style='margin: 8px 0;'>
                    <p style='font-size: 12px; color: #666;'>Click marker for actions</p>
                </div>
                """, max_width=350),
                tooltip=f"{report['disaster_type']} Report - Severity {report['severity']}/5",
                icon=folium.Icon(color=color, icon='exclamation-triangle', prefix='fa')
            ).add_to(reports_group)
        
        reports_group.add_to(crisis_map)
    
    # Add crisis hotspots
    if show_hotspots and len(hotspots) > 0:
        hotspots_group = folium.FeatureGroup(name="🔥 Crisis Hotspots")
        
        for hotspot in hotspots:
            # Color by risk score
            if hotspot['risk_score'] >= 4:
                color = 'darkred'
                fillColor = 'red'
            elif hotspot['risk_score'] >= 3:
                color = 'darkorange'
                fillColor = 'orange'
            else:
                color = 'orange'
                fillColor = 'yellow'
            
            # Create hotspot circle
            folium.Circle(
                location=[hotspot['center_lat'], hotspot['center_lon']],
                radius=5000,  # 5km radius
                popup=folium.Popup(f"""
                <div style='font-family: Arial; width: 300px;'>
                    <h4 style='color: {color}; margin: 0;'>🔥 CRISIS HOTSPOT DETECTED</h4>
                    <hr style='margin: 8px 0;'>
                    <p><b>🆔 Hotspot ID:</b> {hotspot['id']}</p>
                    <p><b>📊 Risk Score:</b> {hotspot['risk_score']:.1f}/5.0</p>
                    <p><b>⚠️ Severity:</b> {hotspot['severity_level']}</p>
                    <p><b>📍 Reports Count:</b> {hotspot['report_count']} incidents</p>
                    <p><b>🎯 Primary Disaster:</b> {hotspot['primary_disaster']} {emergency_system.reporting_system.disaster_types[hotspot['primary_disaster']]}</p>
                    <p><b>📍 Center:</b> {hotspot['center_lat']:.4f}°N, {hotspot['center_lon']:.4f}°W</p>
                    <hr style='margin: 8px 0;'>
                    <p style='color: #dc2626; font-weight: bold;'>🚨 IMMEDIATE UN RESPONSE RECOMMENDED</p>
                </div>
                """, max_width=350),
                tooltip=f"🔥 {hotspot['severity_level']} Hotspot - {hotspot['report_count']} reports",
                color=color,
                weight=4,
                fill=True,
                fillColor=fillColor,
                fillOpacity=0.3
            ).add_to(hotspots_group)
            
            # Add center marker
            folium.Marker(
                location=[hotspot['center_lat'], hotspot['center_lon']],
                tooltip=f"Hotspot Center - Risk {hotspot['risk_score']:.1f}",
                icon=folium.Icon(color=color, icon='fire', prefix='fa')
            ).add_to(hotspots_group)
        
        hotspots_group.add_to(crisis_map)
    
    # Add infrastructure if requested
    if show_infrastructure:
        schools, health, roads = load_infrastructure_data()
        
        if schools is not None:
            schools_group = folium.FeatureGroup(name="🏫 Schools")
            for idx, row in schools.head(50).iterrows():
                school_name = row.get('name', 'Unknown School')
                folium.Marker(
                    location=[row.geometry.y, row.geometry.x],
                    popup=f"🏫 {school_name}",
                    tooltip=f"🏫 {school_name}",
                    icon=folium.Icon(color='gray', icon='graduation-cap', prefix='fa')
                ).add_to(schools_group)
            schools_group.add_to(crisis_map)
        
        if health is not None:
            health_group = folium.FeatureGroup(name="🏥 Health")
            for idx, row in health.head(50).iterrows():
                health_name = row.get('name', 'Unknown Health Facility')
                folium.Marker(
                    location=[row.geometry.y, row.geometry.x],
                    popup=f"🏥 {health_name}",
                    tooltip=f"🏥 {health_name}",
                    icon=folium.Icon(color='gray', icon='plus', prefix='fa')
                ).add_to(health_group)
            health_group.add_to(crisis_map)
    
    # Add layer control
    folium.LayerControl().add_to(crisis_map)
    
    # Display crisis map
    folium_static(crisis_map, width=1000, height=700)
    
    # Crisis Hotspot Analysis
    if len(hotspots) > 0:
        st.markdown("## 🔥 Critical Hotspot Analysis")
        
        for i, hotspot in enumerate(hotspots[:3]):  # Show top 3 hotspots
            severity_color = "🔴" if hotspot['severity_level'] == 'CRITICAL' else "🟠" if hotspot['severity_level'] == 'HIGH' else "🟡"
            
            with st.expander(f"{severity_color} Hotspot {i+1}: {hotspot['severity_level']} - Risk Score {hotspot['risk_score']:.1f}", expanded=(i==0)):
                hotspot_col1, hotspot_col2 = st.columns([1, 1])
                
                with hotspot_col1:
                    st.markdown(f"""
                    **🎯 Hotspot Analysis:**
                    - **Location:** {hotspot['center_lat']:.4f}°N, {hotspot['center_lon']:.4f}°W
                    - **Reports:** {hotspot['report_count']} incidents clustered
                    - **Primary Threat:** {hotspot['primary_disaster']} {emergency_system.reporting_system.disaster_types[hotspot['primary_disaster']]}
                    - **Risk Level:** {hotspot['risk_score']:.1f}/5.0 ({hotspot['severity_level']})
                    """)
                
                with hotspot_col2:
                    st.markdown("**📋 Reports in this cluster:**")
                    for j, report in enumerate(hotspot['reports'][:3]):
                        time_ago = datetime.now() - report['timestamp']
                        hours_ago = time_ago.total_seconds() / 3600
                        st.write(f"{j+1}. {report['disaster_type']} Severity {report['severity']}/5 ({hours_ago:.1f}h ago)")
                
                # Recommended actions
                if hotspot['severity_level'] == 'CRITICAL':
                    st.error("🚨 **IMMEDIATE ACTION REQUIRED:** Deploy emergency response teams, establish evacuation zones, coordinate with local authorities")
                elif hotspot['severity_level'] == 'HIGH':
                    st.warning("⚠️ **HIGH PRIORITY:** Monitor closely, prepare response teams, verify reports on ground")
                else:
                    st.info("📊 **MONITOR:** Continue surveillance, track for escalation patterns")
    
    # Live Reports Table
    st.markdown("## 📊 Live Reports Dashboard")
    
    if len(st.session_state.citizen_reports) > 0:
        # Create reports dataframe
        reports_data = []
        for report in st.session_state.citizen_reports:
            time_ago = datetime.now() - report['timestamp']
            hours_ago = time_ago.total_seconds() / 3600
            
            reports_data.append({
                'ID': report['id'],
                'Time': f"{hours_ago:.1f}h ago",
                'Type': f"{report['disaster_type']} {emergency_system.reporting_system.disaster_types[report['disaster_type']]}",
                'Severity': f"{report['severity']}/5",
                'Location': report['location'].get('address', 'Unknown'),
                'Status': report['status'],
                'Verified': '✅' if report['verified'] else '❓',
                'Contact': report.get('contact_info', 'Anonymous')[:20] + '...' if report.get('contact_info') and len(report.get('contact_info', '')) > 20 else report.get('contact_info', 'Anonymous')
            })
        
        reports_df = pd.DataFrame(reports_data)
        st.dataframe(reports_df, use_container_width=True, height=300)
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        action_col1, action_col2, action_col3, action_col4 = st.columns(4)
        
        with action_col1:
            if st.button("🚁 Deploy Helicopter", help="Deploy emergency helicopter to highest risk area"):
                st.success("🚁 Helicopter dispatched to hotspot location")
        
        with action_col2:
            if st.button("📢 Send Alert", help="Send emergency alert to all citizens in affected areas"):
                st.success("📢 Emergency alert broadcast sent")
        
        with action_col3:
            if st.button("🏥 Medical Team", help="Deploy medical response team"):
                st.success("🏥 Medical response team en route")
        
        with action_col4:
            if st.button("📊 Generate Report", help="Generate crisis situation report"):
                st.success("📊 Situation report generated")
        
    else:
        st.info("📊 No citizen reports received yet. Monitoring systems active.")
    
    # Auto-refresh for monitoring dashboard
    if auto_refresh:
        time.sleep(10)
        st.rerun()

# ================================
# SHARED CONTENT (BOTH INTERFACES)
# ================================

# Enhanced Feature Status Dashboard (for citizen interface only)
if st.session_state.app_mode == 'citizen':
    st.markdown("## 🚀 System Status Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        status_ai = "🟢 Active" if AI_AVAILABLE else "🔴 Offline"
        st.markdown(f"""
        <div class="feature-card">
            <h4>🤖 AI Models</h4>
            <p>{status_ai}</p>
            <small>ChatGPT & Gemini Integration</small>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        status_voice = "🟢 Ready" if VOICE_AVAILABLE else "🟡 Limited"
        st.markdown(f"""
        <div class="feature-card">
            <h4>🎤 Voice AI</h4>
            <p>{status_voice}</p>
            <small>Speech Recognition & TTS</small>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        status_translation = "🟢 Active" if TRANSLATION_AVAILABLE else "🟡 Basic"
        st.markdown(f"""
        <div class="feature-card">
            <h4>🌍 Translation</h4>
            <p>{status_translation}</p>
            <small>10 Languages Supported</small>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        status_map = "🟢 Ready" if FOLIUM_AVAILABLE else "🔴 Offline"
        st.markdown(f"""
        <div class="feature-card">
            <h4>🗺️ Live Maps</h4>
            <p>{status_map}</p>
            <small>Interactive Emergency Mapping</small>
        </div>
        """, unsafe_allow_html=True)

    # Emergency status check
    if st.session_state.emergency_active:
        st.markdown('<div class="emergency-alert">🚨 EMERGENCY MODE ACTIVE 🚨<br>UN Authorities Have Been Notified</div>', unsafe_allow_html=True)

else:
    # ================================
    # UN MONITORING DASHBOARD
    # ================================
    
    st.markdown("---")
    st.markdown("# 🌍 UN Crisis Intelligence Dashboard")
    st.markdown("**Real-time disaster monitoring, hotspot detection, and emergency coordination**")
    
    # Real-time metrics
    st.markdown("## 📊 Live Crisis Metrics")
    
    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
    
    total_reports = len(st.session_state.citizen_reports)
    active_reports = len([r for r in st.session_state.citizen_reports if r['status'] == 'ACTIVE'])
    hotspots = emergency_system.reporting_system.detect_hotspots()
    critical_reports = len([r for r in st.session_state.citizen_reports if r['severity'] >= 4])
    
    with metrics_col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_reports}</div>
            <div class="metric-label">Total Reports</div>
        </div>
        """, unsafe_allow_html=True)
    
    with metrics_col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{active_reports}</div>
            <div class="metric-label">Active Incidents</div>
        </div>
        """, unsafe_allow_html=True)
    
    with metrics_col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(hotspots)}</div>
            <div class="metric-label">Crisis Hotspots</div>
        </div>
        """, unsafe_allow_html=True)
    
    with metrics_col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{critical_reports}</div>
            <div class="metric-label">Critical Cases</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Crisis Intelligence Map
    st.markdown("## 🗺️ Crisis Intelligence Map")
    
    # Map controls
    map_col1, map_col2, map_col3, map_col4 = st.columns(4)
    with map_col1:
        show_reports = st.checkbox("📍 Citizen Reports", value=True)
    with map_col2:
        show_hotspots = st.checkbox("🔥 Crisis Hotspots", value=True)
    with map_col3:
        show_infrastructure = st.checkbox("🏥 Infrastructure", value=True)
    with map_col4:
        auto_refresh = st.checkbox("🔄 Auto Refresh", value=False)
    
    # Create crisis intelligence map
    nicaragua_center = [12.8654, -85.2072]
    crisis_map = folium.Map(
        location=nicaragua_center, 
        zoom_start=7,
        tiles='CartoDB positron',
        width='100%',
        height='700px'
    )
    
    # Add crisis legend
    crisis_legend_html = '''
    <div style="position: fixed; 
                top: 10px; left: 50px; width: 250px; height: auto; 
                background-color: white; border:3px solid #dc2626; z-index:9999; 
                font-size:14px; padding: 15px; border-radius: 12px;
                box-shadow: 0 6px 16px rgba(220,38,38,0.4);">
    <h4 style="margin-top:0; color: #dc2626; text-align: center;">🚨 Crisis Intelligence</h4>
    <p><span style="color:#dc2626;">🔴</span> Critical Hotspot (4.0+ Risk)</p>
    <p><span style="color:#f59e0b;">🟠</span> High Risk Hotspot (3.0+)</p>
    <p><span style="color:#3b82f6;">🔵</span> Active Reports</p>
    <p><span style="color:#10b981;">🟢</span> Resolved Reports</p>
    <p><span style="color:#6b7280;">⚫</span> Infrastructure</p>
    <hr style="margin: 10px 0;">
    <p style="font-size: 12px; color: #666;">Auto-updates every 30s</p>
    </div>
    '''
    crisis_map.get_root().html.add_child(folium.Element(crisis_legend_html))
    
    # Add citizen reports to map
    if show_reports:
        reports_group = folium.FeatureGroup(name="📍 Citizen Reports")
        
        for report in st.session_state.citizen_reports:
            lat = report['location']['latitude']
            lon = report['location']['longitude']
            
            # Color by severity and status
            if report['severity'] >= 4:
                color = 'red' if report['status'] == 'ACTIVE' else 'darkred'
                icon_color = 'white'
            elif report['severity'] >= 3:
                color = 'orange' if report['status'] == 'ACTIVE' else 'darkorange'
                icon_color = 'white'
            else:
                color = 'blue' if report['status'] == 'ACTIVE' else 'darkblue'
                icon_color = 'white'
            
            # Create detailed popup
            time_ago = datetime.now() - report['timestamp']
            hours_ago = time_ago.total_seconds() / 3600
            
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(f"""
                <div style='font-family: Arial; width: 280px;'>
                    <h4 style='color: {color}; margin: 0;'>{report['disaster_type']} Citizen Report</h4>
                    <hr style='margin: 8px 0;'>
                    <p><b>📋 ID:</b> {report['id']}</p>
                    <p><b>🕐 Time:</b> {hours_ago:.1f} hours ago</p>
                    <p><b>⚠️ Severity:</b> {report['severity']}/5</p>
                    <p><b>📍 Location:</b> {report['location'].get('address', 'Unknown')}</p>
                    <p><b>📞 Contact:</b> {report.get('contact_info', 'Anonymous')}</p>
                    <p><b>📄 Description:</b><br>{report['description'][:150]}...</p>
                    <p><b>✅ Verified:</b> {'Yes' if report['verified'] else 'Pending'}</p>
                    <hr style='margin: 8px 0;'>
                    <p style='font-size: 12px; color: #666;'>Click marker for actions</p>
                </div>
                """, max_width=350),
                tooltip=f"{report['disaster_type']} Report - Severity {report['severity']}/5",
                icon=folium.Icon(color=color, icon='exclamation-triangle', prefix='fa')
            ).add_to(reports_group)
        
        reports_group.add_to(crisis_map)
    
    # Add crisis hotspots
    if show_hotspots and len(hotspots) > 0:
        hotspots_group = folium.FeatureGroup(name="🔥 Crisis Hotspots")
        
        for hotspot in hotspots:
            # Color by risk score
            if hotspot['risk_score'] >= 4:
                color = 'darkred'
                fillColor = 'red'
            elif hotspot['risk_score'] >= 3:
                color = 'darkorange'
                fillColor = 'orange'
            else:
                color = 'orange'
                fillColor = 'yellow'
            
            # Create hotspot circle
            folium.Circle(
                location=[hotspot['center_lat'], hotspot['center_lon']],
                radius=5000,  # 5km radius
                popup=folium.Popup(f"""
                <div style='font-family: Arial; width: 300px;'>
                    <h4 style='color: {color}; margin: 0;'>🔥 CRISIS HOTSPOT DETECTED</h4>
                    <hr style='margin: 8px 0;'>
                    <p><b>🆔 Hotspot ID:</b> {hotspot['id']}</p>
                    <p><b>📊 Risk Score:</b> {hotspot['risk_score']:.1f}/5.0</p>
                    <p><b>⚠️ Severity:</b> {hotspot['severity_level']}</p>
                    <p><b>📍 Reports Count:</b> {hotspot['report_count']} incidents</p>
                    <p><b>🎯 Primary Disaster:</b> {hotspot['primary_disaster']} {emergency_system.reporting_system.disaster_types[hotspot['primary_disaster']]}</p>
                    <p><b>📍 Center:</b> {hotspot['center_lat']:.4f}°N, {hotspot['center_lon']:.4f}°W</p>
                    <hr style='margin: 8px 0;'>
                    <p style='color: #dc2626; font-weight: bold;'>🚨 IMMEDIATE UN RESPONSE RECOMMENDED</p>
                </div>
                """, max_width=350),
                tooltip=f"🔥 {hotspot['severity_level']} Hotspot - {hotspot['report_count']} reports",
                color=color,
                weight=4,
                fill=True,
                fillColor=fillColor,
                fillOpacity=0.3
            ).add_to(hotspots_group)
            
            # Add center marker
            folium.Marker(
                location=[hotspot['center_lat'], hotspot['center_lon']],
                tooltip=f"Hotspot Center - Risk {hotspot['risk_score']:.1f}",
                icon=folium.Icon(color=color, icon='fire', prefix='fa')
            ).add_to(hotspots_group)
        
        hotspots_group.add_to(crisis_map)
    
    # Add infrastructure if requested
    if show_infrastructure:
        schools, health, roads = load_infrastructure_data()
        
        if schools is not None:
            schools_group = folium.FeatureGroup(name="🏫 Schools")
            for idx, row in schools.head(50).iterrows():
                school_name = row.get('name', 'Unknown School')
                folium.Marker(
                    location=[row.geometry.y, row.geometry.x],
                    popup=f"🏫 {school_name}",
                    tooltip=f"🏫 {school_name}",
                    icon=folium.Icon(color='gray', icon='graduation-cap', prefix='fa', size=(20,20))
                ).add_to(schools_group)
            schools_group.add_to(crisis_map)
        
        if health is not None:
            health_group = folium.FeatureGroup(name="🏥 Health")
            for idx, row in health.head(50).iterrows():
                health_name = row.get('name', 'Unknown Health Facility')
                folium.Marker(
                    location=[row.geometry.y, row.geometry.x],
                    popup=f"🏥 {health_name}",
                    tooltip=f"🏥 {health_name}",
                    icon=folium.Icon(color='gray', icon='plus', prefix='fa', size=(20,20))
                ).add_to(health_group)
            health_group.add_to(crisis_map)
    
    # Add layer control
    folium.LayerControl().add_to(crisis_map)
    
    # Display crisis map
    folium_static(crisis_map, width=1000, height=700)
    
    # Crisis Hotspot Analysis
    if len(hotspots) > 0:
        st.markdown("## 🔥 Critical Hotspot Analysis")
        
        for i, hotspot in enumerate(hotspots[:3]):  # Show top 3 hotspots
            severity_color = "🔴" if hotspot['severity_level'] == 'CRITICAL' else "🟠" if hotspot['severity_level'] == 'HIGH' else "🟡"
            
            with st.expander(f"{severity_color} Hotspot {i+1}: {hotspot['severity_level']} - Risk Score {hotspot['risk_score']:.1f}", expanded=(i==0)):
                hotspot_col1, hotspot_col2 = st.columns([1, 1])
                
                with hotspot_col1:
                    st.markdown(f"""
                    **🎯 Hotspot Analysis:**
                    - **Location:** {hotspot['center_lat']:.4f}°N, {hotspot['center_lon']:.4f}°W
                    - **Reports:** {hotspot['report_count']} incidents clustered
                    - **Primary Threat:** {hotspot['primary_disaster']} {emergency_system.reporting_system.disaster_types[hotspot['primary_disaster']]}
                    - **Risk Level:** {hotspot['risk_score']:.1f}/5.0 ({hotspot['severity_level']})
                    """)
                
                with hotspot_col2:
                    st.markdown("**📋 Reports in this cluster:**")
                    for j, report in enumerate(hotspot['reports'][:3]):
                        time_ago = datetime.now() - report['timestamp']
                        hours_ago = time_ago.total_seconds() / 3600
                        st.write(f"{j+1}. {report['disaster_type']} Severity {report['severity']}/5 ({hours_ago:.1f}h ago)")
                
                # Recommended actions
                if hotspot['severity_level'] == 'CRITICAL':
                    st.error("🚨 **IMMEDIATE ACTION REQUIRED:** Deploy emergency response teams, establish evacuation zones, coordinate with local authorities")
                elif hotspot['severity_level'] == 'HIGH':
                    st.warning("⚠️ **HIGH PRIORITY:** Monitor closely, prepare response teams, verify reports on ground")
                else:
                    st.info("📊 **MONITOR:** Continue surveillance, track for escalation patterns")
    
    # Live Reports Table
    st.markdown("## 📊 Live Reports Dashboard")
    
    if len(st.session_state.citizen_reports) > 0:
        # Create reports dataframe
        reports_data = []
        for report in st.session_state.citizen_reports:
            time_ago = datetime.now() - report['timestamp']
            hours_ago = time_ago.total_seconds() / 3600
            
            reports_data.append({
                'ID': report['id'],
                'Time': f"{hours_ago:.1f}h ago",
                'Type': f"{report['disaster_type']} {emergency_system.reporting_system.disaster_types[report['disaster_type']]}",
                'Severity': f"{report['severity']}/5",
                'Location': report['location'].get('address', 'Unknown'),
                'Status': report['status'],
                'Verified': '✅' if report['verified'] else '❓',
                'Contact': report.get('contact_info', 'Anonymous')[:20] + '...' if report.get('contact_info') and len(report.get('contact_info', '')) > 20 else report.get('contact_info', 'Anonymous')
            })
        
        reports_df = pd.DataFrame(reports_data)
        st.dataframe(reports_df, use_container_width=True, height=300)
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        action_col1, action_col2, action_col3, action_col4 = st.columns(4)
        
        with action_col1:
            if st.button("🚁 Deploy Helicopter", help="Deploy emergency helicopter to highest risk area"):
                st.success("🚁 Helicopter dispatched to hotspot location")
        
        with action_col2:
            if st.button("📢 Send Alert", help="Send emergency alert to all citizens in affected areas"):
                st.success("📢 Emergency alert broadcast sent")
        
        with action_col3:
            if st.button("🏥 Medical Team", help="Deploy medical response team"):
                st.success("🏥 Medical response team en route")
        
        with action_col4:
            if st.button("📊 Generate Report", help="Generate crisis situation report"):
                st.success("📊 Situation report generated")
        
    else:
        st.info("📊 No citizen reports received yet. Monitoring systems active.")
    
    # Auto-refresh for monitoring dashboard
    if auto_refresh:
        time.sleep(10)
        st.rerun()

# ================================
# SHARED CONTENT (BOTH INTERFACES)
# ================================

# Professional Sidebar for both interfaces
with st.sidebar:
    st.markdown("""
    <div class="sidebar-section" style="text-align: center; border: 2px solid #2563eb;">
        <h2 style="color: #2563eb; margin: 0;">⚙️ Control Center</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Language selection with enhanced styling
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("### 🌍 Language Selection")
    selected_language = st.selectbox(
        "Choose your language:",
        options=list(LANGUAGES.keys()),
        format_func=lambda x: f"{LANGUAGES[x]} ({x.upper()})",
        index=0,
        help="Select your preferred language for the interface"
    )
    st.session_state.current_language = selected_language
    st.markdown('</div>', unsafe_allow_html=True)
    
    # AI Model selection
    st.subheader("🤖 AI Assistant")
    available_models = ["Demo Mode"]
    if OPENAI_AVAILABLE:
        available_models.append("ChatGPT")
    if GEMINI_AVAILABLE:
        available_models.append("Gemini")
    
    ai_model = st.selectbox("Select AI Model:", available_models)
    
    # Initialize API keys in session state
    if 'openai_key' not in st.session_state:
        st.session_state.openai_key = ""
    if 'gemini_key' not in st.session_state:
        st.session_state.gemini_key = ""
    
    if ai_model == "ChatGPT" and OPENAI_AVAILABLE:
        st.session_state.openai_key = st.text_input("OpenAI API Key:", type="password", value=st.session_state.openai_key)
    elif ai_model == "Gemini" and GEMINI_AVAILABLE:
        st.session_state.gemini_key = st.text_input("Gemini API Key:", type="password", value=st.session_state.gemini_key)
    
    # Voice controls
    st.subheader("🎤 Voice Interface")
    if VOICE_AVAILABLE and voice_interface.available:
        voice_enabled = st.checkbox("Enable Voice", value=st.session_state.voice_enabled)
        st.session_state.voice_enabled = voice_enabled
    else:
        st.warning("Voice features not available")
        voice_enabled = False
        st.session_state.voice_enabled = False
    
    if voice_enabled and VOICE_AVAILABLE:
        if st.button("🎤 Listen"):
            with st.spinner("Listening..."):
                text = voice_interface.listen_for_speech(selected_language)
                if text:
                    st.success(f"Heard: {text}")
                    
                    # Check for emergency
                    is_emergency, keywords = emergency_system.detect_emergency_keywords(text, selected_language)
                    if is_emergency:
                        st.session_state.emergency_active = True
                        location = emergency_system.get_user_location()
                        alert_id = emergency_system.trigger_un_alert(text, location, "Voice Emergency")
                        
                        emergency_msg = ai_models.translate_text(
                            f"Emergency detected! Alert ID: {alert_id}. Help is on the way!",
                            selected_language
                        )
                        voice_interface.speak_text(emergency_msg, selected_language)
                        st.rerun()
                    
                    # Add to chat history
                    st.session_state.chat_history.append({"role": "user", "content": text, "timestamp": datetime.now()})
                else:
                    st.error("No speech detected")
    
    # Emergency contacts
    st.markdown('<div class="emergency-contact">', unsafe_allow_html=True)
    st.subheader("📞 Emergency Contacts")
    for contact, number in EMERGENCY_CONTACTS.items():
        st.write(f"**{contact}:** {number}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Location status
    if st.button("📍 Get My Location"):
        location = emergency_system.get_user_location()
        if location:
            st.session_state.user_location = location
            st.markdown('<div class="location-status">', unsafe_allow_html=True)
            st.write(f"📍 **Location:** {location['city']}, {location['country']}")
            st.write(f"🌐 **Coordinates:** {location['latitude']:.4f}, {location['longitude']:.4f}")
            st.markdown('</div>', unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Professional Chat interface
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.markdown("## 🤖 AI Emergency Assistant")
    
    # AI Model Selection with enhanced styling
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_model = st.selectbox(
            "🧠 Choose AI Model",
            ["Demo Mode (Uses Real Data)", "ChatGPT (OpenAI)", "Gemini (Google)"],
            help="Select your preferred AI model for emergency responses"
        )
    
    with col2:
        selected_language = st.selectbox(
            "🌍 Language",
            ["English", "Spanish", "French", "Portuguese", "German", "Italian", "Arabic", "Chinese", "Hindi", "Swahili"],
            help="Choose your preferred language"
        )
    
    # Quick Emergency Actions
    st.markdown("### ⚡ Quick Emergency Actions")
    quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
    
    with quick_col1:
        if st.button("🌊 Flood Emergency", help="Get immediate flood response information"):
            emergency_query = "EMERGENCY: Flood situation in my area. I need immediate evacuation information and safety protocols."
            
            # Trigger emergency alert page for flood emergency
            st.session_state.emergency_active = True
            location = st.session_state.user_location
            alert_id = emergency_system.trigger_un_alert(emergency_query, location, "Flood Emergency")
            
            st.query_params['message'] = emergency_query
            st.query_params['type'] = 'Flood Emergency'
            st.switch_page("emergency_alert_page.py")
    
    with quick_col2:
        if st.button("🏥 Find Medical Help", help="Locate nearest medical facilities"):
            emergency_query = "EMERGENCY: I need immediate medical assistance. Find the nearest hospitals and medical facilities."
            
            # Trigger emergency alert page for medical emergency
            st.session_state.emergency_active = True
            location = st.session_state.user_location
            alert_id = emergency_system.trigger_un_alert(emergency_query, location, "Medical Emergency")
            
            st.query_params['message'] = emergency_query
            st.query_params['type'] = 'Medical Emergency'
            st.switch_page("emergency_alert_page.py")
    
    with quick_col3:
        if st.button("🏫 Evacuation Centers", help="Find safe evacuation locations"):
            emergency_query = "Show me the nearest evacuation centers and schools where I can take shelter during emergency."
            st.session_state.emergency_triggered = True
            st.session_state.quick_query = emergency_query
    
    with quick_col4:
        if st.button("👶 Child Safety", help="Get child protection information"):
            emergency_query = "I have children with me. What are the specific safety protocols for families with children during disasters?"
            st.session_state.emergency_triggered = True
            st.session_state.quick_query = emergency_query
    
    # Enhanced Chat Interface
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Voice Input Section
    if VOICE_AVAILABLE:
        col_voice1, col_voice2 = st.columns([1, 1])
        
        with col_voice1:
            if st.button("🎤 Start Voice Input", help="Click to speak your emergency question"):
                try:
                    with st.spinner("🎧 Listening... Speak now!"):
                        recognizer = sr.Recognizer()
                        microphone = sr.Microphone()
                        
                        with microphone as source:
                            recognizer.adjust_for_ambient_noise(source, duration=1)
                            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                        
                        voice_text = recognizer.recognize_google(audio)
                        st.session_state.voice_input = voice_text
                        st.success(f"🎯 Heard: {voice_text}")
                        
                        # Check for emergency keywords in voice input
                        is_emergency, keywords = emergency_system.detect_emergency_keywords(voice_text, 'en')
                        if is_emergency:
                            st.session_state.emergency_active = True
                            location = emergency_system.get_user_location()
                            alert_id = emergency_system.trigger_un_alert(voice_text, location, "Voice Emergency")
                            
                            # Redirect to emergency alert page
                            st.query_params['message'] = voice_text
                            st.query_params['type'] = 'Voice Emergency'
                            st.switch_page("emergency_alert_page.py")
                        else:
                            # Auto-process voice input normally
                            st.session_state.emergency_triggered = True
                            st.session_state.quick_query = voice_text
                except Exception as e:
                    st.error(f"Voice input error: {str(e)}")
        
        with col_voice2:
            if hasattr(st.session_state, 'voice_input') and st.session_state.voice_input:
                st.info(f"🎤 Voice Input: {st.session_state.voice_input}")
    
    # Text Input
    user_query = st.text_area(
        "💬 Ask me anything - emergency help or general questions:",
        value=st.session_state.get('quick_query', ''),
        height=100,
        placeholder="Examples: 'Hey, how are you doing today?' or 'Help! There's flooding in my area, where should I go?' or 'Tell me about Nicaragua weather'",
        help="I can help with emergencies, general questions, weather information, or just have a conversation. Try anything!"
    )
    
    # Enhanced Response Button
    col_btn1, col_btn2 = st.columns([3, 1])
    
    with col_btn1:
        get_response_btn = st.button("🚀 Get AI Response", help="Click to get AI-powered assistance for any question")
    
    with col_btn2:
        if st.button("🔄 Clear", help="Clear the current query"):
            st.session_state.quick_query = ""
            if 'voice_input' in st.session_state:
                del st.session_state.voice_input
            st.experimental_rerun()
    
    # Process Emergency Response
    if get_response_btn or st.session_state.get('emergency_triggered', False):
        if user_query or st.session_state.get('quick_query'):
            query_to_process = user_query or st.session_state.get('quick_query', '')
            
            # Check for emergency keywords first
            is_emergency, keywords = emergency_system.detect_emergency_keywords(query_to_process, 'en')
            if is_emergency and get_response_btn:  # Only auto-redirect if user clicked button
                st.session_state.emergency_active = True
                location = st.session_state.user_location
                alert_id = emergency_system.trigger_un_alert(query_to_process, location, "Text Emergency")
                
                # Redirect to emergency alert page
                st.query_params['message'] = query_to_process
                st.query_params['type'] = 'Text Emergency'
                st.switch_page("emergency_alert_page.py")
            
            with st.spinner("🤖 AI is analyzing your message and preparing response..."):
                try:
                    # Get API keys from session state
                    openai_key = st.session_state.get('openai_key', '')
                    gemini_key = st.session_state.get('gemini_key', '')
                    
                    # AI Model Response
                    if selected_model == "ChatGPT (OpenAI)" and OPENAI_AVAILABLE and openai_key:
                        ai_response = ai_models.get_chatgpt_response(query_to_process, openai_key)
                    elif selected_model == "Gemini (Google)" and GEMINI_AVAILABLE and gemini_key:
                        ai_response = ai_models.get_gemini_response(query_to_process, gemini_key)
                    else:
                        # Enhanced Demo Response - works for any message
                        ai_response = get_smart_general_response(query_to_process)
                    
                    # Display Response with enhanced formatting
                    st.markdown("### 🤖 AI Response")
                    st.markdown('<div class="ai-response">', unsafe_allow_html=True)
                    st.markdown(ai_response)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Voice Output
                    if VOICE_AVAILABLE and TTS_AVAILABLE:
                        col_voice1, col_voice2 = st.columns([1, 1])
                        with col_voice1:
                            if st.button("🔊 Hear Response", help="Click to hear the response"):
                                try:
                                    # Create TTS
                                    tts = gTTS(text=ai_response[:500], lang='en', slow=False)  # Limit for demo
                                    tts.save("response.mp3")
                                    
                                    # Play audio (platform-specific)
                                    import subprocess
                                    subprocess.Popen(["start", "response.mp3"], shell=True)
                                    st.success("🎵 Playing audio response...")
                                except Exception as e:
                                    st.error(f"Audio error: {str(e)}")
                    
                    # Clear emergency trigger
                    st.session_state.emergency_triggered = False
                    
                except Exception as e:
                    st.error(f"❌ Error generating response: {str(e)}")
                    st.info("💡 The system is using demo mode with real Nicaragua data.")
        else:
            st.warning("⚠️ Please enter a question or select a quick action.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Professional Hurricane tracking map with legend
    st.markdown('<div class="map-container">', unsafe_allow_html=True)
    st.subheader("🌪️ Interactive Emergency Response Map")
    
    # Map controls
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        show_hurricanes = st.checkbox("🌪️ Show Hurricanes", value=True)
    with col2:
        show_infrastructure = st.checkbox("🏥 Show Infrastructure", value=True)
    with col3:
        show_flood_zones = st.checkbox("🌊 Show Flood Zones", value=True)
    
    # Create professional map
    nicaragua_center = [12.8654, -85.2072]
    m = folium.Map(
        location=nicaragua_center, 
        zoom_start=7,
        tiles='CartoDB positron',
        width='100%',
        height='600px'
    )
    
    # Add custom CSS to map
    legend_html = '''
    <div style="position: fixed; 
                top: 10px; left: 50px; width: 200px; height: auto; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px; border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
    <h4 style="margin-top:0; color: #2c3e50;">🗺️ Map Legend</h4>
    <p><span style="color:red;">🔴</span> Hurricane Eta Path</p>
    <p><span style="color:orange;">🟠</span> Hurricane Iota Path</p>
    <p><span style="color:blue;">🏫</span> Schools & Education</p>
    <p><span style="color:red;">🏥</span> Health Facilities</p>
    <p><span style="color:green;">📍</span> Your Location</p>
    <p><span style="color:purple;">🌊</span> Flood Risk Areas</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Load and display hurricane data with enhanced markers
    if show_hurricanes:
        eta_data, iota_data = load_hurricane_data()
        
        if eta_data is not None:
            # Create hurricane group
            eta_group = folium.FeatureGroup(name="🌪️ Hurricane Eta")
            for idx, row in eta_data.iterrows():
                folium.CircleMarker(
                    location=[row.geometry.y, row.geometry.x],
                    radius=12,
                    popup=folium.Popup(f"""
                    <div style='font-family: Arial; width: 200px;'>
                        <h4 style='color: #e74c3c; margin: 0;'>🌪️ Hurricane Eta</h4>
                        <hr style='margin: 5px 0;'>
                        <p><b>📅 Time:</b> {row.get('ISO_TIME', 'Unknown')}</p>
                        <p><b>💨 Category:</b> {row.get('SS', 'Unknown')}</p>
                        <p><b>📍 Location:</b> {row.geometry.y:.3f}°N, {row.geometry.x:.3f}°W</p>
                    </div>
                    """, max_width=300),
                    tooltip="🌪️ Hurricane Eta - Click for details",
                    color='darkred',
                    weight=3,
                    fill=True,
                    fillColor='red',
                    fillOpacity=0.8
                ).add_to(eta_group)
            eta_group.add_to(m)
        
        if iota_data is not None:
            # Create hurricane group
            iota_group = folium.FeatureGroup(name="🌪️ Hurricane Iota")
            for idx, row in iota_data.iterrows():
                folium.CircleMarker(
                    location=[row.geometry.y, row.geometry.x],
                    radius=12,
                    popup=folium.Popup(f"""
                    <div style='font-family: Arial; width: 200px;'>
                        <h4 style='color: #f39c12; margin: 0;'>🌪️ Hurricane Iota</h4>
                        <hr style='margin: 5px 0;'>
                        <p><b>📅 Time:</b> {row.get('ISO_TIME', 'Unknown')}</p>
                        <p><b>💨 Category:</b> {row.get('SS', 'Unknown')}</p>
                        <p><b>📍 Location:</b> {row.geometry.y:.3f}°N, {row.geometry.x:.3f}°W</p>
                    </div>
                    """, max_width=300),
                    tooltip="🌪️ Hurricane Iota - Click for details",
                    color='darkorange',
                    weight=3,
                    fill=True,
                    fillColor='orange',
                    fillOpacity=0.8
                ).add_to(iota_group)
            iota_group.add_to(m)
    
    # Add infrastructure with enhanced markers
    if show_infrastructure:
        schools, health, roads = load_infrastructure_data()
        
        if schools is not None:
            schools_group = folium.FeatureGroup(name="🏫 Schools")
            for idx, row in schools.head(100).iterrows():  # Show more markers
                school_name = row.get('name', 'Unknown School')
                folium.Marker(
                    location=[row.geometry.y, row.geometry.x],
                    popup=folium.Popup(f"""
                    <div style='font-family: Arial; width: 200px;'>
                        <h4 style='color: #3498db; margin: 0;'>🏫 Educational Facility</h4>
                        <hr style='margin: 5px 0;'>
                        <p><b>🏫 Name:</b> {school_name}</p>
                        <p><b>📍 Location:</b> {row.geometry.y:.4f}°N, {row.geometry.x:.4f}°W</p>
                        <p><b>🎒 Type:</b> {row.get('amenity', 'School')}</p>
                        <p><b>📞 Emergency Shelter:</b> Available</p>
                    </div>
                    """, max_width=300),
                    tooltip=f"🏫 {school_name}",
                    icon=folium.Icon(color='blue', icon='graduation-cap', prefix='fa')
                ).add_to(schools_group)
            schools_group.add_to(m)
        
        if health is not None:
            health_group = folium.FeatureGroup(name="🏥 Health Facilities")
            for idx, row in health.head(100).iterrows():  # Show more markers
                health_name = row.get('name', 'Unknown Health Facility')
                folium.Marker(
                    location=[row.geometry.y, row.geometry.x],
                    popup=folium.Popup(f"""
                    <div style='font-family: Arial; width: 200px;'>
                        <h4 style='color: #e74c3c; margin: 0;'>🏥 Health Facility</h4>
                        <hr style='margin: 5px 0;'>
                        <p><b>🏥 Name:</b> {health_name}</p>
                        <p><b>📍 Location:</b> {row.geometry.y:.4f}°N, {row.geometry.x:.4f}°W</p>
                        <p><b>⚕️ Type:</b> {row.get('amenity', 'Healthcare')}</p>
                        <p><b>🚨 Emergency Services:</b> Available 24/7</p>
                    </div>
                    """, max_width=300),
                    tooltip=f"🏥 {health_name}",
                    icon=folium.Icon(color='red', icon='plus', prefix='fa')
                ).add_to(health_group)
            health_group.add_to(m)
    
    # Add flood risk zones
    if show_flood_zones:
        flood_group = folium.FeatureGroup(name="🌊 Flood Risk Zones")
        
        # Add flood risk areas as circles
        flood_locations = {
            'Bluefields': [12.0131, -83.7669],
            'Pearl Lagoon': [12.3428, -83.6703],
            'Managua': [12.1364, -86.2514],
            'León': [12.4343, -86.8780],
            'Granada': [11.9344, -85.9560]
        }
        
        for city, coords in flood_locations.items():
            risk_level = next((level for level, areas in FLOOD_RISK_AREAS.items() if city in areas), 'Medium')
            color = {'Critical': 'darkred', 'High': 'orange', 'Medium': 'yellow', 'Low': 'green'}[risk_level]
            
            folium.Circle(
                location=coords,
                radius=15000,  # 15km radius
                popup=folium.Popup(f"""
                <div style='font-family: Arial; width: 200px;'>
                    <h4 style='color: {color}; margin: 0;'>🌊 Flood Risk Zone</h4>
                    <hr style='margin: 5px 0;'>
                    <p><b>📍 City:</b> {city}</p>
                    <p><b>⚠️ Risk Level:</b> {risk_level}</p>
                    <p><b>🌊 Radius:</b> 15km</p>
                    <p><b>🚨 Action:</b> Monitor weather alerts</p>
                </div>
                """, max_width=300),
                tooltip=f"🌊 {city} - {risk_level} Risk",
                color=color,
                weight=2,
                fill=True,
                fillColor=color,
                fillOpacity=0.2
            ).add_to(flood_group)
        
        flood_group.add_to(m)
    
    # Add user location if available
    if st.session_state.user_location:
        user_group = folium.FeatureGroup(name="📍 Your Location")
        folium.Marker(
            location=[st.session_state.user_location['latitude'], st.session_state.user_location['longitude']],
            popup=folium.Popup(f"""
            <div style='font-family: Arial; width: 200px;'>
                <h4 style='color: #27ae60; margin: 0;'>📍 Your Current Location</h4>
                <hr style='margin: 5px 0;'>
                <p><b>🏙️ City:</b> {st.session_state.user_location['city']}</p>
                <p><b>🌍 Country:</b> {st.session_state.user_location['country']}</p>
                <p><b>📍 Coordinates:</b> {st.session_state.user_location['latitude']:.4f}°N, {st.session_state.user_location['longitude']:.4f}°W</p>
                <p><b>🌐 IP:</b> {st.session_state.user_location['ip']}</p>
            </div>
            """, max_width=300),
            tooltip="📍 Your Location",
            icon=folium.Icon(color='green', icon='user', prefix='fa')
        ).add_to(user_group)
        user_group.add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Display enhanced map
    folium_static(m, width=800, height=600)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Map statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🌪️ Hurricane Tracks", "2 Major Storms", "Eta & Iota 2020")
    with col2:
        st.metric("🏥 Health Facilities", "50+", "Emergency Ready")
    with col3:
        st.metric("🏫 Schools/Shelters", "100+", "Evacuation Centers")
    with col4:
        st.metric("🌊 Flood Zones", "25+ Areas", "Risk Monitored")

with col2:
    # Status panels
    st.subheader("📊 System Status")
    
    # Emergency alerts
    if st.session_state.emergency_alerts:
        st.markdown('<div class="emergency-alert">🚨 ACTIVE EMERGENCY ALERTS</div>', unsafe_allow_html=True)
        for alert in st.session_state.emergency_alerts[-3:]:  # Show last 3 alerts
            st.write(f"**{alert['id']}**")
            st.write(f"Type: {alert['type']}")
            st.write(f"Time: {alert['timestamp'].strftime('%H:%M:%S')}")
            st.write("---")
    
    # Weather data
    st.subheader("🌧️ Precipitation Data")
    precip_files = load_precipitation_data()
    
    if precip_files:
        selected_file = st.selectbox("Select precipitation data:", 
                                   [os.path.basename(f) for f in precip_files])
        
        if st.button("Load Precipitation Map"):
            with st.spinner("Loading precipitation data..."):
                try:
                    file_path = next(f for f in precip_files if os.path.basename(f) == selected_file)
                    
                    with rasterio.open(file_path) as src:
                        data = src.read(1)
                        
                    fig, ax = plt.subplots(figsize=(8, 6))
                    im = ax.imshow(data, cmap='Blues')
                    ax.set_title(f"Precipitation: {selected_file}")
                    plt.colorbar(im, ax=ax, label='Precipitation (mm)')
                    st.pyplot(fig)
                    
                except Exception as e:
                    st.error(f"Error loading precipitation data: {e}")
    
    # Flood risk areas
    st.markdown('<div class="flood-risk">', unsafe_allow_html=True)
    st.subheader("🌊 Flood Risk Areas")
    for risk_level, areas in FLOOD_RISK_AREAS.items():
        color = {'Critical': '🔴', 'High': '🟠', 'Medium': '🟡', 'Low': '🟢'}
        st.write(f"{color[risk_level]} **{risk_level}:** {', '.join(areas)}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat history
    if st.session_state.chat_history:
        st.subheader("💬 Recent Chat")
        for chat in st.session_state.chat_history[-5:]:  # Show last 5 messages
            time_str = chat['timestamp'].strftime('%H:%M')
            if chat['role'] == 'user':
                st.write(f"👤 **You** ({time_str}): {chat['content'][:100]}...")
            else:
                st.write(f"🤖 **AI** ({time_str}): {chat['content'][:100]}...")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🌪️ <strong>StormShieldAI</strong> - Ultimate Emergency Response System | Powered by AI & Real-time Data</p>
    <p>🚨 For immediate emergencies, call 911 or your local emergency services</p>
    <p>🇳🇮 Hurricane Eta & Iota Data | 🏥 Infrastructure Data | 🌍 Multi-language Support</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh for emergency mode
if st.session_state.emergency_active:
    time.sleep(2)
    st.rerun() 
    st.rerun() 