import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr

# Sidebar for prerequisites
with st.sidebar.expander("📝 Prerequisites"):
    st.markdown("""
    To send emails using this application, please keep the following things in mind:

    1. Two-factor authentication of the sender's email should be turned off.
    2. Allow third-party app access:
       - Go to account settings.
       - Select security.
       - Allow third-party/less secure app access.
    """)

# Title of the app
st.title('📧 Cold Email Automation')

# Sidebar for email service selection
st.sidebar.markdown("### 📤 Select Email Service")

# Initialize the session state
if 'hostinger_selected' not in st.session_state:
    st.session_state.hostinger_selected = False
if 'gmail_selected' not in st.session_state:
    st.session_state.gmail_selected = False
if 'show_edit' not in st.session_state:
    st.session_state.show_edit = False  # Default to no expander open
if 'show_preview' not in st.session_state:
    st.session_state.show_preview = False

# Checkbox for Hostinger
if st.sidebar.checkbox('Hostinger', value=st.session_state.hostinger_selected):
    st.session_state.hostinger_selected = True
    st.session_state.gmail_selected = False
else:
    st.session_state.hostinger_selected = False

# Checkbox for Gmail
if st.sidebar.checkbox('Gmail', value=st.session_state.gmail_selected):
    st.session_state.gmail_selected = True
    st.session_state.hostinger_selected = False
else:
    st.session_state.gmail_selected = False

# Show configuration based on the selected service
if st.session_state.hostinger_selected:
    st.sidebar.markdown("### ⚙️ Hostinger Email Configuration")
    smtp_server = st.sidebar.text_input('SMTP Server', value='smtp.hostinger.com')
    smtp_port = st.sidebar.number_input('SMTP Port', value=587, step=1)
elif st.session_state.gmail_selected:
    st.sidebar.markdown("### ⚙️ Gmail Email Configuration")
    smtp_server = st.sidebar.text_input('SMTP Server', value='smtp.gmail.com')
    smtp_port = st.sidebar.number_input('SMTP Port', value=587, step=1)

# Email credentials
email_user = st.text_input('📧 Email Address', value='youremail@example.com')
email_password = st.text_input('🔑 Email Password', type='password')

# Sender's name input
sender_name = st.text_input('🖊️ Your Name', value='Your Name')

# Define email templates
templates = {
    'Pre-existing website 1': """
    Hi {Name},

    Is your website attracting local customers? At {Agency Name}, we optimize your online presence to boost local traffic and engagement.

    Our web solutions help:

    - Enhance local search visibility
    - Maximize user engagement
    - Increase conversions

    We recently increased [Local Business Name]’s traffic by 45% and doubled in-store visits. Interested in boosting your local traffic? Let’s discuss.

    Best,
    {sender_name}
    {Contact}
    """,
    'Pre-existing website 2': """
    Hi {Name},

    Is your website a silent performer or a vibrant profit driver? At {Agency Name}, we transform sites into captivating, efficient platforms. Our clients see up to a 40% boost in conversions with enhanced user experiences and optimal responsiveness. Interested in a redesign? Let's discuss how we can make your site a top performer. Available for a call this week?

    {sender_name}
    {Contact}
    """,
    'WhatsApp chatbot': """
    Hi {Name},

    Imagine a WhatsApp chatbot that doesn’t just respond to customer queries but actively takes orders and convinces customers with personalized, intelligent interactions—day and night. This isn’t just a dream—it’s a reality that {Agency Name} specializes in delivering.

    Why It Matters:

    - Boost Sales: Our bots guide and close deals.
    - 24/7 Presence: Always available for your customers.
    - Seamless Integration: Fits effortlessly into your existing system.

    I’d love to discuss how this could transform {Recipient's Company Name}. Open to a quick call this week?

    Best Regards,
    {sender_name}
    {Agency Name}
    {Contact}
    """,
    'Non-existing website': """
    Hi {Name},

    I noticed your business currently doesn’t have a website. Don’t worry—{Agency Name} can help!

    We specialize in creating high-impact websites that have boosted our clients' sales by up to 80%. Imagine what a professional online presence could do for your business!

    Let’s discuss how we can transform your digital footprint and drive more customers to your door. Are you available for a quick chat or call this week?

    Looking forward to connecting!

    Best regards,
    {sender_name}
    {Agency Name}
    {Contact}
    {url}
    """,
    'Website at low ranks': """
    Hi {Name},

    I noticed your website isn’t ranking as high as it should be—often, it’s buried too low for potential customers to find.

    At {Agency Name}, we can change that! Our expert SEO optimization and targeted ad campaigns are designed to boost your rankings and drive traffic, helping you reach the top of search results and increase sales.

    And it’s not just me saying this—over 400 businesses have seen magnificent growth thanks to our services. Our clients consistently report significant increases in traffic and revenue after partnering with us.

    Let’s discuss how we can get your site where it belongs—at the forefront of your industry. Are you available for a quick chat or call this week?

    Excited to help you succeed!

    Best regards,
    {sender_name}
    {Agency Name}
    {Contact}
    {url}
    """,
    'REEL/SHORT CREATION': """
    Hi {Name},

    I've been following your content, and I see incredible potential to amplify your reach even further! At {Agency Name}, we specialize in creating reels that not only align with the latest trends but also resonate with your audience, driving significant engagement.

    We take care of everything—from content creation and editing to scheduling your reels at peak times to maximize visibility. And it’s not just a promise—over 20 creators have trusted us to grow their presence, and they’ve seen remarkable results.

    Ready to take your reels to the next level? Let’s chat about how we can help you achieve significant growth. Are you available for a quick call this week?

    Looking forward to helping you shine!

    Best regards,
    {sender_name}
    {Agency Name}
    {Contact}
    {url}
    """,
    'HR for interview': """
    Hi {Name},

    Ever wonder what happens when passion meets expertise? That’s exactly what I bring to the table. When I saw the {Job Title} vacancy at {Company Name}, I knew it was the perfect opportunity to combine my skills with your company’s vision.

    In my previous role at {Previous Company Name}, I [mention a specific achievement or responsibility that aligns with the job you're applying for], and I’m eager to bring that same drive and dedication to your team.

    I’ve attached my resume for your review, and I’m excited about the possibility of discussing how I can contribute to {Company Name}. I’m confident that my unique blend of experience and enthusiasm makes me an ideal candidate.

    Thank you for considering my application. I would love to schedule an interview at your earliest convenience.

    Looking forward to the opportunity!

    Best regards,
    {sender_name}
    {Contact}
    {Your LinkedIn Profile URL}
    """,
    'Discount': """
    Hi {Name},

    Hope all is well with you.

    To make things even better, I have something for you—a [{%}] discount on our [Products or services].

    This is an exclusive proposal that's available to a select group of people, and you're among them.

    By taking this unique opportunity, you'll improve your business and reduce your expenses in the process.

    Since what I'm offering is time-limited, hurry up and use your code: [Code]

    Enjoy your day,

    {sender_name}
    """,
    'Pitching yourself': """
    Hi {Name},

    I found your job advert on [website/platform] and it captured my attention because you said you’re looking for a {your profession} on a freelance basis.

    My name is {sender_name} and I’ve worked with numerous companies and individuals over the past {x} years. Some of them are [mention your previous clients and provide the links to your work].

    Not to brag, but they were more than happy with the results of my work, and they’re ready to provide references.

    Here’s the link to my portfolio so that you can check out my other work and see whether it seems like something that you had in mind: [link to portfolio]

    I already have a couple of ideas for your {task/job} and it would be great to share them with you.

    Let me know if you’re interested and pick a time slot in my calendar when it suits you: [link]

    Cheers,

    {sender_name}
    """
}

