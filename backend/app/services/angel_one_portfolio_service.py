"""
Angel One Portfolio Service
Syncs real portfolio data from Angel One broker account
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from smart_auth import SmartAuth
from app import models


class AngelOnePortfolioService:
    """Service to sync and manage Angel One portfolio data"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.auth = SmartAuth()
            self.smart_api = None
            self.authenticated = False
            self.cache_duration = 300  # 5 minutes cache
            self.initialized = True
    
    def authenticate(self) -> bool:
        """Authenticate with Angel One API"""
        try:
            login_data = self.auth.login()
            if login_data['status']:
                self.smart_api = self.auth.get_instance()
                self.authenticated = True
                return True
            else:
                print(f"Angel One login failed: {login_data['message']}")
                return False
        except Exception as e:
            print(f"Angel One authentication error: {e}")
            return False
    
    def ensure_authenticated(self) -> bool:
        """Ensure we have valid authentication"""
        if not self.authenticated:
            return self.authenticate()
        return True
    
    def sync_holdings(self, db: Session, user_id: int) -> Dict:
        """
        Fetch holdings from Angel One and cache in database
        Returns: dict with holdings data
        """
        if not self.ensure_authenticated():
            print("[Angel One] Authentication failed for holdings sync")
            return {
                "success": False,
                "error": "Failed to authenticate with Angel One"
            }
        
        try:
            # Call Angel One API
            response = self.smart_api.holding()
            print(f"[Angel One] Holdings API response status: {response.get('status') if response else 'None'}")
            
            if not response or response.get('status') is False:
                error_msg = response.get('message', 'Failed to fetch holdings') if response else 'No response from API'
                print(f"[Angel One] Holdings sync failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
            
            holdings_data = response.get('data', [])
            
            # Clear old holdings for this user
            db.query(models.AngelOneHolding).filter(
                models.AngelOneHolding.user_id == user_id
            ).delete()
            
            # Store new holdings
            holdings_list = []
            for holding in holdings_data:
                holding_obj = models.AngelOneHolding(
                    user_id=user_id,
                    trading_symbol=holding.get('tradingsymbol', ''),
                    exchange=holding.get('exchange', ''),
                    isin=holding.get('isin', ''),
                    quantity=int(holding.get('quantity', 0)),
                    avg_price=float(holding.get('averageprice', 0)),
                    ltp=float(holding.get('ltp', 0)),
                    pnl=float(holding.get('pnl', 0)),
                    synced_at=datetime.utcnow()
                )
                db.add(holding_obj)
                holdings_list.append({
                    'trading_symbol': holding.get('tradingsymbol'),
                    'exchange': holding.get('exchange'),
                    'quantity': int(holding.get('quantity', 0)),
                    'avg_price': float(holding.get('averageprice', 0)),
                    'ltp': float(holding.get('ltp', 0)),
                    'pnl': float(holding.get('pnl', 0)),
                    'current_value': int(holding.get('quantity', 0)) * float(holding.get('ltp', 0)),
                })
            
            db.commit()
            
            return {
                "success": True,
                "data": holdings_list,
                "synced_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            db.rollback()
            print(f"Error syncing holdings: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def sync_positions(self, db: Session, user_id: int) -> Dict:
        """
        Fetch positions from Angel One and cache in database
        Returns: dict with positions data
        """
        if not self.ensure_authenticated():
            print("[Angel One] Authentication failed for positions sync")
            return {
                "success": False,
                "error": "Failed to authenticate with Angel One"
            }
        
        try:
            # Call Angel One API
            response = self.smart_api.position()
            print(f"[Angel One] Positions API response status: {response.get('status') if response else 'None'}")
            
            if not response or response.get('status') is False:
                error_msg = response.get('message', 'Failed to fetch positions') if response else 'No response from API'
                print(f"[Angel One] Positions sync failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
            
            # Handle None data (no positions)
            positions_data = response.get('data')
            if positions_data is None:
                positions_data = []
            
            # Clear old positions for this user
            db.query(models.AngelOnePosition).filter(
                models.AngelOnePosition.user_id == user_id
            ).delete()
            
            # Store new positions
            positions_list = []
            for position in positions_data:
                # Only store positions with non-zero quantity
                net_qty = int(position.get('netqty', 0))
                if net_qty == 0:
                    continue
                
                position_obj = models.AngelOnePosition(
                    user_id=user_id,
                    trading_symbol=position.get('tradingsymbol', ''),
                    exchange=position.get('exchange', ''),
                    product_type=position.get('producttype', ''),
                    quantity=net_qty,
                    avg_price=float(position.get('averageprice', 0)),
                    ltp=float(position.get('ltp', 0)),
                    pnl=float(position.get('pnl', 0)),
                    synced_at=datetime.utcnow()
                )
                db.add(position_obj)
                positions_list.append({
                    'trading_symbol': position.get('tradingsymbol'),
                    'exchange': position.get('exchange'),
                    'product_type': position.get('producttype'),
                    'quantity': net_qty,
                    'avg_price': float(position.get('averageprice', 0)),
                    'ltp': float(position.get('ltp', 0)),
                    'pnl': float(position.get('pnl', 0)),
                })
            
            db.commit()
            
            return {
                "success": True,
                "data": positions_list,
                "synced_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            db.rollback()
            print(f"Error syncing positions: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def sync_funds(self, db: Session, user_id: int) -> Dict:
        """
        Fetch funds/margin from Angel One and cache in database
        Returns: dict with funds data
        """
        if not self.ensure_authenticated():
            print("[Angel One] Authentication failed for funds sync")
            return {
                "success": False,
                "error": "Failed to authenticate with Angel One"
            }
        
        try:
            # Call Angel One API
            response = self.smart_api.rmsLimit()
            print(f"[Angel One] Funds API response status: {response.get('status') if response else 'None'}")
            
            if not response or response.get('status') is False:
                error_msg = response.get('message', 'Failed to fetch funds') if response else 'No response from API'
                print(f"[Angel One] Funds sync failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
            
            funds_data = response.get('data', {})
            
            # Get or create funds record
            funds_obj = db.query(models.AngelOneFunds).filter(
                models.AngelOneFunds.user_id == user_id
            ).first()
            
            if not funds_obj:
                funds_obj = models.AngelOneFunds(user_id=user_id)
                db.add(funds_obj)
            
            # Update funds data
            funds_obj.available_cash = float(funds_data.get('availablecash', 0))
            funds_obj.used_margin = float(funds_data.get('m2munrealized', 0))
            funds_obj.available_margin = float(funds_data.get('availablemargin', 0))
            funds_obj.synced_at = datetime.utcnow()
            
            db.commit()
            db.refresh(funds_obj)
            
            return {
                "success": True,
                "data": {
                    'available_cash': funds_obj.available_cash,
                    'used_margin': funds_obj.used_margin,
                    'available_margin': funds_obj.available_margin,
                },
                "synced_at": funds_obj.synced_at.isoformat()
            }
            
        except Exception as e:
            db.rollback()
            print(f"Error syncing funds: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def sync_all(self, db: Session, user_id: int) -> Dict:
        """
        Sync all portfolio data (holdings, positions, funds)
        Returns: combined dict with all data
        """
        holdings_result = self.sync_holdings(db, user_id)
        positions_result = self.sync_positions(db, user_id)
        funds_result = self.sync_funds(db, user_id)
        
        # Count successful syncs
        success_count = sum([
            holdings_result['success'],
            positions_result['success'],
            funds_result['success']
        ])
        
        # If ALL syncs failed, return error
        if success_count == 0:
            return {
                "success": False,
                "error": "Failed to sync all data. Please check your Angel One credentials and connection.",
                "details": {
                    "holdings": holdings_result,
                    "positions": positions_result,
                    "funds": funds_result
                }
            }
        
        # Partial or full success - return available data
        errors = []
        if not holdings_result['success']:
            errors.append(f"Holdings: {holdings_result.get('error', 'Unknown error')}")
        if not positions_result['success']:
            errors.append(f"Positions: {positions_result.get('error', 'Unknown error')}")
        if not funds_result['success']:
            errors.append(f"Funds: {funds_result.get('error', 'Unknown error')}")
        
        return {
            "success": True,
            "data": {
                "holdings": holdings_result.get('data', []) if holdings_result['success'] else [],
                "positions": positions_result.get('data', []) if positions_result['success'] else [],
                "funds": funds_result.get('data') if funds_result['success'] else None
            },
            "synced_at": datetime.utcnow().isoformat(),
            "partial_errors": errors if errors else None,
            "sync_status": {
                "holdings": holdings_result['success'],
                "positions": positions_result['success'],
                "funds": funds_result['success']
            }
        }
    
    def get_cached_portfolio(self, db: Session, user_id: int) -> Dict:
        """
        Get cached portfolio data from database
        Returns cached data without calling Angel One API
        """
        try:
            # Get holdings
            holdings = db.query(models.AngelOneHolding).filter(
                models.AngelOneHolding.user_id == user_id
            ).all()
            
            holdings_list = [{
                'trading_symbol': h.trading_symbol,
                'exchange': h.exchange,
                'quantity': h.quantity,
                'avg_price': h.avg_price,
                'ltp': h.ltp,
                'pnl': h.pnl,
                'current_value': h.quantity * h.ltp,
            } for h in holdings]
            
            # Get positions
            positions = db.query(models.AngelOnePosition).filter(
                models.AngelOnePosition.user_id == user_id
            ).all()
            
            positions_list = [{
                'trading_symbol': p.trading_symbol,
                'exchange': p.exchange,
                'product_type': p.product_type,
                'quantity': p.quantity,
                'avg_price': p.avg_price,
                'ltp': p.ltp,
                'pnl': p.pnl,
            } for p in positions]
            
            # Get funds
            funds = db.query(models.AngelOneFunds).filter(
                models.AngelOneFunds.user_id == user_id
            ).first()
            
            funds_data = None
            last_sync = None
            
            if funds:
                funds_data = {
                    'available_cash': funds.available_cash,
                    'used_margin': funds.used_margin,
                    'available_margin': funds.available_margin,
                }
                last_sync = funds.synced_at.isoformat()
            elif holdings:
                last_sync = holdings[0].synced_at.isoformat()
            
            return {
                "success": True,
                "data": {
                    "holdings": holdings_list,
                    "positions": positions_list,
                    "funds": funds_data
                },
                "synced_at": last_sync,
                "cached": True
            }
            
        except Exception as e:
            print(f"Error getting cached portfolio: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Global singleton instance
angel_one_portfolio_service = AngelOnePortfolioService()
