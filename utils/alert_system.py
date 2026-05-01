import smtplib
import json
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.database import db_manager
import logging

class AlertSystem:
    def __init__(self):
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'email': 'your_email@gmail.com',
            'password': 'your_app_password'
        }
        self.alert_subscribers = ['admin@company.com']
    
    def send_alert(self, alert_type, message, severity='medium', metadata=None):
        """Send alert notification"""
        try:
            # Log alert to database
            self._log_alert(alert_type, message, severity, metadata)
            
            # Send email notification for high/critical alerts
            if severity in ['high', 'critical']:
                self._send_email_alert(alert_type, message, severity)
            
            # Send real-time notification to dashboard
            self._send_realtime_notification(alert_type, message, severity)
            
        except Exception as e:
            logging.error(f"Alert system error: {e}")
    
    def _log_alert(self, alert_type, message, severity, metadata):
        """Log alert to database"""
        try:
            cursor = db_manager.get_postgres_cursor()
            cursor.execute("""
                INSERT INTO system_alerts (alert_type, message, severity)
                VALUES (%s, %s, %s)
            """, (alert_type, message, severity))
            
        except Exception as e:
            logging.error(f"Alert logging error: {e}")
    
    def _send_email_alert(self, alert_type, message, severity):
        """Send email alert notification"""
        try:
            subject = f"🚨 {severity.upper()} Security Alert: {alert_type}"
            
            body = f"""
            Security Alert Detected
            
            Alert Type: {alert_type}
            Severity: {severity.upper()}
            Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            Message: {message}
            
            Please check the security dashboard for more details.
            
            ---
            Cybersecurity Threat Detection System
            """
            
            msg = MIMEMultipart()
            msg['From'] = self.email_config['email']
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            # Send to all subscribers
            for subscriber in self.alert_subscribers:
                msg['To'] = subscriber
                
                with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                    server.starttls()
                    server.login(self.email_config['email'], self.email_config['password'])
                    server.send_message(msg)
            
        except Exception as e:
            logging.error(f"Email alert error: {e}")
    
    def _send_realtime_notification(self, alert_type, message, severity):
        """Send real-time notification to dashboard"""
        # This will be implemented with Socket.IO for real-time updates
        notification_data = {
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store in MongoDB for real-time retrieval
        try:
            mongo_collection = db_manager.get_mongo_collection('real_time_alerts')
            mongo_collection.insert_one(notification_data)
        except Exception as e:
            logging.error(f"Real-time notification error: {e}")

# Global alert system instance
alert_system = AlertSystem()