#!/bin/bash

# Step 1: Enable BBR
echo "Enabling BBR..."
if ! sysctl net.ipv4.tcp_congestion_control | grep -q 'bbr'; then
    echo "net.core.default_qdisc=fq" >> /etc/sysctl.conf
    echo "net.ipv4.tcp_congestion_control=bbr" >> /etc/sysctl.conf
    sysctl -p
    if sysctl net.ipv4.tcp_congestion_control | grep -q 'bbr'; then
        echo "BBR enabled successfully."
    else
        echo "Failed to enable BBR."
        exit 1
    fi
else
    echo "BBR is already enabled."
fi

# Step 2: Install Python 3.9 in the current directory
PYTHON_DIR="$PWD/python3.9"
if [ ! -d "$PYTHON_DIR" ]; then
    echo "Downloading and installing Python 3.9..."
    wget https://www.python.org/ftp/python/3.9.18/Python-3.9.18.tgz
    tar -xzf Python-3.9.18.tgz
    cd Python-3.9.18
    ./configure --prefix="$PYTHON_DIR"
    make
    make install
    cd ..
    rm -rf Python-3.9.18 Python-3.9.18.tgz
else
    echo "Python 3.9 is already installed."
fi

# Use the locally installed Python 3.9
PYTHON="$PYTHON_DIR/bin/python3.9"

if ! $PYTHON --version > /dev/null 2>&1; then
    echo "Failed to install Python 3.9."
    exit 1
fi

# Step 3: Install required Python packages using the local Python environment
echo "Installing Python packages: asyncio, pyppeteer, BeautifulSoup..."
$PYTHON -m ensurepip --upgrade
$PYTHON -m pip install --upgrade pip
$PYTHON -m pip install asyncio pyppeteer beautifulsoup4
if $PYTHON -c "import asyncio, pyppeteer, bs4" > /dev/null 2>&1; then
    echo "Python packages installed successfully."
else
    echo "Failed to install Python packages."
    exit 1
fi

# Step 4: Random port and run china_connectivity_checker.py
CONFIG_FILE_PATH="./config.json"
attempts=0
while [ $attempts -lt 5 ]; do
    PORT=$((63000 + RANDOM % 1000))
    echo "Checking connectivity on port $PORT..."
    if $PYTHON china_connectivity_checker.py $PORT; then
        echo "Connectivity check passed on port $PORT. Updating config.json..."
        $PYTHON config_updater.py $CONFIG_FILE_PATH $PORT
        break
    else
        echo "Connectivity check failed on port $PORT."
        attempts=$((attempts + 1))
    fi
done

if [ $attempts -ge 5 ]; then
    echo "Failed to find a working port after 5 attempts."
    exit 1
fi

# Step 5: Copy config.json and start xray service
echo "Copying config.json to /etc/xray/config.json..."
cp config.json /etc/xray/config.json

echo "Starting xray service..."
docker-compose -f compose.yaml up -d

# Step 6: Final connectivity check
echo "Performing final connectivity check..."
if $PYTHON china_connectivity_checker.py $PORT; then
    echo "Setup completed successfully."
else
    echo "Final connectivity check failed. Setup was not successful."
    exit 1
fi
