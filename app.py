from flask import Flask, render_template, request, make_response, jsonify
import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import os
import google.generativeai as genai

app = Flask(__name__)

# Last result ko store karne ke liye
last_result_text = ""

# GEMINI SETUP - NAYA ADD KIYA
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    gemini_model = None

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
    pdf_file = request.files['resume']
    text = extract_text_from_pdf(pdf_file)
    # Tera purana analysis logic yahan rahega - example:
    last_result_text = text[:2000]  # abhi ke liye sample
    return render_template('result.html', result=last_result_text)

# NAYA CHAT AI ROUTE - YE ADD KIYA
@app.route('/chat', methods=['POST'])
def chat():
    if not gemini_model:
        return jsonify({'reply': 'API Key nahi mili! Render me GEMINI_API_KEY check karo'})
    try:
        user_msg = request.json.get('message', '')
        prompt = f"You are SkillScan AI helper for resume and jobs. Reply in Hinglish friendly. User: {user_msg}"
        response = gemini_model.generate_content(prompt)
        return jsonify({'reply': response.text})
    except Exception as e:
        print(f"Chat Error: {e}")
        return jsonify({'reply': 'Thoda error aa gaya, fir se try karo!'})

@app.route('/download')
def download():
    # Tera download wala logic
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, last_result_text[:1000])
    c.save()
    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=result.pdf'
    return response

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)