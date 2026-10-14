# Mightora Semantic Model Mapper

A local-first, GitHub Pages–ready, MIT-licensed tool for exploring Power BI and Microsoft Fabric semantic models and their report visuals.

## Features

- Interactive drag-and-zoom relationship graph of tables, columns, measures and relationship paths.
- Cardinality, active/inactive relationships and single/both cross-filter metadata.
- Inspector for columns, DAX measure definitions and relationship metadata.
- Best-effort direct visual field tracing from Power BI enhanced report (PBIR) `visual.json` files.
- Imports multiple `.tmdl` files, TMSL/tabular JSON, Mapper JSON and report metadata from a selected PBIP folder.
- Two ready-to-explore examples (retail analytics and service desk).
- Export SVG (vector), Mermaid (`.mmd`), Markdown documentation and Mapper JSON.
- One-file standalone offline version, generated from the same source as GitHub Pages.

## Run locally

1. To use the offline edition, download `semantic-model-mapper-offline.zip`, extract and **double-click `index.html`**. It requires no server, installation, internet access or external dependencies.
2. For the online build, use `python3 scripts/build.py` then host `dist/` on any static server, or simply deploy its contents to GitHub Pages. The web edition intentionally loads Mightora shared web components.
3. Edit the source in `index.html`, `src/` and `examples/`, then rebuild. `npm run build` / `npm run test` also work (Python 3 and Node 20+ required for testing/building only).

## Importing a real Power BI Project (PBIP)

In Power BI Desktop, save your model as a **Power BI Project (.pbip)**, using TMDL for the semantic model and PBIR for report metadata. Select **Import a PBIP folder** and pick the project root, or import multiple `.tmdl`/JSON files. The mapper does not open native `.pbix` binaries and cannot access Power BI Service directly.

Model files are processed by your own browser only. No file contents are uploaded, sent to an API or stored in remote telemetry. The offline edition has an explicit CSP disallowing network `connect-src`; using external **links** is a separate user-initiated action.

## Scope and limitations

- The lightweight TMDL parser handles common table, column, measure and relationship declarations and properties; it is **not** a complete official TMDL grammar implementation. Complex TMDL constructs, unusual expressions and unusual cardinality encodings should be independently checked.
- Visual lineage discovers **direct** column and measure references in supported PBIR visual structures; indirect DAX dependencies, calculation groups, field parameters, implicit measures, filter expression dependencies, calculated tables, and proprietary/custom visual internals may not be fully resolved. No claim of comprehensive transitive lineage.
- Large models (hundreds of tables) may become visually crowded. The canvas prioritises model exploration, not automated enterprise-scale graph optimisation.
- Individual files have a 6 MB limit, with 500 importable files maximum.
- Exported SVG contains vector text and shapes. Mermaid describes model cardinalities and stores cross-filter details in the edge labels.
- The app does **not** execute DAX or connect to databases.
- The local development build embeds a branded text fallback if the official Mightora PNG is not available. The CI build downloads and embeds the official image; release checks assert it is present. This is a documented branding exception for builds made entirely without network access.

## Trust, online network and offline verification

Online mode loads official Mightora shared CSS and web components through jsDelivr, `js-yaml` through jsDelivr, and logos/author imagery from public GitHub hosts. A footer component may retrieve a public YAML feed. The model mapper itself does not transmit imported data.

Offline mode embeds script, styles, sample models and its logo and favicon, blocks application network connections, and has no CDN, analytics or telemetry. To verify locally, press **F12 → Network → Preserve log → reload**. Note that browser Resource Timing API display is not a complete list of network activity, and a CSP is not an independent audit.

## Security and quality

GitHub Actions runs Node parsing tests, release/offline artifact validation, npm audit and deployment from `dist/`. CodeQL scans JavaScript. The workflows and README are public evidence once a repository is published and CI runs. Do not claim badges indicate a certified or audited secure application.

## Deployment / repository configuration

Set GitHub Pages to **GitHub Actions** in repository Settings → Pages. Push source and workflows to `main`. Build and deploy jobs upload `dist/` as the Pages artifact, including offline downloads. Official repository: https://github.com/mightora/semantic-model.mightora.io. Production URL: https://semantic-model.mightora.io/. The build embeds the official Mightora logo and tests all online and offline releases. Check GitHub Actions runs and deployment status before relying on them.

## Licence

MIT, see [LICENSE](LICENSE). Built under Mightora's shared branding and static web development standards.

### Shared Mightora footer resilience

The online edition loads the canonical `mightora/shared-ui` footer component and its shared YAML feed.
`assets/footer-fallback.json` is a deliberately static, inspectable snapshot of the same navigation
and brand links, rendered by `scripts/build.py` for both GitHub Pages and the standalone edition.
It remains visible if the shared CDN, JavaScript or footer YAML fails. Modern browsers hide it when
the shared component successfully inserts navigation columns **and** brand cards, avoiding duplicate
links. The fallback uses absolute Mightora links so subdomains never redirect to non-existent
local privacy, about or terms pages. Review the snapshot if the upstream footer navigation changes.

## Accessibility and colour-blind-friendly diagrams

The diagram uses clearly labelled fact and lookup tables, explicit **Single →** and **Both ↔** relationship direction labels, **1 / \*** cardinality markers, solid active and dashed inactive relationships, and a keyboard-operable **Links** list. It does not rely on colour alone to convey these meanings. Use the **High contrast** toggle for stronger monochrome relationship and table outlines; the preference stays in local browser storage (where available). High contrast is enabled automatically when the system requests increased contrast. Text, buttons and interactive states use darker high-contrast colours and larger default sizes. Reduced-motion preferences are respected. The exported SVG preserves these diagram labels and relationship patterns.

Contrast ratios were checked for selected foreground/background combinations, with the smallest of the tested text ratios exceeding 7:1. This is **not** a claim of full WCAG conformance or a substitute for assistive-technology testing.
