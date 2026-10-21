---
title: "Your AI agents don't need API keys. They need identity."
date: 2026-10-21
draft: false
tags: ["AI Agents", "Security", "SPIFFE", "Zero Trust"]
summary: "API keys stored in environment variables don't prove who runs what. With SPIFFE and SPIRE, identity becomes a verifiable property of the workload, which completely changes the security of autonomous agents."
---

We are building AI systems that execute code, query databases, call APIs, access cloud services, and delegate tasks to other agents. In some cases, these systems already operate with enough autonomy to run entire sequences of actions without a human approving each step.

But there is a basic problem in this architecture: how do these agents prove who they are?

In most traditional systems, the answer is disappointingly simple: someone puts an API key in an environment variable, injects a token into the container, or configures a permanent credential in the service. The agent gets access and starts working.

That works until something goes wrong.

A malicious prompt convinces the agent to call the wrong tool. A vulnerability allows reading environment variables. A compromised container exposes its credentials. Suddenly, a secret created for one specific service can be used by someone who should not have access to it.

The problem is not just the AI model. It is the identity architecture we wrapped around it.

The solution goes through an old idea in infrastructure security that takes on new importance with autonomous agents: identity should not be a secret stored inside an application. It should be a verifiable property of the workload that is running.

That is where SPIFFE and SPIRE come in.

## The problem of placing secrets inside agents

Imagine an agent responsible for researching documents, querying a vector database, and executing tools through the Model Context Protocol, MCP.

To do its job, it needs a set of permissions:

- Call an internal API.
- Search documents for a given client.
- Invoke specific tools.
- Access a service hosted in the cloud.

The conventional approach is to hand credentials to the agent and trust that it will use them correctly.

But an AI agent is not a traditional application in operational terms. It interprets instructions, receives external content, selects tools, and may produce sequences of calls that its developers never anticipated.

An attacker does not necessarily need to compromise the whole server. Depending on the available permissions, it is enough to induce the agent to perform an improper action.

If a permanent credential is accessible to the process, the attacker may try to extract it or abuse it. And if they manage to copy it, the credential can remain usable even after the original execution ends.

There is another problem: an API key usually identifies a credential, not the integrity of the process using it. It does not prove, by itself, which binary is running, which container it lives in, which namespace it belongs to, or whether it should have access to that resource.

The right question stops being just "what is this agent's key?" and becomes:

How can the system verify this workload's identity and decide, on every connection, what it is authorized to do?

## SPIFFE and SPIRE: identity as infrastructure

SPIFFE stands for Secure Production Identity Framework for Everyone. It is a specification for identifying workloads in a standardized way.

SPIRE is an implementation of that architecture. It provides the mechanisms needed to attest workloads, issue cryptographic identities, and distribute trust information.

The central piece is the SVID, or SPIFFE Verifiable Identity Document.

An SVID can be an X.509 certificate or a signed JWT token. Instead of relying on a permanent key embedded in the application, the workload receives an identity issued dynamically after passing the configured checks.

A SPIFFE identity may look like this:

```
spiffe://example.org/agent/mcp-executor
```

That identifier represents an identity inside a trust domain. It is not a password: its usefulness depends on the associated cryptographic credentials and on the policies enforced by the services that accept it.

The general flow works like this:

1. The SPIRE server verifies the identity of the node where the workload is running.
2. The local SPIRE agent identifies attributes of the process or container requesting credentials.
3. The server compares those attributes against the authorized registration entries.
4. If the conditions are met, the workload receives a short-lived SVID.
5. The workload uses that identity to authenticate to services that trust the issuing authority.

The important detail is that the application does not need to carry a permanent key to prove its identity. It can obtain and renew its credentials dynamically through the local SPIRE agent.

That changes how we think about authentication.

## What happens inside the SPIRE Server?

The SPIRE Server is the control plane responsible for managing trust and issuing identities.

Its Go implementation is organized into specialized components.

The server initializes its gRPC endpoints, integrates plugins, accesses the registration store, and maintains the certificate authority mechanisms needed to sign credentials.

The identity issuance process relies on a few distinct steps.

### 1. First, the node must prove its identity

Before trusting an agent, the system needs to verify the infrastructure where it is running.

On Kubernetes, this can involve projected service account tokens. In cloud environments, instance identity documents or equivalent mechanisms supported by the attestation plugins can be used.

The server validates the evidence according to the configured mechanism and establishes the identity of the node.

From then on, the SPIRE agent can communicate with the server using its identity and an authenticated channel.

### 2. Then, the process must be identified

A trusted node does not mean that every process running on it is trusted.

The SPIRE agent queries workload attributes, which can include namespace, service account, container image, and other properties supported by the environment.

Those attributes are compared against the authorized identity registration entries.

For example, it is possible to distinguish a tool executor from an agent responsible for querying documents, even if both run in the same cluster.

