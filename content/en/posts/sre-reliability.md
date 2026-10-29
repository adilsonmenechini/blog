---
title: "SRE is not about keeping everything up: it's deciding how much failure your architecture can take"
date: 2026-10-21
draft: false
tags: ["SRE", "DevOps", "Reliability Engineering", "Observability", "Incident Management", "SLO", "Cloud Native"]
summary: "Chasing 100% availability can make an organization slower, more expensive, and not necessarily more reliable. SLOs, error budgets, automation, and blameless postmortems turn reliability into a shared decision instead of a battle of opinions."
---
{{< audio slug="sre-reliability" >}}


There is a widely held idea in the infrastructure world: the job of people who operate systems is to prevent them from going down. The fewer incidents, the better. The higher the availability, the better. And if it were possible, everything should run 100% of the time.

It sounds reasonable. After all, nobody wants to open an app and find an error page, try to make a payment and get a timeout, or discover that a service was unavailable during a product launch.

But there is a problem with this logic: chasing availability at any cost can make an organization slower, more expensive, and, ironically, not always more reliable.

How much time does your team spend staring at dashboards? How many changes are skipped because nobody wants to risk breaking production? How many times does an incident happen and the first reaction is to find out who ran the deploy, instead of understanding why the system allowed that deploy to cause such a big problem?

These questions reveal something important. Reliability is not only a property of the infrastructure. It is also a consequence of architecture decisions, development processes, and the way an organization deals with risk.

That is the context in which Site Reliability Engineering, or SRE, comes in.

The proposal is not to hire a team to put out fires more efficiently. It is to treat system operations as a software engineering problem: measure what matters, automate repetitive work, set explicit reliability objectives, and use data to decide when to speed up and when to slow down the pace of change.

The question stops being "how do we guarantee nothing ever fails?" and becomes:

What level of reliability do our users actually need, and how can we achieve it without turning every change into a threat?

## 1. The problem does not start in production. It starts in the way we build software

For a long time, development and operations were treated as separate disciplines.

The development team received a request, implemented features, and tried to deliver the product as fast as possible. Then the system reached production and became the responsibility of another team.

That second team had to deal with deploys, server configuration, capacity, monitoring, incidents, and problems whose context was often concentrated in the head of whoever wrote the code.

That is the famous wall between development and operations.

```text
Business
   |
   v
Development
   |
   | "It's ready. You can operate it."
   v
Operations
   |
   v
Production
   |
   v
Incidents, alerts, and maintenance
```

The problem with this separation is not simply the lack of communication.

It is that the teams can end up optimizing different objectives.

Development is incentivized to deliver features. Operations is incentivized to preserve stability. One wants to change the system; the other needs to manage the risks of those changes.

If the application fails, development may say the environment is misconfigured. Operations may argue the code was delivered without considering real production conditions.

Both teams can be partially right. And the system keeps presenting problems.

DevOps emerged as a cultural movement and a set of practices to reduce those barriers, improve collaboration, and automate the delivery and operations cycle.

SRE takes that discussion to a more concrete operating model. Instead of relying only on collaboration and good intentions, it introduces measurable mechanisms to manage reliability.

Among them are service indicators, service level objectives, error budgets, automation, and incident analysis without blame.

The fundamental change is this: accountability for a system's behavior in production does not end when the code is delivered.

## 2. Is SRE DevOps with concrete engineering mechanisms?

The classic definition of SRE, attributed to Ben Treynor Sloss from Google, describes the discipline as the result of asking a software engineer to design an operations function.

That definition is interesting because it changes the starting point.

Instead of treating operations as a sequence of manual tasks that need to be executed correctly by people, SRE seeks to solve operational problems with engineering, software, and automation.

That includes building tools, eliminating repetitive tasks, designing resilient systems, improving monitoring, and creating processes that reduce the impact of failures.

SRE is also a professional role. A Site Reliability Engineer usually works at the intersection of development, infrastructure, distributed systems, and service operations.

But it is important not to confuse things: SRE is not a synonym for DevOps, although the two approaches share principles and goals.

DevOps emphasizes collaboration, automation, and integration across the stages of the software lifecycle. SRE offers a specific set of practices to manage reliability, such as SLOs, error budgets, incident response, and toil reduction.

A team can adopt SRE practices without immediately creating a department called SRE. Likewise, hiring engineers with that title does not automatically transform the company's culture.

What matters is how decisions are made and how reliability is built into product development.

## 3. 100% availability: an objective that can get too expensive

Let's start with a well-known metric: availability.

