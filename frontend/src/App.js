import React, { useState } from "react";
import axios from "axios";
import "./App.css";
import { FaFileUpload, FaBookOpen, FaQuestionCircle } from "react-icons/fa";

function App() {
  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState("");
  const [questions, setQuestions] = useState([]);

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file first!");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      // ✅ Point directly to local backend
      const backendUrl = "http://localhost:5000";
      const res = await axios.post(`${backendUrl}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      setSummary(res.data.summary);
      setQuestions(res.data.questions || []);
    } catch (err) {
      console.error("Upload failed:", err);
      alert("Error connecting to backend. Check if backend is running!");
    }
  };

  return (
    <div className="app-container">
      {/* ✅ Clean Landing Header */}
      <header className="landing">
        <h1 className="title">StudyAssist AI</h1>
        <p className="tagline">
          AI-powered PDF Summaries & Smart Quiz Generation
        </p>
      </header>

      {/* ✅ Modern Upload Section */}
      <div className="upload-box">
        <FaFileUpload className="icon-large" />
        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
          className="file-input"
        />
        <button onClick={handleUpload} className="upload-btn">
          Upload & Process
        </button>
      </div>

      {/* ✅ Result Cards */}
      {summary && (
        <div className="card summary-card">
          <FaBookOpen className="icon-card" />
          <h2>Summary</h2>
          <p>{summary}</p>
        </div>
      )}

      {questions.length > 0 && (
        <div className="card quiz-card">
          <FaQuestionCircle className="icon-card" />
          <h2>Quiz Questions</h2>
          <ul>
            {questions.map((q, i) => (
              <li key={i}>{q}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
