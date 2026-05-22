# APA-Citable Sources for "The Optimal Use of Hermes"

Below are formatted APA citations organized by which claim in the essay they support. Sources marked [CONFIRMED] were verified via direct API lookups. Sources marked [TRAINING] are drawn from the agent's pretraining knowledge of well-known, highly-cited academic papers.

---

## Claim 1: Hermes Agent — an open-source agent framework from Nous Research (memory, skills, delegation, cron)

**Nous Research. (2026).** *Hermes Agent documentation.* Retrieved May 21, 2026, from https://hermes-agent.nousresearch.com/docs/

- **Note:** Primary source for the tool itself. Documents the self-improving learning loop, skill system, memory persistence, subagent delegation, cron scheduling, and 70+ built-in tools. Supports the essay's description in "What the Tool Actually Is."

**Nous Research. (2026).** *Hermes Agent* [Computer software]. GitHub. https://github.com/NousResearch/hermes-agent

- **Note:** Open-source repository. Confirms the framework's open-source nature, capabilities (memory, skills, MCP integration, parallel subagents), and its origin at Nous Research. Supports paragraph 2 of the essay.

---

## Claim 2: Distinction between transactional/stateless AI and persistent/stateful AI agents

**[CONFIRMED] Packer, C., Fang, V., Patil, S. G., Lin, K., Wooders, S., & Gonzalez, J. (2023).** MemGPT: Towards LLMs as operating systems. *arXiv preprint arXiv:2310.08560.* https://arxiv.org/abs/2310.08560

- **Note:** Introduces virtual memory management for LLMs, creating persistent agents that maintain context across sessions. Directly supports the essay's contrast between stateless chatbots ("each interaction begins from zero") and stateful agents ("it remembers... across sessions"). Use in "What the Tool Actually Is" section.

**[CONFIRMED] Park, J. S., O'Brien, J., Cai, C. J., Morris, M. R., Liang, P., & Bernstein, M. S. (2023).** Generative agents: Interactive simulacra of human behavior. In *Proceedings of the 36th Annual ACM Symposium on User Interface Software and Technology* (UIST '23). https://doi.org/10.1145/3586183.3606763

- **Note:** Foundational paper demonstrating persistent AI agents with memory streams, reflection, and planning. The memory architecture (recording experiences, retrieving relevant memories, synthesizing reflections) parallels Hermes' durable memory system. Supports the claim that persistent memory transforms agent behavior ("it knows my project structure, my writing voice").

---

## Claim 3: Skills, procedural learning, and compound improvement in AI systems

**[CONFIRMED] Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2022).** ReAct: Synergizing reasoning and acting in language models. *arXiv preprint arXiv:2210.03629.* https://arxiv.org/abs/2210.03629

- **Note:** Introduces the interleaved reasoning-and-action paradigm that underpins skill-based agent workflows. The "thought-action-observation" loop maps directly to how Hermes skills encode step-by-step workflows with verification steps. Use in "The Skills Feedback Loop" section.

**[TRAINING] Wang, G., Xie, Y., Jiang, Y., Mandlekar, A., Xiao, C., Zhu, Y., Fan, L., & Anandkumar, A. (2023).** Voyager: An open-ended embodied agent with large language models. *arXiv preprint arXiv:2305.16291.* https://arxiv.org/abs/2305.16291

- **Note:** Introduces a growing skill library where the agent encodes successful behaviors as reusable code and retrieves them for future tasks — conceptually identical to Hermes' skill creation and reuse mechanism. Supports "Every time we work through a difficult task... the agent can encode what we learned. Next time, it follows the recipe instead of improvising."

**[TRAINING] Shinn, N., Cassano, F., Gopinath, A., Narasimhan, K., & Yao, S. (2023).** Reflexion: Language agents with verbal reinforcement learning. In *Advances in Neural Information Processing Systems*, 36. https://arxiv.org/abs/2303.11366

- **Note:** Describes agents that learn from feedback, record corrections, and improve iteratively — mirroring Hermes' compound learning loop ("it records the correction and does not make that mistake again"). Use in "The Limits Remain" and "The Skills Feedback Loop" sections.

---

## Claim 4: Subagent delegation pattern and its risks (compound error)

**[CONFIRMED] Wu, Q., Bansal, G., Zhang, J., Wu, Y., Li, B., Zhu, E., Jiang, L., Zhang, X., Zhang, S., Liu, J., Awadalla, A. H., White, R. W., Burger, D., & Wang, C. (2023).** AutoGen: Enabling next-gen LLM applications via multi-agent conversation. *arXiv preprint arXiv:2308.08155.* https://arxiv.org/abs/2308.08155

- **Note:** Canonical framework for multi-agent delegation — parent agents spawn subagents that work in isolated contexts and return summaries. Directly supports "Hermes can spawn subagents... to handle subtasks in parallel." Also addresses delegation patterns and trust boundaries. Use in "When to Delegate and When to Do It Yourself."

**[CONFIRMED] Chen, S., Sritharan, N., Wen, X., Zhang, C., Wang, X., & Wang, Y. (2026).** When the chain breaks: Interactive diagnosis of LLM chain-of-thought reasoning errors. *arXiv preprint arXiv:2603.21286.* https://arxiv.org/abs/2603.21286

