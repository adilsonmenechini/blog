---
title: "Kubernetes precisa mesmo do kube-proxy? O que muda quando o eBPF assume o networking"
date: 2026-10-21
draft: false
tags: ["Kubernetes", "Cilium", "eBPF", "Networking", "Linux", "Performance", "Cloud Native"]
summary: "O kube-proxy é obrigatório? Com eBPF, o Cilium implementa o encaminhamento de Services no próprio kernel Linux. Antes de remover componentes, entenda o caminho do pacote, onde o modelo tradicional custa caro e quando a migração vale a pena."
---

Durante anos, tratar o kube-proxy como uma peça obrigatória de qualquer cluster Kubernetes parecia tão natural quanto instalar um runtime de containers ou configurar um CNI. Você cria um cluster, instala os componentes de rede, e o kube-proxy está lá, fazendo seu trabalho silenciosamente.

Mas e se uma parte importante dessa arquitetura pudesse ser eliminada?

É exatamente o que algumas implementações modernas de networking para Kubernetes estão fazendo. Com eBPF, projetos como o Cilium conseguem implementar o encaminhamento de tráfego de Services diretamente no kernel Linux, sem depender do kube-proxy e de suas regras tradicionais de iptables.

A promessa é interessante: menos processamento desnecessário, maior controle sobre o caminho dos pacotes, observabilidade integrada e uma arquitetura que pode escalar melhor em determinados cenários.

Só que existe um detalhe importante. Trocar uma arquitetura por outra não é automaticamente uma otimização. Antes de sair removendo componentes do cluster, precisamos entender o problema que estamos tentando resolver.

Vamos acompanhar o caminho de um pacote, entender onde o modelo tradicional começa a custar caro, descobrir o que o eBPF realmente faz e, finalmente, responder à pergunta que interessa: quando vale a pena abandonar o kube-proxy?

## 1. A ilusão do Service IP

Comecemos pelo básico.

No Kubernetes, quando criamos um Service, normalmente recebemos um endereço IP virtual, conhecido como ClusterIP.

Imagine esta configuração:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: minha-api
spec:
  selector:
    app: minha-api
  ports:
    - port: 80
      targetPort: 8080
  type: ClusterIP
```

O Service pode receber um endereço como `10.96.0.100`. Esse endereço representa a entrada lógica para um conjunto de Pods, e não necessariamente um endereço configurado em uma interface de rede.

Se três Pods atendem ao Service, o cliente não precisa conhecer os endereços individuais deles. Ele acessa o Service, e a infraestrutura de rede encaminha a conexão para um dos backends elegíveis.

É uma abstração conveniente. O consumidor conhece um endereço estável, enquanto os Pods podem nascer, morrer, mudar de IP e ser substituídos sem exigir que cada cliente atualize sua configuração.

Mas alguém precisa transformar essa abstração em tráfego de verdade.

Tradicionalmente, essa é uma das responsabilidades do kube-proxy.

Ele acompanha informações de Services e EndpointSlices pela API do Kubernetes e programa mecanismos de encaminhamento no nó. Dependendo do modo utilizado, isso envolve regras de iptables, IPVS ou outro mecanismo compatível com a implementação.

No modo iptables, por exemplo, as regras permitem reconhecer o destino virtual, selecionar um backend e realizar a tradução de endereço necessária.

O caminho simplificado fica assim:

```text
Cliente
   |
   v
Service IP: 10.96.0.100:80
   |
   v
Regras de encaminhamento no nó
   |
   v
Seleção de um backend
   |
   v
