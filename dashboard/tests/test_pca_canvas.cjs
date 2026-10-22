// Exercise the actual renderer with Canvas 2D only (no WebGL/browser dependency).
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const template = fs.readFileSync(require('node:path').join(__dirname, '../components/pca_viewer.html'), 'utf8');
const script = template.match(/<script>\s*([\s\S]*?)<\/script>/)[1];
for (const filter of ['All', '1']) {
  const points = [0, 1, 2].map(i => ({xyz: [i - 1, i, -i], cluster: String(i % 2), id: String(i), segment: 'Segment', color: '#a855f7'}));
  const payload = {points, centroids: [{...points[0], centroid: true}], variance: [0.5, 0.3, 0.2], filter};
  let dots = 0;
  const elements = {};
  const ctx = new Proxy({}, {get: (_, key) => (...args) => {
    for (const arg of args) if (typeof arg === 'number') assert.ok(Number.isFinite(arg), `${key}: invalid coordinate`);
    if (key === 'arc') dots++;
  }});
  function element() {return {style: {}, clientWidth: 1000, clientHeight: 535, append() {}, addEventListener(name, fn) {this.events ??= {}; this.events[name] = fn;}, getBoundingClientRect() {return {left: 0, top: 0};}, setPointerCapture() {}};}
  const document = {getElementById(id) {return elements[id] ??= element();}, createElement: element, createTextNode: s => s};
  document.getElementById('pca-data').textContent = JSON.stringify(payload);
  document.getElementById('plot').getContext = type => {assert.equal(type, '2d'); return ctx;};
  const context = vm.createContext({document, window: {devicePixelRatio: 2}, ResizeObserver: class {constructor(fn) {this.fn = fn;} observe() {this.fn();}}});
  vm.runInContext(script, context);
  assert.equal(dots, 3);
  assert.equal(elements.count.textContent, filter === 'All' ? '3 customers' : '1 customers');
  const canvas = elements.plot;
  const before = vm.runInContext('JSON.stringify(projected.map(p => [p.x,p.y]))', context);
  canvas.events.pointerdown({clientX: 100, clientY: 100, pointerId: 1});
  canvas.events.pointermove({clientX: 180, clientY: 140});
  canvas.events.pointerup();
  assert.notEqual(vm.runInContext('JSON.stringify(projected.map(p => [p.x,p.y]))', context), before);
  canvas.events.wheel({deltaY: -100, preventDefault() {}});
  assert.ok(vm.runInContext('zoom', context) > 1);
  elements.reset.events.click();
  assert.equal(vm.runInContext('JSON.stringify(projected.map(p => [p.x,p.y]))', context), before);
  const target = vm.runInContext('projected.find(p => active(p.point))', context);
  canvas.events.pointermove({clientX: target.x, clientY: target.y});
  assert.equal(elements.tooltip.style.display, 'block');
  assert.match(elements.tooltip.textContent, /PC3:/);
}
console.log('Canvas renderer: coordinates, filtering, rotation, zoom, reset, and hover passed.');
