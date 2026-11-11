/**
 * FoodBot in-app chatbot — talks to POST /chat and shows restaurant picks.
 */
import { animate } from "https://cdn.jsdelivr.net/npm/motion@12.23.12/+esm";

const toggle = document.getElementById("chat-toggle");
const panel = document.getElementById("chat-panel");
const closeBtn = document.getElementById("chat-close");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const log = document.getElementById("chat-log");
const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const history = [];

function openChat() {
  panel.classList.remove("hidden");
  panel.setAttribute("aria-hidden", "false");
  toggle.setAttribute("aria-expanded", "true");
  if (!reduce) {
    animate(panel, { opacity: [0, 1], y: [16, 0] }, { duration: 0.35, easing: [0.23, 1, 0.32, 1] });
  }
  input.focus();
}

function closeChat() {
  panel.classList.add("hidden");
  panel.setAttribute("aria-hidden", "true");
  toggle.setAttribute("aria-expanded", "false");
}

function appendBubble(role, text, picks = []) {
  const wrap = document.createElement("div");
  wrap.className = `chat-bubble chat-bubble--${role}`;

  const p = document.createElement("p");
  p.textContent = text;
  wrap.appendChild(p);

  if (picks.length) {
    const list = document.createElement("ul");
    list.className = "chat-picks";
    picks.forEach((r) => {
      const li = document.createElement("li");
      const score = Number(r.score ?? r.stars ?? 0).toFixed(1);
      li.innerHTML = `<strong>${r.name || r.business_id}</strong> · ${score}★ · ${r.city || ""}`;
      list.appendChild(li);
    });
    wrap.appendChild(list);
  }

  log.appendChild(wrap);
  log.scrollTop = log.scrollHeight;
  if (!reduce) {
    animate(wrap, { opacity: [0, 1], y: [8, 0] }, { duration: 0.3, easing: [0.23, 1, 0.32, 1] });
  }
}

async function sendChat(message) {
  appendBubble("user", message);
  history.push({ role: "user", content: message });

  const thinking = document.createElement("div");
  thinking.className = "chat-bubble chat-bubble--assistant chat-thinking";
  thinking.textContent = "Finding places…";
  log.appendChild(thinking);
  log.scrollTop = log.scrollHeight;

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        history: history.slice(-8),
        top_k: 5,
        method: "ltr",
      }),
    });
    thinking.remove();
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Chat failed (${res.status})`);
    }
    const data = await res.json();
    history.push({ role: "assistant", content: data.reply });
    appendBubble("assistant", data.reply, data.results || []);
  } catch (err) {
    thinking.remove();
    appendBubble("assistant", err.message || "Something went wrong. Try again.");
  }
}

toggle?.addEventListener("click", () => {
  if (panel.classList.contains("hidden")) openChat();
  else closeChat();
});

closeBtn?.addEventListener("click", closeChat);

form?.addEventListener("submit", (e) => {
  e.preventDefault();
  const msg = (input.value || "").trim();
  if (!msg) return;
  input.value = "";
  sendChat(msg);
});

document.querySelectorAll("[data-chat-prompt]").forEach((btn) => {
  btn.addEventListener("click", () => {
    if (panel.classList.contains("hidden")) openChat();
    sendChat(btn.dataset.chatPrompt);
  });
});

// Welcome once panel first opens
let welcomed = false;
toggle?.addEventListener("click", () => {
  if (!welcomed && !panel.classList.contains("hidden")) {
    welcomed = true;
    appendBubble(
      "assistant",
      "Hi — I'm FoodBot. Ask for a cuisine, vibe, or occasion and I'll recommend restaurants."
    );
  }
});
