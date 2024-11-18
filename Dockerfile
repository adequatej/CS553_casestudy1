FROM python:3.10-slim

WORKDIR /opt/app
COPY . .
RUN pip install --no-cache-dir -r /opt/app/requirements.txt

# Install packages that we need. vim is for helping with debugging
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get upgrade -yq ca-certificates && \
    apt-get install -yq --no-install-recommends \
    prometheus-node-exporter

# EXPOSE 7860
# EXPOSE 8000
# EXPOSE 9100
EXPOSE 2901
EXPOSE 2902
EXPOSE 2903
EXPOSE 2904
EXPOSE 2905
EXPOSE 2906
EXPOSE 2907
EXPOSE 2908
EXPOSE 2909
EXPOSE 2910

ENV GRADIO_SERVER_NAME="0.0.0.0"

CMD bash -c "prometheus-node-exporter --web.listen-address=':9100' & python /opt/app/app.py"