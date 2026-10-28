import { app } from "../../scripts/app.js";

const outputs = [
    ["latent", "LATENT"], ["video_info", "VHS_VIDEOINFO"],
    ["frame_count", "INT"], ["fps", "FLOAT"],
    ["actual_duration_seconds", "FLOAT"], ["width", "INT"],
    ["height", "INT"], ["summary", "STRING"],
];
const obsolete = new Set(["clip", "video_vae", "first_frame", "last_frame", "prompt", "prepare_mode", "size_rounding", "frame_rounding"]);

function repair(node) {
    const widgets = new Map((node.widgets || []).map(w => [w.name, w]));
    const get = name => widgets.get(name)?.value;
    const set = (name, value) => { if (widgets.has(name)) widgets.get(name).value = value; };
    const validSize = value => Number.isInteger(value) && value >= 1 && value <= 16384;
    // Old positional order: duration, width, height, preset, size rounding, frame rounding.
    // New positional order: duration, fps, width, height, preset.
    if (!validSize(get("height")) && typeof get("height") === "string" && validSize(get("fps")) && validSize(get("width"))) {
        const oldWidth = get("fps"), oldHeight = get("width"), oldPreset = get("height");
        set("width", oldWidth);
        set("height", oldHeight);
        set("resolution_preset", oldPreset);
    }
    set("fps", 24);
    if (!validSize(get("width"))) set("width", 512);
    if (!validSize(get("height"))) set("height", 512);
    const preset = widgets.get("resolution_preset");
    const values = typeof preset?.options?.values === "function" ? preset.options.values() : preset?.options?.values;
    if (Array.isArray(values) && !values.includes(preset.value)) preset.value = "Custom";
    for (let i = (node.inputs?.length || 0) - 1; i >= 0; i--) {
        if (obsolete.has(node.inputs[i].name)) node.removeInput(i);
    }
    node.widgets = (node.widgets || []).filter(w => !obsolete.has(w.name));
    const mismatched = node.outputs?.length !== outputs.length || outputs.some(([name, type], i) =>
        node.outputs[i]?.name !== name || node.outputs[i]?.type !== type);
    if (mismatched) {
        // Saved output indices may already have been shifted by an earlier update.
        // Disconnect them instead of retaining a wire with the wrong meaning.
        for (let i = (node.outputs?.length || 0) - 1; i >= 0; i--) node.removeOutput(i);
        for (const [name, type] of outputs) node.addOutput(name, type);
        console.warn("H3 Controller: legacy sockets repaired. Reconnect output wires by name.");
    }
    node.properties ||= {};
    node.properties.h3_controller_schema = 3;
    const minimum = node.computeSize?.();
    if (minimum) node.setSize([Math.max(node.size[0], minimum[0]), minimum[1]]);
    node.setDirtyCanvas?.(true, true);
}

app.registerExtension({
    name: "H3VideoController.WorkflowMigration",
    loadedGraphNode(node) {
        if (node.comfyClass === "H3VideoController") queueMicrotask(() => repair(node));
    },
});
