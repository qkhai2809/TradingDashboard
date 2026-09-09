/* =====================================================================
   DATA — sẽ được gán từ FastAPI sau khi gọi loadData()
   ===================================================================== */
let DATA = null;

/* =====================================================================
   STATE — thuần UI (đang xem outlier nào), không liên quan thuật toán
   ===================================================================== */
const state = { selectedOutlier: { market_cap: null, trading_volume: null } };
let lastRun = 'all';

/* =====================================================================
   API CONFIG
   ===================================================================== */
const API_URL = "http://127.0.0.1:8000/api/pipeline";

/* =====================================================================
   HELPERS — chỉ format hiển thị, không suy luận dữ liệu
   ===================================================================== */
function fmtNum(n){ return n.toLocaleString('en-US', {maximumFractionDigits:1}); }
function pct(entry, current){ return ((current-entry)/entry*100); }

// Dịch nhãn nguồn phát hiện ("Market Cap" / "Trading Volume" / cả hai,
// nối bằng " + ") sang tiếng Việt để hiển thị. Đây chỉ là i18n hiển
// thị — KHÔNG xác định lại nguồn, giá trị gốc luôn đến từ backend.
const SOURCE_LABELS = { "Market Cap": "Vốn hóa", "Trading Volume": "Khối lượng" };
function labelSources(raw){
  return raw.split('+').map(s => SOURCE_LABELS[s.trim()] || s.trim()).join(' + ');
}

/* =====================================================================
   LOAD DATA FROM BACKEND
   ===================================================================== */
async function loadData() {
    const response = await fetch(API_URL);
    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }
    return await response.json();
}

/* =====================================================================
   DASHBOARD — render: một khối nguồn (market_cap / trading_volume)
   ===================================================================== */
function renderSourceBlock(key){
  const d = DATA[key];
  const rows = d.top10.map(r => {
    const isOutlier = d.outliers.some(o => o.ticker === r.ticker);
    return `<tr class="${isOutlier ? 'outlier-row' : ''}">
      <td>${r.rank}</td>
      <td><b>${r.ticker}</b></td>
      <td class="wrap">${r.company}</td>
      <td><span class="tag tag-industry">${r.industry}</span></td>
      <td>${fmtNum(r.value)}</td>
    </tr>`;
  }).join('');

  const outlierCards = d.outliers.map(o => {
    const selected = state.selectedOutlier[key] === o.ticker ? 'selected' : '';
    return `<div class="outlier-card ${selected}" data-source="${key}" data-ticker="${o.ticker}">
      <div class="oc-left">
        <b>${o.ticker}</b> <span class="tag tag-outlier">${o.industry}</span>
        <div class="reason">${o.reason}</div>
      </div>
      <div class="oc-right">Hạng #${o.rank}<br>bấm để xem công ty liên quan</div>
    </div>`;
  }).join('');

  return `
  <div class="panel">
    <div class="panel-head">
      <span class="title">PHÂN TÍCH ${d.label}</span>
      <span class="meta">${d.unit}</span>
    </div>
    <div class="panel-body">
      <div class="stat-row">
        <div class="stat"><span>Ngành chiếm ưu thế</span><b>${d.dominantIndustry}</b></div>
        <div class="stat"><span>Số lượng chiếm ưu thế</span><b>${d.dominantCount} / 10</b></div>
      </div>
      <table>
        <thead><tr><th>Hạng</th><th>Mã</th><th>Công ty</th><th>Ngành</th><th>${d.label === 'VỐN HÓA' ? 'Vốn hóa' : 'Khối lượng'}</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
      <div class="outlier-block">
        <div class="label">NGOẠI LỆ</div>
        ${outlierCards}
      </div>
    </div>
  </div>`;
}

/* ---------------- render: công ty liên quan của outlier đang chọn ---------------- */
function renderRelated(key){
  const ticker = state.selectedOutlier[key];
  if(!ticker) return '';
  const d = DATA[key];
  const list = d.related[ticker] || [];
  const rows = list.map(c => `<tr>
      <td><b>${c.ticker}</b></td>
      <td class="wrap">${c.company}</td>
      <td><span class="tag tag-industry">${c.industry}</span></td>
    </tr>`).join('');
  return `
  <div class="panel">
    <div class="panel-head"><span class="title">CÔNG TY LIÊN QUAN — ${ticker}</span></div>
    <div class="panel-body">
      <table>
        <thead><tr><th>Mã</th><th>Công ty</th><th>Ngành</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  </div>`;
}

