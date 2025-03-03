
from decouple import config
from django.core.mail import send_mail


class OTP:
    def send_otp(self,email, otp, name = "User", otp_type="register"):
        project_name = "Smart Home Controller"
        subject = f"{project_name}: Your One-Time Password (OTP) for Verification"

        register_thanks = f"Thank you for signing up with {project_name}!"
        forgot_password_thanks = f"Thank you for using our servise"
        
        message = f"""
        Hi {name},

        {register_thanks if otp_type == "register" else forgot_password_thanks}
        Your one-time password (OTP) is: {otp}

        Please do not share this OTP with anyone. It will expire after 5 minutes for your security.

        If you did not request this, please ignore this email or contact our support team.

        Regards,
        {project_name} Team
        """

        from_email = config('EMAIL_HOST_USER')
        recipient_list = [email]

        try:
            send_mail(subject, message, from_email, recipient_list)
            print("Email sent successfully")
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False