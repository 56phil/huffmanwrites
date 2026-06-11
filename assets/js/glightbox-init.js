/* GLightbox init for the /gallery/ landing page.
   Wires up the .glightbox link elements with touch navigation and
   looping enabled. The GLightbox library and CSS are loaded from
   jsdelivr in layouts/_default/gallery.html. No-op when GLightbox
   is not yet loaded (e.g. on slow connections before the CDN
   script arrives). */
document.addEventListener('DOMContentLoaded', function() {
  if (typeof GLightbox !== 'function') return;
  GLightbox({
    selector: '.glightbox',
    touchNavigation: true,
    loop: true
  });
});
