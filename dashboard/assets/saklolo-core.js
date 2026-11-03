
/* =====================================================================
   SAKLOLO SHARED CORE — data, TOPSIS and guarded renderers for every page.
   Page-specific code (map, admin forms, routing) lives in each HTML file.
   ===================================================================== */
(() => {
'use strict';
const $  = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const TZ = 'Asia/Manila';
const hhmm = d => d.toLocaleTimeString('en-PH', {timeZone: TZ, hour: '2-digit', minute: '2-digit'});
const rel = ts => { const m = Math.round((Date.now() - ts) / 60000);
  return m < 1 ? 'just now' : m < 60 ? m + ' min ago' : Math.floor(m / 60) + ' h ago'; };

/* ---------- simulated reports (topics follow the six LDA topics in the study) ---------- */
const LEVEL = {high:'High urgency', neutral:'Situational', resolved:'Resolved'};
const REPORTS = [
  {m:3,  brgy:'San Pascual',  lat:14.823, lng:120.732, level:'high',     sent:-0.91, urg:0.96, topicA:'Rescue / Evacuation', topicB:'Stranded Residents', text:'Tulong po! May 3 batang naiipit sa bubong, lagpas-bubong na ang tubig dito sa San Pascual, Hagonoy. Rescue boat po please!'},
  {m:7,  brgy:'Frances',      lat:14.898, lng:120.762, level:'high',     sent:-0.86, urg:0.93, topicA:'Rescue / Evacuation', topicB:'Stranded Residents', text:'Lagpas bewang na ang baha sa Brgy. Frances, Calumpit. May matandang bedridden sa bahay namin, wala pong bangka.'},
  {m:12, brgy:'Tangos North', lat:14.673, lng:120.932, level:'high',     sent:-0.80, urg:0.90, topicA:'Health / Medical',    topicB:'Evacuation Centers', text:'Wala nang kuryente at tubig. May buntis na malapit nang manganak, kailangan ng ambulansya sa Tangos North, Navotas.'},
  {m:15, brgy:'Tonsuya',      lat:14.675, lng:120.957, level:'neutral',  sent:-0.22, urg:0.58, topicA:'Flood Levels',        topicB:'Rising Water', text:'Tuhod na ang baha sa M.H. del Pilar, Tonsuya, Malabon. Hindi na madaanan ng maliliit na sasakyan, pero passable pa sa trak.'},
  {m:21, brgy:'Hagonoy',      lat:14.833, lng:120.738, level:'neutral',  sent:-0.10, urg:0.52, topicA:'Flood Levels',        topicB:'Rising Water', text:'Update: tumaas ng 0.4m ang water level sa Hagonoy river gauge sa loob ng isang oras. Monitoring po.'},
  {m:29, brgy:'Tangos North', lat:14.673, lng:120.932, level:'resolved', sent: 0.84, urg:0.08, topicA:'Rescue / Evacuation', topicB:'Evacuation Centers', text:'Maraming salamat po sa rescue team! Nakarating na kami sa evacuation center ng Tangos North, ligtas po kaming lahat.'},
  {m:38, brgy:'Frances',      lat:14.898, lng:120.762, level:'resolved', sent: 0.79, urg:0.10, topicA:'Rescue / Evacuation', topicB:'Food & Relief Aid', text:'Na-rescue na si Lolo namin. Nasa Calumpit Elementary School na kami, may pagkain at kumot. Salamat po!'},
  {m:46, brgy:'Marulas',      lat:14.678, lng:120.978, level:'resolved', sent: 0.55, urg:0.12, topicA:'Flood Levels',        topicB:'Road & Bridge Damage', text:'Marulas, Valenzuela: humupa na ang tubig sa Gen. T. de Leon, passable na ulit para sa lahat ng sasakyan.'}
];
const INCOMING = [
  {brgy:'San Pascual',  lat:14.823, lng:120.732, level:'high',     sent:-0.88, urg:0.94, topicA:'Rescue / Evacuation', topicB:'Stranded Residents', text:'Paparating pa ang high tide, wala pa ring rescue dito sa San Pascual. May 5 pamilya sa bubong ng chapel.'},
  {brgy:'Tonsuya',      lat:14.675, lng:120.957, level:'neutral',  sent:-0.15, urg:0.49, topicA:'Flood Levels',        topicB:'Road & Bridge Damage', text:'Gutter-deep na lang ang tubig sa Tonsuya, bumababa na pero madulas pa ang kalsada.'},
  {brgy:'Frances',      lat:14.898, lng:120.762, level:'high',     sent:-0.77, urg:0.89, topicA:'Health / Medical',    topicB:'Food & Relief Aid', text:'Diabetic po ang tatay ko, naubusan ng insulin. Lubog ang daan palabas ng Frances, kailangan ng medical team.'},
  {brgy:'Tangos North', lat:14.673, lng:120.932, level:'resolved', sent: 0.72, urg:0.09, topicA:'Health / Medical',    topicB:'Evacuation Centers', text:'Nakapanganak na po ang kapitbahay namin sa ospital, ligtas mag-ina. Salamat sa ambulansya!'}
];

const sentBadge = s => s <= -0.3 ? ['Negative','badge--neg'] : s >= 0.3 ? ['Positive','badge--pos'] : ['Neutral','badge--neu'];

/* ---------- DSS alternatives: the six discovered topics per system ----------
   Data: bulacan_camanava topic x sentiment corpus matrix (n = 10,194 rows).
     neg/neu/pos  = row-normalised sentiment share (%) -> TOPSIS criteria values
     fn/fneu/fpos = raw report counts                 -> supporting facts on the cards
   Criteria = sentiment classifications, ALL BENEFIT: a higher share of any
   classification pulls the topic toward the ideal most-urgent profile. */
const DSS_TOPICS = {
  A: [
    {id:'a-rescue', name:'Rescue / Evacuation',   neg:65, neu:23, pos:12, fn:1790, fneu:640, fpos:323},
    {id:'a-relief', name:'Relief Goods',          neg:25, neu:33, pos:42, fn:540,  fneu:701, fpos:900},
    {id:'a-infra',  name:'Infrastructure Damage', neg:70, neu:22, pos:8,  fn:1210, fneu:385, fpos:138},
    {id:'a-flood',  name:'Flood Levels',          neg:57, neu:36, pos:7,  fn:810,  fneu:515, fpos:102},
    {id:'a-power',  name:'Power / Utilities',     neg:61, neu:32, pos:7,  fn:740,  fneu:395, fpos:88},
    {id:'a-health', name:'Health / Medical',      neg:47, neu:34, pos:19, fn:430,  fneu:310, fpos:177}
  ],
  B: [
    {id:'b-strand', name:'Stranded Residents',    neg:71, neu:22, pos:7,  fn:1720, fneu:520, fpos:170},
    {id:'b-relief', name:'Food & Relief Aid',     neg:24, neu:33, pos:43, fn:470,  fneu:655, fpos:860},
    {id:'b-road',   name:'Road & Bridge Damage',  neg:69, neu:25, pos:6,  fn:1050, fneu:380, fpos:92},
    {id:'b-water',  name:'Rising Water',          neg:56, neu:37, pos:7,  fn:1180, fneu:780, fpos:145},
    {id:'b-power',  name:'Power Outage',          neg:58, neu:34, pos:8,  fn:690,  fneu:400, fpos:90},
    {id:'b-evac',   name:'Evacuation Centers',    neg:35, neu:35, pos:30, fn:345,  fneu:345, fpos:302}
  ]
};
const SENT_CRITERIA = [
  {k:'neg', label:'Negative sentiment', desc:'distress reports',   dir:'benefit'},
  {k:'neu', label:'Neutral sentiment',  desc:'situational reports', dir:'benefit'},
  {k:'pos', label:'Positive sentiment', desc:'resolved reports',   dir:'benefit'}
];
const topicById = id => DSS_TOPICS.A.concat(DSS_TOPICS.B).find(t => t.id === id);

/* ---------- allocation channels (resource-allocation DSS) ----------
   Each channel re-weights the SAME sentiment criteria to answer a different
   resource question. Responders tune these profiles upfront; every profile
   drives its own TOPSIS ranked list (multi-list ranks). */
const CHANNELS = [
  {id:'consult', name:'Consultation focus',                  desc:'which topics to prioritise in community consultations', w:[34,33,33]},
  {id:'info',    name:'Sensitive information dissemination', desc:'where accurate, sensitive messaging is needed most',    w:[34,33,33]},
  {id:'expert',  name:'Expertise',                           desc:'where specialist knowledge should be assigned',          w:[34,33,33]},
  {id:'mats',    name:'Materials & supplies',                desc:'where relief materials should be prepositioned',         w:[34,33,33]}
];
const DEFAULT_CW = CHANNELS.map(c => [...c.w]);
const savedCW = (() => { try {
  const v = JSON.parse(localStorage.getItem('saklolo_channel_weights'));
  return (v && CHANNELS.every(c => Array.isArray(v[c.id]) && v[c.id].length === 3)) ? v : null;
} catch (e) { return null; } })();
if (savedCW) CHANNELS.forEach(c => { c.w = [...savedCW[c.id]]; });

/* TOPSIS: vector-normalise, weight, ideal best/worst, closeness = D- / (D+ + D-) */
function topsis(rows, criteria, weights){
  const sum = weights.reduce((a, b) => a + b, 0) || 1;
  const w = weights.map(x => x / sum), keys = criteria.map(c => c.k);
  const norm = keys.map(k => Math.sqrt(rows.reduce((s, r) => s + r[k] ** 2, 0)) || 1);
  const v = rows.map(r => keys.map((k, j) => r[k] / norm[j] * w[j]));
  const best  = keys.map((_, j) => criteria[j].dir === 'cost' ? Math.min(...v.map(x => x[j])) : Math.max(...v.map(x => x[j])));
  const worst = keys.map((_, j) => criteria[j].dir === 'cost' ? Math.max(...v.map(x => x[j])) : Math.min(...v.map(x => x[j])));
  return rows.map((r, i) => {
    const dp = Math.hypot(...v[i].map((x, j) => x - best[j]));
    const dn = Math.hypot(...v[i].map((x, j) => x - worst[j]));
    return {...r, score: dn / ((dp + dn) || 1)};
  }).sort((a, b) => b.score - a.score);
}

/* ---------- state ---------- */
const DEFAULT_SW = [34, 33, 33];   // equal default: 33% each after normalisation
const savedDecisions = (() => { try { return JSON.parse(localStorage.getItem('saklolo_topic_decisions')) || {}; } catch (e) { return {}; } })();

const savedW = (() => { try { const v = JSON.parse(localStorage.getItem('saklolo_weights'));
  return (Array.isArray(v) && v.length === 3 && v.every(x => typeof x === 'number')) ? v : null; } catch (e) { return null; } })();
const state = {
  filter:'all', sw:[...(savedW || DEFAULT_SW)], dec: savedDecisions, open:null, err:false, inIdx:0,
  freew:[...((() => { try { const v = JSON.parse(localStorage.getItem('saklolo_free_weights'));
    return (Array.isArray(v) && v.length === 3 && v.every(x => typeof x === 'number')) ? v : DEFAULT_SW; } catch (e) { return DEFAULT_SW; } })())],
  reports: REPORTS.map((r, i) => ({...r, pid:'P-' + String(48210 + i * 7), row_type: i % 5 === 4 ? 'comment' : 'post', src: i % 5 === 4 ? 'facebook_comment' : 'facebook_post', ts: Date.now() - r.m * 60000})),
  /* hourly series of the LAST COMPLETED nightly batch (Nov 2, 2026 · ETL-2482):
     24 buckets 12 AM – 11 PM, summing to the incoming-statistics card (1,442 classified / 96 high-urgency) */
  hours:{total:[18,12,9,7,6,8,14,26,41,58,72,85,79,68,63,68,77,90,104,118,129,112,96,82],
         high:[1,1,0,0,0,0,1,2,3,4,5,6,5,4,4,4,5,6,7,8,9,8,7,6]},
  since:REPORTS.length, sinceHigh:REPORTS.filter(r => r.level === 'high').length,
  log:[]
};

/* restore the audit trail across pages */
try { const rawLog = JSON.parse(localStorage.getItem('saklolo_audit_log'));
  if (Array.isArray(rawLog)) state.log = rawLog.slice(0, 40).map(l => ({t:new Date(l.t), msg:String(l.msg)})); } catch (e) {}

const ENGINE = {A:'System A (Hybrid: LDA + RoBERTa)', B:'System B (LLM: Qwen 3 1.7B Q4_K_M)'};
const sys = () => document.body.dataset.system || 'A';
const count = lv => state.reports.filter(r => r.level === lv).length;

function renderLog(){
  const el = $('#rs-log'); if (!el) return;
  el.innerHTML = state.log.map(l => `<li><time>${hhmm(l.t)}</time>${esc(l.msg)}</li>`).join('');
}
function log(msg){
  state.log.unshift({t:new Date(), msg}); state.log = state.log.slice(0, 40);
  try { localStorage.setItem('saklolo_audit_log', JSON.stringify(state.log)); } catch (e) {}
  renderLog();
}

/* ---------- dashboard ---------- */
let chart;
function renderStats(){
  if (!$('#rs-active')) return;
  const h = count('high'), n = count('neutral'), g = count('resolved'), all = state.reports.length;
  $('#rs-active').textContent = h + n; $('#rs-crit').textContent = h; $('#rs-done').textContent = g;
  $('#rs-tri-note').textContent = all + ' content items analysed (posts + comments)';
  $('#rs-tri').innerHTML = [['high',h],['neutral',n],['resolved',g]]
    .map(([lv, v]) => `<div class="rs-lv-${lv}" style="width:${v / all * 100}%" title="${LEVEL[lv]}: ${v}">${v}</div>`).join('');
}
function hourLabels(){   /* fixed window of the Nov 2, 2026 nightly batch (12 AM – 11 PM, the night before) */
  return Array.from({length:24}, (_, h) => (h % 12 || 12) + (h < 12 ? ' AM' : ' PM'));
}
function renderChart(){
  if (typeof Chart === 'undefined') return;                 // offline: cards still work
  const data = {labels: hourLabels(), datasets:[
    {label:'All content',   data:state.hours.total, borderColor:'#4da3ff', backgroundColor:'rgba(77,163,255,.12)', fill:true, tension:.35, pointRadius:2},
    {label:'High urgency', data:state.hours.high,  borderColor:'#ff4d4f', backgroundColor:'rgba(255,77,79,.18)',  fill:true, tension:.35, pointRadius:2}
  ]};
  if (chart){ chart.data = data; chart.update(); return; }
  Chart.defaults.color = '#9fb3bb';
  chart = new Chart($('#rs-chart'), {type:'line', data, options:{
    responsive:true, maintainAspectRatio:false, interaction:{mode:'index', intersect:false},
    plugins: {
      legend: {
        onClick: (e, legendItem, legend) => {
          // Custom click handler to toggle visibility
          const index = legendItem.datasetIndex;
          const ci = legend.chart;
          ci.isDatasetVisible(index) ? ci.hide(index) : ci.show(index);
        },
        labels: {
          boxWidth: 12,
          generateLabels: (chart) => {
            return chart.data.datasets.map((ds, i) => {
              const hidden = !chart.isDatasetVisible(i);
              return {
                text: (hidden ? '☐ ' : '☑ ') + ds.label, // Add checkbox symbol
                fillStyle: hidden ? 'transparent' : ds.backgroundColor,
                strokeStyle: ds.borderColor,
                lineWidth: 1,
                hidden: false, // CRITICAL: This stops Chart.js from crossing out the text
                datasetIndex: i,
                fontColor: hidden ? '#9fb3bb' : '#fff'
              };
            });
          }
        }
      }
    },
    scales:{x:{grid:{color:'rgba(255,255,255,.06)'}, title:{display:true, text:'Hour of day · Nov 2, 2026 (nightly batch ETL-2482)', color:'#9fb3bb', font:{size:11}}}, y:{beginAtZero:true, grid:{color:'rgba(255,255,255,.1)'}}}
  }});
}

/* ---------- map markers + feed ----------
   Leaflet-safe: drawMarkers is a no-op without the map. The feed itself is an
   Excel-style table: same schema for every row, click a header to sort, search
   to filter, click a row for the full record. */
let markerGroup = null;
function mapReady(){ return window.sakloloMap && typeof L !== 'undefined'; }
function drawMarkers(){
  if (!mapReady()) return;
  if (!markerGroup) markerGroup = L.layerGroup().addTo(window.sakloloMap);
  markerGroup.clearLayers();
  state.reports.forEach(r => {
    if (!r.lat || !r.lng) return;
    const c = r.level === 'high' ? '#ff4d4f' : r.level === 'neutral' ? '#ffb020' : '#35d49a';
    L.circleMarker([r.lat, r.lng], { radius:6, color:c, fillColor:c, fillOpacity:.8, weight:1 })
      .bindPopup(`<b>Brgy. ${esc(r.brgy)}</b><br>${esc(r.text)}`).addTo(markerGroup);
  });
}

function renderFeed(){
  const host = $('#rs-feed'); if (!host) return;
  const rows = state.reports.map(r => ({
    ts: r.ts, time: hhmm(new Date(r.ts)), pid: r.pid, type: r.row_type, event: 'Typhoon Carina (Gaemi)',
    loc: BRGY_MAP[r.brgy] || r.brgy, src: r.src, sent: r.sent, urg: r.urg,
    topic: sys() === 'A' ? r.topicA : r.topicB, text: r.text
  }));
  renderXlsxTable(host, FEED_COLS, rows, {
    sk:'ts', sd:-1, rowKey: r => r.pid,
    detail: r => `<b>Full content item</b><p class="xlsx-full">“${esc(r.text)}”</p>
      <dl class="xlsx-dl">
        <div><dt>post_id</dt><dd>${esc(r.pid)}</dd></div>
        <div><dt>row_type</dt><dd>${esc(r.type)}</dd></div>
        <div><dt>disaster_event</dt><dd>${esc(r.event)}</dd></div>
        <div><dt>location</dt><dd>${esc(r.loc)}</dd></div>
        <div><dt>source_type</dt><dd>${esc(r.src)}</dd></div>
        <div><dt>topic (active model)</dt><dd>${esc(r.topic)}</dd></div>
        <div><dt>sentiment score</dt><dd>${r.sent.toFixed(2)}</dd></div>
        <div><dt>urgency score</dt><dd>${r.urg.toFixed(2)}</dd></div>
      </dl>`
  });
}
/* ---------- TOPSIS queue + human-in-the-loop (alternatives = topics) ---------- */
function actionArea(t){
  const d = state.dec[t.id];
  if (d) return `<div class="rs-box"><b class="${d.type === 'accept' ? 'rs-lv-resolved' : 'rs-lv-neutral'}" style="color:var(--c)">${d.type === 'accept' ? 'Priority accepted — resources aligned to this topic' : 'Overridden: ' + esc(d.mod)}</b>
      ${d.note ? `<span>Justification: ${esc(d.note)}</span>` : ''}
      <button type="button" class="rs-btn" data-act="undo" data-id="${t.id}">Undo decision</button></div>`;
  if (state.open === t.id) return `<div class="rs-box">
      <label for="rs-mod"><b>What will change?</b></label>
      <select id="rs-mod"><option>Increase resources</option><option>Reduce resources</option><option>Reassign to another topic</option><option>Defer allocation</option></select>
      <label for="rs-note"><b>Justification (required)</b></label>
      <textarea id="rs-note" rows="3" class="${state.err ? 'is-bad' : ''}" placeholder="e.g. Community consultations already cover this concern; focus materials and expertise on another topic instead."></textarea>
      ${state.err ? '<span class="rs-err">Enter a justification before confirming.</span>' : ''}
      <div class="rs-act"><button type="button" class="rs-btn rs-btn--warn" data-act="confirm" data-id="${t.id}">Confirm override</button>
      <button type="button" class="rs-btn" data-act="cancel">Cancel</button></div></div>`;
  return `<div class="rs-act">
      <button type="button" class="rs-btn rs-btn--ok" data-act="accept" data-id="${t.id}">Accept Allocation Priority</button>
      <button type="button" class="rs-btn rs-btn--warn" data-act="override" data-id="${t.id}">Override / Modify</button></div>`;
}
function renderQueue(){
  const qHost = $('#rs-queue'); if (!qHost) return;
  const tone = i => i === 0 ? 'var(--red,#ff4d4f)' : i === 1 ? 'var(--amber,#ffb020)' : 'var(--rs-acc)';
  const wsum = state.sw.reduce((a, b) => a + b, 0) || 1;
  const wpct = state.sw.map(v => Math.round(v / wsum * 100));
  const ranked = topsis(DSS_TOPICS[sys()], SENT_CRITERIA, state.sw);
  const corpus = ranked.reduce((a, t) => a + t.fn + t.fneu + t.fpos, 0);
  qHost.innerHTML = `
    <div class="rs-qmeta" data-api="/api/dss/queue?system=${sys()}">QUEUE: Overall allocation priority (composite) · ALTERNATIVES: 6 topics · CRITERIA: Negative / Neutral / Positive sentiment (all benefit)
WEIGHTS (admin-set): Neg ${wpct[0]}% · Neu ${wpct[1]}% · Pos ${wpct[2]}% · SOURCE MATRIX: ${ENGINE[sys()]} · n = ${corpus.toLocaleString()} content items</div>` +
    ranked.map((t, i) => `
    <article class="card rs-q" style="--rc:${tone(i)}">
      <div class="rs-qhead">
        <div class="rs-rank" aria-label="Rank ${i + 1}">${i + 1}</div>
        <div class="rs-qmain">
          <h3>${esc(t.name)}<em>${t.score.toFixed(2)}</em></h3>
          <small>Topic alternative &nbsp;TOPSIS closeness to the ideal most-urgent sentiment profile (0 to 1)</small>
          <div class="rs-bar" role="img" aria-label="Closeness score ${t.score.toFixed(2)}"><div style="width:${t.score * 100}%"></div></div>
        </div>
      </div>
      <div class="rs-mix" role="img" aria-label="Sentiment mix: ${t.neg}% negative, ${t.neu}% neutral, ${t.pos}% positive">
        <div style="width:${t.neg}%;background:var(--red,#ff4d4f)" title="Negative ${t.neg}%"></div>
        <div style="width:${t.neu}%;background:var(--amber,#ffb020)" title="Neutral ${t.neu}%"></div>
        <div style="width:${t.pos}%;background:var(--green,#35d49a)" title="Positive ${t.pos}%"></div>
      </div>
      <div class="rs-facts">
        <div class="f-neg"><b>${t.neg}%</b>negative · ${t.fn.toLocaleString()}</div>
        <div class="f-neu"><b>${t.neu}%</b>neutral · ${t.fneu.toLocaleString()}</div>
        <div class="f-pos"><b>${t.pos}%</b>positive · ${t.fpos.toLocaleString()}</div>
        <div><b>${(t.fn + t.fneu + t.fpos).toLocaleString()}</b>reports in topic</div>
      </div>
      ${actionArea(t)}
    </article>`).join('');
}

/* ---------- SitRep ---------- */
function renderSitrep(){
  if (!$('#rs-doc')) return;
  const ranked = topsis(DSS_TOPICS[sys()], SENT_CRITERIA, state.sw);
  const h = count('high'), n = count('neutral'), g = count('resolved'), all = state.reports.length;
  const stamp = new Date().toLocaleString('en-PH', {timeZone: TZ, dateStyle:'long', timeStyle:'short'});
  const decs = Object.entries(state.dec).map(([id, d]) => {
    const t = topicById(id);
    return `   - ${t ? t.name : id}: ${d.type === 'accept' ? 'Allocation priority ACCEPTED' : 'OVERRIDDEN (' + d.mod + '). Reason: ' + d.note}`;
  });
  const wsum = state.sw.reduce((a, b) => a + b, 0) || 1;
  const wpct = state.sw.map(v => Math.round(v / wsum * 100));
  $('#rs-doc').textContent =
`NATIONAL DISASTER RISK REDUCTION AND MANAGEMENT COUNCIL
SITUATION REPORT NO. 01 (auto-generated by SAKLOLO)
As of ${stamp}
Coverage: Bulacan and CAMANAVA (Caloocan, Malabon, Navotas, Valenzuela)
Operational Window: Last 24 Hours

I. INCIDENT OVERVIEW
   ${all} Facebook content items (posts + comments) were analysed by ${ENGINE[sys()]}.
   ${h + n} content items remain active, ${h} of them are high-urgency.
   ${g} content items have been addressed (safe arrival or situation resolved).

II. PRIORITY TOPICS (TOPSIS-ranked, closeness score)
${ranked.slice(0, 4).map((t, i) => `   ${i + 1}. ${t.name}: score ${t.score.toFixed(2)}
      Sentiment profile — Negative ${t.neg}% · Neutral ${t.neu}% · Positive ${t.pos}%
      Corpus volume — ${(t.fn + t.fneu + t.fpos).toLocaleString()} content items
      (${t.fn.toLocaleString()} negative / ${t.fneu.toLocaleString()} neutral / ${t.fpos.toLocaleString()} positive).`).join('\n')}

III. TRIAGE BREAKDOWN
   RED     (high urgency) : ${String(h).padStart(3)}  (${Math.round(h / all * 100)}%)
   YELLOW  (situational)   : ${String(n).padStart(3)}  (${Math.round(n / all * 100)}%)
   GREEN   (resolved)      : ${String(g).padStart(3)}  (${Math.round(g / all * 100)}%)

IV. RESOURCE ALLOCATION DECISIONS
${decs.length ? decs.join('\n') : '   No allocation decisions recorded yet.'}

V. DSS METHOD
   Alternatives: the six discovered topics. Criteria: Negative / Neutral / Positive
   sentiment classifications (all benefit). Decision type: resource allocation across
   topics — consultation focus, sensitive information dissemination, expertise,
   materials and supplies.
   Composite weights — Negative ${wpct[0]}% · Neutral ${wpct[1]}% · Positive ${wpct[2]}%.
   Allocation channels (per-channel weight profiles, top topic per channel):
${CHANNELS.map(ch => { const ctop = topsis(DSS_TOPICS[sys()], SENT_CRITERIA, ch.w)[0]; return '   - ' + ch.name + ': ' + ctop.name + ' (closeness ' + ctop.score.toFixed(2) + ')'; }).join('\n')}
   Source matrix: ${ENGINE[sys()]} · n = 10,194 corpus rows (Facebook posts + comments).

Prepared by: SAKLOLO DSS (prototype, simulated data)
Validated by: ____________________  Date/Time: ______________`;
}

/* ---------- upfront composite weights + allocation channels ---------- */
function renderSw(){
  const swHost = $('#rs-sw'); if (!swHost) return;
  swHost.innerHTML = SENT_CRITERIA.map((c, j) => `
    <div><label for="rs-sw${j}"><span>${c.label} <small>· ${c.desc} · ${c.dir}</small></span><b id="rs-swv${j}"></b></label>
    <input id="rs-sw${j}" data-j="${j}" type="range" min="0" max="100" value="${state.sw[j]}"></div>`).join('');
  swLabels();
}
function swLabels(){
  const s = state.sw.reduce((a, b) => a + b, 0) || 1;
  state.sw.forEach((v, j) => { const el = $('#rs-swv' + j); if (el) el.textContent = Math.round(v / s * 100) + '%'; });
}

/* ---------- allocation channels: upfront profiles + multi-list ranks ---------- */
function cwLabels(ch){
  const s = ch.w.reduce((a, b) => a + b, 0) || 1;
  ch.w.forEach((v, j) => { const el = $('#rs-cw-' + ch.id + 'v' + j); if (el) el.textContent = Math.round(v / s * 100) + '%'; });
}
function renderChannelWeights(){
  const cwHost = $('#rs-cw'); if (!cwHost) return;
  cwHost.innerHTML = CHANNELS.map(ch => `
    <div class="rs-cw-row" id="rs-cw-${ch.id}">
      <div class="rs-cw-head"><b>${esc(ch.name)}</b><small>${esc(ch.desc)}</small></div>
      ${ch.w.map((v, j) => `
      <div class="rs-cw-ctl">
        <label for="rs-cw-${ch.id}${j}">${SENT_CRITERIA[j].k.slice(0, 3).toUpperCase()}</label>
        <input id="rs-cw-${ch.id}${j}" data-ch="${ch.id}" data-j="${j}" type="range" min="0" max="100" value="${v}">
        <b id="rs-cw-${ch.id}v${j}"></b>
      </div>`).join('')}
    </div>`).join('');
  CHANNELS.forEach(cwLabels);
}
function renderChannelRanks(){
  const host = $('#rs-cranks'); if (!host) return;
  host.innerHTML = CHANNELS.map(ch => {
    const ranked = topsis(DSS_TOPICS[sys()], SENT_CRITERIA, ch.w);
    const max = ranked[0].score || 1;
    const wsum = ch.w.reduce((a, b) => a + b, 0) || 1;
    const chips = ch.w.map((v, j) => `<span class="wchip wchip--${SENT_CRITERIA[j].k}">${SENT_CRITERIA[j].k.toUpperCase()} ${Math.round(v / wsum * 100)}%</span>`).join('');
    return `<div class="rs-chcard">
      <div class="rs-chhead"><h4>${esc(ch.name)}</h4><div class="rs-chw" title="Weights assigned by the administrator">${chips}</div></div>
      <p class="rs-chdesc">${esc(ch.desc)} · weights assigned by the administrator</p>
      <ol>${ranked.map((t, i) => `
        <li class="${i === 0 ? 'is-top' : ''}"><i style="width:${(t.score / max * 100).toFixed(0)}%"></i>
        <span class="rk">${i + 1}</span><span class="nm">${esc(t.name)}</span><em>${t.score.toFixed(2)}</em></li>`).join('')}</ol>
      <p class="rs-chfoot">Profile tuned by the administrator · <a href="dss-config.html">DSS Configuration</a></p>
    </div>`;
  }).join('');
}
/* operations-page extras: TOPSIS top-3 mini panel + backend systems panel */
function renderTopMini(){
  const host = $('#rs-topmini'); if (!host) return;
  const ranked = topsis(DSS_TOPICS[sys()], SENT_CRITERIA, state.sw).slice(0, 3);
  const wsum = state.sw.reduce((a, b) => a + b, 0) || 1;
  const wpct = state.sw.map(v => Math.round(v / wsum * 100));
  host.innerHTML = ranked.map((t, i) => `
    <div class="topmini-row"><span class="topmini-rank">${i + 1}</span>
    <span class="topmini-name">${esc(t.name)}</span>
    <span class="topmini-bar"><i style="width:${(t.score * 100).toFixed(0)}%"></i></span>
    <b>${t.score.toFixed(2)}</b></div>`).join('');
  const w = $('#rs-topw'); if (w) w.textContent = `Neg ${wpct[0]}% · Neu ${wpct[1]}% · Pos ${wpct[2]}%`;
}
function renderEngines(){
  const host = $('#rs-engines'); if (!host) return;
  host.innerHTML = ['A', 'B'].map(k => `
    <div class="engine-row ${sys() === k ? 'is-active' : ''}">
      <span class="sw sw--${k.toLowerCase()}"></span>
      <div><b>${ENGINE[k]}${sys() === k ? ' <span class="rs-tag rs-tag--live">active</span>' : ''}</b>
      <small>${k === 'A' ? 'LDA topic modelling + RoBERTa sentiment' : 'Qwen 3 1.7B LLM classification'} · corpus n = 10,194 · feeds the TOPSIS matrix</small></div>
    </div>`).join('');
}
function renderWeightSummary(){
  const el = $('#rs-wsum'); if (!el) return;
  const s = state.sw.reduce((a, b) => a + b, 0) || 1;
  const pct = state.sw.map(v => Math.round(v / s * 100));
  el.innerHTML = `<div class="rs-wsum-row"><b>Composite (overall priority)</b><span>Neg ${pct[0]}% · Neu ${pct[1]}% · Pos ${pct[2]}%</span></div>` +
    CHANNELS.map(ch => { const cs = ch.w.reduce((a, b) => a + b, 0) || 1;
      return `<div class="rs-wsum-row"><b>${esc(ch.name)}</b><span>${ch.w.map((v, j) => SENT_CRITERIA[j].k.slice(0, 3).toUpperCase() + ' ' + Math.round(v / cs * 100) + '%').join(' · ')}</span></div>`; }).join('');
}

/* ---------- topic word sets (single source of truth) ----------
   One keyword set per topic per system — displayed on NLP Topic Analytics
   and used as the blind-evaluation stimuli on the Responder portal. */
const TOPIC_WORDS = {
  A: {
    'Rescue / Evacuation':  ['rescue', 'tulong', 'stranded', 'bangka', 'evacuate', 'bubong'],
    'Relief Goods':         ['relief', 'pagkain', 'tubig', 'donasyon', 'volunteer', 'salamat'],
    'Infrastructure Damage':['tulay', 'kalsada', 'sira', 'gumuho', 'putol', 'daan'],
    'Flood Levels':         ['baha', 'lebel', 'tuhod', 'baywang', 'umaapaw', 'ilog'],
    'Power / Utilities':    ['kuryente', 'brownout', 'ilaw', 'linya', 'meralco', 'signal'],
    'Health / Medical':     ['gamot', 'ospital', 'sugat', 'lagnat', 'leptospirosis', 'medic']
  },
  B: {
    'Stranded Residents':    ['stranded', 'bubong', 'bangka', 'rescue'],
    'Food & Relief Aid':     ['relief', 'pagkain', 'volunteer'],
    'Road & Bridge Damage':  ['tulay', 'putol', 'daan'],
    'Rising Water':          ['baha', 'water level', 'tumataas'],
    'Power Outage':          ['kuryente', 'brownout', 'walang ilaw'],
    'Evacuation Centers':    ['evacuation', 'center', 'lilikas']
  }
};

/* ---------- topic × sentiment matrix (shared by NLP Analytics + Operations) ---------- */
const TOPIC_MATRIX = {
  A: {
    labels: ['Rescue / Evacuation', 'Relief Goods', 'Infrastructure Damage', 'Flood Levels', 'Power / Utilities', 'Health / Medical'],
    freq: { neg: [1790, 540, 1210, 810, 740, 430], neu: [640, 701, 385, 515, 395, 310], pos: [323, 900, 138, 102, 88, 177] },
    norm: { neg: [65, 25, 70, 57, 61, 47], neu: [23, 33, 22, 36, 32, 34], pos: [12, 42, 8, 7, 7, 19] }
  },
  B: {
    labels: ['Stranded Residents', 'Food & Relief Aid', 'Road & Bridge Damage', 'Rising Water', 'Power Outage', 'Evacuation Centers'],
    freq: { neg: [1720, 470, 1050, 1180, 690, 345], neu: [520, 655, 380, 780, 400, 345], pos: [170, 860, 92, 145, 90, 302] },
    norm: { neg: [71, 24, 69, 56, 58, 35], neu: [22, 33, 25, 37, 34, 35], pos: [7, 43, 6, 7, 8, 30] }
  }
};

/* ---------- barangay → city/province map for the live feed ---------- */
const BRGY_MAP = {
  'San Pascual':'Hagonoy, Bulacan', 'Frances':'Calumpit, Bulacan', 'Tangos North':'Navotas City, NCR',
  'Tonsuya':'Malabon City, NCR', 'Hagonoy':'Hagonoy, Bulacan', 'Marulas':'Valenzuela City, NCR'
};

/* ---------- Excel-style data tables (sort · search · clickable rows) ---------- */
const XLSX_STATE = new Map();   // per-host UI state, survives re-renders (live feed + typing)
function xlsxState(host){
  if (!host.id) host.id = 'xlsx-host-' + (XLSX_STATE.size + 1);
  if (!XLSX_STATE.has(host.id)) XLSX_STATE.set(host.id, { q:'', sk:null, sd:1, open:null, bound:false });
  return XLSX_STATE.get(host.id);
}
function renderXlsxTable(host, cols, rows, opts = {}){
  if (!host) return;
  const st = xlsxState(host);
  if (st.sk === null){ st.sk = (opts.sk !== undefined) ? opts.sk : (cols[0] ? cols[0].k : null); st.sd = opts.sd || 1; }
  const keyOf = opts.rowKey || ((r, i) => i);

  let list = rows;
  const q = st.q.trim().toLowerCase();
  if (q) list = rows.filter(r => Object.values(r).some(v => String(v == null ? '' : v).toLowerCase().includes(q)));
  if (st.sk !== null){
    const col = cols.find(c => c.k === st.sk);
    list = [...list].sort((a, b) => {
      let x = a[st.sk], y = b[st.sk];
      if (col && col.num){ x = +x || 0; y = +y || 0; return (x > y ? 1 : x < y ? -1 : 0) * st.sd; }
      x = String(x == null ? '' : x).toLowerCase(); y = String(y == null ? '' : y).toLowerCase();
      return x.localeCompare(y) * st.sd;
    });
  }

  if (!host.querySelector('.xlsx-bar')){
    host.innerHTML = `<div class="xlsx-bar">
        <input type="search" class="xlsx-search" placeholder="Search all columns…" aria-label="Search table rows">
        <span class="xlsx-count" aria-live="polite"></span></div>
      <div class="table-scroll"><table class="data-table xlsx-table"><thead></thead><tbody></tbody></table></div>`;
  }
  const thead = host.querySelector('thead'), tbody = host.querySelector('tbody'), count = host.querySelector('.xlsx-count');

  thead.innerHTML = '<tr>' + cols.map(c => {
    const on = st.sk === c.k;
    return `<th scope="col" data-k="${c.k}" title="Click to sort" aria-sort="${on ? (st.sd === 1 ? 'ascending' : 'descending') : 'none'}">${esc(c.label)}<i class="xlsx-arrow">${on ? (st.sd === 1 ? ' ▲' : ' ▼') : ''}</i></th>`;
  }).join('') + '</tr>';

  const trow = r => {
    const cells = cols.map(c => {
      const raw = r[c.k];
      const cell = (c.html && c.fmt) ? c.fmt(raw, r) : c.fmt ? esc(String(c.fmt(raw, r))) : esc(String(raw == null ? '' : raw));
      const cls = [c.num && 'num', c.cls].filter(Boolean).join(' ');
      return `<td${cls ? ` class="${cls}"` : ''}>${cell}</td>`;
    }).join('');
    const k = String(keyOf(r));
    return `<tr class="xlsx-row${st.open === k ? ' is-open' : ''}" data-key="${esc(k)}" tabindex="0" title="Click for full record">${cells}</tr>`;
  };
  tbody.innerHTML = list.length ? list.map(r => {
    const k = String(keyOf(r));
    if (st.open === k && opts.detail) return trow(r) + `<tr class="xlsx-detail"><td colspan="${cols.length}">${opts.detail(r)}</td></tr>`;
    return trow(r);
  }).join('') : `<tr><td class="xlsx-empty" colspan="${cols.length}">No rows match “${esc(st.q)}”.</td></tr>`;

  count.textContent = list.length + ' of ' + rows.length + ' rows';

  if (!st.bound){
    st.bound = true;
    thead.addEventListener('click', e => {
      const th = e.target.closest('th[data-k]'); if (!th) return;
      const k = th.dataset.k;
      if (st.sk === k) st.sd = -st.sd; else { st.sk = k; st.sd = 1; }
      renderXlsxTable(host, cols, rows, opts);
    });
    tbody.addEventListener('click', e => {
      const row = e.target.closest('tr.xlsx-row'); if (!row) return;
      const k = row.dataset.key;
      st.open = (st.open === k) ? null : k;
      renderXlsxTable(host, cols, rows, opts);
    });
    const search = () => {
      const inp = host.querySelector('.xlsx-search'); if (!inp) return;
      inp.addEventListener('input', () => { st.q = inp.value; renderXlsxTable(host, cols, rows, opts);
        const el = host.querySelector('.xlsx-search'); if (el){ el.focus(); el.setSelectionRange(el.value.length, el.value.length); } });
    };
    search();
  }
}

/* ---------- corpus sample for Data Feed Integration ----------
   Representative sample of the 10,194-row study corpus (posts + comments from
   Facebook pages of LGUs / NGAs; news-site rows are excluded from this study). */
const CORPUS_EVENTS = [
  { name:'Typhoon Carina (Gaemi)',          y:2024, mo:7,  days:[24,25,26] },
  { name:'Typhoon Enteng (Yagi)',           y:2024, mo:9,  days:[2,3,4] },
  { name:'Typhoon Paeng (Nalgae)',          y:2022, mo:10, days:[29,30,31] },
  { name:'Southwest Monsoon (Habagat)',     y:2023, mo:7,  days:[26,27,28] }
];
const CORPUS_PLACES = [
  ['Hagonoy, Bulacan','Region III'], ['Calumpit, Bulacan','Region III'], ['Malolos City, Bulacan','Region III'],
  ['Paombong, Bulacan','Region III'], ['Meycauayan City, Bulacan','Region III'], ['Marilao, Bulacan','Region III'],
  ['San Jose Del Monte City, Bulacan','Region III'], ['Obando, Bulacan','Region III'],
  ['Malabon City','NCR'], ['Navotas City','NCR'], ['Caloocan City','NCR'], ['Valenzuela City','NCR']
];
const CORPUS_TEXTS = [
  'Lampas bewang na ang tubig sa tapat ng bahay namin, wala pa ring rescuer na dumating dito.',
  'Salamat po sa MDRRMO sa mabilis na rescue ng pamilya namin kaninang umaga.',
  'Brownout pa rin sa buong barangay magdamag, minsan wala ring cellphone signal.',
  'May leptospirosis warning po ba dito? Nabasa ang paa ng anak ko sa baha.',
  'Sobra ang taas ng tubig sa tulay, isang lane na lang ang makakadaan.',
  'Nasa evacuation center na kami, may milk po ba para sa mga sanggol?',
  'Hindi pa rin kami nabibigyan ng relief goods, kulang daw ang supplies sa area namin.',
  'Update: humupa na ang baha sa kalsada namin, passable na ulit ang mga tricycle.',
  'Nakakulong kami sa second floor, tatlong bata at dalawang matatanda po dito.',
  'Salamat sa mga volunteer na tumulong sa mga hayop na natira sa aming lugar.',
  'Gumuho ang bahagi ng retaining wall malapit sa amin, evakuado ang mga kapitbahay.',
  'Walang tubig supply since kahapon, halos two days na rin ang brownout.',
  'Inabot ng tuhod ang baha sa palengke, hindi makapagtrabaho ang mga tao dito.',
  'Patuloy pa rin ang pag-ulan dito sa amin, dagundag ng dagundag ang tubig sa ilog.',
  'Nakauwi na po ang lahat ng stranded na residente, salamat sa rescue boat ng BFP.',
  'May warning daw na tataas ang daloy ng dam ngayong gabi, totoo po ba ito?'
];
function mulberry32(seed){
  return function(){
    seed |= 0; seed = seed + 0x6D2B79F5 | 0;
    let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}
const CORPUS = (() => {
  const rnd = mulberry32(10194);
  const DOW = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
  const out = [];
  for (let i = 0; i < 96; i++){
    const ev  = CORPUS_EVENTS[Math.floor(rnd() * CORPUS_EVENTS.length)];
    const [loc, reg] = CORPUS_PLACES[Math.floor(rnd() * CORPUS_PLACES.length)];
    const day = ev.days[Math.floor(rnd() * ev.days.length)];
    const date = `${ev.y}-${String(ev.mo).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    const hh = String(Math.floor(rnd() * 24)).padStart(2, '0');
    const mm = String(Math.floor(rnd() * 60)).padStart(2, '0');
    const ss = String(Math.floor(rnd() * 60)).padStart(2, '0');
    const rowType = rnd() < 0.62 ? 'post' : 'comment';
    const mult = rowType === 'post' ? 1 : 0.15;
    out.push({
      post_id: 'P-' + String(100000 + i * 97 + Math.floor(rnd() * 50)).padStart(6, '0'),
      parent_post_id: rowType === 'comment' ? 'P-' + String(100000 + Math.floor(rnd() * 96) * 97).padStart(6, '0') : 'null',
      row_type: rowType,
      timestamp: `${date} ${hh}:${mm}:${ss}`,
      date, year: ev.y, month: ev.mo,
      day_of_week: DOW[new Date(date + 'T00:00:00').getDay()],
      region: reg, location: loc,
      disaster_event: ev.name,
      source_type: rowType === 'comment' ? 'facebook_comment' : 'facebook_post',
      user_id: 'U-' + String(Math.floor(rnd() * 90000) + 1000),
      num_reactions: Math.floor(rnd() * 900 * mult),
      num_comments: Math.floor(rnd() * 260 * mult),
      num_shares: Math.floor(rnd() * 420 * mult),
      text: CORPUS_TEXTS[Math.floor(rnd() * CORPUS_TEXTS.length)]
    });
  }
  return out.sort((a, b) => b.timestamp.localeCompare(a.timestamp));
})();
const CORPUS_COLS = [
  {k:'post_id',        label:'Post ID'},
  {k:'row_type',       label:'Row type'},
  {k:'timestamp',      label:'Timestamp'},
  {k:'disaster_event', label:'Disaster event'},
  {k:'location',       label:'Location'},
  {k:'region',         label:'Region'},
  {k:'source_type',    label:'Source'},
  {k:'user_id',        label:'User'},
  {k:'num_reactions',  label:'Reactions', num:true},
  {k:'num_comments',   label:'Comments',  num:true},
  {k:'num_shares',     label:'Shares',    num:true},
  {k:'text',           label:'Text',      cls:'xlsx-trunc'}
];

/* ---------- live feed table columns (Raw Live Feed · responder) ---------- */
const FEED_COLS = [
  {k:'ts',    label:'Time (PHT)',       fmt:v => hhmm(new Date(v))},
  {k:'pid',   label:'Post ID'},
  {k:'type',  label:'Row type'},
  {k:'event', label:'Disaster event'},
  {k:'loc',   label:'Location'},
  {k:'src',   label:'Source'},
  {k:'sent',  label:'Sentiment', num:true, html:true, fmt:v => { const [l, c] = sentBadge(v); return `<span class="badge ${c}">${l} ${v > 0 ? '+' : ''}${v.toFixed(2)}</span>`; }},
  {k:'urg',   label:'Urgency', num:true, fmt:v => (+v).toFixed(2)},
  {k:'topic', label:'Topic (active model)'},
  {k:'text',  label:'Content', cls:'xlsx-trunc'}
];

/* ---------- training status (operations · prototype values) ---------- */
const TRAINING = [
  {comp:'System A · LDA topic model',        detail:'Gensim LDA · 6 discovered topics',              last:'Jan 18, 2026', win:'Jul 2022 – Nov 2024', n:'10,194'},
  {comp:'System A · RoBERTa sentiment head', detail:'Fine-tuned 3-class classifier (neg / neu / pos)', last:'Feb 02, 2026', win:'Jul 2022 – Nov 2024', n:'10,194'},
  {comp:'System B · Qwen 3 1.7B (Q4_K_M)',   detail:'Zero-shot prompted classification · no fine-tuning', last:'Feb 09, 2026', win:'Jul 2022 – Nov 2024', n:'10,194'}
];

/* ---------- manual training run (Data Feed Integration · persisted on device) ---------- */
function lastTraining(){
  try { const v = JSON.parse(localStorage.getItem('saklolo_last_training')); if (v && v.ts) return new Date(v.ts); } catch (e) {}
  return null;
}
function fmtTrainStamp(d){
  d = (d instanceof Date) ? d : new Date(d);
  return d.toLocaleDateString('en-PH', { timeZone: TZ, month: 'short', day: '2-digit', year: 'numeric' }) +
         ' · ' + d.toLocaleTimeString('en-PH', { timeZone: TZ, hour: '2-digit', minute: '2-digit' });
}
function setLastTraining(d){
  try { localStorage.setItem('saklolo_last_training', JSON.stringify({ ts: ((d instanceof Date) ? d : new Date()).toISOString() })); } catch (e) {}
  renderTraining();
}

/* ---------- renderers: word sets · free sublist · operations charts · training ---------- */
function renderTopicWords(){
  const a = $('#words-a'), b = $('#words-b');
  if (!a && !b) return;
  const group = (t, w, cls) => `<div class="topic-group"><h3>${esc(t)}</h3><div class="pills ${cls}">${w.map(x => `<span class="pill">${esc(x)}</span>`).join('')}</div></div>`;
  if (a) a.innerHTML = DSS_TOPICS.A.map(t => group(t.name, TOPIC_WORDS.A[t.name] || [], 'pills--a')).join('');
  if (b) b.innerHTML = DSS_TOPICS.B.map(t => group(t.name, TOPIC_WORDS.B[t.name] || [], '')).join('');
}
function renderFreeList(){
  const host = $('#rs-free'); if (!host) return;
  const ssum = state.freew.reduce((a, b) => a + b, 0) || 1;
  host.innerHTML = SENT_CRITERIA.map((c, j) => `
    <div><label for="rs-free${j}"><span>${c.label} <small>· ${c.desc}</small></span><b id="rs-freev${j}">${Math.round(state.freew[j] / ssum * 100)}%</b></label>
    <input id="rs-free${j}" data-j="${j}" type="range" min="0" max="100" value="${state.freew[j]}"></div>`).join('');
  const fr = $('#rs-franks'); if (!fr) return;
  const ranked = topsis(DSS_TOPICS[sys()], SENT_CRITERIA, state.freew);
  const max = ranked[0].score || 1;
  const chips = state.freew.map((v, j) => `<span class="wchip wchip--${SENT_CRITERIA[j].k}">${SENT_CRITERIA[j].k.toUpperCase()} ${Math.round(v / ssum * 100)}%</span>`).join('');
  fr.innerHTML = `<div class="rs-chcard"><div class="rs-chhead"><h4>Your composite ranking (live)</h4><div class="rs-chw" title="Your own weights">${chips}</div></div>
    <ol>${ranked.map((t, i) => `<li class="${i === 0 ? 'is-top' : ''}"><i style="width:${(t.score / max * 100).toFixed(0)}%"></i>
    <span class="rk">${i + 1}</span><span class="nm">${esc(t.name)}</span><em>${t.score.toFixed(2)}</em></li>`).join('')}</ol>
    <p class="rs-chfoot">Stored on this device · re-ranks as you move the sliders</p></div>`;
}
let opsChartT = null, opsChartS = null, opsSysDrawn = null;
function renderOpsCharts(){
  if (typeof Chart === 'undefined') return;
  const ct = $('#rs-ops-topics'), cs = $('#rs-ops-share');
  if (!ct && !cs) return;
  if (opsSysDrawn === sys() && opsChartT) return;   // already drawn for the active system
  opsSysDrawn = sys();
  Chart.defaults.color = '#9fb3bb';
  const M = TOPIC_MATRIX[sys()];
  if (ct){
    if (opsChartT) opsChartT.destroy();
    opsChartT = new Chart(ct, { type:'bar', data:{ labels:M.labels, datasets:[
        { label:'Negative (Distress)',   backgroundColor:'#ff4d4f', data:M.norm.neg },
        { label:'Neutral (Situational)', backgroundColor:'#ffb020', data:M.norm.neu },
        { label:'Positive (Resolved)',   backgroundColor:'#35d49a', data:M.norm.pos } ] },
      options:{ indexAxis:'y', responsive:true, maintainAspectRatio:false,
        scales:{ x:{ stacked:true, max:100, title:{ display:true, text:'Share of topic reports (%)' }, grid:{ color:'rgba(255,255,255,.06)' } },
                 y:{ stacked:true, grid:{ display:false } } },
        plugins:{ legend:{ position:'top', labels:{ boxWidth:12 } }, tooltip:{ mode:'index', intersect:false } } } });
  }
  if (cs){
    if (opsChartS) opsChartS.destroy();
    const vol = M.freq.neg.map((v, i) => v + M.freq.neu[i] + M.freq.pos[i]);
    opsChartS = new Chart(cs, { type:'doughnut', data:{ labels:M.labels, datasets:[{ data:vol,
      backgroundColor:['#4da3ff', '#35d49a', '#ffb020', '#ff4d4f', '#b07cff', '#35d4c9'] }] },
      options:{ responsive:true, maintainAspectRatio:false, plugins:{ legend:{ position:'right', labels:{ boxWidth:12 } } } } });
  }
  const tag = $('#rs-ops-sys'); if (tag) tag.textContent = ENGINE[sys()];
}
function renderTraining(){
  const host = $('#rs-train'); if (!host) return;
  const lt = lastTraining();
  const summary = [
    ['Training date range', 'Jul 2022 – Nov 2024', '10,194 Facebook posts &amp; comments · 4 disaster events'],
    ['Last training run', lt ? fmtTrainStamp(lt) : 'Feb 9, 2026', lt ? 'latest pipeline run — manual train (Data Feed Integration) or nightly ETL' : 'latest of the three model components below'],
    ['Nightly ETL', '3:00 AM PHT', "ingests &amp; re-classifies the day's content with these trained models"]
  ];
  host.innerHTML = '<div class="train-summary">' + summary.map(([l, v, d]) =>
      `<div><small>${l}</small><b>${v}</b><span>${d}</span></div>`).join('') + '</div>' +
    '<div class="train-rows">' + TRAINING.map(t => `
    <div class="train-row"><span class="dot dot--ok"></span>
      <div class="train-main"><b>${esc(t.comp)}</b><small>${esc(t.detail)}</small></div>
      <div class="train-meta"><span>Last trained: <b>${esc(t.last)}</b></span>
        <span>Corpus window: <b>${esc(t.win)}</b></span><span>n = <b>${esc(t.n)}</b> rows (posts + comments)</span></div>
    </div>`).join('') + '</div>' +
    '<small class="train-note">Prototype values shown for demonstration; a deployed deployment would expose live model checkpoints here.</small>';
}

/* ---------- live ingest simulation ----------
   New items arriving after the nightly cutoff are counted into the
   "since cutoff" line of the Incoming data statistics card. */
function ingest(){
  const src = INCOMING[state.inIdx++ % INCOMING.length];
  const isComment = state.inIdx % 5 === 0;
  state.reports.unshift({...src, pid:'P-' + String(48210 + 800 + state.inIdx * 13), row_type: isComment ? 'comment' : 'post', src: isComment ? 'facebook_comment' : 'facebook_post', ts: Date.now()});
  state.since++; if (src.level === 'high') state.sinceHigh++;
  log(`NLP ingest: ${LEVEL[src.level]} ${isComment ? 'comment' : 'post'} from ${src.brgy}`);
  refresh();
}
function renderIngest(){
  const host = $('#rs-ingest'); if (!host) return;
  const cells = [
    ['1,638', 'received'], ['1,016', 'facebook_post'], ['622', 'facebook_comment'],
    ['121', 'duplicates removed'], ['75', 'off-topic filtered'],
    ['1,442', 'classified &amp; kept'], ['96', 'high-urgency flagged']
  ];
  host.innerHTML = cells.map(([v, l]) => `<div class="rs-ing"><b>${v}</b><span>${l}</span></div>`).join('');
  const live = $('#rs-ingest-live');
  if (live) live.innerHTML = `<span class="dot dot--ok"></span> Since cutoff (11:59 PM · Nov 2): <b>${state.since}</b> new item${state.since === 1 ? '' : 's'} streamed in live (${state.sinceHigh} high-urgency) — queued for tonight's batch ETL-2483.`;
}
function renderEngine(){
  $$('.rs-engine').forEach(e => e.textContent = ENGINE[sys()]);
  const dn = $('#driver-name'); if (dn) dn.textContent = ENGINE[sys()];
}
/* Fault-isolated refresh: every renderer runs inside its own guard so one broken
   component (chart CDN, storage, etc.) can NEVER blank the others — most
   importantly the DSS TOPSIS resource-allocation queue must always reach the end user. */
function refresh(){
  const safe = (name, fn) => { try { fn(); } catch (e) { console.error('[SAKLOLO] ' + name + ' failed:', e); } };
  safe('renderEngine', renderEngine);
  safe('renderStats',  renderStats);
  safe('renderChart',  renderChart);
  safe('renderFeed',   renderFeed);
  safe('drawMarkers',  drawMarkers);
  safe('renderQueue',  renderQueue);
  safe('renderTopicWords', renderTopicWords);
  safe('renderFreeList',   renderFreeList);
  safe('renderOpsCharts',  renderOpsCharts);
  safe('renderTraining',   renderTraining);
  safe('renderIngest',     renderIngest);
  safe('renderChannelRanks', renderChannelRanks);
  safe('renderWeightSummary', renderWeightSummary);
  safe('renderTopMini', renderTopMini);
  safe('renderEngines', renderEngines);
  safe('renderSitrep', renderSitrep);
}

/* ---------- system toggle (persisted across pages) ---------- */
function paintSystem(){
  const toggle = $('#sys-toggle'); if (!toggle) return;
  toggle.dataset.active = sys();
  $$('.sys-toggle__opt').forEach(o => { const on = o.dataset.system === sys(); o.classList.toggle('is-active', on); o.setAttribute('aria-checked', on); });
}
const sysToggle = $('#sys-toggle');
if (sysToggle) sysToggle.addEventListener('click', e => {
  const b = e.target.closest('[data-system]'); if (!b) return;
  document.body.dataset.system = b.dataset.system;
  try { localStorage.setItem('saklolo_system', b.dataset.system); } catch (err) {}
});

function boot(){
  const tick = () => { const el = $('#rs-clock');
    if (el) el.textContent = new Date().toLocaleTimeString('en-PH', {timeZone: TZ, hour12:false}) + ' PHT'; };
  tick(); setInterval(tick, 1000);

  // Active model follows the persisted sidebar toggle
  try { const s = localStorage.getItem('saklolo_system'); if (s === 'A' || s === 'B') document.body.dataset.system = s; } catch (e) {}
  paintSystem();

  new MutationObserver(() => {
    renderEngine();
    renderFeed();
    drawMarkers();
    renderQueue();
    renderChannelRanks();
    renderTopMini();
    renderEngines();
    renderSitrep();
    renderOpsCharts();
    renderFreeList();
    log('Active model set to ' + ENGINE[sys()]);
  }).observe(document.body, {attributes:true, attributeFilter:['data-system']});

  const freeHost = $('#rs-free');
  if (freeHost){
    freeHost.addEventListener('input', e => { const j = e.target.dataset.j; if (j === undefined) return;
      state.freew[+j] = +e.target.value; renderFreeList(); });
    freeHost.addEventListener('change', () => { try { localStorage.setItem('saklolo_free_weights', JSON.stringify(state.freew)); } catch (err) {}
      log('Free sublist weights: ' + SENT_CRITERIA.map((c, j) => c.label + ' ' + $('#rs-freev' + j).textContent).join(', ')); });
  }
  const frreset = $('#rs-freereset');
  if (frreset) frreset.addEventListener('click', () => { state.freew = [...DEFAULT_SW];
    try { localStorage.removeItem('saklolo_free_weights'); } catch (err) {}
    renderFreeList(); log('Free sublist reset to equal weights'); });

  const qHost = $('#rs-queue');
  if (qHost) qHost.addEventListener('click', e => {
    const b = e.target.closest('[data-act]'); if (!b) return;
    const id = b.dataset.id, name = (topicById(id) || {}).name || id;
    switch (b.dataset.act){
      case 'accept':   state.dec[id] = {type:'accept'}; log(`Allocation priority accepted for topic: ${name}`); break;
      case 'override': state.open = id; state.err = false; break;
      case 'cancel':   state.open = null; state.err = false; break;
      case 'confirm': {
        const note = $('#rs-note').value.trim(), mod = $('#rs-mod').value;
        if (!note){ state.err = true; break; }
        state.dec[id] = {type:'override', mod, note}; state.open = null; state.err = false;
        log(`Override for topic ${name}: ${mod}. Reason: ${note}`); break; }
      case 'undo': delete state.dec[id]; log(`Decision undone for topic: ${name}`); break;
    }
    try { localStorage.setItem('saklolo_topic_decisions', JSON.stringify(state.dec)); } catch (err) {}
    renderQueue(); renderSitrep();
  });
  const regen = $('#rs-regen'); if (regen) regen.addEventListener('click', renderSitrep);
  const prnt  = $('#rs-print'); if (prnt) prnt.addEventListener('click', () => { renderSitrep(); window.print(); });

  renderSw();
  const swHost = $('#rs-sw');
  if (swHost){
    swHost.addEventListener('input', e => { const j = e.target.dataset.j; if (j === undefined) return; state.sw[j] = +e.target.value; swLabels(); renderQueue(); renderTopMini(); renderWeightSummary(); });
    swHost.addEventListener('change', () => { try { localStorage.setItem('saklolo_weights', JSON.stringify(state.sw)); } catch (err) {}
      log('Composite sentiment weights: ' + SENT_CRITERIA.map((c, j) => c.label + ' ' + $('#rs-swv' + j).textContent).join(', ')); });
  }
  const wreset = $('#rs-wreset');
  if (wreset) wreset.addEventListener('click', () => { state.sw = [...DEFAULT_SW];
    try { localStorage.removeItem('saklolo_weights'); } catch (err) {}
    renderSw(); renderQueue(); renderTopMini(); renderWeightSummary(); log('Composite sentiment weights reset to equal defaults'); });

  renderChannelWeights(); renderChannelRanks(); renderWeightSummary();
  const cwHost = $('#rs-cw');
  if (cwHost){
    cwHost.addEventListener('input', e => {
      const ch = CHANNELS.find(c => c.id === e.target.dataset.ch); if (!ch) return;
      ch.w[+e.target.dataset.j] = +e.target.value; cwLabels(ch); renderChannelRanks();
    });
    cwHost.addEventListener('change', () => {
      try { localStorage.setItem('saklolo_channel_weights', JSON.stringify(Object.fromEntries(CHANNELS.map(c => [c.id, [...c.w]])))); } catch (err) {}
      log('Channel weight profiles updated: ' + CHANNELS.map(c => c.name).join(' · '));
    });
  }
  const cwreset = $('#rs-cwreset');
  if (cwreset) cwreset.addEventListener('click', () => {
    CHANNELS.forEach((c, i) => { c.w = [...DEFAULT_CW[i]]; });
    try { localStorage.removeItem('saklolo_channel_weights'); } catch (err) {}
    renderChannelWeights(); renderChannelRanks();
    log('Channel weight profiles reset to defaults');
  });

  if (window.SAK_CONFIG && window.SAK_CONFIG.ingest) setInterval(() => { if (!document.hidden) ingest(); }, 14000);
  window.sakloloRefresh = refresh;          // pages with async extras (map) can re-render
  /* API surface for page-level scripts (blind eval, corpus table, admin charts) */
  window.SAK = {
    renderXlsxTable, CORPUS, CORPUS_COLS, TOPIC_WORDS, TOPIC_MATRIX, TOPIC_WORDS_LIST: TOPIC_WORDS,
    topsis, SENT_CRITERIA, DSS_TOPICS, ENGINE,
    TRAINING, lastTraining, fmtTrainStamp, setLastTraining
  };
  refresh(); renderLog();
  log('Module online: ' + document.title.replace('SAKLOLO | ', ''));
}
boot();
})();
