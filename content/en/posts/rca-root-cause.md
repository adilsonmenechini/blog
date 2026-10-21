---
title: "RCA is not filling in a form: it is finding out why the system allowed the failure"
date: 2026-10-21
draft: false
tags: ["SRE", "Incident Management", "RCA", "Postmortem"]
summary: "Recovering the service does not eliminate the conditions that produced the failure. An RCA only has value when it turns evidence into verifiable changes to the system, the process, or the controls, not into a document that explains the past."
---

## Introduction: the incident is over, but was the problem solved?

A service becomes unavailable. The operations team receives alerts, starts investigating, and finds a seemingly simple problem. Someone restarts a component, the service responds again, and the metrics start to normalize.

The team breathes a sigh of relief. The incident is closed.

A few days later, the same problem happens again.

The initial response worked, but it did not explain why the failure happened, which conditions allowed it to propagate, or what should change to prevent a new occurrence.

This is one of the most common problems in incident resolution: confusing service recovery with the elimination of the conditions that produced the failure.

Root Cause Analysis, known as RCA, exists to face that problem. Its purpose is not to produce a document to comply with an internal process, nor to find someone to blame. It is to reconstruct the events, test hypotheses, and identify changes capable of reducing the probability of recurrence.

The thesis of this article is simple: **an RCA only has value when it turns the evidence of an incident into verifiable changes to the system, the process, or the control mechanisms.**

Everything else is documentation with no guarantee of learning.

## The problem of looking for culprits instead of investigating systems

When something fails, there is a natural tendency to look for a quick explanation.

Someone ran the wrong command. A change was published without the expected validation. A procedure was not followed. An alert was not addressed in time.

These observations may be true, but they do not necessarily explain the incident.

If a person performed a dangerous operation, for example, the investigation still needs to ask why that operation was possible, which protections should have existed, and why they did not prevent or limit the impact.

Was there a mandatory review? Did the system require confirmation? Was there a rollback mechanism? Was the change limited to a single environment? Were the risk signals visible before execution?

The difference lies between identifying an action associated with the incident and explaining the conditions that allowed it to produce that outcome.

In reliability engineering, this distinction matters because real systems are made of people, processes, software, infrastructure, external dependencies, and decisions made over time.

A failure rarely needs to be explained by a single isolated factor.

That also does not mean people should never be held accountable for their decisions. It means a technical investigation should not close its analysis simply because it found a person or an action near the event.

**If the same mistake can happen again under the same conditions, the investigation still needs to understand what makes that repetition possible.**

## RCA is a method, not a collection of tools

There are several tools used in root cause analysis. Among them are the five whys, the Ishikawa diagram, also known as the cause-and-effect diagram, and the Pareto diagram to help prioritize problems according to the available data.

Each offers a different way of organizing reasoning.

The five whys help deepen an initial explanation. The Ishikawa diagram makes it possible to organize potential causes into categories. Pareto helps identify which occurrences or categories concentrate a relevant share of the observed problems.

None of these tools, in isolation, guarantees that the identified cause is correct.

It is possible to fill an entire diagram with hypotheses that were never verified. It is also possible to ask five questions and end up with a superficial explanation. A well-organized presentation does not turn an assumption into evidence.

For this reason, the tool must be subordinate to the method.

A consistent RCA must start from the facts, reconstruct the sequence of events, formulate hypotheses, look for evidence that supports or contradicts them, and establish actions consistent with the causes found.

The method organizes the investigation. The tools help execute it.

There is no obligation to use every tool on every incident. The choice must consider the complexity of the problem, the availability of data, and the level of depth required.

## When is an RCA worthwhile?

An RCA is especially useful when an incident has significant impact, shows recurrence, reveals an important weakness, or raises doubts about the prevention and recovery mechanisms.

That does not mean every operational failure needs to generate an extensive investigation.

A small, well-understood, and easily fixed interruption may require only proper recording and a one-off action. A recurring failure, a relevant unavailability, or an incident with multiple factors may justify a more structured investigation.

Depth should be proportional to the risk, the impact, and the uncertainty.

It is also important to understand the temporal role of the RCA: it is usually an investigation that happens after an event. During an active incident, the priority is usually to contain the impact, restore the service, and preserve the evidence needed to understand what happened.

The investigation must not delay an urgent recovery.

After stabilization, the team can deepen the analysis and decide which changes are needed to reduce the possibility of recurrence.

The RCA also does not replace preventive practices, resilience testing, risk analysis, or continuous monitoring. It complements those activities by using the experience of a real failure to improve the system.

## The six steps of a root cause analysis

An investigation needs a beginning, a development, and an outcome. In practice, we can organize it into six steps.

### 1. Assemble the investigation team

An RCA should not depend exclusively on the person who was on call or the professional who knows the affected component best.

It is important to bring together people with different perspectives on the system: those who operate the platform, those who develop the application, those who know the infrastructure, and, when necessary, specialists in security, architecture, networks, or vendors.

The size of the group depends on the problem. The team should be small enough to allow a productive discussion, but diverse enough to avoid an investigation limited to a single point of view.

