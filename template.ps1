# Creating Directory Structure
New-Item -ItemType Directory -Force -Path src
New-Item -ItemType Directory -Force -Path research

New-Item -ItemType File -Force -Path src\__init__.py
New-Item -ItemType File -Force -Path src\helpers.py
New-Item -ItemType File -Force -Path src\prompts.py
New-Item -ItemType File -Force -Path .env
New-Item -ItemType File -Force -Path setup.py
New-Item -ItemType File -Force -Path app.py
New-Item -ItemType File -Force -Path research\trials.ipynb
New-Item -ItemType File -Force -Path requirements.txt

Write-Host "Directory structure created successfully."
