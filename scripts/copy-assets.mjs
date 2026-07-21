import { copyFileSync, mkdirSync } from "node:fs";

mkdirSync("static/dist", { recursive: true });
copyFileSync("node_modules/htmx.org/dist/htmx.min.js", "static/dist/htmx.min.js");
