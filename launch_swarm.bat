@echo off
cd C:\Users\Admin\Desktop\polymarket-swarm
start python run_daily.py
python -m streamlit run app.py --server.headless true