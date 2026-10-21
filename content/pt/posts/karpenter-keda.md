---
title: "Kubernetes mais barato e eficiente: combinando Karpenter e KEDA"
date: 2026-10-21
draft: false
tags: ["Kubernetes", "FinOps", "Autoscaling"]
summary: "Escalar a aplicação na demanda e dimensionar a infraestrutura por trás dela são problemas diferentes. Com KEDA e Karpenter trabalhando juntos, o cluster escala quando precisa, reduz quando pode e custa menos para entregar o mesmo resultado."
---

Você já parou para pensar quanto dinheiro pode estar gastando com um cluster Kubernetes que fica ligado o dia inteiro, mesmo quando quase não tem trabalho para executar?

Esse é um problema comum em ambientes cloud. Provisionamos infraestrutura para suportar picos de demanda, mas, quando o movimento diminui, continuamos pagando por recursos que não estamos utilizando.

A boa notícia é que podemos atacar esse problema em duas frentes: escalar as aplicações de acordo com a demanda e ajustar a infraestrutura para atender exatamente ao que elas precisam.

É aqui que entram KEDA e Karpenter.

## O problema não é só ter máquinas grandes demais

Imagine uma aplicação que processa transações financeiras recebidas por uma fila do Amazon SQS.

Durante boa parte do dia, poucas mensagens chegam. Em determinados horários, porém, o volume aumenta bastante e precisamos processar tudo rapidamente.

Se mantivermos dezenas de pods e máquinas disponíveis o tempo inteiro, gastaremos dinheiro com capacidade ociosa.

Se provisionarmos poucos recursos, corremos o risco de acumular mensagens e aumentar o tempo de processamento.

Precisamos encontrar um equilíbrio entre custo, capacidade e desempenho.

E tentar resolver tudo apenas aumentando ou diminuindo o número de máquinas não é suficiente.

## KEDA: escalar a aplicação de acordo com a demanda

O KEDA (Kubernetes Event-Driven Autoscaling) permite escalar aplicações com base em eventos e métricas externas.

Em vez de olhar apenas para CPU e memória, podemos usar sinais como:

- Quantidade de mensagens em uma fila SQS.
- Lag de consumidores no Kafka.
- Métricas externas disponibilizadas por sistemas de monitoramento.
- Eventos provenientes de outros serviços suportados.

Imagine que nossa aplicação consuma mensagens de uma fila SQS.

Quando o volume aumenta, o KEDA disponibiliza métricas para o Kubernetes Horizontal Pod Autoscaler (HPA), que ajusta a quantidade de réplicas conforme as regras configuradas.

Quando a demanda diminui, a quantidade de pods pode ser reduzida. Em cenários compatíveis, podemos inclusive escalar até zero réplicas e voltar a executar quando novos eventos chegarem.

Isso significa que não precisamos manter uma aplicação processadora ativa quando não há trabalho a fazer, desde que ela suporte esse modelo e que os requisitos de latência permitam.

Mas existe um detalhe importante: reduzir a quantidade de pods não significa necessariamente reduzir a quantidade de máquinas.

Se os pods desaparecerem e os nós continuarem ligados, ainda estaremos pagando pela infraestrutura.

É justamente aqui que o Karpenter entra na história.

## Karpenter: provisionar a infraestrutura que realmente precisamos

O Karpenter atua em outra camada: a infraestrutura do cluster.

Quando existem pods pendentes porque não há capacidade disponível, ele analisa os requisitos desses workloads e procura provisionar nós compatíveis.

Essa decisão considera informações como:

- Requests de CPU e memória dos pods.
- Famílias e tamanhos de instâncias permitidos.
- Arquiteturas de processador compatíveis.
- Zonas de disponibilidade.
- Restrições de capacidade e políticas de provisionamento.
- Opções de compra, como instâncias On-Demand e Spot, quando configuradas.

A grande vantagem é não precisar manter manualmente um grupo de nós para cada combinação de instância que desejamos utilizar.

Em ambientes AWS, por exemplo, o Karpenter pode selecionar entre diferentes tipos de instância permitidos pelas configurações do cluster, em vez de depender exclusivamente de uma estratégia baseada em grupos fixos de Auto Scaling.

Ele também pode consolidar workloads quando isso for seguro e economicamente vantajoso, substituindo nós subutilizados por uma configuração mais eficiente.

O objetivo não é simplesmente criar mais máquinas. É disponibilizar a capacidade necessária e evitar manter recursos desnecessários.

## O melhor resultado acontece quando usamos os dois juntos

Agora imagine o fluxo completo.

