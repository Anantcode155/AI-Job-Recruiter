
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_candidate_report_to_hr(candidate_name, candidate_email, report_link):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "anantr683@gmail.com"       # Your Gmail
    sender_password = "vscd agnz zlwi dqrl"   # 16-char Gmail App Password
    hr_email = "anant155.r@gmail.com"         # HR email

    report_url = f"http://localhost:5000/download_report/{os.path.basename(report_link)}"

    subject = f"Candidate Report Available: {candidate_name}"

    body = f"""
    <p>Hello HR Team,</p>
    <p>The following candidate’s report is now available:</p>
    <ul>
        <li><strong>Name:</strong> {candidate_name}</li>
        <li><strong>Email:</strong> {candidate_email}</li>
        <li><strong>Report Link:</strong> <a href="{report_url}">{report_url}</a></li>
    </ul>
    <p>Best regards,<br>AI Recruiter System</p>
    """

    message = MIMEMultipart()
    message["From"] = f"AI Recruiter System <{sender_email}>"
    message["To"] = hr_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
        print(f"✅ Email sent successfully to HR for {candidate_name}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

    
