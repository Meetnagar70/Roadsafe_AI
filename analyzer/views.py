# analyzer/views.py

import os
import pandas as pd
import json
import folium
from folium.plugins import HeatMap
from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings
from django.http import Http404
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required


# --- Helper Function ---
def load_data(file_path):
    """Loads a CSV file into a pandas DataFrame."""
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        return None
    
def get_file_path(subfolder, filename):
    """Constructs the full path to a data file."""
    return os.path.join(settings.DATA_DIR, subfolder, f'{filename}.csv')

# --- Page Views ---

def dashboard_page(request):
    """View for the All-India Dashboard with robust data cleaning."""
    df = load_data(os.path.join(settings.DATA_DIR, 'all_india.csv'))
    if df is None:
        raise Http404("All India dataset not found.")

    # --- THIS IS THE FIX FOR THE LATITUDE/LONGITUDE ERROR ---
    # We force 'latitude' and 'longitude' to be numeric, turning any non-numeric
    # values (like 'Gujarat') into NaN (Not a Number).
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    
    # We also keep the robust fix for the Date column
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    # ---------------------------------------------------------

    # 1. Pie Chart: Accident severity
    severity_counts = df['Accident_Severity'].value_counts().to_dict()

    # 2. Bar Chart: Accidents per road type
    road_type_counts = df['Road_Type'].value_counts().to_dict()

    # 3. Line Chart: Accidents by month
    # This will now safely ignore rows with bad dates or locations
    accidents_by_month = df.dropna(subset=['Date']).resample('M', on='Date').size().to_dict()
    accidents_by_month = {time.strftime('%Y-%m'): count for time, count in accidents_by_month.items()}

    # 4. Map: Overall accident heatmap
    map_center = [20.5937, 78.9629]
    india_map = folium.Map(location=map_center, zoom_start=5)
    # This .dropna() is now very important, as it will remove rows where lat/lon are NaN
    heat_data = df[['latitude', 'longitude']].dropna().values.tolist()
    if heat_data:
        HeatMap(heat_data, radius=15).add_to(india_map)
    map_html = india_map._repr_html_()

    # 5. Top 5 States
    # top_5_states = df['State'].value_counts().head(5).to_dict()
    last_5_states = df['State'][::-1].value_counts().tail(5).sort_values(ascending=True) .to_dict()

    context = {
        'page_title': 'All-India Accident Dashboard',
        'severity_data': json.dumps(severity_counts),
        'road_type_data': json.dumps(road_type_counts),
        'monthly_data': json.dumps(accidents_by_month),
        'map_html': map_html,
        # 'top_5_states': top_5_states,
        'last_5_states': last_5_states
    }
    return render(request, 'analyzer/dashboard.html', context)

# analyzer/views.py

def state_page(request, state_name):
    """View for the State-specific Page, with robust data cleaning."""
    file_path = get_file_path('states', state_name)
    df_full = load_data(file_path)
    if df_full is None:
        raise Http404(f"Data for state '{state_name}' not found.")

    # --- THIS IS THE FIX ---
    # We force all relevant columns to their correct data type.
    # This prevents any sorting or analysis errors.
    df_full['latitude'] = pd.to_numeric(df_full['latitude'], errors='coerce')
    df_full['longitude'] = pd.to_numeric(df_full['longitude'], errors='coerce')
    df_full['Date'] = pd.to_datetime(df_full['Date'], errors='coerce')
    # This line is the most direct fix for the current error.
    df_full['District'] = df_full['District'].astype(str)
    # -----------------------

    # Get a sorted list of unique districts for the filter dropdown
    available_districts = sorted(df_full['District'].unique())

    # Check if a district was selected from the filter form
    selected_district = request.GET.get('district_filter', '')

    # Filter the DataFrame if a district is selected
    if selected_district:
        df = df_full[df_full['District'] == selected_district].copy()
        page_title = f'Analysis for {selected_district}, {state_name}'
    else:
        df = df_full.copy()
        page_title = f'{state_name} State Accident Analysis'

    # --- All calculations below are now safe ---
    severity_counts = df['Accident_Severity'].value_counts().to_dict()

    if selected_district:
        top_5_heading = f'Top Road Types in {selected_district}'
        top_5_data = df['Road_Type'].value_counts().head(5).to_dict()
    else:
        top_5_heading = 'Top 5 Districts'
        top_5_data = df['District'].value_counts().head(5).to_dict()

    weather_counts = df['Weather_Conditions'].value_counts().to_dict()

    accidents_by_month = df.dropna(subset=['Date']).resample('M', on='Date').size().to_dict()
    accidents_by_month = {time.strftime('%Y-%m'): count for time, count in accidents_by_month.items()}

    if not df.empty:
        map_center = [df['latitude'].mean(), df['longitude'].mean()]
        zoom_start = 10 if selected_district else 7
    else:
        map_center = [20.5937, 78.9629]
        zoom_start = 7
        
    state_map = folium.Map(location=map_center, zoom_start=zoom_start)
    heat_data = df[['latitude', 'longitude']].dropna().values.tolist()
    if heat_data:
        HeatMap(heat_data, radius=12).add_to(state_map)
    map_html = state_map._repr_html_()

    context = {
        'page_title': page_title,
        'state_name': state_name,
        'severity_data': json.dumps(severity_counts),
        'top_5_heading': top_5_heading,
        'top_5_data': top_5_data,
        'top_5_data_json': json.dumps(top_5_data),
        'weather_data': json.dumps(weather_counts),
        'monthly_data': json.dumps(accidents_by_month),
        'map_html': map_html,
        'available_districts': available_districts,
        'selected_district': selected_district,
    }
    return render(request, 'analyzer/state_detail.html', context)

