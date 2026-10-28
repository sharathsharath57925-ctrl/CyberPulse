



import runpy
from pathlib import Path
from database.db import init_db

# Initialize the existing database
init_db()

# Run the dashboard script on every Streamlit rerun
dashboard_path = Path(__file__).parent / "frontend" / "dashboard.py"
runpy.run_path(str(dashboard_path), run_name="__main__")
