"""
Email Sender Utility

This module handles sending emails with invoice attachments using SMTP.
"""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Optional

from src.models.models import BusinessSettings, Invoice


class EmailSender:
    def __init__(self, business_settings: BusinessSettings):
        self.business_settings = business_settings

    def send_invoice_email(
        self,
        invoice: Invoice,
        pdf_path: str,
        recipient_email: str = None,
        custom_subject: str = None,
        custom_message: str = None
    ) -> bool:
        """
        Send invoice email with PDF attachment

        Args:
            invoice: Invoice object
            pdf_path: Path to the PDF file
            recipient_email: Email address (uses customer email if not provided)
            custom_subject: Custom email subject
            custom_message: Custom email message

        Returns:
            bool: True if email was sent successfully
        """
        try:
            # Validate email settings
            if not self._validate_email_settings():
                raise ValueError("Email settings are not properly configured")

            # Determine recipient
            to_email = recipient_email or invoice.customer_email
            if not to_email:
                raise ValueError("No recipient email address provided")

            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.business_settings.smtp_username
            msg['To'] = to_email
            msg['Subject'] = custom_subject or self._generate_default_subject(invoice)

            # Email body
            body = custom_message or self._generate_default_message(invoice)
            msg.attach(MIMEText(body, 'plain'))

            # Attach PDF
            if Path(pdf_path).exists():
                with open(pdf_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())

                encoders.encode_base64(part)
                filename = Path(pdf_path).name
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {filename}'
                )
                msg.attach(part)
            else:
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")

            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.business_settings.smtp_server, self.business_settings.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.business_settings.smtp_username, self.business_settings.smtp_password)
                text = msg.as_string()
                server.sendmail(self.business_settings.smtp_username, to_email, text)

            return True

        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False

    def _validate_email_settings(self) -> bool:
        """Validate that email settings are configured"""
        required_fields = [
            self.business_settings.smtp_server,
            self.business_settings.smtp_username,
            self.business_settings.smtp_password
        ]
        return all(field for field in required_fields)

    def _generate_default_subject(self, invoice: Invoice) -> str:
        """Generate default email subject"""
        return f"Invoice {invoice.invoice_number} from {self.business_settings.business_name}"

    def _generate_default_message(self, invoice: Invoice) -> str:
        """Generate default email message"""
        currency = self.business_settings.currency_symbol
        return f"""Dear {invoice.customer_name},

Thank you for your business! Please find attached invoice {invoice.invoice_number} for your recent purchase.

Invoice Details:
- Invoice Number: {invoice.invoice_number}
- Invoice Date: {invoice.date}
- Due Date: {invoice.due_date}
- Amount: {currency}{invoice.grand_total:,.2f}

Please remit payment by the due date. If you have any questions regarding this invoice, please don't hesitate to contact us.

Thank you for choosing {self.business_settings.business_name}!

Best regards,
{self.business_settings.business_name}
{self.business_settings.business_email}
{self.business_settings.business_phone}
"""

    def send_test_email(self, test_email: str) -> bool:
        """
        Send a test email to verify email configuration

        Args:
            test_email: Email address to send test to

        Returns:
            bool: True if test email was sent successfully
        """
        try:
            if not self._validate_email_settings():
                return False

            msg = MIMEMultipart()
            msg['From'] = self.business_settings.smtp_username
            msg['To'] = test_email
            msg['Subject'] = f"Test Email from {self.business_settings.business_name}"

            body = f"""This is a test email from {self.business_settings.business_name}.

If you received this email, your email configuration is working correctly!

Business Details:
- Name: {self.business_settings.business_name}
- Email: {self.business_settings.business_email}
- Phone: {self.business_settings.business_phone}

Test sent at: {invoice.created_at if 'invoice' in locals() else 'now'}
"""

            msg.attach(MIMEText(body, 'plain'))

            context = ssl.create_default_context()
            with smtplib.SMTP(self.business_settings.smtp_server, self.business_settings.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.business_settings.smtp_username, self.business_settings.smtp_password)
                text = msg.as_string()
                server.sendmail(self.business_settings.smtp_username, test_email, text)

            return True

        except Exception as e:
            print(f"Failed to send test email: {str(e)}")
            return False