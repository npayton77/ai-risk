#!/usr/bin/env python3
"""
Email Sender for AI Risk Assessment Reports
Handles sending reports via email with professional formatting
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import List, Optional
from datetime import datetime
import yaml

class EmailSender:
    def __init__(self, config_file: str = 'email_config.yaml'):
        """Initialize email sender with configuration"""
        self.smtp_server = None
        self.smtp_port = 587
        self.smtp_username = None
        self.smtp_password = None
        self.from_email = None
        self.from_name = "AI Risk Assessment Tool"
        
        # Try to load email configuration if file exists
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    email_config = config.get('email', {})
                    
                    self.smtp_server = email_config.get('smtp_server')
                    self.smtp_port = email_config.get('smtp_port', 587)
                    self.smtp_username = email_config.get('smtp_username')
                    self.smtp_password = email_config.get('smtp_password')
                    self.from_email = email_config.get('from_email')
                    self.from_name = email_config.get('from_name', self.from_name)
            except Exception as e:
                print(f"Warning: Could not load email config: {e}")

    def configure_smtp(self, server: str, port: int, username: str, password: str, from_email: str):
        """Configure SMTP settings programmatically"""
        self.smtp_server = server
        self.smtp_port = port
        self.smtp_username = username
        self.smtp_password = password
        self.from_email = from_email

    def send_report(self, 
                   to_emails: List[str], 
                   subject: str,
                   assessment_name: str,
                   risk_level: str,
                   
                   cc_emails: List[str] = None) -> bool:
        """
        Send risk assessment report via email
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject line
            assessment_name: Name of the assessed workflow/system
            risk_level: Risk level (low, medium, high, critical)
            
            cc_emails: List of CC email addresses
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self._is_configured():
            raise Exception("Email not configured. Please set SMTP settings.")
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            
            # Create HTML email body
            html_body = self._create_email_body(assessment_name, risk_level)
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                
                all_recipients = to_emails + (cc_emails if cc_emails else [])
                server.send_message(msg, to_addrs=all_recipients)
            
            return True
            
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False

    def _is_configured(self) -> bool:
        """Check if email is properly configured"""
        return all([
            self.smtp_server,
            self.smtp_username,
            self.smtp_password,
            self.from_email
        ])

    def _create_email_body(self, assessment_name: str, risk_level: str) -> str:
        """Create professional HTML email body"""
        
        risk_colors = {
            'low': '#27ae60',
            'medium': '#f39c12', 
            'high': '#e74c3c',
            'critical': '#8e44ad'
        }
        
        risk_emojis = {
            'low': '[LOW]',
            'medium': '[MED]',
            'high': '[HIGH]',
            'critical': '[CRIT]'
        }
        
        risk_color = risk_colors.get(risk_level, '#f39c12')
        risk_emoji = risk_emojis.get(risk_level, '[MED]')
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI Risk Assessment Report</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); color: white; padding: 30px; text-align: center;">
                    <h1 style="margin: 0; font-size: 24px; font-weight: 300;">AI Risk Assessment Report</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Assessment Complete</p>
                </div>
                
                <!-- Content -->
                <div style="padding: 40px 30px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <div style="background: {risk_color}; color: white; padding: 15px 25px; border-radius: 25px; display: inline-block; font-size: 18px; font-weight: bold; margin-bottom: 15px;">
                            {risk_emoji} {risk_level.upper()} RISK
                        </div>
                        <h2 style="color: #2c3e50; margin: 0; font-size: 20px;">{assessment_name}</h2>
                    </div>
                    
                    <div style="background: #f8f9fa; border-radius: 10px; padding: 25px; margin-bottom: 30px;">
                        <h3 style="color: #2c3e50; margin: 0 0 15px 0; font-size: 18px;">Assessment Summary</h3>
                        <p style="margin: 0; color: #6c757d; line-height: 1.6;">
                            Your AI system "<strong>{assessment_name}</strong>" has been assessed and classified as 
                            <strong style="color: {risk_color};">{risk_level.upper()} RISK</strong>.
                        </p>
                        <p style="margin: 15px 0 0 0; color: #6c757d; line-height: 1.6;">
                            Please review the attached comprehensive report for detailed findings, risk analysis, 
                            and specific recommendations for your AI implementation.
                        </p>
                    </div>
                    
                    <div style="background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); border-radius: 10px; padding: 25px; margin-bottom: 30px;">
                        <h3 style="color: #2c3e50; margin: 0 0 15px 0; font-size: 18px;">Next Steps</h3>
                        <ul style="margin: 0; padding-left: 20px; color: #4a5568; line-height: 1.8;">
                            <li>Review the detailed risk assessment report (attached)</li>
                            <li>Implement the recommended risk mitigation strategies</li>
                            <li>Share findings with relevant stakeholders and decision makers</li>
                            <li>Schedule regular reassessments as your AI system evolves</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; padding: 20px 0;">
                        <p style="margin: 0; color: #6c757d; font-size: 14px;">
                            Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
                        </p>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background: #2c3e50; color: white; padding: 20px; text-align: center;">
                    <p style="margin: 0; font-size: 14px;">
                        <strong>AI Risk Assessment Tool</strong>
                    </p>
                    <p style="margin: 5px 0 0 0; font-size: 12px; opacity: 0.8;">
                        Helping organizations deploy AI responsibly
                    </p>
                </div>
                
            </div>
        </body>
        </html>
        """

    def get_default_config_template(self) -> str:
        """Return a template for email configuration"""
        return """# Email Configuration for AI Risk Assessment Tool
# Copy this to email_config.yaml and fill in your SMTP details

email:
  smtp_server: "smtp.gmail.com"          # Gmail SMTP server
  smtp_port: 587                         # Standard SMTP port
  smtp_username: "your-email@gmail.com"  # Your email address
  smtp_password: "your-app-password"     # Your app-specific password
  from_email: "your-email@gmail.com"     # From address
  from_name: "AI Risk Assessment Tool"   # Display name

# For Gmail:
# 1. Enable 2FA on your Google account
# 2. Generate an app-specific password
# 3. Use that password (not your regular password)

# For other providers:
# - Outlook: smtp.office365.com:587
# - Yahoo: smtp.mail.yahoo.com:587
# - Custom SMTP: Use your provider's settings
""" 