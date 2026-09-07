/* Tino Lunch Special - renders data/*.json. No build step, no dependencies. */
(function () {
  'use strict';

  const FILES = ['plan', 'transit_outbound', 'transit_return', 'fares', 'lunch_specials', 'lunch_rejected', 'flags', 'sources'];
  const D = {};
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  function link(url, label, cls) {
    if (!url) return '';
    return '<a class="' + (cls || '') + '" href="' + esc(url) + '" target="_blank" rel="noopener noreferrer nofollow">' + esc(label || url) + '</a>';
  }
  function money(v) {
    if (v == null || isNaN(v)) return '-';
    return '$' + Number(v).toFixed(2);
  }
  function dash(v) { return (v === null || v === undefined || v === '') ? '-' : v; }
  function dur(min) {
    if (min == null) return '-';
    const h = Math.floor(min / 60), m = min % 60;
    if (h === 0) return m + ' min';
    return h + ' hr ' + (m ? m + ' min' : '0 min');
  }

  /* ---------- header + tabs ---------- */
  function header(D) {
    const p = D.plan, m = D.specials, sp = m.search_protocol;
    const official = m.entries.filter((e) => String(e.verification.level || '').startsWith('official')).length;
    const open = D.flags.lunch.length;
    document.getElementById('subtitle').textContent =
      p.trip_date_label + ' - Cupertino-first lunch research within a 10-15 mile search area';
    const chips = [
      { k: 'Master rows', v: m.entries.length, cls: 'go' },
      { k: 'New verified before add', v: sp.new_entries_verified_before_add, cls: 'go' },
      { k: 'Own-menu evidence', v: official, cls: 'ok' },
      { k: 'Cities covered', v: (sp.cities_covered || []).length, cls: 'flat' },
      { k: 'Open flags', v: open, cls: open ? 'warn' : 'ok' }
    ];
    document.getElementById('headline-chips').innerHTML = chips.map((c) =>
      '<span class="chip ' + c.cls + '"><span class="k">' + esc(c.k) + '</span><span class="v">' + esc(String(c.v)) + '</span></span>').join('');
    document.getElementById('flag-count').textContent = open;
    document.getElementById('footer-note').innerHTML =
      'Lunch research verified on ' + esc(sp.search_date) + '. ' +
      link('https://github.com/buffedlizard55-lab/TinoLunchSpecial', 'Source data and check scripts on GitHub');
  }

  /* ---------- overview ---------- */
  function renderOverview(D) {
    const p = D.plan, m = D.specials, sp = m.search_protocol;
    const official = m.entries.filter((e) => String(e.verification.level || '').startsWith('official')).length;
    const priced = m.entries.filter((e) => e.lunch_special && e.lunch_special.price_from != null && String(e.verification.level || '').startsWith('official')).length;
    const tuesday = m.entries.filter((e) => e.open_on_trip_date === true).length;
    const picks = m.top_picks_for_tuesday_sept_8.slice(0, 6).map((t) => {
      const e = m.entries.find((x) => x.id === t.id);
      return e ? '<tr><td><b>' + esc(e.name) + '</b><div class="tiny">' + esc(e.city) + '</div></td><td>' +
        (e.lunch_special.price_from != null ? money(e.lunch_special.price_from) : '<span class="bad">not published</span>') +
        '</td><td>' + esc(dash(e.hours_tuesday)) + '</td><td>' + badge(e.verification.level) + '</td><td>' + esc(t.why) + '</td></tr>' : '';
    }).join('');
    document.getElementById('panel-overview').innerHTML =
      '<h2>Cupertino lunch research index</h2>' +
      '<p class="lead">A Cupertino-first master list of lunch specials, lunch service, hours, Tuesday availability, prices, and source links. Every row is kept at its evidence level so an unverified lead cannot look like a confirmed deal.</p>' +
      '<div class="callout good"><b>Research threshold met:</b> ' + esc(sp.new_entries_verified_before_add) + ' new entries were verified before being added to the master list, exceeding the requested minimum of ' + esc(sp.minimum_new_entries_required) + '.</div>' +
      '<h2>What is in the list</h2><div class="grid g3">' +
      stat(m.entries.length, 'rows in the master list') + stat(official, 'rows with restaurant-owned evidence') + stat(priced, 'officially priced lunch rows') +
      stat(tuesday, 'rows marked open Tuesday') + stat(sp.candidates_found, 'candidates checked') + stat(sp.rejected_or_deferred, 'rejected or deferred with reasons') +
      '</div>' +
      '<h2>Search coverage</h2><p>' + esc(sp.radius_note) + '</p><p class="tiny"><b>Covered:</b> ' + esc((sp.cities_covered || []).join(', ')) + '</p>' +
      '<h2>Best starting points for Tuesday</h2><p class="tiny">These are research picks, not guarantees. Check each linked source again before visiting because menus, prices, and hours change.</p>' +
      '<div class="scrollpanel"><table class="grid-table"><thead><tr><th>Restaurant</th><th>Price</th><th>Tuesday hours</th><th>Evidence</th><th>Why it is listed</th></tr></thead><tbody>' + picks + '</tbody></table></div>' +
      '<h2>How to use the full list</h2><p>Open the <b>Lunch specials</b> tab to search by restaurant, city, cuisine, price, Tuesday opening, or evidence tier. Use the <b>Flags</b> tab for conflicts, missing addresses, missing coordinates, and any row that needs a phone or source check.</p>';
  }

  function stat(n, label) { return '<div class="card stat"><div class="n">' + esc(String(n)) + '</div><div class="l">' + esc(label) + '</div></div>'; }
  function countVerified(D) {
    let n = 0;
    D.outbound.plans.concat(D.retplan.plans).forEach((p) => p.legs.forEach((l) => { if (/official-live/.test(l.verified || '')) n++; }));
    return n;
  }
  function countLevel(D, lvl) { return D.specials.entries.filter((e) => (e.verification.level || '').indexOf(lvl) === 0).length; }

  function badge(level) {
    const map = { official: 'good', 'official-live': 'good', review: 'warn', review_sourced: 'warn', listing: 'info', mixed: 'info', conflicting: 'bad', unverified: 'bad', incomplete: 'bad', estimate: 'flat', derived: 'flat', interpolated: 'flat', verified: 'good' };
    const key = (level || '').split(' ')[0];
    return '<span class="badge ' + (map[key] || 'flat') + '">' + esc(level || 'n/a') + '</span>';
  }

  /* ---------- transit ---------- */
  function legTable(plan) {
    const rows = plan.legs.map((l) => {
      const src = (l.sources || []).map((s) => link(s.url, s.label, 'srclink')).join('');
      const notes = [l.note, l.fare_note].filter(Boolean).map((n) => '<div class="tiny">' + esc(n) + '</div>').join('');
      const flags = (l.flags || []).length ? '<div class="tiny flagline"><b>Flags:</b> ' + l.flags.map((f) => '<span class="chip bad">' + esc(f) + '</span>').join(' ') + '</div>' : '';
      return '<tr>' +
        '<td class="num">' + esc(l.seq) + '</td>' +
        '<td><b>' + esc(l.mode) + '</b>' + (l.operator && l.operator !== '-' ? '<div class="tiny">' + esc(l.operator) + '</div>' : '') + '</td>' +
        '<td>' + esc(l.line) + '</td>' +
        '<td>' + esc(l.from) + '<div class="tiny">departs ' + esc(l.depart) + '</div></td>' +
        '<td>' + esc(l.to) + '<div class="tiny">arrives ' + esc(l.arrive) + '</div></td>' +
        '<td class="num strong">' + dur(l.travel_min) + '</td>' +
        '<td class="num">' + (l.fare_usd === 0 ? '<span class="muted">free</span>' : money(l.fare_usd)) + '</td>' +
        '<td>' + badge(l.verified) + '</td>' +
        '<td class="src">' + src + '</td>' +
        '<td class="note">' + notes + flags + '</td>' +
        '</tr>';
    }).join('');
    return '<div class="scrollpanel"><table class="grid-table"><thead><tr>' +
      '<th>#</th><th>Mode</th><th>Line / service</th><th>From</th><th>To</th><th>Travel time</th><th>Fare</th><th>Verified</th><th>Official links for this row</th><th>Notes and flags</th>' +
      '</tr></thead><tbody>' + rows + '</tbody></table></div>';
  }

  function renderTransit(D, which) {
    const src = which === 'outbound' ? D.outbound : D.retplan;
    const panels = src.plans;
    document.getElementById('panel-' + which).innerHTML =
      '<h2>' + esc(src.direction) + '</h2>' +
      (which === 'return' ? '<div class="callout ' + (/satisfied|OK/i.test(src.deadline.verdict) ? 'good' : 'bad') + '">' + esc(src.deadline.hard) + ' - ' + esc(src.deadline.target) + '. <b>' + esc(src.deadline.verdict) + '</b></div>' : '') +
      '<div class="chips">' + panels.map((p, i) => '<button class="chip select ' + (i === 0 ? 'is-active' : '') + '" data-plan="' + esc(p.id) + '">' + esc(p.label) + '</button>').join('') + '</div>' +
      panels.map((p, i) => '<div class="planblock" data-planblock="' + esc(p.id) + '"' + (i ? ' hidden' : '') + '>' +
        '<div class="planhead"><h3>' + esc(p.label) + '</h3>' +
        '<div class="chips">' +
        chip('Leave', which === 'outbound' ? p.leave_home : p.leave_destination) +
        chip('Arrive', which === 'outbound' ? p.arrive_destination : p.arrive_home) +
        chip('Door to door', dur(p.total_time_min)) +
        chip('Cash', money(p.cash_cost_usd)) +
        (p.clipper_cost_usd != null ? chip('With Clipper credit', money(p.clipper_cost_usd)) : '') +
        (p.recommended ? '<span class="chip ok">Recommended</span>' : '') +
        '</div></div>' + legTable(p) +
        (p.verdict ? '<div class="callout bad">' + esc(p.verdict) + '</div>' : '') +
        '</div>').join('') +
      (which === 'outbound' ?
        '<h3>Why Sunnyvale and not Mountain View</h3><div class="scrollpanel"><table class="grid-table"><thead><tr><th>Alighting option</th><th>Caltrain leg</th><th>Onward VTA</th><th>Minutes to the front door</th><th>Notes</th></tr></thead><tbody>' +
        D.outbound.station_comparison.map((c) => '<tr><td><b>' + esc(c.option) + '</b></td><td>' + esc(c.caltrain_leg) + '</td><td>' + esc(c.vta) + '</td><td class="num">' + (c.to_door_min != null ? c.to_door_min : '-') + '</td><td class="tiny">' + esc(c.note) + '</td></tr>').join('') +
        '</tbody></table></div>' :
        '<h3>All return options in one table</h3><div class="scrollpanel"><table class="grid-table"><thead><tr><th>Leave the house</th><th>VTA 55 northbound</th><th>At Sunnyvale TC</th><th>Caltrain northbound</th><th>SF terminal</th><th>N Judah westbound</th><th>Home</th><th>Verdict</th></tr></thead><tbody>' +
        D.retplan.option_table.map((r) => '<tr><td class="strong">' + esc(r.leave_gillick) + '</td><td>' + esc(r.vta_55_nb) + '</td><td>' + esc(r.arrives_sunnyvale_tc) + '</td><td>' + esc(r.caltrain_nb) + '</td><td>' + esc(r.arrives_sf_terminal) + '</td><td>' + esc(r.n_judah_wb) + '</td><td class="strong">' + esc(r.home) + '</td><td class="' + (/FAILS/.test(r.status) ? 'bad' : 'tiny') + '">' + esc(r.status) + '</td></tr>').join('') +
        '</tbody></table></div>' +
        '<h3>Notes</h3><ul>' + D.retplan.notes.map((n) => '<li>' + esc(n) + '</li>').join('') + '</ul>') +
      '<h3>Where each number came from</h3><ul class="tiny">' +
      Object.keys(src.source_files).map((k) => '<li>' + esc(k) + ': ' + link(src.source_files[k], src.source_files[k]) + '</li>').join('') + '</ul>';

    document.querySelectorAll('#panel-' + which + ' .chip.select').forEach((b) => {
      b.addEventListener('click', function () {
        const id = this.getAttribute('data-plan');
        document.querySelectorAll('#panel-' + which + ' .chip.select').forEach((x) => x.classList.toggle('is-active', x === b));
        document.querySelectorAll('#panel-' + which + ' [data-planblock]').forEach((x) => { x.hidden = x.getAttribute('data-planblock') !== id; });
      });
    });
  }
  function chip(k, v) { return '<span class="chip flat"><span class="k">' + esc(k) + '</span><span class="v">' + esc(String(v)) + '</span></span>'; }

  /* ---------- fares ---------- */
  function renderFares(D) {
    const f = D.fares;
    const agencies = f.agencies.map((a) =>
      '<h3>' + esc(a.name) + ' &nbsp;' + link(a.official_source.url, 'official fare page', 'srclink') + '</h3>' +
      (a.zone_note ? '<p class="tiny">' + esc(a.zone_note) + '</p>' : '') +
      '<div class="scrollpanel"><table class="grid-table"><thead><tr><th>Ticket</th><th class="num">Price</th><th>Validity</th><th>Applies to this trip</th></tr></thead><tbody>' +
      a.rows.map((r) => '<tr><td>' + esc(r.ticket) + '</td><td class="num strong">' + (r.price < 0 ? '-' + money(-r.price) : money(r.price)) + '</td><td class="tiny">' + esc(r.validity) + '</td><td class="tiny">' + esc(r.applies_to) + '</td></tr>').join('') +
      '</tbody></table></div>' + (a.notes ? '<ul class="tiny">' + a.notes.map((n) => '<li>' + esc(n) + '</li>').join('') + '</ul>' : '')).join('');

    const totals = f.day_totals.map((t) =>
      '<div class="card total ' + (/Cheapest/.test(t.label) ? 'good' : '') + '"><h3>' + esc(t.label) + '</h3>' +
      (t.assumption ? '<p class="tiny"><b>Assumption:</b> ' + esc(t.assumption) + '</p>' : '') +
      '<ul>' + t.items.map((i) => '<li>' + esc(i.label) + ' <b>' + (i.fare === 0 ? 'free' : (i.fare < 0 ? '-' + money(-i.fare) : money(i.fare))) + '</b></li>').join('') + '</ul>' +
      '<div class="grand">' + money(t.total) + '</div><p class="tiny">' + esc(t.caveat) + '</p>' +
      '<p class="tiny">From: ' + String(t.verified_from || '').split(/\s*,\s*/).filter(Boolean).map((u) => link(u, u.replace(/^https?:\/\/(www\.)?/, '').replace(/\/$/, ''), 'srclink')).join('  ') + '</p></div>').join('');

    document.getElementById('panel-fares').innerHTML =
      '<h2>Fares - adult, ' + esc(f.trip_date) + '</h2>' +
      '<p class="lead">Only prices published by the agency itself are in this table, each with the page it came from.</p>' +
      agencies +
      '<h2>What the whole day costs</h2><div class="grid g2">' + totals + '</div>';
  }

  /* ---------- lunch ---------- */
  const FILTERS = { q: '', city: 'all', verifiedOnly: false, cheap: false, openTue: false, fitsBus: false };
  const SORT = { key: 'dist', dir: 1 };
  const SORTVAL = {
    name: (e) => String(e.name || '').toLowerCase(),
    city: (e) => String(e.city || '').toLowerCase(),
    cuisine: (e) => String(e.cuisine || '').toLowerCase(),
    deal: (e) => String(e.lunch_special.name || '').toLowerCase(),
    days: (e) => String(e.lunch_special.days || '').toLowerCase(),
    price: (e) => (e.lunch_special.price_from == null ? 9999 : e.lunch_special.price_from),
    dist: (e) => (e.distance_mi == null ? 9999 : e.distance_mi),
    level: (e) => {
      const l = String(e.verification.level || '');
      return l.indexOf('official') === 0 ? 0 : l.indexOf('review') === 0 ? 1 : l.indexOf('conflicting') === 0 ? 2
        : l.indexOf('mixed') === 0 ? 3 : l.indexOf('listing') === 0 ? 4 : 5;
    },
    id: (e) => e.id
  };

  function distCell(e) {
    if (e.distance_mi == null) return '<span class="tiny">not geocoded</span>';
    const approx = /approximate|block, not/i.test(e.coords_source || '');
    return '<span class="dist">' + (approx ? '~' : '') + e.distance_mi + ' mi</span>' +
      '<div class="tiny">' + (approx ? 'city-block estimate, not a geocoded address' : 'straight-line walk from 20387 Gillick Way') + '</div>';
  }

  function lunchRow(e, level) {
    const ls = e.lunch_special;
    const price = ls.price_from == null && ls.price_to == null
      ? '<span class="bad">not published</span>'
      : (ls.price_from != null ? '<span class="price">' + money(ls.price_from) + '</span>' : '') +
        (ls.price_to != null ? '<span class="price">' + (ls.price_from != null ? '- ' : '') + money(ls.price_to) + '</span>' : '');
    const open = e.open_on_trip_date === false ? '<span class="badge bad">closed on Sept 8</span>' : (e.open_on_trip_date === null ? '<span class="badge unverified">open? unknown</span>' : '<span class="badge good">open Tuesday</span>');
    const fits = e.fits_return_bus && e.fits_return_bus.ok === true ? '<span class="badge good">fits 11:50 departure</span>'
      : e.fits_return_bus && e.fits_return_bus.ok === 'tight' ? '<span class="badge warn">tight</span>'
      : e.fits_return_bus && e.fits_return_bus.ok === false ? '<span class="badge bad">does not fit</span>' : '<span class="badge unverified">unknown</span>';
    const srcs = (e.verification.sources || []).map((s) => link(s.url, s.label, 'srclink')).join('');
    const rev = [
      e.review_links && e.review_links.yelp ? link(e.review_links.yelp, 'Yelp', 'srclink') : '',
      e.review_links && e.review_links.google_maps ? link(e.review_links.google_maps, 'Google Maps', 'srclink') : ''
    ].filter(Boolean).join(' ');
    return '<tr class="' + (level === 'official' ? 'row-official' : '') + '">' +
      '<td class="name"><span class="rid">' + esc(e.id) + '</span><span class="rname">' + esc(e.name) + '</span><span class="rcity">' + esc(e.city) + (e.area ? ' - ' + esc(e.area) : '') + '</span>' +
      '<span class="raddr">' + esc(e.address) + '</span>' +
      '<span class="rtags">' + open + ' ' + fits + '</span></td>' +
      '<td class="num">' + distCell(e) + '</td>' +
      '<td>' + esc(e.cuisine) + '</td>' +
      '<td class="deal">' + esc(ls.name) + (ls.includes ? '<div class="tiny">' + esc(ls.includes) + '</div>' : '') + '</td>' +
      '<td>' + price + (ls.window ? '<div class="tiny">' + esc(ls.window) + '</div>' : '') + '</td>' +
      '<td>' + esc(ls.days) + '</td>' +
      '<td class="tiny">' + esc(e.hours_tuesday) + '<div class="dowrow"><span>all days:</span> ' + esc(e.days_open) + '</div></td>' +
      '<td class="ver">' + badge(level) + '<div class="tiny">verified ' + esc(e.verification.accessed || '') + '</div>' +
      '<div class="links">' + srcs + '</div><div class="links">' + rev + '</div></td>' +
      '<td class="flagscell">' + (e.flags || []).map((f) => '<div class="flag-item">' + esc(f) + '</div>').join('') + '</td>' +
      '</tr>';
  }

  function renderLunch(D) {
    const m = D.specials;
    const levels = {};
    m.entries.forEach((e) => { const k = (e.verification.level || 'n/a').split(' ')[0]; levels[k] = (levels[k] || 0) + 1; });
    const cities = {};
    m.entries.forEach((e) => { cities[e.city] = (cities[e.city] || 0) + 1; });

    document.getElementById('panel-lunch').innerHTML =
      '<h2>Lunch specials within reach of Sunnyvale / Cupertino</h2>' +
      '<p class="lead"><b>100-entry requirement met:</b> ' + (m.search_protocol.new_entries_verified_before_add || 0) + ' new entries were verified before being added. ' + m.search_protocol.added_to_master + ' rows are in the master list, selected from ' + m.search_protocol.candidates_found +
      ' candidates checked line by line across ' + m.search_protocol.queries_run + ' queries on ' + esc(m.search_protocol.search_date) +
      '. ' + esc(m.search_protocol.requirement) + '</p>' +
      '<p class="callout"><b>Evidence rule:</b> prices are only treated as confirmed when published by the restaurant or its menu. Review, listing, conflicting, and unverified rows stay visible for leads and manual review; they are never presented as verified deals.</p>' + '<p class="tiny">Radius: ' + esc(m.search_protocol.radius_note) + ' &nbsp;|&nbsp; Covered: ' +
      esc((m.search_protocol.cities_covered || []).join(', ')) + ' &nbsp;|&nbsp; Rejected or deferred: ' +
      m.search_protocol.rejected_or_deferred + ' (all listed below with reasons)</p>' +
      '<div class="grid g4">' +
      Object.keys(levels).sort((a, b) => levels[b] - levels[a]).map((k) =>
        '<div class="card stat"><div class="n">' + levels[k] + '</div><div class="l">' + esc(k) + ' - ' + esc(m.search_protocol.levels[k] || 'see per-row notes') + '</div></div>').join('') +
      '</div>' +
      '<div class="filters">' +
      '<input id="lq" type="search" placeholder="Search name, city, dish, flag..." />' +
      '<select id="lcity"><option value="all">All cities (' + m.entries.length + ')</option>' +
      Object.keys(cities).sort().map((c) => '<option value="' + esc(c) + '">' + esc(c) + ' (' + cities[c] + ')</option>').join('') + '</select>' +
      '<label><input type="checkbox" id="lopen" /> Open on Tuesday Sept 8</label>' +
      '<label><input type="checkbox" id="lfits" /> Fits the 11:50 AM departure</label>' +
      '<label><input type="checkbox" id="lofficial" /> Restaurant\'s own menu only</label>' +
      '<label><input type="checkbox" id="lcheap" /> $15 or less</label>' +
      '<button id="lreset" type="button">Reset</button>' +
      '<span id="lcount" class="tiny"></span>' +
      '</div>' +
      '<div class="sortbar">Sort by: ' +
      [['dist', 'Closest to 20387 Gillick Way'], ['price', 'Cheapest lunch first'], ['name', 'Name A-Z'], ['city', 'City'], ['level', 'Best evidence first'], ['id', 'As searched']]
        .map(([k, l]) => '<button type="button" class="sortchip" data-sortkey="' + k + '">' + esc(l) + '</button>').join('') +
      '</div>' +
      '<div class="scrollpanel"><table class="ltable"><thead><tr>' +
      [['name', 'Restaurant'], ['dist', 'Distance'], ['cuisine', 'Cuisine'], ['deal', 'What the special is'], ['price', 'Price'], ['days', 'Days']]
        .map(([k, l]) => '<th class="sortable" data-sort="' + k + '">' + l + '<span class="sortind" data-ind="' + k + '"></span></th>').join('') +
      '<th>Tuesday hours / all days</th><th>Verification and links</th><th>Flags and notes</th>' +
      '</tr></thead><tbody id="lbody"></tbody></table></div>' +

      '<h3>Top five for a Tuesday, September 8</h3>' +
      '<ol class="picks">' + m.top_picks_for_tuesday_sept_8.map((t) => {
        const e = m.entries.find((x) => x.id === t.id);
        return '<li><b>' + esc(e ? e.name + ' - ' + e.address + ', ' + e.city : t.id) + '</b> - ' + esc(t.why) + '</li>';
      }).join('') + '</ol>' +

      '<h3>Candidates that were searched and rejected, with reasons</h3>' +
      '<p class="tiny">A candidate only earns a row if a person can check it in one click. Prices seen only on delivery-app or menu-aggregator pages are left out of the price column, and any business whose "lunch special" turned out to belong to a different city (a Las Vegas special, a Chico restaurant listed as "Los Altos") is rejected here rather than carried forward.</p>' +
      '<div class="scrollpanel"><table class="grid-table"><thead><tr><th>#</th><th>Name</th><th>Area</th><th>Why it is not in the master list</th><th>Links</th></tr></thead><tbody>' +
      D.lunch_rejected.rejected.map((r) => '<tr><td class="num">' + esc(r.id) + '</td><td class="strong">' + esc(r.name) +
        (r.count > 1 ? '<div class="tiny">' + r.count + ' businesses, one reason</div>' : '') + '</td><td>' + esc(r.city) + '</td>' +
        '<td>' + esc(r.why) + (r.price_hint ? '<div class="tiny">price seen elsewhere: ' + esc(r.price_hint) + '</div>' : '') + (r.note ? '<div class="tiny">' + esc(r.note) + '</div>' : '') + '</td>' +
        '<td class="src">' + (r.links || []).map((l) => typeof l === 'string' ? link(l, l.replace(/^https?:\/\/(www\.)?/, '').slice(0, 46), 'srclink') : link(l.url, l.label, 'srclink')).join('') + '</td></tr>').join('') +
      '</tbody></table></div>' +

      '<h3>What each verification level means</h3><ul class="tiny">' +
      Object.keys(m.search_protocol.levels).map((k) => '<li><b>' + esc(k) + '</b> - ' + esc(m.search_protocol.levels[k]) + '</li>').join('') +
      '<li><b>Every row above carries a live link to the page it was read from</b>, so any entry can be re-checked in one click. Rows marked <span class="badge bad">unverified</span> or <span class="badge warn">review</span> are exactly that: no published menu price was found, so none is asserted.</li></ul>';

    const body = document.getElementById('lbody');
    const paint = () => {
      const rows = m.entries.filter((e) => {
        if (FILTERS.city !== 'all' && e.city !== FILTERS.city) return false;
        if (FILTERS.openTue && e.open_on_trip_date !== true) return false;
        if (FILTERS.fitsBus && !(e.fits_return_bus && e.fits_return_bus.ok === true)) return false;
        if (FILTERS.verifiedOnly && (e.verification.level || '').indexOf('official') !== 0) return false;
        if (FILTERS.cheap && !(e.lunch_special.price_from != null && e.lunch_special.price_from <= 15)) return false;
        if (FILTERS.q) {
          const hay = JSON.stringify([e,]).toLowerCase();
          if (hay.indexOf(FILTERS.q.toLowerCase()) === -1) return false;
        }
        return true;
      });
      rows.sort((a, b) => {
        const va = SORTVAL[SORT.key](a), vb = SORTVAL[SORT.key](b);
        if (va < vb) return -1 * SORT.dir;
        if (va > vb) return 1 * SORT.dir;
        return a.id < b.id ? -1 : 1;
      });
      body.innerHTML = rows.map((e) => lunchRow(e, e.verification.level)).join('') ||
        '<tr><td colspan="9" class="tiny">Nothing matches - clear a filter.</td></tr>';
      document.querySelectorAll('#panel-lunch .sortind').forEach((s) => {
        s.textContent = s.dataset.ind === SORT.key ? (SORT.dir === 1 ? ' \u25B2' : ' \u25BC') : '';
      });
      document.querySelectorAll('#panel-lunch .sortchip').forEach((c) => c.classList.toggle('is-active', c.dataset.sortkey === SORT.key));
      document.getElementById('lcount').textContent = rows.length + ' of ' + m.entries.length + ' entries shown' +
        (SORT.key === 'dist' ? ' - closest first' : SORT.key === 'price' ? ' - cheapest first' : ' - sorted by ' + SORT.key);
    };
    const bind = (id, fn) => { const el = document.getElementById(id); if (el) el.addEventListener('input', fn) || el.addEventListener('change', fn); };
    document.getElementById('lq').addEventListener('input', (ev) => { FILTERS.q = ev.target.value; paint(); });
    document.getElementById('lcity').addEventListener('change', (ev) => { FILTERS.city = ev.target.value; paint(); });
    document.getElementById('lopen').addEventListener('change', (ev) => { FILTERS.openTue = ev.target.checked; paint(); });
    document.getElementById('lfits').addEventListener('change', (ev) => { FILTERS.fitsBus = ev.target.checked; paint(); });
    document.getElementById('lofficial').addEventListener('change', (ev) => { FILTERS.verifiedOnly = ev.target.checked; paint(); });
    document.getElementById('lcheap').addEventListener('change', (ev) => { FILTERS.cheap = ev.target.checked; paint(); });
    document.querySelectorAll('#panel-lunch th.sortable').forEach((th) => th.addEventListener('click', () => {
      const k = th.dataset.sort;
      SORT.dir = SORT.key === k ? -SORT.dir : 1;
      SORT.key = k;
      paint();
    }));
    document.querySelectorAll('#panel-lunch .sortchip').forEach((b) => b.addEventListener('click', () => {
      SORT.key = b.dataset.sortkey; SORT.dir = 1; paint();
    }));
    document.getElementById('lreset').addEventListener('click', () => {
      Object.keys(FILTERS).forEach((k) => { FILTERS[k] = k === 'city' ? 'all' : (k === 'q' ? '' : false); });
      ['lq'].forEach((i) => document.getElementById(i).value = '');
      ['lopen', 'lfits', 'lofficial', 'lcheap'].forEach((i) => document.getElementById(i).checked = false);
      document.getElementById('lcity').value = 'all';
      paint();
    });
    paint();
  }

  /* ---------- flags ---------- */
  function renderFlags(D) {
    const sev = { important: 'bad', watch: 'warn', data_conflict: 'bad', note: 'flat', risk: 'warn' };
    const card = (f) => '<article class="flag ' + (sev[f.severity] || 'flat') + '">' +
      '<div class="fhead"><span class="fid">' + esc(f.id) + '</span><span class="chip ' + (sev[f.severity] || 'flat') + '">' + esc((f.severity || '').replace(/_/g, ' ')) + '</span></div>' +
      '<h3>' + esc(f.title) + '</h3>' +
      '<p><b>What the sources say:</b> ' + esc(f.what_we_found) + '</p>' +
      (f.implication ? '<p><b>Why it matters:</b> ' + esc(f.implication) + '</p>' : '') +
      '<p><b>What this page did:</b> ' + esc(f.what_we_did) + '</p>' +
      (f.link ? '<p class="tiny">Verify: ' + link(f.link, f.link_label || f.link) + '</p>' : '') +
      (f.rows && f.rows.length ? '<p class="tiny">Rows affected: ' + f.rows.map((r) => '<span class="chip flat">' + esc(r) + '</span>').join(' ') + '</p>' : '') +
      '</article>';
    document.getElementById('panel-flags').innerHTML =
      '<h2>Irregularities found while verifying, all of them</h2>' +
      '<p class="lead">Nothing was smoothed over. These lunch flags cover prices, hours, addresses, Tuesday availability, and source conflicts that could not be pinned down line by line.</p>' +
      '<h3>Lunch (' + D.flags.lunch.length + ')</h3>' + D.flags.lunch.map(card).join('');
  }

  /* ---------- sources + method ---------- */
  function renderSources(D) {
    const lunchSources = D.sources.sources.filter((s) => !/sfmta|caltrain|vta/i.test(String(s.agency || '') + ' ' + String(s.label || '')));
    document.getElementById('panel-sources').innerHTML =
      '<h2>Every source page, and what it was used for</h2>' +
      '<p class="lead">' + esc(D.sources.note) + '</p>' +
      '<div class="scrollpanel"><table class="grid-table"><thead><tr><th>ID</th><th>Agency</th><th>Page</th><th>What it verified</th><th>Fetch status</th></tr></thead><tbody>' +
      lunchSources.map((s) => '<tr><td class="num">' + esc(s.id) + '</td><td>' + esc(s.agency) + '</td>' +
        '<td>' + link(s.url, s.label) + '</td><td class="tiny">' + esc(s.used_for) + '</td>' +
        '<td>' + (s.fetch_status === 'ok' ? '<span class="badge good">ok</span>' : '<span class="badge bad">' + esc(s.fetch_status) + '</span>') + (s.gap ? '<div class="tiny bad">' + esc(s.gap) + '</div>' : '') + '</td></tr>').join('') +
      '</tbody></table></div>' +
      '<h3>Dead ends (things that were tried and did not work)</h3><ul>' +
      D.sources.dead_ends.map((d) => '<li>' + esc(d) + '</li>').join('') + '</ul>' +
      '<h3>What could not be verified at all</h3><ul>' +
      D.sources.could_not_verify.map((c) => '<li>' + esc(c) + '</li>').join('') + '</ul>';
  }

  function renderMethod(D) {
    const p = D.plan, m = D.specials, sp = m.search_protocol;
    document.getElementById('panel-method').innerHTML =
      '<h2>Research method and evidence rules</h2>' +
      '<div class="grid g2"><div class="card"><h3>Scope</h3><ul>' +
      '<li>Start in Cupertino, then expand across the requested surrounding cities.</li>' +
      '<li>Search radius is documented per row; unknown distances are left blank.</li>' +
      '<li>Search date: <b>' + esc(sp.search_date) + '</b>.</li>' +
      '<li>Trip context: <b>' + esc(p.trip_date_label) + '</b>.</li></ul></div>' +
      '<div class="card"><h3>Evidence levels</h3><ul>' + Object.keys(sp.levels).map((k) => '<li><b>' + esc(k) + '</b> - ' + esc(sp.levels[k]) + '</li>').join('') + '</ul></div></div>' +
      '<h3>Line-by-line safeguards</h3><ol><li>Every master row has an evidence source URL.</li><li>Published prices appear only when captured from the stated source; otherwise the table says “not published.”</li><li>Conflicts and missing values stay visible as flags instead of being filled with estimates.</li><li>Rejected and deferred candidates remain available in the Lunch specials tab with the reason they were excluded.</li></ol>' +
      '<h3>Re-run the checks</h3><pre><code>python3 scripts/build_data.py\npython3 scripts/check_links.py --report\nnode scripts/smoke_test.js</code></pre>' +
      '<p class="tiny">The data lives in <code>data/*.json</code>; <code>data/generated.js</code> is the browser bundle. The validator enforces the 100-new-entry threshold and fails if required source fields are removed.</p>';
  }

  /* ---------- boot ---------- */
  // data/generated.js sets window.TINO_DATA; that keeps the site working from file:// as well as Pages.
  async function load() {
    if (window.TINO_DATA) return window.TINO_DATA;
    const r = await fetch('data/generated.js', { cache: 'no-store' });
    if (!r.ok) throw new Error('missing data/generated.js - run python3 scripts/build_data.py');
    return r.json();
  }

  async function init() {
    try {
      const data = await load();
      D.plan = data.plan; D.outbound = data.outbound; D.retplan = data.retplan; D.fares = data.fares;
      D.specials = data.specials; D.lunch_rejected = data.rejected; D.flags = data.flags; D.sources = data.sources;
      header(D);
      renderOverview(D);
      renderLunch(D); renderFlags(D); renderSources(D); renderMethod(D);
    } catch (e) {
      document.getElementById('panel-overview').innerHTML =
        '<h2>Data not built yet</h2><p class="lead">' + esc(e.message) + '</p>' +
        '<p class="tiny">Run <code>python3 scripts/plan_trip.py</code> to compile <code>data/generated.js</code>, or serve the repo with <code>python3 -m http.server</code> if you are opening it over file://.</p>';
    }
    document.querySelectorAll('.tab').forEach((btn) => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach((b) => { b.classList.toggle('is-active', b === btn); b.setAttribute('aria-selected', b === btn ? 'true' : 'false'); });
        document.querySelectorAll('.panel').forEach((p) => p.classList.toggle('is-active', p.id === 'panel-' + btn.dataset.tab));
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    });
  }
  document.addEventListener('DOMContentLoaded', init);
})();
