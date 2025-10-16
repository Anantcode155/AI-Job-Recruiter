// script.js

// Load 20 random aptitude questions from backend
async function loadQuestions() {
  try {
    console.log("Loading questions...");
    const res = await fetch("/get_questions");
    console.log("Response status:", res.status);
    const data = await res.json();
    console.log("Questions data:", data);
    window.questions = data.questions; // [{question:"",options:[],answer:1}, ...]
    window.currentIndex = 0;
    window.answers = [];
    console.log("Questions loaded:", window.questions.length);
    showQuestion();
  } catch (err) {
    console.error("Error fetching questions:", err);
    document.getElementById("question").textContent = "Error loading questions. Please refresh the page.";
  }
}

function showQuestion() {
  const questionBox = document.getElementById("questionBox");
  const progress = document.getElementById("progress");
  const nextBtn = document.getElementById("nextBtn");

  if (window.currentIndex >= window.questions.length) {
    submitAnswers();
    return;
  }

  const q = window.questions[window.currentIndex];

  // Update progress
  progress.textContent = `Question ${window.currentIndex + 1} of ${window.questions.length}`;

  // Update question
  document.getElementById("question").textContent = q.question;

  // Update options
  const optionsContainer = document.getElementById("options");
  let optsHtml = "";
  q.options.forEach((opt, idx) => {
    optsHtml += `
      <div class="option">
        <label>
          <input type="radio" name="answer" value="${idx}"> ${opt}
        </label>
      </div>`;
  });
  optionsContainer.innerHTML = optsHtml;

  // Reset next button
  nextBtn.disabled = true;
  nextBtn.textContent = window.currentIndex === window.questions.length - 1 ? "Submit" : "Next";

  // Add event listeners to radio buttons
  document.querySelectorAll('input[name="answer"]').forEach(radio => {
    radio.addEventListener('change', function() {
      nextBtn.disabled = false;
    });
  });
}

function nextQuestion() {
  // Get selected radio button
  const selected = document.querySelector('input[name="answer"]:checked');
  if (!selected) {
    alert("Please select an option before proceeding.");
    return;
  }

  window.answers.push(parseInt(selected.value));
  window.currentIndex++;
  showQuestion();
}

async function submitAnswers() {
  let score = 0;
  window.questions.forEach((q, idx) => {
    if (window.answers[idx] === q.answer) {
      score++;
    }
  });

  const candidateId = localStorage.getItem("candidate_id");

  try {
    await fetch(`/submit_aptitude/${candidateId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ score: score })
    });

    // Hide question box and show results
    document.getElementById("questionBox").classList.add("hidden");
    document.getElementById("results").classList.remove("hidden");
    document.getElementById("scoreDisplay").textContent = `Your score: ${score} out of ${window.questions.length}`;

    // stop and upload video after test ends
    stopAndUploadVideo();

    // Redirect to next round after 3 seconds
    setTimeout(() => {
      window.location.href = "/next-round";
    }, 3000);

  } catch (error) {
    console.error("Error submitting answers:", error);
    alert("Error submitting answers. Please try again.");
  }
}

// start recording candidate video on test start
async function startRecording() {
  const video = document.getElementById("videoPreview");
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    video.srcObject = stream;

    window.mediaRecorder = new MediaRecorder(stream);
    window.chunks = [];

    window.mediaRecorder.ondataavailable = e => window.chunks.push(e.data);

    // set onstop handler BEFORE calling stop later
    window.mediaRecorder.onstop = async () => {
      const blob = new Blob(window.chunks, { type: 'video/webm' });
      const formData = new FormData();
      formData.append('video', blob, `${localStorage.getItem("candidate_id")}.webm`);
      await fetch(`/upload_video/${localStorage.getItem("candidate_id")}` , {
        method: 'POST',
        body: formData
      });
      console.log("Video uploaded");
    };

    window.mediaRecorder.start();
  } catch (err) {
    alert("Camera permission denied. Test cannot continue.");
  }
}

function stopAndUploadVideo() {
  if (window.mediaRecorder && window.mediaRecorder.state !== "inactive") {
    window.mediaRecorder.stop();
  }
}
// Initialize the test when page loads
document.addEventListener('DOMContentLoaded', function() {
  loadQuestions();
});