/* ---------------- render: so sánh ngành cho outlier đang chọn ----------------
   industry_comparison đã được backend (industry.py) tính sẵn cho từng
   outlier. Frontend chỉ đọc d.industry_comparison[ticker].matches,
   KHÔNG tự lọc list.related theo dominantIndustry nữa. */
function renderIndustryComparison(key){

  const ticker = state.selectedOutlier[key];

  if(!ticker) {
    return '';
  }

  const d = DATA[key];

  const outlier = d.outliers.find(
    o => o.ticker === ticker
  );

  const comparison =
    d.industry_comparison?.[ticker] || {};

  const matches =
    comparison.matches || [];

  const rows = matches.map(c => `
    <div class="flow-row hi">
      <span>
        ${c.ticker} — ${c.industry}
      </span>

      <span class="tag tag-match">
        CÙNG NGÀNH → ỨNG VIÊN
      </span>
    </div>
  `).join('');

  return `
    <div class="panel">

      <div class="panel-head">
        <span class="title">
          SO SÁNH NGÀNH
        </span>
      </div>

      <div class="panel-body">

        <div class="stat-row">

          <div class="stat">
            <span>Ngành của outlier</span>
            <b>${outlier.industry}</b>
          </div>

          <div class="stat">
            <span>Ngành được đối chiếu</span>
            <b>${outlier.industry}</b>
          </div>

        </div>

        <div
          class="label"
          style="
            font-size:11px;
            color:var(--text-dim);
            margin-bottom:6px;
          "
        >
          Công ty con cùng ngành với outlier
        </div>

        ${
          rows ||
          `
          <div class="empty-hint">
            Không có công ty con nào cùng ngành với outlier.
          </div>
          `
        }

      </div>

    </div>
  `;
}

/* ---------------- render: candidates ----------------
   DATA.candidates là danh sách candidate ĐÃ ĐƯỢC MERGE bởi
   pipeline.py (_merge_candidates), phẳng ở top-level — không tách
   theo market_cap/trading_volume. Không còn computeCandidates() ở
   đây: frontend không tự duyệt outlier, không tự lọc ngành, không tự
   gộp trùng nữa — tất cả đã do backend làm. */
function renderCandidates(){
  const cands = DATA.candidates || [];
  const rows = cands.map(c => `<tr>
      <td><b>${c.ticker}</b></td>
      <td><span class="tag tag-industry">${c.industry}</span></td>
      <td><span class="tag tag-match">${c.status}</span></td>
      <td>${labelSources(c.detected_from)}</td>
      <td class="wrap">${c.reason}</td>
    </tr>`).join('');
  return `
  <div class="panel">
    <div class="panel-head"><span class="title">ỨNG VIÊN</span></div>
    <div class="panel-body">
      <table>
        <thead><tr><th>Mã</th><th>Ngành</th><th>Trạng thái</th><th>Phát hiện từ</th><th>Lý do</th></tr></thead>
        <tbody>${rows || '<tr><td colspan="5" class="wrap empty-hint">Chưa có ứng viên nào được phát hiện.</td></tr>'}</tbody>
      </table>
    </div>
  </div>`;
}

/* ---------------- render: vị thế / mục tiêu chốt lời ---------------- */
function renderPositions(){
  const cards = (DATA.positions || []).map(p => {
    const gain = pct(p.entry, p.current);
    const targetGain = pct(p.entry, p.target);
    const hit = gain >= targetGain;
    return `<div class="pos-card">
      <div class="pt"><b>${p.ticker}</b></div>
      <div class="pos-nums">
        <div><span>Giá vào</span><b>${p.entry.toFixed(1)}</b></div>
        <div><span>Mục tiêu (+${targetGain.toFixed(0)}%)</span><b>${p.target.toFixed(1)}</b></div>
        <div><span>Hiện tại</span><b>${p.current.toFixed(1)} (${gain>=0?'+':''}${gain.toFixed(1)}%)</b></div>
      </div>
      <span class="status-pill ${hit ? 'status-sell' : 'status-watching'}">${hit ? 'BÁN' : 'THEO DÕI'}</span>
    </div>`;
  }).join('');
  return `
  <div class="panel">
    <div class="panel-head"><span class="title">VỊ THẾ / MỤC TIÊU CHỐT LỜI</span></div>
    <div class="panel-body">${cards}</div>
  </div>`;
}

