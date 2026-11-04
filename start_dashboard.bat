@echo off
cd /d "C:\Users\Mariem\Documents\retail-data-platform"
call .venv\Scripts\activate.bat
streamlit run dashboards\sales_dashboard.py
pause