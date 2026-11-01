// Ghost Auditor — frontend wiring (presentation only, no matching logic).
//
// Flow: Summon -> POST /upload (files or sample data) -> POST /audit ->
// render the dossier exceptions with their evidence chains, show the
// ghost narration, and enable the Markdown export download.

let currentRunId = null;

function setCrewProgress(state) {
  for (const li of document.querySelectorAll("#crew-progress li")) {
    const agent = li.dataset.agent;
    li.textContent = `${capitalize(agent)} — ${state[agent] || "waiting"}`;
  }
}

function capitalize(word) {
  return word.charAt(0).toUpperCase() + word.slice(1);
}

function money(cents) {
  return `$${(cents / 100).toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

function renderException(exc) {
  const details = exc.details;
  let what = "";
  if (exc.type === "quantity_mismatch") {
    what = `Ordered qty ${details.ordered_qty}, invoiced qty ${details.invoiced_qty} (invoice ${details.invoice_id}).`;
  } else if (exc.type === "price_difference") {
    what = `Ordered unit price ${money(details.ordered_unit_price_cents)}, invoiced unit price ${money(details.invoiced_unit_price_cents)} (invoice ${details.invoice_id}).`;
  } else if (exc.type === "missing_invoice") {
    what = `No invoice found for this order; order total ${money(details.order_total_cents)}.`;
  } else if (exc.type === "duplicate_payment") {
    what = `Paid invoices: ${details.paid_invoice_ids.join(", ")}; extra amount paid more than once: ${money(details.extra_paid_cents)}.`;
  }
  const ev = exc.evidence;
  const order = ev.order;
  let evidenceHtml = `<li>Order line (orders file, row ${order.row}): ${order.order_id}, ${order.supplier}, ${order.item}, qty ${order.quantity}, unit price ${money(order.unit_price_cents)}, total ${money(order.amount_cents)}.</li>`;
  for (const inv of ev.invoices) {
    evidenceHtml += `<li>Invoice line (invoices file, row ${inv.row}): ${inv.invoice_id}, qty ${inv.quantity}, unit price ${money(inv.unit_price_cents)}, total ${money(inv.amount_cents)}, status ${inv.payment_status}.</li>`;
  }
  if (ev.portal) {
    const p = ev.portal;
    evidenceHtml += `<li>Portal value (mock portal, row ${p.row}): qty received ${p.qty_received}, amount ${money(p.amount_cents)}, status ${p.payment_status}.</li>`;
  } else {
    evidenceHtml += `<li>Portal value: not captured.</li>`;
  }
  return `<article class="exception">
    <h3>${exc.type} — ${exc.order_id} <span class="severity">${exc.severity}</span></h3>
    <p>${what}</p>
    <details open><summary>Evidence chain</summary><ul>${evidenceHtml}</ul></details>
  </article>`;
}

function renderDossier(dossier) {
  const list = document.getElementById("dossier-list");
  const summary = dossier.summary;
  let html = `<p><strong>Orders audited:</strong> ${summary.total_orders} · ` +
    `<strong>Matched:</strong> ${summary.matched_count} · ` +
    `<strong>Exceptions:</strong> ${summary.exception_count}</p>`;
  if (dossier.exceptions.length === 0) {
    html += `<p>No exceptions. Every order reconciled.</p>`;
  } else {
    html += dossier.exceptions.map(renderException).join("");
  }
  list.innerHTML = html;
  document.getElementById("ghost-narration").textContent = dossier.narration;
  document.getElementById("export-btn").disabled = false;
}

async function checkHealth() {
  const statusEl = document.getElementById("api-status");
  try {
    const res = await fetch("/health");
    const data = await res.json();
    statusEl.textContent =
      data.status === "ok" ? "API is alive." : "API responded unexpectedly.";
  } catch (err) {
    statusEl.textContent = "API unreachable. Is the server running?";
  }
}

async function onSummon() {
  const btn = document.getElementById("summon-btn");
  const list = document.getElementById("dossier-list");
  btn.disabled = true;
  document.getElementById("export-btn").disabled = true;
  document.getElementById("ghost-narration").textContent = "";
  list.innerHTML = "<p class='placeholder'>The ghost is at work…</p>";
  setCrewProgress({
    capture: "working",
    normalize: "queued",
    match: "queued",
    explain: "queued",
  });
  try {
    const form = new FormData();
    const ordersFile = document.getElementById("orders-file").files[0];
    const invoicesFile = document.getElementById("invoices-file").files[0];
    if (ordersFile) form.append("orders_file", ordersFile);
    if (invoicesFile) form.append("invoices_file", invoicesFile);

    const upRes = await fetch("/upload", { method: "POST", body: form });
    const up = await upRes.json();
    if (!upRes.ok) throw new Error(up.detail || "upload failed");
    currentRunId = up.run_id;

    const auditRes = await fetch("/audit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ run_id: currentRunId }),
    });
    const dossier = await auditRes.json();
    if (!auditRes.ok) throw new Error(dossier.detail || "audit failed");

    setCrewProgress({
      capture: "done",
      normalize: "done",
      match: "done",
      explain: "done",
    });
    document.getElementById("api-status").textContent =
      `Audit complete (run ${currentRunId}). Portal: ${dossier.portal_status}.`;
    renderDossier(dossier);
  } catch (err) {
    list.innerHTML = `<p class='placeholder'>Audit failed: ${err.message}</p>`;
    setCrewProgress({
      capture: "waiting",
      normalize: "waiting",
      match: "waiting",
      explain: "waiting",
    });
  } finally {
    btn.disabled = false;
  }
}

function onExport() {
  if (!currentRunId) return;
  const a = document.createElement("a");
  a.href = `/report/${currentRunId}`;
  a.download = `ghost-auditor-report-${currentRunId}.md`;
  document.body.appendChild(a);
  a.click();
  a.remove();
}

document.addEventListener("DOMContentLoaded", () => {
  checkHealth();
  document.getElementById("summon-btn").addEventListener("click", onSummon);
  document.getElementById("export-btn").addEventListener("click", onExport);
});
