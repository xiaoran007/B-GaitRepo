const STATES = [
  ["ignore", "1"],
  ["normal", "2"],
  ["transition_nonfall", "3"],
  ["falling", "4"],
  ["post_fall", "5"],
  ["recovery", "6"],
];

const COLORS = {
  ignore: "var(--ignore)",
  normal: "var(--normal)",
  transition_nonfall: "var(--transition_nonfall)",
  falling: "var(--falling)",
  post_fall: "var(--post_fall)",
  recovery: "var(--recovery)",
};

const video = document.getElementById("video");
const sampleName = document.getElementById("sampleName");
const timeReadout = document.getElementById("timeReadout");
const dirtyBadge = document.getElementById("dirtyBadge");
const videoSelect = document.getElementById("videoSelect");
const stateButtons = document.getElementById("stateButtons");
const timelineEl = document.getElementById("timeline");
const inPointEl = document.getElementById("inPoint");
const outPointEl = document.getElementById("outPoint");
const segmentInfo = document.getElementById("segmentInfo");
const pathInfo = document.getElementById("pathInfo");
const previewInfo = document.getElementById("previewInfo");

let metadata = null;
let annotation = null;
let videos = [];
let selectedVideo = null;
let timeline = [];
let selectedState = "normal";
let selectedSegment = -1;
let inFrame = null;
let outFrame = null;
let dirty = false;
let drag = null;

function frameCount() {
  return metadata.video.frame_count || Math.max(1, Math.round(metadata.video.duration_sec * metadata.video.fps));
}

function lastFrame() {
  return Math.max(frameCount() - 1, 0);
}

function fps() {
  return metadata.video.fps || 30;
}

function currentFrame() {
  return clamp(Math.round(video.currentTime * fps()), 0, lastFrame());
}

function frameToTime(frame) {
  return frame / fps();
}

function clamp(value, low, high) {
  return Math.min(Math.max(value, low), high);
}

function markDirty(value = true) {
  dirty = value;
  dirtyBadge.textContent = dirty ? "unsaved" : "saved";
  dirtyBadge.classList.toggle("unsaved", dirty);
  document.title = `${dirty ? "*" : ""}B-8Fall-Demo Annotator`;
}

function formatFrame(frame) {
  if (frame === null || frame === undefined) return "unset";
  return `${frame} (${frameToTime(frame).toFixed(2)}s)`;
}

