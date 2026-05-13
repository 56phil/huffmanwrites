---
title: "What 926 Gigabytes Taught Me About Proportion"
description: "On the temptation to reach for the sledgehammer, and the discipline required to use the scalpel instead."
date: 2026-05-10T00:00:00Z
author: Phil Huffman
lastmod: 2026-05-10T00:00:00Z
tags:
  - essays
  - philosophy
  - stoicism
  - technology
hero_desktop: "img/articles/42 scalpel-not-sledgehammer 16x9.webp"
hero_mobile: "img/articles/42 scalpel-not-sledgehammer 4x5.webp"
hero_alt: "A marble figure at a crossroads between a massive sledgehammer over rubble and a delicate scalpel over a glowing gold vein."
hero_caption: "The discipline required to use the scalpel instead of the sledgehammer."
---

I was ready to do something drastic.

My machine had been running hot for weeks. Disk usage climbing, performance lagging, the kind of quiet degradation that starts as inconvenience and ends as crisis. I had installed AnythingLLM to test it, decided it wasn't ready, uninstalled it — and yet the space never came back. The numbers didn't lie. Something was eating my disk, and I couldn't see it.

The easy answer was staring at me: clean install. Wipe the whole system, start fresh, rebuild from zero. It's the digital equivalent of the scorched-earth impulse — the one that says, *if I can't understand the problem, I'll eliminate the conditions that produced it.* I've done it before. Most of us have. It feels like control. It feels like decisiveness. It is almost always a confession that we have failed to understand what we are actually dealing with.

So I paused.

That pause is the hard part. Because in the moment of frustration, action feels like virtue. Sitting with the problem — mapping it, tracing it, refusing the catharsis of a dramatic fix — requires something colder than impulse. It requires the willingness to be confused for a while longer than is comfortable.

I started looking. Not everywhere. That would have been another form of the same imprecision — the brute-force audit, the digital equivalent of tearing up floorboards to find a leak. I looked where the pattern pointed. Where had I made a change? What had I added, and what had I failed to fully remove?

It wasn't in the obvious places. Not in my home directory, where most user data lives. Not in the application folder, where the uninstaller had done its dutiful surface cleaning. The space was hiding in a place most users never see: `~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw`. A single virtual disk image, left behind by Docker's virtualization layer, bloated to 926 gigabytes by the accumulated weight of AnythingLLM's models, vector stores, and container layers.

One file. Nearly a terabyte.

I deleted it. Two directories alongside it — `.omlx` and `.lmstudio`, other local LLM caches I was no longer using — went with it. Then I purged the Time Machine snapshots that were pinning the deleted blocks. The machine dropped from six hundred gigabytes in use to twelve. A 97% reduction. The system was intact. My work was untouched. Nothing was sacrificed that didn't need to be.

The lesson isn't about Docker. It isn't even about disk cleanup.

It's about the right-sized response.

There is a particular violence in the phrase *clean install*. It sounds like hygiene. It promises a fresh start. And it is almost always a sophisticated form of surrender — a decision to tolerate massive collateral damage rather than do the harder intellectual work of locating the actual bleeding vessel. The surgeon who cuts before he finds the bleed doesn't save the patient; he changes the cause of death. The general who levels a city to root out a single cell doesn't win a war; he manufactures the next war. The developer who rebuilds his entire environment to fix a single configuration error isn't solving a problem; he's outsourcing his understanding to entropy.

Brute force is seductive because it satisfies our need for agency. When a system frustrates us, there is genuine emotional relief in declaring scorched earth. It makes us feel like protagonists. But it is, more often than not, an anxiety management technique disguised as a solution. The scorched-earth impulse is what you reach for when the discipline of diagnosis feels like wasted motion.

Surgical precision is slower at the start and faster at the finish. It demands that we accept a period of useful helplessness — the interval where we observe without acting, where we map the topology of the problem before we alter it. The Stoics spoke of *prohairesis*, the faculty of reasoned choice, and of acting only on what is within our control. But control is not binary. It is granular. Brute force pretends to total control while actually ceding most of it to chaos. Surgical precision is the act of calibrating our control to the exact scale of the problem. It is the discipline of the rightly proportioned response.

This shows up everywhere.

The junior developer restarts the server. The senior developer reads the stack trace. The amateur investor sells everything at the first tremor. The disciplined one rebalances. The angry man burns a relationship to the ground; the temperate man isolates the conflict and addresses it directly. The anxious mind catastrophizes an entire future; the trained mind identifies the single assumption driving the fear, and tests it.

In my own writing, I see the same pattern. There is always the temptation, when a chapter is failing, to scrap the whole thing. Delete it. Start over. Sometimes that's correct — when the structure itself is rotten. More often, what's failing is a single joint, a transition, a sentence that carries more weight than it can bear. The discipline is learning to tell the difference between a broken sentence and a broken argument. They require different cures. The first gets a scalpel. The second might genuinely need the sledgehammer. But you can't know which until you've looked.

What I saved this weekend wasn't just disk space. It was my own configuration — the accumulated toolchain, the aliases, the minor customizations that make a machine feel like mine. The stuff that you don't remember until it's gone. That is what brute force always costs you: not just time, but the invisible infrastructure of habit. The clean install gives you a blank slate, but a blank slate is just another word for amnesia. The real art is in excising the tumor without killing the patient.

Precision before power. That is the metric. Not how fast we moved, but how little we broke on the way to fixing what mattered.
