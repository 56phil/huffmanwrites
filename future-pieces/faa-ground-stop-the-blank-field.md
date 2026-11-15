---
title: "The Blank Reason Field"
description: "The order that stopped every departure in the country carried no stated cause, and the cause that emerged two days later was a scheduling decision nobody had integrated."
date: 2026-11-16T07:00:00-06:00
author: Philip Huffman
lastmod: 2026-11-16T07:00:00-06:00
draft: true
featuredOnHome: true
hero_desktop: "img/articles/161-blank-reason-field_16x9.webp"
hero_mobile: "img/articles/161-blank-reason-field_4x5.webp"
hero_alt: "A standing slab of white marble, its face ruled with fine horizontal grooves like the empty rows of a ledger, with one shallow rectangular niche low on the face glowing with warm amber light, set against deep midnight-navy darkness."
hero_caption: "The order named no cause. The page kept the space for one, and the light found it first."
tags:
  - civics
  - essays
  - aviation
---

At 3:54 p.m. Eastern on Friday, November 13, the Air Traffic Control System Command Center issued Advisory 111.

> EVENT TIME: 13/2053 - 14/0400 DUE TO EXTRAORDINARY CIRCUMSTANCES AND FOR REASONS OF SAFETY. ATTENTION ALL AIRCRAFT OPERATORS, BY ORDER OF THE FEDERAL AVIATION COMMAND CENTER ALL AIRPORTS ARE GROUND STOPPED. ALL DEPARTING TRAFFIC SHOULD REMAIN GROUND STOPPED UNTIL FURTHER NOTICE.[^1]

The document that stopped every departure in the United States has no reason field. It has no remarks field. Its only causal language is the boilerplate, and the order is signed 20:54Z against an event window that opens at 20:53Z and closes at 04:00Z on the 14th. "Until further notice" was bounded by a four-hour horizon, written into the order itself.

Four hours and twenty-five minutes later, by the Command Center's own two signatures, Advisory 005 cancelled it:

> REMARKS: THE FAA COMMAND CENTER NATIONWIDE GROUND STOP HAS BEEN CANCELLED.
>
> SIGNATURE: 26/11/14 01:19[^2]

This time the reason field is present. It is blank.

I want to start there, because the blank is not a clerical slip and it is not a cover-up. It is the most accurate thing either document says. At 3:54 p.m. the agency knew that its communications with aircraft had become untrustworthy and it acted. At 8:19 p.m. it judged the immediate fault contained and it lifted the order. Both decisions were correct, both were made in motion, and neither could yet name a cause. A safety system behaves exactly this way. It stops first and explains later.

The explanation came on Saturday morning, and it is the part worth sitting with, because it moves the event out of the category of accident and into the category of schedule.

The scale arrived later, and it is worth one paragraph because it is the only part of the story that was measured honestly throughout. By Friday's close, FlightAware counted 9,201 US cancellations and 7,468 delays. Saturday added 6,692 and 8,689, as airlines rebuilt schedules nobody had planned. Through the evening the delay count had fallen while cancellations climbed, which is what converting a queue into a schedule looks like: fewer aircraft waiting, more aircraft not going.[^21]

## What filled the blank

At a briefing on November 14, Transportation Secretary Sean Duffy and FAA Administrator Bryan Bedford described a maintenance action at a remote FAA facility. A contractor was converting a telecommunications link from copper to fiber. The equipment involved began, in Duffy's description, "flooding other routers in our air traffic control system," at a rate of "over 1,000 connection attempts every four to five seconds," which produced "issues with our communication with airplanes" and "some disruption with our radar feeds."[^3]

The contractor is L3Harris, which operates the FAA Telecommunications Infrastructure network, the FTI, under a contract awarded in 2002 to Harris Corporation and held since. Its own programme page advertises "4,400+ facilities," "29,000+ telecommunications services," and an availability of 99.99971 percent.[^4]

The scope of the overload, according to ABC's Australian service, was seventeen of the agency's twenty-two en route centers.[^5] No facility went dark. The stop was ordered on instability in the information feeds to the centers, which is a different thing from a link failure and, as it happens, a harder thing to see.

The government has not chosen between three candidate faults. Duffy put it as a question: "whether we had incompetence, meaning was it user error or install error from L3Harris or did they install a faulty router?"[^3] L3Harris said it is "supporting the FAA in its investigation to understand the conditions that led to the Nov. 13 ground stop," and that it has "completed more than 70% of the planned airspace communications conversion from legacy copper wires to a fiber optic system."[^4]

