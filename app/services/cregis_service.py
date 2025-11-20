"""
Cregis Payment Service
Handles integration with Cregis Payment Engine for cryptocurrency deposits
"""
import hashlib
import uuid
import time
import requests
from typing import Optional, Dict, Any
from app.core.config import settings


class CregisService:
    """Service for interacting with Cregis Payment Engine API"""
    
    def __init__(self):
        self.project_id = settings.CREGIS_PAYMENT_PROJECT_ID
        self.api_key = settings.CREGIS_PAYMENT_API_KEY
        self.secret = settings.CREGIS_PAYMENT_SECRET
        self.gateway_url = settings.CREGIS_GATEWAY_URL.rstrip('/')
    
    def _generate_signature(self, params: Dict[str, Any], secret_key: str) -> str:
        """
        Generate MD5 signature for Cregis API requests
        
        Steps:
        1. Filter out null, undefined, and empty string values
        2. Sort parameters by key alphabetically
        3. Create string: secretKey + sorted_key_value_pairs
        4. Generate MD5 hash (lowercase hex)
        """
        # Filter out null, None, and empty string values
        filtered = {k: v for k, v in params.items() 
                   if v is not None and v != ""}
        
        # Sort parameters by key
        sorted_params = sorted(filtered.items())
        
        # Create string to sign: secretKey + sorted key-value pairs
        string_to_sign = secret_key + "".join([f"{k}{v}" for k, v in sorted_params])
        
        # Generate MD5 hash in lowercase
        signature = hashlib.md5(string_to_sign.encode()).hexdigest().lower()
        
        return signature
    
    def create_payment_order(
        self,
        order_amount: str,
        order_currency: str,
        callback_url: str,
        success_url: str,
        cancel_url: str,
        payer_id: Optional[str] = None,
        valid_time: int = 30
    ) -> Dict[str, Any]:
        """
        Create a payment order with Cregis
        
        Args:
            order_amount: Amount to deposit (e.g., "100.00")
            order_currency: Currency (e.g., "USDT")
            callback_url: Webhook URL for payment notifications
            success_url: Redirect URL after successful payment
            cancel_url: Redirect URL after cancelled payment
            payer_id: Optional payer ID
            valid_time: Valid time in minutes (default 30, range: 10-60)
        
        Returns:
            Dict with success flag and data or error message
        """
        try:
            # Validate inputs
            if not order_amount or not order_amount.strip():
                return {"success": False, "error": "orderAmount must not be empty"}
            if not order_currency or not order_currency.strip():
                return {"success": False, "error": "orderCurrency must not be empty"}
            if not callback_url or not callback_url.strip():
                return {"success": False, "error": "callbackUrl must not be empty"}
            
            # Clamp valid_time to acceptable range (10-60 minutes)
            valid_time = max(10, min(60, valid_time))
            
            # Generate order ID and prepare payload
            order_id = str(uuid.uuid4())
            timestamp = int(time.time() * 1000)  # Milliseconds
            nonce = uuid.uuid4().hex[:8]
            
            payload: Dict[str, Any] = {
                "pid": int(self.project_id),
                "nonce": nonce,
                "timestamp": timestamp,
                "order_id": order_id,
                "order_amount": order_amount.strip(),
                "order_currency": order_currency.strip(),
                "callback_url": callback_url.strip(),
                "success_url": success_url.strip(),
                "cancel_url": cancel_url.strip(),
                "valid_time": valid_time,
            }
            
            # Add payer_id if provided
            if payer_id and payer_id.strip():
                payload["payer_id"] = payer_id.strip()
            
            # Generate signature
            sign = self._generate_signature(payload, self.api_key)
            request_data = {**payload, "sign": sign}
            
            # Make request to Cregis API
            url = f"{self.gateway_url}/api/v2/checkout"
            response = requests.post(
                url,
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if not response.ok:
                error_text = response.text
                return {
                    "success": False,
                    "error": f"Cregis API request failed with status {response.status_code}: {error_text}"
                }
            
            data = response.json()
            
            # Check response code
            if data.get("code") != "00000":
                error_msg = data.get("msg", "Unknown error")
                
                # Provide helpful error messages
                if "whitelist" in error_msg.lower():
                    # Extract IP from error message if possible
                    return {
                        "success": False,
                        "error": f"IP whitelist error: Your server IP needs to be added to Cregis whitelist. Please contact Cregis support."
                    }
                
                return {"success": False, "error": f"Cregis API error: {error_msg}"}
            
            # Extract payment data
            payment_data = data.get("data", {})
            
            if not payment_data.get("payment_info") or len(payment_data.get("payment_info", [])) == 0:
                return {
                    "success": False,
                    "error": "Cregis API did not return payment information"
                }
            
            return {
                "success": True,
                "data": {
                    "cregis_id": payment_data.get("cregis_id"),
                    "checkout_url": payment_data.get("checkout_url"),
                    "payment_info": payment_data.get("payment_info", []),
                    "expire_time": payment_data.get("expire_time"),
                    "orderId": order_id,
                }
            }
            
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
    
    def verify_callback_signature(
        self,
        params: Dict[str, Any],
        received_sign: str
    ) -> bool:
        """
        Verify Cregis callback signature
        
        Args:
            params: Callback parameters (excluding 'sign')
            received_sign: Signature received from Cregis
        
        Returns:
            True if signature is valid, False otherwise
        """
        # Remove 'sign' from params if present
        params_without_sign = {k: v for k, v in params.items() if k != "sign"}
        
        # Generate expected signature
        expected_sign = self._generate_signature(params_without_sign, self.api_key)
        
        # Compare signatures (case-insensitive)
        return expected_sign.lower() == received_sign.lower()


# Create singleton instance
cregis_service = CregisService()