Uma fila começa a receber milhares de mensagens.

1. O KEDA identifica o aumento da demanda e disponibiliza as métricas para o HPA.
2. O HPA aumenta a quantidade desejada de pods.
3. Se não houver capacidade suficiente, alguns pods ficam pendentes.
4. O Karpenter identifica a necessidade e provisiona nós compatíveis.
5. Quando as novas máquinas ficam disponíveis, o scheduler distribui os pods.
6. Depois que a fila é processada e a demanda diminui, o KEDA reduz as réplicas.
7. O Karpenter pode consolidar ou remover nós que deixaram de ser necessários, respeitando suas políticas e as restrições dos workloads.

Cada ferramenta resolve uma parte diferente do problema.

O KEDA reage à demanda da aplicação. O Karpenter ajusta a capacidade da infraestrutura para acomodar essa demanda.

Essa combinação permite trabalhar com escalabilidade em duas camadas, em vez de tentar resolver tudo com uma única ferramenta.

## E as instâncias Spot? Vale a pena utilizar?

As instâncias Spot podem reduzir bastante o custo de workloads tolerantes a interrupções, mas exigem planejamento.

O Karpenter pode trabalhar com opções Spot e On-Demand, desde que elas sejam permitidas nas configurações dos NodePools.

Quando uma interrupção Spot é anunciada e o mecanismo de interrupção está devidamente configurado, o Karpenter pode tentar substituir a capacidade afetada.

Isso não significa que a interrupção será invisível. A substituição depende da disponibilidade de capacidade, das configurações do cluster e do tempo necessário para iniciar e preparar os novos nós.

Por isso, aplicações críticas precisam considerar tolerância a falhas, múltiplas zonas de disponibilidade, tratamento de interrupções e reprocessamento seguro de mensagens.

A estratégia mais eficiente não é usar Spot em tudo. É identificar quais workloads conseguem aproveitar essa modalidade sem comprometer os requisitos do negócio.

## Escalar para zero também exige cuidado

Existe outro ponto interessante nessa arquitetura: a possibilidade de manter determinadas aplicações sem réplicas quando não existe demanda.

Para processadores de filas, isso pode representar uma economia relevante.

Mas escalar para zero não é gratuito nem instantâneo.

Quando um novo evento chega, pode haver um intervalo até o KEDA solicitar novas réplicas, o Kubernetes agendar os pods e o Karpenter provisionar nós caso não exista capacidade disponível.

Se a aplicação precisa responder em milissegundos, talvez seja necessário manter alguma capacidade mínima aquecida.

Se ela processa tarefas assíncronas e tolera alguns segundos ou minutos de espera, escalar para zero pode ser uma estratégia excelente.

A decisão depende do perfil do workload, não apenas da possibilidade técnica de desligá-lo.

## O que realmente faz diferença na redução de custos?

Instalar KEDA e Karpenter não garante uma conta menor por si só.

O resultado depende de como configuramos e operamos o cluster.

Algumas práticas fazem bastante diferença:

- Definir requests de CPU e memória coerentes com o consumo real das aplicações.
- Configurar gatilhos de escalabilidade que representem a demanda do negócio.
- Permitir flexibilidade de instâncias sem violar os requisitos de compatibilidade.
- Utilizar Spot nos workloads adequados.
- Configurar políticas de consolidação que respeitem disponibilidade e interrupções.
- Medir custos, utilização, latência e tempo de processamento antes e depois das mudanças.

Também é importante observar que KEDA e Karpenter não substituem o dimensionamento correto das aplicações. Se os requests estiverem incorretos ou os gatilhos mal configurados, a automação pode tomar decisões inadequadas.

A meta não deve ser simplesmente reduzir o número de máquinas. Deve ser reduzir o custo por unidade de trabalho processada, mantendo o desempenho e a confiabilidade esperados.

## No fim, a ideia é simples

Kubernetes oferece mecanismos poderosos de escalabilidade, mas a eficiência financeira depende de ajustar a aplicação e a infraestrutura de forma coordenada.

O KEDA ajuda a responder à pergunta: quantas réplicas precisamos para processar a demanda atual?

O Karpenter ajuda a responder a outra: qual infraestrutura precisamos para executar essas réplicas?

Quando combinamos os dois, conseguimos aproximar o consumo de recursos da demanda real, aproveitando melhor a capacidade disponível e reduzindo desperdícios.

Porque, no final das contas, não basta ter um cluster que escala.

O objetivo é ter um cluster que escala quando precisa, reduz quando pode e custa menos para entregar o mesmo resultado.
