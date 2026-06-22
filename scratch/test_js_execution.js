const fs = require('fs');
const path = require('path');

const htmlPath = path.join(__dirname, '..', 'templates', 'index.html');
const html = fs.readFileSync(htmlPath, 'utf-8');
const scriptContent = html.match(/<script>([\s\S]*?)<\/script>/)[1];

// Mock basic browser environment
global.window = {
    addEventListener: () => {},
    navigator: { serviceWorker: { register: () => Promise.resolve() } },
    setInterval: () => {}
};
global.navigator = global.window.navigator;
global.setInterval = global.window.setInterval;
global.FileReader = class {
    readAsDataURL() {}
};
global.FormData = class {};
global.fetch = () => Promise.resolve({ ok: true, json: () => Promise.resolve({}) });

const elements = {};
global.document = {
    getElementById: (id) => {
        if (!elements[id]) {
            elements[id] = {
                style: {},
                classList: { add: () => {}, remove: () => {} },
                querySelector: () => ({ addEventListener: () => {} }),
                appendChild: () => {},
                addEventListener: () => {},
                getContext: () => ({ drawImage: () => {}, save: () => {}, restore: () => {}, beginPath: () => {}, rect: () => {}, arc: () => {}, closePath: () => {}, fill: () => {} }),
                toBlob: () => {}
            };
        }
        return elements[id];
    },
    createElement: () => ({
        style: {},
        addEventListener: () => {},
        appendChild: () => {},
    }),
    addEventListener: () => {}
};

try {
    eval(scriptContent);
    console.log("SUCCESS: El script se ejecuta completamente sin ReferenceError ni TypeError!");
} catch (e) {
    console.error("ERROR de ejecucion:", e);
    process.exit(1);
}
