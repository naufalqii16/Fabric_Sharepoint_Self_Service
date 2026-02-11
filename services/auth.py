import requests
from services.config import TENANT_ID, CLIENT_ID, CLIENT_SECRET, GRAPH_SCOPE

class AuthService:
    def __init__(self):
        self.graph_token = None
        self.fabric_token = None
    
    def get_token(self, scope):
        """Get Azure AD access token"""
        token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
        token_data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials",
            "scope": scope,
        }
        
        try:
            response = requests.post(token_url, data=token_data, timeout=30)
            response.raise_for_status()
            return response.json()["access_token"]
        except Exception as e:
            raise Exception(f"Failed to get token: {e}")
    
    def get_graph_token(self):
        """Get Microsoft Graph token"""
        if not self.graph_token:
            self.graph_token = self.get_token(GRAPH_SCOPE)
        return self.graph_token
    
    # def get_fabric_token(self):
    #     """Get Fabric API token"""
    #     if not self.fabric_token:
    #         self.fabric_token = self.get_token(FABRIC_SCOPE)
    #     return self.fabric_token
    
    def refresh(self):
        """Refresh all tokens"""
        self.graph_token = None
        # self.fabric_token = None

auth = AuthService()