Two days after the outage, on November 15, the FAA had still published no root-cause report. What it has published is a paragraph marked "preliminary and subject to change."[^6] That is not a scandal. It is a normal interval, and the interval is where the rest of this essay lives.

## Why one device could do that

The instinctive reading is that the network should have been built to survive a misbehaving router. It is worth being precise about why that reading does not work as stated, because it is the reading most people will bring.

FTI is built for path failure. The company describes a "dual private Metro Ring solution" with "optical carrier protection switching across diverse telecommunications ingress and egress" at twenty centers, plus a multi-carrier last mile.[^4] On the night in question that architecture performed as advertised: no facility lost its links. Redundancy is a statement about paths. What happened was a statement about participants. One device spoke, repeatedly and wrongly, into peers that believed it, and every alternate path led to the same speaker.

The controls that bear on that failure are a different family: control-plane rate limiting, route dampening, prefix limits, out-of-band management so that a flooding device can be reached and shut down without traversing the path it is flooding. Whether the legacy equipment at a remote FAA site supports any of them is not answered by any document the public holds, and I am not going to assume it is. The honest sentence is narrower than the one people want: the system that failed was the system designed to be redundant, and redundancy answered a question the failure did not ask.

What is documented is the detection gap. Bedford said officials could not identify the cause "for about 45 minutes."[^3] The circuits were up. The devices were up. The device was the fault. A monitoring regime built on availability reports a healthy network in exactly that state, which suggests the operator's proudest number is also the least informative one here.

An availability figure of 99.99971 percent is a true sentence about the wrong quantity. A network can be perfectly available and perfectly wrong.

## The protocol that was not followed, if the union is right

There is a process fact in this record, and it comes from a party with an interest, so it gets stated as such.

The union representing about 11,000 FAA employees, the Professional Aviation Safety Specialists, issued a statement the day after the outage:

> "Historically, contractors have followed a protocol where FAA employees conduct a risk assessment and coordinate the maintenance of the system or equipment. PASS-represented technicians were not involved in the upgrades that led to the ground stop yesterday."[^7]

No fetched page shows the FAA agreeing or disputing that. The union is describing its own exclusion, which gives it a motive to describe it. The claim is also specific, falsifiable, and about a control rather than a component, and if it is right it is the most consequential sentence in the file: a maintenance action on the network that carries the airspace proceeded without the agency's own technicians assessing the risk, under a protocol that ordinarily requires their participation.

A risk assessment is not a formality. It is the step where somebody asks what happens if this goes wrong at this site at this hour, and somebody else has to answer. The absence of that step does not cause a router to flood. It causes nobody to have asked whether the hour was right.

## Eleven thousand three hundred and eighty-nine schedules

On September 14, 2026, two months before the outage, the Government Accountability Office delivered a report to a House Oversight subcommittee on the FAA's modernisation effort. The report's central finding is a scheduling fact, and it reads like a prediction that arrived on time:

> "FAA has not developed an integrated master schedule for phase 1. Instead, FAA has 11,389 individual project schedules that are not integrated. As a result, individual projects are scheduled for installations at the same sites, generally without optimizing the schedules to reduce impacts to controller operations."[^8]

The report names the consequence in its own words: this "could lead to more system outages, ground stops, flight delays, and safety incidents."[^8]

The dates matter as much as the finding. An integrator delivered a preliminary master schedule in April 2026. As of May 2026 the schedules were still unintegrated, because FAA officials told GAO that integrating them "would not be useful or helpful." A tool to optimize them was in testing, with no business rules and no implementation date.[^8]

Set that beside the number the contractor and the Secretary both cite. Of 5,170 copper connections to be replaced, 2,560 were done as of May 2026, which is 49.5 percent.[^8] The company's tracker read 70 percent of sites upgraded as of November 2. A letter the administration sent to Congress on November 12 said 68 percent.[^9] Three figures, three dates, one trend, and no agreement. Half the copper was in the ground six months before the outage, by the agency's own count.

A conversion programme of that size, running at that pace, across sites nobody had scheduled together, is not a series of independent maintenance actions. It is a single process executed 5,170 times, and the report says the process was never sequenced to protect the operation it runs under.

## The same network, seventeen years ago

None of this is the first time.

