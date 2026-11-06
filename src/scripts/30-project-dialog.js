// Project dialog

const projectDialog = document.getElementById('project-dialog');
const projectDialogTitle = document.getElementById('dialog-title');
const projectDialogKicker = document.getElementById('dialog-kicker');
const projectDialogStack = document.getElementById('dialog-stack');
const projectDialogReadme = document.getElementById('dialog-readme');
const projectDialogActions = projectDialog.querySelector('.dialog-actions');
const projectWebsiteLink = projectDialogActions.querySelector('a[aria-label="Open project website"]');
const projectSourceLink = projectDialogActions.querySelector('a[aria-label="Open project source"]');
const projectDialogPanel = projectDialog.querySelector('.project-dialog-panel');
const projectDialogClose = document.getElementById('dialog-close');
const projectDialogExpand = document.getElementById('dialog-expand');
const projectDialogExpandIcon = projectDialogExpand.querySelector('.dialog-expand-icon');
const projectDialogCollapseIcon = projectDialogExpand.querySelector('.dialog-collapse-icon');
let projectDialogOpener = null;

function setProjectDialogExpanded(expanded) {
    projectDialog.classList.toggle('is-expanded', expanded);
    projectDialogPanel.classList.toggle('is-expanded', expanded);
    projectDialogExpand.setAttribute('aria-expanded', String(expanded));
    projectDialogExpand.setAttribute('aria-label', expanded ? 'Restore project card size' : 'Expand project card');
    projectDialogExpand.title = expanded ? 'Restore card size' : 'Expand project card';
    // SVG elements have no .hidden property, so toggle the attribute.
    projectDialogExpandIcon.toggleAttribute('hidden', expanded);
    projectDialogCollapseIcon.toggleAttribute('hidden', !expanded);
}

function setOptionalProjectLink(anchor, url) {
    const isConfigured = typeof url === 'string' && url.trim() !== '' && url.trim() !== '#';
    anchor.hidden = !isConfigured;
    if (isConfigured) {
        anchor.href = url.trim();
        anchor.target = '_blank';
        anchor.rel = 'noopener noreferrer';
    } else {
        anchor.removeAttribute('target');
        anchor.removeAttribute('rel');
        anchor.href = '#';
    }
    return isConfigured;
}

function openProjectDialog(projectId, opener = document.activeElement) {
    const detail = projectDetails[projectId];
    if (!detail) return;

    projectDialogOpener = opener;
    projectDialogKicker.textContent = detail.kicker;
    projectDialogTitle.textContent = detail.title;
    // Hide the Stack label when there is nothing to list.
    projectDialogStack.previousElementSibling.hidden = detail.stack.length === 0;
    projectDialogStack.replaceChildren(...detail.stack.map((item) => {
        const badge = document.createElement('span');
        badge.className = 'dialog-stack-badge';
        badge.textContent = item;
        return badge;
    }));
    // Trusted HTML generated at build time from README.md.
    projectDialogReadme.innerHTML = detail.readme;

    const hasWebsite = setOptionalProjectLink(projectWebsiteLink, detail.website);
    const hasSource = setOptionalProjectLink(projectSourceLink, detail.source);
    projectDialogActions.hidden = !(hasWebsite || hasSource);
    setProjectDialogExpanded(false);

    projectDialog.classList.add('is-open');
    projectDialog.setAttribute('aria-hidden', 'false');
    document.body.classList.add('dialog-open');
    projectDialogClose.focus();
}

function closeProjectDialog() {
    if (!projectDialog.classList.contains('is-open')) return;
    setProjectDialogExpanded(false);
    projectDialog.classList.remove('is-open');
    projectDialog.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('dialog-open');
    if (projectDialogOpener && typeof projectDialogOpener.focus === 'function') projectDialogOpener.focus();
}

document.querySelectorAll('.project-card').forEach((card) => {
    card.addEventListener('click', (event) => {
        if (event.target.closest('a')) return;
        openProjectDialog(card.dataset.project, card);
    });
    card.addEventListener('keydown', (event) => {
        if ((event.key === 'Enter' || event.key === ' ') && !event.target.closest('a')) {
            event.preventDefault();
            openProjectDialog(card.dataset.project, card);
        }
    });
});

projectDialogClose.addEventListener('click', closeProjectDialog);
projectDialogExpand.addEventListener('click', () => {
    setProjectDialogExpanded(projectDialogExpand.getAttribute('aria-expanded') !== 'true');
});
projectDialog.addEventListener('click', (event) => {
    if (event.target === projectDialog) closeProjectDialog();
});
document.addEventListener('keydown', (event) => {
    if (!projectDialog.classList.contains('is-open')) return;
    if (event.key === 'Escape') {
        closeProjectDialog();
        return;
    }
    if (event.key === 'Tab') {
        const focusable = Array.from(projectDialog.querySelectorAll('button:not([disabled]):not([hidden]), a[href]:not([hidden]), [tabindex]:not([tabindex="-1"])'))
            .filter((element) => element.offsetParent !== null);
        if (!focusable.length) return;
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (event.shiftKey && document.activeElement === first) {
            event.preventDefault();
            last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
            event.preventDefault();
            first.focus();
        }
    }
});
