const form = document.getElementById("reviewForm");
const codeInput = document.getElementById("codeInput");
const statusPill = document.getElementById("statusPill");
const summaryOverview = document.getElementById("summaryOverview");
const summaryHighlights = document.getElementById("summaryHighlights");
const summaryNextSteps = document.getElementById("summaryNextSteps");
const lists = {
  critical: document.getElementById("criticalList"),
  best: document.getElementById("bestList"),
  performance: document.getElementById("performanceList"),
  strengths: document.getElementById("strengthList"),
};

// Dynamic heading elements
const dashboardTitle = document.getElementById("dashboardTitle");
const techChip = document.getElementById("techChip");
const performanceLabel = document.getElementById("performanceLabel");
const performanceDescription = document.getElementById("performanceDescription");
const performanceSectionTitle = document.getElementById("performanceSectionTitle");
const performancePlaceholder = document.getElementById("performancePlaceholder");

const endpoint = window.reviewDashboard?.endpoint ?? "/api/review/";

// Framework-specific labels
const frameworkLabels = {
  django: {
    title: "Django Code Review Dashboard",
    tech: "Django · HTML · CSS · Gemini API",
    performance: "Performance (ORM)",
    performanceDesc: "SQL/ORM tuning and efficiency.",
    performanceSection: "Performance & ORM",
    performancePlaceholder: "Query, ORM, and runtime insights will land here.",
  },
  react: {
    title: "React Code Review Dashboard",
    tech: "React · HTML · CSS · Gemini API",
    performance: "Performance (Rendering)",
    performanceDesc: "Component re-renders and bundle optimization.",
    performanceSection: "Performance & Rendering",
    performancePlaceholder: "Re-render, bundle size, and optimization insights will land here.",
  },
  nodejs: {
    title: "Node.js Code Review Dashboard",
    tech: "Node.js · HTML · CSS · Gemini API",
    performance: "Performance (Event Loop)",
    performanceDesc: "Event loop blocking and async efficiency.",
    performanceSection: "Performance & Event Loop",
    performancePlaceholder: "Event loop, async operations, and I/O insights will land here.",
  },
  express: {
    title: "Express.js Code Review Dashboard",
    tech: "Express.js · HTML · CSS · Gemini API",
    performance: "Performance (Middleware)",
    performanceDesc: "Middleware and route optimization.",
    performanceSection: "Performance & Middleware",
    performancePlaceholder: "Middleware, route, and database query insights will land here.",
  },
  nextjs: {
    title: "Next.js Code Review Dashboard",
    tech: "Next.js · HTML · CSS · Gemini API",
    performance: "Performance (SSR/SSG)",
    performanceDesc: "SSR/SSG and bundle optimization.",
    performanceSection: "Performance & SSR/SSG",
    performancePlaceholder: "SSR/SSG, image optimization, and bundle insights will land here.",
  },
  flask: {
    title: "Flask Code Review Dashboard",
    tech: "Flask · HTML · CSS · Gemini API",
    performance: "Performance (Routes)",
    performanceDesc: "Route and database query optimization.",
    performanceSection: "Performance & Routes",
    performancePlaceholder: "Route, database, and request handling insights will land here.",
  },
  fastapi: {
    title: "FastAPI Code Review Dashboard",
    tech: "FastAPI · HTML · CSS · Gemini API",
    performance: "Performance (Async)",
    performanceDesc: "Async/await and request optimization.",
    performanceSection: "Performance & Async",
    performancePlaceholder: "Async operations and request handling insights will land here.",
  },
  angular: {
    title: "Angular Code Review Dashboard",
    tech: "Angular · HTML · CSS · Gemini API",
    performance: "Performance (Change Detection)",
    performanceDesc: "Change detection and bundle optimization.",
    performanceSection: "Performance & Change Detection",
    performancePlaceholder: "Change detection, bundle size, and optimization insights will land here.",
  },
  vue: {
    title: "Vue.js Code Review Dashboard",
    tech: "Vue.js · HTML · CSS · Gemini API",
    performance: "Performance (Reactivity)",
    performanceDesc: "Reactivity system and bundle optimization.",
    performanceSection: "Performance & Reactivity",
    performancePlaceholder: "Reactivity, bundle size, and optimization insights will land here.",
  },
  python: {
    title: "Python Code Review Dashboard",
    tech: "Python · HTML · CSS · Gemini API",
    performance: "Performance",
    performanceDesc: "Algorithm and memory efficiency.",
    performanceSection: "Performance",
    performancePlaceholder: "Algorithm, memory, and I/O insights will land here.",
  },
  javascript: {
    title: "JavaScript Code Review Dashboard",
    tech: "JavaScript · HTML · CSS · Gemini API",
    performance: "Performance",
    performanceDesc: "Event loop and memory efficiency.",
    performanceSection: "Performance",
    performancePlaceholder: "Event loop, memory, and async insights will land here.",
  },
  typescript: {
    title: "TypeScript Code Review Dashboard",
    tech: "TypeScript · HTML · CSS · Gemini API",
    performance: "Performance",
    performanceDesc: "Type safety and runtime efficiency.",
    performanceSection: "Performance",
    performancePlaceholder: "Type safety, runtime, and optimization insights will land here.",
  },
  general: {
    title: "Code Review Dashboard",
    tech: "HTML · CSS · Gemini API",
    performance: "Performance",
    performanceDesc: "Performance optimization insights.",
    performanceSection: "Performance",
    performancePlaceholder: "Performance insights will land here.",
  },
};