On November 19, 2009, "129 of the Nation's air traffic facilities experienced an outage of the Federal Aviation Administration's telecommunications," which delayed thousands of travelers and grounded hundreds of flights. The Inspector General's letter the following June found "network configuration and procedural errors by the contractor caused the FTI outage, which blocked approximately 75 percent of the FTI network traffic and delayed service restoration for 5 hours." It added a sentence that has aged badly: "FAA's oversight of FTI and Harris was not as effective as it should have been."[^10]

Same network. Same contractor lineage. A configuration error, not a hardware failure, and a five-hour restoration.

Then the closest precedent of all, and the one that removes any claim of unforeseeability. On July 3, 2025, the FAA announced that it had "successfully transitioned to a brand-new fiber optic communications network between New York and the Philadelphia Terminal Radar Approach Control," adding: "This upgrade significantly enhances resiliency with new fiber optic connections on two separate communications paths, ensuring equipment will continue to operate if one path is disrupted."[^11]

On September 21, 2026, both paths were unavailable at once. One failed; a construction crew cut the other.[^12] The agency published the promise in July 2025 and, fourteen months later, published the failure of the exact property promised.

## What the money was doing

In July 2025, Congress appropriated $12.52 billion for air traffic control modernisation. The largest single line item, $4.75 billion, was for "telecommunications infrastructure modernization and systems upgrades."[^13] That is the category of equipment that failed on November 13, funded to the tune of nearly five billion dollars sixteen months earlier.

Two things about the statute are worth holding together. It appropriates nothing for salaries, hiring, or retention: the money is for facilities and equipment, and the $100 million training line buys simulators rather than trainees. The House had approved $1 billion for controller recruitment; the conference stripped it, and the bill passed 218 to 214. The White House fact sheet nonetheless described the act as addressing "the more than 3,000-controller shortage by investing in recruitment, retention, and advanced training technologies."[^13] The statute does not appropriate a dollar for recruitment or retention. That is not an interpretation. It is a signed public law beside a press release describing it.

The second thing is a coincidence of the calendar that reads like a joke with no punch line. On Thursday, November 12, the Director of the Office of Management and Budget and the Transportation Secretary sent Congress a letter requesting $30.1 billion more, including $10.1 billion for air traffic control modernisation. Their own words for what it would buy: "a resilient telecommunications backbone for air traffic controllers."[^9] The letter was sent the day before the backbone failed. It was reported the same day the airspace closed.

The next day, at the briefing, Duffy raised the figure to $50 billion. Four outlets carry it; Roll Call notes that officials "didn't fully flesh out" the increase, and that the new number is $19.1 billion above the letter they had signed two days earlier. He said it on Newsmax in the cleanest formulation available: "the president has asked for $30 billion. I want $50 billion."[^14]

He said it. Nothing was filed.

## What this does not license

Three claims are available and I am refusing all three.

The first is that DOGE caused this. No fetched source ties the episode to the outage, and the documents now point elsewhere. The FTI contract predates DOGE by twenty years. The $12.5 billion came from Congress, went to equipment, and passed with the House's $1 billion recruitment line removed. The Verge's own assessment, published in August 2026, is that DOGE "did not help the FAA buy or implement any major system upgrades," and that "none of the $12.5 billion … goes toward personnel."[^15] The failure the Secretary describes is an install or equipment fault at one site. The strongest causal document in the file, GAO's September report, is a finding about how a modernisation programme is managed.

The one channel that stays open runs through duration rather than cause. The agency's own maintenance workforce plan says it is "currently unable to staff all shifts at 67 facilities," that technicians averaged 115 hours of overtime each in fiscal 2025 "fixing aging equipment," and that "staffing shortfalls have resulted in longer restoration times."[^16] Longer restoration times is a description of the four hours and change, and of the forty-five minutes spent finding a device that was broadcasting its own fault. That is a real finding and it is not the same as saying the outage was caused by a reduction in headcount, which no document shows.

The second refused claim is that better redundancy would have contained this. I have explained why the record does not establish that, at least not for the redundancy the network has. Saying otherwise is an engineering assertion about equipment nobody outside the agency has inspected.

The third is that the cause is known. The Secretary offered three candidate faults in one breath and the agency has published a paragraph marked preliminary. A piece that picks the tidier of the two is picking a side in a dispute that the investigation has not settled.

## The recovery, as the government filed it

The most under-read part of this story is in the same advisory index, after 01:19Z.

Every ground stop still in place over the next hours is requested by an airline for its own flights. United at O'Hare and Newark. Delta at Minneapolis. Alaska at Los Angeles, San Diego, Seattle. The words "AIRLINE REQUEST" are printed in the advisory's own comments field.[^17] The national airspace reopened and the airlines then held their own aircraft on the ground, one carrier at a time, because their crews and airplanes were in the wrong cities.

