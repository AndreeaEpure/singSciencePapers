// Single-page router: "?song=<id>" shows a song page, otherwise the gallery.

function route() {
  const id = new URLSearchParams(location.search).get("song");
  if (id) {
    document.getElementById("song-header").hidden = false;
    document.getElementById("song").hidden = false;
    renderSongPage(id);
  } else {
    document.getElementById("home-header").hidden = false;
    document.getElementById("gallery").hidden = false;
    renderGallery();
  }
}

async function loadSongs() {
  const res = await fetch("songs/songs.json");
  if (!res.ok) throw new Error("Could not load songs.json");
  return (await res.json()).songs;
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

async function renderGallery() {
  const gallery = document.getElementById("gallery");
  try {
    const songs = await loadSongs();
    gallery.innerHTML = "";
    if (songs.length === 0) {
      gallery.append(el("p", { class: "loading", text: "No songs yet — add one to songs/songs.json." }));
      return;
    }
    for (const song of songs) {
      const card = el("a", { class: "card", href: `?song=${song.id}` });
      card.append(el("h2", { text: song.title }));
      if (song.hook) card.append(el("p", { class: "hook", text: song.hook }));
      card.append(el("p", { class: "paper-title", text: song.paper.title }));
      const tags = el("div", { class: "tags" });
      for (const t of song.tags || []) tags.append(el("span", { class: "tag", text: t }));
      card.append(tags);
      gallery.append(card);
    }
  } catch (err) {
    gallery.innerHTML = "";
    gallery.append(el("p", { class: "loading", text: `Error: ${err.message}` }));
  }
}

async function renderSongPage(id) {
  const main = document.getElementById("song");
  try {
    const songs = await loadSongs();
    const song = songs.find((s) => s.id === id);
    if (!song) {
      main.innerHTML = "";
      main.append(el("p", { class: "loading", text: "Song not found." }));
      return;
    }
    document.title = song.title;
    main.innerHTML = "";
    main.append(el("h1", { text: song.title }));
    if (song.hook) main.append(el("p", { class: "hook", text: song.hook }));

    const base = `songs/${song.id}/`;
    if (song.video) main.append(el("video", { controls: "", src: base + song.video, preload: "metadata" }));

    if (song.story) {
      const story = el("div", { class: "story" });
      for (const para of song.story.split("\n")) {
        if (para.trim()) story.append(el("p", { text: para }));
      }
      main.append(story);
    }

    const paperP = el("p", { class: "paper-link", text: "The paper: " });
    paperP.append(el("a", { href: song.paper.url, target: "_blank", rel: "noopener", text: song.paper.title }));
    main.append(paperP);

    if (song.lyrics) {
      const details = el("details", { class: "lyrics-box" });
      details.append(el("summary", { text: "Read the lyrics" }));
      const lyricsRes = await fetch(base + song.lyrics);
      const lyricsText = lyricsRes.ok ? await lyricsRes.text() : "(lyrics file not found)";
      details.append(el("div", { class: "lyrics", text: lyricsText }));
      main.append(details);
    }
  } catch (err) {
    main.innerHTML = "";
    main.append(el("p", { class: "loading", text: `Error: ${err.message}` }));
  }
}
