const API_BASE = "";

const $ = (id) => document.getElementById(id);

const cvFile = $("cvFile");
const jdText = $("jdText");

const cvToast = $("cvToast");
const jdToast = $("jdToast");
const cvBadge = $("cvBadge");
const jdBadge = $("jdBadge");

const analysisMeta = $("analysisMeta");
const analysisOut = $("analysisOut");     // kept hidden, but useful for debugging
const analysisNice = $("analysisNice");

const historyList = $("historyList");

const chatOut = $("chatOut");
const chatInput = $("chatInput");
const chatHint = $("chatHint");

const backendStatus = $("backendStatus");

function setBadge(el, text, kind=""){
  el.textContent = text;
  el.classList.remove("ok","warn");
  if (kind) el.classList.add(kind);
}

function setToast(el, text, kind=""){
  el.textContent = text;
  el.style.borderColor = kind === "ok" ? "rgba(46,204,113,.35)" :
                         kind === "warn" ? "rgba(241,196,15,.40)" :
                         kind === "bad" ? "rgba(255,91,91,.35)" : "rgba(255,255,255,.12)";
  el.style.color = kind === "ok" ? "#caffdf" :
                   kind === "warn" ? "#fff0b3" :
                   kind === "bad" ? "#ffc2c2" : "var(--muted)";
}

function setLoading(btn, isLoading, labelWhenLoading="Working…"){
  btn.disabled = isLoading;
  btn.dataset._label = btn.dataset._label || btn.textContent;
  btn.textContent = isLoading ? labelWhenLoading : btn.dataset._label;
}

