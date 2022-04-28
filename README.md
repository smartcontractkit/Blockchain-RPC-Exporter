# EVM RPC Websocket Exporter
Simple exporter used to scrape different metrics from EVM compatible websocket RPCs.

## Metrics
For list of metrics and explanations please check [collect method](src/exporter.py#L42-L79) in exporter source-code.
For available labels please see [metric_labels](src/exporter.py#L37-L40) list in exporter source-code.

# Disclaimer
Please note that this tool is in early development stage, and as such should not be used to influence business crictical decisions.
The project in it's current form suits our short-term needs and will receive limited support. We encourage you to fork the project, and extend it with additional functionality you might need.
This project was inspired by [blackbox-websocket-exporter](https://github.com/smohsensh/blackbox-websocket-exporter)

## Development
It is recommended that you install [pre-commit](https://pre-commit.com/) so that automated linting and formatting checks are performed before each commit. Run:
```bash
pip install pre-commit
pre-commit install
```
### Running locally
1. Make sure you have python3 installed (>3.9.10)
2. Set-up your python environment
```bash
pip3 install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```
1. Generate valid exporter config and validation file. For example see [config example](config/exporter_example/config.yml) and [validation example](config/exporter_example/validation.yml).
2. Export paths of generated configuration files relative to `src/exporter.py`:
```bash
export VALIDATION_FILE_PATH="validation.yml" # For example if we saved validation config file in src/validation.yml
export CONFIG_FILE_PATH="config.yml"  # For example if we saved config file in src/config.yml
```
3. Finally you can run the exporter
```bash
python exporter.py
```
### Run with docker-compose
1. Generate valid exporter config and validation file. For example see [config example](config/exporter_example/config.yml) and [validation example](config/exporter_example/validation.yml).
2. Export paths of generated configuration files relative to `docker-compose.yml`:
```bash
export VALIDATION_FILE_PATH="src/validation.yml" # For example if we saved validation config file in src/validation.yml
export CONFIG_FILE_PATH="src/config.yml"  # For example if we saved config file in src/config.yml
```
3. Execute
```bash
docker-compose build
docker-compose-up
curl localhost:8000/metrics # Exporter
curl localhost:3000         # Grafana
curl localhost:9090         # Prometheus
```