Pod: 10.244.1.10:8080
```

O Service IP não precisa existir como endereço atribuído a uma interface para funcionar. O plano de dados implementa o comportamento necessário para que o tráfego destinado a ele seja encaminhado corretamente.

É uma solução elegante. E funcionou durante anos em clusters de todos os tamanhos.

Então, qual é o problema?

## 2. Quando uma solução simples começa a custar caro

Imagine um cluster com milhares de Services, dezenas de milhares de Pods e uma quantidade enorme de endpoints mudando constantemente.

O problema não é simplesmente o número de Pods. O custo depende da quantidade de regras, do formato delas, da frequência das alterações, da distribuição dos endpoints e do caminho percorrido pelos pacotes.

No modo tradicional baseado em iptables, o kube-proxy mantém regras que representam Services e seus backends. Em clusters grandes, essa configuração pode crescer significativamente.

E existe um custo adicional: quando a configuração muda, as regras precisam ser reconciliadas e atualizadas. Em determinados cenários, isso pode aumentar o tempo de convergência e consumir CPU durante operações de atualização.

Aqui está a distinção que importa: uma coisa é encaminhar um pacote; outra é manter milhares de destinos virtuais, dezenas de milhares de endpoints e suas alterações representados de maneira eficiente.

O iptables não é simplesmente uma lista ingênua que sempre percorre todas as regras para cada pacote. O custo real depende da organização das chains, dos mecanismos utilizados pelo kernel, das regras geradas e do caminho de execução. Ainda assim, o volume de regras e o trabalho de atualização podem se tornar um gargalo em determinadas topologias.

Também não adianta olhar apenas para o encaminhamento de pacotes. Um cluster pode apresentar problemas durante atualizações em massa mesmo quando sua latência normal parece perfeitamente aceitável.

É por isso que, em infraestrutura de grande escala, precisamos olhar para duas dimensões diferentes:

- **Data plane**: quanto custa processar o tráfego enquanto ele circula?
- **Control plane de rede**: quanto custa manter o estado e atualizar as regras quando a infraestrutura muda?

Uma arquitetura pode ser eficiente em uma dimensão e ruim na outra.

E é aqui que entra o eBPF.

## 3. eBPF: colocar a lógica de rede dentro do kernel

eBPF significa extended Berkeley Packet Filter. Apesar do nome histórico, sua utilização moderna vai muito além da filtragem de pacotes.

Ele permite executar programas verificados dentro do kernel Linux, associados a pontos de execução específicos. Dependendo do tipo de programa e do hook utilizado, esses programas podem inspecionar tráfego, aplicar políticas, coletar métricas e implementar partes do encaminhamento de rede.

O detalhe importante é que não estamos falando de executar uma aplicação convencional no espaço de usuário para tomar uma decisão sobre cada pacote.

O programa eBPF é executado no kernel, próximo do ponto em que a decisão precisa acontecer.

Isso permite implementar caminhos de dados especializados, evitando determinadas etapas de processamento existentes em outras arquiteturas.

Uma das estruturas utilizadas é o eBPF map.

Pense em um map como uma estrutura de dados acessível aos programas eBPF, capaz de armazenar informações como associações entre Services e backends, estado de conexões ou dados necessários à aplicação de políticas.

Um mapa pode utilizar uma tabela hash, por exemplo. Nesse caso, uma consulta média pode apresentar custo próximo de `O(1)`, considerando uma tabela bem dimensionada e operações de hash adequadas.

Mas atenção: isso não significa que todo o processamento de rede passa a ter complexidade `O(1)`. A consulta ao mapa é apenas uma etapa. O caminho completo ainda pode envolver seleção de backend, estado de conexão, políticas, encapsulamento, roteamento e outras operações.

A vantagem não é uma promessa matemática universal. É a possibilidade de construir um caminho de dados mais direto e especializado para o problema em questão.

## 4. Cilium e o caminho até o Pod

O Cilium utiliza eBPF para implementar funcionalidades de networking, segurança e observabilidade no Kubernetes.

Em uma configuração compatível, ele pode substituir o kube-proxy, assumindo o encaminhamento de tráfego dos Services por meio de seus próprios programas e estruturas de dados no kernel.

O fluxo conceitual muda de:

```text
Cliente
   |
   v
Service IP
   |
   v
Regras do kube-proxy
   |
   v
Processamento de NAT e seleção
   |
   v
Pod de destino
```

Para algo semelhante a:

```text
Cliente
   |
   v
Service IP
   |
   v
Hook eBPF no caminho do pacote
   |
   v
Consulta às estruturas de dados
   |
   v
Seleção do backend
   |
   v