def district_page(request, state_name=None, district_name=None):
    """
    Handles the District Detail page with robust data cleaning before ML processing.
    """
    # --- Part 1: Get data for the filter dropdowns ---
    states_path = os.path.join(settings.DATA_DIR, 'states')
    try:
        all_states = sorted([name.replace('.csv', '') for name in os.listdir(states_path) if name.endswith('.csv')])
    except FileNotFoundError:
        all_states = []

    selected_state = state_name or request.GET.get('state_select')
    
    available_districts = []
    if selected_state:
        districts_path = os.path.join(settings.DATA_DIR, 'districts', selected_state)
        try:
            available_districts = sorted([name.replace('.csv', '') for name in os.listdir(districts_path) if name.endswith('.csv')])
        except FileNotFoundError:
            available_districts = []

    selected_district = district_name or request.GET.get('district_select')

    # --- Part 2: Load data and run ML model if selected ---
    context = {
        'page_title': 'District Level Analysis',
        'all_states': all_states,
        'available_districts': available_districts,
        'selected_state': selected_state,
        'selected_district': selected_district,
        'data_loaded': False,
    }

    if selected_state and selected_district:
        file_path = os.path.join(settings.DATA_DIR, 'districts', selected_state, f'{selected_district}.csv')
        df = load_data(file_path)
        
        if df is not None and not df.empty:
            # --- THIS IS THE FIX ---
            # 1. Force coordinate columns to be numeric. Invalid values become NaN.
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
            
            # 2. Remove any rows that have invalid coordinates before doing any analysis.
            df.dropna(subset=['latitude', 'longitude'], inplace=True)
            # -----------------------

            context['data_loaded'] = True
            context['page_title'] = f'Hotspot Analysis for {selected_district}, {selected_state}'
            
            # --- ML INTEGRATION (Now Safe) ---
            model_path = os.path.join(settings.BASE_DIR, 'analyzer', 'models', 'dbscan_model.joblib')
            try:
                dbscan_model = joblib.load(model_path)
            except FileNotFoundError:
                dbscan_model = None

            coords = df[['latitude', 'longitude']].to_numpy() # No need for .dropna() here anymore
            
            if dbscan_model is not None and len(coords) > 0:
                scaler = StandardScaler()
                coords_scaled = scaler.fit_transform(coords)
                clusters = dbscan_model.fit_predict(coords_scaled)
                df['cluster'] = clusters
            else:
                df['cluster'] = 0

            # Prepare data for the template
            map_data = df[['latitude', 'longitude', 'Date', 'Time', 'Accident_Severity', 'Road_Type', 'cluster']].copy()
            map_data.columns = ['Latitude', 'Longitude', 'Date', 'Time', 'Severity', 'Road_Type', 'Cluster']
            context['accident_json'] = map_data.to_json(orient='records')
            
            # Other context data...
            context['total_accidents'] = len(df)
            context['peak_time'] = df['Time'].mode()[0] if not df['Time'].empty else 'N/A'
            context['common_road_type'] = df['Road_Type'].mode()[0] if not df['Road_Type'].empty else 'N/A'
            context['severity_data'] = json.dumps(df['Accident_Severity'].value_counts().to_dict())
            context['road_type_data'] = json.dumps(df['Road_Type'].value_counts().to_dict())
            context['weather_data'] = json.dumps(df['Weather_Conditions'].value_counts().to_dict())

    return render(request, 'analyzer/district_detail.html', context)
