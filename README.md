# Blockchain RPC Exporter
The exporter is used to scrape metrics from blockchain RPC endpoints. The purpose of this exporter is to perform black-box testing on RPC endpoints.
## Metrics
Exporter currently supports all EVM-compatible chains. In addition, there is limited support for the following chains:
- Cardano (wss)
- Conflux (wss)
- Solana (https & wss)
- Bitcoin (https)
- Dogecoin (https)
- Filecoin (https)
- Starkware (https)

## Available Metrics

# Disclaimer
Please note that this tool is in the early development stage and should not be used to influence critical business decisions.
The project in its current form suits our short-term needs and will receive limited support. We encourage you to fork the project and extend it with additional functionality you might need.

## Development
You should install [pre-commit](https://pre-commit.com/) so that automated linting and formatting checks are performed before each commit.

Run:
```bash
pip install pre-commit
pre-commit install
```
### Running locally
1. Make sure you have python3 installed (>3.11)
2. Set up your python environment
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
