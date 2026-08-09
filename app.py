from flask import Flask, render_template, request, make_response
import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

app = Flask(__name__)

# Last result ko store karne ke liye
last_result_text = ""

def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    global last_result_text
    pdf = request.files['resume']
    resume_text = extract_text_from_pdf(pdf)
    
    score = 70
    if "python" in resume_text.lower(): score += 10
    if "project" in resume_text.lower(): score += 10
    if len(resume_text) > 500: score += 5
    if score > 95: score = 95
    
    last_result_text = f"""ATS Score: {score}/100
Resume Length: {len(resume_text)} characters
Found Skills: Python, Flask, MS Office, Technical Support

Suggestions:
1. Add more Projects section
2. Add GitHub link
3. Use strong action verbs

Resume Preview:
{resume_text[:2000]}"""

    return render_template('result.html', result=last_result_text, score=score)

@app.route('/download_report')
def download_report():
    global last_result_text
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 750, "SkillScan AI - Resume Analysis Report")
    p.setFont("Helvetica", 10)
    
    # Text ko line by line likhna
    y = 720
    for line in last_result_text.split('\n'):
        p.drawString(50, y, line[:110])
        y -= 15
        if y < 50:
            p.showPage()
            y = 750
            
    p.save()
    buffer.seek(0)
    
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=SkillScan_Report.pdf'
    return response

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)