Security depends on the quality of those selectors, on the integrity of the attestation, and on the precision of the configured rules.

### 3. Finally, the server issues the credential

When the request is authorized, the SPIRE Server signs the appropriate SVID.

For X.509, that results in a certificate that can be used in mutual TLS connections. For JWT, it results in a signed token that can be presented to compatible services.

The certificate or token has limited validity. The application must renew its credentials as needed, instead of relying indefinitely on a static secret.

SPIRE also manages the rotation of signing keys and the distribution of trust bundles.

It is identity infrastructure, not just a token generator.

## What changes in agent-to-agent communication?

Consider an orchestrator agent that needs to call an MCP server responsible for executing internal tools.

In the conventional architecture, the MCP server may require a shared API key or a manually configured token.

With SPIFFE/SPIRE, both workloads can present verifiable identities through X.509 certificates.

During an mTLS connection:

1. The client presents its cryptographic identity.
2. The server presents its own identity.
3. Both sides validate the certificates and the trust chain.
4. Authorization policies determine whether that identity may perform the requested operation.

This provides mutual authentication and encryption in transit, and reduces the dependence on shared secrets.

But there is one fundamental distinction: authenticating an agent does not mean authorizing all of its actions.

An agent identified as `mcp-executor` may still be authorized to call only specific tools. The MCP server must verify that restriction and truly enforce it.

Identity answers "who is calling?". Authorization answers "what is that identity allowed to do?".

Mixing the two is a very efficient way to build an apparently secure architecture that keeps granting excessive permissions.

## And when the agent needs to access the cloud?

The problem does not end with calls between internal services.

Agents frequently need to access managed services, storage, queues, and AI platforms hosted in public clouds.

Storing permanent IAM keys inside containers is a particularly risky alternative.

A better approach is to use identity federation.

The agent requests a JWT SVID intended for the audience expected by the cloud provider. The cloud identity service validates the issuer, the signature, the audience, and the configured trust conditions. If everything checks out, the token can be exchanged for temporary credentials with limited permissions.

The result is a chain of trust between the workload and the cloud service, without needing to distribute a permanent key to each agent.

This setup requires explicit integration with the provider, proper trust policies, and least-privilege permissions. It is not enough to issue any JWT and expect the cloud to accept it.

Still, that model is far more interesting than copying secrets into dozens of applications.

## Identity does not solve everything

It would be tempting to conclude that, after installing SPIRE, the security problem of agents is solved.

It is not.

If a legitimate agent is manipulated through prompt injection, it can still attempt actions that fall within the permissions it received. A valid SVID does not prevent an authorized process from making a bad decision.

SPIRE reduces certain identity risks and credential exposure, but it does not replace the other security layers.

A serious deployment needs to combine:

- Specific identities per workload.
- Short-lived credentials.
- Minimum permissions per tool and service.
- Rigorous attestation and registration rules.
- Protection of signing keys, preferably integrated with appropriate key management systems.
- Auditing of credential issuance and administrative operations.
- Input controls, argument validation, and execution limits for tools.
- Tests that verify tenant isolation.

It is also necessary to remember that a compromised workload can use its legitimate identity while it remains valid and authorized. Revocation, containment, and incident response remain necessary.

Cryptographic identity is one layer of the security architecture, not a replacement for it.

## The architecture that makes sense for autonomous agents

A practical deployment can start with the SPIRE Server, the agents distributed across nodes, and specific registration entries for each type of workload.

Applications use SPIFFE-compatible SDKs to obtain their SVIDs through the local Unix socket. Internal services validate identities and enforce authorization policies. When needed, federation extends trust to other domains or cloud providers.

In production, the stage also includes registration persistence, control plane availability, key management, credential rotation, bundle distribution, and observability.

The goal is not merely to make the first certificate work. It is to keep the infrastructure secure when there are hundreds of agents, multiple tenants, multiple environments, and constant changes in workloads.

That is the moment when identity stops being a configuration detail and becomes a central capability of the platform.

## The next problem is not issuing credentials. It is limiting autonomy.

AI agents are making it easier to build systems that perform tasks once reserved for human operators or rigidly programmed applications.

But operational autonomy should not mean unrestricted access.

The more tools an agent can invoke, the more important it becomes to distinguish its identity, its context, and its permissions. Security must follow the agent during execution, instead of relying on a secret distributed at deploy time.

SPIFFE and SPIRE offer a solid foundation for this model: verifiable identities, temporary credentials, and explicit trust relationships between workloads.

This does not eliminate prompt injection, bugs, or wrong decisions. It eliminates or significantly reduces a class of risks caused by permanent credentials and poorly defined identity.

The mindset shift is simple, even though the implementation requires care:

Stop asking which API key to hand the agent. Start asking how it proves who it is, why it received that identity, and what actions that identity is authorized to perform.

In an infrastructure with autonomous agents, that difference stops being just a good practice. It becomes part of the fundamental design of the system.