const updateHeadings = (framework) => {
  const labels = frameworkLabels[framework] || frameworkLabels.general;
  
  if (dashboardTitle) dashboardTitle.textContent = labels.title;
  if (techChip) techChip.textContent = `Tech stack: ${labels.tech}`;
  if (performanceLabel) performanceLabel.textContent = labels.performance;
  if (performanceDescription) performanceDescription.textContent = labels.performanceDesc;
  if (performanceSectionTitle) performanceSectionTitle.textContent = labels.performanceSection;
  if (performancePlaceholder) performancePlaceholder.textContent = labels.performancePlaceholder;
};

const setStatus = (text, variant = "idle") => {
  statusPill.textContent = text;
  statusPill.classList.remove("active", "error");
  if (variant === "active") statusPill.classList.add("active");
  if (variant === "error") statusPill.classList.add("error");
};

const setCount = (key, value) => {
  const el = document.querySelector(`[data-count="${key}"]`);
  if (el) el.textContent = value;
};

const renderList = (container, items, formatter) => {
  container.innerHTML = "";
  container.classList.toggle("empty", items.length === 0);
  if (!items.length) {
    container.innerHTML = "<p>No data yet.</p>";
    return;
  }
  items.forEach((item) => container.appendChild(formatter(item)));
};

const issueCard = ({ title, details, severity }) => {
  const card = document.createElement("article");
  card.className = "issue-card";
  card.innerHTML = `
    <div class="issue-meta">${severity || "info"}</div>
    <h4>${title || "Untitled finding"}</h4>
    <p>${details || "No details provided."}</p>
  `;
  return card;
};

const bestCard = ({ title, details, status }) => {
  const card = document.createElement("article");
  card.className = "issue-card";
  card.innerHTML = `
    <div class="issue-meta">${status || "status"}</div>
    <h4>${title || "Pattern"}</h4>
    <p>${details || "No details provided."}</p>
  `;
  return card;
};

const performanceCard = ({ title, details, impact }) => {
  const card = document.createElement("article");
  card.className = "issue-card";
  card.innerHTML = `
    <div class="issue-meta">${impact || "performance"}</div>
    <h4>${title || "Observation"}</h4>
    <p>${details || "No details provided."}</p>
  `;
  return card;
};

const updateSummary = ({ overview, highlights, next_steps }) => {
  summaryOverview.textContent = overview ?? "No summary provided.";
  const renderTags = (el, items) => {
    el.innerHTML = "";
    el.classList.toggle("empty", !items.length);
    if (!items.length) {
      const li = document.createElement("li");
      li.textContent = "No data yet.";
      el.appendChild(li);
      return;
    }
    items.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      el.appendChild(li);
    });
  };
  renderTags(summaryHighlights, highlights || []);
  renderTags(summaryNextSteps, next_steps || []);
};

const updateStrengths = (items) => {
  lists.strengths.innerHTML = "";
  lists.strengths.classList.toggle("empty", !items.length);
  if (!items.length) {
    lists.strengths.innerHTML = "<li>No strengths reported yet.</li>";
    return;
  }
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    lists.strengths.appendChild(li);
  });
};

const disableForm = (state) => {
  form.querySelector("button[type=submit]").disabled = state;
  codeInput.readOnly = state;
};

form?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const code = codeInput.value.trim();
  if (!code) {
    setStatus("Paste code to review", "error");
    return;
  }

  const csrfToken = form.querySelector('input[name="csrfmiddlewaretoken"]').value;

  disableForm(true);
  setStatus("Analyzing with Gemini…", "active");

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify({ code }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data?.error || "Gemini request failed");
    }

    // Update dynamic headings based on detected tech
    if (data.detected_tech?.framework) {
      updateHeadings(data.detected_tech.framework);
    }

    updateSummary(data.summary || {});
    renderList(lists.critical, data.critical || [], issueCard);
    renderList(lists.best, data.best_practices || [], bestCard);
    renderList(lists.performance, data.performance || [], performanceCard);
    updateStrengths(data.strengths || []);

    setCount("critical", data.critical?.length || 0);
    setCount("best", data.best_practices?.length || 0);
    setCount("performance", data.performance?.length || 0);
    setCount("strengths", data.strengths?.length || 0);

    setStatus("Review updated", "active");
  } catch (error) {
    console.error(error);
    setStatus(error.message || "Unexpected error", "error");
  } finally {
    disableForm(false);
    setTimeout(() => setStatus("Idle"), 2500);
  }
});

