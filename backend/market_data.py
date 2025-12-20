from .smart_auth import SmartAuth
from datetime import datetime, timedelta

class MarketData:
    def __init__(self):
        self.auth = SmartAuth()
        self.login_response = self.auth.login()
        if self.login_response['status']:
            self.smart_api = self.auth.get_instance()
        else:
            print(f"Login Failed: {self.login_response['message']}")
            self.smart_api = None

    def fetch_historical_data(self, symbol_token, exchange="NSE", interval="ONE_DAY", from_date=None, to_date=None):
        """
        Fetch historical candle data.
        Dates should be in format 'YYYY-MM-DD HH:MM'
        """
        if not self.smart_api:
            return None

        # Default to last 30 days if not provided
        if not from_date or not to_date:
            now = datetime.now()
            thirty_days_ago = now - timedelta(days=30)
            to_date = now.strftime("%Y-%m-%d %H:%M")
            from_date = thirty_days_ago.strftime("%Y-%m-%d %H:%M")

        try:
            historicParam = {
                "exchange": exchange,
                "symboltoken": symbol_token,
                "interval": interval,
                "fromdate": from_date,
                "todate": to_date
            }
            return self.smart_api.getCandleData(historicParam)
        except Exception as e:
            print(f"Error fetching candle data: {e}")
            return None
