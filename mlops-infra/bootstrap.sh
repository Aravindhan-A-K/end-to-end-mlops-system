#!/bin/bash
set -e

echo "Updating packages..."
apt-get update -y

echo "Installing Docker..."
apt-get install -y docker.io

systemctl enable docker
systemctl start docker

echo "Installing Git..."
apt-get install -y git

echo "Creating project directory..."
mkdir -p /home/ubuntu/mlops

cd /home/ubuntu/mlops

echo "Downloading configuration files..."

curl -O https://raw.githubusercontent.com/Aravindhan-A-K/end-to-end-mlops-system/master/mlops-infra/docker-compose.yml

curl -O https://raw.githubusercontent.com/Aravindhan-A-K/end-to-end-mlops-system/master/mlops-infra/nginx.conf

echo "Starting containers..."

docker compose up postgres mlflow -d
docker compose up app -d
docker compose up nginx -d


echo "Bootstrap completed."
