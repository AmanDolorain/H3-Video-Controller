import { app } from "../../scripts/app.js";

const installed = Symbol("h3ResolutionSync");
function install(node) {
    if (node[installed]) return node[installed];
    const find = name => node.widgets?.find(w => w.name === name);
    const width = find("width"), height = find("height"), preset = find("resolution_preset");
    if (!width || !height || !preset) return;
    node.properties ||= {};
    let current = preset.value;
    let busy = false;
    const valid = size => Array.isArray(size) && size.length === 2 && size.every(v => Number.isInteger(v) && v > 0 && v <= 16384);
    const read = () => [width.value, height.value];
    const remember = () => { if (valid(read())) node.properties.h3_custom_size = read(); };
    const apply = initializing => {
        if (busy) return;
        busy = true;
        try {
            if (!initializing && current === "Custom") remember();
            if (preset.value === "Custom") {
                if (!initializing && valid(node.properties.h3_custom_size)) {
                    [width.value, height.value] = node.properties.h3_custom_size;
                } else remember();
            } else {
                const match = String(preset.value).match(/(\d+)\s*x\s*(\d+)\s*$/i);
                if (match) [width.value, height.value] = [Number(match[1]), Number(match[2])];
            }
            current = preset.value;
            node.setDirtyCanvas?.(true, true);
        } finally { busy = false; }
    };
    const previousPreset = preset.callback;
    preset.callback = function (...args) {
        const result = previousPreset?.apply(this, args);
        apply(false);
        return result;
    };
    for (const widget of [width, height]) {
        const previous = widget.callback;
        widget.callback = function (...args) {
            const result = previous?.apply(this, args);
            if (!busy) {
                // Editing a dimension means a custom size; don't leave a preset overriding it.
                preset.value = current = "Custom";
                remember();
                node.setDirtyCanvas?.(true, true);
            }
            return result;
        };
    }
    const state = { initialize() { current = preset.value; apply(true); } };
    node[installed] = state;
    return state;
}
app.registerExtension({
    name: "H3VideoController.ResolutionSync",
    nodeCreated(node) {
        if (node.comfyClass === "H3VideoController") install(node)?.initialize();
    },
    loadedGraphNode(node) {
        if (node.comfyClass === "H3VideoController") {
            // Let legacy widget migration finish before applying the selected preset.
            queueMicrotask(() => queueMicrotask(() => install(node)?.initialize()));
        }
    },
});
