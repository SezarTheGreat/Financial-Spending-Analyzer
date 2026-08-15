// ── FinWise Unified Dashboard JS (Mutual Fund & Spending Intelligence) ─────────
const COLORS = {
  blush: '#F4A7B9', butter: '#F5E642', sage: '#B8D4A8',
  lavender: '#C9B8E8', peach: '#FFD9A0', teal: '#A8D4D4',
  ink: '#1A1A2E', muted: '#7A7A9A', white: '#FEFEFE',
  equity: '#5c6bc0', debt: '#26a69a', liquid: '#ffa726',
};

let _charts = {};
let _currentAudit = null;
let _currentRiskProfile = 'Moderate';

const fmt = (n) => '₹' + Number(n || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 });
const fmtDec = (n) => '₹' + Number(n || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 });

function destroyChart(id) {
  if (_charts[id]) { _charts[id].destroy(); delete _charts[id]; }
}

// ── Navigation & Feature Mode Switching ─────────────────────────
document.querySelectorAll('.nav-item[data-section]').forEach(el => {
  el.addEventListener('click', e => {
    e.preventDefault();
    const sec = el.dataset.section;
    switchSection(sec);
  });
});

function switchSection(sec) {
  const isMF = sec.startsWith('mf-');
  const isSpending = sec.startsWith('spending-');

  document.querySelectorAll('.nav-item').forEach(n => {
    n.classList.toggle('active', n.dataset.section === sec);
  });

  document.querySelectorAll('.dash-section').forEach(s => {
    s.classList.toggle('active', s.id === 'section-' + sec);
  });

  const activeNav = document.querySelector(`.nav-item[data-section="${sec}"]`);
  const titleText = activeNav ? activeNav.textContent.replace(/[◈📊⚯✦💳◉↗⚡≡↩]/g, '').trim() : 'Dashboard';
  const pageTitleEl = document.getElementById('pageTitle');
  if (pageTitleEl) pageTitleEl.textContent = titleText + ' ✦';

  const riskSwitcher = document.getElementById('riskSwitcherTop');
  const rightSidebar = document.getElementById('rightSidebar');
  const sidebarHealth = document.getElementById('sidebarHealthContainer');
  const pageSub = document.getElementById('pageSub');

  if (isMF) {
    document.body.classList.remove('spending-mode');
    document.body.classList.add('mf-mode');
    if (riskSwitcher) riskSwitcher.style.display = 'flex';
    if (rightSidebar) rightSidebar.style.display = 'flex';
    if (sidebarHealth) sidebarHealth.style.display = 'block';
    if (pageSub) pageSub.textContent = 'Deterministic Quant Engine & Gemini AI Advisory';
  } else if (isSpending) {
    document.body.classList.remove('mf-mode');
    document.body.classList.add('spending-mode');
    if (riskSwitcher) riskSwitcher.style.display = 'none';
    if (rightSidebar) rightSidebar.style.display = 'none';
    if (sidebarHealth) sidebarHealth.style.display = 'none';
    if (pageSub) pageSub.textContent = 'Bank Statement & Spending Analytics Engine';
  }
}

// ── App Initialization ──────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  document.getElementById('dateBadge').textContent =
    new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });

  // Default to MF view state
  switchSection('mf-overview');

  // 1. Initialize Mutual Fund Portfolio
  await initMutualFundAudit();

  // 2. Initialize Spending Data
  loadSpendingData();
});

// ── Mutual Fund Audit Loader (Live Synchronized) ──────────────────
async function initMutualFundAudit(forceFresh = false) {
  let auditObj = null;
  if (!forceFresh) {
    const cached = sessionStorage.getItem('finwise_portfolio_audit');
    if (cached) {
      try {
        auditObj = JSON.parse(cached);
        // If cached contains outdated >60% XIRR bug or missing holdings, force fresh sync
        if (auditObj && auditObj.quant_diagnostics && auditObj.quant_diagnostics.portfolio_xirr > 60.0) {
          auditObj = null;
        } else if (auditObj) {
          _currentAudit = auditObj;
          renderMutualFundAudit(_currentAudit);
        }
      } catch (e) {
        console.warn('Cached audit parse error:', e);
      }
    }
  }

  // Always sync fresh recalculations from server
  try {
    const auditId = auditObj ? auditObj.audit_id : (_currentAudit ? _currentAudit.audit_id : null);
    const targetProfile = _currentRiskProfile || (auditObj ? auditObj.risk_profile : 'Moderate');
    
    if (auditId && !auditId.startsWith('aud_demo')) {
      const res = await fetch('/api/portfolio/re-evaluate-risk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          audit_id: auditId,
          risk_profile: targetProfile,
        }),
      });
      if (res.ok) {
        _currentAudit = await res.json();
        sessionStorage.setItem('finwise_portfolio_audit', JSON.stringify(_currentAudit));
        renderMutualFundAudit(_currentAudit);
        return;
      }
    }
  } catch (err) {
    console.debug('Background audit sync failed:', err);
  }

  // Fallback to fresh demo portfolio audit
  await fetchDemoAudit(_currentRiskProfile || 'Moderate');
}

async function fetchDemoAudit(riskProfile) {
  try {
    const fd = new FormData();
    fd.append('risk_profile', riskProfile || 'Moderate');
    const res = await fetch('/api/portfolio/analyze-demo', { method: 'POST', body: fd });
    if (res.ok) {
      _currentAudit = await res.json();
      sessionStorage.setItem('finwise_portfolio_audit', JSON.stringify(_currentAudit));
      renderMutualFundAudit(_currentAudit);
    }
  } catch (err) {
    console.error('Failed to load portfolio audit:', err);
  }
}

// ── Change Risk Profile Dynamically ─────────────────────────────
async function changeRiskProfile(profile) {
  _currentRiskProfile = profile;
  ['Conservative', 'Moderate', 'Aggressive'].forEach(p => {
    const btn = document.getElementById('risk-btn-' + p);
    if (btn) btn.classList.toggle('active', p === profile);
  });

  showToast(`✦ Re-evaluating diagnostics for ${profile} risk profile…`);

  try {
    const auditId = _currentAudit ? _currentAudit.audit_id : null;
    const res = await fetch('/api/portfolio/re-evaluate-risk', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        audit_id: auditId,
        risk_profile: profile,
      }),
    });

    if (res.ok) {
      _currentAudit = await res.json();
      sessionStorage.setItem('finwise_portfolio_audit', JSON.stringify(_currentAudit));
      renderMutualFundAudit(_currentAudit);
      showToast(`✓ Rebalanced recommendations for ${profile} profile.`);
    }
  } catch (err) {
    showToast('⚠️ Failed to re-evaluate risk profile.');
  }
}

