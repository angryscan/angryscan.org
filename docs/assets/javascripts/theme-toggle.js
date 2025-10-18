document.addEventListener("DOMContentLoaded", function () {
  var paletteForm = document.querySelector("form[data-md-component='palette']");
  if (!paletteForm) {
    return;
  }

  var inputs = paletteForm.querySelectorAll("input[name='__palette']");
  if (inputs.length < 2) {
    return;
  }

  paletteForm.classList.add("md-theme-switch__container");

  var switchButton = document.createElement("button");
  switchButton.type = "button";
  switchButton.className = "md-theme-switch";
  switchButton.setAttribute("aria-label", "Toggle color theme");
  switchButton.setAttribute("aria-pressed", "false");
  switchButton.innerHTML = [
    "<span class='md-theme-switch__icon md-theme-switch__icon--sun' aria-hidden='true'></span>",
    "<span class='md-theme-switch__icon md-theme-switch__icon--moon' aria-hidden='true'></span>",
    "<span class='md-theme-switch__thumb'></span>",
  ].join("");

  paletteForm.appendChild(switchButton);

  function isDarkScheme() {
    var active = Array.prototype.find.call(inputs, function (input) {
      return input.checked;
    });
    if (!active) {
      return document.body.getAttribute("data-md-color-scheme") !== "default";
    }
    return active.getAttribute("data-md-color-scheme") !== "default";
  }

  function updateState() {
    var dark = isDarkScheme();
    switchButton.classList.toggle("is-dark", dark);
    switchButton.setAttribute("aria-pressed", dark ? "true" : "false");
  }

  function togglePalette() {
    var dark = isDarkScheme();
    var target = dark
      ? paletteForm.querySelector("#__palette_1")
      : paletteForm.querySelector("#__palette_0");
    if (target) {
      target.click();
    }
  }

  switchButton.addEventListener("click", function (event) {
    event.preventDefault();
    togglePalette();
  });

  inputs.forEach(function (input) {
    input.addEventListener("change", updateState);
  });

  document.addEventListener("palette-changed", updateState);
  updateState();
});
