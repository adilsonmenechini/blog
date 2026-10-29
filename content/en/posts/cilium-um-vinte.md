---
title: "Cilium 1.20: is it time to turn off some Kubernetes boxes?"
date: 2026-09-21
draft: false
tags: ["Cilium", "Kubernetes", "Gateway API", "eBPF", "Networking"]
summary: "Cilium 1.20 brings TCPRoute, UDPRoute, ExternalAuth and more features that allow consolidating gateway, authentication and exposure of TCP/UDP services in a single platform. Is it possible to simplify the architecture?"
---
{{< audio slug="cilium-um-vinte" >}}

There’s something interesting about infrastructure: we install one tool to solve a problem, then another to solve the problem that the first one didn’t solve, and yet another to integrate the two. Before you know it, you’re managing five components to do something that seemed simple at the start.

This happens all the time in Kubernetes.

You install a CNI to take care of the network. Then an Ingress Controller comes along to publish your applications. Then there’s a need for authentication and you put a proxy in front of everything. For some TCP services, a LoadBalancer configuration is added. And when communication between services starts to get complicated, someone suggests installing a service mesh.

You’ve got a platform.

And you also have five things to update, monitor, configure, and explain to anyone who joins the team.

That’s why Cilium 1.20 caught my attention. It’s not just because it has new features, but because it starts to make a quite reasonable question: do we really need so many separate pieces to manage a Kubernetes cluster’s network?

First, the ingress-nginx went away. What now?

In March 2026, Kubernetes archived the ingress-nginx after a series of security problems, including a critical remote code execution vulnerability.

This left many people with a very practical question: where to migrate?

The most interesting answer isn’t just choosing another Ingress Controller and going on. It’s taking the opportunity to reconsider the architecture.

The Gateway API has been gaining traction as an alternative to the traditional Ingress model. It offers a more organized way to declare how traffic enters the cluster, which ports are available, where requests go, and who can manage each part of this configuration.

There was just one detail.

When you needed to publish an HTTP application, fine. But what if you wanted to expose a PostgreSQL? Or a Redis? Or some service that spoke UDP?

That's where the exceptions started. A Service LoadBalancer here, a manual configuration there, another authentication component over there.

In other words: you adopted a modern API to organize traffic and continued to keep a bunch of things outside.

Cilium 1.20 helps narrow this gap.

What’s so interesting about Cilium 1.20?

Let’s put the list of new features aside for a moment and look at what really changes in the lives of those who manage the cluster.

The release brings support for **TCPRoute** and **UDPRoute**, integration of external authentication via the **ExternalAuth** filter, and improvements to the listener management model and backend TLS.

Translating to everyday terms:

- **TCPRoute and UDPRoute**: allow TCP and UDP services to be placed in the same declarative model used to manage gateway traffic.
- **ExternalAuth**: allows integrating an external authentication or authorization service into the gateway flow.
- **ListenerSets**: facilitate the delegation of listeners to different teams and namespaces.
- **BackendTLSPolicy**: helps declare how the gateway establishes TLS connections with backend services.
- **CORS in HTTPRoute**: allows configuring this behavior directly in the route, rather than relying exclusively on the application or additional components.

This doesn’t mean all of these features are at the same level of maturity, nor that you should start enabling everything in production. But together they point to an interesting direction: fewer scattered configurations and more things managed by the same model.

And two of these changes deserve a separate discussion.

## TCP and UDP: can we finally stop treating every service as an exception?

Imagine you have a cluster with web applications, a PostgreSQL, a Redis, and a message broker.

HTTP traffic already passes through the gateway. But the other services need different ports and protocols. Traditionally, you end up creating Services LoadBalancer or NodePort and managing these exposures separately.

It works? Sure.

Is it the best way to organize everything when infrastructure grows? Not always.

With TCPRoute and UDPRoute, Cilium 1.20 allows declaring these routes using the Gateway API. You have a more uniform model for managing the traffic that enters the cluster, even when it’s not HTTP.

There’s a cool technical detail here: Cilium’s L4 implementation doesn’t need to send this traffic through the L7 Envoy proxy. Routes are reconciled in Services and EndpointSlices managed by the operator, which feed service balancing based on eBPF.