// ── Render Complete Mutual Fund Dashboard ────────────────────────
function renderMutualFundAudit(audit) {
  if (!audit) return;

  const summary = audit.portfolio_summary || {};
  const quant = audit.quant_diagnostics || {};
  const ai = audit.ai_insights || {};
  const holdings = summary.holdings || [];

  _currentRiskProfile = audit.risk_profile || 'Moderate';
  ['Conservative', 'Moderate', 'Aggressive'].forEach(p => {
    const btn = document.getElementById('risk-btn-' + p);
    if (btn) btn.classList.toggle('active', p === _currentRiskProfile);
  });

  // Top Stat Cards
  document.getElementById('mfValTotal').textContent = fmt(summary.total_current_value);
  document.getElementById('mfValCost').textContent = `Invested: ${fmt(summary.total_cost_value)}`;
  document.getElementById('mfValGain').textContent = fmt(summary.total_gain);
  
  const returnPct = summary.total_cost_value > 0 ? ((summary.total_gain / summary.total_cost_value) * 100).toFixed(2) : '0.00';
  document.getElementById('mfValGainPct').textContent = `Total Return: +${returnPct}%`;

  const xirrVal = quant.portfolio_xirr;
  document.getElementById('mfValXIRR').textContent = xirrVal ? `${xirrVal.toFixed(2)}% p.a.` : `${returnPct}% p.a.`;

  const directCount = holdings.filter(h => h.plan_type === 'DIRECT').length;
  const regularCount = holdings.filter(h => h.plan_type === 'REGULAR').length;
  document.getElementById('mfValHoldingsCount').textContent = `${holdings.length} Funds`;
  document.getElementById('mfValPlanBreakdown').textContent = `${directCount} Direct · ${regularCount} Regular`;

  // 1. Health Score Gauge
  renderHealthGauge(ai.health_score || 85);

  // 2. Asset Allocation & Drift
  renderAssetAllocation(quant.asset_allocation, quant.asset_drift);

  // 3. Distributor Cost Drag
  renderCostDrag(quant.cost_drag);

  // 4. Key Alerts Preview & Roadmap
  renderOverviewAlerts(ai.key_alerts || []);
  renderOverviewActions(ai.fund_recommendations || []);

  // 5. Holdings & Form Table
  renderHoldingsTable(holdings, quant.rolling_cagrs || [], quant.form_ratings || []);

  // 6. Overlap Matrix & Spatial Flower Venn
  renderOverlapMatrix(quant.overlap_matrix || {}, holdings);

  // 7. Full AI Advisory & Checklist
  renderAIAdvisory(ai);

  // 8. Right Sidebar Stats
  renderRightSidebar(summary, quant, ai);
}

// ── Circular Health Score Gauge ──────────────────────────────────
function renderHealthGauge(score) {
  const numEl = document.getElementById('gaugeScoreNum');
  if (numEl) numEl.textContent = score;

  const titleEl = document.getElementById('gaugeStatusTitle');
  const badgeEl = document.getElementById('healthScoreBadge');
  const sideScore = document.getElementById('sidebarHealthScore');
  const sideStatus = document.getElementById('sidebarHealthStatus');

  let grade = 'Excellent';
  let color = '#2e7d32';
  if (score >= 80) { grade = 'Grade A (Optimal)'; color = '#2e7d32'; }
  else if (score >= 65) { grade = 'Grade B (Solid)'; color = '#1565c0'; }
  else if (score >= 50) { grade = 'Grade C (Moderate Risk)'; color = '#ef6c00'; }
  else { grade = 'Grade D (Critical Drag)'; color = '#c62828'; }

  if (titleEl) titleEl.textContent = grade;
  if (badgeEl) badgeEl.textContent = `${score}/100 Score`;
  if (sideScore) sideScore.textContent = score;
  if (sideStatus) sideStatus.textContent = score >= 80 ? 'Optimal (Grade A)' : score >= 65 ? 'Solid (Grade B)' : score >= 50 ? 'Moderate (Grade C)' : 'At Risk (Grade D)';

  // Draw main gauge canvas
  drawDonutRing('gaugeCanvas', score, 100, color, '#f0ede6');
  drawDonutRing('healthRingSidebar', score, 100, color, 'rgba(255,255,255,0.15)');
}

function drawDonutRing(canvasId, value, max, fgColor, bgColor) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  
  const isSidebar = canvasId === 'healthRingSidebar';
  const logicalW = isSidebar ? 80 : 120;
  const logicalH = isSidebar ? 80 : 120;
  const dpr = window.devicePixelRatio || 1;

  canvas.width = logicalW * dpr;
  canvas.height = logicalH * dpr;
  canvas.style.width = logicalW + 'px';
  canvas.style.height = logicalH + 'px';
  
  ctx.save();
  ctx.scale(dpr, dpr);
  ctx.clearRect(0, 0, logicalW, logicalH);

  const cx = logicalW / 2;
  const cy = logicalH / 2;
  const strokeW = isSidebar ? 7 : 10;
  const radius = cx - strokeW / 2 - 2;

  // Background Ring
  ctx.beginPath();
  ctx.arc(cx, cy, radius, 0, 2 * Math.PI);
  ctx.strokeStyle = bgColor;
  ctx.lineWidth = strokeW;
  ctx.stroke();

  // Progress Ring
  const pct = Math.min(Math.max(value / max, 0), 1);
  const startAngle = -Math.PI / 2;
  const endAngle = startAngle + (2 * Math.PI * pct);

  ctx.beginPath();
  ctx.arc(cx, cy, radius, startAngle, endAngle);
  ctx.strokeStyle = fgColor;
  ctx.lineWidth = strokeW;
  ctx.lineCap = 'round';
  ctx.stroke();

  ctx.restore();
}

// ── Asset Allocation & Drift ─────────────────────────────────────
function renderAssetAllocation(alloc, drift) {
  if (!alloc) return;

  const eqPct = alloc.equity_pct || 0;
  const debtPct = alloc.debt_pct || 0;
  const commPct = alloc.commodities_pct || 0;
  const liqPct = alloc.cash_liquid_pct || 0;

  const barEq = document.getElementById('allocBarEquity');
  const barDebt = document.getElementById('allocBarDebt');
  const barComm = document.getElementById('allocBarCommodities');
  const barLiq = document.getElementById('allocBarLiquid');

  if (barEq) barEq.style.width = eqPct + '%';
  if (barDebt) barDebt.style.width = debtPct + '%';
  if (barComm) barComm.style.width = commPct + '%';
  if (barLiq) barLiq.style.width = liqPct + '%';

  const pctEq = document.getElementById('allocPctEquity');
  const pctDebt = document.getElementById('allocPctDebt');
  const pctComm = document.getElementById('allocPctCommodities');
  const pctLiq = document.getElementById('allocPctLiquid');

  if (pctEq) pctEq.textContent = eqPct.toFixed(2) + '%';
  if (pctDebt) pctDebt.textContent = debtPct.toFixed(2) + '%';
  if (pctComm) pctComm.textContent = commPct.toFixed(2) + '%';
  if (pctLiq) pctLiq.textContent = liqPct.toFixed(2) + '%';

  if (drift) {
    const badge = document.getElementById('driftStatusBadge');
    if (badge) {
      badge.textContent = drift.drift_status;
      badge.className = 'card-badge';
      if (drift.drift_status === 'Aligned') badge.classList.add('badge-glow');
      else if (drift.drift_status === 'High Risk Drift') badge.classList.add('badge-warning');
    }

    const profName = document.getElementById('driftProfileName');
    const targetR = document.getElementById('driftTargetRange');
    const recTxt = document.getElementById('driftRecText');

    if (profName) profName.textContent = drift.risk_profile;
    if (targetR) targetR.textContent = `${drift.target_equity_range[0]}%–${drift.target_equity_range[1]}%`;
    if (recTxt) recTxt.textContent = drift.recommendation;
  }
}

