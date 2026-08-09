/**
 * AERIS Performance Reports Controller
 * Connects to FastAPI (http://localhost:8000/reports)
 */

const API_BASE_URL = window.location.origin.startsWith('http') ? window.location.origin : 'http://localhost:8000';

let allReports = [];
let activeReport = null;

document.addEventListener('DOMContentLoaded', () => {
    console.log('[AERIS Reports] Controller initialized. API URL:', API_BASE_URL);
    initUserProfile();
    initEventListeners();
    loadReports();
});

function initUserProfile() {
    const userStr = localStorage.getItem('aeris_user');
    const customAvatar = localStorage.getItem('aeris_avatar');
    const navAvatarEl = document.getElementById('userNavAvatar');
    const profileBtn = document.getElementById('userProfileBtn');

    if (navAvatarEl) {
        if (customAvatar) {
            navAvatarEl.src = customAvatar;
        } else if (userStr) {
            try {
                const user = JSON.parse(userStr);
                if (user.avatar_url) navAvatarEl.src = user.avatar_url;
            } catch (e) {}
        }
    }

    if (profileBtn) {
        profileBtn.addEventListener('click', (e) => {
            e.preventDefault();
            window.location.href = 'profile.html';
        });
    }
}

/**
 * Event Listeners for Filters, Search, Modal, and Refresh
 */
function initEventListeners() {
    const searchInput = document.getElementById('searchInput');
    const riskFilter = document.getElementById('riskFilter');
    const sortOrder = document.getElementById('sortOrder');
    const refreshBtn = document.getElementById('refreshReportsBtn');
    const exportBtn = document.getElementById('exportAllJsonBtn');

    const modal = document.getElementById('reportModal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const downloadJsonBtn = document.getElementById('downloadJsonBtn');

    if (searchInput) searchInput.addEventListener('input', renderTable);
    if (riskFilter) riskFilter.addEventListener('change', renderTable);
    if (sortOrder) sortOrder.addEventListener('change', renderTable);

    if (refreshBtn) refreshBtn.addEventListener('click', loadReports);
    if (exportBtn) exportBtn.addEventListener('click', exportAllSummary);

    if (closeModalBtn && modal) {
        closeModalBtn.addEventListener('click', () => modal.classList.add('hidden'));
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.classList.add('hidden');
        });
    }

    if (downloadJsonBtn) {
        downloadJsonBtn.addEventListener('click', () => {
            if (!activeReport) return;
            downloadReportJson(activeReport);
        });
    }
}

/**
 * Load Reports from GET /reports
 */
