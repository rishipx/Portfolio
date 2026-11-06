// Email tooltip
(function initEmailTooltip() {
    const emailBtn = document.getElementById('emailTriggerBtn');
    const tooltip = document.getElementById('emailTooltip');
    if (!emailBtn || !tooltip) return;

    const email = emailBtn.dataset.email || '';
    const emailEl = tooltip.querySelector('.email-tooltip-email');
    if (emailEl) emailEl.textContent = email;

    const copyBtn = tooltip.querySelector('.email-tooltip-copy-btn');

    let hideTimer = null;
    let copyTimer = null;

    function positionTooltip() {
        const r = emailBtn.getBoundingClientRect();
        tooltip.style.left = `${r.left + r.width / 2}px`;
        tooltip.style.top = `${r.top}px`;
    }

    function show() {
        clearTimeout(hideTimer);
        positionTooltip();
        tooltip.classList.add('visible');
        tooltip.setAttribute('aria-hidden', 'false');
    }

    function scheduleHide() {
        clearTimeout(hideTimer);
        hideTimer = setTimeout(() => {
            tooltip.classList.remove('visible');
            tooltip.setAttribute('aria-hidden', 'true');
            tooltip.classList.remove('copied');
        }, 120);
    }

    async function copyEmail(ev) {
        if (ev) { ev.preventDefault(); ev.stopPropagation(); }
        let ok = false;
        try {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                await navigator.clipboard.writeText(email);
                ok = true;
            }
        } catch (err) { /* fall back to execCommand */ }
        if (!ok) {
            let ta = null;
            try {
                ta = document.createElement('textarea');
                ta.value = email;
                ta.setAttribute('readonly', '');
                ta.style.position = 'fixed';
                ta.style.top = '-100px';
                ta.style.opacity = '0';
                document.body.appendChild(ta);
                ta.select();
                ok = document.execCommand('copy');
            } catch (err) {
                ok = false;
            } finally {
                if (ta && ta.parentNode) ta.parentNode.removeChild(ta);
            }
        }
        tooltip.classList.toggle('copied', ok);
        if (copyBtn) copyBtn.setAttribute('aria-label', ok ? 'Email address copied' : 'Copy email address');
        clearTimeout(copyTimer);
        copyTimer = setTimeout(() => {
            tooltip.classList.remove('copied');
            if (copyBtn) copyBtn.setAttribute('aria-label', 'Copy email address');
        }, 1800);
    }

    emailBtn.addEventListener('mouseenter', show);
    emailBtn.addEventListener('mouseleave', scheduleHide);
    emailBtn.addEventListener('focus', show);
    emailBtn.addEventListener('blur', scheduleHide);

    tooltip.addEventListener('mouseenter', show);
    tooltip.addEventListener('mouseleave', scheduleHide);

    if (copyBtn) copyBtn.addEventListener('click', copyEmail);

    window.addEventListener('scroll', () => {
        if (tooltip.classList.contains('visible')) positionTooltip();
    }, { passive: true });
    window.addEventListener('resize', () => {
        if (tooltip.classList.contains('visible')) positionTooltip();
    }, { passive: true });
})();
