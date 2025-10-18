document.addEventListener("DOMContentLoaded", function () {
  var repoSlug = "angryscan/angrydata-app";
  var apiUrl = "https://api.github.com/repos/" + repoSlug;

  function formatNumber(value) {
    if (value == null) {
      return "0";
    }
    if (value < 1000) {
      return String(value);
    }
    return (value / 1000).toFixed(1).replace(/\.0$/, "") + "k";
  }

  function injectStats(stars, forks) {
    var targets = document.querySelectorAll(".md-source__repository");
    if (!targets.length) {
      return;
    }

    targets.forEach(function (target) {
      var container = target;
      var existingStats = container.querySelector(".md-source__stats");
      if (existingStats) {
        existingStats.remove();
      }

      var stats = document.createElement("span");
      stats.className = "md-source__stats";

      var star = document.createElement("span");
      star.className = "md-source__stat md-source__stat--stars";
      star.setAttribute("aria-label", stars + " stars on GitHub");
      star.innerHTML = "★ " + formatNumber(stars);

      var fork = document.createElement("span");
      fork.className = "md-source__stat md-source__stat--forks";
      fork.setAttribute("aria-label", forks + " forks on GitHub");
      fork.innerHTML = "⑂ " + formatNumber(forks);

      stats.appendChild(star);
      stats.appendChild(fork);

      container.appendChild(stats);
    });
  }

  fetch(apiUrl, { headers: { Accept: "application/vnd.github+json" } })
    .then(function (response) {
      if (!response.ok) {
        throw new Error("Failed to load repository metadata");
      }
      return response.json();
    })
    .then(function (data) {
      injectStats(data.stargazers_count || 0, data.forks_count || 0);
    })
    .catch(function () {
      /* Swallow errors silently – the default button will remain. */
    });
});