async function loadReports() {
    const tableBody = document.getElementById('reportsTableBody');
    if (tableBody) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="5" class="py-12 text-center text-outline italic">
                    <span class="material-symbols-outlined animate-spin text-primary-green align-middle mr-2">sync</span>
                    Loading historical performance reports...
                </td>
            </tr>
        `;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/reports`);
        if (!response.ok) {
            throw new Error(`Server returned status ${response.status}`);
        }

        allReports = await response.json();
        console.log('[AERIS Reports] Fetched reports:', allReports);

        updateBentoStats(allReports);
        renderTable();

    } catch (err) {
        console.error('[AERIS Reports] Error loading reports:', err);
        if (tableBody) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="py-8 text-center text-rose-600 bg-rose-50 font-medium">
                        Unable to connect to FastAPI backend (${API_BASE_URL}). Make sure uvicorn server is running.
                    </td>
                </tr>
            `;
        }
    }
}

/**
 * Calculate and render top overview Bento cards stats
 */
function updateBentoStats(reports) {
    const statTotal = document.getElementById('statTotalSessions');
    const statAvgReadiness = document.getElementById('statAvgReadiness');
    const statPrimaryHazard = document.getElementById('statPrimaryHazard');
    const statOptimalRate = document.getElementById('statOptimalRate');

    if (!reports || reports.length === 0) {
        if (statTotal) statTotal.textContent = '0';
        if (statAvgReadiness) statAvgReadiness.textContent = '--%';
        if (statPrimaryHazard) statPrimaryHazard.textContent = 'None';
        if (statOptimalRate) statOptimalRate.textContent = '0%';
        return;
    }

    // 1. Total count
    if (statTotal) statTotal.textContent = reports.length;

    // 2. Avg Readiness Score (100 - overall_risk)
    const totalRisk = reports.reduce((acc, r) => acc + (r.overall_risk || 0), 0);
    const avgRisk = totalRisk / reports.length;
    const avgReadiness = Math.max(0, Math.round(100 - avgRisk));
    if (statAvgReadiness) statAvgReadiness.textContent = `${avgReadiness}%`;

    // 3. Primary Hazard (Most frequent alert / highest body risk)
    let kneeSum = 0, spineSum = 0, valgusAlerts = 0;
    reports.forEach(r => {
        kneeSum += r.body_part_risks.knee || 0;
        spineSum += r.body_part_risks.spine || 0;
        if (r.alerts && r.alerts.some(a => a.toLowerCase().includes('valgus'))) {
            valgusAlerts++;
        }
    });

    let primaryHazard = 'Knee Valgus';
    if (spineSum > kneeSum) primaryHazard = 'Trunk Lean';
    if (statPrimaryHazard) statPrimaryHazard.textContent = primaryHazard;

    // 4. Optimal Mechanics Rate (% LOW risk)
    const lowRiskCount = reports.filter(r => r.risk_level === 'LOW').length;
    const optimalRate = Math.round((lowRiskCount / reports.length) * 100);
    if (statOptimalRate) statOptimalRate.textContent = `${optimalRate}%`;
}

/**
 * Filter, sort, and render reports table
 */
function renderTable() {
    const tableBody = document.getElementById('reportsTableBody');
    const searchQuery = (document.getElementById('searchInput')?.value || '').toLowerCase();
    const selectedRisk = document.getElementById('riskFilter')?.value || 'ALL';
    const sortOrder = document.getElementById('sortOrder')?.value || 'NEWEST';

    if (!tableBody) return;

    // Filter
    let filtered = allReports.filter(r => {
        const nameMatch = (r.video_name || '').toLowerCase().includes(searchQuery) ||
                          (r.job_id || '').toLowerCase().includes(searchQuery);
        const riskMatch = selectedRisk === 'ALL' || r.risk_level === selectedRisk;
        return nameMatch && riskMatch;
    });

    // Sort
    if (sortOrder === 'RISK_HIGH') {
        filtered.sort((a, b) => b.overall_risk - a.overall_risk);
    } else if (sortOrder === 'RISK_LOW') {
        filtered.sort((a, b) => a.overall_risk - b.overall_risk);
    } // default NEWEST keeps original order

    if (filtered.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="5" class="py-12 text-center text-outline italic">
                    No performance reports match your search criteria.
                </td>
            </tr>
        `;
        return;
    }

    let html = '';
    filtered.forEach(report => {
        const overallRisk = report.overall_risk;
        const riskLevel = report.risk_level;

        let badgeClass = 'bg-emerald-100 text-emerald-800';
        if (riskLevel === 'MODERATE') badgeClass = 'bg-amber-100 text-amber-800';
        if (riskLevel === 'HIGH') badgeClass = 'bg-orange-100 text-orange-800';
        if (riskLevel === 'VERY HIGH') badgeClass = 'bg-rose-100 text-rose-800';

        const knee = Math.round(report.body_part_risks.knee || 0);
        const hip = Math.round(report.body_part_risks.hip || 0);
        const spine = Math.round(report.body_part_risks.spine || 0);
        const fatigue = Math.round(report.body_part_risks.fatigue || 0);

        html += `
            <tr class="hover:bg-surface-container-low/50 transition-colors">
                <td class="py-4 px-6 font-medium text-on-surface">
                    <div class="flex items-center gap-3">
                        <div class="w-8 h-8 rounded-full bg-accent-soft flex items-center justify-center text-primary-green shrink-0">
                            <span class="material-symbols-outlined text-sm">videocam</span>
                        </div>
                        <div>
                            <span class="block font-bold">${escapeHtml(report.video_name)}</span>
                            <span class="text-xs text-outline font-mono">${escapeHtml(report.job_id.slice(0, 16))}...</span>
                        </div>
                    </div>
                </td>
                <td class="py-4 px-6 font-bold text-on-surface">
                    ${overallRisk} / 100
                </td>
                <td class="py-4 px-6">
                    <span class="font-label-caps text-xs px-2.5 py-1 rounded-full uppercase font-bold ${badgeClass}">
                        ${riskLevel}
                    </span>
                </td>
                <td class="py-4 px-6 text-xs text-on-surface-variant">
                    <span class="inline-block px-1.5 py-0.5 rounded bg-surface border border-outline-variant mr-1">K: ${knee}%</span>
                    <span class="inline-block px-1.5 py-0.5 rounded bg-surface border border-outline-variant mr-1">H: ${hip}%</span>
                    <span class="inline-block px-1.5 py-0.5 rounded bg-surface border border-outline-variant mr-1">S: ${spine}%</span>
                    <span class="inline-block px-1.5 py-0.5 rounded bg-surface border border-outline-variant">F: ${fatigue}%</span>
                </td>
                <td class="py-4 px-6 text-right">
                    <button onclick="openReportModal('${escapeHtml(report.job_id)}')" class="bg-surface hover:bg-surface-container-low text-primary-green border border-primary-green/30 px-3 py-1.5 rounded-lg text-xs font-bold transition-colors">
                        View Report
                    </button>
                </td>
            </tr>
        `;
    });

    tableBody.innerHTML = html;
}

