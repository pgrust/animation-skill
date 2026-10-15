# Opinionated visual direction for Blender explainers

This is the default art direction for a new Blender project. It is intentionally
opinionated: a blank scene and a technically correct event table do not produce
a useful 3D explainer. Change these defaults when the mechanism demands it, not
because a flat diagram is easier to script.

The defaults are neutral. They do not encode a company, product, benchmark, or
brand. They encode the visual decisions that repeatedly made short technical
animations legible at feed size.

## Prove that the story belongs in 3D

Use Blender only when at least one of these carries information:

- a work unit crosses between visible owners;
- several items overlap in a queue, pipeline, pool, fan-out, or merge;
- assembly, storage depth, occlusion, or a material change explains state;
- a camera reframe reveals scale or a relationship that one flat view hides.

Do not make a row of three labeled boxes with one cube sliding through them.
That is an SVG diagram with slower rendering and worse labels. Either enrich it
with depth, repeated work, visible ownership, and a meaningful final state, or
use SVG mode.

## Start from one of five scene archetypes

Pick the closest archetype before creating geometry:

| Archetype | Default staging | Best for |
| --- | --- | --- |
| Queue to worker pool | Diagonal feeder, three depth-separated workers, visible backlog | scheduling, concurrency, reuse, load balancing |
| Parallel pipeline | Three stages across the frame, two or three depth lanes, six to twelve overlapping items | parsing, compilation, ETL, network or storage pipelines |
| Fan-out and merge | One source, curved depth-separated branches, one recombination point | sharding, parallel plans, map/reduce, distributed work |
| Before and after | Two equally sized physical systems sharing one camera and timing | architecture or algorithm comparisons |
| Bank, gate, and rack | Reusable source parts, one transformation gate, numbered destination slots | assembly, JIT, encoding, patching, materialization |

The project generator starts from the parallel-pipeline archetype. Preserve its
camera, lighting, density, beat structure, and validation while replacing its
teaching claim and objects.

## Use a four-beat timeline

For a 10 to 15 second video, use this rhythm:

1. **Orient, 0.6 to 1.2 seconds.** Establish the whole machine and labels. Nothing
   important moves while the viewer learns the frame.
2. **Demonstrate, 1.2 to 2.5 seconds.** Move one identified item through a complete
   operation. Make every ownership change readable.
3. **Accelerate, 4 to 8 seconds.** Overlap repeated items so the mechanism's
   concurrency, throughput shape, or reuse becomes visible.
4. **Land, 1.5 to 2.5 seconds.** Hold the completed state, pulse the takeaway, and
   leave enough time to read it.

At 30 FPS, ordinary transfers should usually take 14 to 27 frames. State commits
should read in 3 to 8 frames. Do not use uniform linear timing for every beat.
Use clamped Bézier motion for physical travel, short scale or emission pulses for
commits, and constant interpolation for discrete visibility.

## Meet the density floor

Unless one large transformation is the subject, a Blender master should begin
with these targets:

- 6 to 12 semantic work items;
- 2 to 4 items visibly in flight at the peak;
- 3 depth planes: foreground, mechanism, and background or destination;
- 3 or more meaningful zones;
- one complete demonstrated operation before acceleration;
- one final composition that visibly accounts for every work item.

These are design defaults, not technical facts. If the real mechanism has only
one item, show its meaningful subparts, intermediate representation, or spatial
transformation instead of cloning it into a false throughput claim.

## Compose for depth before adding motion

Use the default three-quarter camera from
`blender_animation.scene.add_three_quarter_camera`. Its offset in X, Y, and Z
exposes top, front, and side faces. Lay major routes on diagonals or stagger
their Y position. Avoid placing every station, path, and label on one plane.

Reserve quiet screen regions for the title, stage labels, and final takeaway.
Put semantic objects near the center and decorative structure toward the edges.
Check the first, peak, and final frames at 640×360. If depth disappears at that
size, the staging is too shallow.

## Put semantic labels on semantic objects

Default to in-scene labels. A stage name belongs on the stage block. A node name
belongs on the node. A slot number belongs on the slot. A moving-item ID belongs
on the moving item. Parent each label to its owner so transforms, camera motion,
lighting, depth testing, and occlusion remain physically coherent.

Use `add_attached_label` in one of two modes:

- **Surface-aligned** is the default for stationary machinery and objects with
  a readable face. Put text 0.02 to 0.06 scene units above the face to avoid
  z-fighting. A top label lies with the top surface; a front label lies with the
  front face.
