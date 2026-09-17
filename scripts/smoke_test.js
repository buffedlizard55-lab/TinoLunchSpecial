/* Dependency-free rendering and interaction regression tests.
   node scripts/smoke_test.js [all|lunch|transit] */
const fs = require('fs');
const assert = require('assert/strict');
const vm = require('vm');
const page = process.argv[2] || 'all';
assert(['all', 'lunch', 'transit'].includes(page));
const store = {};
function el(id) {
  return { id, innerHTML: '', textContent: '', value: '', checked: false, hidden: false,
    events: {}, dataset: {}, setAttribute() {}, getAttribute() { return 'X1'; },
    addEventListener(name, fn) { this.events[name] = fn; },
    classList: { toggle() {}, add() {}, remove() {} } };
}
function get(id) { return store[id] ||= el(id); }
global.document = {
  body: { dataset: { page } }, getElementById: get, querySelectorAll: () => [],
  addEventListener: (ev, cb) => { global.ready = cb; },
};
global.window = { scrollTo() {} };
vm.runInThisContext(fs.readFileSync(`${__dirname}/../data/generated.js`, 'utf8'));
vm.runInThisContext(fs.readFileSync(`${__dirname}/../assets/app.js`, 'utf8'));
function event(id, kind, value) { get(id).events[kind]({target:{value, checked:value}}); }
function countRows() { return (get('lbody').innerHTML.match(/<tr /g) || []).length; }
(async () => {
  await global.ready();
  const data = window.TINO_DATA;
  const entries = data.specials.entries;
  for (const [id, element] of Object.entries(store)) {
    assert(!/\bundefined\b|\bNaN\b|Data not built yet/.test(element.innerHTML), `Bad render: ${id}`);
  }
  if (page !== 'transit') {
    const complete = entries.filter(e => e.deal_audit?.status === 'complete');
    const local = complete.filter(e => e.distance_mi != null && e.distance_mi <= 15);
    assert(get('panel-lunch').innerHTML.includes(`${complete.length} complete official-source checks`));
    assert(get('panel-lunch').innerHTML.includes(`archive of ${entries.length} entries`));
    assert.equal(countRows(), local.length);
    assert(!get('panel-lunch').innerHTML.includes('Top five for a Tuesday'));
    assert(!get('lbody').innerHTML.includes('fits 11:50 departure'));
    assert(!get('panel-deals').innerHTML.includes('St. John'));
    assert(get('panel-deals').innerHTML.includes('per combo (2 or 3 people)'));
    event('lradius','change','all');
    assert.equal(countRows(), complete.length, 'Unknown coordinates available only outside radius restriction');
    event('lq','input','Sushi Roku'); assert.equal(countRows(),1, 'Consolidated duplicate');
    event('lq','input','zzzz-no-restaurant'); assert.equal(countRows(),0);
    event('lq','input','');
    event('lofficial','change',false);
    event('ldeals','change',false);
    assert.equal(countRows(),entries.length, 'Archive remains inspectable');
    event('lcity','change','Cupertino');
    assert.equal(countRows(),entries.filter(e=>e.city==='Cupertino').length);
    event('lreset','click',null); assert.equal(countRows(),local.length);
    assert.equal(get('lofficial').checked,true); assert.equal(get('lradius').value,'15');
    event('lcheap','change',true);
    assert.equal(countRows(),local.filter(e=>e.lunch_special.price_from<=15).length);
  }
  if (page !== 'lunch') {
    for (const id of ['panel-overview','panel-outbound','panel-return','panel-fares','panel-sources','panel-method'])
      assert(get(id).innerHTML.length>100, `${id} must render`);
  }
  if (page === 'transit') assert(!store['panel-deals'], 'Transit page does not render deals');
  if (page === 'lunch') assert(!store['panel-outbound'], 'Lunch page does not render trip planning');
  console.log(`SMOKE TEST PASSED: ${page}; rendering, counts, filtering and page separation`);
})().catch(err=>{console.error(err);process.exitCode=1;});
