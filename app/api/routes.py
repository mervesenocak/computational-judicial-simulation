from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse

from app.schemas.dava import DavaGirdisi
from app.schemas.response import AnalyzeResponse
from app.services.karar_servisi import KararServisi

router = APIRouter()

_UI_HTML = r"""
<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Hakim Simülasyonu</title>
  <style>
    :root{
      --bg:#0b1220; --panel:#0f1b2e; --card:#101f36; --line:#1e3357;
      --text:#eaf0ff; --muted:#a9b7d0; --btn:#2f6bff; --btn2:#1f2f4d;
      --warn:#ffd27a; --err:#ff5a5a;
      --shadow: 0 20px 60px rgba(0,0,0,.45);
      --radius: 16px;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial;
    }
    body{
      margin:0;
      background:
        radial-gradient(1200px 600px at 25% 10%, rgba(47,107,255,.25), transparent 55%),
        radial-gradient(900px 500px at 80% 20%, rgba(54,211,153,.14), transparent 55%),
        var(--bg);
      color:var(--text);
    }
    .wrap{ max-width: 1040px; margin: 42px auto; padding: 0 18px; }
    .header{
      display:flex; align-items:flex-start; justify-content:space-between; gap:18px;
      margin-bottom:18px;
    }
    .title h1{ margin:0; font-size: 34px; letter-spacing:.2px; }
    .title p{ margin:8px 0 0; color:var(--muted); line-height:1.4; font-size: 14px; }
    .chiprow{ display:flex; gap:8px; flex-wrap:wrap; margin-top:10px; }
    .chip{
      border:1px solid var(--line); color:var(--muted);
      background: rgba(16,31,54,.45); padding:6px 10px; border-radius: 999px;
      font-size: 12px;
    }
    .quick{
      background: rgba(16,31,54,.55);
      border:1px solid var(--line); border-radius: var(--radius);
      padding:14px; min-width: 260px; box-shadow: var(--shadow);
    }
    .quick h3{ margin:0 0 10px; font-size: 14px; color:var(--muted); }
    .quick .row{ display:flex; gap:10px; }
    .a{
      display:inline-block; text-decoration:none; color:var(--text);
      border:1px solid var(--line); background: rgba(11,18,32,.35);
      padding:10px 12px; border-radius: 12px; font-size: 13px;
    }
    .grid{ display:grid; grid-template-columns: 1.15fr .85fr; gap:16px; }
    .panel{
      background: rgba(16,31,54,.55);
      border:1px solid var(--line); border-radius: var(--radius);
      box-shadow: var(--shadow);
      padding: 16px;
    }
    label{ display:block; font-size: 12px; color:var(--muted); margin-bottom:8px; }
    select, textarea, input[type="file"]{
      width:100%; box-sizing:border-box;
      border:1px solid var(--line);
      background: rgba(11,18,32,.35);
      color:var(--text);
      padding: 12px 12px;
      border-radius: 12px;
      outline:none;
    }
    textarea{ min-height: 170px; resize: vertical; line-height: 1.45; }
    .hint{ margin:8px 0 0; font-size:12px; color:var(--muted); }
    .btns{ display:flex; gap:10px; flex-wrap:wrap; margin-top: 12px; }
    button{
      border:1px solid var(--line);
      border-radius: 12px;
      padding: 10px 12px;
      background: var(--btn2);
      color: var(--text);
      cursor:pointer;
      font-weight:600;
    }
    button.primary{ background: var(--btn); border-color: rgba(47,107,255,.7); }
    button:disabled{ opacity:.6; cursor:not-allowed; }

    .out{ margin-top: 16px; display:none; gap: 12px; }
    .card{
      background: rgba(16,31,54,.55);
      border:1px solid var(--line); border-radius: var(--radius);
      padding: 14px;
    }
    .card h3{ margin:0 0 10px; font-size: 14px; color:var(--muted); }
    .kpi{ display:flex; gap:12px; flex-wrap:wrap; }
    .kpi .box{
      background: rgba(11,18,32,.35);
      border:1px solid var(--line);
      border-radius: 14px; padding: 10px 12px;
      min-width: 190px;
    }
    .kpi .box b{ display:block; font-size: 13px; }
    .kpi .box span{ color:var(--muted); font-size: 12px; }
    table{ width:100%; border-collapse: collapse; }
    th, td{ border-bottom: 1px solid rgba(30,51,87,.6); padding: 10px 8px; font-size: 13px; vertical-align: top; }
    th{ color: var(--muted); font-weight: 700; text-align:left; }
    details{
      border: 1px solid rgba(30,51,87,.6);
      background: rgba(11,18,32,.25);
      border-radius: 14px;
      padding: 10px 12px;
      margin-bottom: 8px;
    }
    summary{ cursor:pointer; color: var(--muted); font-weight: 700; }
    .quote{
      margin-top:10px;
      color: var(--text);
      padding: 10px 12px;
      border-left: 3px solid rgba(47,107,255,.7);
      background: rgba(16,31,54,.35);
      border-radius: 12px;
      font-size: 13px;
      line-height: 1.45;
      white-space: pre-wrap;
    }
    pre{ margin:0; white-space: pre-wrap; word-break: break-word; font-size: 13px; line-height: 1.45; color: var(--text); }
    .warn{ color: var(--warn); }
    .err{ color: var(--err); }
    .footer{ margin-top: 12px; color: var(--muted); font-size: 12px; }
    @media (max-width: 920px){
      .grid{ grid-template-columns: 1fr; }
      .quick{ width: 100%; }
      .header{ flex-direction: column; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="header">
      <div class="title">
        <h1>Hakim Simülasyonu</h1>
        <p>
          Denetlenebilir (audit edilebilir) hukuk-AI prototipi.
          <b>Uydurma atıf üretmez</b> — kaynak yoksa “kaynak yok” der.
          <span class="warn">Bu hukuki tavsiye değildir.</span>
        </p>
        <div class="chiprow">
          <span class="chip">Özel hukuk: kural tabanlı</span>
          <span class="chip">Ceza: açıklanabilir puanlama</span>
          <span class="chip">Atıf: yalnız DB</span>
        </div>
      </div>

      <div class="quick">
        <h3>Hızlı Linkler</h3>
        <div class="row">
          <a class="a" href="/docs" target="_blank" rel="noreferrer">Swagger</a>
          <a class="a" href="/openapi.json" target="_blank" rel="noreferrer">OpenAPI</a>
        </div>
        <div class="footer">UI: /api/web • API: /api/analyze</div>
      </div>
    </div>

    <div class="grid">
      <div class="panel">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
          <div>
            <label>Dava Türü</label>
            <select id="dava_turu">
              <option value="ozel">Özel Hukuk</option>
              <option value="ceza">Ceza</option>
            </select>
            <div class="hint">İstersen dosya yükle, istersen metni aşağıya yapıştır.</div>
          </div>
          <div>
            <label>Dosya (PDF / DOCX / TXT) — opsiyonel</label>
            <input id="file" type="file" />
            <div class="hint">Dosya seçmezsen metin alanını kullan.</div>
          </div>
        </div>

        <div style="margin-top:12px">
          <label>Olay Özeti / Metin</label>
          <textarea id="olay" placeholder="Olayı yaz. Delil/talep varsa ekle."></textarea>
        </div>

        <div class="btns">
          <button class="primary" id="btn" onclick="analyze()">Analiz Et</button>
          <button onclick="fillOzel()" type="button">Örnek Özel</button>
          <button onclick="fillCeza()" type="button">Örnek Ceza</button>
          <button onclick="clearAll()" type="button">Temizle</button>
        </div>

        <div class="out" id="outWrap">
          <div class="card">
            <h3>Karar Özeti</h3>
            <div class="kpi" id="kpi"></div>
          </div>

          <div class="card" id="scoreCard" style="display:none;">
            <h3>Puanlama Tablosu</h3>
            <div id="scoreTable"></div>
          </div>

          <div class="card" id="citCard" style="display:none;">
            <h3>Hukuki Dayanaklar</h3>
            <div id="citations"></div>
          </div>

          <div class="card">
            <h3>Gerekçeli Metin</h3>
            <pre id="decision"></pre>
          </div>

          <div class="card" id="warnCard" style="display:none;">
            <h3>Uyarılar</h3>
            <div id="warnings"></div>
          </div>
        </div>

        <div class="footer">Not: Bu uygulama eğitim/portföy amaçlıdır. Hukuki tavsiye değildir.</div>
      </div>

      <div class="panel">
        <h3 style="margin:0 0 10px; color:var(--muted); font-size:14px;">Jüriye cümle</h3>
        <div class="quote">
Bu prototip, özel hukukta deterministik kural motoru ile gerekçeli karar taslağı üretir;
ceza alanında ise açıklanabilir puanlama modeliyle öneri üretir.
Atıflar yalnızca yerel veritabanındaki mevzuat/ictihat kaynaklarından gelir; uydurma atıf üretmez.
        </div>
      </div>
    </div>
  </div>

<script>
function esc(s){
  return (s ?? "").toString()
    .replaceAll("&","&amp;").replaceAll("<","&lt;")
    .replaceAll(">","&gt;").replaceAll('"',"&quot;")
    .replaceAll("'","&#039;");
}

function setBusy(b){
  const btn = document.getElementById("btn");
  btn.disabled = b;
  btn.textContent = b ? "Analiz ediliyor..." : "Analiz Et";
}

function fillOzel(){
  document.getElementById("dava_turu").value = "ozel";
  document.getElementById("olay").value =
`Davacı, davalının kusurlu davranışıyla maddi ve manevi zarara uğradığını ileri sürmektedir.
Talepler: maddi tazminat, manevi tazminat.
Deliller: tanık beyanı, dekont, bilirkişi raporu.`;
}

function fillCeza(){
  document.getElementById("dava_turu").value = "ceza";
  document.getElementById("olay").value =
`Sanığın kasten yaralama fiilini işlediği, kamera görüntüsü ve bilirkişi raporu bulunduğu iddia edilmektedir.
Etkin pişmanlık gösterdiği ve zararı giderdiği belirtilmiştir.
Deliller: kamera görüntüsü, bilirkişi raporu, tanık beyanı.`;
}

function clearAll(){
  document.getElementById("olay").value = "";
  document.getElementById("file").value = "";
  document.getElementById("outWrap").style.display = "none";
}

function renderKPI(data){
  const kpi = document.getElementById("kpi");
  kpi.innerHTML = "";
  const scores = data.scores || {};
  const toplam = scores.toplam_puan ?? "—";
  const oneri = scores.onerilen_sonuc ?? "—";
  const citCount = (data.citations || []).length;

  const items = [
    ["Dava Türü", data.case_type],
    ["Öneri", oneri],
    ["Toplam Puan", toplam],
    ["Atıf Sayısı", citCount],
  ];
  for(const [k,v] of items){
    const d = document.createElement("div");
    d.className = "box";
    d.innerHTML = `<b>${esc(k)}</b><span>${esc(v)}</span>`;
    kpi.appendChild(d);
  }
}

function renderScores(data){
  const scoreCard = document.getElementById("scoreCard");
  const scoreTable = document.getElementById("scoreTable");
  const scores = data.scores || {};
  const kalemler = scores.kalemler || [];
  if(!kalemler.length){
    scoreCard.style.display = "none";
    return;
  }
  scoreCard.style.display = "block";
  let html = `<table><thead><tr><th>Kriter</th><th>Puan</th><th>Gerekçe</th></tr></thead><tbody>`;
  for(const k of kalemler){
    html += `<tr><td>${esc(k.faktor)}</td><td>${esc(k.puan)}</td><td>${esc(k.aciklama)}</td></tr>`;
  }
  html += `</tbody></table>`;
  scoreTable.innerHTML = html;
}

function renderCitations(data){
  const citCard = document.getElementById("citCard");
  const citationsDiv = document.getElementById("citations");
  const cits = data.citations || [];
  if(!cits.length){
    citCard.style.display = "none";
    return;
  }
  citCard.style.display = "block";
  citationsDiv.innerHTML = "";
  for(const c of cits){
    const title = (c.kaynak_turu === "kanun")
      ? `${c.kanun_veya_daire} m.${c.madde_no || "?"}`
      : `${c.kanun_veya_daire} ${c.esas_no || ""}/${c.karar_no || ""}`.trim();

    const det = document.createElement("details");
    det.innerHTML = `
      <summary>${esc(title)}</summary>
      <div class="quote">
<b>Kaynak Kimlik:</b> ${esc(c.kaynak_kimlik)}<br/>
<b>Tarih:</b> ${esc(c.tarih || "—")}<br/>
<b>Özet:</b> ${esc(c.ozet || "—")}<br/>
<b>Alıntı:</b> ${esc(c.alinti || "—")}
      </div>
    `;
    citationsDiv.appendChild(det);
  }
}

function renderWarnings(data){
  const warnCard = document.getElementById("warnCard");
  const warnings = document.getElementById("warnings");
  const ws = data.warnings || [];
  if(!ws.length){
    warnCard.style.display = "none";
    return;
  }
  warnCard.style.display = "block";
  warnings.innerHTML = ws.map(w => `<div class="warn">• ${esc(w)}</div>`).join("");
}

async function analyze(){
  setBusy(true);
  document.getElementById("outWrap").style.display = "none";

  const dava_turu = document.getElementById("dava_turu").value;
  const olay = document.getElementById("olay").value || "";
  const f = document.getElementById("file").files[0];

  try{
    if (f){
      const fd = new FormData();
      fd.append("file", f);
      fd.append("dava_turu", dava_turu);
      fd.append("olay_ozeti", olay);

      let res = await fetch("upload_analyze", { method:"POST", body: fd });
      if (!res.ok){
        res = await fetch("analyze_pdf", { method:"POST", body: fd });
      }
      const data = await res.json();
      renderKPI(data);
      renderScores(data);
      renderCitations(data);
      renderWarnings(data);
      document.getElementById("decision").textContent = data.decision_text || "";
      document.getElementById("outWrap").style.display = "grid";
      setBusy(false);
      return;
    }

    const payload = {
      dava_turu: dava_turu,
      olay_ozeti: olay,
      taraflar: null,
      talepler: null,
      deliller: null,
      tarih: null,
      ek_bilgiler: null
    };

    const res = await fetch("analyze", {
      method:"POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    renderKPI(data);
    renderScores(data);
    renderCitations(data);
    renderWarnings(data);
    document.getElementById("decision").textContent = data.decision_text || "";
    document.getElementById("outWrap").style.display = "grid";
  } catch(e){
    document.getElementById("outWrap").style.display = "grid";
    document.getElementById("warnCard").style.display = "block";
    document.getElementById("warnings").innerHTML = `<div class="err">Hata: ${esc(e.message || e)}</div>`;
  } finally {
    setBusy(false);
  }
}
</script>
</body>
</html>
"""

