@echo off
setlocal

python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

if not exist .env copy .env.example .env

echo Installation completed.
echo Edit .env if needed, then run run_mcp_server.cmd.
