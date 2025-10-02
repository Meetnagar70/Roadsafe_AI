🛣️ RoadSafeAI – Smart Accident Pattern Analyzer & Hotspot Predictor
RoadSafeAI is a Django-based web application designed for the analysis and visualization of road accident data. It empowers users to explore accident trends, identify high-risk zones, and contribute new data to a system that dynamically updates its understanding of accident hotspots using a DBSCAN clustering model.

📋 Features
Multi-level Dashboards:

All-India Dashboard: A comprehensive overview of national accident statistics, including severity, road types, monthly trends, and a heatmap of accident density.

State-wise Dashboard: Detailed analysis for individual states with district-level filtering, showing local trends and hotspots.

Interactive District Analysis:

A dynamic page with dropdowns to select any state and district.

Displays an interactive map with accident locations clustered by an ML model.

Color-coded hotspots to instantly identify dangerous areas.

Detailed popups for each accident pin.

User Authentication:

Secure user registration and login system powered by Django's built-in authentication.

Protected routes ensure that only logged-in users can submit new data.

Dynamic Data Submission:

An interactive form where authenticated users can report new accidents.

Automatic Geolocation: Users click on a map to get the precise latitude and longitude, eliminating manual entry.

Live System Updates: Submitting a new report automatically appends the data to the relevant CSV files (district, state, and national).

Live ML Model Re-training:

After each new submission, the system automatically re-trains the DBSCAN clustering model on the updated dataset and saves the new model. This ensures the hotspot analysis is always up-to-date.

🛠️ Tech Stack
Backend: Django, Python 3.10

Data Analysis & ML: Pandas, Scikit-learn, Joblib

Data Visualization: Folium (for server-side heatmaps), Chart.js (for interactive charts), Leaflet.js (for client-side interactive maps)

Frontend: HTML5, CSS3, Bootstrap 5

Data Storage: CSV files (File-based database approach)

🚀 Setup and Installation
Follow these steps to get the project running on your local machine.

1. Prerequisites
Python 3.10 installed on your system.

pip and venv for package management.

2. Clone the Repository
git clone "Not on Git yet Comming Soon"

3. Create and Activate a Virtual Environment
On Windows:

python -m venv venv
.\venv\Scripts\activate

On macOS/Linux:

python3 -m venv venv
source venv/bin/activate

4. Install Dependencies
First, create a requirements.txt file by running this command in your terminal:

pip freeze > requirements.txt

Then, install the required packages:

pip install -r requirements.txt

Note: If you don't have a requirements.txt file, you can install the packages manually:

pip install django pandas scikit-learn joblib folium

5. Apply Migrations
This will set up the necessary tables for Django's authentication system.

python manage.py migrate

6. Run the Development Server
python manage.py runserver

The application will be available at http://127.0.0.1:8000/.

📂 Folder Structure
The project uses a file-based data storage system. Ensure your data is structured as follows:

roadsafe_ai/
├── analyzer/
│   ├── models/
│   │   └── dbscan_model.joblib  # The ML model
│   ├── templates/
│   ├── views.py
│   └── ...
├── data/
│   ├── all_india.csv
│   ├── states/
│   │   ├── Gujarat.csv
│   │   └── ...
│   └── districts/
│       ├── Gujarat/
│       │   ├── Ahmedabad.csv
│       │   └── ...
│       └── ...
└── manage.py

🖥️ How to Use
Register an Account: Navigate to the "Sign Up" page to create a new user account.

Explore Data: Browse the All-India and State-wise dashboards to view analytics.

Analyze a District: Go to the "District Analysis" page. Select a state from the first dropdown (the page will reload), then select a district from the second dropdown and click "Show Analysis" to view the interactive hotspot map.

Submit an Accident:

Log in to your account.

Click the "Submit New Report" button.

Click on the map to place a marker for the accident location.

Fill out the rest of the form details.

Click "Submit Report". The system will update the data and re-train the ML model.