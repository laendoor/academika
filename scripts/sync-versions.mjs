// ponytail: replica la versión del package.json raíz a web/ y api/ (una sola fuente de verdad).
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

bumpJson(new URL("../web/package.json", import.meta.url));
bumpJson(new URL("../web/package-lock.json", import.meta.url), (json) => {
	if (json.packages?.[""]) json.packages[""].version = version;
});

const pyUrl = new URL("../api/pyproject.toml", import.meta.url);
writeFileSync(
	pyUrl,
	readFileSync(pyUrl, "utf8").replace(
		/^version = ".*"$/m,
		`version = "${version}"`,
	),
);

console.log(`synced to ${version}`);
