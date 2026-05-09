/* Auto-open <details> blocks when the URL hash matches their id or an
   element inside them. Keeps deep-link anchors working after we folded
   troubleshooting/recipe H3/H4 sections into <details class="collapsible-issue">. */

function openDetailsForHash() {
  var hash = window.location.hash;
  if (!hash || hash.length < 2) return;
  var target;
  try {
    target = document.querySelector(hash);
  } catch (e) {
    return; // malformed selector
  }
  if (!target) return;

  // Walk up and open any ancestor <details> elements.
  var el = target;
  while (el && el !== document.body) {
    if (el.tagName && el.tagName.toLowerCase() === "details") {
      el.open = true;
    }
    el = el.parentElement;
  }

  // Re-scroll to ensure the target is in view after opening collapsed blocks.
  if (typeof target.scrollIntoView === "function") {
    target.scrollIntoView({ behavior: "instant", block: "start" });
  }
}

/* Material uses instant navigation — subscribe to document$ so this fires
   on both initial load and XHR page swaps. */
if (typeof document$ !== "undefined") {
  document$.subscribe(openDetailsForHash);
} else {
  document.addEventListener("DOMContentLoaded", openDetailsForHash);
}

/* Also run on hashchange (e.g. user clicks an in-page TOC link). */
window.addEventListener("hashchange", openDetailsForHash);