/* ---------------- render toàn bộ dashboard ---------------- */
function renderDashboard(which){
  const el = document.getElementById('dashboardResults');
  if (!DATA) {
    el.innerHTML = `
      <div class="panel">
        <div class="panel-body">
          <p>Chưa có dữ liệu. Nhấn một trong các nút "CHẠY" để tải phân tích từ Backend.</p>
        </div>
      </div>
    `;
    return;
  }
  let html = '';
  const keys = which === 'all' ? ['market_cap','trading_volume'] : [which];

  keys.forEach(key => {
    html += renderSourceBlock(key);
    if(state.selectedOutlier[key]){
      html += `<div class="grid-2">${renderRelated(key)}${renderIndustryComparison(key)}</div>`;
    }
  });

  // Candidates + Positions là kết quả toàn cục của pipeline (không phụ
  // thuộc market_cap/trading_volume riêng lẻ hay outlier đang chọn),
  // nên luôn hiển thị sau các khối nguồn.
  html += renderCandidates();
  html += renderPositions();

  el.innerHTML = html;
  attachOutlierHandlers();
}

function attachOutlierHandlers(){
  document.querySelectorAll('.outlier-card').forEach(card => {
    card.addEventListener('click', () => {
      const key = card.dataset.source;
      const ticker = card.dataset.ticker;
      state.selectedOutlier[key] = state.selectedOutlier[key] === ticker ? null : ticker;
      renderDashboard(lastRun);
    });
  });
}

/* ---------------- runWithLoading: gọi API và cập nhật DATA ---------------- */
async function runWithLoading(which, label){
  lastRun = which;
  const veil = document.getElementById('loadingVeil');
  document.getElementById('loadingText').textContent = label;
  veil.classList.add('show');

  try {
    DATA = await loadData();
    // Sau khi có dữ liệu, render lại dashboard
    renderDashboard(which);
  } catch (error) {
    console.error(error);
    // Hiển thị lỗi trong dashboard
    const el = document.getElementById('dashboardResults');
    el.innerHTML = `
      <div class="panel">
        <div class="panel-body" style="color:var(--red);">
          <b>Lỗi kết nối Backend:</b> ${error.message}<br>
          Vui lòng kiểm tra FastAPI đang chạy tại ${API_URL}
        </div>
      </div>
    `;
  } finally {
    veil.classList.remove('show');
  }
}

/* =====================================================================
   TESTS PAGE
   ===================================================================== */

const TESTS_API_URL = "http://127.0.0.1:8000/api/tests";


/* ---------------------------------------------------------------------
   Gọi Backend để chạy pytest thật
   --------------------------------------------------------------------- */

async function loadTests() {

  const response = await fetch(TESTS_API_URL);

  if (!response.ok) {
    throw new Error(`Test API error: ${response.status}`);
  }

  return await response.json();
}


/* ---------------------------------------------------------------------
   Render kết quả test do Backend trả về
   --------------------------------------------------------------------- */

