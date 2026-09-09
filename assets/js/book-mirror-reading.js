const menu = document.querySelector("aside details");
if (menu) menu.open = innerWidth > 850;

const dialog = document.querySelector("dialog");
document.querySelectorAll("button.diagram").forEach((button) => {
  button.addEventListener("click", () => {
    dialog.querySelector(".zoom-content").innerHTML = button.innerHTML;
    dialog.showModal();
  });
});

dialog?.querySelector("button").addEventListener("click", () => dialog.close());
dialog?.addEventListener("click", (event) => {
  if (event.target === dialog) dialog.close();
});
