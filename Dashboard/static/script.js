/**
 * AI Office Pilot — Dashboard JavaScript
 */

// ─── Mobile Menu Functionality ───
let isMobileMenuOpen = false;

function toggleMobileMenu() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    const menuToggle = document.querySelector('.menu-toggle');
    
    isMobileMenuOpen = !isMobileMenuOpen;
    
    if (isMobileMenuOpen) {
        sidebar.classList.add('active');
        overlay.classList.add('active');
        menuToggle.classList.add('active');
        menuToggle.setAttribute('aria-expanded', 'true');
        document.body.style.overflow = 'hidden';
    } else {
        sidebar.classList.remove('active');
        overlay.classList.remove('active');
        menuToggle.classList.remove('active');
        menuToggle.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
    }
}

function closeMobileMenu() {
    if (isMobileMenuOpen) {
        toggleMobileMenu();
    }
}

// Close menu when clicking on overlay
const overlay = document.querySelector('.sidebar-overlay');
if (overlay) {
    overlay.addEventListener('click', closeMobileMenu);
}

// Close menu when clicking on nav links (mobile)
const navLinks = document.querySelectorAll('.nav-links a');
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        if (window.innerWidth <= 768) {
            closeMobileMenu();
        }
    });
});

// Close menu on escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isMobileMenuOpen) {
        closeMobileMenu();
    }
});

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

// ─── Notification Functions with ARIA Support ───
async function toggleNotifications() {
    const dropdown = document.getElementById('notificationDropdown');
    const bellBtn = document.querySelector('.bell-btn');
    const isExpanded = dropdown.hasAttribute('hidden');
    
    if (isExpanded) {
        dropdown.removeAttribute('hidden');
        bellBtn.setAttribute('aria-expanded', 'true');
        await loadNotifications();
    } else {
        dropdown.setAttribute('hidden', 'true');
        bellBtn.setAttribute('aria-expanded', 'false');
    }
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