import os
from settings import configuration
cfg_file_path = os.getenv('CONFIG_FILE_PATH', default='/config/config.yml')
valid_file_path = os.getenv('VALIDATION_FILE_PATH', default='/config/validation.yml')
cfg = configuration(cfg_file_path, valid_file_path)