This means you don’t need to add an L7 proxy hop just to forward a TCP connection.

There’s also support for propagating backend weights. With the appropriate weight, it’s possible to stop sending new connections to a backend and allow existing ones to terminate, according to the behavior of the implementation.

Think about a service update. You want to withdraw an instance from balancing without necessarily dropping all the connections it already serves.

This kind of operation becomes much more interesting when it’s part of the traffic management model, rather than depending on a collection of manual adjustments.

The big advantage, therefore, isn’t just performance. It’s being able to manage more things consistently.

## And authentication? One less proxy?

Here’s another very common situation.

You publish an internal application and want to require authentication before letting someone access it. Maybe you use an SSO service, a custom authorizer, or some token integration.

A traditional solution is to put an authentication proxy between the gateway and the application. It receives the request, queries the service responsible for the decision, and grants or blocks access.

It works very well. The problem is that this proxy becomes another service to maintain.

With the ExternalAuth filter, Cilium allows declaring this integration in the gateway’s configuration. The decision can still be taken by an external service, but the authentication flow is integrated into the gateway’s route management.

Notice the difference: we’re not necessarily eliminating the authentication system. We’re eliminating the need to maintain a separate intermediate component when it exists only to connect the gateway to that system.

This can simplify quite a bit a small platform.

But pay attention: ExternalAuth has its own maturity level and needs to be evaluated before being adopted in production. Furthermore, the external service still needs availability, monitoring, and appropriate policies.

It doesn’t help to remove a proxy and discover later that you’ve only transferred the problem to another place.

## What would an infrastructure like this look like in practice?

Let’s imagine a small Kubernetes fleet running on self-managed servers, with Cilium as the CNI.

Today, it has ingress-nginx for HTTP, Services LoadBalancer for some TCP services, and an additional proxy for authentication.

The team also maintains network policies to control communication between applications.

It doesn’t seem like an absurd architecture. In fact, it’s quite similar to what many people have put together over the past few years.

The problem is that each component has its own way of working. When an update comes along, you need to understand the impact on each part. When something fails, you need to find out where the problem is.

With a well-planned migration to the Gateway API, the architecture could look something like this:

- A **Gateway** to organize incoming traffic.
- **HTTPRoute** for web applications.
- **TCPRoute and UDPRoute** for services using other protocols.
- **ExternalAuth** to integrate authorization into the gateway flow.
- TLS policies for connections with backends.
- **Cilium NetworkPolicies** to continue controlling communication between workloads.

The goal is to reduce the number of independent components without mixing responsibilities that need to remain separate.

The Gateway API doesn’t replace network policies. And authenticating someone at the cluster’s entry doesn’t mean that person or application should have unrestricted access to all internal services.

Each thing still has its role.

The difference is that you need fewer pieces to put the architecture together.

## Alright. So it’s just an update and we can delete ingress-nginx?

I wish I could say yes, but that would be too easy.

Migration is precisely the part that requires the most care.

Tools like **ingress2gateway** help convert Ingress resources to the Gateway API. This is great for reducing mechanical work, but it doesn’t guarantee that everything will continue to work exactly as before.

The problem is usually in the small particularities accumulated over time.

You know that annotation someone put three years ago to rewrite a URL? Or that custom snippet that nobody remembers why it exists? Or that authentication configuration that has been being adjusted until it worked?

That’s where migration can fail.

A tool can convert many objects, but it can’t always reproduce the specific behavior of each controller. Some rules need to be rewritten using Gateway API filters or mechanisms specific to the chosen implementation.

That’s why I’d start by comparing route behavior, not just generated YAML.

Another caution is the CRD version. To use TCPRoute and UDPRoute, you need to install compatible versions of the Gateway API definitions. Updating Cilium doesn’t automatically guarantee that these definitions are available in the correct version.

It’s worth checking this before migrating any L4 service.

It’s also important to verify the Envoy execution mode and implementation limitations. There are scenarios in which TCP/UDP listeners and routes are not reconciled when the Cilium Envoy is configured to operate in host network mode.

And, of course, network policies need to be tested again. A major datapath change isn’t the time to assume that all rules will continue to behave exactly as before.

