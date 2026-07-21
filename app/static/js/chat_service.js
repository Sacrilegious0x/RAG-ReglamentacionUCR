/* ======================================================================
   CONFIGURACIÓN
   ====================================================================== */
// Ruta relativa: como este archivo lo sirve el mismo FastAPI que expone
// /chat, no hace falta hardcodear host:puerto. Si en algún momento el
// frontend se sirve desde otro origen, volvé a poner la URL completa
// (ej: "http://localhost:8000/chat") y asegurate de que CORS lo permita.
const API_URL = "/chat";
// Se espera un POST con body: { "query": "...", "history": [...] }
// y una respuesta JSON con la forma:
// {
//   "answer": "texto de la respuesta",
//   "sources": [
//     { "articulo": "Art. 15", "documento": "Reglamento de Régimen Académico Estudiantil" },
//     ...
//   ]
// }
/* ====================================================================== */

const messagesEl = document.getElementById('messages');
const inputEl = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const stampList = document.getElementById('stampList');
const statusLabel = document.getElementById('statusLabel');

let history = [];
let seenArticles = new Set();

// Autosize del textarea
inputEl.addEventListener('input', () => {
  inputEl.style.height = 'auto';
  inputEl.style.height = Math.min(inputEl.scrollHeight, 140) + 'px';
});
inputEl.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// En móvil, cuando se abre/cierra el teclado virtual, el visualViewport
// cambia de tamaño (a diferencia de window, que se mantiene fijo). Sin esto,
// el último mensaje puede quedar tapado por el teclado en iOS/Android.
if (window.visualViewport) {
  window.visualViewport.addEventListener('resize', () => {
    scrollToBottom();
  });
}

function toggleExpediente(open) {
  const el = document.getElementById('expediente');
  if (open) el.classList.add('open');
  else el.classList.remove('open');
}

function scrollToBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function addMessage(role, html) {
  const wrap = document.createElement('div');
  wrap.className = 'msg ' + role;
  wrap.innerHTML = `<div class="bubble">${html}</div>`;
  messagesEl.appendChild(wrap);
  scrollToBottom();
  return wrap;
}

function addTyping() {
  const wrap = document.createElement('div');
  wrap.className = 'msg assistant';
  wrap.id = 'typingIndicator';
  wrap.innerHTML = `<div class="bubble"><div class="typing"><span></span><span></span><span></span></div></div>`;
  messagesEl.appendChild(wrap);
  scrollToBottom();
}

function removeTyping() {
  const el = document.getElementById('typingIndicator');
  if (el) el.remove();
}

function escapeHtml(str) {
  const d = document.createElement('div');
  d.innerText = str;
  return d.innerHTML;
}

function addStamp(articulo, documento) {
  const key = articulo + '|' + documento;
  if (seenArticles.has(key)) return;
  seenArticles.add(key);
  const div = document.createElement('div');
  div.className = 'stamp';
  div.innerHTML = `<span class="art">${escapeHtml(articulo)}</span><div class="doc">${escapeHtml(documento)}</div>`;
  stampList.appendChild(div);
}

function renderSources(sources) {
  if (!sources || !sources.length) return '';
  const chips = sources.map(s => {
    addStamp(s.articulo || '—', s.documento || 'Documento no identificado');
    return `<span class="cite-chip">${escapeHtml(s.articulo || '—')}</span>`;
  }).join('');
  return `<div class="cites">${chips}</div>`;
}

async function sendMessage() {
  const text = inputEl.value.trim();
  if (!text) return;

  addMessage('user', escapeHtml(text));
  history.push({ role: 'user', content: text });
  inputEl.value = '';
  inputEl.style.height = 'auto';
  sendBtn.disabled = true;
  addTyping();

  try {
    const res = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: text, history })
    });

    if (!res.ok) {
      throw new Error(`El servidor respondió con estado ${res.status}`);
    }

    const data = await res.json();
    removeTyping();

    const answer = data.answer ?? data.response ?? data.result ?? '(el backend no devolvió un campo "answer")';
    const sourcesHtml = renderSources(data.sources);

    addMessage('assistant', `<p>${escapeHtml(answer).replace(/\n/g, '<br>')}</p>${sourcesHtml}`);
    history.push({ role: 'assistant', content: answer });

  } catch (err) {
    removeTyping();
    const msg = addMessage('assistant', `No se pudo obtener respuesta del servidor.<br><small>${escapeHtml(err.message)}</small><br><small>Verificá que el backend esté corriendo y que <code>${API_URL}</code> responda.</small>`);
    msg.querySelector('.bubble').classList.add('error-bubble');
  } finally {
    sendBtn.disabled = false;
    inputEl.focus();
  }
}

async function checkHealth() {
  try {
    const base = new URL(API_URL, window.location.origin).origin;
    const res = await fetch(base + '/health', { method: 'GET' }).catch(() => null);
    if (res && res.ok) {
      statusLabel.textContent = 'backend conectado';
      statusLabel.style.color = '#8FBF8F';
    } else {
      statusLabel.textContent = 'backend no verificado';
    }
  } catch (e) {
    statusLabel.textContent = 'backend no verificado';
  }
}
checkHealth();