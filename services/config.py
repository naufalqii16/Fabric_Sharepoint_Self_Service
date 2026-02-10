import os
from dotenv import load_dotenv

load_dotenv()

# Azure AD
TENANT_ID = os.getenv('TENANT_ID')
CLIENT_ID = os.getenv('APP_ID')
CLIENT_SECRET = os.getenv('SECRET_VALUE')

# SharePoint
SITE_ID = os.getenv('SITE_ID')
DRIVE_ID = os.getenv('DRIVE_ID')
SHAREPOINT_DOMAIN = os.getenv('SHAREPOINT_DOMAIN', 'siloamhospitals.sharepoint.com')
SITE_NAME = os.getenv('SITE_NAME', 'DataEngineering')

# Fabric
DEV_WS_ID = os.getenv('DEV_WS_ID')
LAKEHOUSE_ID = os.getenv('LAKEHOUSE_ID')
FABRIC_API_URL = "https://api.fabric.microsoft.com/v1"

# API Scopes
GRAPH_SCOPE = "https://graph.microsoft.com/.default"
# FABRIC_SCOPE = "https://analysis.windows.net/powerbi/api/.default"

def validate_config():
    """Validate all required config"""
    missing = [name for name, val in [
        ('TENANT_ID', TENANT_ID),
        ('CLIENT_ID', CLIENT_ID),
        ('CLIENT_SECRET', CLIENT_SECRET),
        ('SITE_ID', SITE_ID),
        ('DRIVE_ID', DRIVE_ID),
        ('DEV_WS_ID', DEV_WS_ID)
    ] if not val]
    
    if missing:
        raise ValueError(f"Missing required config: {', '.join(missing)}")
    
    return True