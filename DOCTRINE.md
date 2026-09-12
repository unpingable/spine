# DOCTRINE

Spine is the read plane of the constellation. Its purpose is to make a corpus
of governed material navigable, legible, and durable for readers — including
strangers — without requiring oral tradition.

This document defines what Spine is allowed to be. It is the first artifact
in this repository because the boundary is cheaper to draw now than to
excavate later.

## Position in the constellation

- **Continuity** is the intended semantic substrate for reliance; no live
  Continuity dependency is implemented here.
- **Maude** supplies approved PlanCore validation for proposals; a human accepts
  proposals, and **AG** is the authority boundary for governed authorization.
- **Spine** governs what can be found and read. (Read plane.)

Spine's intended architecture reads declarations from Continuity; Continuity does
not depend on Spine. Spine may arrange, package, and present governed material,
but it does not originate canonical semantic state.

Spine performs none of PlanCore validation, human acceptance, or AG
authorization. The current public ingress is a provisional declared Git manifest;
the static Continuity-shaped fixture is a substitution fixture, not an actual
Continuity dependency. Imported documents, external references, generated indexes,
and editions assembled from already-governed material may be declared directly.

## Charter

- **C1.** Spine may present declared material without inferring reliance from it.
- **C2.** PlanCore validation, human acceptance, and AG authorization remain
  outside Spine.
- **C3.** Spine governs what can be found and read.
- **C4.** Presentation must not collapse into authority.
- **C5.** Spine-native objects include at least *index*, *edition*, and
  *stele*, each with distinct durability and status promises.
- **C6.** If a stranger cannot recover the corpus without oral tradition,
  Spine has failed its purpose.

## Object classes

**Index** — navigational. A mutable finding aid. Confers no status. May
change without ceremony.

**Edition** — packaging. A timestamped assembly of governed material.
Immutable once published; may be superseded, withdrawn, or tombstoned only
with visible notice, never silently revised.

**Stele** — inscription. A durable public artifact, set in stone, with
visible amendment burden. Meant to outlive the reader.

These are not interchangeable. A stele is not a heavy index; an edition is
not a stele with a date stamp; an index is not a draft edition.

## Must not

- **N1.** Spine MUST NOT silently mutate canonical semantic state.
- **N2.** Spine MUST NOT confer reliance by presentation, arrangement, or
  prominence.
- **N3.** Spine MUST NOT imply adjudication or standing by inclusion,
  arrangement, or prominence.
- **N4.** Spine MUST NOT hide supersession or amendment where durability is
  claimed.
- **N5.** Spine MUST NOT present a published object whose provenance and
  class are not legible to the reader.

## Falsification

> If a stranger cannot walk up to the corpus and recover its structure
> without oral tradition, Spine has failed.

This is the test, not an aspiration. When a design choice is contested, ask
whether it makes the corpus more or less recoverable by someone who arrives
with no context and no chaperone.
