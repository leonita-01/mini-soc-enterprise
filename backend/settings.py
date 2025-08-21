import os, yaml
_CFG=None
def load_config(path='backend/config.yml'):
    global _CFG
    if _CFG is None:
        with open(path, 'r') as f:
            _CFG = yaml.safe_load(f)
    return _CFG
def get_jwt_secret():
    return os.getenv('JWT_SECRET') or load_config().get('jwt_secret', 'dev-secret')
def get_api_key():
    return os.getenv('API_KEY') or load_config().get('api_key', 'dev-key-12345')
def get_database_url():
    return os.getenv('DATABASE_URL', 'sqlite:///soc.db')
