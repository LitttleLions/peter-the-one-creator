import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import higgsfieldClient from "@higgsfield/client";

const { HiggsfieldClient } = higgsfieldClient;
const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function loadDotenv() {
  const envPath = path.join(repoRoot, ".env");
  if (!fs.existsSync(envPath)) {
    return;
  }
  const text = fs.readFileSync(envPath, "utf8");
  for (const rawLine of text.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#") || !line.includes("=")) {
      continue;
    }
    const idx = line.indexOf("=");
    const key = line.slice(0, idx).trim();
    let value = line.slice(idx + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    if (!process.env[key]) {
      process.env[key] = value;
    }
  }
}

function output(payload, exitCode = 0) {
  process.stdout.write(JSON.stringify(payload, null, 2) + "\n");
  process.exitCode = exitCode;
}

function credentialsFromEnv() {
  const credentials = process.env.HF_CREDENTIALS;
  if (credentials) {
    const parts = credentials.split(":");
    if (parts.length !== 2 || !parts[0] || !parts[1]) {
      throw Object.assign(new Error("HF_CREDENTIALS muss KEY_ID:KEY_SECRET sein"), {
        code: "HIGGSFIELD_API_CREDENTIALS_INVALID",
      });
    }
    return { apiKey: parts[0], apiSecret: parts[1] };
  }
  const apiKey = process.env.HF_API_KEY;
  const apiSecret = process.env.HF_API_SECRET;
  if (apiKey && apiSecret) {
    return { apiKey, apiSecret };
  }
  throw Object.assign(
    new Error("Higgsfield-Credentials fehlen: HF_CREDENTIALS oder HF_API_KEY + HF_API_SECRET setzen"),
    { code: "HIGGSFIELD_API_CREDENTIALS_MISSING" },
  );
}

function readKnownMoodboards() {
  const booksDir = path.join(repoRoot, "books");
  const entries = [];
  if (!fs.existsSync(booksDir)) {
    return entries;
  }
  for (const bookId of fs.readdirSync(booksDir)) {
    const bookYaml = path.join(booksDir, bookId, "book.yaml");
    if (!fs.existsSync(bookYaml)) {
      continue;
    }
    const text = fs.readFileSync(bookYaml, "utf8");
    const styleMatch =
      text.match(/^\s{4}web_ui_moodboard_id:\s*"?([^"\r\n]+)"?\s*$/m) ??
      text.match(/^\s{4}style_id:\s*"?([^"\r\n]+)"?\s*$/m);
    if (!styleMatch) {
      continue;
    }
    const nameMatch = text.match(/^\s{4}name:\s*"?([^"\r\n]+)"?\s*$/m);
    entries.push({
      book_id: bookId,
      style_id: styleMatch[1].trim(),
      expected_name: nameMatch ? nameMatch[1].trim() : null,
    });
  }
  return entries;
}

try {
  loadDotenv();
  const known = readKnownMoodboards();
  const client = new HiggsfieldClient(credentialsFromEnv());
  const styles = await client.getSoulStyles();
  client.close?.();
  const byId = new Map(styles.map((style) => [style.id, style]));
  output({
    ok: true,
    no_generation: true,
    results: known.map((entry) => {
      const found = byId.get(entry.style_id);
      return {
        style_id: entry.style_id,
        expected_name: entry.expected_name,
        found: Boolean(found),
        api_name: found?.name ?? null,
        match: Boolean(found && (!entry.expected_name || found.name === entry.expected_name)),
        book_id: entry.book_id,
      };
    }),
  });
} catch (error) {
  output(
    {
      ok: false,
      error_code: error.code || "HIGGSFIELD_API_ERROR",
      message: error.message || String(error),
      details: {},
    },
    1,
  );
}
