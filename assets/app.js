// Single-page app, YouTube style: the gallery is the home view; clicking a
// video expands it in place into a watch layout (player + sidebar), with
// pushState keeping ?song=<id> URLs shareable.

let SONGS = null;

async function loadSongs() {
  if (SONGS) return SONGS;
  const res = await fetch("songs/songs.json");
  if (!res.ok) throw new Error("Could not load songs.json");
  SONGS = (await res.json()).songs;
  return SONGS;
}

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "text") node.textContent = v;
    else node.setAttribute(k, v);
  }
  node.append(...children);
  return node;
}

function goTo(id, push = true) {
  if (push) {
    const url = id ? `?song=${id}` : location.pathname;
    history.pushState({ song: id }, "", url);
  }
  render(id);
}

// Older cached index.html called route(); keep it working.
const route = () => initApp();

async function initApp() {
  document.querySelector("[data-home]").addEventListener("click", (e) => {
    e.preventDefault();
    goTo(null);
  });
  window.addEventListener("popstate", () => {
    render(new URLSearchParams(location.search).get("song"), false);
  });
  render(new URLSearchParams(location.search).get("song"));
}

async function render(id) {
  const hero = document.getElementById("hero");
  const gallery = document.getElementById("gallery");
  const watch = document.getElementById("watch");
  try {
    const songs = await loadSongs();
    const song = id && songs.find((s) => s.id === id);
    if (song) {
      hero.hidden = true;
      gallery.hidden = true;
      watch.hidden = false;
      renderWatch(song, songs);
    } else {
      hero.hidden = false;
      gallery.hidden = false;
      watch.hidden = true;
      document.title = "Paper Songs";
      renderGallery(songs);
    }
    window.scrollTo({ top: 0 });
  } catch (err) {
    gallery.hidden = false;
    gallery.innerHTML = "";
    gallery.append(el("p", { class: "loading", text: `Error: ${err.message}` }));
  }
}

function thumbEl(song) {
  const thumb = el("div", { class: "thumb" });
  if (song.thumb) {
    thumb.append(el("img", { src: `songs/${song.id}/${song.thumb}`, alt: song.title, loading: "lazy" }));
  }
  if (song.duration) thumb.append(el("span", { class: "duration", text: song.duration }));
  return thumb;
}

function songLink(song, className, ...content) {
  const link = el("a", { class: className, href: `?song=${song.id}` }, ...content);
  link.addEventListener("click", (e) => {
    e.preventDefault();
    goTo(song.id);
  });
  return link;
}

function renderGallery(songs) {
  const gallery = document.getElementById("gallery");
  gallery.innerHTML = "";
  if (songs.length === 0) {
    gallery.append(el("p", { class: "loading", text: "No songs yet — add one to songs/songs.json." }));
    return;
  }
  for (const song of songs) {
    const card = songLink(song, "card", thumbEl(song));
    card.append(el("h2", { text: song.title }));
    if (song.hook) card.append(el("p", { class: "hook", text: song.hook }));
    const tags = el("div", { class: "tags" });
    for (const t of song.tags || []) tags.append(el("span", { class: "tag", text: t }));
    card.append(tags);
    gallery.append(card);
  }
}

async function renderWatch(song, songs) {
  document.title = song.title;
  const main = document.getElementById("watch-main");
  const side = document.getElementById("watch-side");
  main.innerHTML = "";
  side.innerHTML = "";

  // Player + title.
  const base = `songs/${song.id}/`;
  if (song.video) {
    main.append(el("video", { controls: "", autoplay: "", src: base + song.video, preload: "metadata" }));
  }
  main.append(el("h1", { text: song.title }));

  // Collapsible description box.
  const desc = el("div", { class: "description collapsed" });
  if (song.hook) desc.append(el("p", { class: "hook", text: song.hook }));
  if (song.story) {
    for (const para of song.story.split("\n")) {
      if (para.trim()) desc.append(el("p", { text: para }));
    }
  }
  const paperP = el("p", { class: "paper-link", text: "The paper: " });
  paperP.append(el("a", { href: song.paper.url, target: "_blank", rel: "noopener", text: song.paper.title }));
  desc.append(paperP);

  if (song.lyrics) {
    const details = el("details", { class: "lyrics-box" });
    details.append(el("summary", { text: "Read the lyrics" }));
    const lyricsRes = await fetch(base + song.lyrics);
    const lyricsText = lyricsRes.ok ? await lyricsRes.text() : "(lyrics file not found)";
    details.append(el("div", { class: "lyrics", text: lyricsText }));
    desc.append(details);
  }
  main.append(desc);

  const moreBtn = el("button", { class: "more-btn", text: "...more" });
  main.append(moreBtn);
  const toggle = () => {
    const collapsed = desc.classList.toggle("collapsed");
    moreBtn.textContent = collapsed ? "...more" : "Show less";
  };
  moreBtn.addEventListener("click", toggle);
  desc.addEventListener("click", (e) => {
    if (desc.classList.contains("collapsed") && e.target.tagName !== "A" && e.target.tagName !== "SUMMARY") toggle();
  });
  if (desc.scrollHeight <= desc.clientHeight + 16) {
    desc.classList.remove("collapsed");
    moreBtn.remove();
  }

  // Sidebar: the other songs, compact.
  const others = songs.filter((s) => s.id !== song.id);
  if (others.length === 0) {
    side.append(el("p", { class: "side-note", text: "More papers are getting sung... check back soon." }));
    return;
  }
  for (const other of others) {
    const item = songLink(other, "side-card", thumbEl(other));
    const meta = el("div", { class: "side-meta" });
    meta.append(el("h3", { text: other.title }));
    if (other.hook) meta.append(el("p", { text: other.hook }));
    item.append(meta);
    side.append(item);
  }
}
