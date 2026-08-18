/**
 * FinWise — Dedicated Bank Spending Analytics Dashboard Controller
 * Handles data fetching, Chart.js visualizations, calendar heatmap,
 * financial health gauge, and tab routing for /spending-analytics.
 */

// ── Color System ─────────────────────────────────────────────────
const COLORS = {
  blush:    '#F4A7B9',
  butter:   '#F5E642',
  sage:     '#B8D4A8',
  lavender: '#C9B8E8',
  peach:    '#FFD9A0',
  teal:     '#A8D4D4',
  ink:      '#1A1A2E',
  muted:    '#7A7A9A',
  palette:  ['#F4A7B9', '#F5E642', '#B8D4A8', '#C9B8E8', '#FFD9A0', '#A8D4D4', '#E8B4B8', '#B4D4E8', '#E8D4B4']
};

const CAT_COLORS = {
  'Food & Dining':   '#F4A7B9',
  'Shopping':        '#F5E642',
  'Transportation':  '#A8D4D4',
  'Entertainment':   '#C9B8E8',
  'Utilities':       '#FFD9A0',
  'Healthcare':      '#B8D4A8',
  'Education':       '#B4D4E8',
  'Housing':         '#E8B4B8',
  'Income':          '#10B981',
  'Investments':     '#4F46E5',
};

// ── Global State ─────────────────────────────────────────────────
let _charts = {};
let _calData = {};
let _calYear = new Date().getFullYear();
let _calMonth = new Date().getMonth();
let _monthlyMode = 'stacked';
let _txPage = 1;
let _spendingDataCache = null;

