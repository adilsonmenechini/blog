---
title: "Does Kubernetes really need kube-proxy? What changes when eBPF takes over the networking"
date: 2026-10-21
draft: false
tags: ["Kubernetes", "Cilium", "eBPF", "Networking", "Linux", "Performance", "Cloud Native"]
summary: "Is kube-proxy mandatory? With eBPF, Cilium implements Service forwarding directly in the Linux kernel. Before removing components, understand the packet path, where the traditional model gets expensive, and when the migration is worth it."
---
{{< audio slug="kube-proxy-ebpf" >}}


For years, treating kube-proxy as a mandatory piece of any Kubernetes cluster seemed as natural as installing a container runtime or configuring a CNI. You create a cluster, install the network components, and kube-proxy is there, quietly doing its job.

But what if an important part of that architecture could be eliminated?

That is exactly what some modern Kubernetes networking implementations are doing. With eBPF, projects like Cilium manage to implement Service traffic forwarding directly in the Linux kernel, without relying on kube-proxy and its traditional iptables rules.

The promise is appealing: less unnecessary processing, more control over the packet path, integrated observability, and an architecture that can scale better in certain scenarios.

But there is an important detail. Swapping one architecture for another is not automatically an optimization. Before we start removing components from the cluster, we need to understand the problem we are trying to solve.

Let's follow the path of a packet, understand where the traditional model starts to get expensive, discover what eBPF really does, and finally answer the question that matters: when is it worth abandoning kube-proxy?

## 1. The illusion of the Service IP

Let's start with the basics.

In Kubernetes, when we create a Service, we usually get a virtual IP address, known as the ClusterIP.

Consider this configuration:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-api
spec:
  selector:
    app: my-api
  ports:
    - port: 80
      targetPort: 8080
  type: ClusterIP
```

The Service may receive an address like `10.96.0.100`. That address represents the logical entry point for a set of Pods, not necessarily an address configured on a network interface.

If three Pods serve the Service, the client does not need to know their individual addresses. It accesses the Service, and the network infrastructure forwards the connection to one of the eligible backends.

It is a convenient abstraction. The consumer knows a stable address, while Pods can be born, die, change IPs, and be replaced without requiring each client to update its configuration.

But someone needs to turn that abstraction into real traffic.

Traditionally, that is one of kube-proxy's responsibilities.

It watches Service and EndpointSlice information through the Kubernetes API and programs forwarding mechanisms on the node. Depending on the mode used, this involves iptables rules, IPVS, or another mechanism compatible with the implementation.

In iptables mode, for example, the rules make it possible to recognize the virtual destination, select a backend, and perform the necessary address translation.

The simplified path looks like this:

```text
Client
   |
   v
Service IP: 10.96.0.100:80
   |
   v
Forwarding rules on the node
   |
   v
Selection of a backend
   |
   v
Pod: 10.244.1.10:8080
```

The Service IP does not need to exist as an address assigned to an interface in order to work. The data plane implements the behavior needed to forward traffic destined to it correctly.

It is an elegant solution. And it worked for years in clusters of all sizes.

So, what is the problem?

## 2. When a simple solution starts to get expensive

Imagine a cluster with thousands of Services, tens of thousands of Pods, and a huge number of endpoints changing constantly.

The problem is not simply the number of Pods. The cost depends on the number of rules, their format, the frequency of changes, the distribution of endpoints, and the path packets travel.

In the traditional iptables-based mode, kube-proxy maintains rules that represent Services and their backends. In large clusters, this configuration can grow significantly.

And there is an additional cost: when the configuration changes, the rules need to be reconciled and updated. In certain scenarios, this can increase convergence time and consume CPU during update operations.

Here is the distinction that matters: forwarding a packet is one thing; representing thousands of virtual destinations, tens of thousands of endpoints, and their changes efficiently is another.

iptables is not simply a naive list that always walks through every rule for every packet. The real cost depends on the organization of the chains, the mechanisms the kernel uses, the generated rules, and the execution path. Still, the volume of rules and the update work can become a bottleneck in certain topologies.

It is also not enough to look only at packet forwarding. A cluster can have problems during mass updates even when its normal latency seems perfectly acceptable.

That is why, in large-scale infrastructure, we need to look at two different dimensions:

- **Data plane**: how much does it cost to process traffic while it flows?
- **Network control plane**: how much does it cost to maintain state and update rules when the infrastructure changes?

An architecture can be efficient in one dimension and poor in the other.

And that is where eBPF comes in.

## 3. eBPF: putting the network logic inside the kernel

eBPF stands for extended Berkeley Packet Filter. Despite the historical name, its modern use goes far beyond packet filtering.

It allows executing verified programs inside the Linux kernel, attached to specific execution points. Depending on the program type and the hook used, these programs can inspect traffic, apply policies, collect metrics, and implement parts of network forwarding.

The important detail: we are not talking about running a conventional userspace application to make a decision for every packet.

The eBPF program runs in the kernel, close to the point where the decision needs to happen.

This makes it possible to implement specialized data paths, avoiding certain processing steps present in other architectures.

One of the structures used is the eBPF map.

Think of a map as a data structure accessible to eBPF programs, able to store information such as associations between Services and backends, connection state, or data needed to apply policies.

A map can use a hash table, for example. In that case, an average lookup can cost close to `O(1)`, considering a well-sized table and proper hash operations.

But note: that does not mean all network processing becomes `O(1)`. The map lookup is only one step. The complete path may still involve backend selection, connection state, policies, encapsulation, routing, and other operations.

The advantage is not a universal mathematical promise. It is the possibility of building a more direct and specialized data path for the problem at hand.

## 4. Cilium and the path to the Pod

Cilium uses eBPF to implement networking, security, and observability features in Kubernetes.

In a compatible configuration, it can replace kube-proxy, taking over Service traffic forwarding through its own programs and data structures in the kernel.

The conceptual flow changes from:

```text
Client
   |
   v