That is the queue being converted into a schedule, done by the parties that owned the schedules. It was not free. American offered flight attendants extra pay to pick up trips; Delta offered double pay and confirmed seats to reposition crews; United offered premium pay through Sunday.[^18] The recovery was bought from people who had already worked a day they did not plan.

Passengers, meanwhile, hold waivers rather than compensation. Carriers owe a refund where a flight is cancelled and the passenger chooses not to fly. A failure caused by the government triggers no duty of care, and no rule converts four lost hours into a payment. American extended its travel alert through November 18 and capped fares on some routes. That is the whole of what a passenger is owed, and anyone who tells you the airline will look after you is describing a courtesy rather than a right.[^18]

## The next one

Duffy was asked whether this exact thing would happen again. He said: "I don't — I don't know that this exact scenario will happen." Speaking to CBS, he said something more useful: "you will have more of these. You will have more of them unless the American people and the Congress tell us to build."[^19]

Both answers are honest. The second is the one that will be quoted, and it should be, because it is the only forward-looking statement in the record that anyone has made without hedging.

What the record does not contain is any answer to the question the next conversion raises. The Secretary said there would be "a reevaluation of when we do this work." No document says what the reevaluation will consist of, whether the agency's own technicians will assess the risk this time, or whether the remaining copper connections will be converted under a schedule that has been integrated. The advisory index for November 15 carries operations plans, launch-window restrictions, and five volcanic-activity bulletins. It carries no national stop, which is the good news, and no answer to any of those questions, which is the ordinary news.

The Thanksgiving travel period opens on Friday. Airlines for America projects nearly 29 million passengers between November 20 and 30, with the busiest days on the 29th and 30th, and carriers have added 38,000 seats a day over last year to carry them.[^20] That is the test the schedule will now face, and it is a fairer test than any hearing, because a network either holds under that load or it does not, and no one has to interpret the result.

The blank reason field is the honest artifact of this whole affair. At 3:54 p.m. the agency stopped the country and could not say why, and at 8:19 p.m. it lifted the order and left the field empty, because the fault had been isolated but not explained. Two documents, four hours and twenty-five minutes, and no cause in either of them. What filled the blank two days later was not a villain. It was a maintenance procedure executed on a schedule nobody had put in one place, on equipment an auditor had called unsustainable for two years, with the people who normally assess the risk sitting outside the room, and a monitoring system that could see every circuit and none of the conversations.

The stop was the safety system working. The question the record leaves open is narrower and harder: whether the next conversion, and the one after that, will be scheduled by someone who can see the whole calendar at once.

Think clearly. Live intentionally. Love deeply.

---

## Notes

[^1]: Air Traffic Control System Command Center, Advisory 111, November 13, 2026, "NATIONAL GROUND STOP," sent 20:54Z. Text quoted from the advisory as published: `https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=111`. Archived copy: `http://web.archive.org/web/20261115092220/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=111`. The advisory carries no REASON field and no REMARKS field; its only causal language is "DUE TO EXTRAORDINARY CIRCUMSTANCES AND FOR REASONS OF SAFETY." The event window is `13/2053 - 14/0400`.

[^2]: Advisory 005, November 14, 2026, "CNX NATIONWIDE GROUND STOP," signature `26/11/14 01:19`, effective `140119-140200`. `https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=5`. Archived: `http://web.archive.org/web/20261114013716/https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11142026&advn=5`. The REASON field is present and empty. Of the two stop orders, only the re-issue, Advisory 120, carries a stated reason: `REASON: COMMUNICATIONS FAILURE`, with the agency's internal rendering labelling the same advisory `EQUIPMENT / OUTAGE`; `https://www.fly.faa.gov/adv/adv_otherdis?adv_date=11132026&advn=120`.

[^3]: DOT briefing, November 14, 2026, with Secretary Sean Duffy and Administrator Bryan Bedford. The department's transcript page answers 403 to this client; the wording quoted is as the department renders it and is carried by Reuters and CNBC, fetched directly. Duffy on the mechanism: "In at least one of our remote FAA locations, a contractor was doing routine maintenance to switch telecommunication lines from old copper wire and they were bringing it over to fiber. That contractor that does the work for us is L3Harris"; the router "started flooding other routers in our air traffic control system"; "we had over 1,000 connection attempts every four to five seconds." Bedford on detection: officials could not identify the cause "for about 45 minutes," and "no FAA facilities went dark." The causal question is rendered two ways: DOT has "user error or install error from L3Harris or did they install a faulty router"; CNBC has "user error, installator error from L3 Harris, or did they install a faulty router." Quote with the outlet named.

