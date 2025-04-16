document.addEventListener("DOMContentLoaded", () => {
  "use strict";

  // Selector helper
  const select = (el, all = false) => {
    el = el.trim();
    if (all) {
      return [...document.querySelectorAll(el)];
    } else {
      return document.querySelector(el);
    }
  };

  // Event listener helper
  const on = (type, el, listener, all = false) => {
    const elements = all ? select(el, true) : [select(el)];
    elements.forEach(e => e && e.addEventListener(type, listener));
  };

  // Sidebar toggle
  const toggleSidebarBtn = select(".toggle-sidebar-btn");
  console.log("Toggle Sidebar Btn:", toggleSidebarBtn);
  if (toggleSidebarBtn) {
    on("click", ".toggle-sidebar-btn", () => {
      const body = select("body");
      if (body) {
        body.classList.toggle("toggle-sidebar");
        console.log("Sidebar toggled");
      } else {
        console.error("Body not found");
      }
    });
  } else {
    console.warn("Toggle sidebar button not found");
  }
});