function escapeHtml(str) {
  return (str || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function nowTime(){
  const d = new Date();
  return d.toLocaleTimeString([], {hour:"2-digit", minute:"2-digit"});
}

function addBubble(role, text){
  const div = document.createElement("div");
  div.className = `bubble ${role}`;

  const meta = document.createElement("div");
  meta.className = "meta";
  meta.innerHTML = `<span>${role === "user" ? "You" : "Assistant"}</span><span>•</span><span>${nowTime()}</span>`;

  const body = document.createElement("div");
  body.innerText = text;

  div.appendChild(meta);
  div.appendChild(body);
  chatOut.appendChild(div);
  chatOut.scrollTop = chatOut.scrollHeight;
}

function showTyping(on){
  if (on){
    chatHint.innerHTML = `<span class="typing">Typing…</span>`;
  } else {
    chatHint.textContent = "";
  }
}

// Friendly report rendering
function renderReport(reportText){
  analysisOut.textContent = reportText || "";

  const parsed = parseReport(reportText || "");
  analysisNice.innerHTML = "";

  // Score card
  const scoreCard = document.createElement("div");
  scoreCard.className = "score";

  const left = document.createElement("div");
  left.innerHTML = `
    <div class="label">Match score</div>
    <div class="num">${parsed.score !== null ? parsed.score : "—"}<span style="font-size:14px;color:var(--muted)">/100</span></div>
    <div class="meter"><div class="bar" id="scoreBar"></div></div>
  `;

  const right = document.createElement("div");
  right.className = "mini";
  right.innerHTML = parsed.score !== null
    ? `${parsed.score >= 85 ? "✅ Strong fit" : parsed.score >= 65 ? "⚠️ Medium fit" : "❗ Weak fit"}`
    : `Score not found`;

  scoreCard.appendChild(left);
  scoreCard.appendChild(right);
  analysisNice.appendChild(scoreCard);

  const bar = scoreCard.querySelector("#scoreBar");
  if (bar && parsed.score !== null) bar.style.width = `${Math.max(0, Math.min(100, parsed.score))}%`;

  // Sections
  analysisNice.appendChild(makeListSection("✅ Strengths", parsed.strengths));
  analysisNice.appendChild(makeListSection("⚠️ Gaps", parsed.gaps));
  analysisNice.appendChild(makeListSection("✨ Suggested resume improvements", parsed.improvements));

  // fallback if empty
  if (!parsed.strengths.length && !parsed.gaps.length && !parsed.improvements.length){
    const raw = document.createElement("pre");
    raw.className = "output";
    raw.textContent = reportText || "";
    analysisNice.appendChild(raw);
  }
}

function makeListSection(title, items){
  const sec = document.createElement("div");
  sec.className = "section";
  sec.innerHTML = `<h4>${escapeHtml(title)}</h4>`;

  if (!items || items.length === 0){
    const p = document.createElement("div");
    p.className = "muted";
    p.textContent = "Nothing listed.";
    sec.appendChild(p);
    return sec;
  }

  const ul = document.createElement("ul");
  for (const it of items){
    const li = document.createElement("li");
    li.textContent = it;
    ul.appendChild(li);
  }
  sec.appendChild(ul);
  return sec;
}

// very light parser for your report format
function parseReport(txt){
  const lines = (txt || "").split("\n");
  let score = null;

  // Score line like: Match score: 87/100
  const m = txt.match(/Match score:\s*(\d{1,3})\s*\/\s*100/i);
  if (m) score = parseInt(m[1], 10);

  const strengths = extractBulletsBetween(txt, "### Strengths", "### Gaps");
  const gaps = extractBulletsBetween(txt, "### Gaps", "### Suggested resume improvements");
  const improvements = extractBulletsAfter(txt, "### Suggested resume improvements");

  return { score, strengths, gaps, improvements };
}

function extractBulletsBetween(txt, startHeader, endHeader){
  const start = txt.indexOf(startHeader);
  if (start === -1) return [];
  const end = txt.indexOf(endHeader, start + startHeader.length);
  const block = end === -1 ? txt.slice(start) : txt.slice(start, end);
  return extractBullets(block);
}

function extractBulletsAfter(txt, header){
  const start = txt.indexOf(header);
  if (start === -1) return [];
  const block = txt.slice(start + header.length);
  return extractBullets(block);
}

function extractBullets(block){
  const out = [];
  const lines = block.split("\n");
  for (const l of lines){
    const line = l.trim();
    if (line.startsWith("- ")){
      // remove markdown ** **
      out.push(line.slice(2).replaceAll("**","").trim());
    }
  }
  return out;
}

async function checkBackend(){
  try{
    const res = await fetch(`/health`);
    const data = await res.json();
    backendStatus.textContent = data.ok ? "Backend: OK ✅" : "Backend: Problem";
    backendStatus.style.color = data.ok ? "var(--ok)" : "var(--bad)";
  }catch(e){
    backendStatus.textContent = "Backend: offline";
    backendStatus.style.color = "var(--bad)";
  }
}

$("btnUploadCV").onclick = async () => {
  const btn = $("btnUploadCV");
  setLoading(btn, true, "Uploading…");

  try {
    if (!cvFile.files || cvFile.files.length === 0) {
      setToast(cvToast, "Please select a CV file first.", "warn");
      return;
    }

    setToast(cvToast, "Uploading your CV and preparing it for search…", "");
    const form = new FormData();
    form.append("file", cvFile.files[0]);

    const res = await fetch(`${API_BASE}/api/resume/upload`, { method: "POST", body: form });
    const data = await res.json();

    if (!res.ok || !data.ok) {
      setToast(cvToast, data.error || "Upload failed.", "bad");
      setBadge(cvBadge, "Upload failed", "warn");
      return;
    }

    setBadge(cvBadge, "Uploaded ✅", "ok");
    setToast(cvToast, "✅ CV uploaded successfully. You can now run analysis or chat.", "ok");
    addBubble("bot", "✅ CV uploaded. Paste the job description next, then run analysis.");
  } catch (e) {
    setToast(cvToast, String(e), "bad");
  } finally {
    setLoading(btn, false);
  }
};

$("btnUpdateJD").onclick = async () => {
  const btn = $("btnUpdateJD");
  setLoading(btn, true, "Saving…");

  try {
    const text = (jdText.value || "").trim();
    if (!text) {
      setToast(jdToast, "Paste a job description first.", "warn");
      return;
    }

    setToast(jdToast, "Saving job description…", "");
    const res = await fetch(`${API_BASE}/api/jd/update`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ text })
    });

    const data = await res.json();
    if (!res.ok || !data.ok) {
      setToast(jdToast, data.error || "Save failed.", "bad");
      setBadge(jdBadge, "Save failed", "warn");
      return;
    }

    setBadge(jdBadge, "Saved ✅", "ok");
    setToast(jdToast, "✅ Job description saved. You can now run AI Fit Analysis.", "ok");
    addBubble("bot", "✅ Job description saved. Ready when you are — click Run Analysis.");

  } catch (e) {
    setToast(jdToast, String(e), "bad");
  } finally {
    setLoading(btn, false);
  }
};