Pod de destino
```

O segundo diagrama é deliberadamente simplificado. Os hooks utilizados, as operações executadas e a necessidade de NAT dependem da configuração e do caminho do tráfego. O Cilium não elimina magicamente todo processamento de rede, nem significa que cada pacote percorre sempre uma única consulta a um mapa.

O que ele oferece é uma implementação alternativa do plano de dados, com controle mais direto sobre as decisões de encaminhamento.

Em vez de depender do kube-proxy para manter as regras tradicionais de Services, o Cilium acompanha o estado relevante do Kubernetes e programa suas estruturas e seus programas eBPF.

O resultado é uma arquitetura na qual o processamento pode evitar parte do trabalho associado ao caminho convencional.

E não estamos falando apenas de performance.

## 5. Mais do que velocidade: segurança e observabilidade

Uma das vantagens interessantes do Cilium é que o mesmo ecossistema de eBPF pode ser utilizado para diferentes necessidades de infraestrutura.

### Políticas de rede

O Cilium oferece políticas de rede que permitem controlar quais workloads podem se comunicar, com base em atributos como identidade, labels, direção do tráfego e outros critérios suportados.

Isso ajuda a implementar segmentação entre serviços e reduzir a superfície de comunicação permitida.

Naturalmente, a segurança depende das políticas configuradas, do modelo de identidade, dos pontos de aplicação e dos caminhos efetivamente cobertos. Instalar Cilium não significa que toda a rede estará automaticamente protegida.

### Observabilidade com Hubble

O Hubble utiliza a infraestrutura de observabilidade do Cilium para expor informações sobre fluxos de rede e comunicação entre workloads.

Em vez de investigar um problema exclusivamente a partir de logs de aplicação e capturas manuais de pacotes, podemos obter visibilidade sobre conexões, decisões de política e fluxos observados.

Isso é especialmente útil em ambientes nos quais dezenas ou centenas de serviços se comunicam e o problema não está necessariamente dentro da aplicação.

### Balanceamento de carga

O Cilium também implementa mecanismos de balanceamento para tráfego destinado a Services, com estratégias e comportamentos que dependem da configuração.

A seleção de backend pode ocorrer no plano de dados, utilizando informações mantidas no kernel.

Isso não significa que todas as estratégias estejam disponíveis em qualquer configuração, nem que um algoritmo específico seja sempre superior. Afinidade de sessão, distribuição de carga, estado de conexões e requisitos da aplicação continuam influenciando a escolha.

O ponto central é que networking, segurança e observabilidade podem compartilhar uma arquitetura integrada.

Isso pode simplificar a operação, mas também aumenta a importância de compreender a implementação, os requisitos do kernel e as ferramentas de diagnóstico utilizadas.

## 6. O que significa realmente eliminar o kube-proxy?

Aqui vale evitar uma confusão comum.

O kube-proxy não é o Kubernetes inteiro. Ele é um componente que implementa parte do comportamento de rede associado aos Services.

O Kubernetes continua precisando de seus mecanismos de controle, de seus objetos Service e EndpointSlice e de uma implementação de rede capaz de conectar os workloads.

Quando o Cilium opera em modo de substituição do kube-proxy, ele assume as responsabilidades correspondentes de encaminhamento que foram configuradas para esse modo.

Isso não significa eliminar o CNI, remover todos os mecanismos de NAT ou fazer com que todo o tráfego deixe de passar pelo kernel.

Também não significa que o iptables desapareça completamente do nó. Ele pode continuar sendo utilizado por outras partes do sistema operacional, por ferramentas de firewall ou por componentes que não fazem parte do caminho de Services substituído pelo Cilium.

A expressão *kube-proxy replacement* é mais precisa do que interpretar a mudança como uma máquina Linux completamente livre de iptables.

A distinção é importante porque arquitetura não se resume a remover um processo. É preciso entender quais responsabilidades foram transferidas, quais permanecem e como o novo caminho é implementado.

## 7. Então, o desempenho melhora quanto?

Essa é a pergunta que costuma aparecer depois de uma demonstração impressionante.

A resposta honesta é: depende.

O Cilium pode reduzir determinados custos de encaminhamento, melhorar o comportamento em cenários com grande quantidade de Services e oferecer vantagens em cargas de trabalho específicas. Mas não existe um percentual universal de ganho que possa ser aplicado a qualquer cluster.

O resultado depende de fatores como:

- Quantidade de Services e endpoints.
- Taxa de criação, remoção e atualização de workloads.
- Volume de tráfego e tamanho dos pacotes.
- Tráfego dentro do mesmo nó ou entre nós.
- Necessidade de encapsulamento e tradução de endereços.
- Configuração de políticas de segurança.
- Modelo de balanceamento de carga.
- Versão do kernel Linux e do Cilium.
- Hardware, drivers e configuração da infraestrutura.

Se o cluster estiver limitado por consultas ao banco de dados, processamento da aplicação ou latência de uma dependência externa, mudar o plano de dados de rede pode produzir pouco ou nenhum ganho perceptível para o usuário.

Da mesma forma, não faz sentido presumir que qualquer configuração tradicional seja lenta. Um cluster pequeno, com poucas regras e baixa taxa de alteração, pode funcionar muito bem com kube-proxy.

Antes de decidir, eu mediria pelo menos quatro coisas:

1. CPU consumida pelos componentes de networking.
2. Latência e throughput do tráfego relevante.
3. Tempo de convergência após mudanças nos Services e endpoints.
4. Comportamento do cluster durante picos de criação e remoção de workloads.

Benchmarks precisam representar a carga real e comparar configurações equivalentes. Também é necessário testar conectividade, políticas, acesso externo, DNS e os modos de tráfego utilizados pela aplicação.

Sem essas medidas, trocar a arquitetura pode ser apenas uma maneira mais sofisticada de mudar algo que não era o problema.

## 8. Quando vale a pena adotar Cilium?

A decisão depende menos de uma disputa entre tecnologias e mais das necessidades do ambiente.

### Cluster pequeno ou convencional

Se você opera um cluster com poucas dezenas de nós, uma quantidade moderada de Services e uma aplicação que não apresenta gargalos de networking, não há razão automática para migrar.

O kube-proxy continua sendo uma opção válida. Uma implementação tradicional pode ser simples, previsível e suficiente para o trabalho.

### Cluster grande e com muitas mudanças

Se o ambiente tem grande volume de Services e endpoints, atualizações frequentes, pressão de CPU relacionada à rede ou problemas de convergência, vale investigar alternativas.

Nesse cenário, Cilium pode oferecer benefícios tanto no encaminhamento quanto na forma de manter o estado da rede.

Mas a decisão deve vir acompanhada de medições e testes de carga, não apenas da quantidade de nós.

### Ambientes que exigem segurança e visibilidade

Mesmo quando o desempenho não é o principal problema, os recursos de políticas de rede, identidade e observabilidade podem justificar a adoção.

Nesse caso, a comparação precisa considerar a arquitetura de segurança existente, a experiência operacional da equipe e os requisitos de auditoria e diagnóstico.

Em qualquer cenário, a migração precisa considerar compatibilidade com o kernel, configuração do CNI, balanceamento, roteamento, integração com firewalls e procedimentos de recuperação.

Uma mudança no plano de dados de rede afeta uma parte fundamental da infraestrutura. O ideal é testar em um ambiente representativo, validar os caminhos de tráfego e planejar uma estratégia de reversão.

## 9. A lição é maior do que o kube-proxy

O mais interessante nessa mudança não é simplesmente trocar iptables por eBPF.

É perceber que componentes considerados fundamentais em uma arquitetura podem ser substituídos quando entendemos exatamente qual problema resolvem e quanto custa mantê-los.

O kube-proxy cumpriu, e ainda pode cumprir, um papel importante no Kubernetes. O modelo tradicional não foi um erro. Foi uma solução prática para implementar uma abstração necessária.

O eBPF permite explorar outro ponto de integração com o kernel e construir caminhos de dados especializados. O Cilium aproveita essa possibilidade para combinar networking, segurança e observabilidade em uma implementação integrada.

Isso não torna toda arquitetura anterior obsoleta, nem transforma eBPF em uma solução universal. Significa que agora temos outras opções, com diferentes custos e benefícios.

Minha conclusão é simples: não troque o kube-proxy porque alguém prometeu que eBPF é mais rápido. Entenda o caminho dos pacotes, identifique o gargalo, meça o comportamento do cluster e só então escolha a arquitetura.

A melhor infraestrutura não é necessariamente a que utiliza a tecnologia mais recente. É a que resolve o problema real com o menor custo operacional, desempenho adequado e complexidade que sua equipe consegue administrar.

E fica uma pergunta para levar adiante: se conseguimos repensar uma parte tão tradicional do networking do Kubernetes ao aproximar a lógica de decisão do kernel, quais outros gargalos da infraestrutura estamos aceitando apenas porque sempre foram implementados dessa maneira?

## Referências para aprofundamento

- [Cilium: documentação oficial](https://docs.cilium.io/)
- [Cilium: kube-proxy replacement](https://docs.cilium.io/en/stable/network/kubernetes/kubeproxy-free/)
- [Cilium: visão geral de eBPF](https://docs.cilium.io/en/stable/bpf/)
- [Kubernetes: Services, Load Balancing e Networking](https://kubernetes.io/docs/concepts/services-networking/service/)
- [Linux Kernel: documentação de eBPF](https://docs.kernel.org/bpf/)
