---
title: "Golden Gate: The Mac Just Crossed Its Own Bridge"
description: "macOS 27 Golden Gate shipped today, the first macOS that runs only on Apple silicon. Intel Macs are done, Siri was rebuilt from scratch, and the Mac crossed the same bridge it started building in 2020. The gate is a good place to stop and look at both shores."
date: 2026-09-15T07:30:00-05:00
author: Philip Huffman
lastmod: 2026-09-15T07:30:00-05:00
hero_desktop: "img/articles/79-golden-gate_16x9.webp"
hero_mobile: "img/articles/79-golden-gate_4x5.webp"
hero_alt: "Two weathered pillars of white Parian marble standing in dark water, a band of glowing gold light stretching between them on the horizon, sparse golden dust in a deep midnight navy sky."
hero_caption: "Every threshold is a place where the old current and the new current meet."
tags:
  - technology
  - essays
  - apple
  - ai
draft: false
---

Yesterday, Apple released macOS 27. Golden Gate. It is the first version of macOS that will not run on a single Intel Mac, and it is the last with full Rosetta 2 support, the translation layer that let Apple silicon Macs run Intel software.[^1] Four machines that supported the previous release were dropped flat: the 16-inch MacBook Pro from 2019, the 13-inch MacBook Pro from 2020, the 2020 iMac, and the Intel Mac Pro from 2019.[^2] If you are reading this on one of them, yesterday was the day the current stopped.

The name is not a metaphor Apple chose casually. Golden Gate is the strait between San Francisco and the Marin Headlands, the passage where the bay meets the Pacific.[^3] And the same name, spelled without a space, was the internal codename for macOS Big Sur, the release that shipped the very first Apple silicon Macs in late 2020.[^4] Apple built its own chips, crossed the strait, and six years later named the other shore after the water in between.

## The first crossing

The Mac has crossed this water once before, in the other direction. In January 2006, at Macworld in San Francisco, Steve Jobs introduced the first Intel-based Macs, the iMac and the MacBook Pro.[^5] The PowerPC era ended quietly. Developers recompiled, users upgraded, and an entire architecture went out to pasture without a funeral.

The transition off Intel was announced in June 2020 by Tim Cook, who called it "a historic day for the Mac," and it moved fast even by Apple's own plan.[^6] The M1 shipped before the end of 2020, six months after the announcement, and the mainstream lineup was on Apple silicon within two years. The Mac Pro, the last Intel holdout, got its Apple silicon version in June 2023, the date Apple itself marked as completing the transition.[^23] Last year Apple said Tahoe would be the last version to run on Intel hardware, and yesterday was the day that promise was kept.[^2]

Rosetta 2 is the reason the end of Intel support has been so gentle, and its phaseout is the reason the end of Intel support is real. Rosetta translates x86 instructions to Arm on the fly, and it has been quietly running old software on new chips since 2020. Golden Gate is the last version with full support.[^1] The Macs that cannot upgrade will keep working, for now, but they will stop getting new features, and the software they run will age with them. That is how architecture changes happen. Not with a bang, but with a release note.

## The assistant crossed too

The big story of Golden Gate is not the hardware cutoff. It is Siri, which Apple entirely rebuilt and renamed Siri AI, and which the company is clearly positioning as the reason to care about this release at all.[^7]

Siri AI is a generative assistant in the ChatGPT and Claude mold. It can hold back-and-forth conversations, search across your Mail, Messages, Notes, Reminders, Calendar and photos to answer questions about your own life, look at what is on your screen through Visual Intelligence, and take actions inside apps, like drafting an email or adding an event to Calendar.[^7] On the Mac it lives inside Spotlight: Command-Space now brings up a "Search or Ask" bar, and you can type or speak to the assistant right where you used to search for files.[^8] There is a dedicated Siri app that keeps your conversation history and syncs it across devices, so you can start a question on your iPhone and finish it on your Mac.[^7] A new "Write with Siri" can draft text, proofread it, or rewrite it in your own style.[^8]

The underlying models matter as much as the interface. Apple built the next generation of its Foundation Models with Google, using the technology behind Gemini.[^9] And Apple is expanding Private Cloud Compute, the system that runs heavier AI requests on servers so the data never touches Apple's ordinary cloud, to run on Google Cloud hardware with NVIDIA chips.[^9]