In its simplest form, we can measure availability as the proportion of time a service works correctly.

But there is a difference between a server being up and a service being available to its users.

A server can respond to a health check while the application takes several seconds to process a request. An API can respond normally but return incorrect data. A platform can remain accessible while its payment functionality is completely down.

In distributed systems, measuring only machine uptime is not enough.

We need to measure service behavior from a perspective that makes sense to the user.

Imagine an API that received 100,000 valid requests during a measurement window. Of those, 99,900 completed successfully within the defined latency limit.

We can express the observed availability in this example as:

```
SLI = (99,900 / 100,000) × 100
```

The result is 99.9%.

This approach evaluates the outcome of interactions, instead of assuming the service was available simply because its servers were powered on.

Of course, the indicator must define which requests count as valid, which responses represent success, and which period will be analyzed. Those decisions are part of the measurement contract.

And here comes the first SRE lesson: we cannot manage reliability seriously if we do not agree on what it means to be reliable.

### The famous nines

When we discuss availability, it is common to hear expressions like three nines, four nines, or five nines.

They represent different availability levels:

| Availability | Theoretical downtime in 30 days |
| --- | --- |
| 99% | 7 h 12 min |
| 99.9% | 43 min 12 s |
| 99.95% | 21 min 36 s |
| 99.99% | 4 min 19 s |
| 99.999% | 26 s |

*Approximate values for a 30-day period, considering a time-based availability metric.*

At first glance, it seems obvious that five nines are better than three. Technically, they represent a stricter availability target. But that does not mean they are always the right choice.

Raising availability may require geographic redundancy, data replication, failover mechanisms, additional testing, more idle capacity, and a much more complex architecture.

Those measures can be essential for a critical financial service. For an internal tool that can be down for a few minutes without relevant consequences, they may represent an unnecessary cost.

Also, time-based availability and request-based availability are not interchangeable metrics. A short failure during a traffic peak can affect far more users than a longer failure during a low-demand period.

The goal is not to choose the highest possible number of nines. It is to determine which reliability level meets the real needs of the service.

## 4. SLI, SLO, and SLA: three acronyms that do not mean the same thing

An SRE implementation starts with clear definitions. And few things cause as much confusion as these three acronyms.

### SLI: Service Level Indicator

The SLI is the indicator that measures the service's behavior.

It can represent the proportion of successful requests, response latency, the error rate, or another characteristic that matters to users.

Examples:

- Percentage of HTTP requests completed successfully.
- Percentage of requests that finish in under 300 milliseconds.
- Percentage of payment operations processed correctly.
- Percentage of messages processed within a defined deadline.

A good SLI must represent something that genuinely matters to the user experience, not merely something that is easy to collect.

### SLO: Service Level Objective

The SLO is the target set for one or more SLIs over a measurement window.

For example:

At least 99.9% of the API's valid requests must complete successfully over a rolling 30-day window.

Now we have something that can guide decisions.

If the indicator starts to drift away from the target, we need to investigate. If the service stays consistently within the objective, we can assess whether the architecture is adequate or whether there is room to improve operational efficiency.

An SLO does not have to be only about availability. It can set separate objectives for latency, correctness of results, or on-time processing.

It is also important that the SLO be defined with participation from engineering, product, and the business. A purely technical target may not represent what users actually need.

### SLA: Service Level Agreement

The SLA is a formal service level agreement, usually established with customers or consumers of the service.

It can define commitments, measurement conditions, exclusions, and consequences when the agreed levels are not met.

Imagine a platform that offers a contractual SLA of 99.9% availability, while its team works with a stricter internal SLO of 99.95%.

The internal SLO creates a margin to manage risk before violating the contractual commitment. The SLA, in turn, sets the commercial conditions and the obligations toward the customer.

In short:

| Concept | Question it answers |
| --- | --- |
| SLI | What are we measuring? |
| SLO | What result do we want to achieve? |
| SLA | What commitment do we make to the customer? |

Building a dashboard with colorful charts is not enough. Without a relevant indicator, an explicit target, and an understanding of the commitments made, it is hard to decide when to invest in reliability and when to prioritize other improvements.

## 5. Error budget: the mechanism that balances reliability and speed

Here we reach the concept I consider one of the most important in SRE.

If a service has an SLO of 99.9%, the complement up to 100% is 0.1%.

That complement is the basis of the error budget for an availability target.

Over a 30-day window, if we are using a time-based metric, 0.1% equals roughly 43 minutes of unavailability.

That does not mean the team must be down for 43 minutes. It means the target tolerates a certain amount of failures according to the defined metric and window.

