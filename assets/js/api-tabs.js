/* API page tab switcher.
   Switches the active tab in the .usage-tabs / .tab-content groups
   on the /api/ landing page. Clicking a .tab-button with a
   data-tab="<id>" attribute shows the .tab-content with the matching
   id and hides the others.

   Loaded only on /api/ via layouts/api/list.html. No-op when the
   required DOM elements are missing. */
document.addEventListener('DOMContentLoaded', function() {
  var tabButtons = document.querySelectorAll('.tab-button');
  var tabContents = document.querySelectorAll('.tab-content');

  tabButtons.forEach(function(button) {
    button.addEventListener('click', function() {
      var targetTab = this.getAttribute('data-tab');

      tabButtons.forEach(function(btn) { btn.classList.remove('active'); });
      tabContents.forEach(function(content) { content.classList.remove('active'); });

      this.classList.add('active');
      document.getElementById(targetTab).classList.add('active');
    });
  });
});
