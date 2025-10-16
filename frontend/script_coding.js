const JUDGE0_PROXY = "https://judge0-ce.p.rapidapi.com/submissions"; // Judge0 API
const JUDGE0_API_KEY = "YOUR_RAPIDAPI_KEY"; // You'll need to get this from RapidAPI

let currentProblem = null;
let candidateId = localStorage.getItem("candidate_id");
let codingQuestions = [];

// Load coding questions from our backend
async function loadCodingQuestions() {
  try {
    const response = await fetch('/get_coding_questions');
    const data = await response.json();
    codingQuestions = data.questions;
    
    // Populate problem select
    const select = document.getElementById("problemSelect");
    codingQuestions.forEach((q, idx) => {
      const opt = document.createElement("option");
      opt.value = idx;
      opt.text = q.title;
      select.appendChild(opt);
    });
    select.addEventListener("change", e => loadProblem(e.target.value));
    loadProblem(0);
    
    // Show interface
    document.getElementById("loadingMessage").style.display = "none";
    document.getElementById("codingInterface").style.display = "block";
  } catch (error) {
    console.error("Error loading coding questions:", error);
    document.getElementById("loadingMessage").innerHTML = "<h3>Error loading questions. Please refresh the page.</h3>";
  }
}

window.onload = () => {
  if (!candidateId) {
    alert("Candidate details not found. Please start from the beginning.");
    window.location.href = "/";
    return;
  }
  loadCodingQuestions();
};

function loadProblem(idx) {
  currentProblem = codingQuestions[idx];
  document.getElementById("problemDescription").innerHTML = `
    <h3>${currentProblem.title}</h3>
    <p>${currentProblem.description}</p>
    <h4>Test Cases:</h4>
    <ul>
      ${currentProblem.testcases.map((tc, i) => `
        <li>
          <strong>Test Case ${i + 1}:</strong><br>
          Input: <code>${tc.input}</code><br>
          Expected Output: <code>${tc.expected_output}</code>
        </li>
      `).join('')}
    </ul>
  `;
}

async function runCode() {
  const source = document.getElementById("sourceCode").value;
  const language_id = document.getElementById("language").value;

  if (!source.trim()) {
    document.getElementById("outputBox").innerHTML = "Please write some code first!";
    return;
  }

  document.getElementById("outputBox").innerHTML = "Running code... Please wait...";

  try {
    // For now, we'll simulate code execution since Judge0 requires API key
    // In a real implementation, you'd use Judge0 API here
    const tc = currentProblem.testcases[0];
    
    // Simulate execution delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Mock response for demonstration
    document.getElementById("outputBox").innerHTML = `
      <strong>Test Case 1 Result:</strong><br>
      Input: ${tc.input}<br>
      Expected: ${tc.expected_output}<br>
      <em>Note: This is a demo. In production, this would run your actual code.</em>
    `;
  } catch (error) {
    document.getElementById("outputBox").innerHTML = `Error: ${error.message}`;
  }
}

async function submitCode() {
  const source = document.getElementById("sourceCode").value;
  const language_id = document.getElementById("language").value;

  if (!source.trim()) {
    alert("Please write some code before submitting!");
    return;
  }

  if (!candidateId) {
    alert("Candidate details not found. Please start from the beginning.");
    window.location.href = "/";
    return;
  }

  // Show loading
  document.getElementById("outputBox").innerHTML = "Submitting your solution... Please wait...";

  try {
    // For demo purposes, we'll simulate grading
    // In production, this would run actual code execution
    let passed = 0;
    const totalTests = currentProblem.testcases.length;
    
    // Simulate test execution
    for (let i = 0; i < totalTests; i++) {
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate execution time
      // For demo, we'll give a random score between 60-100
      if (Math.random() > 0.3) passed++;
    }

    const score = Math.round((passed / totalTests) * 100);
    
    // Submit to our backend
    const response = await fetch(`/submit_coding/${candidateId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ score: score })
    });

    if (response.ok) {
      const result = await response.json();
      document.getElementById("outputBox").innerHTML = `
        <div style="background: rgba(46, 204, 113, 0.2); padding: 15px; border-radius: 8px; border: 2px solid #2ecc71;">
          <h3>✅ Solution Submitted Successfully!</h3>
          <p><strong>Score:</strong> ${score}% (${passed}/${totalTests} test cases passed)</p>
          <p><strong>Status:</strong> ${result.message}</p>
        </div>
      `;
      
      // Show success message and redirect after delay
      setTimeout(() => {
        alert(`Coding round completed! Your score: ${score}%`);
        window.location.href = "/next-round";
      }, 3000);
    } else {
      throw new Error("Failed to submit coding solution");
    }
  } catch (error) {
    console.error("Error submitting code:", error);
    document.getElementById("outputBox").innerHTML = `
      <div style="background: rgba(231, 76, 60, 0.2); padding: 15px; border-radius: 8px; border: 2px solid #e74c3c;">
        <h3>❌ Submission Failed</h3>
        <p>Error: ${error.message}</p>
        <p>Please try again.</p>
      </div>
    `;
  }
}
