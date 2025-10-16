const JUDGE0_PROXY = "/api/judge0/submit"; // backend proxy

let currentProblem = null;
let candidateId = localStorage.getItem("candidateId") || "1"; // fallback to seeded id

window.onload = () => {
  // populate problem select
  const select = document.getElementById("problemSelect");
  window.codingQuestions.forEach((q, idx) => {
    const opt = document.createElement("option");
    opt.value = idx;
    opt.text = q.title;
    select.appendChild(opt);
  });
  select.addEventListener("change", e => loadProblem(e.target.value));
  loadProblem(0);
};

function loadProblem(idx) {
  currentProblem = window.codingQuestions[idx];
  document.getElementById("problemDescription").innerHTML = `
    <h3>${currentProblem.title}</h3>
    <p>${currentProblem.description}</p>
  `;
}

async function runCode() {
  const source = document.getElementById("sourceCode").value;
  const language_id = document.getElementById("language").value;

  // Run first test case for preview
  const tc = currentProblem.testcases[0];
  const res = await fetch(JUDGE0_PROXY, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source_code: source, language_id, stdin: tc.input })
  });

  const data = await res.json();
  document.getElementById("outputBox").innerHTML = `<pre>${data.stdout || data.stderr || data.compile_output}</pre>`;
}

async function submitCode() {
  const source = document.getElementById("sourceCode").value;
  const language_id = document.getElementById("language").value;

  // grade by running all testcases
  let passed = 0;
  for (const tc of currentProblem.testcases) {
    const res = await fetch(JUDGE0_PROXY, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source_code: source, language_id, stdin: tc.input })
    });
    const data = await res.json();
    if ((data.stdout || "").trim() === tc.expected_output.trim()) passed++;
  }

  const score = Math.round((passed / currentProblem.testcases.length) * 100);
  await fetch(`http://127.0.0.1:5000/submit_coding/${candidateId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ score: score })
  });

  alert(`Your code has been submitted. ${passed}/${currentProblem.testcases.length} testcases passed.`);
}