- **Object-anchored billboard** is allowed for a small mover or irregular object
  whose surfaces never face the camera. It must remain a child of that object.
  It may rotate with the camera, but it may not live in the camera plane or be
  parented to the camera.

Unanchored camera-facing text is reserved for one title and, when the scene
needs it, one caption or final takeaway. Do not use compositor text, camera-space
HUD text, or floating screen-parallel labels for stages, nodes, fields, rows,
ports, or work items. If removing the object would leave its label floating in
the same screen position, the label is wrong.

### Readability rules

- Use one line and one to three words per object label. Prefer 18 or fewer
  characters. Move explanation into the caption or surrounding post.
- At 1280×720, important object labels should render at roughly 18 px cap height
  or larger. At the 640×360 review size they must remain identifiable, even if
  small secondary text is no longer comfortable to read.
- Use light text on a dark surface or dark text on a bright plate. If the object
  changes color, add a stable contrasting inset plate instead of letting label
  contrast change with state.
- Use restrained emission, typically 0.1 to 0.35, only to protect readability.
  Text still needs surface shading and must not bloom into its background.
- Keep a clear border around the glyphs. The label should occupy no more than
  about 70 percent of its owning face's width.
- Render the longest label at the most oblique camera pose and at final
  resolution. Check for surface intersection, z-fighting, clipping, and
  occlusion by moving objects.

The semantic label itself should be a real object visible in the Blender scene
graph. A title may read like graphic design; machinery labels should read like
labels manufactured onto the machinery.

### Camera choreography

A strong fixed oblique camera is the safe default. Camera motion is not a
substitute for object motion. Add at most two semantic reframes:

- a short 8 to 12 percent dolly or scale change from overview to mechanism;
- a 6 to 12 degree orbit when it reveals hidden depth or a final assembly;
- a final reframe toward the completed state.

Hold the camera still during fast handoffs. Do not run a constant orbit. It
makes labels drift and makes ownership harder to judge. Use
`key_camera_pose` for the reframe. Use `follow_orthographic_camera` only for an
object-anchored billboard that must stay parallel to an animated orthographic
camera; surface labels should keep their owner's rotation.

Depth of field is off by default because blurred owners and labels weaken an
explainer. Use shallow depth of field only for a label-free introduction or
final beauty beat, and render a sharp version to confirm that the blur carries
meaning rather than hiding weak composition. Motion blur is also off by default.

## Make state changes causal

Every moving work item needs its own material data block. Use three visible
states:

- idle: dark structural material;
- active: saturated color plus restrained emission;
- settled: a distinct success material or quiet returned state.

The destination must respond to arrival with a ring, light, scale pulse, latch,
counter, or physical occupancy. Moving an object near a box without a response
does not communicate ownership. Keep inactive gates and destinations dim.

Use `DEFAULT_PALETTE` as the neutral starting palette:

- near-black world and navy floor;
- blue-gray machinery with bright edge separation;
- off-white text and muted blue-gray secondary copy;
- cyan active state, amber secondary path, violet accent, and green settled state.

The palette is a tested starting point, not a semantic standard. Replace it as
a complete system. Do not borrow a user's product palette without permission.

## Use lighting that describes form

Start with `add_three_point_lighting`: warm key, cool fill, and neutral rim. Use
beveled geometry so highlights expose edges. Keep the world dim and let object
materials, contact shadows, and rim light separate overlapping forms.

Avoid these common failures:

- emissive panels with no surface shading, which look like flat SVG cards;
- one frontal light, which erases depth;
- pure black idle objects, which disappear before activation;
- bloom or emission strong enough to wash out labels;
- decorative reflections that compete with ownership state.

## Validate the visual design

Before a final render, answer these questions from pixels, not source code:

1. Does the first frame explain the whole stage without motion?
2. Does the camera show top, front, and side faces on the main objects?
3. Does the peak frame contain at least two meaningful items in motion when the
   mechanism is concurrent?
4. Can a viewer identify the active item, its owner, and its destination at
   640×360?
5. Does each commit produce a visible response at the destination?
6. Does the final frame account for every item and hold for at least 1.5 seconds?
7. Would the story be equally clear as three flat cards and one moving dot? If
   yes, rebuild the 3D metaphor or switch to SVG.
8. Are stage, node, slot, and work-item labels children of their owning objects,
   with normal scene occlusion? A floating semantic HUD label fails review.

Review orientation, first completion, peak overlap, and final state as stills.
Then review the complete low-resolution timeline and dense strips around every
handoff. A contact sheet alone cannot prove short transitions are correct.
