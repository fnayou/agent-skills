# Brand track

Apply this reference when the request is about a repository's palette, accent,
logo, banners, favicon, social preview, or generated brand assets. It works for
a new project and for auditing or aligning an existing one, and it does not
require any documentation work.

## Shared foundation

Use Catppuccin Macchiato as the base palette. Each project keeps its own
accent, chosen from the palette's accent colors or already present in the
repository. Projects look related through the shared base and differ through
the accent.

Macchiato values:

| Role | Hex | Role | Hex |
|---|---|---|---|
| base | `#24273a` | rosewater | `#f4dbd6` |
| mantle | `#1e2030` | flamingo | `#f0c6c6` |
| crust | `#181926` | pink | `#f5bde6` |
| surface0 | `#363a4f` | mauve | `#c6a0f6` |
| surface1 | `#494d64` | red | `#ed8796` |
| surface2 | `#5b6078` | maroon | `#ee99a0` |
| overlay0 | `#6e738d` | peach | `#f5a97f` |
| overlay1 | `#8087a2` | yellow | `#eed49f` |
| overlay2 | `#939ab7` | green | `#a6da95` |
| subtext0 | `#a5adcb` | teal | `#8bd5ca` |
| subtext1 | `#b8c0e0` | sky | `#91d7e3` |
| text | `#cad3f5` | sapphire | `#7dc4e4` |
| | | blue | `#8aadf4` |
| | | lavender | `#b7bdf8` |

Pick the accent once per repository and record it in the repository's brand
data, not in this skill.

## Decide

Resolve these from the repository first. Ask only about gaps or conflicts.

1. **Accent:** an existing accent color wins. Otherwise propose one and say
   why; the operator decides.
2. **Mark:** what the logo shows. An existing logo wins.
3. **Tagline and claims:** taken from the README or product facts. Never
   invented.
4. **Required assets:** logo, README banner, favicon, social preview. Add
   others only on request.

## Structure

Keep brand material in the repository, in this layout:

```text
brand/
├── data/
│   ├── brand.json      # palette and accent, as hex values
│   └── facts.json      # tagline and the verified facts artwork may state
├── src/                # canonical SVG templates, hand-edited
└── generated/          # SVG output and any raster derivatives, committed
```

- **`src/`** holds SVG templates. A template references data with
  `{{TOKEN}}` placeholders, for example `{{ACCENT}}` or `{{TAGLINE}}`.
- **`data/`** holds the only values artwork may take from the project.
- **`generated/`** is output. Do not edit it by hand.

Commit all three. Reviewers see the template change and the output change
together.

## Rules for artwork

- SVG is canonical. Produce a raster derivative only where a platform requires
  one, for example a social preview PNG at the size the platform states.
- Draw handwritten or distinctive lettering as vector paths. Do not depend on
  a font that the viewer's machine may lack.
- Use palette tokens, never loose hex values, in templates. This keeps an
  accent change to one data edit.
- Keep text contrast readable on its background in both the light and dark
  surfaces the asset appears on.
- Give each SVG a `<title>` so it has an accessible name, and set a `viewBox`.
- Do not embed remote resources, scripts, or external references.
- Ground every feature statement in `facts.json`, and ground each fact in the
  repository: a setting, a constant, a test, or documentation.
- Draw architecture and workflow diagrams from machine-readable repository
  data where practical, so they cannot drift from the implementation.

## Publish the social preview

The generated `social-preview.png` is a file in the repository. No platform
shows it until someone publishes it.

- **GitHub repository preview:** GitHub has no API for it. Ask the operator to
  upload the PNG under Settings → General → Social preview. Report it as a
  step for them; do not attempt it yourself.
- **Site link cards:** a documentation site needs Open Graph tags pointing to
  the same image. Those belong to the documentation track; skip them when the
  project has no site.
- A platform caches the old preview, so a change can take time to appear.

## Generate and check

Provide two tasks, named for the project's task runner:

- `brand:generate` renders `src/` and `data/` into `generated/`.
- `brand:check` fails when a committed output is stale or missing, when a
  placeholder is unresolved, or when a rasterized file is malformed.

Run `brand:check` in CI on the paths that affect it, and on the default
branch. A check that only passes after generation proves the output is
committed, which is the point.

The [starter generator](../scripts/brand_generate.py) implements this with the
Python standard library. Its `--check` re-renders every template, compares the
result with the committed file byte for byte, and validates any raster
derivative's signature and size without comparing bytes, because rasterizers
differ between versions. Rasters need `rsvg-convert`; a project that needs none
installs nothing.

## Starter files

Copy what the project lacks and adapt it. Replace every `example` value.

- [`assets/brand/data/brand.json`](../assets/brand/data/brand.json): palette
  and accent.
- [`assets/brand/data/facts.json`](../assets/brand/data/facts.json): tagline
  and facts.
- [`assets/brand/src/logo.svg`](../assets/brand/src/logo.svg): mark and
  wordmark template.
- [`assets/brand/src/readme-banner.svg`](../assets/brand/src/readme-banner.svg):
  banner template.
- [`assets/tasks/brand-tasks.yml`](../assets/tasks/brand-tasks.yml): task
  definitions.
- [`assets/workflows/brand.yml`](../assets/workflows/brand.yml): CI check.

The starter artwork is a neutral placeholder. It is not a logo. Replace it
with the project's own mark.

## Bootstrap a new project

1. Inspect, then ask the one message of open questions.
2. Create `brand/data/brand.json` and `brand/data/facts.json`.
3. Copy the generator to the project's scripts directory and the starter
   templates to `brand/src/`; replace the placeholder mark.
4. Add the two tasks and the CI workflow.
5. Run `brand:generate`, then `brand:check`. Report both results.
6. Reference the generated banner from the README with alternative text.

## Align an existing project

1. Inspect and list what exists, what is missing, and what conflicts.
2. Keep every sound decision. Move existing assets into the structure only
   when the operator agrees, and keep the originals until the generated copies
   match.
3. Fill gaps first (a missing favicon, an unchecked asset), then address
   conflicts the operator resolves.
4. Add `brand:check` before changing any artwork, so the first change is
   already covered.

## Check the result

Before reporting completion, confirm each item by running or reading it:

- `brand:check` passes, and fails after you edit a generated file by hand.
- No template contains a loose hex value or a remote reference.
- Every statement in the artwork traces to `facts.json`.
- The README alt text describes the image.
- No path in a committed file is machine-specific.
