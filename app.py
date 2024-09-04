from flask import Flask, render_template, request, send_file
from PyPDF2 import PdfReader, PdfWriter
import io
import tempfile
import html
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

app = Flask(__name__)

def fill_pdf(template_path, form_data):
    reader = PdfReader(template_path)
    writer = PdfWriter()

    # Copy pages from the template to the writer
    for page in reader.pages:
        writer.add_page(page)

    # Update form fields
    for field in writer.get_form_text_fields():
        if field in form_data:
            writer.update_page_form_field_values(page, {field: form_data[field]})

    # Create a temporary PDF file
    temp_pdf_path = tempfile.mktemp(suffix=".pdf")
    with open(temp_pdf_path, "wb") as f:
        writer.write(f)

    return temp_pdf_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    try:
        # Sanitize user input
        form_data = {
            key: html.escape(request.form[key])
            for key in request.form
        }

        # Path to the pre-generated PDF template
        template_path = 'template.pdf'

        # Fill in the PDF template
        pdf_path = fill_pdf(template_path, form_data)

        # Send the PDF via email
        send_email_with_attachment(pdf_path, request.form.get('recipient_email'))

        # Return the PDF for download
        return send_file(pdf_path, as_attachment=True, download_name='filled_form.pdf')

    except Exception as e:
        # Log the exception for debugging
        app.logger.error(f"An error occurred: {str(e)}")
        return f"An error occurred: {str(e)}"

def send_email_with_attachment(pdf_path, recipient_email):
    # Email credentials
    sender_email = 'prescricoesineb@gmail.com'
    sender_password = 'affr ebla htup lznh'
    subject = 'Aqui está a prescrição!'
    body = 'PDF anexado abaixo.'

    # Create email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    # Attach PDF file
    with open(pdf_path, 'rb') as attachment:
        part = MIMEApplication(attachment.read(), _subtype="pdf")
        part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(pdf_path))
        msg.attach(part)

    # Send email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())

if __name__ == '__main__':
    app.run(debug=True)
