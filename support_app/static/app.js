document.addEventListener("DOMContentLoaded", () => {
  const flash = document.querySelector(".flash");
  if (flash) window.setTimeout(() => flash.remove(), 5000);
});
