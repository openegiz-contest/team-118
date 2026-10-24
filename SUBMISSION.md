# SUBMISSION

<!-- Fill in every section. The AI Jury studies this file together with the code, the Build Report, the presentation and the Stand's interface. Accepted languages: English, Kazakh, Russian. These hint comments may be deleted. -->

## Concept

**Enterprise:** This digital twin represents part of JV Inkai, an in-situ uranium recovery operation in Kazakhstan. It focuses on three areas: MPP, Sat-1 and Sat-2. It also includes the area ion-exchange plants and the limit of MPP drying and packaging.

**Users:** The main user is a wellfield production planner. This person plans when new blocks should receive acid and when they can start production. A production manager is a second user. They can use the twin to compare area production and possible curtailment. The model does not represent the internal logistics system of Kazatomprom.

**Decision:** If sulphuric acid arrives later than planned, how should the planner change the acidification and start dates of new blocks? When the delivery returns to normal, in which order can the delayed blocks start without going over the plant limits? The twin will compare a few clear policies. It will not claim to find the best possible or a proven operating plan.

**Why this choice:** I have always been interested in Kazakhstan's large mineral resources. I want to use data science to study a real problem in this area. Kazatomprom reported that changes in acid delivery timing in 2024 delayed the acidification schedule of new Inkai blocks. This happened even though acid requirements were fulfilled at 106% for the first nine months. Cameco later reported 7.8 million pounds of U₃O₈ production for 2024, compared with a target of 8.3 million pounds. This makes delivery timing a useful problem to study with a digital twin. I want the model to show its assumptions and compare scenarios instead of showing simulated results as real operating facts.

**Real or fictional:** JV Inkai and its main operating details are real. This project is a representative simulation based on public sources. It is not a site-calibrated copy of Inkai. I will use public capacities and historical totals where available. Block group locations, individual block details, acid dose and duration, commissioning delays and production ramp-up are synthetic or assumed unless a source directly supports them. The map will be drawn for this project. It will not copy a published site figure.

## Team

<!-- GitHub usernames of the Participants. Other personal data are not required: the repository becomes public after the Freeze (Rules, section 15). -->

| GitHub |
|---|
|  |

## Mine

<!-- Which part of a mining enterprise the Submission represents (open pit, underground mine, processing plant…), which objects are twins in OpenEgiz, how they are related, and where they are defined in the code. -->

## Modules and What-if Scenarios

<!-- Modules: functions on top of the twin, from the Mine Map or your own. What-if Scenarios: changes of an operating condition that can be run on the Stand without changing the code (close a road, stop equipment…). Only what works on the Stand is taken into account. -->

| Module or What-if Scenario | What it does | How to see it on the Stand | How to undo it (scenarios) |
|---|---|---|---|
|  |  |  |  |

## What works and what does not

<!-- What has been verified, what is unfinished, which bugs are known. -->

## Data and Assumptions

<!--
- Synthetic and real data.
- Sources of parameters: equipment data sheets, reference literature, industrial safety regulations, datasets.
- Datasets: source, license, how they are provided (in the repository or downloaded per the README).
Confidential data of organizations and personal data are prohibited.
-->

## Mine visualization

<!-- Address on the Stand, dashboard or scene; what it shows. -->

## Limitations

## Presentation

`presentation.pdf` in the repository root. Video (optional): <link>

---

Platform: OpenEgiz v1.0.4.
