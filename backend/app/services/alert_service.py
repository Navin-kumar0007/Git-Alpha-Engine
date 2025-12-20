"""
Alert Service - Manages price alerts and notifications
"""

from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session
from app.models import PriceAlert, User
from app.api.websocket import broadcast_alert


class AlertService:
    """Service for managing and checking price alerts"""
    
    @staticmethod
    def create_alert(
        db: Session,
        user_id: int,
        token: str,
        symbol_name: str,
        alert_type: str,
        target_price: float = None,
        percentage: float = None
    ) -> PriceAlert:
        """
        Create a new price alert
        
        Args:
            db: Database session
            user_id: User ID
            token: Angel One token
            symbol_name: Human-readable symbol name
            alert_type: "above", "below", or "percentage_change"
            target_price: Target price for above/below alerts
            percentage: Percentage for percentage_change alerts
            
        Returns:
            Created PriceAlert object
        """
        alert = PriceAlert(
            user_id=user_id,
            token=token,
            symbol_name=symbol_name,
            alert_type=alert_type,
            target_price=target_price,
            percentage=percentage,
            is_active=True
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert
    
    @staticmethod
    def get_user_alerts(db: Session, user_id: int, active_only: bool = True) -> List[PriceAlert]:
        """Get all alerts for a user"""
        query = db.query(PriceAlert).filter(PriceAlert.user_id == user_id)
        if active_only:
            query = query.filter(PriceAlert.is_active == True)
        return query.all()
    
    @staticmethod
    def delete_alert(db: Session, alert_id: int, user_id: int) -> bool:
        """Delete an alert"""
        alert = db.query(PriceAlert).filter(
            PriceAlert.id == alert_id,
            PriceAlert.user_id == user_id
        ).first()
        
        if alert:
            db.delete(alert)
            db.commit()
            return True
        return False
    
    @staticmethod
    def check_tick_for_alerts(db: Session, tick_data: dict):
        """
        Check if a tick triggers any alerts
        
        Args:
            db: Database session
            tick_data: Normalized tick data from Angel One
        """
        token = tick_data.get('token')
        current_price = tick_data.get('last_traded_price_rupees')
        
        if not token or not current_price:
            return
        
        # Get all active alerts for this token
        alerts = db.query(PriceAlert).filter(
            PriceAlert.token == token,
            PriceAlert.is_active == True,
            PriceAlert.is_triggered == False
        ).all()
        
        for alert in alerts:
            triggered = False
            message = ""
            
            if alert.alert_type == "above" and current_price >= alert.target_price:
                triggered = True
                message = f"{alert.symbol_name} is now ₹{current_price:.2f} (above your target of ₹{alert.target_price:.2f})"
            
            elif alert.alert_type == "below" and current_price <= alert.target_price:
                triggered = True
                message = f"{alert.symbol_name} is now ₹{current_price:.2f} (below your target of ₹{alert.target_price:.2f})"
            
            elif alert.alert_type == "percentage_change":
                # TODO: Implement percentage change logic (requires historical baseline)
                pass
            
            if triggered:
                # Mark alert as triggered
                alert.is_triggered = True
                alert.triggered_at = datetime.utcnow()
                db.commit()
                
                # Broadcast alert to user via WebSocket
                import asyncio
                asyncio.create_task(broadcast_alert({
                    "type": "PRICE_ALERT",
                    "alert_id": alert.id,
                    "message": message,
                    "token": token,
                    "symbol_name": alert.symbol_name,
                    "current_price": current_price,
                    "timestamp": datetime.now().isoformat()
                }))
                
                print(f"Alert triggered: {message}")


# Global instance
alert_service = AlertService()
