// build_web.js — build do dashboard HomeoVet sem dependências.
// Copia o index.html standalone (base embutida) para dist/.
// Uso: npm run build
"use strict";
const fs = require("fs");
const path = require("path");

const raiz = path.join(__dirname, "..");
const dist = path.join(raiz, "dist");

fs.rmSync(dist, { recursive: true, force: true });
fs.mkdirSync(dist, { recursive: true });
fs.copyFileSync(path.join(raiz, "index.html"), path.join(dist, "index.html"));

console.log("dist/index.html gerado (dashboard standalone, base embutida).");