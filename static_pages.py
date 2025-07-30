#!/usr/bin/env python3
"""
Static Page Handlers for AI Risk Assessment Tool
Contains HTML content and handlers for informational pages
"""

def generate_system_info_page() -> str:
    """Generate the system information page HTML"""
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>System Information - AI Risk Assessment Tool</title>
        <link rel="icon" type="image/svg+xml" href="/favicon.ico">
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 20px; min-height: 100vh; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 15px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
            h1 {{ color: #2c3e50; text-align: center; margin-bottom: 30px; }}
            .status-box {{ background: #f8f9fa; border-radius: 10px; padding: 20px; margin: 20px 0; }}
            .status-good {{ border-left: 4px solid #27ae60; background: #d4edda; }}
            .status-warning {{ border-left: 4px solid #ffc107; background: #fff3cd; }}
            pre {{ background: #2c3e50; color: #ecf0f1; padding: 20px; border-radius: 8px; overflow-x: auto; font-size: 14px; }}
            .btn {{ background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); color: white; padding: 12px 25px; border: none; border-radius: 25px; cursor: pointer; font-weight: bold; text-decoration: none; display: inline-block; margin: 10px; }}
            .feature-list {{ list-style: none; padding: 0; }}
            .feature-item {{ padding: 10px; margin: 5px 0; border-radius: 8px; display: flex; align-items: center; gap: 10px; }}
            .feature-enabled {{ background: #d4edda; color: #155724; }}
            .feature-fallback {{ background: #fff3cd; color: #856404; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔧 System Information</h1>
            
            <div class="status-box status-good">
                <h3>Application Features</h3>
                <ul class="feature-list">
                    <li class="feature-item feature-enabled">
                        ✅ HTML Report Generation: Enabled
                    </li>
                    <li class="feature-item feature-enabled">
                        ✅ Email Functionality: Enabled (uses default mail client)
                    </li>
                    <li class="feature-item feature-enabled">
                        ✅ Risk Assessment: Enabled
                    </li>
                </ul>
            </div>
            
            <div class="status-box">
                <h3>Current Features</h3>
                <p><strong>✨ Available Now:</strong></p>
                <ul>
                    <li>📊 Comprehensive AI Risk Assessment</li>
                    <li>🎨 Beautiful HTML Reports</li>
                    <li>📧 Email Report Delivery</li>
                    <li>📄 HTML Download (Use browser's "Print to PDF" for PDF)</li>
                    <li>🔄 Dynamic YAML Configuration</li>
                    <li>📱 Mobile-Responsive Design</li>
                    <li>🧭 Multi-Step Wizard Interface</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="/" class="btn">🔄 Back to Assessment Tool</a>
                <a href="/email_info" class="btn">📧 Email Info</a>
            </div>
        </div>
    </body>
    </html>
    '''

def generate_email_info_page() -> str:
    """Generate the email information page HTML"""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email Functionality - AI Risk Assessment Tool</title>
        <link rel="icon" type="image/svg+xml" href="/favicon.ico">
        <style>
            body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 20px; min-height: 100vh; }
            .container { max-width: 800px; margin: 0 auto; background: white; border-radius: 15px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
            h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
            .info-box { background: #f8f9fa; border-radius: 10px; padding: 20px; margin: 20px 0; }
            .success-box { border-left: 4px solid #27ae60; background: #d4edda; }
            .btn { background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); color: white; padding: 12px 25px; border: none; border-radius: 25px; cursor: pointer; font-weight: bold; text-decoration: none; display: inline-block; margin: 10px; }
            .feature-list { list-style: none; padding: 0; }
            .feature-item { padding: 10px; margin: 5px 0; border-radius: 8px; display: flex; align-items: center; gap: 10px; background: #e8f5e8; color: #2d5a2d; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📧 Email Functionality</h1>
            
            <div class="info-box success-box">
                <h3>✅ Simple & User-Friendly Email</h3>
                <p>Our email functionality uses your default mail client - <strong>no complex setup required!</strong></p>
                <p>When you click "📧 Email Report", it will:</p>
                <ul class="feature-list">
                    <li class="feature-item">✅ Open your default mail app (Outlook, Mail, Gmail, etc.)</li>
                    <li class="feature-item">✅ Pre-fill the subject with the assessment name</li>
                    <li class="feature-item">✅ Include a professional email body with key findings</li>
                    <li class="feature-item">✅ Provide links to view and download the report</li>
                </ul>
            </div>
            
            <div class="info-box">
                <h3>How It Works</h3>
                <p><strong>1. Generate your risk assessment report</strong></p>
                <p><strong>2. Click "📧 Email Report"</strong> - your mail client opens automatically</p>
                <p><strong>3. Add recipient email addresses</strong> and send!</p>
                
                <p><strong>What's included in the email:</strong></p>
                <ul>
                    <li>📊 Assessment summary (risk level, score, assessor)</li>
                    <li>🔗 Direct link to view the report online</li>
                    <li>📄 Link to download the report file</li>
                    <li>📋 Top 3 key recommendations</li>
                    <li>✉️ Professional formatting</li>
                </ul>
            </div>
            
            <div class="info-box">
                <h3>🎯 Benefits</h3>
                <ul>
                    <li><strong>Zero Configuration:</strong> Works with any email client</li>
                    <li><strong>Privacy First:</strong> No credentials or SMTP setup needed</li>
                    <li><strong>Universal Compatibility:</strong> Works on all operating systems</li>
                    <li><strong>Professional Output:</strong> Formatted, ready-to-send emails</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="/" class="btn">🔄 Back to Assessment Tool</a>
            </div>
        </div>
    </body>
    </html>
    ''' 