My approach would be very simple: create a parallel Gateway, migrate a low-criticality HTTP application, validate the behavior, and only then move on to authentication and TCP/UDP services.

If possible, keep the old path available during the transition. It’s much better to be able to go back calmly than to discover at two in the morning that a forgotten annotation controlled something important.

## Can we forget about service mesh too?

Slow down. One thing at a time.

Cilium 1.20 reduces the need for some components that used to surround the gateway, but that doesn’t mean it automatically replaces all the functions of a service mesh.

Think about the difference between these two questions:

- Who can access my application from the internet?
- Which internal service can call which operation of another service?

The first can be solved at the gateway. The second requires a policy for communication between workloads, with appropriate identity and authorization.

It’s possible to build part of this architecture with Cilium’s own features. Depending on requirements, however, you may still need additional mesh functionalities.

The same applies to retries, circuit breaking, advanced traffic distribution, canary releases, and fault injection. It all depends on what your platform needs and what the chosen implementation offers.

And there’s an important difference between authenticating a request at the edge and establishing cryptographic identity between services using mTLS.

These are related problems, but not equivalent.

So I wouldn’t say that service mesh is dead. I’d say it’s more difficult to justify its automatic installation across all Kubernetes infrastructure.

If you need its functionalities, great. But if the goal was just to publish applications, apply some policies, and control access at the cluster’s entry, perhaps you were keeping more infrastructure than needed.

This is an important difference: choosing a mesh because there’s a concrete need is quite different from installing one because it seems like the next mandatory step.

## And this simplification doesn’t create another problem?

It can, yes.

There’s a temptation to look at this evolution and conclude that the more things a single platform offers, the better.

Not always.

When you concentrate more responsibilities on Cilium, you become more dependent on it. A problematic update can affect a larger part of the infrastructure. Recent features may have limitations that haven’t shown up in your environment yet. And the team needs to know how the solution works well to avoid turning consolidation into a new black box.

On the other hand, maintaining several independent components also has a cost. There are more integrations, more update cycles, and more points where a configuration can get inconsistent.

There’s no universal answer. There’s a trade-off between the complexity of managing several tools and the dependency on a more comprehensive platform.

For a small team, this trade-off can make quite a bit of sense, as long as adoption is gradual and accompanied by tests.

## What would I do if I were setting up this infrastructure today?

If I were already using Cilium, I’d start with the simplest path.

First, I’d check the compatibility of the Gateway API CRDs and create a test Gateway. Then I’d migrate a HTTP application without much criticality.

With that working, I’d test ExternalAuth and backend TLS configuration. Only then would I start migrating TCP and UDP services, paying special attention to persistent connections and behavior during updates.

I’d also review network policies and rollback procedures before decommissioning any old component.

Nothing very glamorous. It’s the kind of work that prevents discovering problems in production.

And I wouldn’t try to eliminate service mesh in the same move. First I’d consolidate what the gateway can solve well. Then I’d evaluate which needs continue requiring an additional layer.

The goal isn’t to have the smallest number of deployments just to be able to say that the infrastructure is lean.

The goal is to stop operating components that don’t deliver enough value to justify their existence.

## In the end, fewer boxes is good news

Cilium 1.20 doesn’t transform Kubernetes into something simple. We still need to deal with versions, policies, observability, certificates, failures, and all those small surprises that come with administering infrastructure.

But the evolution of the Gateway API opens an interesting possibility: managing HTTP, TCP, UDP, authentication, and backend TLS more uniformly, leveraging a network platform that you might already have running in the cluster.

And this changes the conversation.

Instead of asking which controller to install, which proxy to add, and how to integrate another component, we can start by asking if we need them all.

For those who maintain a small self-hosted fleet, each component removed can mean fewer updates, fewer duplicated configurations, and fewer things to figure out when something breaks.

The archived ingress-nginx made migration necessary for those who still depended on it. Cilium 1.20 offers an opportunity to do something better than just swapping one tool for another.

Maybe the best architecture isn’t the one that has a specialized solution for every small problem.

Maybe it’s the one where you can solve real problems with fewer pieces, without losing control over what happens inside the cluster.

And, come on, if we already have enough work administrating Kubernetes, removing some boxes from the list doesn’t seem like a bad idea.