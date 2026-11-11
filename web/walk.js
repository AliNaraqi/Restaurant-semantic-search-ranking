/**
 * Silent walk-into-restaurant intro (Motion).
 * entrance → dining → kitchen — no caption text.
 */
import { animate, stagger } from "https://cdn.jsdelivr.net/npm/motion@12.23.12/+esm";

const STEPS = [
  { scene: "entrance", holdMs: 2000 },
  { scene: "dining", holdMs: 2200 },
  { scene: "kitchen", holdMs: 2400 },
];

const KITCHEN_PHOTO =
  "url('https://images.unsplash.com/photo-1556910103-1c02745aae4d?auto=format&fit=crop&w=1920&q=80')";

const PRELOAD = [
  "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=1920&q=80",
  "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=1920&q=80",
  "https://images.unsplash.com/photo-1556910103-1c02745aae4d?auto=format&fit=crop&w=1920&q=80",
];

const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function sleep(ms) {
  return new Promise((r) => window.setTimeout(r, ms));
}

async function revealUi() {
  const shell = document.getElementById("app-shell");
  const hero = document.getElementById("hero");
  if (!shell) return;

  if (reduce) {
    shell.style.opacity = "1";
    shell.style.transform = "none";
    return;
  }

  await animate(
    shell,
    { opacity: [0, 1], y: [18, 0] },
    { duration: 0.7, easing: [0.23, 1, 0.32, 1] }
  ).finished;

  if (hero) {
    const kids = [...hero.children];
    kids.forEach((el) => {
      el.style.opacity = "0";
      el.style.transform = "translateY(14px)";
    });
    animate(
      kids,
      { opacity: [0, 1], y: [14, 0] },
      { delay: stagger(0.08), duration: 0.55, easing: [0.23, 1, 0.32, 1] }
    );
  }
}

async function finishWalk(walk) {
  document.body.classList.remove("is-walking");
  document.body.classList.add("walk-done");

  const ambient = document.getElementById("ambient-photo");
  if (ambient) {
    ambient.style.backgroundImage = [
      "linear-gradient(105deg, rgba(20, 10, 6, 0.88) 0%, rgba(20, 10, 6, 0.5) 45%, rgba(20, 10, 6, 0.3) 100%)",
      KITCHEN_PHOTO,
    ].join(", ");
  }

  if (walk) {
    await animate(walk, { opacity: 0 }, { duration: 0.7, easing: "ease-out" }).finished;
    walk.remove();
  }

  await revealUi();
}

async function showScene(scenes, step) {
  const active = scenes.find((s) => s.dataset.scene === step.scene);
  if (!active) return;

  scenes.forEach((s) => {
    s.classList.remove("is-active");
    s.style.opacity = "0";
    s.style.zIndex = "0";
  });

  active.classList.add("is-active");
  active.style.zIndex = "1";
  active.style.transformOrigin = "50% 55%";

  if (reduce) {
    active.style.opacity = "1";
    active.style.transform = "scale(1.08)";
    return;
  }

  await animate(
    active,
    {
      opacity: [0, 1],
      scale: [1.0, 1.16],
      filter: ["brightness(0.75)", "brightness(1.05)"],
    },
    { duration: step.holdMs / 1000, easing: [0.22, 1, 0.36, 1] }
  ).finished;
}

async function runWalk() {
  const walk = document.getElementById("walk");
  const skip = document.getElementById("walk-skip");
  if (!walk) return;

  let cancelled = false;
  const cancel = async () => {
    if (cancelled) return;
    cancelled = true;
    await finishWalk(walk);
  };
  skip?.addEventListener("click", () => cancel(), { once: true });

  if (reduce) {
    await cancel();
    return;
  }

  await Promise.all(
    PRELOAD.map(
      (src) =>
        new Promise((resolve) => {
          const img = new Image();
          img.onload = resolve;
          img.onerror = resolve;
          img.src = src;
        })
    )
  );

  if (cancelled) return;

  const scenes = [...walk.querySelectorAll(".walk-scene")];

  for (const step of STEPS) {
    if (cancelled) return;
    walk.dataset.step = step.scene;
    await showScene(scenes, step);
    await sleep(120);
  }

  if (!cancelled) await finishWalk(walk);
}

runWalk();
