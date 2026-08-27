// Client-side filter/sort for the Scholarships hub (scholarships.html).
//
// Every scholarship card is already fully present in the static HTML —
// this script only shows/hides and reorders cards after the page loads.
// Search engine crawlers see the complete, unfiltered list regardless of
// JavaScript execution, which keeps every listing indexable.
(function () {
  "use strict";

  var grid = document.getElementById("scholarship-grid");
  if (!grid) return;

  var levelSelect = document.getElementById("filter-level");
  var countrySelect = document.getElementById("filter-country");
  var sortSelect = document.getElementById("filter-sort");
  var resetBtn = document.getElementById("filter-reset");
  var countNum = document.getElementById("filter-count-num");
  var noResults = document.getElementById("no-results");

  var cards = Array.prototype.slice.call(
    grid.querySelectorAll(".scholarship-card")
  );

  function cardLevels(card) {
    return (card.getAttribute("data-level") || "").split(/\s+/).filter(Boolean);
  }

  function apply() {
    var level = levelSelect.value;
    var country = countrySelect.value;
    var sort = sortSelect.value;

    var visible = [];

    cards.forEach(function (card) {
      var matchesLevel = level === "all" || cardLevels(card).indexOf(level) !== -1;
      var matchesCountry =
        country === "all" || card.getAttribute("data-country") === country;
      var show = matchesLevel && matchesCountry;
      card.hidden = !show;
      if (show) visible.push(card);
    });

    visible.sort(function (a, b) {
      if (sort === "deadline") {
        return a.getAttribute("data-deadline").localeCompare(
          b.getAttribute("data-deadline")
        );
      }
      var aPosted = a.getAttribute("data-posted");
      var bPosted = b.getAttribute("data-posted");
      return sort === "oldest"
        ? aPosted.localeCompare(bPosted)
        : bPosted.localeCompare(aPosted);
    });

    visible.forEach(function (card) {
      grid.appendChild(card);
    });

    if (countNum) countNum.textContent = String(visible.length);
    if (noResults) noResults.hidden = visible.length !== 0;
  }

  [levelSelect, countrySelect, sortSelect].forEach(function (el) {
    if (el) el.addEventListener("change", apply);
  });

  if (resetBtn) {
    resetBtn.addEventListener("click", function () {
      levelSelect.value = "all";
      countrySelect.value = "all";
      sortSelect.value = "newest";
      apply();
    });
  }

  apply();
})();
