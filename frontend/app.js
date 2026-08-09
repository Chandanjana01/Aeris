/**
 * AERIS Athlete Performance Dashboard - Main JavaScript Controller
 * Dynamically resolves API_BASE_URL from current location
 */

// Dynamically determine API origin (handles localhost, 127.0.0.1, or custom host)
const API_BASE_URL = window.location.origin.startsWith('http') ? window.location.origin : 'http://localhost:8000';

// Global state
let selectedFile = null;
let currentJobId = null;
let pollInterval = null;

// DOM Elements
document.addEventListener('DOMContentLoaded', () => {
    console.log('[AERIS] Dashboard initialized. API Base URL:', API_BASE_URL);
    initUserProfile();
    initDropzone();
    initAnalyzeButton();
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
 * Initialize Drag & Drop Zone and File Input
 */
function initDropzone() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('videoFileInput');
    const fileInfo = document.getElementById('fileInfo');
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const fileSizeDisplay = document.getElementById('fileSizeDisplay');
    const dropzonePrompt = document.getElementById('dropzonePrompt');

    if (!dropzone || !fileInput) return;

    // Trigger click on file input when clicking dropzone
    dropzone.addEventListener('click', (e) => {
        // Don't re-trigger if clicking internal elements
        fileInput.click();
    });

    // File selected via input
    fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });

    // Drag and Drop Events
    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('bg-surface-container-low', 'border-primary-green');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('bg-surface-container-low', 'border-primary-green');
        }, false);
    });

    dropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files && files.length > 0) {
            handleFileSelect(files[0]);
        }
    });

    function handleFileSelect(file) {
        // Validate file type
        const validExtensions = ['mp4', 'mov', 'avi', 'mkv', 'wmv'];
        const ext = file.name.split('.').pop().toLowerCase();

        if (!validExtensions.includes(ext)) {
            alert(`Invalid file format .${ext}. Please upload MP4, MOV, AVI, MKV, or WMV.`);
            return;
        }

        selectedFile = file;
        console.log('[AERIS] Video file selected:', file.name, formatBytes(file.size));

        if (fileNameDisplay) fileNameDisplay.textContent = file.name;
        if (fileSizeDisplay) fileSizeDisplay.textContent = formatBytes(file.size);

        if (dropzonePrompt) dropzonePrompt.classList.add('hidden');
        if (fileInfo) fileInfo.classList.remove('hidden');
    }
}

/**
 * Format byte count to human readable MB/KB
 */
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Initialize Analyze Button Click Handler
 */
function initAnalyzeButton() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const fileInput = document.getElementById('videoFileInput');
    if (!analyzeBtn) return;

    analyzeBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        console.log('[AERIS] Analyze button clicked. Selected file:', selectedFile ? selectedFile.name : 'None');

        if (!selectedFile) {
            console.log('[AERIS] No file selected yet. Triggering file picker...');
            if (fileInput) fileInput.click();
            return;
        }

        await startAnalysisWorkflow(selectedFile);
    });
}

/**
 * Main Analysis Workflow: Upload -> Poll -> Fetch Report -> Update UI
 */
async function startAnalysisWorkflow(file) {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const analyzeBtnText = document.getElementById('analyzeBtnText');
    const analyzeBtnIcon = document.getElementById('analyzeBtnIcon');
    const statusBanner = document.getElementById('statusBanner');
    const statusText = document.getElementById('statusText');

    // UI Loading State
    analyzeBtn.disabled = true;
    analyzeBtn.classList.add('opacity-75', 'cursor-not-allowed');
    if (analyzeBtnText) analyzeBtnText.textContent = 'Uploading Video...';
    if (analyzeBtnIcon) analyzeBtnIcon.classList.add('animate-spin');

    if (statusBanner) {
        statusBanner.classList.remove('hidden');
        if (statusText) statusText.textContent = 'Uploading video to AERIS AI Engine...';
    }

    try {
        // 1. Upload Video (POST /analyze)
        const formData = new FormData();
        formData.append('file', file);

        console.log('[AERIS] Sending POST request to:', `${API_BASE_URL}/analyze`);
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || 'Upload failed');
        }

        const data = await response.json();
        currentJobId = data.job_id;
        console.log('[AERIS] Video uploaded successfully. Job ID:', currentJobId);

        if (statusText) statusText.textContent = `Analysis queued (Job: ${currentJobId.slice(0, 8)}...). Running MediaPipe pose detection...`;
        if (analyzeBtnText) analyzeBtnText.textContent = 'Processing Pose Analysis...';

        // 2. Poll Status (GET /status/{job_id})
        startPolling(currentJobId);

    } catch (error) {
        console.error('[AERIS] Analysis error:', error);
        alert(`Failed to start analysis: ${error.message}`);
        resetAnalyzeButton();
        if (statusBanner) statusBanner.classList.add('hidden');
    }
}

