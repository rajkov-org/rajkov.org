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
      if (e.target.closest("a")) {
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
   Web Share Level 2 needs HTTPS + a user gesture; where files are not shareable we fall back to download. */
(function () {
  var buttons = document.querySelectorAll("[data-share-audio]");
  if (!buttons.length) return;
  buttons.forEach(function (btn) {
    btn.addEventListener("click", async function () {
      var url = btn.getAttribute("data-share-audio");
      var title = btn.getAttribute("data-share-title") || "RAJKOV Bulletin";
      var text = btn.getAttribute("data-share-text") || "";
      var name = btn.getAttribute("data-share-name") || url.split("/").pop();   // the shared file's name (owner: rajkov-news-<date>-<language>.mp3)
      var label = btn.textContent;
      try {
        btn.disabled = true; btn.textContent = "Preparing…";
        var res = await fetch(url, { cache: "force-cache" });
        var blob = await res.blob();
        var file = new File([blob], name, { type: "audio/mpeg" });
        if (navigator.canShare && navigator.canShare({ files: [file] })) {
          await navigator.share({ files: [file], title: title, text: text });
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
