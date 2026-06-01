---
title: "The Optimal Use of Hermes: From Tool to Editorial Operation"
description: "How a persistent AI agent changed the way I think, write, and work — and what I've learned about using it well."
date: 2026-05-21T00:00:00Z
author: Phil Huffman
lastmod: 2026-06-01T00:00:00Z
tags:
  - ai
  - essays
  - tools
  - writing
---

**Update (June 2026)**: Hermes is no longer part of my workflow. It has been replaced by [Claude](https://claude.ai), a more reliable and consistent AI assistant. While Hermes was groundbreaking in its approach, it leaped without looking too many times—its autonomous nature often led to unpredictable or undesirable outcomes. This essay remains online as a historical record of my experience with Hermes, but I no longer use or recommend it.

---

About six weeks ago, I wrote a short essay explaining that I use artificial intelligence as part of my writing process. The core observation was simple: AI does not originate ideas, but it exposes structure. It mirrors patterns back at you, shows you where an argument repeats itself, amplifies confusion rather than resolving it, and generally behaves less like a writer and more like a diagnostic instrument.

That was true then. It is still true now. But the tool has changed, and so has the nature of the partnership.

I now work with Hermes, an open-source AI agent framework from Nous Research (Nous Research, 2026a, 2026b). It is not a chatbot. It is not a single model accessed through a web interface. It is a persistent agent — stateful, autonomous, capable of running shell commands, reading and writing files, spawning subagents to handle parallel work, searching the web, scheduling recurring tasks, and maintaining durable memory across sessions. It learns from experience and encodes that learning into reusable skills. It does not wait to be prompted for every small step. It acts.

This essay is about what I have learned about using such a tool well. Not the setup instructions or the configuration flags — those are documented elsewhere. What I want to describe is the mental model shift: from treating AI as a drafting assistant to treating it as an editorial operation.

## What the Tool Actually Is

Most people's experience with AI is transactional. You type a prompt. You get a response. The machine has no memory of your last conversation and no independent capacity to act on your behalf. Each interaction begins from zero. This stateless paradigm has been the norm since the first chatbots, but it is a fundamental constraint on what AI can become. As Packer et al. (2023) demonstrated with MemGPT, persistent memory transforms an LLM from a single-purpose query engine into something closer to an operating system — able to maintain context, recall relevant history, and manage long-running tasks across session boundaries.

Hermes is different in several ways that matter.

First, it remembers. Not just within a conversation, but across sessions. It maintains a durable memory store where it records facts about you, your preferences, your environment, and lessons learned from previous work. When we start a new session, it does not ask me to reintroduce myself. It knows my project structure, my writing voice, my time zone, and which design choices in my site are intentional rather than accidental. This mirrors what Park et al. (2023) called the "memory stream" in generative agents — a persistent, retrievable record of experience that enables agents to develop coherent, context-aware behavior over time.

Second, it learns procedurally. When we solve a complex problem together — debugging a Hugo template, setting up a cron job that fetches financial data, converting book covers from one format to another — it can encode the workflow as a skill. Next time the same kind of task arises, the skill loads automatically with step-by-step instructions, known pitfalls, and verification steps. The agent literally gets better at my specific tasks the more I use it. This self-improving loop echoes the approach of systems like Voyager, where Wang et al. (2023) showed that encoding successful behaviors as a reusable skill library — rather than re-deriving solutions from scratch — produces dramatic compound improvements in agent capability over time.

Third, it delegates. Hermes can spawn subagents — isolated instances with their own context and terminal sessions — to handle subtasks in parallel. A single instruction can fan out into three simultaneous workstreams: one researching, one editing, one checking links. The parent agent receives summaries and integrates the results. Multi-agent architectures like this were formalized by Wu et al. (2023) in AutoGen, which demonstrated that delegating subtasks to specialized subagents outperforms monolithic single-agent approaches for complex multi-step work. This is not a gimmick. It is the difference between writing a report yourself and managing a small team that writes it for you.

Fourth, it schedules. Cron jobs let me set up recurring autonomous tasks — site audits every Monday at 11:30 PM, portfolio performance reports every Sunday at 1:30 PM. The agent wakes up, does the work, writes a formatted report to my inbox, and delivers a summary. I do not have to remember.

None of these capabilities are individually new. Task scheduling has existed for decades. Delegation is management 101. Memory is what databases do. What is new is combining all of them inside a reasoning system that can exercise judgment about how and when to use each one.

## The Shift: From Tool to Operation

The first essay described a one-to-one relationship. I wrote. The AI reflected structure back at me. I revised. The loop was tight and personal.

That loop still exists, and I still use it. But it is now only one mode among several. The more interesting modes are the ones where I am not drafting at all — I am directing. Dellermann et al. (2019) called this "hybrid intelligence" — the shift from AI as a passive instrument to AI as a collaborative partner that augments human decision-making rather than merely executing it.

Here is a concrete example. Earlier today I told Hermes to audit my Hugo site and write a report. It did not ask me which pages to check, which links to scan, or what format to use. It loaded its site-maintenance skill, which contains the full pre-commit workflow: spelling and grammar scans, a build verification step, commit conventions, and a checklist. It ran the checks. It found issues. It fixed them. It updated the running session-state document. It committed and pushed. Then it told me what it had done.

That is not an AI writing assistant. That is an editorial operation with one human in the loop.

The optimal use of Hermes, I have found, is to treat it this way. As a persistent, learning, self-improving editorial staff. Your role shifts from author to managing editor. You define the task, the standards, and the boundaries. The agent executes within them. When it makes a mistake — and it does — it records the correction and does not make that mistake again.

## The Skills Feedback Loop

The most important concept in Hermes is the skill. A skill is a markdown document that describes a workflow: when to trigger it, what steps to follow, what commands to run, what pitfalls to avoid, and how to verify the work.

The crucial property is that the agent can create, update, and improve its own skills. This means the tool is not static. Every time we work through a difficult task — something involving five or more tool calls, or requiring us to overcome errors, or resulting in a user correction that changes the approach — the agent can encode what we learned. Next time, it follows the recipe instead of improvising. Shinn et al. (2023) described a similar dynamic in Reflexion, where agents that learn from verbal feedback and record corrections outperform those that treat each task as an isolated attempt. The mechanism is different — Hermes encodes workflow documents rather than verbal reflections — but the principle is identical: an agent that records and reuses what it learns will compound its capability.

Over weeks of use, the skill library grows. The agent that started as a general-purpose assistant becomes specialized to your specific projects, your specific environment, your specific preferences. It develops institutional knowledge.

This is the single most underappreciated aspect of working with an agent. Most AI tools treat every interaction as isolated. Hermes treats every interaction as training data for the next one. The compound effect is real and it is large.

## When to Delegate and When to Do It Yourself

The delegation tools are powerful and easy to misuse. A subagent can be told to research a topic, write a section, debug a function, or check for broken links. It works in its own context, with its own terminal, and returns a summary. The parent agent never sees the intermediate steps — only the result. Wu et al. (2023) demonstrated this multi-agent pattern in AutoGen, where a manager agent coordinates specialist subagents that produce results the manager must integrate.

This is efficient but also dangerous. A subagent is a self-reporting system. It may claim to have uploaded a file, validated a link, or verified a claim, and be wrong. The parent agent must treat subagent summaries as unverified assertions, not established facts. Chen et al. (2026) documented a related risk in multi-step reasoning chains: errors introduced at one stage propagate silently through subsequent stages, and the final output can be confidently wrong without any visible signal of the upstream failure. The same dynamic applies to agent delegation. If a subagent misidentifies a working link as broken, and the parent agent acts on that claim without verification, the site audit produces a false positive and the fix may break something that was fine.

I have developed a simple rule: delegate mechanical verification tasks, but keep judgment tasks close. Let a subagent run the link checker and return a list of URLs with their status codes. But do not let a subagent decide which broken links matter. Let a subagent draft a section. But review it yourself before it goes into the final document.

This mirrors a principle from software engineering: you can parallelize execution, but you cannot parallelize design review. The conductor still decides the tempo.

## The Cron Dimension: Autonomous Work

The cron scheduler is where the agent stops being a responsive tool and starts being an autonomous system. A cron job is a self-contained prompt that fires on a schedule. The agent wakes up, loads any attached skills, executes the task, and delivers the result.

My site audit runs every Monday night. It builds the Hugo site, checks for broken links, reviews the content security policy, verifies Hugo is current, and writes a report. I do not have to ask for it. I just find the report in my inbox on Tuesday morning.

This changes the relationship. The agent is no longer something I invoke. It is something that works while I am not watching. That demands a different kind of trust — not trust in correctness, but trust that failures will be reported rather than hidden.

## The Limits Remain

None of this changes the fundamental limitation I described in the first essay. The agent has no stake in the truth of what it produces. It can be confident and wrong. It can build a plausible argument from false premises. It can verify a link as working and miss that the page content has changed entirely. It can write a skill that encodes an approach that worked once but does not generalize.

The optimal use of the tool requires constant vigilance about this limitation. Amershi et al. (2019), in Microsoft's guidelines for human-AI interaction, identified this as a core design principle: AI systems should make clear when their output is uncertain, and should defer to human judgment for high-stakes decisions. But the responsibility runs both ways. The system must signal its uncertainty, and the human must receive the signal. If you outsource your judgment, you have not optimized your use of the tool. You have abdicated.

But if you hold the judgment and let the tool handle the execution — the repetitive checks, the mechanical conversions, the scheduled reminders, the parallel research — something shifts. You find yourself thinking at a higher level of abstraction. Instead of asking "did I check all the links?", you ask "is the site healthy this week?" Instead of asking "how do I convert this cover image?", you ask "are the book covers current?" The tool handles the how. You handle the whether and the why.

## What This Means for Writing

I said in the first essay that AI does not replace the writer. It holds the lantern while the writer finds the path. With Hermes, the lantern has become a headlamp, a map, a compass, and a small research team. But the path is still mine to find. Seeber et al. (2020) argued that the most productive framing for AI in collaborative work is not "tool" or "assistant" but "teammate" — an entity with complementary strengths that requires trust, clear role definition, and accountability. That framing captures something important. A teammate can do things you cannot, but you do not abdicate your responsibility to a teammate. You work with them.

The optimal use of the tool is not to maximize what it does but to maximize what you can think about while it does the rest. If you spend the time you save on more thinking, more questioning, more revising, more connecting — the tool pays for itself in depth. If you spend the saved time on distraction, the tool is just a faster way to produce shallower work.

I do not use Hermes because it lets me write more. I use it because it lets me think better. The writing is the evidence of the thinking. The tool handles the scaffolding so I can reach higher. But I still have to climb.

## Sources

- Amershi, S., Weld, D., Vorvoreanu, M., Fourney, A., Nushi, B., Collisson, P., Suh, J., Iqbal, S., Bennett, P. N., Inkpen, K., Teevan, J., Kikin-Gil, R., & Horvitz, E. (2019). Guidelines for human-AI interaction. In *Proceedings of the 2019 CHI Conference on Human Factors in Computing Systems* (CHI '19). https://doi.org/10.1145/3290605.3300233
- Chen, S., Sritharan, N., Wen, X., Zhang, C., Wang, X., & Wang, Y. (2026). When the chain breaks: Interactive diagnosis of LLM chain-of-thought reasoning errors. *arXiv preprint arXiv:2603.21286.* https://arxiv.org/abs/2603.21286
- Dellermann, D., Ebel, P., Söllner, M., & Leimeister, J. M. (2019). Hybrid intelligence. *Business & Information Systems Engineering, 61*(5), 637–643. https://doi.org/10.1007/s12599-019-00595-2
- Nous Research. (2026a). *Hermes Agent* [Computer software]. GitHub. https://github.com/NousResearch/hermes-agent
- Nous Research. (2026b). *Hermes Agent documentation.* Retrieved May 21, 2026, from https://hermes-agent.nousresearch.com/docs/
- Packer, C., Fang, V., Patil, S. G., Lin, K., Wooders, S., & Gonzalez, J. (2023). MemGPT: Towards LLMs as operating systems. *arXiv preprint arXiv:2310.08560.* https://arxiv.org/abs/2310.08560
- Park, J. S., O'Brien, J., Cai, C. J., Morris, M. R., Liang, P., & Bernstein, M. S. (2023). Generative agents: Interactive simulacra of human behavior. In *Proceedings of the 36th Annual ACM Symposium on User Interface Software and Technology* (UIST '23). https://doi.org/10.1145/3586183.3606763
- Seeber, I., Bittner, E., Briggs, R. O., de Vreede, T., de Vreede, G.-J., Elkins, A., Maier, R., Merz, A. B., Oeste-Reiß, S., Randrup, N., Schwabe, G., & Söllner, M. (2020). Machines as teammates: A research agenda on AI in team collaboration. *Information & Management, 57*(2), 103174. https://doi.org/10.1016/j.im.2019.103174
- Shinn, N., Cassano, F., Gopinath, A., Narasimhan, K., & Yao, S. (2023). Reflexion: Language agents with verbal reinforcement learning. In *Advances in Neural Information Processing Systems*, 36. https://arxiv.org/abs/2303.11366
- Wang, G., Xie, Y., Jiang, Y., Mandlekar, A., Xiao, C., Zhu, Y., Fan, L., & Anandkumar, A. (2023). Voyager: An open-ended embodied agent with large language models. *arXiv preprint arXiv:2305.16291.* https://arxiv.org/abs/2305.16291
- Wu, Q., Bansal, G., Zhang, J., Wu, Y., Li, B., Zhu, E., Jiang, L., Zhang, X., Zhang, S., Liu, J., Awadalla, A. H., White, R. W., Burger, D., & Wang, C. (2023). AutoGen: Enabling next-gen LLM applications via multi-agent conversation. *arXiv preprint arXiv:2308.08155.* https://arxiv.org/abs/2308.08155
