#!/bin/bash

# Anzeigematrix Display Server - Installations-Script für Raspberry Pi

echo "🚀 Installing Anzeigematrix Display Server..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and pip
echo "🐍 Installing Python dependencies..."
sudo apt install python3 python3-pip -y

# Install Flask and watchdog
echo "🌶️ Installing Flask and watchdog..."
pip3 install flask watchdog

# Create directories
echo "📁 Creating application directories..."
mkdir -p /home/pi/anzeigematrix
mkdir -p /home/pi/apps/dashboard
mkdir -p /home/pi/apps/weather
mkdir -p /home/pi/apps/calendar
mkdir -p /home/pi/apps/db_fahrplan
mkdir -p /home/pi/apps/news
mkdir -p /home/pi/apps/slideshow
mkdir -p /home/pi/apps/menu
mkdir -p /home/pi/apps/uhr
cd /home/pi/anzeigematrix

# Note: User needs to copy files manually
echo "📋 Please copy the following files to /home/pi/anzeigematrix/:"
echo "   - display_server.py"
echo "   - display_manager.py"
echo "   - clock_app.py (place in /home/pi/apps/uhr/)"
echo "   You can use scp, USB stick, or download them directly"

# Make executable
if [ -f "display_server.py" ]; then
    chmod +x display_server.py
    echo "✅ Made display_server.py executable"
fi

if [ -f "display_manager.py" ]; then
    chmod +x display_manager.py
    echo "✅ Made display_manager.py executable"
fi

# Create systemd service for Flask server
echo "⚙️ Creating systemd service for Flask server..."
sudo tee /etc/systemd/system/anzeigematrix-server.service > /dev/null <<EOF
[Unit]
Description=Anzeigematrix Flask Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/anzeigematrix
ExecStart=/usr/bin/python3 /home/pi/anzeigematrix/display_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create systemd service for Display Manager
echo "⚙️ Creating systemd service for Display Manager..."
sudo tee /etc/systemd/system/anzeigematrix-manager.service > /dev/null <<EOF
[Unit]
Description=Anzeigematrix Display Manager
After=network.target anzeigematrix-server.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/anzeigematrix
ExecStart=/usr/bin/python3 /home/pi/anzeigematrix/display_manager.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable services (will start after reboot)
sudo systemctl enable anzeigematrix-server.service
sudo systemctl enable anzeigematrix-manager.service

# Configure firewall (if ufw is installed)
if command -v ufw &> /dev/null; then
    echo "🔥 Configuring firewall..."
    sudo ufw allow 80/tcp
fi

echo ""
echo "✅ Installation completed!"
echo ""
echo "📋 Next steps:"
echo "1. Copy display_server.py and display_manager.py to /home/pi/anzeigematrix/"
echo "2. Copy clock_app.py to /home/pi/apps/uhr/"
echo "3. Test the server: cd /home/pi/anzeigematrix && python3 display_server.py"
echo "4. Test the manager: cd /home/pi/anzeigematrix && python3 display_manager.py"
echo "5. Start the services:"
echo "   sudo systemctl start anzeigematrix-server.service"
echo "   sudo systemctl start anzeigematrix-manager.service"
echo "6. Check status:"
echo "   sudo systemctl status anzeigematrix-server.service"
echo "   sudo systemctl status anzeigematrix-manager.service"
echo ""
echo "🌐 Your server will be available at:"
echo "   http://$(hostname -I | awk '{print $1}'):80"
echo ""
echo "🔧 Useful commands:"
echo "   # Server service"
echo "   sudo systemctl status anzeigematrix-server.service  # Check server status"
echo "   sudo systemctl restart anzeigematrix-server.service # Restart server"
echo "   sudo journalctl -u anzeigematrix-server.service -f  # View server logs"
echo ""
echo "   # Manager service"
echo "   sudo systemctl status anzeigematrix-manager.service  # Check manager status"
echo "   sudo systemctl restart anzeigematrix-manager.service # Restart manager"
echo "   sudo journalctl -u anzeigematrix-manager.service -f  # View manager logs"
