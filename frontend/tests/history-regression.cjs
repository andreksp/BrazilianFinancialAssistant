// Isolated service/component regressions without a browser or paid LLM calls.
const ts = require('typescript');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { of, throwError } = require('rxjs');
class HttpParams {
  constructor(values = {}) { this.values = values; }
  set(key, value) { return new HttpParams({ ...this.values, [key]: value }); }
}
function load(file) {
  const source = fs.readFileSync(path.join(__dirname, '../src/app', file), 'utf8');
  const js = ts.transpileModule(source, { compilerOptions: {
    module: ts.ModuleKind.CommonJS, experimentalDecorators: true,
  }}).outputText;
  const exports = {};
  vm.runInThisContext('(function(exports, require) {' + js + '\n})')(exports, name => {
    if (name === '@angular/core') return { Injectable: () => x => x, Component: () => x => x };
    if (name === '@angular/common/http') return { HttpParams };
    if (name.includes('api.service')) return {};
    return require(name);
  });
  return exports;
}
const { ApiService } = load('services/api.service.ts');
const calls = [];
const api = new ApiService({
  get: (...args) => { calls.push(args); return of([]); },
  post: (...args) => { calls.push(args); return of({}); },
});
api.processTrade({});
assert.equal(calls.pop()[2].params.values.user_id, 'user123');
api.sendChat({ message: 'compra', user_id: 'wrong' });
assert.equal(calls.pop()[1].user_id, 'user123');
for (const method of ['getTradeHistory', 'getMonthlySummary', 'getDarfInfo']) {
  api[method](9, 2026);
  const params = calls.pop()[1].params.values;
  assert.equal(params.user_id, 'user123');
  assert.equal(params.month, '9');
  assert.equal(params.year, '2026');
}
const { HistoricoComponent } = load('components/historico/historico.component.ts');
const fake = {
  getMonthlySummary: () => throwError(() => ({ status: 404 })),
  getDarfInfo: () => of({ valor_a_pagar: 0 }),
  getTradeHistory: () => of([{ tipo_operacao: 'compra' }]),
};
const component = new HistoricoComponent(fake);
component.load();
assert.equal(component.trades.length, 1);
assert.equal(component.loaded, true);
assert.equal(component.error, null);
assert.equal(component.darf, null);
fake.getMonthlySummary = () => throwError(() => ({ status: 500 }));
component.load();
assert.ok(component.error);
assert.equal(component.loaded, false);
assert.equal(component.darf, null);
fake.getMonthlySummary = () => of({ ir_total_devido: 10 });
component.load();
assert.equal(component.summary.ir_total_devido, 10);
assert.equal(component.loaded, true);
console.log('PASS: shared identity, purchase-only history, failure state, sale summary.');