$("btnClearJD").onclick = () => {
  jdText.value = "";
  setToast(jdToast, "Cleared JD text box.", "");
};

$("btnAnalyze").onclick = async () => {
  const btn = $("btnAnalyze");
  setLoading(btn, true, "Analyzing…");
  analysisMeta.textContent = "Running…";
  renderReport(""); // clear

  try {
    const res = await fetch(`${API_BASE}/api/analyze`, { method: "POST" });
    const data = await res.json();

    if (!res.ok || !data.ok) {
      analysisMeta.textContent = "";
      analysisNice.innerHTML = `<div class="section"><h4>⚠️ Cannot run analysis</h4><div class="muted">${escapeHtml(data.error || "Analysis failed")}</div></div>`;
      return;
    }

    analysisMeta.textContent = "Saved to history ✅";
    renderReport(data.report || "");
    await loadHistory();

  } catch (e) {
    analysisMeta.textContent = "";
    analysisNice.innerHTML = `<div class="section"><h4>⚠️ Error</h4><div class="muted">${escapeHtml(String(e))}</div></div>`;
  } finally {
    setLoading(btn, false);
  }
};

async function loadHistory(){
  historyList.innerHTML = `<div class="muted">Loading history…</div>`;

  try {
    const res = await fetch(`${API_BASE}/api/history`);
    const data = await res.json();

    if (!res.ok || !data.ok) {
      historyList.innerHTML = `<div class="muted">${escapeHtml(data.error || "Failed to load history")}</div>`;
      return;
    }

    if (!data.items || data.items.length === 0){
      historyList.innerHTML = `<div class="muted">No history yet.</div>`;
      return;
    }

    historyList.innerHTML = "";
    for (const it of data.items){
      const div = document.createElement("div");
      div.className = "history-item";

      const when = it.analysis_time || "";
      const score = it.match_score ?? "N/A";
      const jdprev = it.jd_preview || "";

      div.innerHTML = `
        <small>${escapeHtml(when)} • score: ${escapeHtml(String(score))}</small>
        <div class="mini" style="margin-top:6px;"><strong>JD preview:</strong> ${escapeHtml(jdprev)}</div>
        <details>
          <summary>Open report</summary>
          <pre class="output">${escapeHtml(it.report || "")}</pre>
        </details>
      `;
      historyList.appendChild(div);
    }

  } catch(e){
    historyList.innerHTML = `<div class="muted">${escapeHtml(String(e))}</div>`;
  }
}

$("btnRefreshHistory").onclick = loadHistory;

$("btnClearHistory").onclick = async () => {
  if (!confirm("Delete ALL history? This cannot be undone.")) return;

  const btn = $("btnClearHistory");
  setLoading(btn, true, "Deleting…");

  try{
    const res = await fetch(`${API_BASE}/api/history/clear`, { method:"POST" });
    const data = await res.json();
    if (!res.ok || !data.ok){
      alert(data.error || "Failed to delete history.");
      return;
    }
    await loadHistory();
    addBubble("bot", "🧹 History cleared.");
  }catch(e){
    alert(String(e));
  }finally{
    setLoading(btn, false, "Delete All");
  }
};

async function sendChat(){
  const msg = (chatInput.value || "").trim();
  if (!msg) return;

  addBubble("user", msg);
  chatInput.value = "";
  showTyping(true);

  try{
    const res = await fetch(`${API_BASE}/api/chat`, {
      method:"POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ message: msg })
    });
    const data = await res.json();
    if (!res.ok || !data.ok){
      addBubble("bot", data.error || "Chat failed.");
      return;
    }
    addBubble("bot", data.reply || "");
  }catch(e){
    addBubble("bot", String(e));
  }finally{
    showTyping(false);
  }
}

$("btnSendChat").onclick = sendChat;
chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendChat();
});

$("btnOpenHistory").onclick = () => {
  $("historySection").scrollIntoView({behavior:"smooth", block:"start"});
};

$("btnScrollTop").onclick = () => {
  window.scrollTo({top:0, behavior:"smooth"});
};

checkBackend();
loadHistory();
addBubble("bot", "Hi 👋 Upload your CV and save a job description, then I can analyze fit or answer questions.");
