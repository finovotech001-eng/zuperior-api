"""
MT5 Service
Handles integration with MT5 API for balance operations
"""
import requests
from typing import Dict, Any, Optional
from app.core.config import settings


class MT5Service:
    """Service for interacting with MT5 API"""
    
    def __init__(self):
        self.api_url = settings.MT5_API_URL.rstrip('/') if settings.MT5_API_URL else ""
        self.api_token = settings.MT5_API_TOKEN
    
    def add_client_balance(
        self,
        login: str,
        balance: float,
        comment: str
    ) -> Dict[str, Any]:
        """
        Add balance to MT5 account using AddClientBalance API
        
        Args:
            login: MT5 account login (account ID)
            balance: Amount to credit
            comment: Transaction comment
        
        Returns:
            Dict with Success flag and Data or error message
        """
        try:
            if not self.api_url:
                return {
                    "Success": False,
                    "Message": "MT5 API URL not configured"
                }
            
            # Convert login to string
            login_str = str(login).strip()
            if not login_str:
                return {
                    "Success": False,
                    "Message": "Invalid MT5 login"
                }
            
            # Prepare request
            url = f"{self.api_url}/api/Users/{login_str}/AddClientBalance"
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Add authorization if token is configured
            if self.api_token:
                headers["Authorization"] = f"Bearer {self.api_token}"
            
            payload = {
                "balance": float(balance),
                "comment": comment
            }
            
            # Make request
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if not response.ok:
                error_text = response.text
                return {
                    "Success": False,
                    "Message": f"MT5 API request failed with status {response.status_code}: {error_text}"
                }
            
            # Try to parse JSON response
            try:
                data = response.json()
                return data
            except ValueError:
                # If response is not JSON, return text
                return {
                    "Success": False,
                    "Message": f"MT5 API returned invalid JSON: {response.text}"
                }
            
        except requests.exceptions.RequestException as e:
            return {
                "Success": False,
                "Message": f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                "Success": False,
                "Message": f"Unexpected error: {str(e)}"
            }


# Create singleton instance
mt5_service = MT5Service()

