#!/bin/bash

# ====================================================================
# FINAL PROJECT TKA - KELOMPOK 3
# AUTOMATION DEPLOYMENT SCRIPT (Raynard - DEVOPS)
# ====================================================================

VM1_IP="20.2.138.164" # Webserver / Load Balancer
VM2_IP="20.6.129.82"  # Backend 1
VM3_IP="20.2.140.143" # Backend 2
VM4_IP="70.153.26.17" # Database Server

echo "======================================================="
echo " STARTING AUTOMATED DEPLOYMENT - KELOMPOK 3 "
echo "======================================================="

# --------------------------------------------------------------------
# STEP 1: SETUP VM 4 (DATABASE MONGO)
# --------------------------------------------------------------------
echo "--> Configured Database Server (VM 4)..."
ssh Dbaseserver@$VM4_IP << 'EOF'
  if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
  fi
  sudo docker rm -f mongodb-server 2>/dev/null
  sudo docker run -d --name mongodb-server -p 27017:27017 --restart always mongo:latest
  sleep 3
  sudo docker cp /home/Dbaseserver/DB/dump/. mongodb-server:/tmp/dump
  sudo docker exec -i mongodb-server mongorestore /tmp/dump
EOF

# --------------------------------------------------------------------
# STEP 2: SETUP VM 2 (BACKEND NODE 1)
# --------------------------------------------------------------------
echo "--> Configuring Backend Node 1 (VM 2)..."
ssh Backend1@$VM2_IP << 'EOF'
  if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
  fi
  mkdir -p Resources/BE
  cp BE/app.py Resources/BE/ 2>/dev/null
  sudo docker rm -f backend-node1 2>/dev/null
  sudo docker build -t flask-backend .
  sudo docker run -d --name backend-node1 -p 5000:5000 -e MONGO_URI="mongodb://70.153.26.17:27017/ordermanagement" --restart always flask-backend
EOF

# --------------------------------------------------------------------
# STEP 3: SETUP VM 3 (BACKEND NODE 2)
# --------------------------------------------------------------------
echo "--> Configuring Backend Node 2 (VM 3)..."
ssh Backend2@$VM3_IP << 'EOF'
  if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
  fi
  mkdir -p Resources/BE
  cp BE/app.py Resources/BE/ 2>/dev/null
  sudo docker rm -f backend-node2 2>/dev/null
  sudo docker build -t flask-backend .
  sudo docker run -d --name backend-node2 -p 5000:5000 -e MONGO_URI="mongodb://70.153.26.17:27017/ordermanagement" --restart always flask-backend
EOF

# --------------------------------------------------------------------
# STEP 4: SETUP VM 1 (NGINX LOAD BALANCER & FRONTEND)
# --------------------------------------------------------------------
echo "--> Configuring Web Server Load Balancer (VM 1)..."
ssh Webserver@$VM1_IP << 'EOF'
  if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
  fi
  sudo docker rm -f nginx-lb 2>/dev/null
  sudo docker run -d --name nginx-lb \
    -v /home/Webserver/nginx.conf:/etc/nginx/nginx.conf:ro \
    -v /home/Webserver/FE:/usr/share/nginx/html:ro \
    -p 80:80 --restart always nginx:latest
EOF

echo "======================================================="
echo " DEPLOYMENT SUCCESSFUL! ALL SYSTEMS LIVE! "
echo " URL: http://$VM1_IP "
echo "======================================================="