// ── Currency / Number Helpers ────────────────────────────────────
function fmt(n) {
  if (n === undefined || n === null || isNaN(n)) return '₹0';
  return '₹' + Math.round(n).toLocaleString('en-IN');
}
function fmtDec(n) {
  if (n === undefined || n === null || isNaN(n)) return '₹0.00';
  return '₹' + Number(n).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// ── Tab / Section Navigation ─────────────────────────────────────
function switchSection(secId) {
  // Update sidebar active link
  document.querySelectorAll('.sidebar-nav .nav-item[data-section]').forEach(el => {
    el.classList.toggle('active', el.dataset.section === secId);
  });

  // Update visible section
  document.querySelectorAll('.dash-section').forEach(sec => {
    sec.classList.remove('active');
  });
  const target = document.getElementById('section-' + secId);
  if (target) target.classList.add('active');

  // Update top bar title
  const titles = {
    'overview':        { title: 'Spending Overview ✦', sub: 'Cash Flow, Spending Trajectory & Category Analytics' },
    'categories':      { title: 'Expense Categories ◉', sub: 'Deep-Dive Category Distribution & Allocation' },
    'trends':          { title: 'Spending Trends ↗', sub: 'Daily Spending Velocity & Income vs Expense Dynamics' },
    'anomalies':       { title: 'Detected Anomalies ⚡', sub: 'Statistical Gaussian Outlier & High-Variance Spikes' },
    'insights':        { title: 'AI Spending Insights ✦', sub: 'Contextual Cash Flow Heuristics & Spending Patterns' },
    'recommendations': { title: 'Financial Recommendations 🎯', sub: 'Institutional Health Score, 50/30/20 & Emergency Fund Multipliers' },
    'transactions':    { title: 'Transaction Ledger 📜', sub: 'Searchable & Paginated Multi-Bank Statement Ledger' },
  };
  const t = titles[secId] || { title: 'Spending Analytics ✦', sub: 'Bank Statement Intelligence' };
  document.getElementById('pageTitle').textContent = t.title;
  document.getElementById('pageSubText').textContent = t.sub;

  // Trigger chart resizes if needed
  window.dispatchEvent(new Event('resize'));
}

// ── Main Data Loader ─────────────────────────────────────────────
async function loadAllSpendingData() {
  try {
    const [overview, categories, ie, monthly, weekly, trends, anomalies, calendar, health, insights] =
      await Promise.all([
        fetch('/api/overview').then(r => r.json()),
        fetch('/api/categories').then(r => r.json()),
        fetch('/api/income-expense').then(r => r.json()),
        fetch('/api/monthly').then(r => r.json()),
        fetch('/api/weekly').then(r => r.json()),
        fetch('/api/trends').then(r => r.json()),
        fetch('/api/anomalies').then(r => r.json()),
        fetch('/api/calendar').then(r => r.json()),
        fetch('/api/health').then(r => r.json()),
        fetch('/api/insights').then(r => r.json()),
      ]);

    _spendingDataCache = { overview, categories, ie, monthly, weekly, trends, anomalies, calendar, health, insights };

    // 1. Render Topbar Greeting & Date Range
    renderGreeting();
    document.getElementById('topDateSpan').textContent = (overview.start_date || '—') + ' → ' + (overview.end_date || '—');
    document.getElementById('topTxBadge').textContent = (overview.total_transactions || 0) + ' transactions';

    // 2. Render Top 4 KPI Cards
    renderKPIs(overview);

    // 3. Render Overview Charts
    renderCategoriesDonut(categories);
    renderIncomeExpenseGraph(ie);
    renderSessionsMetrics(overview, weekly);
    renderSpendingTrendMini(trends);
    renderMonthlyChart(monthly, _monthlyMode);
    renderWeeklyChart(weekly);

    // 4. Render Deep-Dive Tabs
    renderCategoriesDeepDive(categories);
    renderTrendsFull(trends, ie);
    renderAnomalies(anomalies);
    renderInsights(insights);
    renderHealth(health, insights.tips || []);

    // 5. Render Right Sidebar Components
    renderCalendar(calendar);
    renderRightSidebarAlerts(overview, health, anomalies);

    // 6. Load First Page of Transactions
    loadTransactions(1);

  } catch (err) {
    console.error('Error loading spending analytics:', err);
    showToast('⚠️ Could not load data. Loading sample dataset...');
    await loadSampleData();
  }
}

function renderGreeting() {
  const hour = new Date().getHours();
  let greet = 'Good morning';
  if (hour >= 12 && hour < 17) greet = 'Good afternoon';
  else if (hour >= 17) greet = 'Good evening';
  const el = document.getElementById('greetingText');
  if (el) el.textContent = greet + ' ✦';
}

// ── Top 4 KPI Cards ──────────────────────────────────────────────
function renderKPIs(d) {
  document.getElementById('statIncome').textContent = fmt(d.total_income);
  document.getElementById('statIncomeSub').textContent = `${d.start_date || '—'} to ${d.end_date || '—'}`;

  document.getElementById('statExpenses').textContent = fmt(d.total_expenses);
  document.getElementById('statExpensesSub').textContent = `${d.total_transactions || 0} transactions tracked`;

  document.getElementById('statSavings').textContent = fmt(d.net_savings);
  document.getElementById('statSavingsRate').textContent = `${d.savings_rate || 0}% savings rate`;

  document.getElementById('statSpendingRate').textContent = `${d.spending_rate || 0}%`;
  document.getElementById('statSpendingRateSub').textContent = 'of income spent';
}

// ── Chart Helper ─────────────────────────────────────────────────
function buildChart(id, config) {
  if (_charts[id]) {
    _charts[id].destroy();
  }
  const canvas = document.getElementById(id);
  if (!canvas) return null;
  _charts[id] = new Chart(canvas, config);
  return _charts[id];
}

// ── Donut Chart: Categories ──────────────────────────────────────
function renderCategoriesDonut(d) {
  const topCat = d.labels && d.labels.length ? d.labels[0] : '—';
  document.getElementById('donutTopCat').textContent = topCat;

  const bgColors = d.labels.map((l, i) => CAT_COLORS[l] || COLORS.palette[i % COLORS.palette.length]);

  buildChart('donutChart', {
    type: 'doughnut',
    data: {
      labels: d.labels,
      datasets: [{
        data: d.amounts,
        backgroundColor: bgColors,
        borderWidth: 2,
        borderColor: '#FEFEFE',
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '72%',
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.label}: ₹${Number(ctx.raw).toLocaleString('en-IN')} (${d.percentages[ctx.dataIndex]}%)`
          }
        }
      }
    }
  });

  // Render Legend Pills
  const leg = document.getElementById('catLegend');
  leg.innerHTML = d.labels.map((l, i) => `
    <div class="legend-pill">
      <div class="legend-dot" style="background:${bgColors[i]}"></div>
      <span>${l}</span>
      <strong style="color:var(--ink)">${d.percentages[i]}%</strong>
    </div>
  `).join('');
}

// ── Expenditure Graph: Income vs Expense vs Savings ──────────────
function renderIncomeExpenseGraph(d) {
  buildChart('incomeExpenseChart', {
    type: 'line',
    data: {
      labels: d.months,
      datasets: [
        {
          label: 'Income',
          data: d.income,
          borderColor: '#10B981',
          backgroundColor: 'rgba(16,185,129,0.08)',
          tension: 0.35,
          fill: true,
          pointRadius: 4,
          pointHoverRadius: 6
        },
        {
          label: 'Expense',
          data: d.expense,
          borderColor: COLORS.blush,
          backgroundColor: 'rgba(244,167,185,0.08)',
          tension: 0.35,
          fill: true,
          pointRadius: 4,
          pointHoverRadius: 6
        },
        {
          label: 'Savings',
          data: d.savings,
          borderColor: '#4F46E5',
          borderDash: [5, 5],
          backgroundColor: 'transparent',
          tension: 0.35,
          pointRadius: 3
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'top', labels: { boxWidth: 10, font: { family: 'DM Sans', size: 11 } } },
        tooltip: { callbacks: { label: ctx => ` ${ctx.dataset.label}: ₹${Number(ctx.raw).toLocaleString('en-IN')}` } }
      },
      scales: {
        x: { grid: { display: false }, ticks: { font: { size: 10 } } },
        y: {
          grid: { color: 'rgba(26,26,46,0.05)' },
          ticks: { font: { size: 10 }, callback: v => '₹' + (v >= 1000 ? (v/1000).toFixed(0)+'k' : v) }
        }
      }
    }
  });
}

// ── Sessions & Mini Bar Chart ────────────────────────────────────
function renderSessionsMetrics(overview, weekly) {
  const avgMonth = overview.total_expenses ? overview.total_expenses / 12 : 0;
  document.getElementById('sessAvg').textContent = fmt(avgMonth);

  const minAmt = weekly.amounts && weekly.amounts.length ? Math.min(...weekly.amounts) : 0;
  const maxAmt = weekly.amounts && weekly.amounts.length ? Math.max(...weekly.amounts) : 0;
  document.getElementById('sessMin').textContent = fmt(minAmt);
  document.getElementById('sessMax').textContent = fmt(maxAmt);

  document.getElementById('peakDayBadge').textContent = `Peak: ${weekly.peak_day || 'Saturday'}`;

  // Mini Bar Chart
  buildChart('miniSpendChart', {
    type: 'bar',
    data: {
      labels: weekly.days,
      datasets: [{
        data: weekly.amounts,
        backgroundColor: weekly.days.map(d => d === weekly.peak_day ? '#1A1A2E' : 'rgba(26,26,46,0.25)'),
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: ctx => ` ₹${Number(ctx.raw).toLocaleString('en-IN')}` } } },
      scales: {
        x: { grid: { display: false }, ticks: { font: { size: 9 } } },
        y: { display: false }
      }
    }
  });
}

// ── Spending Trend Mini (Daily) ──────────────────────────────────
function renderSpendingTrendMini(d) {
  buildChart('trendChart', {
    type: 'line',
    data: {
      labels: d.dates,
      datasets: [{
        data: d.amounts,
        borderColor: '#7C3AED',
        backgroundColor: 'rgba(124,58,237,0.08)',
        fill: true,
        tension: 0.35,
        pointRadius: 0,
        pointHoverRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: ctx => ` Spending: ₹${Number(ctx.raw).toLocaleString('en-IN')}` } } },
      scales: {
        x: { grid: { display: false }, ticks: { font: { size: 9 }, maxTicksLimit: 8 } },
        y: {
          grid: { color: 'rgba(26,26,46,0.05)' },
          ticks: { font: { size: 9 }, callback: v => '₹' + (v >= 1000 ? (v/1000).toFixed(0)+'k' : v) }
        }
      }
    }
  });
}

// ── Month-wise Stacked / Line Chart ──────────────────────────────
function switchMonthly(mode) {
  _monthlyMode = mode;
  document.querySelectorAll('.toggle-btn').forEach(b => {
    b.classList.toggle('active', b.textContent.toLowerCase() === mode.toLowerCase());
  });
  if (_spendingDataCache && _spendingDataCache.monthly) {
    renderMonthlyChart(_spendingDataCache.monthly, mode);
  }
}

function renderMonthlyChart(d, mode) {
  const datasets = (d.categories || []).map((cat, i) => ({
    label: cat,
    data: d.matrix ? d.matrix[cat] : [],
    backgroundColor: CAT_COLORS[cat] || COLORS.palette[i % COLORS.palette.length],
    borderColor: CAT_COLORS[cat] || COLORS.palette[i % COLORS.palette.length],
    fill: mode === 'stacked',
    borderRadius: mode === 'stacked' ? 4 : 0,
    tension: 0.3
  }));

  buildChart('monthlyChart', {
    type: mode === 'stacked' ? 'bar' : 'line',
    data: {
      labels: d.months || [],
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'top', labels: { boxWidth: 8, font: { size: 10 } } },
        tooltip: { callbacks: { label: ctx => ` ${ctx.dataset.label}: ₹${Number(ctx.raw).toLocaleString('en-IN')}` } }
      },
      scales: {
        x: { stacked: mode === 'stacked', grid: { display: false }, ticks: { font: { size: 9 } } },
        y: {
          stacked: mode === 'stacked',
          grid: { color: 'rgba(26,26,46,0.05)' },
          ticks: { font: { size: 9 }, callback: v => '₹' + (v >= 1000 ? (v/1000).toFixed(0)+'k' : v) }
        }
      }
    }
  });
}

// ── Week-wise Breakdown Chart ────────────────────────────────────
function renderWeeklyChart(d) {
  buildChart('weeklyChart', {
    type: 'bar',
    data: {
      labels: d.days || [],
      datasets: [{
        data: d.amounts || [],
        backgroundColor: (d.days || []).map(day => day === d.peak_day ? '#0D9488' : '#A8D4D4'),
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` Total: ₹${Number(ctx.raw).toLocaleString('en-IN')}` } }
      },
      scales: {
        x: { grid: { display: false }, ticks: { font: { size: 10 } } },
        y: {
          grid: { color: 'rgba(26,26,46,0.05)' },
          ticks: { font: { size: 10 }, callback: v => '₹' + (v >= 1000 ? (v/1000).toFixed(0)+'k' : v) }
        }
      }
    }
  });
}

// ── Categories Tab: Deep Dive ────────────────────────────────────
function renderCategoriesDeepDive(d) {
  const bgColors = d.labels.map((l, i) => CAT_COLORS[l] || COLORS.palette[i % COLORS.palette.length]);

  // Horizontal Bar Chart
  buildChart('catBarChart', {
    type: 'bar',
    data: {
      labels: d.labels,
      datasets: [{
        data: d.amounts,
        backgroundColor: bgColors,
        borderRadius: 6
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` ₹${Number(ctx.raw).toLocaleString('en-IN')} (${d.percentages[ctx.dataIndex]}%)` } }
      },
      scales: {
        x: { grid: { color: 'rgba(26,26,46,0.05)' }, ticks: { font: { size: 10 }, callback: v => '₹' + (v >= 1000 ? (v/1000).toFixed(0)+'k' : v) } },
        y: { grid: { display: false }, ticks: { font: { size: 11, weight: '600' } } }
      }
    }
  });

  // Table
  const table = document.getElementById('catTable');
  table.innerHTML = d.labels.map((cat, i) => `
    <div class="cat-table-row">
      <div class="cat-color-bar" style="background:${bgColors[i]}"></div>
      <div class="cat-name">${cat}</div>
      <div class="cat-bar-wrap">
        <div class="cat-bar-fill" style="width:${d.percentages[i]}%;background:${bgColors[i]}"></div>
      </div>
      <div class="cat-amount">${fmt(d.amounts[i])}</div>
      <div class="cat-pct">${d.percentages[i]}%</div>
    </div>
  `).join('');
}

// ── Trends Tab: Full View ────────────────────────────────────────
function renderTrendsFull(trends, ie) {
  buildChart('trendChartFull', {
    type: 'line',
    data: {
      labels: trends.dates,
      datasets: [{
        label: 'Daily Outflow',
        data: trends.amounts,
        borderColor: '#7C3AED',
        backgroundColor: 'rgba(124,58,237,0.08)',
        fill: true,
        tension: 0.35,
        pointRadius: 2,
        pointHoverRadius: 5
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: ctx => ` ₹${Number(ctx.raw).toLocaleString('en-IN')}` } } },
      scales: {
        x: { grid: { display: false }, ticks: { font: { size: 10 } } },
        y: { grid: { color: 'rgba(26,26,46,0.05)' }, ticks: { font: { size: 10 }, callback: v => '₹' + (v >= 1000 ? (v/1000).toFixed(0)+'k' : v) } }
      }
    }
  });

  buildChart('ieChartFull', {
    type: 'bar',
    data: {
      labels: ie.months,
      datasets: [
        { label: 'Income', data: ie.income, backgroundColor: '#10B981', borderRadius: 4 },
        { label: 'Expenses', data: ie.expense, backgroundColor: COLORS.blush, borderRadius: 4 },
        { label: 'Net Savings', data: ie.savings, backgroundColor: '#4F46E5', borderRadius: 4 }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'top', labels: { boxWidth: 10 } }, tooltip: { callbacks: { label: ctx => ` ${ctx.dataset.label}: ₹${Number(ctx.raw).toLocaleString('en-IN')}` } } },
      scales: {
        x: { grid: { display: false }, ticks: { font: { size: 10 } } },
        y: { grid: { color: 'rgba(26,26,46,0.05)' }, ticks: { font: { size: 10 }, callback: v => '₹' + (v >= 1000 ? (v/1000).toFixed(0)+'k' : v) } }
      }
    }
  });
}

// ── Anomalies Tab ────────────────────────────────────────────────
function renderAnomalies(d) {
  const list = document.getElementById('anomalyList');
  if (!d.anomalies || !d.anomalies.length) {
    list.innerHTML = `
      <div style="text-align:center;padding:32px;color:var(--muted)">
        <div style="font-size:2rem;margin-bottom:8px">🎉</div>
        <p>No unusual transaction anomalies detected in your spending dataset.</p>
      </div>`;
    return;
  }

  list.innerHTML = d.anomalies.map(a => `
    <div class="anomaly-row">
      <div class="anomaly-cat-dot" style="background:${CAT_COLORS[a.category]||COLORS.blush}"></div>
      <div class="anomaly-desc">
        <div class="anomaly-desc-title">${a.description}</div>
        <div class="anomaly-desc-sub">${a.date} • ${a.category} (Category avg: ₹${Math.round(a.mean||0).toLocaleString('en-IN')})</div>
      </div>
      <div class="anomaly-amount">${fmt(a.amount)}</div>
      <span class="anomaly-badge">Z: +${Number(a.z_score).toFixed(2)}σ</span>
    </div>
  `).join('');
}

// ── AI Insights Tab ──────────────────────────────────────────────
function renderInsights(d) {
  const grid = document.getElementById('insightsGrid');
  if (!d.insights || !d.insights.length) {
    grid.innerHTML = '<p style="color:var(--muted)">No insights generated yet.</p>';
    return;
  }
  grid.innerHTML = d.insights.map(i => `
    <div class="insight-card ${i.type}">
      <div class="insight-icon">${i.icon}</div>
      <div class="insight-text">${i.text}</div>
    </div>
  `).join('');
}

// ── Health Score & Recommendations ──────────────────────────────
function renderHealth(h, tips) {
  document.getElementById('healthBigScore').textContent = h.score;
  document.getElementById('healthBigGrade').textContent = 'Grade ' + h.grade;
  document.getElementById('sidebarScore').textContent = h.score + ' / 100';
  document.getElementById('sidebarGrade').textContent = 'Grade ' + h.grade;

  const bars = [
    { label: 'Savings Rate', val: Math.min(100, (h.savings_rate || 0) * 2), color: COLORS.sage },
    { label: 'Spending Rate Control', val: Math.max(0, 100 - (h.spending_rate || 0)), color: COLORS.blush },
  ];
  document.getElementById('healthBars').innerHTML = bars.map(b => `
    <div class="health-bar-row">
      <div class="health-bar-label"><span>${b.label}</span><span>${b.val.toFixed(0)}%</span></div>
      <div class="health-bar-track"><div class="health-bar-fill" style="width:${b.val}%;background:${b.color}"></div></div>
    </div>
  `).join('');

  // Tips Grid
  const tipsGrid = document.getElementById('tipsGrid');
  tipsGrid.innerHTML = (tips || []).map(t => `
    <div class="tip-card">
      <div class="tip-icon">${t.icon}</div>
      <div class="tip-title">${t.title}</div>
      <div class="tip-text">${t.text}</div>
    </div>
  `).join('');

  // Canvas Health Rings
  drawHealthRing('healthRingSmall', h.score, 32, 7);
  drawHealthRing('healthRingBig', h.score, 68, 14);
}

function drawHealthRing(canvasId, score, radius, lineWidth) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const cx = canvas.width / 2, cy = canvas.height / 2;
  const startAngle = -Math.PI / 2;
  const endAngle = startAngle + (Math.max(0, Math.min(100, score)) / 100) * Math.PI * 2;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Background track
  ctx.beginPath();
  ctx.arc(cx, cy, radius, 0, Math.PI * 2);
  ctx.strokeStyle = 'rgba(255,255,255,0.12)';
  ctx.lineWidth = lineWidth;
  ctx.stroke();

  // Score arc
  const color = score >= 80 ? '#10B981' : score >= 60 ? '#F5E642' : '#F4A7B9';
  ctx.beginPath();
  ctx.arc(cx, cy, radius, startAngle, endAngle);
  ctx.strokeStyle = color;
  ctx.lineWidth = lineWidth;
  ctx.lineCap = 'round';
  ctx.stroke();
}

// ── Calendar Heatmap (Right Sidebar) ─────────────────────────────
function renderCalendar(data) {
  _calData = {};
  if (data && data.dates) {
    data.dates.forEach((d, i) => { _calData[d] = data.amounts[i]; });
  }
  drawCalendar();
}

function drawCalendar() {
  const label = document.getElementById('calMonthLabel');
  const grid = document.getElementById('calGrid');
  if (!label || !grid) return;

  const monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  label.textContent = `${monthNames[_calMonth]} ${_calYear}`;

  const allVals = Object.values(_calData);
  const maxVal = allVals.length ? Math.max(...allVals) : 1;

  const dayLabels = ['Mo','Tu','We','Th','Fr','Sa','Su'];
  let html = dayLabels.map(d => `<div class="cal-day-label">${d}</div>`).join('');

  const first = new Date(_calYear, _calMonth, 1);
  let startDow = first.getDay();
  startDow = startDow === 0 ? 6 : startDow - 1; // Monday-based index

  for (let i = 0; i < startDow; i++) {
    html += '<div class="cal-day"></div>';
  }

  const daysInMonth = new Date(_calYear, _calMonth + 1, 0).getDate();
  const today = new Date();

  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${_calYear}-${String(_calMonth+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
    const amt = _calData[dateStr] || 0;
    const intensity = amt ? Math.max(0.12, Math.min(1.0, amt / maxVal)) : 0;
    const bg = amt ? `rgba(244,167,185,${intensity.toFixed(2)})` : 'rgba(26,26,46,0.04)';
    const isToday = (today.getFullYear() === _calYear && today.getMonth() === _calMonth && today.getDate() === d);
    const tooltip = amt ? `₹${Math.round(amt).toLocaleString('en-IN')}` : '';

    html += `
      <div class="cal-day ${amt?'has-data':''} ${isToday?'today':''}" style="background:${bg}">
        ${d}
        ${tooltip ? `<div class="cal-tooltip">${dateStr}: ${tooltip}</div>` : ''}
      </div>`;
  }

  grid.innerHTML = html;
}

function prevMonth() {
  _calMonth--;
  if (_calMonth < 0) { _calMonth = 11; _calYear--; }
  drawCalendar();
}
function nextMonth() {
  _calMonth++;
  if (_calMonth > 11) { _calMonth = 0; _calYear++; }
  drawCalendar();
}

// ── Right Sidebar Alerts & Savings Wins ──────────────────────────
function renderRightSidebarAlerts(overview, health, anomalies) {
  const alertsEl = document.getElementById('aiAlerts');
  const alerts = [];

  if (health && health.spending_rate > 80) {
    alerts.push({ icon: '⚠️', text: `High burn rate: ${health.spending_rate}% of income spent.` });
  }
  if (anomalies && anomalies.anomalies && anomalies.anomalies.length > 0) {
    alerts.push({ icon: '⚡', text: `${anomalies.anomalies.length} transaction outliers flagged (Z > 2.0).` });
  }
  if (health && health.top_category_pct > 40) {
    alerts.push({ icon: '🔍', text: `${health.top_category} takes ${health.top_category_pct}% of budget.` });
  }
  if (!alerts.length) {
    alerts.push({ icon: '✦', text: 'All clear! Spending patterns within target boundaries.' });
  }

  alertsEl.innerHTML = alerts.map(a => `
    <div class="alert-item"><span class="alert-icon">${a.icon}</span><span>${a.text}</span></div>
  `).join('');

  // Savings Wins
  const winsEl = document.getElementById('savingsWins');
  const wins = [];
  if (overview.savings_rate >= 20) {
    wins.push({ icon: '🎯', text: 'Savings Target Hit', val: overview.savings_rate + '%' });
  }
  if (overview.net_savings > 0) {
    wins.push({ icon: '🌱', text: 'Positive Surplus', val: fmt(overview.net_savings) });
  }
  wins.push({ icon: '📊', text: 'Transactions Tracked', val: overview.total_transactions || 0 });

  winsEl.innerHTML = wins.map(w => `
    <div class="win-item"><span>${w.icon}</span><span>${w.text}</span><span class="win-val">${w.val}</span></div>
  `).join('');
}

// ── Transactions Ledger ──────────────────────────────────────────
async function loadTransactions(page) {
  _txPage = page;
  try {
    const res = await fetch(`/api/transactions?page=${page}`);
    const data = await res.json();

    document.getElementById('txCount').textContent = `${data.total || 0} total records`;

    const list = document.getElementById('txList');
    list.innerHTML = (data.transactions || []).map(tx => `
      <div class="tx-row">
        <div class="tx-dot" style="background:${CAT_COLORS[tx.category] || '#CCC'}"></div>
        <div class="tx-desc">
          <div>${tx.description}</div>
          <div class="tx-cat">${tx.category}</div>
        </div>
        <div class="tx-date">${tx.date}</div>
        <div class="tx-amount ${tx.type}">${tx.type === 'income' ? '+' : '-'}${fmtDec(tx.amount)}</div>
      </div>
    `).join('');

    // Pagination
    const totalPages = Math.ceil((data.total || 1) / 20);
    const pg = document.getElementById('pagination');
    let pgHtml = '';
    if (page > 1) pgHtml += `<button class="pg-btn" onclick="loadTransactions(${page - 1})">← Prev</button>`;
    for (let p = Math.max(1, page - 2); p <= Math.min(totalPages, page + 2); p++) {
      pgHtml += `<button class="pg-btn ${p === page ? 'active' : ''}" onclick="loadTransactions(${p})">${p}</button>`;
    }
    if (page < totalPages) pgHtml += `<button class="pg-btn" onclick="loadTransactions(${page + 1})">Next →</button>`;
    pg.innerHTML = pgHtml;
  } catch (err) {
    console.error('Error loading transactions:', err);
  }
}

// ── Sample Dataset & File Upload Triggers ─────────────────────────
async function loadSampleData() {
  showToast('Loading sample dataset...');
  try {
    const res = await fetch('/api/sample');
    const data = await res.json();
    if (data.success) {
      showToast('✓ Sample dataset loaded!');
      await loadAllSpendingData();
    }
  } catch (err) {
    showToast('⚠️ Failed to load sample data.');
  }
}

function handleCsvUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  const fd = new FormData();
  fd.append('file', file);

  showToast('Uploading CSV statement...');
  fetch('/api/upload', { method: 'POST', body: fd })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        showToast('✓ Statement ingested successfully!');
        loadAllSpendingData();
      } else {
        showToast('⚠️ ' + (data.error || 'Upload failed.'));
      }
    })
    .catch(err => showToast('⚠️ Upload error: ' + err.message));
}

// ── Toast Notification Helper ────────────────────────────────────
function showToast(msg) {
  let toast = document.getElementById('toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast';
    toast.style.cssText = 'position:fixed;bottom:24px;right:24px;background:#1A1A2E;color:#FEFEFE;padding:12px 20px;border-radius:12px;font-size:0.85rem;font-weight:600;z-index:9999;box-shadow:0 8px 24px rgba(0,0,0,0.2);opacity:0;transition:opacity 0.3s;pointer-events:none;';
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.style.opacity = '1';
  setTimeout(() => { toast.style.opacity = '0'; }, 3000);
}

// ── Lifecycle Init ───────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  // Sidebar navigation click listeners
  document.querySelectorAll('.sidebar-nav .nav-item[data-section]').forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      switchSection(item.dataset.section);
    });
  });

  loadAllSpendingData();
});