// ── Distributor Cost Drag ─────────────────────────────────────────
function renderCostDrag(costDrag) {
  if (!costDrag) return;

  document.getElementById('dragRegularCorpus').textContent = fmt(costDrag.total_regular_corpus);
  document.getElementById('dragAnnualAmount').textContent = `~${fmt(costDrag.annual_expense_drag_amount)} / year`;
  document.getElementById('drag10YrLoss').textContent = fmt(costDrag.projected_10yr_cost_drag);
  document.getElementById('drag10YrDirectComparison').textContent =
    `Direct plan projection: ${fmt(costDrag.projected_10yr_direct_value)} vs Regular: ${fmt(costDrag.projected_10yr_regular_value)}`;

  const badge = document.getElementById('costDragBadge');
  if (costDrag.affected_schemes_count === 0) {
    badge.textContent = '0 Regular Plans (0% Leakage)';
    badge.className = 'card-badge badge-glow';
  } else {
    badge.textContent = `${costDrag.affected_schemes_count} Regular Plans (${costDrag.annual_expense_drag_percentage}% p.a. Drag)`;
    badge.className = 'card-badge badge-warning';
  }
}

// ── Overview Alerts & Actions ─────────────────────────────────────
function renderOverviewAlerts(alerts) {
  const container = document.getElementById('overviewAlertsContainer');
  if (!container) return;

  if (!alerts || alerts.length === 0) {
    container.innerHTML = '<div class="alert-card alert-low"><div class="alert-title">✓ No critical anomalies detected</div></div>';
    return;
  }

  container.innerHTML = alerts.slice(0, 3).map(a => {
    const sev = (a.severity || 'LOW').toLowerCase();
    return `
      <div class="alert-card alert-${sev}">
        <div class="alert-top">
          <div class="alert-title">${a.title}</div>
          <span class="alert-tag tag-${sev}">${a.severity}</span>
        </div>
        <div class="alert-body">${a.description}</div>
      </div>
    `;
  }).join('');
}

function renderOverviewActions(actions) {
  const container = document.getElementById('overviewActionsList');
  if (!container) return;

  if (!actions || actions.length === 0) {
    container.innerHTML = '<div class="action-card"><div class="action-scheme">All holdings optimal.</div></div>';
    return;
  }

  container.innerHTML = actions.slice(0, 3).map(act => `
    <div class="action-card">
      <div class="action-header">
        <span class="action-scheme">${act.scheme_name}</span>
        <span class="action-badge badge-${act.action}">${act.action.replace(/_/g, ' ')}</span>
      </div>
      <div class="action-rationale">${act.rationale}</div>
      ${act.target_alternative ? `<div class="action-target">↳ Alternative: ${act.target_alternative}</div>` : ''}
    </div>
  `).join('');
}

// ── Holdings & 4-Tier Form Table ──────────────────────────────────
function renderHoldingsTable(holdings, rollingCagrs, formRatings) {
  const tbody = document.getElementById('mfHoldingsTableBody');
  const rationalesGrid = document.getElementById('formRationalesGrid');
  if (!tbody) return;

  const cagrMap = {};
  rollingCagrs.forEach(rc => { cagrMap[rc.scheme_name] = rc; });

  const formMap = {};
  formRatings.forEach(fr => { formMap[fr.scheme_name] = fr; });

  tbody.innerHTML = holdings.map(h => {
    const rc = cagrMap[h.scheme_name] || {};
    const fr = formMap[h.scheme_name] || {};
    const tier = fr.form_tier || 'On-Track';
    const tierClass = 'form-' + tier.toLowerCase().replace(/\s+/g, '-');

    const cagr1 = rc.cagr_1y !== null && rc.cagr_1y !== undefined ? `${rc.cagr_1y}%` : '–';
    const cagr3 = rc.cagr_3y !== null && rc.cagr_3y !== undefined ? `${rc.cagr_3y}%` : '–';
    const alpha1 = rc.alpha_1y !== null && rc.alpha_1y !== undefined ? (rc.alpha_1y >= 0 ? `+${rc.alpha_1y}%` : `${rc.alpha_1y}%`) : '–';
    const fundXirr = rc.xirr ? `${rc.xirr.toFixed(2)}%` : (h.return_percentage ? `${h.return_percentage}%` : '–');
    const weightPct = (h.portfolio_weight_pct !== undefined && h.portfolio_weight_pct !== null && h.portfolio_weight_pct > 0)
      ? `${h.portfolio_weight_pct.toFixed(2)}%`
      : (rc.portfolio_weight_pct ? `${rc.portfolio_weight_pct.toFixed(2)}%` : '–');

    return `
      <tr>
        <td>
          <strong>${h.scheme_name}</strong>
          <div style="font-size:0.68rem;color:var(--muted)">Folio: ${h.folio_number || '–'}</div>
        </td>
        <td>${h.category || 'Equity'}</td>
        <td>
          <span class="plan-tag ${h.plan_type === 'DIRECT' ? 'plan-direct' : 'plan-regular'}">
            ${h.plan_type}
          </span>
        </td>
        <td>${fmt(h.cost_value)}</td>
        <td><strong>${fmt(h.current_value)}</strong></td>
        <td><span style="font-weight:700;color:var(--ink);background:var(--cream);padding:2px 8px;border-radius:6px;">${weightPct}</span></td>
        <td class="text-success">+${h.return_percentage}%</td>
        <td><strong>${fundXirr}</strong></td>
        <td>${cagr1} / ${cagr3}</td>
        <td>${alpha1}</td>
        <td>
          <span class="form-badge ${tierClass}">
            ${tier === 'In-Form' ? '🟢' : tier === 'On-Track' ? '🟡' : tier === 'Off-Track' ? '🟠' : '🔴'} ${tier}
          </span>
        </td>
      </tr>
    `;
  }).join('');

  if (rationalesGrid) {
    rationalesGrid.innerHTML = formRatings.map(fr => {
      const tierClass = 'form-' + (fr.form_tier || 'on-track').toLowerCase().replace(/\s+/g, '-');
      return `
        <div class="form-rat-card">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <strong>${fr.scheme_name}</strong>
            <span class="form-badge ${tierClass}">${fr.form_tier}</span>
          </div>
          <p style="font-size:0.75rem;color:var(--ink2);margin-top:4px;">${fr.rationale}</p>
        </div>
      `;
    }).join('');
  }
}

// ── Overlap Matrix & Spatial Flower Venn Studio ───────────────────
let _globalOverlapData = null;
let _globalHoldingsData = null;

