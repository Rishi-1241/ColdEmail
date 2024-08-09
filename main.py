import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

# Streamlit app
st.title('Cold Email Automation')

# Sidebar for email service selection
email_service = st.sidebar.selectbox('Select Email Service', ['Hostinger', 'Gmail'])

if email_service == 'Hostinger':
    st.sidebar.markdown("### Hostinger Email Configuration")
    smtp_server = st.sidebar.text_input('SMTP Server', value='smtp.hostinger.com')
    smtp_port = st.sidebar.number_input('SMTP Port', value=587, step=1)
elif email_service == 'Gmail':
    st.sidebar.markdown("### Gmail Configuration")
    smtp_server = st.sidebar.text_input('SMTP Server', value='smtp.gmail.com')
    smtp_port = st.sidebar.number_input('SMTP Port', value=587, step=1)

# Email credentials
email_user = st.text_input('Email Address', value='youremail@example.com')
email_password = st.text_input('Email Password', type='password')

# Sender's name input
sender_name = st.text_input('Your Name', value='Your Name')

# Define email templates
templates = {
    'Web Services': """
    Dear {name},

    I hope this email finds you well. We offer top-notch web development services that can help enhance your online presence.

    Our team of experts is ready to assist you in creating a stunning website that meets your needs.

    Best regards,
    {sender_name}
    """,
    'Digital Marketing': """
    Dear {name},

    I hope you're doing well. Our digital marketing services are designed to boost your brand's online visibility and drive more traffic to your website.

    We can help you with SEO, social media marketing, and more.

    Best regards,
    {sender_name}
    """
}

# Template selection
template_choice = st.selectbox('Select Email Template', options=list(templates.keys()))


# Subject input
subject = st.text_input('Subject', value='Your Personalized Subject')

# Upload CSV file
uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])

if uploaded_file is not None:
    contacts = pd.read_csv(uploaded_file)

    # Debugging: Display CSV content
    st.write("CSV Data Preview:")
    st.write(contacts.head())

    # Preview button
    if st.button('Preview Email'):
        # Preview email for the first contact
        if not contacts.empty:
            recipient_name = contacts.iloc[0]['Name']
            preview_body = templates[template_choice].format(name=recipient_name, sender_name=sender_name)
            st.text_area('Preview Email', value=preview_body, height=300, disabled=True)

    if st.button('Send Emails'):
        # Create the SMTP session
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_user, email_password)

            # Send emails
            for index, row in contacts.iterrows():
                recipient_name = row['Name']
                recipient_email = row['Email']

                msg = MIMEMultipart()
                msg['From'] = formataddr((sender_name, email_user))
                msg['To'] = recipient_email
                msg['Subject'] = subject

                body = templates[template_choice].format(name=recipient_name, sender_name=sender_name)
                msg.attach(MIMEText(body, 'plain'))

                server.sendmail(email_user, recipient_email, msg.as_string())
                st.success(f'Email sent to {recipient_name} at {recipient_email}')

            # Quit the server
            server.quit()

        except smtplib.SMTPAuthenticationError as e:
            st.error(f'Authentication error: {e}')
        except Exception as e:
            st.error(f'An error occurred: {e}')