It is also important to define responsibilities: who leads the analysis, who provides the evidence, who decides on the changes, and who tracks their implementation.

Leadership participation may be necessary to provide resources and remove impediments. Without that support, an investigation may correctly identify a weakness and end up unable to fix it.

### 2. Reconstruct what happened

Before explaining a failure, we need to establish the facts.

That includes recording the observed impact, the affected services, the start time, the sequence of events, recent changes, and the moment the service was recovered.

In software environments, the sources may include:

- Application and infrastructure logs.
- Metrics of latency, traffic, errors, and saturation.
- Distributed traces and dependencies between services.
- Kubernetes and cloud provider events.
- Deploy history, configuration changes, and infrastructure changes.
- Alerts, support records, and operational communications.

Chronology is especially important because events close in time do not always have a causal relationship.

A deployment may have happened before the incident without causing the failure. A latency increase may be the cause of a subsequent error or just another effect of the same problem.

The investigation must separate what was observed from what is being inferred.

Another important point is preserving the data. Logs may expire, metrics may have limited retention, and temporary events may disappear. Recording the chronology while the evidence is available reduces dependence on participants' memory.

### 3. Identify potential causes

With the sequence of events established, the team can start formulating hypotheses.

Imagine a service that starts showing errors after an infrastructure change. Possible hypotheses include a misconfiguration, a capacity limitation, a connectivity failure, or unexpected behavior from an external dependency.

At this point, the team does not need to immediately choose a single explanation.

The Ishikawa diagram can help organize those possibilities. The five whys can deepen the most relevant hypotheses.

The fundamental care is not to confuse a plausible hypothesis with a demonstrated cause.

For each proposed explanation, the team must ask: what evidence do we expect to find if that hypothesis is correct? What observation could contradict it? Do we have enough data to distinguish it from the alternatives?

That process reduces the risk of selecting the first explanation that seems reasonable and building the whole investigation around it.

### 4. Identify the fundamental causes

A fundamental cause must explain a relevant portion of the sequence that produced the incident and point to conditions that can be treated.

That does not mean there is always a single root cause.

In distributed systems, different factors can interact: a dependency slows down, a queue grows, timeouts accumulate, and the available capacity becomes insufficient. The final impact may depend on the combination of those factors.

The investigation should look for causal relationships supported by evidence, without forcing a single explanation when the data points to multiple contributions.

It is also necessary to distinguish the immediate cause from the underlying conditions.

A process may have been killed by lack of memory. That is a mechanism close to the failure. The investigation still needs to verify why consumption grew, why capacity was insufficient, and which controls could have detected or limited the problem.

The analysis ends when the team has an explanation supported enough to guide concrete actions, not when it finds a short sentence to fill in the "root cause" field.

### 5. Implement corrective actions

An RCA without an action plan will hardly produce lasting improvement.

The actions need to be related to the identified causes and have owners, deadlines, and completion criteria.

Depending on the incident, they may include:

- Fixing a configuration or a software defect.
- Introducing automatic validations into CI/CD pipelines.
- Adjusting resource limits, timeouts, or retry policies.
- Improving change management and rollback mechanisms.
- Creating alerts for signals that were not being watched.
- Introducing access controls or protections against dangerous operations.
- Improving operational procedures and recovery documentation.

Priority should be given to actions that effectively change the conditions of the problem.

Training and documentation may be necessary, but they should not replace technical controls when those are viable and appropriate.

For example, if a destructive operation can be run by mistake, simply asking everyone to be more careful may be insufficient. A validation, a permission restriction, or an additional confirmation can reduce the dependence on perfect behavior.

### 6. Verify whether the actions worked

Implementing a fix is not the same as demonstrating its effectiveness.

A change may have been completed and still not resolve the identified cause. It may reduce the frequency of the problem without eliminating it. Or it may introduce another risk that was not present before.

For that reason, the team must define how to evaluate the outcome.

The criteria may include the absence of recurrence over an adequate observation window, a reduction in an error rate, improvement of an SLO, or proof that a protection mechanism blocks the unwanted behavior.

The evaluation window needs to consider the expected frequency of the event. A problem that occurred daily may allow a relatively quick assessment. A failure that appears only under certain seasonal conditions may require much longer monitoring.

Finally, the knowledge must be transferred to those who maintain the system. The changes, the remaining risks, and the relevant procedures should become part of normal operations, not remain restricted to the group that conducted the investigation.

Without that transfer, the organization risks losing the learning when people change teams.

## A practical example: the service came back, but the cause is still there

Consider an illustrative scenario of an application running on Kubernetes.

After a deployment, the service starts showing increased latency and errors. Some instances restart, and the team notices availability dropped.

The team performs a rollback and the service recovers.

The first conclusion could be: "the deploy caused the incident".

That statement is an initial hypothesis, not a sufficient conclusion.

The investigation needs to correlate the deployment time with metrics, logs, pod events, and configuration changes. It also needs to check whether the problem appears exclusively in the new version, or whether some infrastructure or dependency condition explains the behavior.

