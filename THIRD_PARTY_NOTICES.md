# License scope and third-party material

Original Your Whole Personality application code and documentation are licensed under the root MIT license. This does not grant rights in third-party APIs, data, artwork, names, trademarks or separately licensed material.

- The Sites runtime is adapted from the official Sites Vinext starter. Retained vendored Sites Vite plugin notices are in `sites/scripts/vite/sites-vite-plugin.LICENSE`. Retained styling notices are in `sites/vendor/shadcn-tailwind-4.13.0.LICENSE.md`.
- Installed npm dependencies retain their own licenses. `sites/package-lock.json` pins their versions; package distributions include their license notices. Dependency code and local `node_modules` are not vendored into this repository.
- Qloo provides entity/tag/audience resolution, affinities, recommendation rankings and remote artwork URLs. Stored responses, catalog/demo entity metadata and research API captures remain subject to applicable Qloo and underlying third-party terms; the MIT license does not relicense those data or images. Entity names and trademarks belong to their respective owners. Exported game cards use text rather than copying remote artwork pixels.
- NVIDIA hosts model inference; model/service access is subject to its applicable account and model terms. This repository contains no model weights or provider credentials.
- Archived prior research retains its provenance and limitations in `research/ARCHIVE.md` and the archive's own documentation/notices. Application licensing does not establish permission to redistribute externally supplied data in the archive.

This release is intended for a time-limited hackathon judging demonstration. That intent is not a provider entitlement or a representation that all public-use/data permissions have been verified. No permission is granted to reuse other people's API credentials. Supply your own authorized keys through server environment settings.
