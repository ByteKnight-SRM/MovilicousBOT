import smtplib
from email.message import EmailMessage
import config
from db_handler import get_movie_details

def send_movie_email(to_email, movie_title):
    """
    Fetch movie details from MongoDB and send via email.
    """
    movie_data = get_movie_details(movie_title)
    if not movie_data:
        print("❌ Movie not found in database.")
        return False

    movie_details = f"""
    🎬 **Title:** {movie_data['Title']}
    📅 **Released:** {movie_data['Released']}
    👥 **Actors:** {movie_data['Actors']}
    🎭 **Plot:** {movie_data['Plot']}
    ⭐ **Metascore:** {movie_data.get('Metascore', 'N/A')}
    """

    msg = EmailMessage()
    msg["Subject"] = f"Movie Details: {movie_data['Title']}"
    msg["From"] = config.EMAIL_ADDRESS
    msg["To"] = to_email
    msg.set_content(movie_details)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"✅ Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False