For a request-based SLO, the budget is calculated from the eligible requests, not directly from the minutes of the month.

Consider an API that receives one million valid requests in a window and has an SLO of 99.9% success.

The simplified calculation is:

```
Error budget = 1,000,000 × 0.001 = 1,000
```

In that scenario, up to one thousand unsuccessful requests can occur before the service exceeds the corresponding budget, considering this is the only indicator and all events are counted the same way.

The value should not be interpreted as permission to deliberately cause one thousand failures. It is a limit for managing accumulated risk.

### Why does this change the relationship between development and operations?

Without a shared mechanism, the discussion tends to become a battle of opinions.

Development wants to launch a feature. Operations fears the deploy will cause an outage. Product pushes for the deadline. The decision depends on who has more authority or who is willing to take the risk.

With error budgets, there is a common reference.

If the service is running well and has budget available, the team can keep launching changes, provided it uses risk mitigation mechanisms.

If the budget is being consumed quickly or is already exhausted, it may be necessary to slow down risky changes and prioritize reliability, while keeping urgent security fixes and other essential work.

The budget turns reliability into a shared decision criterion, instead of an abstract debate between teams.

### What happens when the budget runs out?

An SRE policy can establish that, when the budget is exhausted, launches that increase risk are temporarily paused until reliability recovers or the policy is revised.

That should not be a bureaucratic ritual or a punishment for the development team.

It is an evidence-based governance mechanism.

We should also not confuse available budget with unrestricted permission to take risks. A service can be within its SLO and still have a serious security vulnerability or a data integrity problem that requires immediate action.

Reliability is multidimensional. The budget is a tool to manage certain risks, not a substitute for technical judgment.

## 6. Operations should not mean endless manual work

There is a kind of work that seems inevitable on many infrastructure teams: responding to alerts, restarting processes, running scripts, adjusting configurations, collecting logs, and repeating procedures that have been performed dozens of times.

The problem is not that all operational activity is manual. There are situations where human intervention is necessary and desirable.

The problem is when manual, repetitive, and predictable tasks consume most of the time of professionals who could be solving structural problems.

In SRE terminology, this kind of work is known as toil.

Toil is operational work that tends to be manual, repetitive, reactive, automatable, and lacking lasting value proportional to the effort. It also tends to grow as the system grows.

Imagine a team that must manually run a verification procedure for every newly deployed service. If there are ten services, the process may be manageable. If there are hundreds, the team may end up spending a growing share of its time simply repeating the same work.

A well-designed automation can run the checks, record the results, alert when necessary, and keep the procedure consistent.

The benefit is not simply saving a few minutes.

It is enabling the team to invest time in improvements that reduce the probability of failures, simplify the architecture, and lower future operational cost.

For this reason, automating should not mean turning any task into code without evaluating its usefulness. Automation needs to be reliable, observable, maintained, and proportional to the problem.

The goal is to reduce repetitive work to free up engineering capacity.

## 7. Monitoring: alert people only when they need to act

Having thousands of metrics does not mean having a well-monitored system.

It is possible to build impressive dashboards and still find out about an outage from the customer.

It is also possible to configure so many alerts that nobody can distinguish important events from noise.

Monitoring must answer a fundamental question: is the service meeting users' needs?

For that, it is useful to track traffic, latency, errors, and saturation indicators, plus signals specific to the application and the service objectives.

But measuring is not enough. We need to define what to do when indicators drift from what is expected.

A practical rule is to separate monitoring outputs by urgency:

- **Immediate alert**: someone needs to act now to mitigate a relevant impact.
- **Ticket or task**: there is a problem that needs investigation, but it does not require immediate intervention.
- **Log or record**: the information needs to be available for diagnosis and later analysis.

If everything generates an urgent alert, nothing is truly urgent.

The result is alert fatigue: professionals start ignoring notifications because many of them require no action or represent no relevant impact.

An SRE team should work so that alerts are tied to real consequences, especially when there is a risk of SLO violation.

The goal is not to eliminate human participation. It is to reserve human attention for situations where it really makes a difference.

## 8. Capacity and performance: scaling is not simply adding machines

Another important aspect of SRE is capacity planning.

Applications grow for different reasons. The user base increases, new features are launched, marketing campaigns drive traffic up, and seasonal events create demand spikes.

If the team only reacts when resources hit their limits, planning has already failed.

On the other hand, provisioning excess capacity without need also has a cost. Idle resources consume money, increase complexity, and can hide inefficiencies.

The challenge is to find a balance between enough capacity to serve demand and headroom to absorb unexpected variations.