/**
 * Open Inspector Modal with detailed report information
 */
window.openReportModal = function(jobId) {
    const report = allReports.find(r => r.job_id === jobId);
    if (!report) return;

    activeReport = report;
    const modal = document.getElementById('reportModal');

    document.getElementById('modalVideoTitle').textContent = report.video_name;
    document.getElementById('modalJobId').textContent = `Job ID: ${report.job_id}`;
    document.getElementById('modalRiskScore').textContent = `${report.overall_risk}/100`;

    const levelBadge = document.getElementById('modalRiskLevel');
    levelBadge.textContent = report.risk_level;
    if (report.risk_level === 'LOW') {
        levelBadge.className = 'font-label-caps text-xs font-bold text-emerald-800 bg-emerald-100 px-3 py-1 rounded-full mt-2 inline-block';
    } else if (report.risk_level === 'MODERATE') {
        levelBadge.className = 'font-label-caps text-xs font-bold text-amber-800 bg-amber-100 px-3 py-1 rounded-full mt-2 inline-block';
    } else {
        levelBadge.className = 'font-label-caps text-xs font-bold text-rose-800 bg-rose-100 px-3 py-1 rounded-full mt-2 inline-block';
    }

    document.getElementById('modalLandingScore').textContent = Math.round(report.movement_scores.landing_quality || 0);
    document.getElementById('modalSymmetryScore').textContent = `${Math.round(report.movement_scores.symmetry_score || 0)}%`;

    document.getElementById('modalKneeRisk').textContent = `${Math.round(report.body_part_risks.knee || 0)}%`;
    document.getElementById('modalHipRisk').textContent = `${Math.round(report.body_part_risks.hip || 0)}%`;
    document.getElementById('modalSpineRisk').textContent = `${Math.round(report.body_part_risks.spine || 0)}%`;
    document.getElementById('modalFatigueRisk').textContent = `${Math.round(report.body_part_risks.fatigue || 0)}%`;

    // Alerts & Recommendations
    const alertsContainer = document.getElementById('modalAlertsContainer');
    let alertsHtml = '';

    const llmRecs = report.llm_recommendations;

    if (llmRecs && typeof llmRecs === 'object') {
        const engineName = llmRecs.engine || 'Groq LLM';
        const execSummary = llmRecs.executive_summary || '';
        const exercises = llmRecs.corrective_exercises || [];
        const posture = llmRecs.posture_and_ergonomics || [];
        const recovery = llmRecs.recovery_protocol || [];

        alertsHtml += `
            <div class="flex flex-col gap-3">
                <div class="flex items-center justify-between bg-gradient-to-r from-emerald-900 to-teal-800 text-white p-3 rounded-lg">
                    <div class="flex items-center gap-2">
                        <span class="material-symbols-outlined text-emerald-400 text-base">auto_awesome</span>
                        <span class="font-bold text-xs">AI Specialist Recommendations (${escapeHtml(engineName)})</span>
                    </div>
                </div>

                ${execSummary ? `
                <div class="p-3 bg-emerald-50 rounded-lg border border-emerald-200 text-xs text-emerald-900">
                    <strong class="block mb-1 text-emerald-950 font-bold">Executive Summary:</strong>
                    ${escapeHtml(execSummary)}
                </div>
                ` : ''}

                ${exercises.length > 0 ? `
                <div class="flex flex-col gap-2">
                    <strong class="text-xs font-bold text-on-surface">Targeted Exercises:</strong>
                    ${exercises.map(ex => `
                        <div class="p-2.5 bg-surface rounded-lg border border-outline-variant text-xs">
                            <div class="flex justify-between font-bold text-on-surface">
                                <span>${escapeHtml(ex.name)}</span>
                                <span class="text-primary-green">${escapeHtml(ex.sets_reps || '')}</span>
                            </div>
                            <p class="text-outline text-[11px] font-medium">${escapeHtml(ex.description || '')}</p>
                            ${ex.coaching_cue ? `<p class="text-teal-800 text-[11px] mt-1 bg-teal-50 p-1.5 rounded"><strong>Cue:</strong> ${escapeHtml(ex.coaching_cue)}</p>` : ''}
                        </div>
                    `).join('')}
                </div>
                ` : ''}

                ${(posture.length > 0 || recovery.length > 0) ? `
                <div class="grid grid-cols-1 gap-2 text-xs">
                    ${posture.length > 0 ? `
                    <div class="p-2.5 bg-blue-50 rounded-lg border border-blue-200 text-blue-900">
                        <strong class="block mb-1 text-blue-950 font-bold">Posture & Ergonomics:</strong>
                        <ul class="list-disc pl-4 space-y-1">
                            ${posture.map(p => `<li>${escapeHtml(p)}</li>`).join('')}
                        </ul>
                    </div>
                    ` : ''}
                    ${recovery.length > 0 ? `
                    <div class="p-2.5 bg-purple-50 rounded-lg border border-purple-200 text-purple-900">
                        <strong class="block mb-1 text-purple-950 font-bold">Recovery Protocol:</strong>
                        <ul class="list-disc pl-4 space-y-1">
                            ${recovery.map(r => `<li>${escapeHtml(r)}</li>`).join('')}
                        </ul>
                    </div>
                    ` : ''}
                </div>
                ` : ''}
            </div>
        `;
    } else if ((report.alerts || []).length === 0 && (report.recommendations || []).length === 0) {
        alertsHtml = `<p class="text-xs text-emerald-700 bg-emerald-50 p-3 rounded-lg border border-emerald-200">No posture abnormalities detected.</p>`;
    } else {
        (report.alerts || []).forEach(alertText => {
            alertsHtml += `
                <div class="flex items-start gap-2 p-2.5 bg-amber-50 rounded-lg border border-amber-200 text-xs text-amber-900 font-medium mb-2">
                    <span class="material-symbols-outlined text-amber-600 text-sm mt-0.5">warning</span>
                    <span>${escapeHtml(alertText)}</span>
                </div>
            `;
        });
        (report.recommendations || []).forEach(recText => {
            alertsHtml += `
                <div class="flex items-start gap-2 p-2.5 bg-emerald-50 rounded-lg border border-emerald-200 text-xs text-emerald-900 font-medium mb-2">
                    <span class="material-symbols-outlined text-emerald-600 text-sm mt-0.5">task_alt</span>
                    <span>${escapeHtml(recText)}</span>
                </div>
            `;
        });
    }
    alertsContainer.innerHTML = alertsHtml;


    modal.classList.remove('hidden');
};

/**
 * Download single report JSON file
 */
function downloadReportJson(report) {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(report, null, 2));
    const dlAnchorElem = document.createElement('a');
    dlAnchorElem.setAttribute("href", dataStr);
    dlAnchorElem.setAttribute("download", `risk_report_${report.video_name}.json`);
    document.body.appendChild(dlAnchorElem);
    dlAnchorElem.click();
    dlAnchorElem.remove();
}

/**
 * Export summary of all loaded reports
 */
function exportAllSummary() {
    if (allReports.length === 0) {
        alert('No reports available to export.');
        return;
    }
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(allReports, null, 2));
    const dlAnchorElem = document.createElement('a');
    dlAnchorElem.setAttribute("href", dataStr);
    dlAnchorElem.setAttribute("download", `aeris_all_reports_summary.json`);
    document.body.appendChild(dlAnchorElem);
    dlAnchorElem.click();
    dlAnchorElem.remove();
}

function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/[&<>"']/g, function(m) {
        return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m];
    });
}
