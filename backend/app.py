from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch

app = Flask(__name__)
CORS(app)

# ✅ Use lightweight summarizer
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# ✅ Load smaller question generation model
qg_model = AutoModelForSeq2SeqLM.from_pretrained("valhalla/t5-small-qg-hl")
qg_tokenizer = AutoTokenizer.from_pretrained("valhalla/t5-small-qg-hl")

device = 0 if torch.cuda.is_available() else -1

def generate_questions(text, num_questions=5):
    """
    Generates quiz questions from text using the QG model.
    """
    inputs = qg_tokenizer.encode(
        "generate questions: " + text,
        return_tensors="pt",
        max_length=512,
        truncation=True
    )

    outputs = qg_model.generate(
        inputs,
        max_length=64,
        num_beams=num_questions,  # ✅ beams >= return_sequences
        num_return_sequences=num_questions,
        early_stopping=True
    )

    questions = [qg_tokenizer.decode(out, skip_special_tokens=True) for out in outputs]
    return list(set(questions))  # remove duplicates

@app.route("/upload", methods=["POST"])
def upload_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    if not text.strip():
        return jsonify({"error": "No readable text found in PDF"}), 400

    # ✅ Summarize first ~1000 chars to keep it short
    summary = summarizer(text[:1000], max_length=150, min_length=50, do_sample=False)

    # ✅ Generate quiz questions from same chunk
    questions = generate_questions(text[:500], num_questions=5)

    return jsonify({
        "summary": summary[0]['summary_text'],
        "questions": questions
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
