#!/bin/bash
# IF YOU DO NOT KNOW HOW ALL THIS WORKS, DO NOT CHANGE ANYTHING


# Setup
set -e
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
WHITE='\033[1;37m'
NC='\033[0m'


# Vars
remote_host="158.160.135.246"
private_key="portforward_key"
port_file="/tmp/random_port.txt"


# Loading or generating port
echo "Loading or generating random port..."
if [[ -f "$port_file" ]]; then
  random_port=$(cat "$port_file")
  echo "Loaded port: $random_port"
else
  random_port=$(awk -v min=1024 -v max=65535 'BEGIN{srand(); print int(min+rand()*(max-min+1))}')
  echo "$random_port" > "$port_file"
  echo "Generated port: $random_port"
fi


# Check uv is installed
if ! command -v uv &> /dev/null; then
  echo -e "${RED}uv is not installed. Install it first: curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
  exit 1
fi
echo "uv found: $(uv --version)"

# Installing Project's dependencies
echo "Installing Project's dependencies..."
uv sync
echo "Dependencies installed successfully."


# Starting the app
echo -e "${WHITE}Launching the app...${NC}"
uv run fastapi dev app/api/main.py --host 0.0.0.0 --port 6872 &

# Starting the web-client (streamlit)
PYTHONPATH=$(pwd) uv run streamlit run app/web/streamlit_app.py --server.port=8502 --server.address=0.0.0.0


# Log address for registration
echo "Your address for registration is:"
echo "http://$remote_host:$random_port"
