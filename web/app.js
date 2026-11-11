import { animate, stagger } from "https://cdn.jsdelivr.net/npm/motion@12.23.12/+esm";

const form = document.getElementById("search-form");
const queryEl = document.getElementById("query");
const cityEl = document.getElementById("city");
const priceEl = document.getElementById("price_max");
const vibeEl = document.getElementById("vibe");
const sortEl = document.getElementById("sort_by");
const submitBtn = document.getElementById("submit-btn");
const resultsEl = document.getElementById("results");
const parsedPanel = document.getElementById("parsed-panel");
const statusEl = document.getElementById("status");
const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function dollars(n) {
  const p = Number(n) || 0;
  return p > 0 ? "$".repeat(Math.min(4, p)) : "—";
}

function stars(n) {
  const v = Math.max(0, Math.min(5, Number(n) || 0));
  return `${v.toFixed(1)}★`;
}

/** API already returns score on a 0–5 scale. */
function withScore5(items) {
  return items.map((r) => ({
    ...r,
    score5: Math.round(Math.max(0, Math.min(5, Number(r.score) || 0)) * 10) / 10,
  }));
}

function chipList(parsed) {
  const chips = [];
  if (parsed.cuisines?.length) chips.push(...parsed.cuisines.map((c) => `Cuisine: ${c}`));
  if (parsed.quiet) chips.push("Quiet");
  if (parsed.romantic) chips.push("Date / romantic");
  if (parsed.vegetarian) chips.push("Vegetarian");
  if (parsed.vegan) chips.push("Vegan");
  if (parsed.city) chips.push(parsed.city);
  if (parsed.price_max) chips.push(`Max price ${"$".repeat(parsed.price_max)}`);
  if (parsed.occasion) chips.push(`Occasion: ${parsed.occasion}`);
  return chips;
}

function renderParsed(parsed) {
  const chips = chipList(parsed);
  parsedPanel.classList.remove("hidden");
  parsedPanel.innerHTML = `
    <h2>Understood</h2>
    <div class="chips">
      ${chips.length ? chips.map((c) => `<span class="chip">${c}</span>`).join("") : `<span class="chip">Open search</span>`}
    </div>
  `;
  if (!reduce) {
    animate(
      parsedPanel,
      { opacity: [0, 1], y: [10, 0] },
      { duration: 0.4, easing: [0.23, 1, 0.32, 1] }
    );
  }
}

function renderResults(items) {
  if (!items.length) {
    resultsEl.innerHTML = `<p class="empty">No restaurants matched. Try a broader query.</p>`;
    return;
  }

  const ranked = withScore5(items);

  resultsEl.innerHTML = ranked
    .map((r, i) => {
      const flags = [];
      if (r.quiet) flags.push("Quiet");
      if (r.romantic) flags.push("Romantic");
      if (r.vegetarian_friendly) flags.push("Vegetarian-friendly");
      if (r.noise_level) flags.push(`Noise: ${r.noise_level}`);

      return `
        <article class="result">
          <div class="rank">${i + 1}</div>
          <div class="result-body">
            <h3>${r.name || r.business_id}</h3>
            <p class="meta">
              ${r.city || "—"} · ${dollars(r.price_range)}
              · ${(r.review_count || 0).toLocaleString()} reviews
            </p>
            <p class="meta rating-line">
              <span class="rating">${stars(r.score5)}</span>
              <span class="rating-sub">match · Yelp ${stars(r.stars)}</span>
            </p>
            <p class="meta categories">${r.categories || ""}</p>
            <div class="flags">
              ${flags.map((f) => `<span class="flag">${f}</span>`).join("")}
            </div>
          </div>
        </article>
      `;
    })
    .join("");

  const cards = [...resultsEl.querySelectorAll(".result")];
  if (!reduce && cards.length) {
    cards.forEach((c) => {
      c.style.opacity = "0";
    });
    animate(
      cards,
      { opacity: [0, 1], y: [16, 0] },
      { delay: stagger(0.06), duration: 0.45, easing: [0.23, 1, 0.32, 1] }
    );
  }
}

function filterPayload() {
  const price = priceEl.value;
  return {
    city: cityEl.value || null,
    price_max: price ? Number(price) : null,
    vibe: vibeEl.value || "any",
    sort_by: sortEl.value || "match",
  };
}

async function loadHealth() {
  try {
    const res = await fetch("/health");
    if (!res.ok) throw new Error("Engine not ready");
    const data = await res.json();
    statusEl.textContent = `${data.restaurants_indexed} places · LTR ${data.ltr_loaded ? "on" : "off"}`;
  } catch {
    statusEl.textContent = "Engine offline — run setup scripts first";
  }
}

async function runSearch(query) {
  submitBtn.disabled = true;
  resultsEl.innerHTML = `<p class="empty">Searching…</p>`;

  try {
    const filters = filterPayload();
    const res = await fetch("/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query,
        method: "ltr",
        top_k: 10,
        use_filters: true,
        ...filters,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Search failed (${res.status})`);
    }

    const data = await res.json();
    renderParsed(data.parsed);
    renderResults(data.results);
    resultsEl.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (err) {
    parsedPanel.classList.add("hidden");
    resultsEl.innerHTML = `<p class="error">${err.message}</p>`;
  } finally {
    submitBtn.disabled = false;
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const q = queryEl.value.trim();
  if (q) runSearch(q);
});

document.getElementById("suggestions").addEventListener("click", (e) => {
  const btn = e.target.closest("button[data-q]");
  if (!btn) return;
  queryEl.value = btn.dataset.q;
  runSearch(btn.dataset.q);
});

loadHealth();