function renderTests(data = null) {

  const body = document.getElementById('testTableBody');
  const summary = document.getElementById('testSummary');

  if (!body || !summary) {
    return;
  }


  /* ---------------------------------------------------------------
     Chưa chạy test
     --------------------------------------------------------------- */

  if (!data) {

    summary.innerHTML = `
      <div class="item">
        <b>—</b>
        <span>chưa chạy</span>
      </div>

      <div class="item">
        <b>Backend</b>
        <span>nơi thực hiện kiểm thử</span>
      </div>

      <div class="item">
        <b>pytest</b>
        <span>framework kiểm thử</span>
      </div>
    `;

    body.innerHTML = `
      <tr>
        <td colspan="4" class="wrap empty-hint">
          Nhấn "CHẠY TẤT CẢ TEST" để chạy bộ kiểm thử thực tế tại Backend.
        </td>
      </tr>
    `;

    return;
  }


  /* ---------------------------------------------------------------
     Summary
     --------------------------------------------------------------- */

  summary.innerHTML = `
    <div class="item">
      <b>${data.passed}</b>
      <span>đạt</span>
    </div>

    <div class="item">
      <b style="color:var(--red)">
        ${data.failed}
      </b>
      <span>không đạt</span>
    </div>

    <div class="item">
      <b>${data.total}</b>
      <span>tổng số test</span>
    </div>
  `;


  /* ---------------------------------------------------------------
     Danh sách test
     --------------------------------------------------------------- */

  if (!data.tests || data.tests.length === 0) {

    body.innerHTML = `
      <tr>
        <td colspan="4" class="wrap empty-hint">
          Backend không trả về test nào.
        </td>
      </tr>
    `;

    return;
  }


  body.innerHTML = data.tests.map(test => {

    const isPassed = test.status === "passed";

    const statusText = isPassed
      ? "ĐẠT"
      : test.status === "skipped"
        ? "BỎ QUA"
        : "KHÔNG ĐẠT";

    const statusClass = isPassed
      ? "tag-pass"
      : test.status === "skipped"
        ? "tag-industry"
        : "tag-outlier";


    return `
      <tr>

        <td class="wrap">
          <b>${test.name}</b>
          <div style="
            font-size:11px;
            color:var(--text-dim);
            margin-top:3px;
          ">
            ${test.classname}
          </div>
        </td>

        <td>
          ${test.duration.toFixed(3)}s
        </td>

        <td>
          <span class="tag ${statusClass}">
            ${statusText}
          </span>
        </td>

        <td>
          <span class="tag ${isPassed ? 'tag-pass' : 'tag-outlier'}">
            ${test.status.toUpperCase()}
          </span>
        </td>

      </tr>
    `;

  }).join('');
}


/* ---------------------------------------------------------------------
   Nút CHẠY TẤT CẢ TEST
   --------------------------------------------------------------------- */

async function runTestsWithLoading() {

  const veil = document.getElementById('loadingVeil');
  const loadingText = document.getElementById('loadingText');

  if (veil) {
    veil.classList.add('show');
  }

  if (loadingText) {
    loadingText.textContent = 'ĐANG CHẠY TOÀN BỘ TEST…';
  }


  try {

    const result = await loadTests();

    renderTests(result);

  } catch (error) {

    console.error(error);

    const body = document.getElementById('testTableBody');
    const summary = document.getElementById('testSummary');

    if (summary) {
      summary.innerHTML = `
        <div class="item">
          <b style="color:var(--red)">ERROR</b>
          <span>không chạy được test</span>
        </div>
      `;
    }

    if (body) {
      body.innerHTML = `
        <tr>
          <td colspan="4" class="wrap" style="color:var(--red);">
            <b>Lỗi khi chạy Backend tests:</b><br>
            ${error.message}
          </td>
        </tr>
      `;
    }

  } finally {

    if (veil) {
      veil.classList.remove('show');
    }

  }
}

/* =====================================================================
   DEBUG PAGE — chỉ hiển thị lại kết quả pipeline đã trả về từng bước
   ===================================================================== */
