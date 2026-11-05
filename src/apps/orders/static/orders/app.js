// Order desk enhancements. The page works without this script; it only adds a
// live quote (from /api/quote) and prevents double submits.
(() => {
  "use strict";

  const form = document.querySelector("[data-order-form]");
  const panel = document.querySelector("[data-quote]");
  if (!form || !panel) return;

  const el = {
    price: panel.querySelector("[data-quote-price]"),
    days: panel.querySelector("[data-quote-days]"),
    eta: panel.querySelector("[data-quote-eta]"),
    note: panel.querySelector("[data-quote-note]"),
    inline: form.querySelector("[data-inline-quote]"),
  };
  const quoteUrl = form.dataset.quoteUrl;
  const dateFormat = new Intl.DateTimeFormat(undefined, { weekday: "short", day: "numeric", month: "short" });

  let timer;
  let controller;

  function show({ state, price = "—", days = "—", eta = "—", note = "" }) {
    panel.dataset.state = state;
    el.price.textContent = price;
    el.days.textContent = days;
    el.eta.textContent = eta;
    el.note.textContent = note;
    if (el.inline) {
      el.inline.replaceChildren();
      if (state === "ready") {
        const strong = document.createElement("strong");
        strong.textContent = price;
        el.inline.append(strong, ` · arrives ${eta}`);
      }
    }
  }

  function idle(note = "Enter a weight to see the price.") {
    show({ state: "idle", note });
  }

  async function update() {
    const data = new FormData(form);
    const params = new URLSearchParams({
      zone: data.get("zone") || "",
      service: data.get("service") || "",
      weight_kg: (data.get("weight_kg") || "").toString().trim(),
    });
    const weight = Number(params.get("weight_kg"));
    if (!params.get("weight_kg") || !Number.isFinite(weight) || weight <= 0) {
      idle();
      return;
    }

    controller?.abort();
    controller = new AbortController();
    panel.dataset.state = "loading";

    try {
      const response = await fetch(`${quoteUrl}?${params}`, {
        headers: { Accept: "application/json" },
        signal: controller.signal,
      });
      const body = await response.json();
      if (!response.ok) {
        show({ state: "error", note: body.error || "Check the details and try again." });
        return;
      }
      const arrival = new Date();
      arrival.setDate(arrival.getDate() + body.delivery_days);
      show({
        state: "ready",
        price: `$${body.price.toFixed(2)}`,
        days: `${body.delivery_days} day${body.delivery_days === 1 ? "" : "s"}`,
        eta: dateFormat.format(arrival),
        note: "Price includes the zone base rate and $1.20 per kg.",
      });
    } catch (err) {
      if (err.name !== "AbortError") idle("Quote unavailable right now. You can still book.");
    }
  }

  form.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(update, 200);
  });

  form.addEventListener("submit", () => {
    const button = form.querySelector("[data-submit]");
    if (!button) return;
    // Defer so the button's value is still part of the submission.
    setTimeout(() => {
      button.disabled = true;
      button.setAttribute("data-loading", "");
      button.querySelector(".btn__label").textContent = "Booking…";
    }, 0);
  });

  update();
})();
