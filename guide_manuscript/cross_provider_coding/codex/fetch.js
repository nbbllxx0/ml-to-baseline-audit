// Download one URL into this session folder.
//
//     node fetch.js <url> tmp/<name>
//
// Uses Node's own TLS, which works inside the Codex sandbox on Windows (curl.exe and Invoke-WebRequest fail there).
// Follows up to 10 redirects, stops after 60 s or 80 MB, refuses shadow libraries, and writes only inside the current
// folder. Prints the HTTP status, the final URL, the content type and the number of bytes saved.
"use strict";
const fs = require("fs");
const path = require("path");
const http = require("http");
const https = require("https");

const BLOCKED = /(sci-hub|scihub|libgen|library\.lol|annas-archive|z-lib|zlibrary|1lib|booksc|b-ok\.)/i;
const MAX_BYTES = 80 * 1024 * 1024;
const UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36";

const [url, out] = process.argv.slice(2);
if (!url || !out) {
  console.error("usage: node fetch.js <url> tmp/<name>");
  process.exit(2);
}
const target = path.resolve(out);
if (!target.startsWith(process.cwd() + path.sep)) {
  console.error("refused: the output file must be inside this folder");
  process.exit(2);
}
fs.mkdirSync(path.dirname(target), { recursive: true });

function get(u, hops) {
  if (BLOCKED.test(u)) {
    console.error(`refused: ${new URL(u).host} is not a legitimate open source (access rules)`);
    process.exit(3);
  }
  const lib = u.startsWith("https:") ? https : http;
  const req = lib.get(u, { headers: { "User-Agent": UA, Accept: "*/*" }, timeout: 60000 }, (res) => {
    if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
      res.resume();
      if (hops >= 10) {
        console.error("stopped: more than 10 redirects");
        process.exit(4);
      }
      get(new URL(res.headers.location, u).toString(), hops + 1);
      return;
    }
    const file = fs.createWriteStream(target);
    let bytes = 0;
    res.on("data", (chunk) => {
      bytes += chunk.length;
      if (bytes > MAX_BYTES) {
        req.destroy();
        file.close();
        console.error(`stopped: larger than ${MAX_BYTES} bytes`);
        process.exit(5);
      }
    });
    res.pipe(file);
    file.on("finish", () => {
      console.log(`status ${res.statusCode} | ${u} | ${res.headers["content-type"] || "?"} | ${bytes} bytes -> ${out}`);
      process.exit(res.statusCode >= 400 ? 1 : 0);
    });
  });
  req.on("timeout", () => req.destroy(new Error("timeout after 60 s")));
  req.on("error", (e) => {
    console.error(`error: ${e.message}`);
    process.exit(1);
  });
}

get(url, 0);
