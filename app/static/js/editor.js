/**
 * Editor Scripts
 */

let editor_options = {lineNumbers: true, indentUnit: 4}  // TODO: "indentUnit: 4" is not correct
if (fileExtension === "unknown") editor_options["mode"] = null;
else editor_options["mode"] = fileExtension;

const dmp = new diff_match_patch();
const editorSocketUrl = `ws://${window.location.host}/ws/files/${filePk}/file_consumers/${fileConsumerPk}/`;
const editor = CodeMirror.fromTextArea(document.getElementById("editor"), editor_options);

let differencesSenderInterval = null;
let clientDifferencesStack = {};
let editorSocket = null;
let lock = false;
let shadow = {
    content: editor.getValue(),
    client_version: 0,
    server_version: 0,
};
let backup_shadow = {
    content: editor.getValue(),
    client_version: 0,
};

function differencesSenderIntervalManager(set) {
    if (set) differencesSenderInterval = setInterval(sendDifferences, 1000);
    else clearInterval(differencesSenderInterval);
}

function calculateDifferences() {
    while (lock) {}

    lock = true;

    const content = editor.getValue();
    const clientDifferences = dmp.diff_main(shadow.content, content);
    clientDifferencesStack[shadow.client_version.toString()] = clientDifferences;
    shadow.content = content;
    shadow.client_version += 1;

    lock = false;
}

function sendDifferences() {
    while (lock) {}

    lock = true;

    data = {
        differences_stack: clientDifferencesStack,
        server_version: shadow.server_version,
    };

    backup_shadow.content = shadow.content;
    backup_shadow.client_version = shadow.client_version;

    editorSocket.send(JSON.stringify(data));

    lock = false;
}

function applyDifferences(differences) {
    let index = 0;

    differences.forEach(difference => {
        switch (difference[0]) {
            case 0:
                index += difference[1].length;
                break;
            case 1:
                editor.replaceRange(difference[1], editor.posFromIndex(index));
                index += difference[1].length;
                break;
            case -1:
                editor.replaceRange(
                    "", editor.posFromIndex(index), editor.posFromIndex(index + difference[1].length)
                );
                break;
        }
    });
}

function handleDifferences(e) {
    const data = JSON.parse(e.data);
    const serverDifferencesStack = data.differences_stack;

    // TODO: to be removed
    console.log("----------------------------------");
    console.log("client.shadow.client_version: " + shadow.client_version);
    console.log("client.backup_shadow.client_version: " + backup_shadow.client_version);
    console.log("server.shadow.client_version: " + data.client_version);
    console.log("----------------------------------");

    if ((shadow.client_version == data.client_version) || ((shadow.client_version != data.client_version) && (backup_shadow.client_version == data.client_version))) {
        if (shadow.server_version.toString() in serverDifferencesStack) {
            while (lock) {}

            lock = true;

            if (shadow.client_version != data.client_version) {
                clientDifferencesStack = {};
                shadow.content = backup_shadow.content;
                shadow.client_version = backup_shadow.client_version;
            }

            let clientVersion = data.client_version;

            while (clientVersion >= 0) {
                if (clientVersion.toString() in clientDifferencesStack) {
                    delete clientDifferencesStack[clientVersion.toString()];
                    clientVersion -= 1;
                } else break;
            }

            const serverDifferences = serverDifferencesStack[shadow.server_version.toString()];
            const patches = dmp.patch_make(serverDifferences);
            const shadowContent = dmp.patch_apply(patches, shadow.content)[0];

            shadow.content = shadowContent;
            shadow.server_version += 1;

            const newContent = dmp.patch_apply(patches, editor.getValue())[0];
            const localDifferences = dmp.diff_main(editor.getValue(), newContent);
            dmp.diff_cleanupEfficiency(localDifferences);
            applyDifferences(localDifferences);

            lock = false;
        }
        else console.warn("shadow.server_version not present in serverDifferencesStack!");
    }
    else {
        console.warn("client_version(s) do not match!");
        editorSocket.close();
    }
}

function editorSocketConnectionManager() {
    editorSocket = new WebSocket(editorSocketUrl);

    editorSocket.onopen = function(e) {
        differencesSenderIntervalManager(true);
    };

    editorSocket.onmessage = function(e) {
        handleDifferences(e);
    };

    editorSocket.onclose = function(e) {
        differencesSenderIntervalManager(false);
        setTimeout(editorSocketConnectionManager, 1000);
    };

    editorSocket.onerror = function(e) {};
}

setInterval(calculateDifferences, 300);

editorSocketConnectionManager();