@login_required
def submit_page(request):
    """
    Handles submission of new accident data, ensuring correct data types and column order.
    """
    states_path = os.path.join(settings.DATA_DIR, 'states')
    try:
        all_states = sorted([name.replace('.csv', '') for name in os.listdir(states_path) if name.endswith('.csv')])
    except FileNotFoundError:
        all_states = []

    districts_by_state = {}
    for state in all_states:
        districts_path = os.path.join(settings.DATA_DIR, 'districts', state)
        try:
            districts_by_state[state] = sorted([name.replace('.csv', '') for name in os.listdir(districts_path) if name.endswith('.csv')])
        except FileNotFoundError:
            districts_by_state[state] = []

    india_df = load_data(os.path.join(settings.DATA_DIR, 'all_india.csv'))
    if india_df is not None:
        road_types = sorted(india_df['Road_Type'].dropna().unique())
        weather_conditions = sorted(india_df['Weather_Conditions'].dropna().unique())
        light_conditions = sorted(india_df['Light_Conditions'].dropna().unique())
    else:
        road_types, weather_conditions, light_conditions = [], [], []

    if request.method == 'POST':
        # Get all data from the form
        state = request.POST.get('state')
        district = request.POST.get('district')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        date = request.POST.get('date')
        time = request.POST.get('time')
        severity = request.POST.get('severity')
        road_type = request.POST.get('road_type')
        weather = request.POST.get('weather')
        num_vehicles = request.POST.get('num_vehicles')
        num_casualties = request.POST.get('num_casualties')
        light = request.POST.get('light_conditions')

        if not all([state, district, latitude, longitude, date, time, severity, road_type, weather, num_vehicles, num_casualties, light]):
            return redirect('submit_page')

        # Define the master column order
        master_column_order = [
            'Accident_Index', 'Date', 'Time', 'latitude', 'longitude', 
            'Accident_Severity', 'Number_of_Vehicles', 'Number_of_Casualties', 
            'Road_Type', 'Weather_Conditions', 'Light_Conditions', 'State', 'District'
        ]

        # Get the last Accident_Index
        india_csv_path = os.path.join(settings.DATA_DIR, 'all_india.csv')
        try:
            last_index_str = pd.read_csv(india_csv_path, usecols=['Accident_Index']).iloc[-1]['Accident_Index']
            new_index = int(float(last_index_str)) + 1
        except (FileNotFoundError, IndexError, ValueError, TypeError):
            new_index = 1

        # --- THIS IS THE CORRECTED PART ---
        # Create the new record, ensuring the correct data types (float)
        new_record = {
            'Accident_Index': [float(new_index)],
            'Date': [date],
            'Time': [time],
            'latitude': [float(latitude)],
            'longitude': [float(longitude)],
            'Accident_Severity': [severity],
            'Number_of_Vehicles': [float(num_vehicles)], # Changed to float
            'Number_of_Casualties': [float(num_casualties)], # Changed to float
            'Road_Type': [road_type],
            'Weather_Conditions': [weather],
            'Light_Conditions': [light],
            'State': [state],
            'District': [district]
        }
        
        # Create and reorder the DataFrame
        new_df = pd.DataFrame(new_record)
        new_df = new_df[master_column_order]

        # Append to all CSVs
        district_csv_path = os.path.join(settings.DATA_DIR, 'districts', state, f'{district}.csv')
        state_csv_path = os.path.join(settings.DATA_DIR, 'states', f'{state}.csv')
        new_df.to_csv(district_csv_path, mode='a', header=False, index=False)
        new_df.to_csv(state_csv_path, mode='a', header=False, index=False)
        new_df.to_csv(india_csv_path, mode='a', header=False, index=False)

        # Re-train the ML Model
        full_df = pd.read_csv(india_csv_path)
        coords = full_df[['latitude', 'longitude']].dropna().to_numpy()
        if len(coords) > 0:
            scaler = StandardScaler()
            coords_scaled = scaler.fit_transform(coords)
            dbscan_model = DBSCAN(eps=0.5, min_samples=5)
            dbscan_model.fit(coords_scaled)
            model_path = os.path.join(settings.BASE_DIR, 'analyzer', 'models', 'dbscan_model.joblib')
            joblib.dump(dbscan_model, model_path)

        return redirect('dashboard')

    context = {
        'page_title': 'Submit New Accident Report',
        'all_states': all_states,
        'districts_by_state_json': json.dumps(districts_by_state),
        'road_types': road_types,
        'weather_conditions': weather_conditions,
        'light_conditions': light_conditions,
    }
    return render(request, 'analyzer/submit_form.html', context)

# analyzer/views.py

# --- AUTHENTICATION VIEWS ---

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account has been created.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()
    return render(request, 'analyzer/signup.html', {'form': form, 'page_title': 'Sign Up'})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect('dashboard')
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    form = AuthenticationForm()
    return render(request, "analyzer/login.html", {"form": form, 'page_title': 'Log In'})


def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.") 
    return redirect('dashboard')