Imagine an API that normally receives one thousand requests per second but can reach five thousand during a campaign.

Before scaling the infrastructure fivefold, we need to understand how the application behaves under load.

Can the database handle the extra volume? Is the connection pool sufficient? Is there a dependent service with a capacity limit? Do the caches help or create load concentration? Do load tests reproduce the real behavior?

Scaling an application horizontally does not automatically resolve bottlenecks in shared dependencies.

Planning needs to consider growth scenarios, capacity testing, costs, technical limits, and graceful degradation mechanisms.

It is also important to prepare the system for failures. An architecture operating exactly at the limit of its normal capacity can collapse when it loses a node or has to absorb another instance's traffic.

Capacity headroom has a cost. Lack of it does too.

SRE seeks to make that decision based on measurements and on the impact different scenarios would have on users.

## 9. Changes in production: small changes can also cause big incidents

A single configuration line, a dependency update, or a seemingly trivial change can affect an entire system.

The risk depends on the context, the architecture, the dependencies, and the conditions under which the change is applied.

That is why change management should not be understood merely as an approval form before every deploy.

The goal is to reduce the risk and impact of changes.

Useful practices include:

- Automated tests and validations before deployment.
- Progressive deploys, exposing the change initially to a fraction of the traffic.
- Monitoring service indicators during deployment.
- Automated rollback or well-defined recovery procedures.
- Feature flags to decouple deploying code from activating the feature.
- Risk analysis proportional to the potential impact of the change.

These techniques help detect problems early and limit the number of affected users.

Imagine a new version of an API. Instead of replacing all instances at once, we can release the version to a small percentage of traffic, watch errors and latency, and gradually increase exposure.

If the indicators worsen, the team can halt the progression or roll back the version before the impact grows.

It is important to understand that safe changes are not changes that never fail. They are changes designed so failures are detected and contained quickly.

## 10. Incidents: recover the service first, investigate later

When a system goes down, there is a natural tendency to immediately look for the cause.

Someone wants to find out which commit was responsible, who ran the deploy, or which configuration was wrong.

Those questions may be relevant during investigation. But while the service remains unavailable, the priority is reducing the impact on users.

In incident response, it is important to establish clear responsibilities, communicate the status of the problem, and execute mitigation actions.

Sometimes the immediate fix will be to revert a change. In other cases, it will be necessary to disable a feature, shift traffic, add capacity, or restore data.

The priority is to recover the service safely. Deeper investigation can continue after the situation is stabilized.

That does not mean ignoring the cause. It means separating two activities with different goals: mitigating the incident and learning from it.

### The postmortem is not a courtroom

After a significant incident, a team may produce a postmortem: a document recording what happened, what the impact was, how the system behaved, and which actions can reduce the likelihood or severity of recurrences.

A good analysis includes a timeline, the observed signals, the decisions made, the conditions that contributed to the incident, and the identified improvement items.

But there is an important cultural principle: the postmortem must be conducted blamelessly.

That does not mean absence of accountability. It means avoiding investigations that limit themselves to pointing at a person as the cause of the problem.

If an engineer ran a dangerous command, we need to understand why that command was available, what protections existed, whether there was review, whether the procedure was documented, and why the system allowed a single action to cause that impact.

The analysis changes when the question stops being "who made the mistake?" and becomes "what conditions made that outcome possible?".

Maybe the procedure was ambiguous. Maybe the environment lacked automated validation. Maybe the system offered no safe rollback. Maybe operational pressure encouraged a decision that seemed reasonable with the information available.

The goal is to turn the learning into concrete changes, with owners and follow-up.

A postmortem without effective actions risks becoming just the documentation of an incident that will happen again.

## 11. How to start implementing SRE without transforming the whole company

Adopting SRE does not need to start with a corporate reorganization, a new team, or a complex observability platform.

In fact, starting small is usually more useful.

Choose a relevant service, with identifiable users and an operational problem the team can observe.

Then move forward in steps.

### Step 1: define what success means for the user

Identify the most important operations of the service. For a payments API, it may be completing payments correctly within a latency limit. For a content platform, it may be delivering pages without errors and within an acceptable time.

Avoid starting with infrastructure metrics that are not clearly tied to the user experience.

### Step 2: choose an SLI and set an SLO

Start with an indicator that can be measured consistently.

Define the target, the measurement window, and the conditions that determine what counts as success.

Do not try to address every dimension of reliability at once. A simple, useful target is better than a set of objectives nobody can interpret.

### Step 3: make the error budget visible

