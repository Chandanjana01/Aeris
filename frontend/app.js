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
    initDropzone();
    initAnalyzeButton();
});

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
    updateAlertsAndRecommendations(report.alerts, report.recommendations);
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
 * Display Alerts & Recommendations list
 */
function updateAlertsAndRecommendations(alerts = [], recommendations = []) {
    const container = document.getElementById('recommendationsContainer');
    if (!container) return;

    if (alerts.length === 0 && recommendations.length === 0) {
        container.innerHTML = `
            <p class="text-body-sm text-emerald-700 font-medium bg-emerald-50 p-3 rounded-lg border border-emerald-200 flex items-center gap-2">
                <span class="material-symbols-outlined text-emerald-600" data-icon="check_circle">check_circle</span>
                No critical ergonomic hazards detected. Posture mechanics are optimal.
            </p>
        `;
        return;
    }

    let html = '<div class="flex flex-col gap-3 mt-2">';

    alerts.forEach((alertText) => {
        html += `
            <div class="flex items-start gap-3 p-3 bg-amber-50 rounded-lg border border-amber-200">
                <span class="material-symbols-outlined text-amber-600 text-sm mt-0.5" data-icon="warning">warning</span>
                <span class="text-body-sm text-amber-900 font-medium">${alertText}</span>
            </div>
        `;
    });

    recommendations.forEach((recText) => {
        html += `
            <div class="flex items-start gap-3 p-3 bg-emerald-50 rounded-lg border border-emerald-200">
                <span class="material-symbols-outlined text-emerald-600 text-sm mt-0.5" data-icon="task_alt">task_alt</span>
                <span class="text-body-sm text-emerald-900 font-medium">${recText}</span>
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
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