Suppose the analysis of the evidence confirms the following sequence:

1. A change introduced a behavior that raised memory consumption under a specific load.
2. The pods exceeded the configured memory limits and were terminated by the system's protection mechanism.
3. The remaining capacity was not enough to absorb the traffic during restarts.
4. The application had not been validated with a load test representative of that condition before deployment.

In that scenario, the rollback restored the service, but it did not fix the defect or the validation gap.

The action plan could include fixing the behavior that raised consumption, adding a load test that reproduces the relevant condition, and establishing observation criteria during deployment.

The actions must be defined according to the real evidence of the incident; this example does not represent a universal diagnosis for pod restarts.

The central point is that the investigation did not stop at the most visible event. It connected the application behavior, the platform capacity, and the controls in place before deployment.

It is that connection that allows proposing improvements beyond repeating the rollback at the next occurrence.

## How the RCA connects to reliability engineering

In SRE (Site Reliability Engineering), incident investigation should contribute to the reliability of the service.

That means relating the learning to observable indicators and objectives, such as SLIs, SLOs, availability, latency, error rate, and time to recovery.

A corrective action should be evaluated not only by its administrative completion, but by the effect it produces on the system.

If a change intends to reduce the duration of outages, for example, the team needs to define how to observe that reduction. If it intends to detect a failure before it affects users, it must verify that the new mechanism actually produces a useful and actionable signal.

The RCA also helps identify repetitive operational work that can be eliminated through automation, improve response procedures, and guide resilience testing.

The goal is not only to reduce the number of incidents. It is to make failures less likely, limit their impact, and improve the ability to recover when they happen.

A well-conducted investigation can also reveal limitations that will not be solved by an isolated change. External dependencies, architectural decisions, and business constraints may require a gradual plan, with risks explicitly documented.

Reliability improves when incident learning influences later engineering decisions.

## What can artificial intelligence change in the RCA?

An organization can conduct good investigations and still lose part of the knowledge produced.

Reports get scattered across documents, ticketing systems, observability tools, and communication channels. Months later, another team faces a similar symptom without knowing that a similar situation was already investigated.

That is where artificial intelligence can help.

If RCA records are organized and accessible, a solution based on information retrieval, such as RAG (Retrieval-Augmented Generation), can locate previous investigations, summarize hypotheses already evaluated, and relate incidents that share relevant characteristics.

An agent can also help structure a timeline, identify gaps in a report, or suggest questions to deepen a hypothesis.

These capabilities can reduce the time spent searching for information and make it easier to reuse operational knowledge.

But there is an important difference between supporting an investigation and determining its conclusion.

A language model can produce a convincing explanation that is not supported by the available evidence. It can associate incidents that share symptoms but have different causes. It can also ignore environment-specific details if that data is not present in the retrieved context.

For that reason, a responsible implementation must preserve the origin of the information, allow verification of the evidence, and clearly distinguish facts, hypotheses, and model-generated recommendations.

AI must not turn a hypothesis into a root cause just because it can explain it well.

It also does not replace the instrumentation needed to investigate the system. If there are no metrics, logs, or proper change records, a model cannot safely recover what was never observed.

The greatest potential benefit lies in combining reliable operational data, structured documentation, and knowledge retrieval capability.

In that scenario, each incident can contribute to making the next investigations faster and better grounded.

## The limits of an RCA

Root cause analysis is not a guarantee that an incident will never happen again.

An investigation can be limited by the absence of data, the complexity of the system, or the difficulty of reproducing certain conditions. A change may reduce a risk without eliminating every possible path to the failure.

In chronic problems, with multiple factors and variations that are hard to observe, it may be necessary to complement the RCA with statistical analysis, more detailed monitoring, controlled experiments, or continuous improvement methods.

There is also the risk of turning the process into bureaucracy: lengthy reports, unproductive meetings, and action plans that are never verified.

A longer analysis is not necessarily a better analysis.

The level of rigor must be sufficient to support the conclusions and guide decisions proportional to the risk. When the evidence does not allow determining a cause with confidence, acknowledging the uncertainty is better than manufacturing a definitive answer.

The outcome of an RCA should be understood as an explanation supported by the available evidence, subject to revision if new relevant information appears.

## Conclusion: the learning must survive the incident

An organization does not demonstrate operational maturity because it owns an RCA form, a documented process, or a mandatory meeting after every failure.

It demonstrates maturity when it manages to turn incidents into concrete changes, track the results of those changes, and share the knowledge produced.

That requires discipline to reconstruct the facts, willingness to question initial explanations, collaboration across different areas, and commitment to implementing the actions.

It also requires accepting that not every failure will have a simple explanation, and that not every action will be enough on the first attempt.

Root cause analysis does not exist to retell what happened. It exists to understand which conditions made the incident possible and to decide what needs to change.

If the service came back, but the conditions that produced the failure are still present, the work is not finished yet.

**The real outcome of an RCA is not the document that explains the past. It is the verifiable improvement that changes the future behavior of the system.**