[^4]: L3Harris Technologies, FAA Telecommunications Infrastructure programme page and sell sheet, fetched November 15, 2026: "4,400+ facilities," "29,000+ telecommunications services," "dual private Metro Ring solution," "optical carrier protection switching across diverse telecommunications ingress and egress," availability "99.99971%"; copper-to-fiber tracker at 70 percent of sites and 5,170 connections, last updated November 2, 2026. Statement via CNBC, November 14: "We are supporting the FAA in its investigation to understand the conditions that led to the Nov. 13 ground stop of our nation's air travel," and "completed more than 70% of the planned airspace communications conversion from legacy copper wires to a fiber optic system." The contract is `DTFA01-02-D-03006`, awarded to Harris Corporation in July 2002, with L3Harris Technologies as parent recipient in USAspending and a potential end date of September 30, 2027.

[^5]: ABC News (Australia), November 15, 2026: the overload affected "17 of the FAA's 22 en route centres." The FAA's own statement says "multiple Air Route Traffic Control Centers"; Duffy's post on X said "all Air Route Traffic Control Centers." Three figures for one quantity, each printed with its source.

[^6]: FAA, "FAA Statement on Nationwide Ground Stop," November 13, 2026: "This information is preliminary and subject to change. The FAA issued a nationwide ground stop for all U.S. airports following communication issues impacting multiple Air Route Traffic Control Centers. FAA technicians are investigating the issue. We will provide updates." `https://www.faa.gov/newsroom/faa-statement-nationwide-ground-stop`

[^7]: Professional Aviation Safety Specialists statement, November 14, 2026, via ABC News. PASS represents roughly 11,000 FAA employees. The statement is the union's account of its own exclusion and is not corroborated by the FAA in any fetched page.

[^8]: U.S. Government Accountability Office, *Air Traffic Control Systems: Ambitious New Modernization Effort Needs Cost and Schedule Planning*, GAO-26-107992, September 14, 2026, to the Subcommittee on Government Operations, House Committee on Oversight and Government Reform. "FAA has 11,389 individual project schedules that are not integrated… without optimizing the schedules to reduce impacts to controller operations"; the consequence "could lead to more system outages, ground stops, flight delays, and safety incidents"; the integrator's preliminary master schedule delivered April 2026; FAA officials stating that integrating the schedules "would not be useful or helpful"; 2,560 of 5,170 copper connections replaced as of May 2026; phase 1 estimated at $10.2 billion, to be complete by December 2028. PDF: `https://download.aopa.org/advocacy/2026/2026-09_GAO-26-107992-Air-Traffic-Control-Systems.pdf`

[^9]: Letter from OMB Director Russell Vought and Secretary Duffy to Senators Collins and Murray and Representatives Cole and DeLauro, sent Thursday, November 12, 2026, reported November 13: $30.1 billion, including $10.1 billion for air traffic control modernisation, and "$7.2 billion for a common automation platform and controller workstations and $2 billion for cloud computing"; "a resilient telecommunications backbone for air traffic controllers"; and the claim that the FAA "has replaced 68% of legacy copper telecommunications network with high-speed fiber infrastructure." Via Reuters, fetched November 15.

[^10]: Department of Transportation Office of Inspector General, letter to the Administrator regarding the November 19, 2009, FTI outage, June 17, 2010: "129 of the Nation's air traffic facilities experienced an outage"; "network configuration and procedural errors by the contractor caused the FTI outage, which blocked approximately 75 percent of the FTI network traffic and delayed service restoration for 5 hours"; "FAA's oversight of FTI and Harris was not as effective as it should have been."

[^11]: FAA statement, July 3, 2025: "This morning, the FAA successfully transitioned to a brand-new fiber optic communications network between New York and the Philadelphia Terminal Radar Approach Control (TRACON)… This upgrade significantly enhances resiliency with new fiber optic connections on two separate communications paths, ensuring equipment will continue to operate if one path is disrupted."

[^12]: September 21, 2026, Philadelphia TRACON. Administrator Bedford, via NBC: "A major circuit blew at the Philadelphia facility that controls air traffic to Newark Liberty International, Teterboro and Philadelphia airports Monday," and "when it went to flip into the backup, we discovered that the backup fiber had a break." Four parties, including the FAA, Amtrak, NJ Transit and Verizon, offered four accounts of the fiber cut; none is adopted here.