- **Note:** Analyzes how errors propagate through multi-step LLM reasoning chains — directly relevant to the essay's warning about subagents: "A subagent is a self-reporting system. It may claim to have uploaded a file... and be wrong." Use to ground the compound-error risk in "When to Delegate."

**[TRAINING] Chase, H. (2022).** *LangChain: Building applications with LLMs through composability* [Computer software]. https://github.com/langchain-ai/langchain

- **Note:** If a software citation is appropriate: LangChain formalized the concept of chained LLM calls with tool use. Relevant as the broader ecosystem context for agent delegation patterns. Use as background for the subagent delegation discussion.

---

## Claim 5: The shift from "tool" to "autonomous system" / "editorial operation" in human-AI collaboration

**[TRAINING] Dellermann, D., Ebel, P., Söllner, M., & Leimeister, J. M. (2019).** Hybrid intelligence. *Business & Information Systems Engineering, 61*(5), 637–643. https://doi.org/10.1007/s12599-019-00595-2

- **Note:** Defines "hybrid intelligence" as the shift from AI as a passive tool to AI as a collaborative partner that augments human decision-making. Directly supports the essay's core thesis: "the mental model shift: from treating AI as a drafting assistant to treating it as an editorial operation." Use in "The Shift: From Tool to Operation."

**[TRAINING] Amershi, S., Weld, D., Vorvoreanu, M., Fourney, A., Nushi, B., Collisson, P., Suh, J., Iqbal, S., Bennett, P. N., Inkpen, K., Teevan, J., Kikin-Gil, R., & Horvitz, E. (2019).** Guidelines for human-AI interaction. In *Proceedings of the 2019 CHI Conference on Human Factors in Computing Systems* (CHI '19). https://doi.org/10.1145/3290605.3300233

- **Note:** Microsoft's foundational design guidelines for when AI systems should act autonomously vs. defer to human judgment. Supports "The agent is a staff, but you are the editor in chief" and the essay's boundary-setting: "If you outsource your judgment, you have not optimized your use of the tool. You have abdicated." Use in "The Limits Remain."

**[TRAINING] Seeber, I., Bittner, E., Briggs, R. O., de Vreede, T., de Vreede, G.-J., Elkins, A., Maier, R., Merz, A. B., Oeste-Reiß, S., Randrup, N., Schwabe, G., & Söllner, M. (2020).** Machines as teammates: A research agenda on AI in team collaboration. *Information & Management, 57*(2), 103174. https://doi.org/10.1016/j.im.2019.103174

- **Note:** Argues that AI should be treated as a teammate rather than a tool, with implications for trust, delegation, and shared mental models. Supports the "editorial operation with one human in the loop" framing and the "managing editor" role described in "The Shift." Use there or in "What This Means for Writing."

---

## Broad / Survey Sources (support multiple claims)

**[TRAINING] Xi, Z., Chen, W., Guo, X., He, W., Ding, Y., Hong, B., Zhang, M., Wang, J., Jin, S., Zhou, E., Zheng, R., Fan, X., Wang, X., Xiong, L., Zhou, Y., Wang, W., Jiang, C., Zou, Y., Liu, X., ... Gui, T. (2023).** The rise and potential of large language model based agents: A survey. *arXiv preprint arXiv:2309.07864.* https://arxiv.org/abs/2309.07864

- **Note:** Comprehensive survey covering agent architectures, memory, tool use, multi-agent collaboration, and human-agent interaction. Useful as an umbrella citation for the essay's overview of agent capabilities. Use in "What the Tool Actually Is."

**[TRAINING] Weng, L. (2023, June 23).** LLM-powered autonomous agents. *Lil'Log.* https://lilianweng.github.io/posts/2023-06-23-agent/

- **Note:** Widely-cited technical overview of the three core components of LLM agents: planning, memory, and tool use. Maps cleanly to Hermes' skill system (planning), durable memory (memory), and shell/API capabilities (tool use). Use in "What the Tool Actually Is."

---

## Implementation Notes

- All arXiv papers should be cited with their arXiv ID and the URL https://arxiv.org/abs/[ID].
- Where a paper has a published venue (e.g., CHI '19, UIST '23, NeurIPS), include both the conference proceedings and the arXiv preprint — the essay can use either.
- The Hermes Agent docs and GitHub repo are the primary sources for Claim 1. No academic paper yet exists specifically about Hermes Agent (released 2026), so the documentation itself is the citable source.
- For a "Sources" section at the end of the essay, group by theme: "Agent Architecture & Memory," "Skills & Learning," "Multi-Agent Delegation," "Human-AI Collaboration."

---

## Quick-Reference: Citation Mapping to Essay Sections

| Essay Section | Sources |
|---|---|
| What the Tool Actually Is | Nous Research (2026) docs; Park et al. (2023); Packer et al. (2023); Xi et al. (2023); Weng (2023) |
| The Shift: From Tool to Operation | Dellermann et al. (2019); Seeber et al. (2020); Amershi et al. (2019) |
| The Skills Feedback Loop | Wang et al. (2023); Shinn et al. (2023); Yao et al. (2022) |
| When to Delegate and When to Do It Yourself | Wu et al. (2023); Chen et al. (2026); Amershi et al. (2019) |
| The Cron Dimension | Nous Research (2026) docs |
| The Limits Remain | Shinn et al. (2023); Amershi et al. (2019); Chen et al. (2026) |
| What This Means for Writing | Dellermann et al. (2019); Seeber et al. (2020) |
