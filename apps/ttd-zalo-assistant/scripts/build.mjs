import { build } from "esbuild";
import { copyFile } from "node:fs/promises";
await build({ entryPoints: ["src/renderer.tsx"], bundle: true, minify: true, outfile: "dist/ui.js",
  define: { "process.env.NODE_ENV": '"production"' },
  legalComments: "linked" });
for (const file of ["index.html", "style.css", "preload.cjs"]) await copyFile("src/" + file, "dist/" + file);