# Sidebar for template previews (default closed)
with st.sidebar.expander("📄 Template Previews", expanded=False):
    selected_template = st.selectbox('📝 Select Template to Preview', options=list(templates.keys()))
    st.markdown("### Template Preview")
    st.text_area('Preview', value=templates[selected_template], height=300)

# Main content
st.markdown("### Email Content")
template_choice = st.selectbox('Select Email Template', options=list(templates.keys()))

# Subject input
subject = st.text_input('Subject', value='Your Personalized Subject')

# Upload CSV file
uploaded_file = st.file_uploader("📂 Upload CSV file", type=['csv'])

# Upload attachments
uploaded_attachments = st.file_uploader("📎 Upload Attachments", type=['jpg', 'jpeg', 'png', 'pdf', 'docx', 'pptx'], accept_multiple_files=True)

if uploaded_file is not None:
    contacts = pd.read_csv(uploaded_file)
    st.write("Uploaded Contacts:", contacts.head())

# Option to edit the template
if st.checkbox('✏️ Edit Template'):
    st.session_state.show_edit = True
    st.session_state.show_preview = False
    template_content = st.text_area("Template Content", value=templates[template_choice], height=250)

    # Save the edited template back to the templates dictionary
    templates[template_choice] = template_content

# Option to preview the email
if st.checkbox('👁️ Preview Email'):
    st.session_state.show_edit = False
    st.session_state.show_preview = True
    if uploaded_file is not None:
        for i, contact in contacts.iterrows():
            preview = templates[template_choice].format(Name=contact['Name'], sender_name=sender_name)
            st.subheader(f"Preview for {contact['Name']}")
            st.text_area("Preview", value=preview, height=250)
    else:
        preview = templates[template_choice].format(Name="Recipient Name", sender_name=sender_name)
        st.subheader("Preview")
        st.text_area("Preview", value=preview, height=250)

# Send emails button
if st.button('📧 Send Emails'):
    if uploaded_file is not None:
        for i, contact in contacts.iterrows():
            msg = MIMEMultipart()
            msg['From'] = formataddr((sender_name, email_user))
            msg['To'] = contact['Email']
            msg['Subject'] = subject

            # Fill in the template with contact details
            body = templates[template_choice].format(Name=contact['Name'], sender_name=sender_name)
            msg.attach(MIMEText(body, 'plain'))

            # Attach files if any
            if uploaded_attachments:
                for attachment in uploaded_attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename={attachment.name}',
                    )
                    msg.attach(part)

            # Send email
            try:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(email_user, email_password)
                text = msg.as_string()
                server.sendmail(email_user, contact['Email'], text)
                server.quit()
                st.success(f'Email sent to {contact["Name"]} ({contact["Email"]})')
            except Exception as e:
                st.error(f'Failed to send email to {contact["Name"]} ({contact["Email"]}): {str(e)}')
    else:
        st.error('Please upload a CSV file with contacts.')
