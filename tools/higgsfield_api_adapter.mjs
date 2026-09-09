import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import higgsfieldClient from "@higgsfield/client";

const { HiggsfieldClient } = higgsfieldClient;
const SOUL_ENDPOINT = "/v1/text2image/soul";
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

function sizeForAspectRatio(aspectRatio) {
  const value = String(aspectRatio ?? "3:4").trim();
  const mapping = {
    "1:1": "1536x1536",
    "3:4": "1536x2048",
    "4:3": "2048x1536",
    "9:16": "1152x2048",
    "16:9": "2048x1152",
  };
  return mapping[value] ?? value;
}

function qualityForSoul(value) {
  const normalized = String(value ?? "hd").trim().toLowerCase();
  if (["hd", "1080p", "1.5k", "2k"].includes(normalized)) {
    return "1080p";
  }
  if (["sd", "720p"].includes(normalized)) {
    return "720p";
  }
  return value;
}

function ok(payload) {
  process.stdout.write(JSON.stringify({ ok: true, ...payload }, null, 2) + "\n");
}

function fail(errorCode, message, details = {}) {
  process.stdout.write(
    JSON.stringify(
      {
        ok: false,
        error_code: errorCode,
        message,
        details,
      },
      null,
      2,
    ) + "\n",
  );
  process.exitCode = 1;
}

async function readStdinJson() {
  const chunks = [];
  for await (const chunk of process.stdin) {
    chunks.push(chunk);
  }
  const text = Buffer.concat(chunks).toString("utf8").trim();
  if (!text) {
    throw Object.assign(new Error("stdin enthaelt kein JSON"), {
      code: "HIGGSFIELD_API_BAD_INPUT",
    });
  }
  try {
    return JSON.parse(text);
  } catch (error) {
    throw Object.assign(new Error(`stdin enthaelt kein gueltiges JSON: ${error.message}`), {
      code: "HIGGSFIELD_API_BAD_INPUT",
    });
  }
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

function clientFromEnv() {
  const credentials = credentialsFromEnv();
  return new HiggsfieldClient(credentials);
}

function cleanStyle(style) {
  return {
    id: style?.id ?? null,
    name: style?.name ?? null,
    description: style?.description ?? null,
    preview_url: style?.preview_url ?? null,
  };
}

function assertNumber(value, field) {
  if (typeof value !== "number" || Number.isNaN(value)) {
    throw Object.assign(new Error(`${field} muss eine Zahl sein`), {
      code: "HIGGSFIELD_API_BAD_INPUT",
    });
  }
}

function buildGeneratePayload(input) {
  if (!input.prompt || typeof input.prompt !== "string") {
    throw Object.assign(new Error("prompt ist erforderlich"), {
      code: "HIGGSFIELD_API_BAD_INPUT",
    });
  }

  const payload = {
    prompt: input.prompt,
    width_and_height: sizeForAspectRatio(input.aspect_ratio),
    quality: qualityForSoul(input.quality),
    batch_size: input.batch_size ?? 1,
  };

  if (input.style_id) {
    if (input.style_strength === undefined || input.style_strength === null) {
      throw Object.assign(new Error("style_strength ist erforderlich, wenn style_id gesetzt ist"), {
        code: "HIGGSFIELD_API_BAD_INPUT",
      });
    }
    assertNumber(input.style_strength, "style_strength");
    payload.style_id = input.style_id;
    payload.style_strength = input.style_strength;
  }

  if (input.soul_id) {
    if (input.soul_strength === undefined || input.soul_strength === null) {
      throw Object.assign(new Error("soul_strength ist erforderlich, wenn soul_id gesetzt ist"), {
        code: "HIGGSFIELD_API_BAD_INPUT",
      });
    }
    assertNumber(input.soul_strength, "soul_strength");
    payload.custom_reference_id = input.soul_id;
    payload.custom_reference_strength = input.soul_strength;
  }

  return payload;
}

function firstImageUrl(jobSet) {
  for (const job of jobSet?.jobs ?? []) {
    const rawUrl = job?.results?.raw?.url;
    if (rawUrl) {
      return rawUrl;
    }
    const minUrl = job?.results?.min?.url;
    if (minUrl) {
      return minUrl;
    }
  }
  return null;
}

async function listStyles() {
  const client = clientFromEnv();
  try {
    const styles = await client.getSoulStyles();
    ok({ styles: styles.map(cleanStyle) });
  } finally {
    client.close?.();
  }
}

async function generate(input) {
  const requestPayload = buildGeneratePayload(input);
  if (input.dry_run) {
    ok({
      endpoint: SOUL_ENDPOINT,
      request_payload: requestPayload,
      dry_run: true,
    });
    return;
  }

  const client = clientFromEnv();
  try {
    const jobSet = await client.generate(SOUL_ENDPOINT, requestPayload, {
      withPolling: true,
    });
    ok({
      request_id: jobSet?.id ?? null,
      status: jobSet?.jobs?.[0]?.status ?? null,
      job_id: jobSet?.jobs?.[0]?.id ?? null,
      image_url: firstImageUrl(jobSet),
      raw_response: jobSet,
    });
  } finally {
    client.close?.();
  }
}

try {
  loadDotenv();
  const input = await readStdinJson();
  if (input.action === "list_styles") {
    await listStyles();
  } else if (input.action === "generate") {
    await generate(input);
  } else {
    fail("HIGGSFIELD_API_BAD_INPUT", "Unbekannte action", {
      action: input.action ?? null,
    });
  }
} catch (error) {
  fail(error.code || "HIGGSFIELD_API_ERROR", error.message || String(error), {});
}
