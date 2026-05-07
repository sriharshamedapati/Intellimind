/* ============================================================
   markdown.js — Shared Markdown → HTML Renderer
   ============================================================ */

function esc(s) {
  return String(s)
    .replace(/&/g,"&amp;").replace(/</g,"&lt;")
    .replace(/>/g,"&gt;").replace(/"/g,"&quot;")
    .replace(/'/g,"&#39;");
}

function renderMarkdown(raw) {
  const parts   = [];
  const CODE_RE = /```(\w*)\n?([\s\S]*?)```/g;
  let last = 0, m;
  while ((m = CODE_RE.exec(raw)) !== null) {
    if (m.index > last) parts.push({ t:"text", v: raw.slice(last, m.index) });
    parts.push({ t:"code", lang: m[1] || "text", v: m[2] });
    last = CODE_RE.lastIndex;
  }
  if (last < raw.length) parts.push({ t:"text", v: raw.slice(last) });
  return parts.map(p => p.t === "code" ? buildCodeBlock(p.lang, p.v) : renderText(p.v)).join("");
}

function renderText(raw) {
  let s = esc(raw);

  // Pre-process mashed inline bullets (e.g., "idea. * Reason:")
  s = s.replace(/([.?!:])\s+([\*\-\•])(?=\s+[A-Z])/g, "$1\n\n$2");

  // Block elements
  s = s.replace(/^\s*###\s+(.+)$/gm, "\n\n<h3>$1</h3>\n\n");
  s = s.replace(/^\s*##\s+(.+)$/gm,  "\n\n<h3>$1</h3>\n\n");
  s = s.replace(/^\s*#\s+(.+)$/gm,   "\n\n<h3>$1</h3>\n\n");
  s = s.replace(/^\s*---+$/gm, "\n\n<hr>\n\n");
  
  s = s.replace(/((?:^\s*\d+\.\s+.+\n?)+)/gm, blk =>
    "\n\n<ol>" + blk.trim().split("\n").map(l => l.replace(/^\s*\d+\.\s+/, "").trim()).filter(l => l.length > 0).map(l => "<li>" + l + "</li>").join("") + "</ol>\n\n");
  s = s.replace(/((?:^\s*[•\-\*]\s*.+\n?)+)/gm, blk =>
    "\n\n<ul>" + blk.trim().split("\n").map(l => l.replace(/^\s*[•\-\*]\s*/, "").trim()).filter(l => l.length > 0).map(l => "<li>" + l + "</li>").join("") + "</ul>\n\n");

  // Inline elements
  s = s.replace(/\*\*\*(.+?)\*\*\*/g, "<strong><em>$1</em></strong>");
  s = s.replace(/\*\*(.+?)\*\*/g,     "<strong>$1</strong>");
  s = s.replace(/__(.+?)__/g,         "<strong>$1</strong>");
  s = s.replace(/\*([^\s\*].*?[^\s\*]|[^\s\*])\*/g, "<em>$1</em>");
  s = s.replace(/`([^`]+)`/g, "<code>$1</code>");

  // Paragraph wrapping
  s = s.split(/\n{2,}/).map(para => {
    para = para.trim();
    if (!para) return "";
    if (/^<(h3|ul|ol|hr)/.test(para)) return para;
    return "<p>" + para.replace(/\n/g, "<br>") + "</p>";
  }).join("");
  return s;
}

function buildCodeBlock(lang, code) {
  const id          = "cb" + Math.random().toString(36).slice(2, 9);
  const highlighted = highlight(esc(code.trimEnd()), lang.toLowerCase());
  return `
<div class="code-block">
  <div class="code-header">
    <div class="code-dots"><span class="d1"></span><span class="d2"></span><span class="d3"></span></div>
    <span class="code-lang">${esc(lang || "code")}</span>
    <button class="copy-btn" onclick="copyCode('${id}',this)">
      <svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
      Copy
    </button>
  </div>
  <div class="code-body" id="${id}">${highlighted}</div>
</div>`;
}

function highlight(html, lang) {
  if (["python","py"].includes(lang)) {
    return html
      .replace(/(#[^\n]*)(?![^<]*>)/g, '<span class="tok-cmt">$1</span>')
      .replace(/\b(def|class|return|if|elif|else|for|while|import|from|as|in|not|and|or|is|None|True|False|pass|break|continue|try|except|with|lambda|yield|async|await|raise|del|global|nonlocal|print)\b(?![^<]*>)/g, '<span class="tok-kw">$1</span>')
      .replace(/\b([A-Z][a-zA-Z0-9_]*)\b(?![^<]*>)/g, '<span class="tok-cls">$1</span>')
      .replace(/([a-zA-Z_]\w*)\s*(?=\()(?![^<]*>)/g,  '<span class="tok-fn">$1</span>')
      .replace(/(&#39;.*?&#39;|&quot;.*?&quot;)(?![^<]*>)/g, '<span class="tok-str">$1</span>')
      .replace(/\b(\d+\.?\d*)\b(?![^<]*>)/g, '<span class="tok-num">$1</span>');
  }
  if (["js","javascript","ts","typescript"].includes(lang)) {
    return html
      .replace(/(\/\/[^\n]*)(?![^<]*>)/g, '<span class="tok-cmt">$1</span>')
      .replace(/\b(const|let|var|function|return|if|else|for|while|class|new|this|import|export|from|of|in|typeof|instanceof|async|await|try|catch|finally|throw|null|undefined|true|false|switch|case|default|break|continue|do|extends|super|=&gt;)\b(?![^<]*>)/g, '<span class="tok-kw">$1</span>')
      .replace(/\b([A-Z][a-zA-Z0-9_]*)\b(?![^<]*>)/g, '<span class="tok-cls">$1</span>')
      .replace(/([a-zA-Z_$]\w*)\s*(?=\()(?![^<]*>)/g, '<span class="tok-fn">$1</span>')
      .replace(/(&#39;.*?&#39;|&quot;.*?&quot;)(?![^<]*>)/g, '<span class="tok-str">$1</span>')
      .replace(/\b(\d+\.?\d*)\b(?![^<]*>)/g, '<span class="tok-num">$1</span>');
  }
  if (["java","cpp","c"].includes(lang)) {
    return html
      .replace(/(\/\/[^\n]*)(?![^<]*>)/g, '<span class="tok-cmt">$1</span>')
      .replace(/\b(int|long|float|double|char|boolean|void|class|public|private|protected|static|final|return|if|else|for|while|new|this|import|package|interface|extends|implements|try|catch|finally|throw|null|true|false|String|System|out|println|include|using|namespace|std|cout|cin|endl|auto|template|typename)\b(?![^<]*>)/g, '<span class="tok-kw">$1</span>')
      .replace(/([a-zA-Z_]\w*)\s*(?=\()(?![^<]*>)/g, '<span class="tok-fn">$1</span>')
      .replace(/(&#34;.*?&#34;)(?![^<]*>)/g, '<span class="tok-str">$1</span>')
      .replace(/\b(\d+\.?\d*)\b(?![^<]*>)/g, '<span class="tok-num">$1</span>');
  }
  if (lang === "sql") {
    return html.replace(/\b(SELECT|FROM|WHERE|JOIN|LEFT|RIGHT|INNER|OUTER|ON|GROUP BY|ORDER BY|HAVING|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|TABLE|INTO|VALUES|SET|AS|AND|OR|NOT|IN|LIKE|BETWEEN|NULL|IS|COUNT|SUM|AVG|MAX|MIN|DISTINCT|LIMIT|INDEX|PRIMARY|KEY|FOREIGN|REFERENCES|CONSTRAINT|DEFAULT)\b(?![^<]*>)/gi,
      '<span class="tok-kw">$1</span>');
  }
  return html;
}

function copyCode(id, btn) {
  const text = document.getElementById(id).innerText;
  navigator.clipboard.writeText(text).then(() => {
    btn.innerHTML = `<svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg> Copied!`;
    btn.classList.add("copied");
    setTimeout(() => {
      btn.innerHTML = `<svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg> Copy`;
      btn.classList.remove("copied");
    }, 2000);
  });
}
