// Page scrollbar: a custom thumb that mirrors the window scroll position
const scrollTrack = document.getElementById('custom-scrollbar-track');
const scrollThumb = document.getElementById('custom-scrollbar-thumb');
let isDraggingThumb = false;
let scrollFrame = 0;

function scrollMetrics() {
    const viewport = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    const thumbHeight = Math.max(32, (viewport / documentHeight) * viewport);
    return {
        maxScroll: Math.max(documentHeight - viewport, 1),
        thumbHeight,
        maxThumbTop: viewport - thumbHeight,
    };
}

function updateCustomScrollbar() {
    scrollFrame = 0;
    const { maxScroll, thumbHeight, maxThumbTop } = scrollMetrics();
    const fraction = Math.min(1, Math.max(0, window.scrollY / maxScroll));
    scrollThumb.style.height = `${thumbHeight}px`;
    scrollThumb.style.top = `${fraction * maxThumbTop}px`;
}

function requestScrollbarUpdate() {
    if (!scrollFrame) scrollFrame = requestAnimationFrame(updateCustomScrollbar);
}

function scrollFromPointer(clientY) {
    const { maxScroll, thumbHeight, maxThumbTop } = scrollMetrics();
    const targetThumbTop = Math.min(maxThumbTop, Math.max(0, clientY - thumbHeight / 2));
    const fraction = maxThumbTop > 0 ? targetThumbTop / maxThumbTop : 0;
    window.scrollTo({ top: fraction * maxScroll, behavior: isDraggingThumb ? 'auto' : 'smooth' });
}

function stopDragging() {
    isDraggingThumb = false;
    scrollThumb.classList.remove('dragging');
    document.documentElement.classList.remove('is-scroll-dragging');
}

// Pointer events cover mouse, touch and pen. The track captures the pointer, so a drag
// keeps working when the cursor or finger leaves the thin track.
scrollTrack.addEventListener('pointerdown', (event) => {
    if (event.pointerType === 'mouse' && event.button !== 0) return;
    event.preventDefault();
    scrollTrack.setPointerCapture(event.pointerId);
    scrollFromPointer(event.clientY); // glides to the pressed spot; the drag itself follows instantly
    isDraggingThumb = true;
    scrollThumb.classList.add('dragging');
    document.documentElement.classList.add('is-scroll-dragging');
});
scrollTrack.addEventListener('pointermove', (event) => {
    if (isDraggingThumb) scrollFromPointer(event.clientY);
});
['pointerup', 'pointercancel', 'lostpointercapture'].forEach((type) => {
    scrollTrack.addEventListener(type, stopDragging);
});
window.addEventListener('blur', stopDragging);

window.addEventListener('scroll', requestScrollbarUpdate, { passive: true });
window.addEventListener('resize', requestScrollbarUpdate, { passive: true });
updateCustomScrollbar();
