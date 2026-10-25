# Documentation track

Apply this reference when the request is about a repository's public
documentation site. It works for a new site and for auditing or aligning an
existing one, and it does not require any brand work. When the project has
brand assets, reuse them as described under
[Reuse the brand](#reuse-the-brand); when it has none, do not create any.

## Layout

- `website/` holds public content: pages a visitor reads.
- `docs/` holds internal engineering material: decisions, runbooks, audits.
  It is not published.
- `zensical.toml` at the repository root configures the site, with
  `docs_dir = "website"`.

Never publish `docs/` by accident. A page belongs in `website/` only when a
visitor needs it.

## Tool

Use [Zensical](https://zensical.org/) with its native `zensical.toml`
configuration for a new or aligned site. An existing site on another generator
stays as it is unless the operator asks to migrate it.

- Pin the exact release in `requirements-docs.txt` (`zensical==<version>`),
  using the version you installed and built with. Never leave it unpinned.
- Validate every configuration key and feature against that release by
  building with `zensical build --strict`. Do not assume a Material for
  MkDocs plugin or option works; remove what the build rejects instead of
  guessing a substitute.
- Read the project's current Zensical documentation for any key you are unsure
  of.

## Decide

Resolve from the repository first. Ask once, only about gaps or conflicts.

1. **Existing site:** generator, content directory, navigation, and deployment.
   Keep what is sound.
2. **Palette and accent:** from the brand data or the existing stylesheet. The
   base is Catppuccin Macchiato; the accent is the project's own. If there is
   none, ask the operator.
3. **Pages:** start with Home and Getting Started. Add a page only when the
   repository has the facts to fill it.
4. **Deployment:** GitHub Pages through GitHub Actions, unless the project
   already deploys elsewhere.

## Content rules

- Every statement is supported by the repository: a command that runs, a
  setting that exists, a test, or documentation. Cite no number, speed, or
  compatibility you did not verify.
- Separate implemented from planned. List only released behavior as a
  capability. Put planned work in a clearly labeled place, such as a
  `!!! note "Planned"` admonition or a page titled Roadmap, and never imply it
  is available.
- Show a command together with what the reader should see.
- Use plain headings, short paragraphs, and descriptive link text. Do not
  write "click here".
- Give every image alternative text that says what it shows. A decorative
  image gets an empty `alt=""`.

## Style

The starter [`macchiato.css`](../assets/docs/website/stylesheets/macchiato.css)
defines the Macchiato theme. Change only the `--project-accent` value to match
the project; every other accent reference reads from it.

- Dark first. The Macchiato scheme is the default; add a light scheme only if
  the operator asks for one.
- Text and the accent must keep a contrast ratio of at least 4.5:1 against the
  background. Check it rather than judging by eye: the starter checker does
  this from the brand palette.
- Keep a visible focus outline on links and buttons.
- Respect `prefers-reduced-motion`.
- Images use `max-width: 100%`. Content must not scroll horizontally at a
  narrow viewport, around 360 px wide. Check wide tables and code blocks.
- Do not set the accent to a color the palette lacks, and do not hard-code a
  second brand color in a page.

## Reuse the brand

Reference generated assets from the brand track by path; do not copy them
into a second place that can drift.

- Point `extra_css` or the theme logo and favicon at files copied from
  `brand/generated/` by the docs build, or place the build step before
  `zensical build`. Keep one source of truth.
- Embed a diagram as an `<img>` with alt text that summarizes it. Diagrams are
  drawn from repository data in the brand track, so the page stays accurate.
- With no brand assets, use a text title and skip the logo.

## Build and check

Provide two tasks, named for the project's task runner:

- `docs:build` runs `zensical build --strict`.
- `docs:check` builds, then runs the
  [starter checker](../scripts/check_docs.py) on the built `site/`.

The checker works offline on the generated HTML and reports:

- a missing `lang`, title, `main` landmark, or a count of `h1` other than one;
- an image without an `alt` attribute and a link with no accessible name;
- a broken internal link or a missing anchor;
- with `--base-path`, a root-absolute link outside the Pages path;
- with `--palette`, a text or accent color below 4.5:1 on the base color.

Run `docs:check` in CI on pull requests and before every deployment.

## Deploy to GitHub Pages

Use the [starter workflow](../assets/workflows/docs-pages.yml). It builds and
checks on every pull request, and deploys only from the default branch.

- Deploy with GitHub Actions, the built-in token and the `pages: write` and
  `id-token: write` permissions. Do not use a personal access token or a
  deploy key by default.
- Grant those two permissions only to the deploy job. Keep `contents: read`
  elsewhere.
- Pin every action to a full commit SHA with the version in a comment.
- Set the Pages source to GitHub Actions in repository settings. Changing a
  repository setting needs the operator's approval; report it as a step for
  them and do not make the change yourself.
- A project Pages site lives under `/<repository>/`. Set `site_url`
  accordingly and run the checker with `--base-path /<repository>/`.

## Starter files

Copy what the project lacks and adapt it. Replace every placeholder in angle
brackets and every `example` value.

- [`assets/docs/zensical.toml`](../assets/docs/zensical.toml): site
  configuration.
- [`assets/docs/website/index.md`](../assets/docs/website/index.md) and
  [`getting-started.md`](../assets/docs/website/getting-started.md): page
  skeletons with the implemented and planned convention.
- [`assets/docs/website/stylesheets/macchiato.css`](../assets/docs/website/stylesheets/macchiato.css):
  theme.
- [`assets/tasks/docs-tasks.yml`](../assets/tasks/docs-tasks.yml): task
  definitions.
- [`assets/workflows/docs-pages.yml`](../assets/workflows/docs-pages.yml):
  build, check, and deploy.

## Bootstrap a new site

1. Inspect, then ask the one message of open questions.
2. Copy the configuration, pages, and stylesheet; set `site_name`, `site_url`,
   and the accent.
3. Pin Zensical in `requirements-docs.txt` after installing and building with
   it.
4. Write pages from repository facts only.
5. Copy the checker, the tasks, and the workflow.
6. Run `docs:check` and report the result. Report the Pages setting for the
   operator to enable.

## Align an existing site

1. Inspect and list what exists, what is missing, and what conflicts.
2. Keep the current generator, navigation, and sound content.
3. Add `docs:check` first, so every later change is already covered. Fix what
   it reports in order of reader impact: broken links, then missing alt text
   and landmarks, then contrast.
4. Replace unsupported or unverified claims. Label planned work as planned.
5. Move to Zensical, or to `website/`, only on the operator's request.

## Check the result

Confirm each item by running or reading it:

- `docs:check` passes, and fails after you break a link on purpose.
- No page states a capability the repository does not implement; planned work
  is labeled.
- The workflow deploys only from the default branch and uses no personal token.
- The site reads at a narrow viewport without horizontal page scroll.
- No committed file contains a machine-specific path.
