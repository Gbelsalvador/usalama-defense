(function () {
  const U = window.USALAMA, KEY = "usalama_history";
  const $ = (id) => document.getElementById(id);
  let cfg = null;

  const norm = (s) => s.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  const load = () => { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (e) { return []; } };
  const save = (h) => { try { localStorage.setItem(KEY, JSON.stringify(h.slice(0, 30))); } catch (e) {} };
  const li = (ul, text) => { const x = document.createElement("li"); x.textContent = text; ul.appendChild(x); };

  function analyze(text) {
    const t = norm(text);
    let score = 0; const why = [], todo = new Set();
    cfg.regles.forEach((r) => {
      if (r.patterns.some((p) => new RegExp(norm(p), "i").test(t))) {
        score += r.poids; why.push(r.explication); todo.add(r.conseil);
      }
    });
    if (/https?:\/\/|www\.|bit\.ly|tinyurl/.test(t)) { score += 3; why.push(U.t.lien); }
    const level = score >= cfg.seuils.eleve ? "eleve" : score >= cfg.seuils.a_verifier ? "verifier" : "faible";
    return { level, why, todo: [...todo] };
  }

  function show(res) {
    const box = $("verdict"); box.hidden = false; box.dataset.level = res.level;
    $("v-title").textContent = U.t[res.level];
    $("v-sub").textContent = U.t["sub" + res.level[0].toUpperCase() + res.level.slice(1)];
    const w = $("v-why"), d = $("v-do"); w.innerHTML = ""; d.innerHTML = "";
    res.why.forEach((x) => li(w, x)); res.todo.forEach((x) => li(d, x));
    box.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function renderHistory() {
    const ul = $("history"); ul.innerHTML = ""; const h = load();
    if (!h.length) return li(ul, U.t.vide);
    h.forEach((e) => li(ul, `${new Date(e.d).toLocaleDateString(U.lang)} — ${U.t[e.l]} — ${e.s}`));
  }

  async function init() {
    try { cfg = await (await fetch(U.rulesUrl)).json(); } catch (e) { $("v-title").textContent = U.t.erreur; }
    $("go").addEventListener("click", () => {
      const text = $("msg").value.trim(); if (!text || !cfg) return;
      const res = analyze(text); show(res);
      const h = load(); h.unshift({ d: Date.now(), l: res.level, s: text.slice(0, 40) + (text.length > 40 ? "…" : "") });
      save(h); renderHistory();
    });
    $("clear").addEventListener("click", () => { localStorage.removeItem(KEY); renderHistory(); });
    renderHistory();
  }
  init();
})();
