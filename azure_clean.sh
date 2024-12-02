#! /bin/bash

# Build the container
az containerapp delete \
  --name cs553azure \
  --resource-group rcpaffenroth-rg