function renderOverlapMatrix(overlap, holdings = []) {
  _globalOverlapData = overlap || {};
  _globalHoldingsData = holdings || [];

  initOverlapTabSwitchers();
  renderSpatialFlowerVenn(_globalOverlapData, _globalHoldingsData);
  renderPairwiseVennSimulator(_globalOverlapData);
  renderCrossFundStockExplorer(_globalOverlapData);
  renderOverlapSummaryCards(_globalOverlapData.pairs || []);

  const badge = document.getElementById('overlapSummaryBadge');
  const highPairs = _globalOverlapData.high_overlap_pairs || [];
  if (badge) {
    badge.textContent = highPairs.length > 0 
      ? `${highPairs.length} High-Overlap Pairs (≥30%)` 
      : `Diversified (${(_globalOverlapData.pairs || []).length} Pairs Analyzed)`;
  }
}

function initOverlapTabSwitchers() {
  const tabBtns = document.querySelectorAll('.overlap-tab-btn');
  tabBtns.forEach(btn => {
    btn.onclick = () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.overlap-panel').forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const targetTab = btn.dataset.tab;
      const targetPanel = document.getElementById(`overlap-panel-${targetTab}`);
      if (targetPanel) targetPanel.classList.add('active');

      if (targetTab === 'spatial-flower' && _globalOverlapData) {
        renderSpatialFlowerVenn(_globalOverlapData, _globalHoldingsData);
      }
    };
  });
}

// 🌸 1. SPATIAL FLOWER VENN TOPOLOGY
function renderSpatialFlowerVenn(overlap, holdings) {
  const svgEl = document.getElementById('spatialFlowerSvg');
  if (!svgEl) return;

  const pairs = overlap.pairs || [];
  const holdingsMap = overlap.fund_holdings_map || {};
  const fundNames = Object.keys(holdingsMap);

  if (fundNames.length === 0) {
    svgEl.innerHTML = '<text x="425" y="230" text-anchor="middle" fill="#6B7280" font-size="14">No multiple equity funds available for spatial Venn mapping.</text>';
    return;
  }

  const width = 850;
  const height = 460;
  const cx = width / 2;
  const cy = height / 2;
  const R = 155; // Radius of orbital flower ring

  const colors = [
    '#4F46E5', '#059669', '#D97706', '#0284C7', '#7C3AED',
    '#DB2777', '#2563EB', '#0D9488', '#EA580C', '#64748B'
  ];

  // Calculate node positions around a celestial flower ring
  const nodes = fundNames.map((name, i) => {
    const angle = (2 * Math.PI * i) / fundNames.length - Math.PI / 2;
    const x = cx + R * Math.cos(angle);
    const y = cy + R * Math.sin(angle);
    const cleanName = name.replace(/Fund.*$/i, '').replace(/-.*$/i, '').trim();
    return {
      id: name,
      shortName: cleanName.length > 22 ? cleanName.substring(0, 20) + '…' : cleanName,
      fullName: name,
      x,
      y,
      angle,
      color: colors[i % colors.length]
    };
  });

  const nodeMap = new Map(nodes.map(n => [n.id, n]));

  // Build SVG content
  let svgHtml = `
    <defs>
      <filter id="flowerGlow" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="4" result="blur" />
        <feComposite in="SourceGraphic" in2="blur" operator="over" />
      </filter>
      <radialGradient id="flowerCenterGlow" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#4F46E5" stop-opacity="0.12"/>
        <stop offset="100%" stop-color="#4F46E5" stop-opacity="0"/>
      </radialGradient>
    </defs>
    <!-- Central Core Ambient Ring -->
    <circle cx="${cx}" cy="${cy}" r="${R + 35}" fill="none" stroke="rgba(17,24,39,0.06)" stroke-width="1.5" stroke-dasharray="4,6" />
    <circle cx="${cx}" cy="${cy}" r="${R - 35}" fill="url(#flowerCenterGlow)" />
  `;

  // Draw connecting overlap chords & text directly on the line using textPath
  pairs.forEach((p, idx) => {
    const na = nodeMap.get(p.fund_a);
    const nb = nodeMap.get(p.fund_b);
    if (!na || !nb) return;

    const pct = p.overlap_percentage || 0;
    if (pct <= 0) return;

    const strokeColor = pct >= 25 ? '#DC2626' : pct >= 10 ? '#D97706' : '#059669';
    const strokeWidth = Math.max(2.5, Math.min(8, pct * 0.4));
    const opacity = Math.max(0.4, Math.min(0.85, pct / 25));

    // Calculate curved bezier chord through midpoint with gentle curvature
    const mx = (na.x + nb.x) / 2;
    const my = (na.y + nb.y) / 2;
    const pull = 0.25; // Gentle pull so chord curves cleanly around the center
    const ctrlX = mx * (1 - pull) + cx * pull;
    const ctrlY = my * (1 - pull) + cy * pull;

    // Ensure path direction is consistent (left to right) so textPath renders upright
    let startNode = na;
    let endNode = nb;
    if (na.x > nb.x) {
      startNode = nb;
      endNode = na;
    }

    const pathId = `flower-chord-path-${idx}-${sanitizeId(p.fund_a).substring(0,6)}-${sanitizeId(p.fund_b).substring(0,6)}`;
    const pathData = `M ${startNode.x} ${startNode.y} Q ${ctrlX} ${ctrlY} ${endNode.x} ${endNode.y}`;

    svgHtml += `
      <path id="${pathId}"
            class="flower-chord chord-${sanitizeId(p.fund_a)} chord-${sanitizeId(p.fund_b)}"
            d="${pathData}"
            fill="none"
            stroke="${strokeColor}"
            stroke-width="${strokeWidth}"
            stroke-opacity="${opacity}"
            stroke-linecap="round"
            data-a="${p.fund_a}"
            data-b="${p.fund_b}"
            data-pct="${pct}" />
      
      <!-- Overlap Text Riding on the Outer Clear Section of the Line (30% offset from node) -->
      <text class="chord-line-text chord-${sanitizeId(p.fund_a)} chord-${sanitizeId(p.fund_b)}"
            dy="-4"
            font-size="10"
            font-weight="800"
            style="pointer-events:none;">
        <textPath href="#${pathId}" startOffset="30%" text-anchor="middle"
                  stroke="#FFFFFF" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">
          ${pct}%
        </textPath>
        <textPath href="#${pathId}" startOffset="30%" text-anchor="middle" fill="${strokeColor}">
          ${pct}%
        </textPath>
      </text>
    `;
  });

  // Central Core Hub (Rendered on top of chords for clean occlusion)
  svgHtml += `
    <circle cx="${cx}" cy="${cy}" r="34" fill="#FFFFFF" stroke="rgba(17,24,39,0.12)" stroke-width="2" />
    <text x="${cx}" y="${cy + 4}" text-anchor="middle" font-size="11" font-weight="800" fill="#111827" letter-spacing="1">PORTFOLIO</text>
  `;

  // Draw Fund Petal Nodes with Clean Outer Radial Label Placement
  nodes.forEach(n => {
    const petalW = 40;
    const petalH = 64;
    const rot = (n.angle * 180) / Math.PI + 90;

    const cosA = Math.cos(n.angle);
    const sinA = Math.sin(n.angle);

    // Position outer label beyond petal boundary
    const labelDist = 58;
    const lx = cosA * labelDist;
    const ly = sinA * labelDist;

    let textAnchor = "middle";
    let dyOffset = 4;
    if (cosA > 0.3) {
      textAnchor = "start";
      dyOffset = 4;
    } else if (cosA < -0.3) {
      textAnchor = "end";
      dyOffset = 4;
    } else if (sinA < -0.6) {
      textAnchor = "middle";
      dyOffset = -8;
    } else if (sinA > 0.6) {
      textAnchor = "middle";
      dyOffset = 14;
    }

    svgHtml += `
      <g class="flower-petal-node" data-id="${n.id}" style="cursor:pointer;" transform="translate(${n.x}, ${n.y})">
        <!-- Outward Petal Shape -->
        <ellipse cx="0" cy="0" rx="${petalW / 2}" ry="${petalH / 2}"
                 transform="rotate(${rot})"
                 fill="${n.color}"
                 fill-opacity="0.18"
                 stroke="${n.color}"
                 stroke-width="2.5" />
        
        <!-- Core Node Circle -->
        <circle cx="0" cy="0" r="18" fill="#FFFFFF" stroke="${n.color}" stroke-width="3" />
        <circle cx="0" cy="0" r="13" fill="${n.color}" />
        <text x="0" y="3.5" text-anchor="middle" font-size="10" font-weight="800" fill="#FFFFFF">MF</text>
        
        <!-- Clean Fund Label Placed Safely Outside Petal -->
        <text x="${lx}" y="${ly + dyOffset}"
              text-anchor="${textAnchor}"
              font-size="11"
              font-weight="700"
              fill="#111827"
              stroke="#FFFFFF"
              stroke-width="3"
              style="paint-order: stroke fill; stroke-linejoin: round;">
          ${n.shortName}
        </text>
      </g>
    `;
  });

  svgEl.innerHTML = svgHtml;

  // Attach Interactive Event Handlers
  const tooltip = document.getElementById('flowerTooltip');
  const detailsBar = document.getElementById('flowerBarTitle');
  const tagsContainer = document.getElementById('flowerSelectedTags');

  document.querySelectorAll('.flower-petal-node').forEach(nodeEl => {
    const fundId = nodeEl.dataset.id;
    const nodeObj = nodeMap.get(fundId);

    nodeEl.onmouseenter = (e) => {
      highlightFundPetal(fundId);
      if (tooltip && nodeObj) {
        const relatedPairs = pairs.filter(p => p.fund_a === fundId || p.fund_b === fundId);
        const topOverlap = relatedPairs.sort((a, b) => b.overlap_percentage - a.overlap_percentage)[0];
        
        tooltip.innerHTML = `
          <strong style="color:${nodeObj.color};">${nodeObj.fullName}</strong>
          <div style="margin-top:4px;font-size:0.7rem;color:#D1D5DB;">
            ${relatedPairs.length} Overlapping Links · Max Overlap: <strong>${topOverlap ? topOverlap.overlap_percentage : 0}%</strong>
          </div>
        `;
        tooltip.style.opacity = '1';
        positionTooltip(e, tooltip);
      }
    };

    nodeEl.onmousemove = (e) => positionTooltip(e, tooltip);

    nodeEl.onmouseleave = () => {
      resetFlowerHighlights();
      if (tooltip) tooltip.style.opacity = '0';
    };

    nodeEl.onclick = () => {
      selectFundForInspection(fundId, nodeObj, pairs, detailsBar, tagsContainer);
    };
  });
}

