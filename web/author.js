import { app } from "../../scripts/app.js";

const installed = Symbol("h3VideoControlFooter");
const states = new Set();
let observer;
let scheduled = false;

function makeCredit() {
    const label = document.createElement("span");
    label.className = "h3-video-controller-author-credit";
    label.textContent = "Author: Aman Dolorain";
    label.title = "H3 Video Controller — Author: Aman Dolorain";
    Object.assign(label.style, {
        marginLeft: "auto",
        flex: "0 0 auto",
        alignSelf: "center",
        font: "10px/20px sans-serif",
        color: "var(--descrip-text, #9aa0a6)",
        opacity: "0.7",
        whiteSpace: "nowrap",
        pointerEvents: "none",
        userSelect: "none",
        paddingRight: "4px",
    });
    return label;
}

function clearMount(state) {
    state.label?.remove();
    state.ownRow?.remove();
    state.label = state.ownRow = state.root = null;
}

function syncCredits() {
    scheduled = false;
    const activeGraph = app.canvas?.graph;
    const roots = [...document.querySelectorAll(".lg-node[data-node-id]")];
    for (const state of states) {
        const { node } = state;
        const root = node.graph === activeGraph && !node.flags?.collapsed
            ? roots.find((element) => element.dataset.nodeId === String(node.id))
            : null;
        if (!root || root.dataset.collapsed) {
            if (state.root) clearMount(state);
            continue;
        }
        if (state.root && state.root !== root) clearMount(state);
        const body = [...root.querySelectorAll("[data-testid]")].find(
            (element) => element.dataset.testid === `node-body-${node.id}`,
        );
        if (!body) continue;
        // NodeBadges.vue renders a direct .mt-auto flex row in the Vue node body.
        // Put the credit IN that row so it shares the package badge's baseline.
        let row = [...body.children].find(
            (element) => element.classList.contains("mt-auto") && element !== state.ownRow,
        );
        if (!row) {
            if (!state.ownRow?.isConnected) {
                const footer = document.createElement("div");
                footer.className = "h3-video-controller-credit-row";
                Object.assign(footer.style, {
                    display: "flex", alignItems: "center", minHeight: "24px",
                    marginTop: "auto", padding: "0 8px", flexShrink: "0",
                });
                body.append(footer);
                state.ownRow = footer;
            }
            row = state.ownRow;
        } else if (state.ownRow) {
            state.ownRow.remove();
            state.ownRow = null;
        }
        if (!state.label) state.label = makeCredit();
        if (state.label.parentElement !== row) row.append(state.label);
        state.root = root;
    }
}

function scheduleSync() {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(syncCredits);
}

function observeNodes() {
    if (observer) return;
    observer = new MutationObserver(scheduleSync);
    observer.observe(document.body, {
        childList: true, subtree: true, attributes: true,
        attributeFilter: ["data-collapsed", "data-node-id"],
    });
}

app.registerExtension({
    name: "H3VideoController.AuthorCredit",
    setup() { observeNodes(); scheduleSync(); },
    nodeCreated(node) {
        if (node.comfyClass !== "H3VideoController" || node[installed]) return;
        node[installed] = true;
        const state = { node, label: null, ownRow: null, root: null };
        states.add(state);

        // Classic canvas fallback. Vue nodes use the DOM footer above instead.
        const previousComputeSize = node.computeSize;
        node.computeSize = function (...args) {
            const size = previousComputeSize.apply(this, args);
            return [Math.max(size[0], 300), size[1] + 24];
        };
        const previousDraw = node.onDrawForeground;
        node.onDrawForeground = function (ctx, ...args) {
            const result = previousDraw?.call(this, ctx, ...args);
            if (this.flags?.collapsed || state.root?.isConnected) return result;
            ctx.save();
            try {
                ctx.font = "10px sans-serif";
                ctx.fillStyle = "#9aa0a6";
                ctx.globalAlpha *= 0.7;
                ctx.textAlign = "right";
                ctx.textBaseline = "middle";
                ctx.fillText("Author: Aman Dolorain", this.size[0] - 12, this.size[1] - 18);
            } finally { ctx.restore(); }
            return result;
        };
        const previousRemoved = node.onRemoved;
        node.onRemoved = function (...args) {
            states.delete(state);
            clearMount(state);
            return previousRemoved?.apply(this, args);
        };
        const minimum = node.computeSize();
        node.setSize([Math.max(node.size[0], minimum[0]), Math.max(node.size[1], minimum[1])]);
        observeNodes();
        scheduleSync();
        node.setDirtyCanvas?.(true, true);
    },
});
