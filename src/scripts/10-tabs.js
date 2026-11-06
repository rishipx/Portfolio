// Tabs (click and keyboard)
const experienceTabs = Array.from(document.querySelectorAll('.experience-tab'));
function activateExperienceTab(tab, moveFocus = false) {
    const target = tab.getAttribute('data-tab');
    experienceTabs.forEach((item) => {
        const isActive = item === tab;
        item.classList.toggle('active', isActive);
        item.setAttribute('aria-selected', String(isActive));
        item.tabIndex = isActive ? 0 : -1;
    });
    document.querySelectorAll('.experience-list').forEach((panel) => {
        panel.hidden = panel.getAttribute('data-panel') !== target;
    });
    if (moveFocus) tab.focus();
}
experienceTabs.forEach((tab, index) => {
    tab.addEventListener('click', () => activateExperienceTab(tab));
    tab.addEventListener('keydown', (event) => {
        let nextIndex = index;
        if (event.key === 'ArrowRight' || event.key === 'ArrowDown') nextIndex = (index + 1) % experienceTabs.length;
        else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') nextIndex = (index - 1 + experienceTabs.length) % experienceTabs.length;
        else if (event.key === 'Home') nextIndex = 0;
        else if (event.key === 'End') nextIndex = experienceTabs.length - 1;
        else return;
        event.preventDefault();
        activateExperienceTab(experienceTabs[nextIndex], true);
    });
});
