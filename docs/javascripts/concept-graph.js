/* Interactive concept map for resources/concept-map.md.
   Reads assets/concept-graph.json (built by scripts/concept_graph_hook.py)
   and renders a force-directed graph of page cross-links with cytoscape.js.

   Controls:
     - Click a node to navigate to the page
     - Hover to highlight neighbors
     - Legend checkboxes filter by section
     - Fit-to-screen button re-centers the layout
*/

(function () {
  "use strict";

  const MOUNT_ID = "concept-graph";
  const JSON_URL_CANDIDATES = [
    "/lab-setup-guide/assets/concept-graph.json",
    "/assets/concept-graph.json",
    "../assets/concept-graph.json",
    "assets/concept-graph.json",
  ];

  function waitForCytoscape(cb, tries) {
    tries = tries || 0;
    if (typeof window.cytoscape !== "undefined") return cb();
    if (tries > 50) {
      console.error("[concept-graph] cytoscape failed to load");
      return;
    }
    setTimeout(function () { waitForCytoscape(cb, tries + 1); }, 100);
  }

  async function fetchJSON() {
    for (const url of JSON_URL_CANDIDATES) {
      try {
        const res = await fetch(url);
        if (res.ok) return await res.json();
      } catch (e) { /* try next */ }
    }
    throw new Error("concept-graph.json not found at any candidate URL");
  }

  function sectionLabel(section) {
    return section.replace(/-/g, " ").replace(/\b\w/g, c => c.toUpperCase());
  }

  function buildLegend(mount, sections, cy) {
    const wrap = document.createElement("div");
    wrap.className = "concept-graph__legend";
    sections.forEach(function (s) {
      const item = document.createElement("label");
      item.className = "concept-graph__legend-item";
      const cb = document.createElement("input");
      cb.type = "checkbox";
      cb.checked = true;
      cb.addEventListener("change", function () {
        const sel = cy.nodes('[section = "' + s.name + '"]');
        if (cb.checked) {
          sel.style("display", "element");
          sel.connectedEdges().style("display", "element");
        } else {
          sel.style("display", "none");
          sel.connectedEdges().style("display", "none");
        }
      });
      const swatch = document.createElement("span");
      swatch.className = "concept-graph__swatch";
      swatch.style.background = s.color;
      const text = document.createElement("span");
      text.textContent = sectionLabel(s.name) + " (" + s.count + ")";
      item.appendChild(cb);
      item.appendChild(swatch);
      item.appendChild(text);
      wrap.appendChild(item);
    });

    const fitBtn = document.createElement("button");
    fitBtn.type = "button";
    fitBtn.className = "concept-graph__fit";
    fitBtn.textContent = "Re-center";
    fitBtn.addEventListener("click", function () { cy.fit(cy.nodes(":visible"), 30); });
    wrap.appendChild(fitBtn);

    mount.appendChild(wrap);
  }

  async function render() {
    const mount = document.getElementById(MOUNT_ID);
    if (!mount) return;
    mount.innerHTML = '<div class="concept-graph__status">Loading graph…</div>';

    let data;
    try {
      data = await fetchJSON();
    } catch (e) {
      mount.innerHTML = '<div class="concept-graph__status concept-graph__status--error">'
        + 'Could not load concept-graph.json. Run <code>python scripts/concept_graph_hook.py</code> '
        + 'or rebuild the site.</div>';
      return;
    }

    // Count pages per section
    const sectionMap = new Map();
    data.nodes.forEach(function (n) {
      const s = n.data.section;
      const color = n.data.color;
      if (!sectionMap.has(s)) sectionMap.set(s, { name: s, color: color, count: 0 });
      sectionMap.get(s).count += 1;
    });
    const sections = Array.from(sectionMap.values()).sort((a, b) => a.name.localeCompare(b.name));

    mount.innerHTML = "";
    const canvas = document.createElement("div");
    canvas.className = "concept-graph__canvas";
    mount.appendChild(canvas);

    const cy = window.cytoscape({
      container: canvas,
      elements: data.nodes.concat(data.edges),
      layout: {
        name: "cose",
        animate: false,
        idealEdgeLength: 120,
        nodeOverlap: 20,
        nodeRepulsion: 8000,
        edgeElasticity: 100,
        gravity: 0.25,
        padding: 30,
      },
      style: [
        {
          selector: "node",
          style: {
            "background-color": "data(color)",
            "label": "data(label)",
            "color": "var(--md-default-fg-color, #222)",
            "font-size": "10px",
            "font-family": "var(--md-text-font-family, sans-serif)",
            "text-valign": "bottom",
            "text-halign": "center",
            "text-margin-y": 4,
            "text-wrap": "wrap",
            "text-max-width": 120,
            "width": 22,
            "height": 22,
            "border-width": 1,
            "border-color": "rgba(0,0,0,0.2)",
          },
        },
        {
          selector: "edge",
          style: {
            "width": 1,
            "line-color": "rgba(120,120,120,0.35)",
            "target-arrow-shape": "triangle",
            "target-arrow-color": "rgba(120,120,120,0.35)",
            "arrow-scale": 0.7,
            "curve-style": "bezier",
          },
        },
        {
          selector: "node.hover",
          style: { "border-width": 3, "border-color": "#bb0000", "width": 28, "height": 28 },
        },
        {
          selector: "edge.hover",
          style: { "line-color": "#bb0000", "target-arrow-color": "#bb0000", "width": 2 },
        },
        {
          selector: ".faded",
          style: { "opacity": 0.15 },
        },
      ],
    });

    cy.on("mouseover", "node", function (evt) {
      const node = evt.target;
      const neighborhood = node.closedNeighborhood();
      cy.elements().not(neighborhood).addClass("faded");
      node.addClass("hover");
      node.connectedEdges().addClass("hover");
    });
    cy.on("mouseout", "node", function () {
      cy.elements().removeClass("faded hover");
    });
    cy.on("tap", "node", function (evt) {
      const url = evt.target.data("url");
      if (url) window.location.href = url;
    });

    buildLegend(mount, sections, cy);
  }

  function init() {
    const mount = document.getElementById(MOUNT_ID);
    if (!mount) return;
    waitForCytoscape(render);
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(init);
  } else {
    document.addEventListener("DOMContentLoaded", init);
  }
})();
