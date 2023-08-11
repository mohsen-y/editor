/**
 * Copy to Clipboard Scripts
 */

function copyToClipboard(button, text) {
    navigator.clipboard.writeText(window.location.host + text);
    button.innerText = "Copied!";
  }
