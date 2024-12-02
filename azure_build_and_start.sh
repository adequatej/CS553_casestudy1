#! /bin/bash

# Build the container
docker build -t adequatej/spotifychatbot .

# Push the container to docker hub
docker push adequatej/spotifychatbot

# Run the container on Azure
az containerapp create \
  --name cs553azure \
  --resource-group WPI-asc-export \
  --environment managedEnvironment-WPIascexport-9633 \
  --image adequatej/spotifychatbot \
  --ingress external \
  --target-port 7860

# Get the URL
az containerapp show \
  --name cs553azure \
  --resource-group WPI-asc-export \
  --query properties.configuration.ingress.fqdn