function sanitizeId(str) {
  return (str || '').replace(/[^a-zA-Z0-9]/g, '_');
}

function positionTooltip(e, tooltip) {
  if (!tooltip) return;
  const wrap = document.querySelector('.spatial-flower-canvas-wrap');
  if (!wrap) return;
  const rect = wrap.getBoundingClientRect();
  const x = e.clientX - rect.left + 15;
  const y = e.clientY - rect.top + 15;
  tooltip.style.left = `${x}px`;
  tooltip.style.top = `${y}px`;
}

function highlightFundPetal(fundId) {
  const safeId = sanitizeId(fundId);
  document.querySelectorAll('.flower-chord').forEach(chord => {
    chord.style.strokeOpacity = chord.classList.contains(`chord-${safeId}`) ? '1' : '0.08';
    chord.style.strokeWidth = chord.classList.contains(`chord-${safeId}`) ? '4' : '1.5';
  });
  document.querySelectorAll('.chord-line-text').forEach(txt => {
    txt.style.opacity = txt.classList.contains(`chord-${safeId}`) ? '1' : '0.1';
  });
  document.querySelectorAll('.flower-petal-node').forEach(node => {
    node.style.opacity = node.dataset.id === fundId ? '1' : '0.35';
  });
}

function resetFlowerHighlights() {
  document.querySelectorAll('.flower-chord').forEach(chord => {
    const pct = parseFloat(chord.dataset.pct || 0);
    chord.style.strokeOpacity = Math.max(0.4, Math.min(0.85, pct / 25));
    chord.style.strokeWidth = Math.max(2.5, Math.min(8, pct * 0.4));
  });
  document.querySelectorAll('.chord-line-text').forEach(txt => {
    txt.style.opacity = '1';
  });
  document.querySelectorAll('.flower-petal-node').forEach(node => {
    node.style.opacity = '1';
  });
}

function selectFundForInspection(fundId, nodeObj, pairs, barTitle, tagsContainer) {
  const related = pairs.filter(p => p.fund_a === fundId || p.fund_b === fundId);
  if (barTitle) {
    barTitle.innerHTML = `Connected Overlap Links for: <strong style="color:${nodeObj.color}">${nodeObj.fullName}</strong>`;
  }
  if (tagsContainer) {
    if (related.length === 0) {
      tagsContainer.innerHTML = '<span class="flower-tag-chip">No common equity overlap with other schemes.</span>';
      return;
    }
    tagsContainer.innerHTML = related.map(p => {
      const otherFund = p.fund_a === fundId ? p.fund_b : p.fund_a;
      return `
        <span class="flower-tag-chip" style="cursor:pointer;" onclick="switchPairwiseSelect('${fundId}', '${otherFund}')">
          <span>⚯ <strong>${otherFund}</strong>:</span>
          <span style="color:#0284C7;font-weight:700;">${p.overlap_percentage}%</span>
          <small style="color:var(--muted)">(${p.common_holdings.length} stocks)</small>
        </span>
      `;
    }).join('');
  }
}