That is a lot of infrastructure, and Apple is charging for part of it, quietly. Image generation and similar resource-intensive features have daily usage caps, with more access tied to paid iCloud+ plans.[^10] Apple's release notes say usage limits may apply to Siri AI, the photo editing tools, Image Playground, and the AFM 3 cloud models in Shortcuts.[^11] The free tier of the new assistant is generous, but it is a meter, and it is the first time Apple has put a meter on a core system feature.

There is a genuinely strange regulatory twist in the rollout. Because of the European Union's Digital Markets Act, Siri AI is not available on iPhone and iPad in the EU, where Apple has to give third parties access to system features. On the Mac, it is available the first day.[^12] Europe's Mac users get the new assistant before Europe's iPhone users, because the DMA treats the two platforms differently. Whatever you think of the law, that inversion is a small sign of how much the AI assistant is now the product.

## The one Apple is not advertising

The most interesting Siri news is the thing Apple did not put in the keynote. Code sleuths found private frameworks in the release candidate called Model Delegation and Model Manager Services, which appear to let third-party models plug into Siri at a surprisingly deep level.[^13] In one demo, a user picked Claude from an "Ask..." menu and Siri handed the request over, then took the result back. In a second demo, a third-party model replaced Apple's own server-side Siri model entirely, receiving Apple's planner prompt and tool definitions, making system calls, and answering in Siri's own interface.[^13]

The caveats are real. The "Ask..." menu currently ships only with the ChatGPT extension, Claude is not actually enabled, and Apple has not opened the model-delegation entitlement to third parties.[^13] This is plumbing, not a feature you can use today. But it is the direction. Apple spent the last year being sued and regulated over the App Store, and the same pressure that opened payments and browsers is now reaching the assistant. Apple is building Siri so that, at the code level, it can be a host for other people's models. Whether that is a concession to the DMA or a strategic retreat to being the interface rather than the brain, it is the biggest single fact about the future of the Mac that Apple mentioned today only by not mentioning it.[^13]

## The rest of the release

The rest of Golden Gate is a refinement release, in the good way. Liquid Glass gets a transparency slider, so the frosted-glass look can be dialed from ultra-clear to a fully tinted, more legible version. Toolbars are uniform across apps, sidebars are edge-to-edge instead of floating, sidebar icons are colored again, and the over-rounded corners of Tahoe are gone.[^14] The wallpapers include a Golden Gate Sunset and a Golden Gate Night, which animate when you unlock the Mac and double as screen savers.[^15]

Safari groups your tabs into topics automatically, can watch a page for changes and notify you when a price drops or something restocks, and lets you describe an extension in plain language and have one generated for you.[^16] Photos gets significantly better AI editing: Clean Up is better at removing objects, Extend expands a photo's borders with generative fill, and Reframe uses the spatial data in photos to change the perspective after the fact.[^17] Mail search was rebuilt to rank by relevance and intent instead of keywords and recency.[^18] The Home app can summarize its own security footage, and HomeKit Secure Video now supports 4K.[^19]

There are new parental controls worth a look even if they are not your problem. Ask to Browse requires a child to request permission before visiting a new website, Communication Safety now blurs gore and violence in addition to nudity, and Time Allowances let parents cap entire categories of apps, with schedules per time of day.[^16][^20]

Performance gets the expected bump: faster AirDrop, faster network file browsing, and better ultrawide display support, including 5K at 120Hz, with window positions remembered across display swaps.[^21] New Mac mini and Mac Studio models ship September 22 with Golden Gate installed.[^22]

## What the gate actually is

Strip away the features and the release has one plot. The Mac that ran the old architecture is gone, and the assistant that could not hold a conversation is gone, and both went out the same gate, in the same year, on the same software release.

The comparison is the point. It took Apple only three years to move the Mac from Intel to its own silicon, and the transition worked because the software kept running through Rosetta. Now the machine is a reasoning machine. Siri AI is not a better command parser. It is the first assistant that can read your own files and act, and it is being positioned next to the same models the labs are building, with the plumbing to let them in.

The reason to think about the gate with some care is that both of its shores are moving. The hardware threshold closed yesterday, quietly, for four Mac models. The assistant threshold is still open, and Apple is still building the road to it. If you are the kind of person who holds onto a machine until it stops getting updates, this is what the end of that feels like. And if you are the kind of person who wonders where the next generation of the Mac is going, the answer is in the direction everyone can now see: the Mac is becoming the thing you talk to. The gate is not just a strait. It is the direction of travel.

Think clearly. Live intentionally. Love deeply.