function renderDebug(){
  if (!DATA) {
    document.getElementById('debugFlow').innerHTML = `
      <div class="flow-step">
        <div class="fs-label">Chưa có dữ liệu</div>
        <div class="fs-body">Hãy chạy phân tích từ Dashboard trước.</div>
      </div>
    `;
    return;
  }
  const key = document.getElementById('debugSource').value;
  const d = DATA[key];

  const relatedBlocks = d.outliers.map(o => {
    const rel = d.related[o.ticker] || [];
    const relLines = rel.map(c => `<div class="flow-row">&nbsp;&nbsp;├── ${c.ticker} — ${c.industry}</div>`).join('');
    return `<div class="flow-row flow-out">${o.ticker}</div>${relLines}`;
  }).join('');

  // Đọc thẳng industry_comparison do backend trả, không tự filter lại.
  const comparisonBlocks = d.outliers.map(o => {
    const matches = (d.industry_comparison[o.ticker] || {}).matches || [];
    if(matches.length === 0) return `<div class="flow-row">${o.ticker} → không trùng</div>`;
    return matches.map(m => `<div class="flow-row flow-match">${m.ticker} → ${m.status}</div>`).join('');
  }).join('');

  // Chỉ trích xuất (không lọc lại) danh sách ticker đã có sẵn trong
  // industry_comparison để hiển thị gọn ở bước cuối.
  const candidateTickers = [...new Set(
    Object.values(d.industry_comparison).flatMap(ic => ic.matches.map(m => m.ticker))
  )];

  const outlierRows = d.outliers.map(o => `<div class="flow-row flow-out">${o.ticker} → NGOẠI LỆ</div>`).join('');

  document.getElementById('debugFlow').innerHTML = `
    <div class="flow-step"><div class="fs-label">DỮ LIỆU ĐẦU VÀO</div><div class="fs-body">${d.label} · Top 10 · Hạng ${d.top10[0].rank}–${d.top10[d.top10.length-1].rank}</div></div>
    <div class="flow-arrow">↓</div>
    <div class="flow-step"><div class="fs-label">ĐÃ TẢI TOP 10</div><div class="fs-body">${d.top10.length} dòng dữ liệu</div></div>
    <div class="flow-arrow">↓</div>
    <div class="flow-step"><div class="fs-label">NGÀNH CHIẾM ƯU THẾ</div><div class="fs-body mono">${d.dominantIndustry} (${d.dominantCount}/10)</div></div>
    <div class="flow-arrow">↓</div>
    <div class="flow-step"><div class="fs-label">PHÁT HIỆN NGOẠI LỆ</div><div class="fs-body">${outlierRows}</div></div>
    <div class="flow-arrow">↓</div>
    <div class="flow-step"><div class="fs-label">CÔNG TY LIÊN QUAN</div><div class="fs-body">${relatedBlocks}</div></div>
    <div class="flow-arrow">↓</div>
    <div class="flow-step"><div class="fs-label">SO SÁNH NGÀNH</div><div class="fs-body">${comparisonBlocks}</div></div>
    <div class="flow-arrow">↓</div>
    <div class="flow-step"><div class="fs-label">ỨNG VIÊN</div><div class="fs-body mono" style="color:var(--amber)">${candidateTickers.join(', ') || '—'}</div></div>
  `;
}

/* =====================================================================
   NAVIGATION
   ===================================================================== */
function initNavigation(){
  document.querySelectorAll('.navitem').forEach(item => {
    item.addEventListener('click', () => {
      document.querySelectorAll('.navitem').forEach(n => n.classList.remove('active'));
      document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
      item.classList.add('active');
      document.getElementById('page-' + item.dataset.page).classList.add('active');
    });
  });
}

/* =====================================================================
   WIRING + INITIAL RENDER
   ===================================================================== */
function init(){
  // Khởi tạo các sự kiện
  document.getElementById('btnRunAll').addEventListener(
    'click',
    () => runWithLoading('all', 'ĐANG CHẠY TOÀN BỘ PHÂN TÍCH…')
  );

  document.getElementById('btnMarketCap').addEventListener(
    'click',
    () => runWithLoading('market_cap', 'ĐANG PHÂN TÍCH VỐN HÓA…')
  );

  document.getElementById('btnVolume').addEventListener(
    'click',
    () => runWithLoading(
      'trading_volume',
      'ĐANG PHÂN TÍCH KHỐI LƯỢNG GIAO DỊCH…'
    )
  );

  const btnRunTests = document.getElementById('btnRunTests');

  if (btnRunTests) {
    btnRunTests.addEventListener('click', runTestsWithLoading);
  }

  document.getElementById('debugSource').addEventListener(
    'change',
    renderDebug
  );

  initNavigation();
  
  // Hiển thị trạng thái chờ, không dùng MOCK
  renderDashboard('all');
  renderTests();
  renderDebug();
}
document.addEventListener('DOMContentLoaded', init);