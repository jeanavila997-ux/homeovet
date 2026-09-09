// server.js — servidor estático mínimo para hospedagem Node (Hostinger).
// Zero dependências: serve o dashboard construído em dist/index.html.
// Uso: npm start (porta definida pelo host via process.env.PORT).
"use strict";
const http = require("http");
const fs = require("fs");
const path = require("path");

const PORTA = process.env.PORT || 3000;
const ARQUIVO = path.join(__dirname, "dist", "index.html");

const servidor = http.createServer((req, res) => {
  fs.readFile(ARQUIVO, (erro, dados) => {
    if (erro) {
      res.writeHead(500, { "Content-Type": "text/plain; charset=utf-8" });
      res.end("Erro ao carregar o dashboard HomeoVet. Rode primeiro: npm run build");
      return;
    }
    res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
    res.end(dados);
  });
});

servidor.listen(PORTA, () => {
  console.log(`HomeoVet (uso educacional) rodando na porta ${PORTA}`);
});