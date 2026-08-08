/**
 * AERIS Auth Controller - Sign Up & Sign In
 * Connects to FastAPI (POST /signup & POST /login) with SQLite PBKDF2 Password Hashing
 */

const API_BASE_URL = window.location.origin.startsWith('http') ? window.location.origin : 'http://localhost:8000';

let isSignUp = true; // Mode state: true = Sign Up, false = Sign In

document.addEventListener('DOMContentLoaded', () => {
    console.log('[AERIS Auth] Initialized. API Base URL:', API_BASE_URL);
    initAuthUI();
});

function initAuthUI() {
    const authForm = document.getElementById('authForm');
    const switchModeBtn = document.getElementById('switchModeBtn');
    const togglePasswordBtn = document.getElementById('togglePasswordBtn');
    const passwordInput = document.getElementById('passwordInput');

    if (switchModeBtn) {
        switchModeBtn.addEventListener('click', toggleAuthMode);
    }

    if (togglePasswordBtn && passwordInput) {
        togglePasswordBtn.addEventListener('click', () => {
            const isPassword = passwordInput.type === 'password';
            passwordInput.type = isPassword ? 'text' : 'password';
            const icon = document.getElementById('passwordVisibilityIcon');
            if (icon) icon.textContent = isPassword ? 'visibility' : 'visibility_off';
        });
    }

    if (passwordInput) {
        passwordInput.addEventListener('input', validatePasswordRequirements);
    }

    if (authForm) {
        authForm.addEventListener('submit', handleFormSubmit);
    }
}

/**
 * Toggle between Sign Up and Sign In modes
 */
function toggleAuthMode() {
    isSignUp = !isSignUp;
    const authTitle = document.getElementById('authTitle');
    const authSubtitle = document.getElementById('authSubtitle');
    const fullNameGroup = document.getElementById('fullNameGroup');
    const fullNameInput = document.getElementById('fullNameInput');
    const passwordRequirements = document.getElementById('passwordRequirements');
    const submitBtnText = document.getElementById('submitBtnText');
    const switchPrompt = document.getElementById('switchPrompt');
    const switchModeBtn = document.getElementById('switchModeBtn');
    const authAlert = document.getElementById('authAlert');

    if (authAlert) authAlert.classList.add('hidden');

    if (isSignUp) {
        if (authTitle) authTitle.textContent = 'Sign Up';
        if (authSubtitle) authSubtitle.textContent = 'Create your account to run biomechanical movement analysis.';
        if (fullNameGroup) fullNameGroup.classList.remove('hidden');
        if (fullNameInput) fullNameInput.required = true;
        if (passwordRequirements) passwordRequirements.classList.remove('hidden');
        if (submitBtnText) submitBtnText.textContent = 'Sign Up';
        if (switchPrompt) switchPrompt.textContent = 'Already have an account?';
        if (switchModeBtn) switchModeBtn.textContent = 'Sign In';
    } else {
        if (authTitle) authTitle.textContent = 'Sign In';
        if (authSubtitle) authSubtitle.textContent = 'Welcome back! Enter your credentials to access your dashboard.';
        if (fullNameGroup) fullNameGroup.classList.add('hidden');
        if (fullNameInput) fullNameInput.required = false;
        if (passwordRequirements) passwordRequirements.classList.add('hidden');
        if (submitBtnText) submitBtnText.textContent = 'Sign In';
        if (switchPrompt) switchPrompt.textContent = "Don't have an account?";
        if (switchModeBtn) switchModeBtn.textContent = 'Sign Up';
    }
}

/**
 * Real-time password requirement validation
 */
function validatePasswordRequirements() {
    const password = document.getElementById('passwordInput')?.value || '';
    const reqLength = document.getElementById('reqLength');
    const reqUppercase = document.getElementById('reqUppercase');
    const reqNumber = document.getElementById('reqNumber');

    const hasLength = password.length >= 6;
    const hasUpper = /[A-Z]/.test(password);
    const hasNum = /[0-9]/.test(password);

    updateReqStyle(reqLength, hasLength);
    updateReqStyle(reqUppercase, hasUpper);
    updateReqStyle(reqNumber, hasNum);
}

function updateReqStyle(el, isValid) {
    if (!el) return;
    const icon = el.querySelector('.material-symbols-outlined');
    if (isValid) {
        el.className = 'flex items-center text-emerald-600 font-medium';
        if (icon) {
            icon.textContent = 'check_circle';
            icon.style.fontVariationSettings = "'FILL' 1";
        }
    } else {
        el.className = 'flex items-center text-outline';
        if (icon) {
            icon.textContent = 'radio_button_unchecked';
            icon.style.fontVariationSettings = "'FILL' 0";
        }
    }
}

/**
 * Handle Sign Up / Sign In Form Submission
 */
async function handleFormSubmit(e) {
    e.preventDefault();

    const fullName = document.getElementById('fullNameInput')?.value.trim();
    const email = document.getElementById('emailInput')?.value.trim();
    const password = document.getElementById('passwordInput')?.value.trim();
    const submitBtn = document.getElementById('submitBtn');
    const submitBtnText = document.getElementById('submitBtnText');
    const submitBtnIcon = document.getElementById('submitBtnIcon');

    if (!email || !password || (isSignUp && !fullName)) {
        showAlert('Please fill in all required fields.', 'error');
        return;
    }

    // Set Loading State
    if (submitBtn) submitBtn.disabled = true;
    if (submitBtnText) submitBtnText.textContent = isSignUp ? 'Creating Account...' : 'Signing In...';
    if (submitBtnIcon) submitBtnIcon.classList.add('animate-spin');

    const endpoint = isSignUp ? `${API_BASE_URL}/signup` : `${API_BASE_URL}/login`;
    const payload = isSignUp ? { full_name: fullName, email, password } : { email, password };

    try {
        console.log(`[AERIS Auth] Sending POST to ${endpoint}`);
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Authentication failed');
        }

        console.log('[AERIS Auth] Success response:', data);
        showAlert(data.message || 'Success! Redirecting to dashboard...', 'success');

        // Save Auth Session to localStorage
        localStorage.setItem('aeris_token', data.access_token);
        localStorage.setItem('aeris_user', JSON.stringify(data.user));

        // Redirect to Dashboard after 1 second
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 1000);

    } catch (err) {
        console.error('[AERIS Auth] Error:', err);
        showAlert(err.message || 'An error occurred during authentication.', 'error');
        resetSubmitButton();
    }
}

function showAlert(message, type) {
    const alertBox = document.getElementById('authAlert');
    if (!alertBox) return;

    alertBox.textContent = message;
    alertBox.classList.remove('hidden');

    if (type === 'error') {
        alertBox.className = 'p-4 rounded-xl text-xs font-medium mb-6 bg-rose-50 border border-rose-200 text-rose-800';
    } else {
        alertBox.className = 'p-4 rounded-xl text-xs font-medium mb-6 bg-emerald-50 border border-emerald-200 text-emerald-800';
    }
}

function resetSubmitButton() {
    const submitBtn = document.getElementById('submitBtn');
    const submitBtnText = document.getElementById('submitBtnText');
    const submitBtnIcon = document.getElementById('submitBtnIcon');

    if (submitBtn) submitBtn.disabled = false;
    if (submitBtnText) submitBtnText.textContent = isSignUp ? 'Sign Up' : 'Sign In';
    if (submitBtnIcon) submitBtnIcon.classList.remove('animate-spin');
}
