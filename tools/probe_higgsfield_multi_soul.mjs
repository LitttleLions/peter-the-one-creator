import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import higgsfieldClient from "@higgsfield/client";

const { HiggsfieldClient } = higgsfieldClient;
const SOUL_ENDPOINT = "/v1/text2image/soul";
const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

const DEFAULTS = {
  book: "aelita",
  styleId: "6fdd3fde-4c0d-4b21-a7fa-cf0f4aa1a7ba",
  styleStrength: 0.8,
  fairyId: "0fb45e81-0939-41e4-bee4-f0d007a8ec43",
  whispersId: "27e7e3ca-aa27-48f0-8a82-e59541dcfd20",
  widthAndHeight: "1152x1536",
  quality: "720p",
};

const DEFAULT_PROMPT = [
  "Post-revolutionary Soviet Union 1920s and ancient Mars civilisation.",
  "Two clearly separated characters in one cinematic vertical illustration:",
  "Aelita, a blue-skinned Martian princess with delicate birdlike facial features,",
  "standing on the left in pale ceremonial clothing;",
  "Los, a lean Soviet engineer in a practical cap and dark work coat,",
  "standing on the right beside a metal airship console.",
  "Red desert, canals, vertical Martian architecture, atmospheric depth.",
].join(" ");

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

function credentialsFromEnv() {
  const credentials = process.env.HF_CREDENTIALS;
  if (credentials) {
    const parts = credentials.split(":");
    if (parts.length !== 2 || !parts[0] || !parts[1]) {
      throw new Error("HF_CREDENTIALS must be KEY_ID:KEY_SECRET");
    }
    return { apiKey: parts[0], apiSecret: parts[1] };
  }
  const apiKey = process.env.HF_API_KEY;
  const apiSecret = process.env.HF_API_SECRET;
  if (apiKey && apiSecret) {
    return { apiKey, apiSecret };
  }
  throw new Error("Missing Higgsfield credentials: set HF_CREDENTIALS or HF_API_KEY + HF_API_SECRET");
}

function parseArgs(argv) {
  const args = {
    dryRun: true,
    allowPaidGeneration: false,
    outputDir: path.join(
      repoRoot,
      "books",
      DEFAULTS.book,
      "work",
      "prompts",
      "higgsfield",
      "soul-tests",
    ),
    variants: ["single_fairy", "single_whispers", "array_two", "object_named"],
    prompt: DEFAULT_PROMPT,
  };
  for (let i = 0; i < argv.length; i += 1) {
    const item = argv[i];
    if (item === "--allow-paid-generation") {
      args.allowPaidGeneration = true;
      args.dryRun = false;
    } else if (item === "--dry-run") {
      args.dryRun = true;
    } else if (item === "--output-dir") {
      args.outputDir = path.resolve(argv[++i]);
    } else if (item === "--variant") {
      args.variants = [argv[++i]];
    } else if (item === "--variants") {
      args.variants = argv[++i].split(",").map((value) => value.trim()).filter(Boolean);
    } else if (item === "--prompt") {
      args.prompt = argv[++i];
    } else if (item === "--help" || item === "-h") {
      args.help = true;
    } else {
      throw new Error(`Unknown argument: ${item}`);
    }
  }
  return args;
}

function printHelp() {
  console.log(`Usage:
  node tools/probe_higgsfield_multi_soul.mjs [--dry-run]
  node tools/probe_higgsfield_multi_soul.mjs --allow-paid-generation --variant single_fairy
  node tools/probe_higgsfield_multi_soul.mjs --allow-paid-generation --variants array_two,object_named

Writes JSON payloads/results to:
  books/aelita/work/prompts/higgsfield/soul-tests/

Variants:
  single_fairy     custom_reference_id = Fairy I
  single_whispers  custom_reference_id = Whispers of Aether
  array_two        custom_reference_id = [Fairy I, Whispers of Aether]
  object_named     custom_reference_id = { Aelita: Fairy I, Los: Whispers of Aether }
`);
}

function basePayload(prompt) {
  return {
    prompt,
    width_and_height: DEFAULTS.widthAndHeight,
    quality: DEFAULTS.quality,
    batch_size: 1,
    style_id: DEFAULTS.styleId,
    style_strength: DEFAULTS.styleStrength,
  };
}

function payloadForVariant(variant, prompt) {
  const payload = basePayload(prompt);
  if (variant === "single_fairy") {
    payload.custom_reference_id = DEFAULTS.fairyId;
    payload.custom_reference_strength = 1.0;
  } else if (variant === "single_whispers") {
    payload.custom_reference_id = DEFAULTS.whispersId;
    payload.custom_reference_strength = 1.0;
  } else if (variant === "array_two") {
    payload.custom_reference_id = [DEFAULTS.fairyId, DEFAULTS.whispersId];
    payload.custom_reference_strength = 1.0;
  } else if (variant === "object_named") {
    payload.custom_reference_id = {
      Aelita: DEFAULTS.fairyId,
      Los: DEFAULTS.whispersId,
    };
    payload.custom_reference_strength = 1.0;
  } else {
    throw new Error(`Unknown variant: ${variant}`);
  }
  return payload;
}

function timestamp() {
  return new Date().toISOString().replace(/[-:]/g, "").replace(/\..+$/, "Z");
}

function writeJson(filePath, data) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + "\n", "utf8");
}

async function generate(payload) {
  const client = new HiggsfieldClient(credentialsFromEnv());
  try {
    const jobSet = await client.generate(SOUL_ENDPOINT, payload, {
      withPolling: true,
    });
    return {
      request_id: jobSet?.id ?? null,
      status: jobSet?.jobs?.[0]?.status ?? null,
      job_id: jobSet?.jobs?.[0]?.id ?? null,
      raw_response: jobSet,
    };
  } finally {
    client.close?.();
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    printHelp();
    return;
  }
  loadDotenv();
  const runId = timestamp();
  const summary = {
    run_id: runId,
    endpoint: SOUL_ENDPOINT,
    dry_run: args.dryRun,
    variants: [],
  };
  for (const variant of args.variants) {
    const payload = payloadForVariant(variant, args.prompt);
    const record = {
      variant,
      endpoint: SOUL_ENDPOINT,
      dry_run: args.dryRun,
      payload,
      result: null,
      error: null,
    };
    if (!args.dryRun) {
      if (!args.allowPaidGeneration) {
        throw new Error("Paid generation requires --allow-paid-generation");
      }
      try {
        record.result = await generate(payload);
      } catch (error) {
        record.error = {
          message: error?.message ?? String(error),
          stack: error?.stack ?? null,
        };
      }
    }
    const filePath = path.join(args.outputDir, `${runId}-${variant}.json`);
    writeJson(filePath, record);
    summary.variants.push({
      variant,
      file: filePath,
      ok: !record.error,
      job_id: record.result?.job_id ?? null,
      error: record.error?.message ?? null,
    });
    console.log(`${variant}: ${filePath}`);
    if (record.error) {
      console.log(`  ERROR: ${record.error.message}`);
    }
  }
  const summaryPath = path.join(args.outputDir, `${runId}-summary.json`);
  writeJson(summaryPath, summary);
  console.log(`summary: ${summaryPath}`);
}

main().catch((error) => {
  console.error(error?.message ?? String(error));
  process.exitCode = 1;
});