@router.get("/", response_class=HTMLResponse)
def home():
    # Bu endpoint /api/ olur
    return "<h3>Hakim Simülasyonu ✅</h3><p><a href='/api/web'>UI</a> • <a href='/docs'>Swagger</a></p>"

@router.get("/web", response_class=HTMLResponse)
def web_form():
    # Bu endpoint /api/web olur
    return _UI_HTML

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(dava: DavaGirdisi):
    servis = KararServisi()
    decision_text, citations, scores, warnings = servis.karar_uret(dava)
    return AnalyzeResponse(
        case_type=dava.dava_turu,
        decision_text=decision_text,
        citations=citations,
        scores=scores,
        warnings=warnings,
    )

@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    return {"filename": file.filename, "size_bytes": len(content)}

@router.post("/upload_analyze", response_model=AnalyzeResponse)
async def upload_and_analyze(
    file: UploadFile = File(...),
    dava_turu: str = Form("ozel"),
    olay_ozeti: str = Form(""),
):
    _ = await file.read()
    dava = DavaGirdisi(
        dava_turu=dava_turu,
        olay_ozeti=olay_ozeti or f"Dosya yüklendi: {file.filename}",
        taraflar=None,
        talepler=None,
        deliller=None,
        tarih=None,
        ek_bilgiler=f"Yüklenen dosya: {file.filename}",
    )
    return analyze(dava)

