/**
 * AI Office Pilot — Dashboard JavaScript
 */

// ─── Auto-refresh status ───
let refreshInterval = null;

function startAutoRefresh(seconds = 30) {
    refreshInterval = setInterval(async () => {
        try {
            const res = await fetch('/api/status');
            if (res.ok) {
                const data = await res.json();
                updateDashboard(data);
            }
        } catch (e) {
            console.log('Status refresh failed:', e);
        }
    }, seconds * 1000);
}

function updateDashboard(data) {
    // Update RAM
    const ramEl = document.querySelector('[data-metric="ram"]');
    if (ramEl) ramEl.textContent = data.health.ram.percent + '%';

    // Update learning score
    const scoreEl = document.querySelector('[data-metric="score"]');
    if (scoreEl && data.learning) {
        scoreEl.textContent = data.learning.learning_score;
    }
}

// ─── Notifications ───
function showNotification(title, body, type = 'info') {
    // Desktop notification
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, { body, icon: '🤖' });
    }

    // In-page toast
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <strong>${title}</strong>
        <p>${body}</p>
    `;
    document.body.appendChild(toast);

    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// ─── Keyboard shortcuts ───
document.addEventListener('keydown', (e) => {
    // Ctrl+Shift+R = Run cycle
    if (e.ctrlKey && e.shiftKey && e.key === 'R') {
        e.preventDefault();
        if (typeof runCycle === 'function') runCycle();
    }

    // Ctrl+Shift+L = Lock
    if (e.ctrlKey && e.shiftKey && e.key === 'L') {
        e.preventDefault();
        window.location = '/logout';
    }
});

// ─── Request notification permission ───
if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
}

// ─── Start auto-refresh on dashboard page ───
if (document.querySelector('.activity-feed')) {
    startAutoRefresh(30);
}

console.log('🤖 AI Office Pilot Dashboard loaded');