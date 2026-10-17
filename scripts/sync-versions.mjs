// ponytail: replica la versión del package.json raíz a apps/ y packages/ (una sola fuente de verdad).
import { readFileSync, writeFileSync } from "node:fs";

const version = JSON.parse(
	readFileSync(new URL("../package.json", import.meta.url), "utf8"),
).version;

function bumpJson(url, extra) {
	const raw = readFileSync(url, "utf8");
	const indent = raw.match(/^( +|\t+)/m)?.[1] ?? "\t";
	const json = JSON.parse(raw);
	json.version = version;
	extra?.(json);
	writeFileSync(url, `${JSON.stringify(json, null, indent)}\n`);
}

bumpJson(new URL("../apps/web/package.json", import.meta.url));
bumpJson(new URL("../apps/web/package-lock.json", import.meta.url), (json) => {
	if (json.packages?.[""]) json.packages[""].version = version;
});

function bumpPy(url) {
	writeFileSync(
		url,
		readFileSync(url, "utf8").replace(
			/^version = ".*"$/m,
			`version = "${version}"`,
		),
	);
}

bumpPy(new URL("../pyproject.toml", import.meta.url));
bumpPy(new URL("../apps/api/pyproject.toml", import.meta.url));
bumpPy(new URL("../packages/analytika/pyproject.toml", import.meta.url));
bumpPy(new URL("../packages/db/pyproject.toml", import.meta.url));

console.log(`synced to ${version}`);