---

## Notes

[^1]: Wikipedia. (2026). macOS Golden Gate: "It is the first version of macOS to run exclusively on Macs with Apple silicon and the last version with full Rosetta 2 functionality." Announced June 8, 2026 at WWDC 2026, released late 2026; macOS 27 released to the public September 14, 2026 per MacRumors and Apple. https://en.wikipedia.org/wiki/MacOs_Golden_Gate

[^2]: Christoffel, R. (2026, June 8). macOS Golden Gate: Here's the list of Macs compatible with the update. 9to5Mac. Four Macs that supported Tahoe are dropped: MacBook Pro (16-inch, 2019), MacBook Pro (13-inch, 2020, Four Thunderbolt 3 ports), iMac (2020), Mac Pro (2019). Apple announced at WWDC 2025 that Tahoe would be the last version supporting pre-Apple-silicon Macs. https://9to5mac.com/2026/06/08/macos-golden-gate-heres-the-list-of-macs-compatible-with-the-update/

[^3]: Wikipedia. (2026). macOS Golden Gate: "It is named after the Golden Gate, a strait between the Presidio of San Francisco and the Marin Headlands, which connects the San Francisco Bay and the Pacific Ocean." https://en.wikipedia.org/wiki/MacOs_Golden_Gate

[^4]: Wikipedia. (2026). macOS Golden Gate: "The name 'Golden Gate' (specifically 'GoldenGate', no spaces) was also previously used as the internal code name for macOS Big Sur." Big Sur shipped the first Apple silicon Macs in November 2020. https://en.wikipedia.org/wiki/MacOs_Golden_Gate

[^5]: Apple Newsroom. (2006, January 10). Apple Unveils New iMac with Intel Core Duo Processor and Apple Introduces MacBook Pro. The first Intel-based Macs were introduced at Macworld San Francisco. https://www.apple.com/newsroom/2006/01/10Apple-Unveils-New-iMac-with-Intel-Core-Duo-Processor/ ; https://www.apple.com/newsroom/2006/01/10Apple-Introduces-MacBook-Pro/

[^6]: Apple Newsroom. (2020, June 22). Apple announces Mac transition to Apple silicon. Tim Cook: "Today we're announcing our transition to Apple silicon, making this a historic day for the Mac." The first Apple silicon Mac shipped by year's end; the transition was to complete "in about two years." https://www.apple.com/newsroom/2020/06/apple-announces-mac-transition-to-apple-silicon/

[^7]: MacRumors Staff. (2026, September 14). macOS Golden Gate: Everything We Know. Siri AI is an overhauled Siri using generative AI models; it holds conversations, uses personal context across Mail, Messages, Notes, Reminders, Calendar, and can take app actions; the Siri app syncs conversations across devices via iCloud; Apple's next-generation Foundation Models were developed in collaboration with Google using Gemini technology; Private Cloud Compute is expanding to Google Cloud with NVIDIA hardware. https://www.macrumors.com/roundup/macos-27/

[^8]: Apple. (2026). macOS 27 Golden Gate (official page). Spotlight's Search or Ask lets you type or talk to Siri AI; Write with Siri generates drafts, corrects grammar, and matches your style in Messages and Mail. https://www.apple.com/os/macos/

[^9]: MacRumors Staff. (2026, September 14). macOS Golden Gate: Everything We Know. "Apple used the technologies behind the Gemini AI models to develop the next generation of Apple Foundation models." Private Cloud Compute is expanding to run Apple Intelligence workloads on Google Cloud using NVIDIA hardware. https://www.macrumors.com/roundup/macos-27/

[^10]: MacRumors Staff. (2026, September 14). macOS Golden Gate: Everything We Know. "Image generation and similar resource-intensive AI features will have daily usage caps with more access tied to paid iCloud+ plans, but Apple's AI features will be otherwise free." https://www.macrumors.com/roundup/macos-27/

[^11]: Apple. (2026, September 9). macOS 27 release notes, quoted in full by Christoffel, R., 9to5Mac: "Usage limits may apply for some Apple Intelligence features, including but not limited to Siri AI, Intelligent Photo Editing Tools, Image Playground and AFM 3 Cloud models in Shortcuts." https://9to5mac.com/2026/09/09/macos-27-golden-gate-here-are-apples-full-release-notes/

