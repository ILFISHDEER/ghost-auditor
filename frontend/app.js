// Ghost Auditor — frontend skeleton.
//
// Wired so far: a /health check on page load, and the Summon button
// reports that the backend endpoints are still stubs. Dossier rendering,
// upload, audit, and export wiring are TODOs, completed as the backend
// endpoints land (see .kiro/specs/ghost-auditor/tasks.md).

async function checkHealth() {
  const statusEl = document.getElementById("api-status");
  try {
    const res = await fetch("/health");
    const data = await res.json();
    statusEl.textContent =
      data.status === "ok"
        ? "API is alive. Backend endpoints are still stubs."
        : "API responded unexpectedly.";
  } catch (err) {
    statusEl.textContent = "API unreachable. Is the server running?";
  }
}

function onSummon() {
  // TODO: POST uploads to /upload, then POST /audit, then render the
  // dossier into #dossier-list and the narration into #ghost-narration.
  const list = document.getElementById("dossier-list");
  list.innerHTML =
    "<p class='placeholder'>Audit not implemented yet — the backend " +
    "endpoints are stubs. See backend/main.py.</p>";
}

document.addEventListener("DOMContentLoaded", () => {
  checkHealth();
  document.getElementById("summon-btn").addEventListener("click", onSummon);
});
