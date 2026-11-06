// Theme toggle
const hangingLamp = document.getElementById('hanging-lamp');
const htmlEl = document.documentElement;

const themeColorMeta = document.querySelector('meta[name="theme-color"]');

function syncLampState(theme) {
    if (hangingLamp) {
        hangingLamp.setAttribute('aria-pressed', String(theme === 'light'));
    }
    if (themeColorMeta) {
        themeColorMeta.setAttribute('content', theme === 'light' ? '#F4F2ED' : '#000000');
    }
}

function toggleTheme() {
    const next = htmlEl.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    htmlEl.setAttribute('data-theme', next);
    try {
        localStorage.setItem('theme', next);
    } catch (error) {
        // Storage may be blocked; the theme still switches.
    }
    syncLampState(next);
}

// Dark is the default; a saved choice overrides it
let savedTheme = null;
try {
    savedTheme = localStorage.getItem('theme');
} catch (error) {
    // Storage may be blocked.
}
const initialTheme = savedTheme === 'light' ? 'light' : 'dark';
htmlEl.setAttribute('data-theme', initialTheme);
syncLampState(initialTheme);

// Hanging lamp: same toggle, plus a pull animation
let lampPullTimer = null;
if (hangingLamp) {
    hangingLamp.addEventListener('click', () => {
        toggleTheme();
        hangingLamp.classList.remove('pulled');
        void hangingLamp.offsetWidth; // force reflow to restart the animation
        hangingLamp.classList.add('pulled');
        clearTimeout(lampPullTimer);
        lampPullTimer = setTimeout(() => {
            hangingLamp.classList.remove('pulled');
        }, 620);
    });
}
