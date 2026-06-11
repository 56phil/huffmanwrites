/* Reading progress indicator.
   Thin fixed bar at the top of the viewport that fills left-to-right
   as the user scrolls through the article body. Visually communicates
   reading depth on long-form posts. Respects prefers-reduced-motion
   (the transition is disabled in CSS for reduce-motion users). No-op
   when the required DOM elements are missing or JS is disabled.

   Loaded on every post page via layouts/_default/single.html. The
   bar/fill elements are also emitted from that same template, so
   the IIFE will exit early if either is absent. The article query
   selector includes .post-content (most post pages), .book-content-body
   (book detail pages), and .entry-content (any PaperMod post) for
   resilience. */
(function(){
  var bar = document.getElementById('reading-progress');
  var fill = document.getElementById('reading-progress-fill');
  var article = document.querySelector('.post-content, .book-content-body, .entry-content');
  if (!bar || !fill || !article) return;
  var ticking = false;
  function update() {
    var rect = article.getBoundingClientRect();
    var articleTop = window.scrollY + rect.top;
    var articleHeight = article.offsetHeight;
    var viewport = window.innerHeight;
    var scrolled = window.scrollY - articleTop;
    var trackable = Math.max(1, articleHeight - viewport);
    var pct = Math.min(100, Math.max(0, (scrolled / trackable) * 100));
    fill.style.width = pct + '%';
    bar.setAttribute('aria-valuenow', Math.round(pct));
    ticking = false;
  }
  function onScroll() {
    if (!ticking) {
      window.requestAnimationFrame(update);
      ticking = true;
    }
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll, { passive: true });
  update();
})();
