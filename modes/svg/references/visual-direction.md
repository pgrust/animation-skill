# SVG visual direction

Use these defaults unless the story gives you a reason to change them. They are
neutral rather than brand-specific, and they optimize for a silent technical
clip viewed near 640 pixels wide.

## Composition

Start at the scene's native dimensions. The starter uses 1280×720. Keep critical
text and motion at least 48 pixels from the edge.

Use this hierarchy:

1. one short headline;
2. names for the systems, stages, or mechanisms;
3. the dominant moving objects;
4. counters or progress attached to their owners;
5. one quiet accuracy note when timing or values are illustrative.

Reserve space for the longest label, largest counter, peak number of moving
objects, and final conclusion before animating. Remove permanent regions that
repeat the surrounding post or narration. Mechanism needs the space more than
dashboard chrome does.

For a comparison, give both sides the same relevant baselines, path lengths,
input denominator, and progress scale. Write a small geometry ledger before
styling: spawn point, destination, travel distance, object bounds, stage bounds,
and any intake aperture.

## Palette and type

The starter palette is a useful neutral baseline:

- canvas: `#080b10`;
- surface: `#111722`;
- structural border: `#2a3442`;
- primary text: `#edf2f7`;
- muted text: `#8390a0`;
- active work: `#58b7ff`;
- completed or verified state: `#61d6a3`;
- failure only: `#ef6f79`.

Use one accent for active work and one for a verified destination. Do not assign
a new color to every noun. Keep glow behind information and reserve it for
movement, selection, or a commit.

Use sans-serif text for headlines and entity names. Use a native monospace
stack for IDs, code, counters, and machine state. Keep the headline under about
eight words. Prefer full familiar labels over abbreviations a viewer must decode.

## Objects and paths

Use a small vocabulary: work item, queue, stage boundary, lane, source, sink,
counter, and progress track. Make data physical by moving, stacking, splitting,
merging, draining, or committing it. Prefer a moving object over an arrow when
the object can carry the meaning.

Every semantic object has one visible owner. Derive source visibility, mover
position, destination state, counter, and progress from the same event. Do not
render separate source and destination copies that can overlap during a handoff.

Keep paths topologically honest. A bend implies routing, a pause implies a stage,
and a split implies fan-out. Move a label or resize a panel instead of inventing
a technical event to solve a composition problem.

Use this paint order as a review starting point:

1. background and quiet texture;
2. queues, rails, and inactive structure;
3. stage surfaces;
4. moving work;
5. narrow masks or intake lips;
6. state text, counters, and progress.

## Motion

Use four motion types:

- **Reveal:** opacity plus 8–20 pixels of travel over 300–600 ms.
- **Transfer:** one clear path over 450–900 ms.
- **Commit:** a 100–250 ms stroke, glow, or scale pulse when state changes.
- **Finale:** a stable result held long enough to read.

Avoid bounce for data movement. Use one easing curve per transfer. If overlap is
part of the mechanism, make transfer duration longer than dispatch interval and
inspect a peak frame with two to four readable items in flight.

The `fast` and `presenter` profiles must share events, object identities, data,
geometry, and final state. Change stage timing, repetition gaps, and holds—not
global video speed.

| Profile | Setup | First complete example | Final hold |
| --- | ---: | ---: | ---: |
| `fast` | 0.3–0.7 s | 0.8–1.4 s | 0.9–1.4 s |
| `presenter` | 0.8–1.5 s | 1.6–3.0 s | 1.8–3.0 s |

## Labels and state

Attach labels to the object or stage they name. Keep them outside motion
corridors. Give control signals and data different shapes so a pulse cannot be
mistaken for a row or packet.

Counters, queue contents, progress, highlights, and final totals must come from
the same state function as moving objects. Test the widest value, largest total,
peak overlap, and final settled frame. Temporary arithmetic may move a value,
but settled output should return to its optical center.

## Review at feed size

At first glance, a viewer should be able to answer:

1. What objects or systems are present?
2. What is moving or changing?
3. What state changed at the destination?
4. What mechanism caused the result?

Capture orientation, first complete event, peak overlap, and final state at
native resolution. Then inspect the same frames near 640 pixels wide. Use a
dense strip around every 100–300 ms handoff; sparse contact sheets miss duplicate
owners, stale counters, border collisions, and one-frame flashes.
