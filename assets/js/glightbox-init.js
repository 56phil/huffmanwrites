/* GLightbox init for the /gallery/ landing page.
   Wires up the .glightbox link elements with touch navigation and
   looping enabled. The GLightbox library and CSS are vendored
   (assets/js/glightbox.min.js, assets/css/glightbox.min.css) and
   loaded via bundle.html before this script, so the library is
   defined by the time this runs. The self-check remains as a safety
   net. All 80 gallery cards render on every page (off-page ones are
   hidden with CSS), so the lightbox navigates the full gallery
   regardless of which page you start on. */
document.addEventListener('DOMContentLoaded', function() {
  if (typeof GLightbox !== 'function') return;
  GLightbox({
    selector: '.glightbox',
    touchNavigation: true,
    loop: true
  });
});
