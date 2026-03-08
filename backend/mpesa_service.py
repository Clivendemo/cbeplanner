"""
M-Pesa Daraja API Integration Service
Handles STK Push payments for wallet top-ups
"""

import os
import base64
import httpx
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

logger = logging.getLogger(__name__)

class MpesaService:
    """
    M-Pesa Daraja API Service for STK Push payments
    """
    
    def __init__(self):
        self.consumer_key = os.getenv('MPESA_CONSUMER_KEY', '')
        self.consumer_secret = os.getenv('MPESA_CONSUMER_SECRET', '')
        self.shortcode = os.getenv('MPESA_SHORTCODE', '174379')  # Sandbox default
        self.passkey = os.getenv('MPESA_PASSKEY', 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919')  # Sandbox default
        self.callback_url = os.getenv('MPESA_CALLBACK_URL', '')
        self.env = os.getenv('MPESA_ENV', 'sandbox')
        
        # Set base URL based on environment
        if self.env == 'production':
            self.base_url = 'https://api.safaricom.co.ke'
        else:
            self.base_url = 'https://sandbox.safaricom.co.ke'
        
        self._access_token = None
        self._token_expiry = None
    
    async def get_access_token(self) -> str:
        """
        Get OAuth access token from M-Pesa API
        Caches token until expiry
        """
        # Check if we have a valid cached token
        if self._access_token and self._token_expiry:
            if datetime.utcnow() < self._token_expiry:
                return self._access_token
        
        # Generate new token
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        
        # Create basic auth header
        credentials = f"{self.consumer_key}:{self.consumer_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                
                self._access_token = data.get('access_token')
                # Token expires in 3599 seconds, we'll refresh at 3500
                from datetime import timedelta
                self._token_expiry = datetime.utcnow() + timedelta(seconds=3500)
                
                logger.info("M-Pesa access token obtained successfully")
                return self._access_token
                
            except httpx.HTTPError as e:
                logger.error(f"Failed to get M-Pesa access token: {str(e)}")
                raise Exception(f"M-Pesa authentication failed: {str(e)}")
    
    def generate_password(self, timestamp: str) -> str:
        """
        Generate the password for STK Push request
        Password = Base64(Shortcode + Passkey + Timestamp)
        """
        data_to_encode = f"{self.shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(data_to_encode.encode()).decode()
    
    def generate_timestamp(self) -> str:
        """
        Generate timestamp in format YYYYMMDDHHmmss
        Must be in East Africa Time (EAT = UTC+3) for Safaricom API
        """
        from datetime import timezone, timedelta
        eat = timezone(timedelta(hours=3))  # East Africa Time UTC+3
        return datetime.now(eat).strftime('%Y%m%d%H%M%S')
    
    def generate_tx_ref(self) -> str:
        """
        Generate unique transaction reference
        Format: CBE-YYYYMMDDHHMMSS-XXXX
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_id = uuid.uuid4().hex[:8].upper()
        return f"CBE-{timestamp}-{unique_id}"
    
    def format_phone_number(self, phone: str) -> str:
        """
        Format phone number to 254XXXXXXXXX format
        Handles various input formats:
        - 0712345678 -> 254712345678
        - +254712345678 -> 254712345678
        - 254712345678 -> 254712345678
        - 712345678 -> 254712345678
        """
        # Remove any spaces, dashes, or special characters
        phone = ''.join(filter(str.isdigit, phone.replace('+', '')))
        
        # Handle different formats
        if phone.startswith('0') and len(phone) == 10:
            return '254' + phone[1:]
        elif phone.startswith('254') and len(phone) == 12:
            return phone
        elif len(phone) == 9:
            return '254' + phone
        else:
            raise ValueError(f"Invalid phone number format: {phone}")
    
    async def initiate_stk_push(
        self,
        phone_number: str,
        amount: int,
        account_reference: str,
        transaction_desc: str = "Wallet Top Up"
    ) -> Dict[str, Any]:
        """
        Initiate M-Pesa STK Push payment
        
        Args:
            phone_number: Customer phone number
            amount: Amount in KES (integer)
            account_reference: Reference for the transaction
            transaction_desc: Description shown to customer
            
        Returns:
            Dict with CheckoutRequestID, MerchantRequestID, etc.
        """
        # Get access token
        access_token = await self.get_access_token()
        
        # Generate timestamp and password
        timestamp = self.generate_timestamp()
        password = self.generate_password(timestamp)
        
        # Format phone number
        formatted_phone = self.format_phone_number(phone_number)
        
        # Prepare request payload
        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": formatted_phone,
            "PartyB": self.shortcode,
            "PhoneNumber": formatted_phone,
            "CallBackURL": self.callback_url,
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                logger.info(f"Initiating STK Push for {formatted_phone}, amount: {amount}")
                logger.info(f"STK Push payload: BusinessShortCode={payload['BusinessShortCode']}, Timestamp={payload['Timestamp']}")
                
                response = await client.post(url, json=payload, headers=headers, timeout=30.0)
                
                # Log response details before raising for status
                logger.info(f"STK Push HTTP Status: {response.status_code}")
                logger.info(f"STK Push Response Body: {response.text}")
                
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"STK Push response: {data}")
                
                if data.get('ResponseCode') == '0':
                    return {
                        "success": True,
                        "checkoutRequestID": data.get('CheckoutRequestID'),
                        "merchantRequestID": data.get('MerchantRequestID'),
                        "responseDescription": data.get('ResponseDescription'),
                        "customerMessage": data.get('CustomerMessage')
                    }
                else:
                    return {
                        "success": False,
                        "error": data.get('ResponseDescription', 'STK Push failed'),
                        "errorCode": data.get('ResponseCode')
                    }
                    
            except httpx.HTTPStatusError as e:
                # Capture the actual response body for HTTP errors
                error_body = e.response.text if e.response else "No response body"
                logger.error(f"STK Push HTTP error: {e.response.status_code} - {error_body}")
                raise Exception(f"M-Pesa STK Push failed: {e.response.status_code} - {error_body}")
            except httpx.HTTPError as e:
                logger.error(f"STK Push request failed: {str(e)}")
                raise Exception(f"M-Pesa STK Push failed: {str(e)}")
    
    async def query_stk_status(self, checkout_request_id: str) -> Dict[str, Any]:
        """
        Query the status of an STK Push transaction
        
        Args:
            checkout_request_id: The CheckoutRequestID from STK Push response
            
        Returns:
            Dict with transaction status
        """
        access_token = await self.get_access_token()
        
        timestamp = self.generate_timestamp()
        password = self.generate_password(timestamp)
        
        url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
        
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=headers, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"STK Query response: {data}")
                
                # ResultCode 0 means success
                result_code = data.get('ResultCode')
                
                if result_code == '0' or result_code == 0:
                    return {
                        "success": True,
                        "status": "successful",
                        "resultDesc": data.get('ResultDesc'),
                        "merchantRequestID": data.get('MerchantRequestID'),
                        "checkoutRequestID": data.get('CheckoutRequestID')
                    }
                elif result_code == '1032':
                    # Transaction cancelled by user
                    return {
                        "success": False,
                        "status": "cancelled",
                        "resultDesc": "Transaction cancelled by user"
                    }
                elif result_code == '1037':
                    # Transaction timed out
                    return {
                        "success": False,
                        "status": "timeout",
                        "resultDesc": "Transaction timed out"
                    }
                else:
                    return {
                        "success": False,
                        "status": "failed",
                        "resultDesc": data.get('ResultDesc', 'Transaction failed'),
                        "resultCode": result_code
                    }
                    
            except httpx.HTTPError as e:
                logger.error(f"STK Query failed: {str(e)}")
                # Return pending if we can't query - might still be processing
                return {
                    "success": False,
                    "status": "pending",
                    "resultDesc": "Unable to query status"
                }


# Singleton instance
mpesa_service = MpesaService()