// ⚯ 2. DYNAMIC PAIRWISE VENN SIMULATOR
function renderPairwiseVennSimulator(overlap) {
  const selectA = document.getElementById('fundSelectA');
  const selectB = document.getElementById('fundSelectB');
  if (!selectA || !selectB) return;

  const holdingsMap = overlap.fund_holdings_map || {};
  const fundNames = Object.keys(holdingsMap);

  if (fundNames.length < 2) {
    selectA.innerHTML = '<option>Not enough funds</option>';
    selectB.innerHTML = '<option>Not enough funds</option>';
    return;
  }

  selectA.innerHTML = fundNames.map(f => `<option value="${f}">${f}</option>`).join('');
  selectB.innerHTML = fundNames.map(f => `<option value="${f}">${f}</option>`).join('');

  // Default selection to prominent pair (e.g. Nippon India Growth vs Parag Parikh Flexi)
  const defaultA = fundNames.find(f => f.toUpperCase().includes('NIPPON') || f.toUpperCase().includes('QUANT')) || fundNames[0];
  const defaultB = fundNames.find(f => f.toUpperCase().includes('PARAG PARIKH')) || fundNames[1];

  selectA.value = defaultA;
  selectB.value = defaultB;

  const updatePairwiseView = () => {
    const fa = selectA.value;
    const fb = selectB.value;
    updatePairwiseVennDisplay(fa, fb, overlap);
  };

  selectA.onchange = updatePairwiseView;
  selectB.onchange = updatePairwiseView;

  // Search filter for common stocks
  const searchInput = document.getElementById('commonStocksSearch');
  if (searchInput) {
    searchInput.oninput = () => {
      const q = searchInput.value.toLowerCase().trim();
      document.querySelectorAll('#commonStocksTableBody tr').forEach(tr => {
        const txt = tr.textContent.toLowerCase();
        tr.style.display = txt.includes(q) ? '' : 'none';
      });
    };
  }

  updatePairwiseView();
}

function updatePairwiseVennDisplay(fundA, fundB, overlap) {
  const pairs = overlap.pairs || [];
  const holdingsMap = overlap.fund_holdings_map || {};

  let pair = pairs.find(p => 
    (p.fund_a === fundA && p.fund_b === fundB) || 
    (p.fund_a === fundB && p.fund_b === fundA)
  );

  let overlapPct = 0.0;
  let breakdown = [];
  let verdict = 'Good Diversification';
  let level = 'Low Overlap';

  if (fundA === fundB) {
    overlapPct = 100.0;
    level = 'Identical Scheme';
    verdict = '100% complete duplication (Same Scheme Selected).';
    const fundHoldings = holdingsMap[fundA] || [];
    breakdown = fundHoldings.map(h => ({
      stock_name: h.stock_name,
      weight_in_a: h.weight,
      weight_in_b: h.weight,
      overlap_contribution: h.weight
    }));
  } else if (pair) {
    overlapPct = pair.overlap_percentage;
    breakdown = pair.common_stocks_breakdown || [];
    verdict = pair.diversification_verdict || 'Good Diversification';
    level = pair.overlap_level || 'Low Overlap';
  } else {
    // Dynamic calculate if not in precomputed pairs
    const wa = Object.fromEntries((holdingsMap[fundA] || []).map(h => [h.stock_name, h.weight]));
    const wb = Object.fromEntries((holdingsMap[fundB] || []).map(h => [h.stock_name, h.weight]));
    const common = Object.keys(wa).filter(k => wb.hasOwnProperty(k));

    common.forEach(k => {
      const c = Math.min(wa[k], wb[k]);
      overlapPct += c;
      breakdown.push({
        stock_name: k,
        weight_in_a: wa[k],
        weight_in_b: wb[k],
        overlap_contribution: c
      });
    });
    overlapPct = Math.round(overlapPct * 100) / 100;
    breakdown.sort((a, b) => b.overlap_contribution - a.overlap_contribution);
  }

  // 1. Draw SVG Overlapping Venn Circles
  drawPairwiseVennSvg(fundA, fundB, overlapPct);

  // 2. Update Hero Numbers & Badges
  const numEl = document.getElementById('vennOverlapNumber');
  const lvlBadge = document.getElementById('vennOverlapLvlBadge');
  const divBadge = document.getElementById('vennDiversificationBadge');
  const diagText = document.getElementById('vennDiagnosisText');

  if (numEl) numEl.textContent = `${overlapPct.toFixed(2)}% Overlap`;
  if (lvlBadge) {
    lvlBadge.textContent = level;
    lvlBadge.className = `venn-pill-badge ${overlapPct >= 30 ? 'badge-concentration' : 'badge-overlap-lvl'}`;
  }
  if (divBadge) {
    divBadge.textContent = verdict.includes('Good') ? 'Good Diversification' : 'Concentration Alert';
    divBadge.className = `venn-pill-badge ${verdict.includes('Good') ? 'badge-diversification' : 'badge-concentration'}`;
  }
  if (diagText) diagText.textContent = verdict;

  // 3. Render Common Stocks Table
  const tableBody = document.getElementById('commonStocksTableBody');
  const countEl = document.getElementById('commonStocksCount');
  const hdrA = document.getElementById('hdrFundAWeight');
  const hdrB = document.getElementById('hdrFundBWeight');

  if (countEl) countEl.textContent = breakdown.length;
  if (hdrA) hdrA.textContent = `% in ${fundA.substring(0, 18)}…`;
  if (hdrB) hdrB.textContent = `% in ${fundB.substring(0, 18)}…`;

  if (tableBody) {
    if (breakdown.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--muted);padding:24px;">No common stock holdings detected between these two funds.</td></tr>';
    } else {
      tableBody.innerHTML = breakdown.map(st => `
        <tr>
          <td><strong>${st.stock_name}</strong></td>
          <td>${st.weight_in_a.toFixed(2)}%</td>
          <td>${st.weight_in_b.toFixed(2)}%</td>
          <td>
            <span style="font-weight:800;color:#0284C7;background:#E0F2FE;padding:2px 8px;border-radius:6px;">
              ${st.overlap_contribution.toFixed(2)}%
            </span>
          </td>
        </tr>
      `).join('');
    }
  }
}

function drawPairwiseVennSvg(fundA, fundB, overlapPct) {
  const svg = document.getElementById('pairwiseVennSvg');
  if (!svg) return;

  const width = 500;
  const height = 200;
  const cy = height / 2;
  const radius = 62;

  // Center distance varies inversely with overlap percentage
  // 0% -> d = 124 (barely touching), 100% -> d = 0 (completely overlapping)
  const clampedPct = Math.max(0, Math.min(100, overlapPct));
  const d = Math.max(30, 124 - (clampedPct / 100.0) * 88);

  const cx1 = width / 2 - d / 2;
  const cx2 = width / 2 + d / 2;

  svg.innerHTML = `
    <defs>
      <linearGradient id="vennGradA" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#3B82F6" stop-opacity="0.85"/>
        <stop offset="100%" stop-color="#1D4ED8" stop-opacity="0.95"/>
      </linearGradient>
      <linearGradient id="vennGradB" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#93C5FD" stop-opacity="0.85"/>
        <stop offset="100%" stop-color="#60A5FA" stop-opacity="0.95"/>
      </linearGradient>
      <filter id="vennShadow" x="-20%" y="-20%" width="140%" height="140%">
        <feDropShadow dx="0" dy="4" stdDeviation="6" flood-opacity="0.12"/>
      </filter>
    </defs>

    <!-- Circle A (Fund A) -->
    <circle cx="${cx1}" cy="${cy}" r="${radius}" fill="url(#vennGradA)" filter="url(#vennShadow)" />
    <text x="${cx1 - 12}" y="${cy + 5}" text-anchor="middle" font-size="12" font-weight="700" fill="#FFFFFF">Fund A</text>

    <!-- Circle B (Fund B) -->
    <circle cx="${cx2}" cy="${cy}" r="${radius}" fill="url(#vennGradB)" filter="url(#vennShadow)" style="mix-blend-mode: multiply;" />
    <text x="${cx2 + 12}" y="${cy + 5}" text-anchor="middle" font-size="12" font-weight="700" fill="#1E3A8A">Fund B</text>

    <!-- Intersection Overlap Core -->
    <text x="${width / 2}" y="${cy + 4}" text-anchor="middle" font-size="13" font-weight="900" fill="#FFFFFF">
      ${overlapPct > 0 ? `${overlapPct.toFixed(1)}%` : ''}
    </text>
  `;
}

