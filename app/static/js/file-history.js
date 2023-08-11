/**
 * File History Scripts
 */

function formatPatchContent(content) {
    const patchContentElement = document.getElementById("patch-content");
    const contentFormatted = content.replace(/%0A/g, "");
    const lines = contentFormatted.split("\n");
    let firstLine = true;

    lines.forEach(line => {
        const lineElement = document.createElement("div");

        if (line.startsWith("@@")) {
            lineElement.className = "diff-header";
            if (firstLine) firstLine = false;
            else line = "\n\n" + line;
        }
        else if (line.startsWith("-")) lineElement.className = "diff-removed";
        else if (line.startsWith("+")) lineElement.className = "diff-added";
        else lineElement.className = "diff-not-changed";

        lineElement.textContent = line;
        patchContentElement.appendChild(lineElement);
    });
}

formatPatchContent(patchFileContent);