@router.post("/analyze_pdf", response_model=AnalyzeResponse)
async def analyze_pdf(
    file: UploadFile = File(...),
    dava_turu: str = Form("ozel"),
    olay_ozeti: str = Form(""),
):
    _ = await file.read()
    dava = DavaGirdisi(
        dava_turu=dava_turu,
        olay_ozeti=olay_ozeti or f"PDF/DOCX yüklendi: {file.filename}",
        taraflar=None,
        talepler=None,
        deliller=None,
        tarih=None,
        ek_bilgiler=f"Yüklenen dosya: {file.filename} (parse henüz bağlı değil)",
    )
    return analyze(dava)

@router.post("/web_pdf")
def web_pdf(dava_turu: str = Form("ozel"), olay_ozeti: str = Form("")):
    try:
        from app.services.pdf_servisi import karar_metninden_pdf_bytes
    except Exception:
        raise HTTPException(status_code=501, detail="PDF servisi bağlı değil (pdf_servisi.py bulunamadı).")

    dava = DavaGirdisi(
        dava_turu=dava_turu,
        olay_ozeti=olay_ozeti,
        taraflar=None,
        talepler=None,
        deliller=None,
        tarih=None,
        ek_bilgiler=None,
    )
    servis = KararServisi()
    decision_text, _, _, _ = servis.karar_uret(dava)
    pdf_bytes = karar_metninden_pdf_bytes(decision_text)

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=karar.pdf"},
    )