[^12]: MacRumors Staff. (2026, September 14). macOS Golden Gate: Everything We Know. "Siri AI is available in English... Unlike on the iPhone and iPad, Siri AI is available on the Mac in the European Union, so EU Mac users avoid the Digital Markets Act delay. Siri AI and the new Apple Intelligence features are not available in China." https://www.macrumors.com/roundup/macos-27/

[^13]: Hardwick, T. (2026, September 14). Apple's Siri AI Can Be Swapped Out for Claude, ChatGPT, Code Shows. MacRumors. Code sleuth "pdfu" found Model Delegation and Model Manager Services in the iOS 27 / macOS Golden Gate release candidate; a demo showed Claude as a Siri extension in the "Ask..." menu; a second protocol allows a third-party inference provider (e.g. GPT-5.6) to replace Apple's server-side Siri model. The "Ask..." menu currently ships with only the ChatGPT extension; the entitlement is not open to third parties. https://www.macrumors.com/2026/09/14/siri-can-be-swapped-out-for-chatgpt-claude/

[^14]: MacRumors Staff. (2026, September 14). macOS Golden Gate: Everything We Know. Design changes: Liquid Glass slider under System Settings > Appearance; uniform toolbars; same corner radius across apps; edge-to-edge sidebars; colored sidebar icons; "the super rounded corners that people disliked in macOS Tahoe are gone." https://www.macrumors.com/roundup/macos-27/

[^15]: MacRumors Staff. (2026, September 14). macOS Golden Gate: Everything We Know. "Apple added Golden Gate Sunset and Golden Gate Night options featuring the Golden Gate Bridge in San Francisco, California, along with a version-specific abstract wallpaper. The new wallpapers animate when unlocking the Mac and can be set as screen savers." https://www.macrumors.com/roundup/macos-27/

[^16]: Apple. (2026). macOS 27 Golden Gate (official page). Safari tabs automatically grouped by topic; Notify Me monitors pages for changes; Describe an Extension creates custom extensions; child safety features (Ask to Browse, Time Allowances, Schedules). https://www.apple.com/os/macos/

[^17]: Apple. (2026). macOS 27 release notes, quoted in full by 9to5Mac: "Use intelligent photo editing tools to reframe a photo after it's been taken with Spatial Reframing or expand your shot with the Extend tool. And enhancements to Clean Up let you remove distractions with better quality and more realistic infill, even when the scene is complex." https://9to5mac.com/2026/09/09/macos-27-golden-gate-here-are-apples-full-release-notes/

[^18]: MacRumors Staff. (2026, September 14). macOS Golden Gate: Everything We Know. "macOS Golden Gate has an overhauled search system that extends to the Mail app. Instead of surfacing results based on keywords and recency, the Mail app search ranks results by relevance and intent." https://www.macrumors.com/roundup/macos-27/

[^19]: MacRumors Staff. (2026, September 14). macOS Golden Gate: Everything We Know. Home app generates AI summaries of motion alerts and can stitch footage from multiple cameras; HomeKit Secure Video supports 4K. https://www.macrumors.com/roundup/macos-27/

[^20]: MacRumors Staff. (2026, September 14). macOS Golden Gate: Everything We Know. "Communication Safety is being updated to blur gore and violence in Messages and FaceTime calls by default for users under 18." Time Allowances manage time in Entertainment, Games, and Social Media categories with schedules. https://www.macrumors.com/roundup/macos-27/

[^21]: Apple. (2026). macOS 27 Golden Gate (official page). "Now you can get higher resolutions on ultrawide displays, such as 5K at 120Hz. And your display arrangements stay exactly as you left them." AirDrop and network file browsing are faster per Apple and MacRumors. https://www.apple.com/os/macos/

[^22]: MacRumors Staff. (2026, September 14). macOS Golden Gate: Everything We Know. "Apple is releasing new Mac mini and Mac Studio models on September 22, and the machines will ship with macOS Golden Gate installed. The update was released to the public on September 14." https://www.macrumors.com/roundup/macos-27/

[^23]: Apple Newsroom. (2023, June 5). Apple unveils new Mac Studio and brings Apple silicon to Mac Pro. "The new Mac Pro ... completes the Mac transition to Apple silicon." The M2 Ultra Mac Pro was announced at WWDC 2023 and available June 13, 2023. https://www.apple.com/newsroom/2023/06/apple-unveils-new-mac-studio-and-brings-apple-silicon-to-mac-pro/

---

*PRH | [huffmanwrites.org](https://www.huffmanwrites.org/) | © Philip Huffman*
