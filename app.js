const DATA_URL = "./data/words.json";
const STATUSES_API_URL = "/api/statuses";
const STATUS_TEXT = {
  known: "熟词",
  fuzzy: "模糊",
  unknown: "不会",
};

const categoryList = document.querySelector("#category-list");
const categoryTemplate = document.querySelector("#category-template");
const cardTemplate = document.querySelector("#card-template");
const quickNavSelect = document.querySelector("#quick-nav-select");
const filterButtons = [...document.querySelectorAll("[data-filter]")];
const statTargets = {
  total: document.querySelector("#total-count"),
  known: document.querySelector("#known-count"),
  fuzzy: document.querySelector("#fuzzy-count"),
  unknown: document.querySelector("#unknown-count"),
};

let dataset = null;
let statuses = {};
let activeFilter = "all";

bootstrap();

async function bootstrap() {
  const [wordsResponse, statusesResponse] = await Promise.all([
    fetch(DATA_URL),
    fetch(STATUSES_API_URL),
  ]);
  dataset = await wordsResponse.json();
  statuses = (await statusesResponse.json()).statuses ?? {};
  bindFilters();
  renderQuickNav();
  render();
}

function bindFilters() {
  filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      activeFilter = button.dataset.filter;
      filterButtons.forEach((item) =>
        item.classList.toggle("is-active", item.dataset.filter === activeFilter)
      );
      render();
    });
  });
}

function render() {
  updateStats();
  renderCategories();
}

function updateStats() {
  const totalWords = dataset.categories.reduce(
    (sum, category) => sum + category.words.length,
    0
  );

  const counts = {
    known: 0,
    fuzzy: 0,
    unknown: 0,
  };

  Object.values(statuses).forEach((value) => {
    if (counts[value] !== undefined) {
      counts[value] += 1;
    }
  });

  statTargets.total.textContent = totalWords;
  statTargets.known.textContent = counts.known;
  statTargets.fuzzy.textContent = counts.fuzzy;
  statTargets.unknown.textContent = counts.unknown;
}

function renderCategories() {
  categoryList.innerHTML = "";

  dataset.categories.forEach((category, index) => {
    const visibleWords = category.words.filter((word) => matchesFilter(word.word));
    if (visibleWords.length === 0) {
      return;
    }

    const fragment = categoryTemplate.content.cloneNode(true);
    const section = fragment.querySelector(".category-section");
    const title = fragment.querySelector(".category-title");
    const count = fragment.querySelector(".category-count");
    const grid = fragment.querySelector(".word-grid");

    section.id = `category-${index}`;
    section.dataset.categoryIndex = String(index);
    title.textContent = category.title;
    count.textContent = `${visibleWords.length} / ${category.words.length}`;

    visibleWords.forEach((word) => {
      grid.appendChild(createCard(word));
    });

    categoryList.appendChild(section);
  });

  syncQuickNav();
}

function renderQuickNav() {
  quickNavSelect.addEventListener("change", () => {
    const target = document.getElementById(quickNavSelect.value);
    if (!target) {
      return;
    }
    target.scrollIntoView({ behavior: "smooth", block: "start" });
  });
}

function syncQuickNav() {
  const visibleSections = [...document.querySelectorAll(".category-section")];
  const previousValue = quickNavSelect.value;

  quickNavSelect.innerHTML = "";

  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = visibleSections.length
    ? "选择分类并跳转"
    : "当前筛选下没有可跳转分类";
  quickNavSelect.appendChild(placeholder);

  visibleSections.forEach((section) => {
    const index = Number(section.dataset.categoryIndex);
    const option = document.createElement("option");
    option.value = section.id;
    option.textContent = dataset.categories[index].title.split("（")[0];
    quickNavSelect.appendChild(option);
  });

  const hasPrevious = [...quickNavSelect.options].some(
    (option) => option.value === previousValue
  );
  quickNavSelect.value = hasPrevious ? previousValue : "";
  quickNavSelect.disabled = visibleSections.length === 0;
}

function matchesFilter(word) {
  if (activeFilter === "all") {
    return true;
  }
  if (activeFilter === "unlearned") {
    return statuses[word] === undefined;
  }
  return statuses[word] === activeFilter;
}

function createCard(word) {
  const fragment = cardTemplate.content.cloneNode(true);
  const card = fragment.querySelector(".word-card");
  const wordIndex = fragment.querySelector(".word-index");
  const wordText = fragment.querySelector(".word-text");
  const translation = fragment.querySelector(".word-translation");
  const ipa = fragment.querySelector(".word-ipa");
  const partOfSpeech = fragment.querySelector(".part-of-speech");
  const audioButton = fragment.querySelector(".audio-button");
  const statusButtons = [...fragment.querySelectorAll(".status-button")];

  card.dataset.word = word.word;
  wordIndex.textContent = `#${word.index}`;
  wordText.textContent = formatDisplayWord(word.word);
  translation.textContent = word.translation;
  ipa.textContent = word.ipa;
  partOfSpeech.textContent = word.partOfSpeech;

  card.addEventListener("click", (event) => {
    if (
      event.target.closest(".audio-button") ||
      event.target.closest(".status-button")
    ) {
      return;
    }
    card.classList.toggle("is-flipped");
  });

  audioButton.addEventListener("click", (event) => {
    event.stopPropagation();
    playPronunciation(word.word);
  });

  statusButtons.forEach((button) => {
    const isActive = statuses[word.word] === button.dataset.status;
    button.classList.toggle("is-selected", isActive);
    button.setAttribute("aria-pressed", String(isActive));

    button.addEventListener("click", (event) => {
      event.stopPropagation();
      const nextStatus = button.dataset.status;
      void saveStatus(word.word, nextStatus);
    });
  });

  const currentStatus = statuses[word.word];
  if (currentStatus) {
    card.dataset.status = currentStatus;
    card.title = `当前标记：${STATUS_TEXT[currentStatus]}`;
  }

  return fragment;
}

function playPronunciation(word) {
  const audio = new Audio(
    `https://dict.youdao.com/dictvoice?audio=${encodeURIComponent(word)}&type=2`
  );
  audio.play().catch(() => {
    window.alert(`暂时无法播放 ${word} 的读音，请稍后再试。`);
  });
}

function formatDisplayWord(word) {
  return word.toLowerCase();
}

async function saveStatus(word, status) {
  const previousStatus = statuses[word];
  statuses[word] = status;
  render();

  try {
    const response = await fetch(STATUSES_API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ word, status }),
    });

    if (!response.ok) {
      throw new Error(`Request failed with ${response.status}`);
    }
  } catch (error) {
    if (previousStatus === undefined) {
      delete statuses[word];
    } else {
      statuses[word] = previousStatus;
    }
    render();
    window.alert("保存失败，请确认本地服务仍在运行。");
  }
}
