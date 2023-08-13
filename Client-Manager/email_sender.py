import ssl
import json
import smtplib
import sqlite3
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


conn1 = sqlite3.connect('db.sqlite3')
conn2 = sqlite3.connect('x-ui.db')

new_accounts = []
cursor = conn1.cursor()
cursor.execute('SELECT name, email FROM UserPanel_customer WHERE verified=1')
for name, email in cursor.fetchall():
    cursor = conn2.cursor()
    cursor.execute(f'SELECT * FROM inbounds WHERE remark="{name}"')
    result = cursor.fetchone()
    if result and email != 'provided during registration':
        new_accounts.append((name, email, result))
	
if not new_accounts:
	exit(0)

smtp_server = 'smtp.gmail.com'
smtp_port = 465
sender_email = 'gameguard.contact@gmail.com'
sender_password = 'gykmoofciuceddza'

new_account_message = """\
<html>
    <body>
        <p>Dear <strong>%s</strong>,</p>
        <p>
            Thank you for choosing GameGuard as your VPN provider!
            We appreciate your business and hope you have a great experience using our service.
        </p>
        <p>
            We are pleased to inform you that your VPN plan purchase has been successfully processed and your account details are now ready for use.
            Please find your account information below:
        </p>
        <p>
            <strong>Link:</strong> %s
        </p>
        <p>
            Please keep this information safe as it will be required to access your VPN account.
            If you have any issues with logging in or have any questions about our service, please do not hesitate to contact our support team.
        </p>
        <p>
            We would also like to remind you that our VPN plans support multiple devices, with separate data and usernames.
            This means that you can share your plan with friends or family members by simply providing us with their desired usernames.
            We'll create additional accounts for them under your plan, so they can enjoy the benefits of GameGuard VPN as well.
            You just need to reply to this email and send us the usernames that you want to add with desired limitations (if needed).
        </p>
        <p>
            Thank you for choosing GameGuard as your VPN provider.
            We look forward to serving you in the future.
        </p>
        <p>
            Best regards,<br>
            The GameGuard Team
        </p>
    </body>
</html>
"""

context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
    server.login(sender_email, sender_password)
    
    for name, email, data in new_accounts:
        port = data[12]
        id = json.loads(data[14])['clients'][0]['id']
        server_name = json.loads(data[15])['tlsSettings']['serverName']
        link = f"vless://{id}@{server_name}:{port}?type=ws&security=tls&path=%2F&sni={server_name}&fp=chrome#{name.split(' - ')[0].replace(' ', '')}"

        message = MIMEMultipart('alternative')
        message['From'] = 'GameGuard Support'
        message['To'] = email
        message['Subject'] = 'Welcome to GameGuard VPN | Your Account Details Inside!'
        message.attach(MIMEText(new_account_message % (name.replace(' - ', ' '), link), 'html'))
        server.sendmail(sender_email, email, message.as_string())

        cursor = conn1.cursor()
        cursor.execute(f'DELETE FROM UserPanel_customer WHERE name="{name}"')
        conn1.commit()
