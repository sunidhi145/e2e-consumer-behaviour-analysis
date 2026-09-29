window.addEventListener("DOMContentLoaded", function () {
  document.body.addEventListener("click", function (event) {
    var target = event.target.closest(".nav-link");
    if (!target) return;
    document.querySelectorAll(".nav-link").forEach(function (link) {
      link.classList.toggle("active", link.getAttribute("href") === target.getAttribute("href"));
    });
  });
});