/**
 * Poll job status until done or failed
 */
function startPolling(jobId) {
    const statusText = document.getElementById('statusText');
    const analyzeBtnText = document.getElementById('analyzeBtnText');

    if (pollInterval) clearInterval(pollInterval);

    pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/status/${jobId}`);
            if (!response.ok) return;

            const data = await response.json();
            console.log('[AERIS] Polling status for job:', jobId, '->', data.status);

            if (data.status === 'processing') {
                if (statusText) statusText.textContent = 'MediaPipe 33-Landmark Pose Tracking & Feature Extraction in progress...';
                if (analyzeBtnText) analyzeBtnText.textContent = 'Extracting Biomechanics...';
            } else if (data.status === 'done') {
                clearInterval(pollInterval);
                console.log('[AERIS] Job completed! Fetching report...');
                if (statusText) statusText.textContent = 'Analysis complete! Fetching risk assessment report...';
                if (analyzeBtnText) analyzeBtnText.textContent = 'Finalizing Report...';

                // Fetch final report
                await fetchAndDisplayReport(jobId);
                resetAnalyzeButton();
            } else if (data.status === 'failed') {
                clearInterval(pollInterval);
                console.error('[AERIS] Job failed with error:', data.error);
                alert(`Analysis failed: ${data.error || 'Unknown error'}`);
                resetAnalyzeButton();
                const statusBanner = document.getElementById('statusBanner');
                if (statusBanner) statusBanner.classList.add('hidden');
            }
        } catch (err) {
            console.error('[AERIS] Polling fetch error:', err);
        }
    }, 2000);
}

/**
 * Fetch Risk Report JSON (GET /report/{job_id}) and update Dashboard UI
 */
async function fetchAndDisplayReport(jobId) {
    try {
        console.log('[AERIS] Fetching final report from:', `${API_BASE_URL}/report/${jobId}`);
        const response = await fetch(`${API_BASE_URL}/report/${jobId}`);
        if (!response.ok) {
            throw new Error('Failed to retrieve risk report');
        }

        const report = await response.json();
        console.log('[AERIS] Received Report:', report);
        updateDashboardUI(report);

    } catch (err) {
        console.error('[AERIS] Report fetch error:', err);
        alert('Could not load report details.');
    }
}

/**
 * Update Dashboard UI elements with real backend data
 */
function updateDashboardUI(report) {
    // 1. Overall Readiness Score (100 - overall_risk)
    const readinessScore = Math.max(0, Math.round(100 - report.overall_risk));
    const readinessValue = document.getElementById('readinessValue');
    const readinessBadge = document.getElementById('readinessBadge');
    const gaugeCircle = document.getElementById('gaugeCircle');

    if (readinessValue) readinessValue.innerHTML = `${readinessScore}<span class="text-body-md text-outline">%</span>`;

    let strokeColor = '#16A34A';
    if (readinessBadge) {
        if (report.risk_level === 'LOW') {
            readinessBadge.textContent = 'LOW RISK';
            readinessBadge.className = 'font-label-caps text-label-caps text-emerald-800 bg-emerald-100 px-3 py-1 rounded-full mt-2';
            strokeColor = '#16A34A';
        } else if (report.risk_level === 'MODERATE') {
            readinessBadge.textContent = 'MODERATE RISK';
            readinessBadge.className = 'font-label-caps text-label-caps text-amber-800 bg-amber-100 px-3 py-1 rounded-full mt-2';
            strokeColor = '#D97706';
        } else if (report.risk_level === 'HIGH') {
            readinessBadge.textContent = 'HIGH RISK';
            readinessBadge.className = 'font-label-caps text-label-caps text-orange-800 bg-orange-100 px-3 py-1 rounded-full mt-2';
            strokeColor = '#EA580C';
        } else {
            readinessBadge.textContent = 'VERY HIGH RISK';
            readinessBadge.className = 'font-label-caps text-label-caps text-rose-800 bg-rose-100 px-3 py-1 rounded-full mt-2';
            strokeColor = '#DC2626';
        }
    }

    // Gauge SVG Circle dashoffset (283 circumference)
    if (gaugeCircle) {
        const offset = 283 - (283 * readinessScore / 100);
        gaugeCircle.style.stroke = strokeColor;
        gaugeCircle.style.strokeDashoffset = offset;
    }

    // 2. Kinematic Metrics (Landing quality, Symmetry, Stability)
    const m1 = document.getElementById('kinematicMetric1');
    const m2 = document.getElementById('kinematicMetric2');
    const m3 = document.getElementById('kinematicMetric3');

    if (m1 && report.movement_scores.landing_quality !== undefined) {
        m1.textContent = `LANDING: ${Math.round(report.movement_scores.landing_quality)}`;
    }
    if (m2 && report.movement_scores.symmetry_score !== undefined) {
        m2.textContent = `SYMMETRY: ${Math.round(report.movement_scores.symmetry_score)}%`;
    }
    if (m3 && report.movement_scores.stability_score !== undefined) {
        m3.textContent = `STABILITY: ${Math.round(report.movement_scores.stability_score)}`;
    }

    // 3. Regional Risk Breakdown Bars
    const kneeVal = Math.round(report.body_part_risks.knee || 0);
    const hipVal = Math.round(report.body_part_risks.hip || 0);
    const spineVal = Math.round(report.body_part_risks.spine || 0);
    const fatigueVal = Math.round(report.body_part_risks.fatigue || 0);

    updateRiskBar('kneeBar', 'kneeVal', kneeVal);
    updateRiskBar('hipBar', 'hipVal', hipVal);
    updateRiskBar('spineBar', 'spineVal', spineVal);
    updateRiskBar('fatigueBar', 'fatigueVal', fatigueVal);

    // 4. Recent Session Summary Card
    const recentSessionCard = document.getElementById('recentSessionCard');
    const recentSessionName = document.getElementById('recentSessionName');
    const recentSessionTime = document.getElementById('recentSessionTime');
    const recentSessionBadge = document.getElementById('recentSessionBadge');

    if (recentSessionCard) {
        recentSessionCard.classList.remove('hidden');
    }

    if (recentSessionName) {
        recentSessionName.textContent = selectedFile ? selectedFile.name : report.video_name;
    }
    if (recentSessionTime) {
        recentSessionTime.textContent = 'Analysis Complete • Just now';
    }
    if (recentSessionBadge) {
        recentSessionBadge.textContent = `${report.risk_level} RISK (${report.overall_risk}/100)`;
        if (report.risk_level === 'LOW') {
            recentSessionBadge.className = 'font-label-caps text-label-caps bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full uppercase';
        } else if (report.risk_level === 'MODERATE') {
            recentSessionBadge.className = 'font-label-caps text-label-caps bg-amber-100 text-amber-800 px-3 py-1 rounded-full uppercase';
        } else {
            recentSessionBadge.className = 'font-label-caps text-label-caps bg-rose-100 text-rose-800 px-3 py-1 rounded-full uppercase';
        }
    }

    // 5. Update Alerts & Recommendations
    updateAlertsAndRecommendations(report.alerts, report.recommendations, report.llm_recommendations);
}

/**
 * Helper to update a risk progress bar width, label, and color based on risk value
 */
function updateRiskBar(barId, valId, value) {
    const bar = document.getElementById(barId);
    const val = document.getElementById(valId);

    if (!bar || !val) return;

    bar.style.width = `${value}%`;
    val.textContent = `${value}%`;

    // Dynamic bar color based on risk severity
    if (value < 25) {
        bar.className = 'h-full bg-emerald-500 transition-all duration-700 rounded-full';
    } else if (value < 50) {
        bar.className = 'h-full bg-amber-500 transition-all duration-700 rounded-full';
    } else if (value < 75) {
        bar.className = 'h-full bg-orange-500 transition-all duration-700 rounded-full';
    } else {
        bar.className = 'h-full bg-rose-600 transition-all duration-700 rounded-full';
    }
}

/**
 * Display Alerts & Recommendations list with Groq LLM formatting
 */
function updateAlertsAndRecommendations(alerts = [], recommendations = [], llmRecs = null) {
    const container = document.getElementById('recommendationsContainer');
    if (!container) return;

    let html = '';

    // If Groq LLM recommendations exist, render structured AI layout
    if (llmRecs && typeof llmRecs === 'object') {
        const engineName = llmRecs.engine || 'Groq LLM';
        const execSummary = llmRecs.executive_summary || '';
        const exercises = llmRecs.corrective_exercises || [];
        const posture = llmRecs.posture_and_ergonomics || [];
        const recovery = llmRecs.recovery_protocol || [];
        const tips = llmRecs.actionable_tips || [];

        html += `
            <div class="flex flex-col gap-4 mt-2">
                <!-- LLM Header Badge -->
                <div class="flex items-center justify-between bg-gradient-to-r from-emerald-900 to-teal-800 text-white p-3.5 rounded-xl shadow-sm">
                    <div class="flex items-center gap-2.5">
                        <span class="material-symbols-outlined text-emerald-400 text-xl">auto_awesome</span>
                        <div>
                            <h4 class="font-bold text-xs tracking-wider uppercase">AI Physical Therapy Specialist</h4>
                            <p class="text-[11px] text-emerald-200">${escapeHtml(engineName)}</p>
                        </div>
                    </div>
                    <span class="bg-emerald-400/20 text-emerald-300 text-[10px] font-mono px-2.5 py-1 rounded-full border border-emerald-400/30 font-bold uppercase">GROQ POWERED</span>
                </div>

                ${execSummary ? `
                <!-- Executive Summary -->
                <div class="p-3.5 bg-emerald-50/80 rounded-xl border border-emerald-200">
                    <h5 class="text-xs font-bold text-emerald-950 uppercase tracking-wide mb-1 flex items-center gap-1.5">
                        <span class="material-symbols-outlined text-emerald-700 text-sm">clinical_notes</span> Clinical Executive Summary
                    </h5>
                    <p class="text-xs text-emerald-900 leading-relaxed font-medium">${escapeHtml(execSummary)}</p>
                </div>
                ` : ''}

                ${alerts.length > 0 ? `
                <!-- System Alerts -->
                <div class="flex flex-col gap-2">
                    <h5 class="text-xs font-bold text-amber-900 uppercase tracking-wide flex items-center gap-1.5">
                        <span class="material-symbols-outlined text-amber-600 text-sm">warning</span> Detected Kinematic Deviations
                    </h5>
                    ${alerts.map(alertText => `
                        <div class="flex items-start gap-2.5 p-2.5 bg-amber-50 rounded-lg border border-amber-200 text-xs text-amber-900 font-medium">
                            <span class="material-symbols-outlined text-amber-600 text-sm mt-0.5">priority_high</span>
                            <span>${escapeHtml(alertText)}</span>
                        </div>
                    `).join('')}
                </div>
                ` : ''}

                ${exercises.length > 0 ? `
                <!-- Corrective Exercise Routine -->
                <div class="flex flex-col gap-2">
                    <h5 class="text-xs font-bold text-on-surface uppercase tracking-wide flex items-center gap-1.5">
                        <span class="material-symbols-outlined text-primary-green text-sm">fitness_center</span> Targeted Corrective Exercises
                    </h5>
                    <div class="grid grid-cols-1 gap-2.5">
                        ${exercises.map(ex => `
                            <div class="p-3 bg-surface rounded-xl border border-surface-container-high shadow-2xs hover:border-primary-green/40 transition-colors">
                                <div class="flex justify-between items-start mb-1">
                                    <h6 class="font-bold text-xs text-on-surface">${escapeHtml(ex.name)}</h6>
                                    <span class="text-[10px] font-bold text-primary-green bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">${escapeHtml(ex.sets_reps || '')}</span>
                                </div>
                                <p class="text-[11px] text-outline font-medium mb-1.5"><strong class="text-on-surface-variant">Target:</strong> ${escapeHtml(ex.target_area || '')}</p>
                                <p class="text-xs text-on-surface-variant leading-normal mb-1.5">${escapeHtml(ex.description || '')}</p>
                                ${ex.coaching_cue ? `
                                <div class="text-[11px] text-teal-900 bg-teal-50/80 p-2 rounded-lg border border-teal-100 flex items-center gap-1.5">
                                    <span class="material-symbols-outlined text-teal-700 text-xs shrink-0">tips_and_updates</span>
                                    <span><strong>Cue:</strong> ${escapeHtml(ex.coaching_cue)}</span>
                                </div>
                                ` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
                ` : ''}

                ${(posture.length > 0 || recovery.length > 0) ? `
                <!-- Ergonomics & Recovery Grid -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    ${posture.length > 0 ? `
                    <div class="p-3 bg-blue-50/60 rounded-xl border border-blue-200/60">
                        <h5 class="text-xs font-bold text-blue-950 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                            <span class="material-symbols-outlined text-blue-700 text-sm">accessibility</span> Posture & Ergonomics
                        </h5>
                        <ul class="flex flex-col gap-1.5">
                            ${posture.map(p => `
                                <li class="text-xs text-blue-900 font-medium flex items-start gap-1.5">
                                    <span class="material-symbols-outlined text-blue-600 text-xs mt-0.5">check</span>
                                    <span>${escapeHtml(p)}</span>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                    ` : ''}

                    ${recovery.length > 0 ? `
                    <div class="p-3 bg-purple-50/60 rounded-xl border border-purple-200/60">
                        <h5 class="text-xs font-bold text-purple-950 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                            <span class="material-symbols-outlined text-purple-700 text-sm">self_improvement</span> Recovery & Mobility
                        </h5>
                        <ul class="flex flex-col gap-1.5">
                            ${recovery.map(r => `
                                <li class="text-xs text-purple-900 font-medium flex items-start gap-1.5">
                                    <span class="material-symbols-outlined text-purple-600 text-xs mt-0.5">restore</span>
                                    <span>${escapeHtml(r)}</span>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                    ` : ''}
                </div>
                ` : ''}
            </div>
        `;
        container.innerHTML = html;
        return;
    }

    // Fallback standard rules rendering
    if (alerts.length === 0 && recommendations.length === 0) {
        container.innerHTML = `
            <p class="text-body-sm text-emerald-700 font-medium bg-emerald-50 p-3 rounded-lg border border-emerald-200 flex items-center gap-2">
                <span class="material-symbols-outlined text-emerald-600" data-icon="check_circle">check_circle</span>
                No critical ergonomic hazards detected. Posture mechanics are optimal.
            </p>
        `;
        return;
    }

    html = '<div class="flex flex-col gap-3 mt-2">';

    alerts.forEach((alertText) => {
        html += `
            <div class="flex items-start gap-3 p-3 bg-amber-50 rounded-lg border border-amber-200">
                <span class="material-symbols-outlined text-amber-600 text-sm mt-0.5" data-icon="warning">warning</span>
                <span class="text-body-sm text-amber-900 font-medium">${escapeHtml(alertText)}</span>
            </div>
        `;
    });

    recommendations.forEach((recText) => {
        html += `
            <div class="flex items-start gap-3 p-3 bg-emerald-50 rounded-lg border border-emerald-200">
                <span class="material-symbols-outlined text-emerald-600 text-sm mt-0.5" data-icon="task_alt">task_alt</span>
                <span class="text-body-sm text-emerald-900 font-medium">${escapeHtml(recText)}</span>
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
}

function escapeHtml(str) {
    if (typeof str !== 'string') return str;
    return str.replace(/[&<>"']/g, function(m) {
        return {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        }[m];
    });
}


/**
 * Reset analyze button UI state
 */
function resetAnalyzeButton() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const analyzeBtnText = document.getElementById('analyzeBtnText');
    const analyzeBtnIcon = document.getElementById('analyzeBtnIcon');

    if (!analyzeBtn) return;

    analyzeBtn.disabled = false;
    analyzeBtn.classList.remove('opacity-75', 'cursor-not-allowed');
    if (analyzeBtnText) analyzeBtnText.textContent = 'Analyze Performance';
    if (analyzeBtnIcon) analyzeBtnIcon.classList.remove('animate-spin');
}
