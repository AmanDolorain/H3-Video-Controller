import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const source = fs.readFileSync(new URL('../web/migration.js', import.meta.url), 'utf8').replace(/^import .*;\n/, '');
let extension;
vm.runInNewContext(source, {app:{registerExtension:e=>extension=e}, queueMicrotask:f=>f(), console:{warn(){}}, Map, Set, Number, Array, Math});
const names=['duration_seconds','fps','width','height','resolution_preset'];
const outputNames=['latent','video_info','frame_count','fps','actual_duration_seconds','width','height','summary'];
const types=['LATENT','VHS_VIDEOINFO','INT','FLOAT','FLOAT','INT','INT','STRING'];
function make(values, stale=true) {
 return {comfyClass:'H3VideoController', widgets:names.map((name,i)=>({name,value:values[i],options:{values:['Custom','Square 512 x 512']}})),
 inputs:stale?['clip','video_vae','first_frame','last_frame'].map(name=>({name})):[],
 outputs:outputNames.map((name,i)=>({name,type:types[i]})).concat(stale?[{name:'summary',type:'STRING'}]:[]),
 size:[400,600], removed:0,removeInput(i){this.inputs.splice(i,1)},removeOutput(i){this.outputs.splice(i,1);this.removed++},addOutput(name,type){this.outputs.push({name,type})},computeSize(){return [300,400]},setSize(size){this.size=size}};
}
const legacy=make([5,864,480,'Custom','nearest']);
extension.loadedGraphNode(legacy);
assert.deepEqual(legacy.widgets.map(w=>w.value),[5,24,864,480,'Custom']);
assert.equal(legacy.inputs.length,0);
assert.deepEqual(legacy.outputs.map(o=>o.name),outputNames);
assert.equal(legacy.removed,9);
const removed=legacy.removed;
extension.loadedGraphNode(legacy);
assert.equal(legacy.removed,removed); // idempotent reload preserves repaired wiring
const current=make([5,24,1024,768,'Custom'],false);
extension.loadedGraphNode(current);
assert.deepEqual(current.widgets.map(w=>w.value),[5,24,1024,768,'Custom']);
assert.equal(current.removed,0); // current output links are untouched
console.log('PASS: legacy positional values, stale inputs, duplicate outputs, idempotence, current workflow');