function switchPairwiseSelect(fundA, fundB) {
  const btn = document.querySelector('.overlap-tab-btn[data-tab="pairwise-sim"]');
  if (btn) btn.click();

  const selectA = document.getElementById('fundSelectA');
  const selectB = document.getElementById('fundSelectB');
  if (selectA) selectA.value = fundA;
  if (selectB) selectB.value = fundB;

  if (_globalOverlapData) {
    updatePairwiseVennDisplay(fundA, fundB, _globalOverlapData);
  }
}

// 🏛️ 3. CONSOLIDATED CROSS-FUND STOCK EXPLORER
function renderCrossFundStockExplorer(overlap) {
  const tableBody = document.getElementById('crossStockTableBody');
  const searchInput = document.getElementById('crossStockSearch');
  if (!tableBody) return;

  const holdingsMap = overlap.fund_holdings_map || {};
  const stockAggregator = {};

  Object.entries(holdingsMap).forEach(([fundName, constituents]) => {
    const fundHolding = (_globalHoldingsData || []).find(h => h.scheme_name === fundName);
    const fundPortfolioWeight = fundHolding ? (fundHolding.portfolio_weight_pct || 10.0) : 10.0;

    constituents.forEach(c => {
      if (!stockAggregator[c.stock_name]) {
        stockAggregator[c.stock_name] = {
          stock_name: c.stock_name,
          funds: [],
          totalAggregatedWeight: 0.0
        };
      }
      stockAggregator[c.stock_name].funds.push({
        fund_name: fundName,
        weight_in_fund: c.weight
      });
      stockAggregator[c.stock_name].totalAggregatedWeight += (c.weight * fundPortfolioWeight) / 100.0;
    });
  });

  const sortedStocks = Object.values(stockAggregator).sort((a, b) => b.funds.length - a.funds.length || b.totalAggregatedWeight - a.totalAggregatedWeight);

  const renderRows = (list) => {
    if (list.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--muted);padding:24px;">No stocks matching search filter.</td></tr>';
      return;
    }
    tableBody.innerHTML = list.map(st => `
      <tr>
        <td><strong>${st.stock_name}</strong></td>
        <td>
          <div style="display:flex;flex-wrap:wrap;gap:4px;">
            ${st.funds.map(f => `
              <span class="stock-chip" style="font-size:0.7rem;background:var(--cream);">
                ${f.fund_name.replace(/Fund.*$/i, '').trim()} (${f.weight_in_fund.toFixed(1)}%)
              </span>
            `).join('')}
          </div>
        </td>
        <td>
          <span style="font-weight:700;background:var(--ink);color:var(--white);padding:2px 8px;border-radius:12px;font-size:0.72rem;">
            ${st.funds.length} Funds
          </span>
        </td>
        <td>
          <strong style="color:#059669;">${st.totalAggregatedWeight.toFixed(2)}%</strong>
        </td>
      </tr>
    `).join('');
  };

  renderRows(sortedStocks);

  if (searchInput) {
    searchInput.oninput = () => {
      const q = searchInput.value.toLowerCase().trim();
      renderRows(sortedStocks.filter(s => s.stock_name.toLowerCase().includes(q)));
    };
  }
}

// Summary Cards Grid
function renderOverlapSummaryCards(pairs) {
  const container = document.getElementById('overlapPairsGrid');
  if (!container) return;

  if (pairs.length === 0) {
    container.innerHTML = '<div class="card"><p>No multiple equity funds detected for overlap calculation.</p></div>';
    return;
  }

  container.innerHTML = pairs.map(p => {
    const isHigh = p.overlap_percentage >= 30.0;
    return `
      <div class="overlap-card ${isHigh ? 'high-overlap' : ''}" onclick="switchPairwiseSelect('${p.fund_a}', '${p.fund_b}')">
        <div class="overlap-header">
          <div class="overlap-funds-title">${p.fund_a} <br>⚯ ${p.fund_b}</div>
          <span class="overlap-pct-badge ${isHigh ? 'pct-high' : 'pct-normal'}">${p.overlap_percentage}% Overlap</span>
        </div>
        <div style="font-size:0.72rem;color:var(--muted);font-weight:600;">Top Common Holdings (${p.common_holdings.length}):</div>
        <div class="overlap-chips">
          ${(p.common_holdings || []).slice(0, 6).map(st => `<span class="stock-chip">${st}</span>`).join('')}
          ${(p.common_holdings || []).length > 6 ? `<span class="stock-chip">+${p.common_holdings.length - 6} more</span>` : ''}
        </div>
      </div>
    `;
  }).join('');
}

// ── AI Advisory & Interactive Checklist ───────────────────────────
function renderAIAdvisory(ai) {
  // 1. Verdict
  const verdictEl = document.getElementById('aiVerdictText');
  if (verdictEl && ai.risk_alignment_verdict) {
    verdictEl.textContent = ai.risk_alignment_verdict;
  }

  // 2. Full recommendations
  const recGrid = document.getElementById('fullRecommendationsGrid');
  if (recGrid && ai.fund_recommendations) {
    recGrid.innerHTML = ai.fund_recommendations.map(act => `
      <div class="action-card" style="padding:16px;">
        <div class="action-header">
          <strong style="font-size:0.88rem;">${act.scheme_name}</strong>
          <span class="action-badge badge-${act.action}">${act.action.replace(/_/g, ' ')}</span>
        </div>
        <div class="action-rationale" style="margin-top:6px;font-size:0.78rem;">${act.rationale}</div>
        ${act.target_alternative ? `<div class="action-target" style="margin-top:6px;">↳ Reinvest Alternative: <strong>${act.target_alternative}</strong></div>` : ''}
      </div>
    `).join('');
  }

  // 3. Step-by-Step Checklist with Interactive Checkboxes
  const checkContainer = document.getElementById('rebalanceChecklistContainer');
  if (checkContainer && ai.step_by_step_rebalance_checklist) {
    checkContainer.innerHTML = ai.step_by_step_rebalance_checklist.map((step, idx) => `
      <div class="checklist-item" id="step-item-${idx}">
        <input type="checkbox" class="checklist-cb" onchange="toggleChecklistStep(${idx}, this)">
        <div class="checklist-content">
          <div class="checklist-title-row">
            <span class="checklist-title">Step ${step.step}: ${step.title}</span>
            <span class="priority-pill prio-${step.priority}">${step.priority}</span>
          </div>
          <div class="checklist-desc">${step.description}</div>
        </div>
      </div>
    `).join('');
  }
}

