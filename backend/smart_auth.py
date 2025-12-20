from SmartApi import SmartConnect
import pyotp
import os
from dotenv import load_dotenv

load_dotenv()

class SmartAuth:
    def __init__(self): 
        self.api_key = os.getenv("ANGEL_API_KEY")
        self.client_id = os.getenv("ANGEL_CLIENT_ID")
        self.password = os.getenv("ANGEL_PASSWORD")
        self.totp_key = os.getenv("ANGEL_TOTP_KEY")
        
        if not all([self.api_key, self.client_id, self.password, self.totp_key]):
            print("Warning: Angel One credentials missing in .env")
            
        self.smart_api = SmartConnect(api_key=self.api_key)
        self.session_data = None

    def login(self):
        try:
            if not self.totp_key:
                return {"status": False, "message": "TOTP Key missing"}
                
            totp = pyotp.TOTP(self.totp_key).now()
            data = self.smart_api.generateSession(self.client_id, self.password, totp)
            
            if data['status']:
                self.session_data = data['data']
                return {
                    "status": True, 
                    "message": "Login Successful", 
                    "auth_token": data['data']['jwtToken'],
                    "feed_token": data['data']['feedToken']
                }
            else:
                return {"status": False, "message": data['message']}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def get_instance(self):
        return self.smart_api
