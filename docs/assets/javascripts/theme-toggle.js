document.addEventListener("DOMContentLoaded", function () {
  var paletteForm = document.querySelector("form[data-md-component='palette']");
  if (!paletteForm) {
    return;
  }

  if (paletteForm.querySelector('.theme-toggle')) {
    return;
  }

  var radios = Array.from(paletteForm.querySelectorAll("input[name='__palette']"));
  if (radios.length < 2) {
    return;
  }

  var lightRadio = radios.find(function (input) {
    return (input.getAttribute('data-md-color-scheme') || '').toLowerCase() === 'default';
  }) || radios[0];
  var darkRadio = radios.find(function (input) {
    return (input.getAttribute('data-md-color-scheme') || '').toLowerCase() !== 'default';
  }) || radios[radios.length - 1];

  var uniqueId = 'theme-toggle__classic__cutout__' + Math.random().toString(36).slice(2, 9);

  var toggle = document.createElement('label');
  toggle.className = 'theme-toggle theme-toggle--classic theme-toggle--force-motion';
  toggle.setAttribute('title', 'Toggle color theme');
  toggle.setAttribute('tabindex', '0');

  var checkbox = document.createElement('input');
  checkbox.type = 'checkbox';
  checkbox.setAttribute('aria-label', 'Toggle color theme');

  var sr = document.createElement('span');
  sr.className = 'theme-toggle-sr';
  sr.textContent = 'Toggle color theme';

  var svg = '\n<svg xmlns="http://www.w3.org/2000/svg" aria-hidden="true" width="1em" height="1em" fill="currentColor" stroke-linecap="round" class="theme-toggle__classic" viewBox="0 0 32 32">\n  <clipPath id="' + uniqueId + '">\n    <path d="M0-5h30a1 1 0 0 0 9 13v24H0Z"/>\n  </clipPath>\n  <g clip-path="url(#' + uniqueId + ')">\n    <circle cx="16" cy="16" r="9.34"/>\n    <g stroke="currentColor" stroke-width="1.5">\n      <path d="M16 5.5v-4"/>\n      <path d="M16 30.5v-4"/>\n      <path d="M1.5 16h4"/>\n      <path d="M26.5 16h4"/>\n      <path d="m23.4 8.6 2.8-2.8"/>\n      <path d="m5.7 26.3 2.9-2.9"/>\n      <path d="m5.8 5.8 2.8 2.8"/>\n      <path d="m23.4 23.4 2.9 2.9"/>\n    </g>\n  </g>\n</svg>\n';

  toggle.appendChild(checkbox);
  toggle.appendChild(sr);
  toggle.insertAdjacentHTML('beforeend', svg);

  paletteForm.appendChild(toggle);

  function currentIsDark() {
    var active = radios.find(function (input) {
      return input.checked;
    });
    if (!active) {
      return (document.body.getAttribute('data-md-color-scheme') || '').toLowerCase() !== 'default';
    }
    return (active.getAttribute('data-md-color-scheme') || '').toLowerCase() !== 'default';
  }

  function syncState() {
    var dark = currentIsDark();
    checkbox.checked = dark;
    toggle.setAttribute('aria-pressed', dark ? 'true' : 'false');
    toggle.classList.toggle('theme-toggle--toggled', dark);
  }

  function activatePalette(target) {
    if (target && typeof target.click === 'function') {
      target.click();
    }
  }

  checkbox.addEventListener('change', function () {
    if (checkbox.checked) {
      activatePalette(darkRadio);
    } else {
      activatePalette(lightRadio);
    }
    setTimeout(syncState, 0);
  });

  toggle.addEventListener('keydown', function (event) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      checkbox.checked = !checkbox.checked;
      if (checkbox.checked) {
        activatePalette(darkRadio);
      } else {
        activatePalette(lightRadio);
      }
      setTimeout(syncState, 0);
    }
  });

  toggle.addEventListener('click', function (event) {
    if (event.target === checkbox) {
      return;
    }
    checkbox.checked = !checkbox.checked;
    if (checkbox.checked) {
      activatePalette(darkRadio);
    } else {
      activatePalette(lightRadio);
    }
    setTimeout(syncState, 0);
  });

  radios.forEach(function (input) {
    input.addEventListener('change', function () {
      setTimeout(syncState, 0);
    });
  });

  document.addEventListener('palette-changed', function () {
    setTimeout(syncState, 0);
  });

  syncState();
});