Calculate the budget corresponding to the SLO and track its evolution.

The team needs to understand not only whether it is within the target, but also how fast the budget is being consumed.

A budget that disappears quickly is a signal to investigate, even if the target has not yet been exceeded.

### Step 4: improve your alerts

Configure alerts that require human action when there is relevant risk to the service.

Reduce redundant notifications, document response procedures, and define when an event should be treated as an incident.

### Step 5: identify and eliminate toil

Observe the team's daily work. Which activities are repetitive? Which tasks depend on someone manually checking a dashboard? Which procedures could be safely automated?

Prioritize automations that reduce risk, intervention frequency, and time spent on tasks with no lasting value.

### Step 6: create a learning routine

After significant incidents, record what happened and turn the conclusions into verifiable improvements.

Track whether the actions were completed and whether they actually reduced the likelihood or impact of similar failures.

### Step 7: expand with evidence

When the model works for the first service, document the results and share the learning.

Use data to show what improved: fewer incidents, faster recovery, less manual work, or greater deploy predictability.

That way, expanding SRE becomes a decision based on results, not just the adoption of new terminology.

## 12. So, do you need to be a developer to work with SRE?

There is no single career path into SRE.

People with experience in operating systems, networks, infrastructure, cloud, observability, or development can build a career in the field.

But there is a difference between knowing the principles of SRE and performing a reliability engineering role that requires developing and maintaining software.

In an SRE position, programming, automation, debugging, and understanding application behavior are often essential. It is also necessary to understand distributed systems, networks, capacity, monitoring, and incident response.

Starting your career as an application developer is not mandatory. However, relying exclusively on manual procedures limits the kind of problem you will be able to solve.

An infrastructure professional who learns to write tools, automate processes, and investigate the internal behavior of applications is developing skills directly useful for SRE.

Likewise, a developer who learns about production, observability, resilience, and incident management expands their capacity to design operable software.

The goal is not to turn everyone into a specialist in everything. It is to reduce the barriers between building, delivering, and operating systems.

## 13. Reliability is a product decision, not just an infrastructure one

There is an important conclusion behind all these concepts.

SLOs, error budgets, automation, capacity planning, and postmortems are not isolated tools. They form a model for making better decisions about systems in production.

The SLI shows the observed behavior. The SLO defines the service level we want to offer. The SLA formalizes certain commitments with customers. The error budget helps manage the risk of change. Automation reduces repetitive work. Postmortems turn failures into improvement opportunities.

All of this converges toward one question: how do we deliver value to users sustainably?

A service does not need the highest technically possible availability. It needs the availability appropriate to its needs and its risks.

A critical application can justify considerable investment in redundancy and recovery. An internal tool can accept a planned maintenance window if the impact is low and the cost of continuous availability is disproportionate.

These decisions should not be made in isolation by the infrastructure team. Product, engineering, business, and operations need to understand the involved trade-offs.

It is also not enough to declare that failures are normal and use that as an excuse to neglect quality. The SRE philosophy does not diminish the importance of reliability; it demands that reliability be defined, measured, and managed explicitly.

The goal is to avoid both recklessness and excessive conservatism.

## Conclusion: the best SRE is not the one who never gets an alert

It is the one who helps build a system that needs fewer manual interventions, makes its problems visible before they become crises, and allows the team to respond to failures without turning every incident into a blame hunt.

SRE changes the conversation between development and operations because it replaces part of the opinion conflicts with shared objectives and observable data.

Instead of demanding absolute availability, we set realistic targets. Instead of banning changes out of fear, we manage risk with error budgets and safe deployment mechanisms. Instead of repeating operational tasks forever, we invest in automation. And when something fails, we investigate the conditions that allowed the problem and improve the system.

My recommendation is to start with one service, measure what really matters, and use the results to guide the next steps.

You do not need to deploy a complete SRE structure to start practicing reliability engineering. You need to recognize that operations are part of the software lifecycle and that decisions about reliability must consider both the user experience and the cost of keeping the system running.

The question I leave you with is this: if your team spent the next week without having to put out a single fire, what would it finally manage to build so that the following week would be like that too?

## References for further reading

- [Google SRE Book: Site Reliability Engineering](https://sre.google/sre-book/table-of-contents/)
- [Google SRE: Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)
- [Google SRE: Production Services Best Practices](https://sre.google/workbook/table-of-contents/)
- [Google Cloud: SLI, SLO and SLA](https://sre.google/workbook/implementing-slos/)
- [Google SRE: Introduction to reliability engineering](https://sre.google/sre-book/introduction/)
