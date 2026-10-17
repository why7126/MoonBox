import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const distRoot = new URL("../dist/", import.meta.url);
const assetsRoot = new URL("assets/", distRoot);
const forbidden = ["待应用成果", "查看成果", "审阅治理成果", "确认应用"];
const files = [
  new URL("index.html", distRoot),
  ...readdirSync(assetsRoot).filter((name) => name.endsWith(".js") || name.endsWith(".css")).map((name) => new URL(join("assets", name), distRoot)),
];

if (files.length <= 1) throw new Error("dist assets are missing");

const hits = [];
for (const file of files) {
  const content = readFileSync(file, "utf8");
  for (const value of forbidden) {
    if (content.includes(value)) hits.push(`${file.pathname}:${value}`);
  }
}

if (hits.length) {
  throw new Error(`runtime bundle exposes governance panel text: ${hits.join(", ")}`);
}

console.log(JSON.stringify({ files: files.length, forbidden_hits: 0 }));
