import { readFileSync } from 'node:fs';
import { JSDOM } from 'jsdom';

const dom = new JSDOM('<!doctype html><html><body></body></html>', { pretendToBeVisual: true });
globalThis.window = dom.window;
globalThis.document = dom.window.document;
Object.defineProperty(globalThis, 'navigator', {
  value: dom.window.navigator,
  configurable: true,
});
globalThis.DOMPurify = undefined;
globalThis.SVGElement = dom.window.SVGElement;
globalThis.Element = dom.window.Element;
globalThis.Node = dom.window.Node;
globalThis.HTMLElement = dom.window.HTMLElement;
globalThis.MutationObserver = dom.window.MutationObserver;
globalThis.getComputedStyle = dom.window.getComputedStyle;
globalThis.requestAnimationFrame = (cb) => setTimeout(cb, 0);

const { default: mermaid } = await import('mermaid');
mermaid.initialize({ startOnLoad: false, securityLevel: 'loose' });

const ruta = process.argv[2];
const texto = readFileSync(ruta, 'utf8').split('\r\n').join('\n');
const bloques = [...texto.matchAll(/```mermaid\n([\s\S]*?)\n```/g)].map((m) => m[1]);

console.log(`Diagramas encontrados: ${bloques.length}\n`);
let fallos = 0;
for (const [indice, codigo] of bloques.entries()) {
  const primera = codigo.split('\n')[0].trim();
  try {
    await mermaid.parse(codigo);
    console.log(`  OK   #${indice + 1}  ${primera}`);
  } catch (error) {
    fallos += 1;
    console.log(`  FAIL #${indice + 1}  ${primera}`);
    console.log(`       ${String(error.message ?? error).split('\n').slice(0, 6).join('\n       ')}`);
  }
}
console.log(`\n${bloques.length - fallos}/${bloques.length} diagramas válidos`);
process.exit(fallos === 0 ? 0 : 1);
