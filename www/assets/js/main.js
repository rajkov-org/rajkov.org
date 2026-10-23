/* RAJKOV — site interactions (progressive enhancement, no dependencies) */
(function () {
  "use strict";

  /* --- Mobile navigation toggle --- */
  var toggle = document.querySelector(".nav-toggle");
  var links = document.getElementById("nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      var open = links.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });
    links.addEventListener("click", function (e) {
      var a = e.target.closest("a");
      if (a) {
        a.blur(); // let a desktop dropdown close after a section jump
        links.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && links.classList.contains("open")) {
        links.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });
  }

  /* --- Header shadow on scroll --- */
  var header = document.querySelector(".site-header");
  if (header) {
    var onScroll = function () { header.classList.toggle("scrolled", window.scrollY > 8); };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* --- Mark the current page in the nav (clean URLs: /about === /about.html) --- */
  var path = location.pathname.replace(/\.html$/, "").replace(/\/index$/, "/");
  document.querySelectorAll(".nav-links a").forEach(function (a) {
    var href = a.getAttribute("href") || "";
    if (href.charAt(0) !== "/") return;
    var active = href === "/" ? path === "/" : path === href || path.indexOf(href + "/") === 0;
    if (active) a.setAttribute("aria-current", "page");
  });

  /* --- Current year in footer --- */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  /* --- Reveal-on-scroll --- */
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var revealables = document.querySelectorAll(".reveal");
  if (reduce || !("IntersectionObserver" in window)) {
    revealables.forEach(function (el) { el.classList.add("in"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { entry.target.classList.add("in"); io.unobserve(entry.target); }
      });
    }, { threshold: 0.12 });
    revealables.forEach(function (el) { io.observe(el); });
  }
})();

/* Weekly Rajasthan Bulletin: hand the MP3 to the phone's share sheet as a file (WhatsApp, etc.).
   Web Share Level 2 needs HTTPS + a user gesture; where files are not shareable we fall back to download.
   iPhone lessons (owner, 2026-10-12 — the sheet got stuck sharing to WhatsApp):
   - Safari only honours navigator.share() while the tap's user activation is alive. Awaiting a 1 MB fetch
     first can outlive it, so the MP3 is pre-fetched on first touch/hover/focus and shared straight away.
   - iOS WhatsApp stalls when a file share also carries `text`; on iOS we send the file + title only. */
(function () {
  var buttons = document.querySelectorAll("[data-share-audio]");
  if (!buttons.length) return;
  var isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  buttons.forEach(function (btn) {
    var url = btn.getAttribute("data-share-audio");
    var title = btn.getAttribute("data-share-title") || "RAJKOV Bulletin";
    var text = btn.getAttribute("data-share-text") || "";
    var name = btn.getAttribute("data-share-name") || url.split("/").pop();   // the shared file's name (owner: rajkov-news-<date>-<language>.mp3)
    var filePromise = null;
    function prefetch() {
      if (!filePromise) {
        filePromise = fetch(url, { cache: "force-cache" })
          .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.blob(); })
          .then(function (blob) { return new File([blob], name, { type: "audio/mpeg" }); })
          .catch(function (e) { filePromise = null; throw e; });
      }
      return filePromise;
    }
    ["pointerdown", "touchstart", "mouseenter", "focus"].forEach(function (ev) { btn.addEventListener(ev, prefetch, { passive: true }); });
    btn.addEventListener("click", async function () {
      var label = btn.textContent;
      try {
        btn.disabled = true; btn.textContent = "Preparing…";
        var file = await prefetch();
        if (navigator.canShare && navigator.canShare({ files: [file] })) {
          var data = isIOS ? { files: [file], title: title } : { files: [file], title: title, text: text };
          await navigator.share(data);
        } else if (navigator.share) {
          await navigator.share({ title: title, text: text, url: location.href });
        } else {
          var a = document.createElement("a"); a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove();
        }
      } catch (e) {
        if (!(e && e.name === "AbortError")) { console.warn("[bulletin] share failed:", e); location.href = url; }
      } finally {
        btn.disabled = false; btn.textContent = label;
      }
    });
  });
})();
