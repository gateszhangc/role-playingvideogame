const pathContent = {
  story: {
    kicker: "Story-first entry",
    title: "Look for RPGs built around party bonds and a clear dramatic arc.",
    body:
      "This lane favors authored characters, readable quest flow, and battles that support the story instead of overwhelming it. It is the easiest way to learn how builds, companions, and world stakes fit together."
  },
  tactics: {
    kicker: "Systems-first entry",
    title: "Choose an RPG where planning, dialogue checks, and layered encounters lead the pace.",
    body:
      "This path suits players who enjoy reading the battlefield, preparing a party, and watching the world respond to high-agency decisions. It teaches how rules, choice, and consequence lock together."
  },
  action: {
    kicker: "Momentum-first entry",
    title: "Start with an RPG that keeps direct movement and combat at the center.",
    body:
      "Action-focused RPGs are helpful if you want a familiar physical rhythm while still learning loot, stats, and skill trees. The numbers stay meaningful, but the controls remain immediate."
  },
  world: {
    kicker: "Routine-first entry",
    title: "Pick a shared-world RPG if long-term rituals and social identity are the draw.",
    body:
      "Persistent online worlds make progression feel communal. Daily routes, guilds, crafting, and role identity become the language that teaches you why progression systems matter over months, not hours."
  }
};

const header = document.querySelector("[data-header]");
const navLinks = Array.from(document.querySelectorAll(".site-nav a"));
const sections = navLinks
  .map((link) => document.querySelector(link.getAttribute("href")))
  .filter(Boolean);

const buttons = Array.from(document.querySelectorAll("[data-path]"));
const outputKicker = document.querySelector("[data-path-output-kicker]");
const outputTitle = document.querySelector("[data-path-output-title]");
const outputBody = document.querySelector("[data-path-output-body]");

const updatePath = (key) => {
  const entry = pathContent[key];
  if (!entry) {
    return;
  }

  outputKicker.textContent = entry.kicker;
  outputTitle.textContent = entry.title;
  outputBody.textContent = entry.body;

  buttons.forEach((button) => {
    const active = button.dataset.path === key;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-selected", String(active));
  });
};

buttons.forEach((button) => {
  button.addEventListener("click", () => {
    updatePath(button.dataset.path);
  });
});

const sectionObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) {
        return;
      }

      navLinks.forEach((link) => {
        const matches = link.getAttribute("href") === `#${entry.target.id}`;
        if (matches) {
          link.setAttribute("aria-current", "true");
        } else {
          link.removeAttribute("aria-current");
        }
      });
    });
  },
  {
    rootMargin: "-35% 0px -45% 0px",
    threshold: 0.05
  }
);

sections.forEach((section) => sectionObserver.observe(section));

const syncHeader = () => {
  header.classList.toggle("is-scrolled", window.scrollY > 12);
};

syncHeader();
window.addEventListener("scroll", syncHeader, { passive: true });