async function init() {
  const videoPayload = await fetchJson("/api/videos");
  videos = videoPayload.videos || [];
  selectedVideo = videoPayload.default_video || (videos[0] && videos[0].name);
  buildVideoSelect();
  buildStateButtons();
  await loadVideo(selectedVideo);
  renderAll();
  markDirty(false);
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

function buildStateButtons() {
  stateButtons.innerHTML = "";
  STATES.forEach(([state, key]) => {
    const button = document.createElement("button");
    button.className = "stateButton";
    button.dataset.state = state;
    button.innerHTML = `<span>${key}. ${state}</span><span class="swatch" style="background:${COLORS[state]}"></span>`;
    button.addEventListener("click", () => setSelectedState(state));
    stateButtons.appendChild(button);
  });
  setSelectedState(selectedState);
}

function buildVideoSelect() {
  videoSelect.innerHTML = "";
  videos.forEach((item) => {
    const option = document.createElement("option");
    option.value = item.name;
    option.textContent = item.name;
    videoSelect.appendChild(option);
  });
  videoSelect.value = selectedVideo;
  videoSelect.disabled = videos.length <= 1;
}

async function loadVideo(videoName) {
  if (!videoName) return;
  selectedVideo = videoName;
  metadata = await fetchJson(apiUrl("/api/metadata"));
  annotation = await fetchJson(apiUrl("/api/annotation"));
  timeline = normalizeTimeline(annotation.timeline || []);
  selectedSegment = -1;
  inFrame = null;
  outFrame = null;
  video.src = apiUrl("/video");
  video.load();
  sampleName.textContent = `${metadata.video.stem} · ${annotation.source}`;
  pathInfo.textContent = metadata.paths.annotation;
  previewInfo.textContent = metadata.paths.annotation_preview;
  videoSelect.value = selectedVideo;
  markDirty(false);
  renderAll();
}

function apiUrl(path) {
  const params = new URLSearchParams();
  if (selectedVideo) {
    params.set("video", selectedVideo);
  }
  return `${path}?${params.toString()}`;
}

function setSelectedState(state) {
  selectedState = state;
  document.querySelectorAll(".stateButton").forEach((button) => {
    button.classList.toggle("active", button.dataset.state === state);
  });
}

function normalizeTimeline(items) {
  const end = lastFrame();
  const clean = items
    .map((item) => ({
      start_frame: clamp(Number(item.start_frame) || 0, 0, end),
      end_frame: clamp(Number(item.end_frame) || 0, 0, end),
      state: COLORS[item.state] ? item.state : "normal",
    }))
    .map((item) => item.start_frame <= item.end_frame ? item : {
      start_frame: item.end_frame,
      end_frame: item.start_frame,
      state: item.state,
    })
    .sort((a, b) => a.start_frame - b.start_frame || a.end_frame - b.end_frame);

  const filled = [];
  let cursor = 0;
  clean.forEach((item) => {
    const start = Math.max(item.start_frame, cursor);
    const finish = Math.max(item.end_frame, start);
    if (start > cursor) {
      filled.push({ start_frame: cursor, end_frame: start - 1, state: "normal" });
    }
    if (start <= end) {
      filled.push({ start_frame: start, end_frame: Math.min(finish, end), state: item.state });
      cursor = Math.min(finish + 1, end + 1);
    }
  });
  if (cursor <= end) {
    filled.push({ start_frame: cursor, end_frame: end, state: "normal" });
  }
  return mergeAdjacent(filled);
}

function mergeAdjacent(items) {
  const merged = [];
  items.forEach((item) => {
    const prev = merged[merged.length - 1];
    if (prev && prev.state === item.state && prev.end_frame + 1 >= item.start_frame) {
      prev.end_frame = Math.max(prev.end_frame, item.end_frame);
    } else {
      merged.push({ ...item });
    }
  });
  return merged;
}

function renderAll() {
  renderTimeline();
  renderReadouts();
}

function renderTimeline() {
  timelineEl.innerHTML = "";
  const total = Math.max(frameCount(), 1);
  timeline.forEach((segment, index) => {
    const div = document.createElement("div");
    div.className = `segment${index === selectedSegment ? " selected" : ""}`;
    div.style.left = `${segment.start_frame / total * 100}%`;
    div.style.width = `${(segment.end_frame - segment.start_frame + 1) / total * 100}%`;
    div.style.background = COLORS[segment.state];
    div.title = `${segment.state}: ${formatFrame(segment.start_frame)} - ${formatFrame(segment.end_frame)}`;
    div.addEventListener("click", (event) => {
      event.stopPropagation();
      selectedSegment = index;
      seekToFrame(frameFromTimelineEvent(event));
      renderAll();
    });
    div.appendChild(makeHandle("left", index));
    div.appendChild(makeHandle("right", index));
    timelineEl.appendChild(div);
  });

  addMarker("playhead", currentFrame());
  if (inFrame !== null) addMarker("rangeMarker", inFrame);
  if (outFrame !== null) addMarker("rangeMarker", outFrame);
}

function makeHandle(side, index) {
  const handle = document.createElement("div");
  handle.className = `handle ${side}`;
  handle.addEventListener("mousedown", (event) => {
    event.stopPropagation();
    selectedSegment = index;
    drag = { index, side };
    renderAll();
  });
  return handle;
}

function addMarker(className, frame) {
  const marker = document.createElement("div");
  marker.className = className;
  marker.style.left = `${frame / Math.max(frameCount(), 1) * 100}%`;
  timelineEl.appendChild(marker);
}

function renderReadouts() {
  const frame = currentFrame();
  timeReadout.textContent = `frame ${frame} / ${lastFrame()} · ${video.currentTime.toFixed(2)}s`;
  inPointEl.textContent = formatFrame(inFrame);
  outPointEl.textContent = formatFrame(outFrame);
  if (selectedSegment >= 0 && timeline[selectedSegment]) {
    const item = timeline[selectedSegment];
    segmentInfo.textContent = `${item.state}: ${formatFrame(item.start_frame)} - ${formatFrame(item.end_frame)}`;
  } else {
    segmentInfo.textContent = "No segment selected";
  }
}

function frameFromTimelineEvent(event) {
  const rect = timelineEl.getBoundingClientRect();
  const ratio = clamp((event.clientX - rect.left) / rect.width, 0, 1);
  return clamp(Math.round(ratio * lastFrame()), 0, lastFrame());
}

function seekToFrame(frame) {
  video.currentTime = frameToTime(clamp(frame, 0, lastFrame()));
}

function applyRange(start, end, state) {
  let left = clamp(start, 0, lastFrame());
  let right = clamp(end, 0, lastFrame());
  if (right < left) [left, right] = [right, left];

  const next = [];
  let inserted = false;
  timeline.forEach((segment) => {
    if (segment.end_frame < left || segment.start_frame > right) {
      next.push({ ...segment });
      return;
    }
    if (segment.start_frame < left) {
      next.push({ start_frame: segment.start_frame, end_frame: left - 1, state: segment.state });
    }
    if (!inserted) {
      next.push({ start_frame: left, end_frame: right, state });
      inserted = true;
    }
    if (segment.end_frame > right) {
      next.push({ start_frame: right + 1, end_frame: segment.end_frame, state: segment.state });
    }
  });
  timeline = normalizeTimeline(next);
  selectedSegment = findSegmentIndex(left);
  markDirty();
  renderAll();
}

function findSegmentIndex(frame) {
  return timeline.findIndex((segment) => segment.start_frame <= frame && frame <= segment.end_frame);
}

function splitAt(frame) {
  const index = findSegmentIndex(frame);
  if (index < 0) return;
  const item = timeline[index];
  if (frame <= item.start_frame || frame > item.end_frame) return;
  timeline.splice(index, 1,
    { start_frame: item.start_frame, end_frame: frame - 1, state: item.state },
    { start_frame: frame, end_frame: item.end_frame, state: item.state },
  );
  selectedSegment = index + 1;
  markDirty();
  renderAll();
}

function deleteSelected() {
  if (selectedSegment < 0 || !timeline[selectedSegment]) return;
  const item = timeline[selectedSegment];
  applyRange(item.start_frame, item.end_frame, "normal");
  selectedSegment = findSegmentIndex(item.start_frame);
}

function setInPoint() {
  inFrame = currentFrame();
  renderAll();
}

function setOutPoint() {
  outFrame = currentFrame();
  renderAll();
}

function applySelection() {
  if (inFrame === null || outFrame === null) return;
  applyRange(inFrame, outFrame, selectedState);
}

function applySelectedSegment() {
  if (selectedSegment < 0 || !timeline[selectedSegment]) return;
  const item = timeline[selectedSegment];
  applyRange(item.start_frame, item.end_frame, selectedState);
  selectedSegment = findSegmentIndex(item.start_frame);
}

async function saveAnnotation() {
  const payload = { timeline };
  const saved = await fetchJson(apiUrl("/api/annotation"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  annotation = saved;
  timeline = normalizeTimeline(saved.timeline || timeline);
  sampleName.textContent = `${metadata.video.stem} · annotation`;
  markDirty(false);
  renderAll();
}

async function renderPreview() {
  if (dirty) {
    await saveAnnotation();
  }
  previewInfo.textContent = "Rendering preview...";
  const result = await fetchJson(apiUrl("/api/preview"), { method: "POST" });
  previewInfo.textContent = result.preview_path;
}

function handleKey(event) {
  if (event.target && ["INPUT", "TEXTAREA", "SELECT"].includes(event.target.tagName)) return;
  const key = event.key.toLowerCase();
  if (key === " ") {
    event.preventDefault();
    video.paused ? video.play() : video.pause();
  } else if (key === "a") {
    seekToFrame(currentFrame() - Math.round(fps()));
  } else if (key === "d") {
    seekToFrame(currentFrame() + Math.round(fps()));
  } else if (key === "q") {
    seekToFrame(currentFrame() - Math.round(fps() * 5));
  } else if (key === "e") {
    seekToFrame(currentFrame() + Math.round(fps() * 5));
  } else if (key === ",") {
    video.pause();
    seekToFrame(currentFrame() - 1);
  } else if (key === ".") {
    video.pause();
    seekToFrame(currentFrame() + 1);
  } else if (key >= "1" && key <= "6") {
    setSelectedState(STATES[Number(key) - 1][0]);
  } else if (key === "i") {
    setInPoint();
  } else if (key === "o") {
    setOutPoint();
  } else if (key === "enter") {
    applySelection();
  } else if (key === "m") {
    applySelectedSegment();
  } else if (key === "b") {
    splitAt(currentFrame());
  } else if (key === "backspace") {
    event.preventDefault();
    deleteSelected();
  } else if (key === "s") {
    event.preventDefault();
    saveAnnotation().catch(alert);
  }
}

timelineEl.addEventListener("click", (event) => {
  seekToFrame(frameFromTimelineEvent(event));
});

videoSelect.addEventListener("change", () => {
  const nextVideo = videoSelect.value;
  if (dirty && !window.confirm("Current annotation has unsaved changes. Switch videos anyway?")) {
    videoSelect.value = selectedVideo;
    return;
  }
  loadVideo(nextVideo).catch(alert);
});

document.addEventListener("mousemove", (event) => {
  if (!drag) return;
  const frame = frameFromTimelineEvent(event);
  const item = timeline[drag.index];
  if (!item) return;
  if (drag.side === "left") {
    item.start_frame = clamp(frame, drag.index > 0 ? timeline[drag.index - 1].end_frame + 1 : 0, item.end_frame);
  } else {
    item.end_frame = clamp(frame, item.start_frame, drag.index + 1 < timeline.length ? timeline[drag.index + 1].start_frame - 1 : lastFrame());
  }
  markDirty();
  renderAll();
});

document.addEventListener("mouseup", () => {
  if (drag) {
    timeline = normalizeTimeline(timeline);
    drag = null;
    renderAll();
  }
});

video.addEventListener("timeupdate", renderAll);
video.addEventListener("loadedmetadata", renderAll);
document.addEventListener("keydown", handleKey);
document.getElementById("applyButton").addEventListener("click", applySelection);
document.getElementById("applySegmentButton").addEventListener("click", applySelectedSegment);
document.getElementById("splitButton").addEventListener("click", () => splitAt(currentFrame()));
document.getElementById("deleteButton").addEventListener("click", deleteSelected);
document.getElementById("saveButton").addEventListener("click", () => saveAnnotation().catch(alert));
document.getElementById("previewButton").addEventListener("click", () => renderPreview().catch(alert));

window.addEventListener("beforeunload", (event) => {
  if (!dirty) return;
  event.preventDefault();
  event.returnValue = "";
});

init().catch((error) => {
  sampleName.textContent = "Failed to load annotator";
  alert(error.message);
});
