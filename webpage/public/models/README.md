# Shelf hardcover models (`public/models/`)

Local Three.js assets for the Motivatier shelf. Browser code loads only files
from this folder (and `manifest.json`). Never call Mint MCP from the client.

## Status (2026-07-28)

| Item | Status |
|------|--------|
| `mint-threejs-skills` | Installed globally (`~\.agents\skills\mint-threejs-skills`) |
| Mint MCP (`https://mcp.mint.gg/mcp`) | **Not connected** in this Cursor session |
| GLB Asset Pack | **Blocked** — no MCP tools available; no fake binaries committed |

Available MCP servers when this was prepared: `cursor-app-control`,
`cursor-ide-browser`, `plugin-huggingface-skills-*`, `plugin-supabase-supabase`,
`plugin-vercel-vercel`, `plugin-zapier-zapier`. Pattern search for `mint` /
`mcp.mint` returned no tools. `mcp_auth` could not be invoked because the Mint
server is absent from the host catalog.

### Unblock

1. In Cursor: **Settings → Cursor Settings → Tools & MCP** → add / Connect
   Mint MCP at `https://mcp.mint.gg/mcp` (or the current Mint MCP URL).
2. Authenticate when prompted (`mcp_auth` on the Mint server).
3. Re-run the asset phase with `mint-threejs-skills` + live Mint tools in
   **auto** mode: coherent clothbound hardcover **Asset Pack** (~12–16 items,
   varied proportions, warm editorial cream / walnut shelf look).
4. Sync artifacts via `sync-mint-assets.mjs` (skill script) into this folder,
   then update `manifest.json` with real local paths.

Until then the shelf app should keep using fallback box meshes + cover textures.

## Expected layout after Mint import

```text
webpage/public/models/
  README.md                 # this file
  manifest.json             # loader-facing index (committed)
  mint-pack-manifest.json   # optional raw Mint artifact manifest (agent-only, can be gitignored)
  hardcover-01/
    optimized_glb.glb       # canonical Draco-optimized model
    preview_image.webp      # optional
  hardcover-02/
    ...
  hardcover-NN/
    ...
```

Canonical GLBs typically use `KHR_draco_mesh_compression`. Use a shared
Draco-capable `GLTFLoader` (see mint-threejs-skills
`gltf-runtime-compatibility.md`). Do not load Mint-optimized GLBs with a bare
`GLTFLoader`.

Optional project-root registry after sync:

- `mint-assets.json` — durable registry from `sync-mint-assets.mjs`
- Prefer `assetRoot` pointing at `webpage/public/models` (or mirror paths into
  this folder and keep `manifest.json` as the browser index)

## `manifest.json` contract

```json
{
  "version": 1,
  "packId": "clothbound-hardcovers",
  "status": "pending_mint",
  "description": "Cohesive clothbound hardcover variants for the shelf",
  "look": {
    "style": "clothbound hardcover",
    "palette": "warm editorial cream / walnut",
    "countTarget": [12, 16]
  },
  "models": [
    {
      "id": "hardcover-01",
      "url": "/models/hardcover-01/optimized_glb.glb",
      "role": "canonical_model",
      "loaderHint": "gltf",
      "requiresDraco": true,
      "proportions": { "width": 0.9, "height": 1.0, "depth": 1.0 },
      "notes": "slightly narrow spine"
    }
  ]
}
```

Rules:

- `models[].url` is a **browser** path under Vite `public/` (`/models/...`).
- Only list entries whose `.glb` files actually exist on disk.
- While `status` is `pending_mint`, `models` stays `[]` and the app uses boxes.
- After import, set `status` to `ready` and fill `models` in stable pack order.
- Do not invent placeholder GLB binaries.

## Target pack brief (for the next Mint generation)

- **Kind:** model asset pack (not a world)
- **Subject:** clothbound hardcover books standing upright, closed
- **Count:** ~12–16 cohesive variants
- **Variation:** height, thickness (spine width), slight depth differences;
  cloth colors in a warm editorial range that reads next to cream UI and walnut
  wood (muted burgundy, forest, ochre, navy, sand — avoid neon / plastic)
- **UVs:** front cover + spine usable for catalog cover textures
- **Mode:** automatic Mint generation; import via artifact manifest tools only
