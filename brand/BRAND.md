# rasid — Brand Notes

## The idea

**rasid** (راصد) means *observer*. The project watches ships to predict congestion. The logo is a lowercase wordmark where **the dot of the "i" is a container ship** heading right, toward the "d" and toward what comes next, which is what forecasting is about.

- **It reads first as a word,** and the ship is the detail you notice second. That's the difference between a designed mark and clip-art.
- **The ship is one solid silhouette:** hull with a raked bow, three container stacks, and the bridge tower at the stern. Gaps between the stacks match the letters' rhythm.
- **Exact alignments:** the top of the bridge lines up with the top of the "d", and the gap between ship and "i" follows the font's own dot spacing.
- **Rejected along the way:** the ship as the "I" (it read as a rocket or bullet), the "D" as a hull (it read as a ▷ play button), and a top-view ship dot (it read as a pencil or bullet). A ship's side profile is the only view that's unambiguous at small sizes.

## Colors

| Name | Hex | Use |
|---|---|---|
| Deep navy | `#0E2238` | Wordmark on light backgrounds; dark backgrounds |
| Signal orange | `#D4602A` | The ship, the one accent: maritime safety orange (lifeboats, buoys) |
| Ivory | `#F4F0E8` | Wordmark on dark backgrounds |
| Warm gray | `#C9C3BA` | Studio / neutral surfaces |

Rule: **orange is only ever the ship.** Never color letters orange.

## Typography

- **Bahnschrift** (Windows system font, DIN-style). Its technical, signage character fits maritime and data.
- Logo weight: Regular, with a slight outline bevel for presence.
- Body text in documents: any clean sans-serif (Segoe UI, Inter).

## Files (`brand/`)

| File | Use |
|---|---|
| `rasid_logo_flat_light.png` | Main logo on white / light backgrounds (transparent PNG) |
| `rasid_logo_flat_dark.png` | Logo on dark backgrounds (transparent PNG) |
| `rasid_mark.png` | App icon / avatar / favicon source (ship on a navy tile) |
| `rasid_logo_3d.png`, `rasid_logo_3d_dark.png` | Hero images for slides, the README banner, the defense deck |
| `rasid_logo.blend`, `rasid_logo_dark.blend` | Editable Blender scenes |
| `rasid_logo.py` | Regenerates everything: `blender -b --factory-startup -P brand/rasid_logo.py [-- --dark]` |
| `rasid_logo_circle.svg`, `.png` | **Official emblem.** The wordmark in a navy instrument dial: satin metal bezel, a radar sweep aimed at the ship, bearing ticks, wake lines, and a lettered ring ("MARITIME CONGESTION PREDICTOR" / راصد). For cover pages, title slides and posters: anything wider than ~4 cm |
| `rasid_logo_circle_small.svg`, `.png` | The same emblem without the lettered ring, which is unreadable when small. For **document headers (top-left, ~2.5 cm)**, avatars, and anything 1–4 cm wide |
| `rasid_logo_circle.py` | Regenerates both emblems (needs only `fontTools`; reads ship geometry, colours and font from `rasid_logo.py`): `python brand/rasid_logo_circle.py`. PNGs (2000 px, transparent corners) are rendered from the SVGs with headless Edge |

The emblems are the one place the brand uses gradients and a soft lift shadow: they imitate a physical instrument. The flat wordmark rules below still apply everywhere else.

## Don'ts

- Don't stretch the logo, add shadows or outlines to the flat logo, or put the navy version on dark photos.
- Don't separate the ship from the "i" in the wordmark. On its own, the ship is only used as the app icon.
- Keep clear space around the logo of at least the width of the ship on all sides.
