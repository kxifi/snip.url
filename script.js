document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("shorten-form");
  const input = document.getElementById("urlInput");
  const result = document.getElementById("result");
  const error = document.getElementById("error");

  form.addEventListener("submit", async (e) => {
    e.preventDefault(); // prevent page reload on submit

    // Clear previous messages
    result.textContent = "";
    error.textContent = "";

    const url = input.value.trim();

    if (!url) {
      error.textContent = "Please enter a URL.";
      return;
    }

    try {
      const response = await fetch("/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ original_url: url })
      });

      const data = await response.json();

      if (response.ok) {
        result.innerHTML = `
          <p>Shortened URL: <a href="${data.short_url}" target="_blank" rel="noopener noreferrer">${data.short_url}</a></p>
          <button id="copy-btn">Copy</button>
        `;

        // Copy to clipboard functionality
        const copyBtn = document.getElementById("copy-btn");
        copyBtn.addEventListener("click", () => {
          navigator.clipboard.writeText(data.short_url)
            .then(() => {
              copyBtn.textContent = "Copied!";
              setTimeout(() => {
                copyBtn.textContent = "Copy";
              }, 2000);
            })
            .catch(() => {
              copyBtn.textContent = "Failed to copy";
            });
        });

        // Optionally clear the input after success
        input.value = "";
      } else {
        error.textContent = data.error || "Something went wrong.";
      }
    } catch (err) {
      error.textContent = "Network error. Please try again.";
      console.error(err);
    }
  });
});

// DARK MODE //

const toggleButton = document.getElementById('themeToggle');

function setThemeIcon() {
  const isDark = document.body.classList.contains('dark-mode');
  toggleButton.textContent = isDark ? '☀️' : '🌙';
}

function toggleTheme() {
  document.body.classList.toggle('dark-mode');
  setThemeIcon();
}

toggleButton.addEventListener('click', toggleTheme);

setThemeIcon();