Service IP
   |
   v
kube-proxy rules
   |
   v
NAT processing and selection
   |
   v
Destination Pod
```

To something similar to:

```text
Client
   |
   v
Service IP
   |
   v
eBPF hook on the packet path
   |
   v
Query to the data structures
   |
   v
Backend selection
   |
   v
Destination Pod
```

The second diagram is deliberately simplified. The hooks used, the operations performed, and the need for NAT depend on the configuration and the traffic path. Cilium does not magically eliminate all network processing, nor does it mean every packet always performs a single map lookup.

What it offers is an alternative implementation of the data plane, with more direct control over forwarding decisions.

Instead of relying on kube-proxy to maintain the traditional Service rules, Cilium watches the relevant Kubernetes state and programs its own eBPF structures and programs.

The result is an architecture in which processing can avoid part of the work associated with the conventional path.

And we are not just talking about performance.

## 5. More than speed: security and observability

One of the interesting advantages of Cilium is that the same eBPF ecosystem can serve different infrastructure needs.

### Network policies

Cilium offers network policies that control which workloads may communicate, based on attributes such as identity, labels, traffic direction, and other supported criteria.

This helps implement segmentation between services and reduce the allowed communication surface.

Naturally, security depends on the configured policies, the identity model, the enforcement points, and the paths actually covered. Installing Cilium does not mean the entire network is automatically protected.

### Observability with Hubble

Hubble uses Cilium's observability infrastructure to expose information about network flows and communication between workloads.

Instead of investigating a problem solely from application logs and manual packet captures, we can gain visibility into connections, policy decisions, and observed flows.

This is especially useful in environments where dozens or hundreds of services communicate, and the problem is not necessarily inside the application.

### Load balancing

Cilium also implements load balancing mechanisms for traffic destined to Services, with strategies and behaviors that depend on the configuration.

Backend selection can happen in the data plane, using information kept in the kernel.

That does not mean every strategy is available in every configuration, nor that a specific algorithm is always superior. Session affinity, load distribution, connection state, and application requirements continue to influence the choice.

The central point is that networking, security, and observability can share an integrated architecture.

This can simplify operation, but it also raises the importance of understanding the implementation, the kernel requirements, and the diagnostic tools involved.

## 6. What does eliminating kube-proxy actually mean?

Here it is worth avoiding a common confusion.

kube-proxy is not the whole Kubernetes. It is a component that implements part of the network behavior associated with Services.

Kubernetes still needs its control mechanisms, its Service and EndpointSlice objects, and a network implementation capable of connecting the workloads.

When Cilium operates in kube-proxy replacement mode, it assumes the forwarding responsibilities configured for that mode.

That does not mean eliminating the CNI, removing all NAT mechanisms, or making all traffic bypass the kernel.

It also does not mean iptables disappears completely from the node. It may still be used by other parts of the operating system, by firewall tools, or by components that are not part of the Service path replaced by Cilium.

The expression *kube-proxy replacement* is more precise than interpreting the change as a Linux machine completely free of iptables.

The distinction matters because an architecture is not just about removing a process. You must understand which responsibilities were transferred, which remain, and how the new path is implemented.

## 7. So, how much does performance improve?

This is the question that usually comes up after an impressive demo.

The honest answer is: it depends.

Cilium can reduce certain forwarding costs, improve behavior in scenarios with a large number of Services, and offer advantages for specific workloads. But there is no universal percentage of gain that applies to any cluster.

The result depends on factors such as:

- The number of Services and endpoints.
- The rate of workload creation, removal, and updates.
- Traffic volume and packet size.
- Traffic within the same node or across nodes.
- The need for encapsulation and address translation.
- Security policy configuration.
- The load balancing model.
- The Linux kernel and Cilium versions.
- Hardware, drivers, and infrastructure configuration.

If the cluster is limited by database queries, application processing, or the latency of an external dependency, changing the network data plane may produce little or no perceptible gain for the user.

Likewise, it makes no sense to assume that any traditional setup is slow. A small cluster, with few rules and a low change rate, can work very well with kube-proxy.

Before deciding, I would measure at least four things:

1. CPU consumed by the networking components.
2. Latency and throughput of the relevant traffic.
3. Convergence time after changes to Services and endpoints.
4. Cluster behavior during peaks of workload creation and removal.

Benchmarks must represent the real load and compare equivalent configurations. You also need to test connectivity, policies, external access, DNS, and the traffic modes used by the application.

Without those measurements, switching the architecture may just be a more sophisticated way of changing something that was not the problem.

## 8. When is it worth adopting Cilium?

The decision depends less on a dispute between technologies and more on the needs of the environment.

### Small or conventional cluster

If you run a cluster with a few dozen nodes, a moderate number of Services, and an application without networking bottlenecks, there is no automatic reason to migrate.

kube-proxy remains a valid option. A traditional implementation can be simple, predictable, and sufficient for the job.

### Large cluster with many changes

If the environment has a large volume of Services and endpoints, frequent updates, network-related CPU pressure, or convergence problems, it is worth investigating alternatives.

In that scenario, Cilium can deliver benefits both in forwarding and in how the network state is maintained.

But the decision should come with measurements and load tests, not just the number of nodes.

### Environments that require security and visibility

Even when performance is not the main problem, network policy, identity, and observability features can justify adoption.

In that case, the comparison must consider the existing security architecture, the team's operational experience, and the auditing and diagnostic requirements.

In any scenario, the migration must consider kernel compatibility, CNI configuration, load balancing, routing, firewall integration, and recovery procedures.

A change in the network data plane touches a fundamental part of the infrastructure. Ideally, test it in a representative environment, validate the traffic paths, and plan a rollback strategy.

## 9. The lesson is bigger than kube-proxy

The most interesting part of this change is not simply swapping iptables for eBPF.

It is realizing that components considered fundamental in an architecture can be replaced once we understand exactly which problem they solve and how much it costs to keep them.

kube-proxy has played, and can still play, an important role in Kubernetes. The traditional model was not a mistake. It was a practical solution to implement a necessary abstraction.

eBPF allows exploring another integration point with the kernel and building specialized data paths. Cilium takes advantage of that possibility to combine networking, security, and observability in an integrated implementation.

That does not make every previous architecture obsolete, nor does it turn eBPF into a universal solution. It means we now have other options, with different costs and benefits.

My conclusion is simple: do not replace kube-proxy because someone promised that eBPF is faster. Understand the packet path, identify the bottleneck, measure the cluster's behavior, and only then choose the architecture.

The best infrastructure is not necessarily the one using the newest technology. It is the one that solves the real problem with the lowest operational cost, adequate performance, and a level of complexity your team can manage.

And one question to carry forward: if we managed to rethink such a traditional part of Kubernetes networking by bringing the decision logic closer to the kernel, which other infrastructure bottlenecks are we accepting just because they have always been implemented that way?

## References for further reading

- [Cilium: official documentation](https://docs.cilium.io/)
- [Cilium: kube-proxy replacement](https://docs.cilium.io/en/stable/network/kubernetes/kubeproxy-free/)
- [Cilium: eBPF overview](https://docs.cilium.io/en/stable/bpf/)
- [Kubernetes: Services, Load Balancing and Networking](https://kubernetes.io/docs/concepts/services-networking/service/)
- [Linux Kernel: eBPF documentation](https://docs.kernel.org/bpf/)
