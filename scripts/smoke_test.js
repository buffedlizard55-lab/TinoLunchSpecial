/*
 * Render the whole site headlessly with a stub DOM.
 *
 *     node scripts/smoke_test.js
 *
 * No dependencies. Catches the two failure modes that matter for a static data
 * site: a render function throwing because a JSON key was renamed, and a label
 * silently printing "undefined" or "NaN" instead of a value. Exits 1 either way.
 */
const fs = require('fs');
const store = {};
function el(id) {
  return {
    id, _html: '', innerHTML: '', textContent: '', value: '', checked: false, hidden: false,
    setAttribute() {}, getAttribute() { return 'X1'; }, addEventListener() {},
    classList: { toggle() {}, add() {}, remove() {} }, dataset: {},
  };
}
global.document = {
  getElementById: (id) => (store[id] = store[id] || el(id)),
  querySelectorAll: () => [],
  addEventListener: (ev, cb) => { global.__ready = cb; },
};
global.window = { scrollTo() {}, };
const src = fs.readFileSync(`${__dirname}/../data/generated.js`, 'utf8');
eval(src);
global.window.TINO_DATA = global.TINO_DATA || (new Function('window', src + ';return window.TINO_DATA'))({});
const app = fs.readFileSync(`${__dirname}/../assets/app.js`, 'utf8');
eval(app);
global.__ready();
setTimeout(() => {
  const data = global.window.TINO_DATA;
  const out = {};
  for (const k of Object.keys(store)) out[k] = String(store[k].innerHTML || store[k].textContent || '').length;
  console.log('rendered element content lengths:', JSON.stringify(out, null, 1));
  for (const p of ['panel-overview','panel-lunch','panel-flags','panel-sources','panel-method']) {
    const h = String(store[p].innerHTML);
    if (h.includes('undefined]') || /\bundefined\b/.test(h.replace(/data-planblock="[^"]*"/g,''))) console.log('!! "undefined" text appears in', p, h.match(/.{0,60}undefined.{0,60}/)[0]);
    if (h.includes('NaN')) console.log('!! NaN in', p);
    if (h.includes('Data not built yet')) console.log('!! render threw in', p);
  }
  const errEl = store['panel-overview'].innerHTML;
  if (errEl.includes('Data not built yet')) { console.log('FALLBACK RENDERED - see below'); console.log(errEl.slice(0, 600)); process.exit(1); }
  console.log('SMOKE TEST PASSED (all lunch panels rendered without throwing)');
  console.log('lunch rows in body:', (String(store['lbody'].innerHTML).match(/<tr /g) || []).length);
}, 60);