[^13]: P.L. 119-21, §40003, signed July 4, 2025: $12,520,000,000 for "the acquisition, construction, sustainment, and improvement of facilities and equipment necessary to improve or maintain aviation safety," including $4,750,000,000 "for telecommunications infrastructure modernization and systems upgrades," and $100,000,000 "for air traffic controller advanced training technologies." The section contains no salary, personnel, or hiring authority. The House-passed $1 billion for controller recruitment and retention was not in the conference report; the vote was 218–214. The White House fact sheet of July 2025 states that the act "Addresses the more than 3,000-controller shortage by investing in recruitment, retention, and advanced training technologies." Text from `https://www.govinfo.gov/content/pkg/PLAW-119publ21/uslm/PLAW-119publ21.xml`; the appropriation was reported by AAAE on July 3, 2025.

[^14]: Duffy, quoted by Mediaite and ABC: "This is an emergency. I want Congress to give us emergency funding. This is bipartisan. This is American. I want $50 billion." On Newsmax, via Yahoo: "the president has asked for $30 billion. I want $50 billion." Roll Call: the administration officials "didn't fully flesh out" the increase, and the figure is "$19.1 billion higher" than the letter of November 12. The words are confirmed by four outlets; no formal request was filed.

[^15]: The Verge, August 18, 2026: DOGE "did not help the FAA buy or implement any major system upgrades," and "none of the $12.5 billion … goes toward personnel."

[^16]: FAA, *Air Traffic Controller and Maintenance Technician Workforce Plan, 2026–2030*: the agency is "currently unable to staff all shifts at 67 facilities"; technicians averaged 115 hours of overtime each in fiscal 2025 "fixing aging equipment"; "staffing shortfalls have resulted in longer restoration times and increased reliance on second level support." The shortfall the plan documents long predates the February 2025 reductions, which the plan does not mention.

[^17]: Advisory index, November 14, 2026: Advisory 011 (O'Hare, "CARRIER UAL ONLY"), 012 (Seattle, "AIRLINE REQUEST"), 014 (San Diego, "AIRLINE REQUEST MAIN AND SUBS"), 016 (Newark, "UAL AND UAL SUBS ONLY"), 017 (Minneapolis, "CARRIER DAL ONLY"), 021 (Los Angeles, "CARRIER ASA ONLY"), and 018, sent 02:24Z, whose plan states "SEVERAL GROUND STOPS ARE IN PLACE AT AIRLINE'S REQUESTS" and lists no national stop. Index: `https://www.fly.faa.gov/adv/adv_list?whichAdvisories=ATCSCC&advisoryCategory=All&date=2026-11-14&airflow=true&ctop=true&gStop=true&gDelay=true&route=true&other=true`

[^18]: CNBC, November 14, 2026, from internal messages: American offered flight attendants extra pay to pick up trips; Delta offered double pay and confirmed seats to reposition crews; United offered premium pay through Sunday. ABC News, November 15: American extended its travel alert through November 18 and capped fares on domestic and short international routes. Under US rules a carrier owes a refund where a flight is cancelled and the passenger chooses not to fly; a government-caused failure creates no duty of care.

[^19]: Duffy to reporters, via the Associated Press live page: "Is this exact thing going to happen again? … I don't — I don't know that this exact scenario will happen." Via CBS: "But you will have more of these. You will have more of them unless the American people and the Congress tell us to build."

[^20]: Airlines for America, November 10, 2026: "Airlines for America (A4A) projects U.S. airlines will carry nearly 29 million passengers over the Thanksgiving holiday travel period (November 20 – 30)," with "38,000 more seats daily, on average, than they did in 2025" and the busiest days expected to be Sunday, November 29 and Monday, November 30. `https://airlines.org/news-update/u-s-airlines-prepare-for-busy-thanksgiving-travel-period-amid-record-high-jet-fuel-costs/`

[^21]: FlightAware, fetched November 15, 2026: 9,201 cancellations and 7,468 delays on Friday, November 13; 6,692 and 8,689 on Saturday, November 14; 1,620 cancellations worldwide on Sunday. Earlier intraday snapshots counted a lower cancellation total and a higher delay total on Friday, because the queue was being converted into a schedule as the day went on. Duration is stated here by the Command Center's own two signatures, 20:54Z to 01:19Z, which is four hours and twenty-five minutes.

*PRH | [huffmanwrites.org](https://www.huffmanwrites.org) | © Philip Huffman*