function toggleChecklistStep(idx, cb) {
  const item = document.getElementById(`step-item-${idx}`);
  if (item) {
    item.classList.toggle('completed', cb.checked);
  }
}

// ── Right Sidebar ────────────────────────────────────────────────
function renderRightSidebar(summary, quant, ai) {
  document.getElementById('rsInvestorName').textContent = summary.investor_name || 'Valued Investor';
  document.getElementById('rsInvestorPan').textContent = summary.pan || '–';
  document.getElementById('rsInvestorPeriod').textContent = summary.statement_period || 'Latest eCAS';

  if (quant.cost_drag) {
    document.getElementById('rsDragAmount').textContent = fmt(quant.cost_drag.annual_expense_drag_amount) + ' / yr';
  }

  const rsActions = document.getElementById('rsQuickActions');
  if (rsActions && ai.fund_recommendations) {
    const urgent = ai.fund_recommendations.filter(r => r.action === 'SWITCH_TO_DIRECT' || r.action === 'EXIT_AND_REINVEST');
    if (urgent.length > 0) {
      rsActions.innerHTML = urgent.slice(0, 4).map(u => `
        <div class="rs-action-item">
          <span style="max-width:140px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${u.scheme_name}</span>
          <span class="action-badge badge-${u.action}" style="font-size:0.6rem;padding:2px 6px;">${u.action === 'SWITCH_TO_DIRECT' ? 'SWITCH' : 'EXIT'}</span>
        </div>
      `).join('');
    } else {
      rsActions.innerHTML = '<div class="rs-empty" style="font-size:0.72rem;color:var(--muted);">All funds aligned.</div>';
    }
  }
}

// ── Spending Analytics Data Loader ───────────────────────────────
async function loadSpendingData() {
  try {
    const [overview, categories, ie, monthly, weekly, trends, anomalies, insights, calendar, health] =
      await Promise.all([
        fetch('/api/overview').then(r=>r.json()),
        fetch('/api/categories').then(r=>r.json()),
        fetch('/api/income-expense').then(r=>r.json()),
        fetch('/api/monthly').then(r=>r.json()),
        fetch('/api/weekly').then(r=>r.json()),
        fetch('/api/trends').then(r=>r.json()),
        fetch('/api/anomalies').then(r=>r.json()),
        fetch('/api/insights').then(r=>r.json()),
        fetch('/api/calendar').then(r=>r.json()),
        fetch('/api/health').then(r=>r.json()),
      ]);

    renderSpendingOverview(overview);
    renderSpendingCategories(categories);
    renderSpendingIncomeExpense(ie);
    renderSpendingTrends(trends);
    renderSpendingAnomalies(anomalies);
  } catch (e) {
    console.log('Spending analytics background load notice:', e);
  }
}

function renderSpendingOverview(d) {
  if (!d || d.error) return;
  const incEl = document.getElementById('statIncome');
  if (incEl) incEl.textContent = fmt(d.total_income);
  const expEl = document.getElementById('statExpenses');
  if (expEl) expEl.textContent = fmt(d.total_expenses);
  const savEl = document.getElementById('statSavings');
  if (savEl) savEl.textContent = fmt(d.net_savings);
  const savRateEl = document.getElementById('statSavingsRate');
  if (savRateEl) savRateEl.textContent = (d.savings_rate || 0) + '% savings rate';
  const spRateEl = document.getElementById('statSpendingRate');
  if (spRateEl) spRateEl.textContent = (100 - (d.savings_rate || 0)).toFixed(1) + '%';
  const txCountEl = document.getElementById('statTxCount');
  if (txCountEl) txCountEl.textContent = `${d.total_transactions || 0} transactions`;
  const incRangeEl = document.getElementById('statIncomeRange');
  if (incRangeEl && d.date_range) incRangeEl.textContent = `${d.date_range.start} – ${d.date_range.end}`;
}

function renderSpendingCategories(d) {
  if (!d || !d.labels || d.labels.length === 0) return;
  destroyChart('donut');
  const canvas = document.getElementById('donutChart');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    _charts['donut'] = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: d.labels,
        datasets: [{ data: d.values, backgroundColor: d.colors, borderWidth: 2, borderColor: COLORS.white }]
      },
      options: { cutout: '68%', plugins: { legend: { display: false } }, animation: { duration: 600 } }
    });
  }

  const leg = document.getElementById('catLegend');
  if (leg) {
    leg.innerHTML = d.labels.slice(0, 5).map((label, i) =>
      `<div class="legend-item"><div class="legend-dot" style="background:${d.colors[i]}"></div>${label}</div>`
    ).join('');
  }

  destroyChart('catBar');
  const barCanvas = document.getElementById('catBarChart');
  if (barCanvas) {
    const ctx2 = barCanvas.getContext('2d');
    _charts['catBar'] = new Chart(ctx2, {
      type: 'bar',
      data: {
        labels: d.labels,
        datasets: [{ label: 'Amount (₹)', data: d.values, backgroundColor: d.colors, borderRadius: 8 }]
      },
      options: { indexAxis: 'y', plugins: { legend: { display: false } } }
    });
  }
}

function renderSpendingIncomeExpense(d) {
  if (!d || !d.months) return;
  destroyChart('ie');
  const canvas = document.getElementById('incomeExpenseChart');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    _charts['ie'] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: d.months,
        datasets: [
          { label: 'Income', data: d.income, backgroundColor: COLORS.sage, borderRadius: 6 },
          { label: 'Expense', data: d.expense, backgroundColor: COLORS.blush, borderRadius: 6 }
        ]
      },
      options: { plugins: { legend: { position: 'top' } } }
    });
  }
}

function renderSpendingTrends(d) {
  if (!d || !d.dates) return;
  destroyChart('trendFull');
  const canvas = document.getElementById('trendChartFull');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    _charts['trendFull'] = new Chart(ctx, {
      type: 'line',
      data: {
        labels: d.dates,
        datasets: [{ label: 'Daily Spend (₹)', data: d.daily, borderColor: COLORS.ink, tension: 0.3, fill: false }]
      },
      options: { plugins: { legend: { display: false } } }
    });
  }
}

function renderSpendingAnomalies(d) {
  const container = document.getElementById('anomalyList');
  if (!container || !d || !d.anomalies) return;
  container.innerHTML = d.anomalies.map(a => `
    <div class="alert-card alert-high" style="margin-bottom:8px;">
      <div class="alert-top">
        <strong>${a.description} (${a.category})</strong>
        <span class="text-danger" style="font-weight:700;">${fmt(a.amount)}</span>
      </div>
      <div style="font-size:0.72rem;color:var(--muted);">${a.date} · Z-score: ${a.z_score}</div>
    </div>
  `).join('');
}

function refreshCurrentView() {
  showToast('✦ Refreshing live quant & AI intelligence…');
  sessionStorage.removeItem('finwise_portfolio_audit');
  initMutualFundAudit(true);
  loadSpendingData();
}

function showToast(msg) {
  const t = document.getElementById('toast');
  if (!t) return;
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3500);
}
