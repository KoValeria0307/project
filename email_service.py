from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import smtplib

def send_email_with_pdf(subject, body, to_emails, pdf_path, from_email, smtp_config, job_id, base_url=None):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = ', '.join(to_emails)
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #006633;">Новая вакансия требует проверки</h2>
                    <p>{body}</p>
                    
                    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p style="margin: 0;">Подробности вакансии доступны в прикрепленном PDF-файле.</p>
                    </div>
                    
                    <p>Пожалуйста, выберите действие:</p>
                    
                    <div style="margin: 25px 0;">
                        <form action="{base_url}/approve/{job_id}" method="POST" style="display: inline-block; margin-right: 10px;">
                            <button type="submit" style="background-color: #4CAF50; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px;">
                                ✓ Одобрить и опубликовать
                            </button>
                        </form>
                        <form action="{base_url}/reject/{job_id}" method="POST" style="display: inline-block;">
                            <button type="submit" style="background-color: #f44336; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px;">
                                ✗ Отклонить вакансию
                            </button>
                        </form>
                    </div>
                    
                    <p style="font-size: 12px; color: #777;">
                        Это автоматическое сообщение. Пожалуйста, не отвечайте на него.
                    </p>
                </div>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        with open(pdf_path, 'rb') as f:
            attach = MIMEApplication(f.read(), _subtype="pdf")
            attach.add_header('Content-Disposition', 'attachment', filename='vacancy.pdf')
            msg.attach(attach)
        
        with smtplib.SMTP(smtp_config['host'], smtp_config['port']) as server:
            server.starttls()
            server.login(smtp_config['user'], smtp_config['password'])
            server.send_message(msg)
        
        return True
    except Exception as e:
        logging.error(f"Ошибка отправки email: {str(e)}")
        return False