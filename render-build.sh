# Render Deployment Script for Training Wheels Trading Dashboard
# This script installs dependencies and starts the Streamlit application

#!/bin/bash

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories for the application
mkdir -p logs
mkdir -p data
mkdir -p temp

# Set environment variables for production
export STREAMLIT_SERVER_PORT=${PORT:-8501}
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_ENABLE_CORS=false
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true

# Create Streamlit configuration directory
mkdir -p ~/.streamlit

# Create Streamlit config file
cat > ~/.streamlit/config.toml << EOF
[server]
port = ${PORT:-8501}
address = "0.0.0.0"
headless = true
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 200

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[logger]
level = "info"
EOF

echo "Starting Training Wheels Trading Dashboard..."
echo "Application will be available on port ${PORT:-8501}"

# Start the Streamlit application
streamlit run streamlit_app.py --server.port=${PORT:-8501} --server.address=0.0.0.0
