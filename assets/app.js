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
      const thumb = el("div", { class: "thumb" });
      if (song.thumb) {
        thumb.append(el("img", { src: `songs/${song.id}/${song.thumb}`, alt: song.title, loading: "lazy" }));
      }
      if (song.duration) thumb.append(el("span", { class: "duration", text: song.duration }));
      card.append(thumb);
      card.append(el("h2", { text: song.title }));
      if (song.hook) card.append(el("p", { class: "hook", text: song.hook }));
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

    // Video first, like a watch page.
    const base = `songs/${song.id}/`;
    if (song.video) main.append(el("video", { controls: "", autoplay: "", src: base + song.video, preload: "metadata" }));
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
      if (collapsed) desc.scrollIntoView({ block: "nearest" });
    };
    moreBtn.addEventListener("click", toggle);
    desc.addEventListener("click", (e) => {
      if (desc.classList.contains("collapsed") && e.target.tagName !== "A") toggle();
    });
    // No need to collapse short descriptions.
    if (desc.scrollHeight <= desc.clientHeight + 16) {
      desc.classList.remove("collapsed");
      moreBtn.remove();
    }
  } catch (err) {
    main.innerHTML = "";
    main.append(el("p", { class: "loading", text: `Error: ${err.message}` }));
  }
}
