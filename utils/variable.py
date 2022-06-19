import json

with open('config.json', 'r') as f:
    config = json.load(f)
    default_password = config['DEFAULT_PASSWORD']
    default_email = config['DEFAULT_EMAIL']
