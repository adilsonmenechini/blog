---
title: "Cheaper and more efficient Kubernetes: combining Karpenter and KEDA"
date: 2026-10-21
draft: false
tags: ["Kubernetes", "FinOps", "Autoscaling"]
summary: "Scaling the application with demand and sizing the infrastructure behind it are different problems. With KEDA and Karpenter working together, the cluster scales when it needs to, shrinks when it can, and costs less to deliver the same result."
---
{{< audio slug="karpenter-keda" >}}


Have you ever stopped to think about how much money you might be spending on a Kubernetes cluster that runs all day long, even when it has almost no work to do?

This is a common problem in cloud environments. We provision infrastructure to support demand peaks, but when traffic slows down, we keep paying for resources we are not using.

The good news is that we can attack this problem on two fronts: scale the applications according to demand and adjust the infrastructure to match exactly what they need.

That is where KEDA and Karpenter come in.

## The problem is not just having machines that are too big

Imagine an application that processes financial transactions received through an Amazon SQS queue.

For most of the day, few messages arrive. At certain times, however, the volume spikes and we need to process everything quickly.

If we keep dozens of pods and machines available all day long, we will spend money on idle capacity.

If we provision too few resources, we risk accumulating messages and increasing processing time.

We need to find a balance between cost, capacity, and performance.

And trying to solve everything by simply increasing or decreasing the number of machines is not enough.

## KEDA: scale the application according to demand

KEDA (Kubernetes Event-Driven Autoscaling) allows you to scale applications based on external events and metrics.

Instead of looking only at CPU and memory, we can use signals such as:

- The number of messages in an SQS queue.
- Consumer lag on Kafka.
- External metrics provided by monitoring systems.
- Events coming from other supported services.

Imagine our application consumes messages from an SQS queue.

When the volume increases, KEDA feeds metrics to the Kubernetes Horizontal Pod Autoscaler (HPA), which adjusts the number of replicas according to the configured rules.

When demand decreases, the number of pods can be reduced. In compatible scenarios, we can even scale down to zero replicas and start running again when new events arrive.

This means we do not need to keep a processor application active when there is no work, provided it supports this model and the latency requirements allow it.

But there is an important detail: reducing the number of pods does not necessarily reduce the number of machines.

If the pods disappear and the nodes stay up, we are still paying for the infrastructure.

That is exactly where Karpenter enters the story.

## Karpenter: provision the infrastructure we actually need

Karpenter operates at a different layer: the cluster infrastructure.

When pods are pending because there is no available capacity, it analyzes the requirements of those workloads and tries to provision compatible nodes.

That decision takes into account information such as:

- CPU and memory requests of the pods.
- Allowed instance families and sizes.
- Compatible processor architectures.
- Availability zones.
- Capacity constraints and provisioning policies.
- Purchase options, such as On-Demand and Spot instances, when configured.

The great advantage is not having to manually maintain a node group for every instance combination we want to use.

In AWS environments, for example, Karpenter can select among different instance types allowed by the cluster configurations, instead of relying exclusively on a strategy based on fixed Auto Scaling groups.

It can also consolidate workloads when that is safe and economically advantageous, replacing underutilized nodes with a more efficient configuration.

The goal is not simply to create more machines. It is to provide the necessary capacity and avoid keeping unnecessary resources.

## The best outcome happens when we use both together

Now imagine the complete flow.

A queue starts receiving thousands of messages.

1. KEDA detects the increase in demand and feeds the metrics to the HPA.
2. The HPA increases the desired number of pods.
3. If there is not enough capacity, some pods become pending.
4. Karpenter detects the need and provisions compatible nodes.
5. When the new machines become available, the scheduler distributes the pods.
6. Once the queue is drained and demand decreases, KEDA scales down the replicas.
7. Karpenter can consolidate or remove nodes that are no longer needed, respecting its policies and the workloads' constraints.

Each tool solves a different part of the problem.

KEDA reacts to the application's demand. Karpenter adjusts the infrastructure capacity to accommodate that demand.

This combination lets us work with two-layer scalability, instead of trying to solve everything with a single tool.

## What about Spot instances? Are they worth using?

Spot instances can significantly reduce the cost of interruption-tolerant workloads, but they require planning.

Karpenter can work with both Spot and On-Demand options, as long as they are allowed in the NodePool configurations.

When a Spot interruption is announced and the interruption handling mechanism is properly configured, Karpenter can try to replace the affected capacity.

That does not mean the interruption will be invisible. The replacement depends on capacity availability, cluster configurations, and the time needed to start and prepare the new nodes.

For this reason, critical applications must consider fault tolerance, multiple availability zones, interruption handling, and safe message reprocessing.

The most efficient strategy is not to use Spot for everything. It is to identify which workloads can take advantage of this mode without compromising business requirements.

## Scaling to zero also requires care

There is another interesting point in this architecture: the possibility of keeping certain applications with zero replicas when there is no demand.

For queue processors, this can represent a relevant saving.

But scaling to zero is neither free nor instant.

When a new event arrives, there can be an interval before KEDA requests new replicas, Kubernetes schedules the pods, and Karpenter provisions nodes if no capacity is available.

If the application needs to respond in milliseconds, it may be necessary to keep some minimum warmed-up capacity.

If it processes asynchronous tasks and tolerates a few seconds or minutes of waiting, scaling to zero can be an excellent strategy.

The decision depends on the workload's profile, not just on the technical possibility of shutting it down.

## What actually makes a difference in cost reduction?

Installing KEDA and Karpenter does not guarantee a lower bill by itself.

The result depends on how we configure and operate the cluster.

Some practices make a big difference:

- Define CPU and memory requests consistent with the applications' real consumption.
- Configure scaling triggers that represent the business demand.
- Allow instance flexibility without violating compatibility requirements.
- Use Spot on the right workloads.
- Configure consolidation policies that respect availability and interruptions.
- Measure costs, utilization, latency, and processing time before and after the changes.

It is also important to note that KEDA and Karpenter do not replace proper application sizing. If the requests are wrong or the triggers are poorly configured, the automation can make bad decisions.

The goal should not simply be to reduce the number of machines. It should be to reduce the cost per unit of processed work, while keeping the expected performance and reliability.

## In the end, the idea is simple

Kubernetes offers powerful scaling mechanisms, but financial efficiency depends on tuning the application and the infrastructure in a coordinated way.

KEDA helps answer one question: how many replicas do we need to process the current demand?

Karpenter helps answer another: what infrastructure do we need to run those replicas?

When we combine the two, we can bring resource consumption closer to real demand, make better use of available capacity, and reduce waste.

Because, in the end, it is not enough to have a cluster that scales.

The goal is to have a cluster that scales when it needs to, shrinks when it can, and costs less to deliver the same result.
