# Failure Doctrine

The governing document for how this repository treats failures and organizes
itself. The flat layout, `manifest.json`, `tickets-flattening.md`, and the
execution ledger all implement these rules. Text recorded verbatim from the
repository owner (2026-09-02).

## Plainly

| What was written | What it means, plainly |
| --- | --- |
| "A system does not learn by receiving a failure, assigning it a type, and eliminating it." | Sorting a failure into a category and deleting that category teaches you nothing. You edited your filing system, not your understanding. |
| "It learns when a failure changes the visible graph of relations among evidence, assumptions, actions, agents, tools, people, and consequences." | A failure is a flashlight in a dark machine room. The lesson is not the failure — it's the wiring it lights up: which guess fed which action, which person or tool touched which outcome. |
| "Multiple loops may then run, repeat, fork, or change order according to the edges that have become visible." | Once you can see the wiring, your routines (watch, check, act, review) stop being a fixed checklist. You reorder them, repeat some, split others — whatever order the new wiring demands. |

## The ten rules

1. **A failure is prey, not a pest.** You don't fence it out — you study it. It's your own hidden wiring showing itself.
2. **Read the tracks before you shoot.** Understand the path before you fix anything.
3. **Move upwind.** Watch without disturbing — read-only before you write.
4. **Ambush the water holes.** Put your checks where many paths cross, not everywhere.
5. **Follow, don't chase.** A rushed fix destroys the trail.
6. **Butcher, don't box.** Cut along the failure's real path, not your category list — root-cause hunting serves the need to blame, not the need to understand.
7. **Use every part.** Plains families got meat, tools from bone, thread from sinew, fuel from fat — a failure yields relations, timing, slack needs, and monitoring gaps.
8. **Take only what you need.** Smallest irreversible action that reveals the most.
9. **Thank the animal and the messenger.** Never punish whoever reports a failure, or the reports stop coming.
10. **Return the bones, leave the herd.** Publish learning back into shared memory, and never optimize away all your surprises.

## The step-by-step playbook

Standing setup, before any failure:

0. **Build the water holes.** Know your baseline, place monitoring where paths converge, and agree who watches downwind — the one testing the assumption everyone else shares.

When a failure lands:

1. **Stop.** Freeze the scene — capture state, logs, and timeline before anything changes.
2. **List the wiring it exposed**: which assumption fed which action, which tool, agent, or person connected to which consequence, in what order.
3. **Ask "what did this connect?"** — never "what type is this?"
4. **Butcher it**: validated relations go to memory, monitoring gaps become new instrumentation, sequence facts become order rules, consumed slack becomes resized buffers.
5. **Tell the story around the fire**: a short, blame-free narrative of the relations, with the reporter thanked by name.
6. **Re-order your loops from the new map**: which runs first, which forks, which repeats. Write it as triggers ("when X, loop Y"), not a fixed schedule.
7. **Decide only when independent edges converge** — then take the smallest irreversible shot.
8. **Return the bones**: story, timeline, and new checks go into shared memory, so the next failure arrives as a gift rather than an ambush.
9. **Leave the herd alive**: restore slack, keep some ground unmeasured, rotate where you hunt next season. Return to step 1.

## The moments

| The moment | The rule | The move |
| --- | --- | --- |
| A failure appears | Prey, not pest | Freeze; don't fix yet |
| You itch to fix it now | Follow, don't chase | Trace the whole path first |
| You reach for a label | Butcher, don't box | Write the edges instead |
| Someone reports it | Thank the messenger | Zero blame, public thanks |
| A decision looms | The shot | Wait for independent edges to converge; take the smallest one |
| Learning is finished | Return the bones | Publish story, timeline, and new checks |
| Things look stable | Rotate the seasons | Explore unmeasured ground; test the shared assumption |
| You've "eliminated failure" | The last deer | Stop — you've starved your teachers; put variance back |

## Constitution

- **Move**: along visible edges, upwind, toward water holes.
- **Learn**: butcher the whole animal; keep stories, not labels.
- **Plan**: triggers and seasons, never fixed routes.
- **Decide**: converge first, then one small irreversible shot.
- **Sustain**: return the bones; leave the herd.

**Epistemological system management, in one sentence:** run what your system
knows the way a hunter runs a hunt — treat every failure as an animal that
gives itself to you, extract the full anatomy, waste nothing, take little,
give back, and never kill the source of future gifts.

## How this repository implements it

- **Keep stories, not labels** → the folder taxonomy (labels) was removed;
  `manifest.json` keeps every file's old-path→new-path edge (the story).
  Ticket record: `tickets-flattening.md`.
- **Freeze the scene** → pre-mutation SHA-256 inventory before any move;
  pure-rename commit provable by `git diff -M100%`.
- **Move upwind (read-only before you write)** → the execution ledger records
  constraints at session open, before mutation.
- **Ambush the water holes** → `validate.sh` checks the few places all paths
  cross (flat invariant, manifest coverage, chain integrity, tests), not
  everything everywhere.
- **Take only what you need** → moves keep original basenames; no content
  byte changed except where a receipt says `edited`.
- **Return the bones** → this doctrine, the tickets, and the manifest are the
  bones returned to shared memory.
