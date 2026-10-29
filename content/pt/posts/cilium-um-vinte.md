---
title: "Cilium 1.20: será que dá para desligar mais umas caixas do Kubernetes?"
date: 2026-09-21
draft: false
tags: ["Cilium", "Kubernetes", "Gateway API", "eBPF", "Networking"]
summary: "O Cilium 1.20 traz TCPRoute, UDPRoute, ExternalAuth e mais recursos que permitem consolidar gateway, autenticação e exposição de serviços TCP/UDP numa única plataforma. Será que conseguimos simplificar a arquitetura?"
---
{{< audio slug="cilium-um-vinte" >}}

Tem uma coisa curiosa em infraestrutura: a gente instala uma ferramenta para resolver um problema, depois instala outra para resolver o problema que a primeira não resolve, e mais uma para integrar as duas. Quando percebe, está administrando cinco componentes para fazer algo que parecia simples no começo.

No Kubernetes, isso acontece o tempo todo.

Você instala uma CNI para cuidar da rede. Depois vem um Ingress Controller para publicar suas aplicações. Aí aparece a necessidade de autenticação e você coloca um proxy na frente de tudo. Para alguns serviços TCP, entra mais uma configuração de LoadBalancer. E, quando a comunicação entre os serviços começa a ficar complicada, alguém sugere instalar um service mesh.

Pronto. Você tem uma plataforma.

E também tem cinco coisas para atualizar, monitorar, configurar e explicar para quem entrar no time.

É por isso que o Cilium 1.20 me chamou a atenção. Não é só porque ganhou recursos novos, mas porque começa a tornar uma pergunta bastante razoável: será que precisamos mesmo de tantas peças separadas para administrar a rede de um cluster Kubernetes?

## Primeiro, o ingress-nginx saiu de cena. E agora?

Em março de 2026, o Kubernetes arquivou o ingress-nginx depois de uma sequência de problemas de segurança, incluindo uma vulnerabilidade crítica de execução remota de código.

Isso deixou muita gente com uma pergunta bem prática: para onde migrar?

A resposta mais interessante não é simplesmente escolher outro Ingress Controller e seguir a vida. É aproveitar a oportunidade para rever a arquitetura.

A Gateway API já vinha ganhando espaço como alternativa ao modelo tradicional de Ingress. Ela oferece uma maneira mais organizada de declarar como o tráfego entra no cluster, quais portas ficam disponíveis, para onde as requisições vão e quem pode administrar cada parte dessa configuração.

Só que existia um detalhe.

Quando você precisava publicar uma aplicação HTTP, tudo bem. Mas e quando queria expor um PostgreSQL? Ou um Redis? Ou algum serviço que falasse UDP?

Aí começavam as exceções. Um Service LoadBalancer aqui, uma configuração manual ali, mais um componente para autenticação acolá.

Ou seja: você adotava uma API moderna para organizar o tráfego e continuava mantendo um monte de coisas por fora.

O Cilium 1.20 ajuda a diminuir essa diferença.

## O que chegou de tão interessante no Cilium 1.20?

Vamos deixar a lista de novidades de lado por um instante e olhar para o que realmente muda na vida de quem administra o cluster.

O lançamento traz suporte a **TCPRoute** e **UDPRoute**, integração de autenticação externa por meio do filtro **ExternalAuth** e melhorias no modelo de gerenciamento de listeners e TLS de backend.

Traduzindo para o dia a dia:

- **TCPRoute e UDPRoute**: permitem colocar serviços TCP e UDP no mesmo modelo declarativo usado para gerenciar o tráfego do gateway.
- **ExternalAuth**: permite integrar um serviço externo de autenticação ou autorização ao fluxo do gateway.
- **ListenerSets**: facilitam a delegação de listeners para diferentes equipes e namespaces.
- **BackendTLSPolicy**: ajuda a declarar como o gateway estabelece conexões TLS com os serviços de backend.
- **CORS em HTTPRoute**: permite configurar esse comportamento diretamente na rota, em vez de depender exclusivamente da aplicação ou de componentes adicionais.

Não significa que todos esses recursos estejam no mesmo nível de maturidade, nem que você deva sair habilitando tudo em produção. Mas, juntos, eles apontam para uma direção interessante: menos configurações espalhadas e mais coisas administradas pelo mesmo modelo.

E duas dessas mudanças merecem uma conversa à parte.

## TCP e UDP: finalmente podemos parar de tratar cada serviço como uma exceção?

Imagine que você tem um cluster com aplicações web, um PostgreSQL, um Redis e um broker de mensagens.

O tráfego HTTP já passa pelo gateway. Mas os outros serviços precisam de portas e protocolos diferentes. Tradicionalmente, você acaba criando Services LoadBalancer ou NodePort e administrando essas exposições separadamente.

Funciona? Claro.

É a melhor maneira de organizar tudo quando a infraestrutura cresce? Nem sempre.

Com TCPRoute e UDPRoute, o Cilium 1.20 permite declarar essas rotas usando a Gateway API. Você passa a ter um modelo mais uniforme para administrar o tráfego que entra no cluster, mesmo quando ele não é HTTP.

Existe um detalhe técnico legal aqui: a implementação L4 do Cilium não precisa mandar esse tráfego pelo proxy Envoy de camada 7. As rotas são reconciliadas em Services e EndpointSlices gerenciados pelo operador, que alimentam o balanceamento de serviços baseado em eBPF.

Isso significa que você não precisa adicionar um salto pelo proxy L7 só para encaminhar uma conexão TCP.

Também existe suporte à propagação de pesos dos backends. Com o peso adequado, é possível deixar de enviar novas conexões para um backend e permitir que as existentes terminem, conforme o comportamento da implementação.

Pense em uma atualização de serviço. Você quer retirar uma instância do balanceamento sem necessariamente derrubar todas as conexões que ela já atende.

Esse tipo de operação fica muito mais interessante quando faz parte do modelo de gerenciamento do tráfego, em vez de depender de uma coleção de ajustes manuais.

A grande vantagem, portanto, não é apenas desempenho. É poder administrar mais coisas de maneira consistente.

## E a autenticação? Mais um proxy a menos?

Aqui está outra situação bastante comum.

Você publica uma aplicação interna e quer exigir autenticação antes de deixar alguém acessá-la. Talvez utilize um serviço de SSO, um autorizador próprio ou alguma integração com tokens.

Uma solução tradicional é colocar um proxy de autenticação entre o gateway e a aplicação. Ele recebe a requisição, consulta o serviço responsável pela decisão e libera ou bloqueia o acesso.

Funciona muito bem. O problema é que esse proxy vira mais um serviço para manter.

Com o filtro ExternalAuth, o Cilium permite declarar essa integração na configuração do gateway. A decisão continua podendo ser tomada por um serviço externo, mas o fluxo de autenticação fica integrado ao gerenciamento das rotas.

Perceba a diferença: não estamos necessariamente eliminando o sistema de autenticação. Estamos eliminando a necessidade de manter um componente intermediário separado quando ele existe apenas para conectar o gateway a esse sistema.

Isso pode simplificar bastante uma plataforma pequena.

Mas atenção: o ExternalAuth tem seu próprio nível de maturidade e precisa ser avaliado antes de ser adotado em produção. Além disso, o serviço externo continua precisando de disponibilidade, monitoramento e políticas adequadas.

Não adianta remover um proxy e descobrir depois que você apenas transferiu o problema para outro lugar.

## Como ficaria uma infraestrutura dessas na prática?

Vamos imaginar uma pequena frota Kubernetes rodando em servidores próprios, com Cilium como CNI.

Hoje, ela tem ingress-nginx para HTTP, Services LoadBalancer para alguns serviços TCP e um proxy adicional para autenticação.

A equipe também mantém políticas de rede para controlar a comunicação entre aplicações.

Não parece uma arquitetura absurda. Na verdade, é bem parecida com o que muita gente montou ao longo dos últimos anos.

O problema é que cada componente tem sua própria maneira de funcionar. Quando aparece uma atualização, você precisa entender o impacto em cada parte. Quando algo falha, precisa descobrir em qual delas está o problema.

Com uma migração bem planejada para a Gateway API, a arquitetura pode ficar mais ou menos assim:

- Um **Gateway** para organizar a entrada do tráfego.
- **HTTPRoute** para aplicações web.
- **TCPRoute e UDPRoute** para serviços que utilizam outros protocolos.
- **ExternalAuth** para integrar a autorização ao fluxo do gateway.
- Políticas de TLS para conexões com backends.
- **Cilium NetworkPolicies** para continuar controlando a comunicação entre workloads.

A ideia é reduzir o número de componentes independentes sem misturar responsabilidades que precisam continuar separadas.

A Gateway API não substitui as políticas de rede. E autenticar alguém na entrada do cluster não significa que essa pessoa ou aplicação deva ter acesso irrestrito a todos os serviços internos.

Cada coisa continua tendo seu papel.

A diferença é que você passa a precisar de menos peças para montar a arquitetura.

## Beleza. Então é só atualizar e apagar o ingress-nginx?

Queria dizer que sim, mas aí seria fácil demais.

A migração é justamente a parte que exige mais cuidado.

Ferramentas como o **ingress2gateway** ajudam a converter recursos Ingress para a Gateway API. Isso é ótimo para reduzir o trabalho mecânico, mas não garante que tudo vai continuar funcionando exatamente como antes.

O problema geralmente está nas pequenas particularidades acumuladas ao longo do tempo.

Sabe aquela anotação que alguém colocou há três anos para reescrever uma URL? Ou aquele snippet personalizado que ninguém lembra por que existe? Ou a configuração de autenticação que foi sendo ajustada até funcionar?

É aí que a migração pode dar errado.

Uma ferramenta consegue converter muitos objetos, mas nem sempre consegue reproduzir o comportamento específico de cada controlador. Algumas regras precisam ser reescritas usando filtros da Gateway API ou mecanismos específicos da implementação escolhida.

Por isso, eu começaria comparando o comportamento das rotas, não apenas o YAML gerado.

Outro cuidado é a versão das CRDs. Para usar TCPRoute e UDPRoute, você precisa instalar versões compatíveis das definições da Gateway API. Atualizar o Cilium não garante automaticamente que essas definições estejam disponíveis na versão correta.

Vale conferir isso antes de migrar qualquer serviço L4.

Também é importante verificar o modo de execução do Envoy e as limitações da implementação. Há cenários em que listeners e rotas TCP/UDP não são reconciliados quando o Envoy do Cilium está configurado para operar na rede do host.

E, claro, políticas de rede precisam ser testadas novamente. Uma mudança importante no datapath não é o momento de presumir que todas as regras continuarão se comportando exatamente como antes.

Minha abordagem seria bem simples: criar um Gateway paralelo, migrar uma aplicação HTTP pouco crítica, validar o comportamento e só depois avançar para autenticação e serviços TCP/UDP.

Se possível, mantenha o caminho antigo disponível durante a transição. É muito melhor poder voltar atrás com tranquilidade do que descobrir, às duas da manhã, que uma anotação esquecida controlava alguma coisa importante.

## Já podemos esquecer o service mesh também?

Calma. Uma coisa de cada vez.

O Cilium 1.20 reduz a necessidade de alguns componentes que costumavam ficar ao redor do gateway, mas isso não significa que ele substitui automaticamente todas as funções de um service mesh.

Pense na diferença entre estas duas perguntas:

- Quem pode acessar minha aplicação pela internet?
- Qual serviço interno pode chamar qual operação de outro serviço?

A primeira pode ser resolvida no gateway. A segunda exige uma política de comunicação entre workloads, com identidade e autorização adequadas.

É possível construir parte dessa arquitetura com recursos do próprio Cilium. Dependendo dos requisitos, porém, você ainda pode precisar de funcionalidades adicionais de mesh.

O mesmo vale para retries, circuit breaking, distribuição avançada de tráfego, canários e injeção de falhas. Tudo depende do que sua plataforma precisa e do que a implementação escolhida oferece.

E existe uma diferença importante entre autenticar uma requisição na borda e estabelecer identidade criptográfica entre serviços usando mTLS.

São problemas relacionados, mas não equivalentes.

Por isso, eu não diria que o service mesh morreu. Diria que ficou mais difícil justificar sua instalação automática em toda infraestrutura Kubernetes.

Se você precisa de suas funcionalidades, ótimo. Mas, se o objetivo era apenas publicar aplicações, aplicar algumas políticas e controlar o acesso na entrada do cluster, talvez estivesse mantendo mais infraestrutura do que precisava.

Essa é uma diferença importante: escolher um mesh porque existe uma necessidade concreta é bem diferente de instalar um porque parece ser o próximo passo obrigatório.

## E a tal simplificação não cria outro problema?

Pode criar, sim.

Existe uma tentação de olhar para essa evolução e concluir que quanto mais coisas uma única plataforma oferece, melhor.

Nem sempre.

Quando você concentra mais responsabilidades no Cilium, passa a depender mais dele. Uma atualização problemática pode afetar uma parte maior da infraestrutura. Recursos recentes podem ter limitações que ainda não apareceram no seu ambiente. E a equipe precisa conhecer bem o funcionamento da solução para não transformar a consolidação em uma nova caixa-preta.

Por outro lado, manter vários componentes independentes também tem um custo. São mais integrações, mais ciclos de atualização e mais pontos em que uma configuração pode ficar inconsistente.

Não existe uma resposta universal. Existe uma troca entre a complexidade de administrar várias ferramentas e a dependência de uma plataforma mais abrangente.

Para uma equipe pequena, essa troca pode fazer bastante sentido, desde que a adoção seja gradual e acompanhada de testes.

## O que eu faria se estivesse montando essa infraestrutura hoje?

Se já estivesse usando Cilium, começaria pelo caminho mais simples.

Primeiro, verificaria a compatibilidade das CRDs da Gateway API e criaria um Gateway de teste. Depois, migraria uma aplicação HTTP sem muita criticidade.

Com isso funcionando, testaria o ExternalAuth e a configuração de TLS de backend. Só então começaria a migrar os serviços TCP e UDP, prestando atenção especial às conexões persistentes e ao comportamento durante atualizações.

Também revisaria as políticas de rede e os procedimentos de rollback antes de desligar qualquer componente antigo.

Nada muito glamouroso. É o tipo de trabalho que evita descobrir problemas em produção.

E eu não tentaria eliminar o service mesh no mesmo movimento. Primeiro consolidaria o que o gateway consegue resolver bem. Depois avaliaria quais necessidades continuam exigindo uma camada adicional.

A meta não é ter o menor número possível de deployments só para poder dizer que a infraestrutura ficou enxuta.

A meta é parar de operar componentes que não entregam valor suficiente para justificar sua existência.

## No fim das contas, menos caixas é uma boa notícia

O Cilium 1.20 não transforma Kubernetes em algo simples. A gente ainda precisa lidar com versões, políticas, observabilidade, certificados, falhas e todas aquelas pequenas surpresas que fazem parte da vida de quem administra infraestrutura.

Mas a evolução da Gateway API abre uma possibilidade interessante: administrar HTTP, TCP, UDP, autenticação e TLS de backend de maneira mais uniforme, aproveitando uma plataforma de rede que talvez já esteja rodando no cluster.

E isso muda a conversa.

Em vez de perguntar qual controlador instalar, qual proxy adicionar e como integrar mais um componente, podemos começar perguntando se precisamos mesmo de todos eles.

Para quem mantém uma pequena frota auto-hospedada, cada componente removido pode significar menos atualizações, menos configurações duplicadas e menos coisas para descobrir quando algo quebra.

O ingress-nginx arquivado tornou a migração necessária para quem ainda dependia dele. O Cilium 1.20 oferece uma oportunidade de fazer algo melhor do que simplesmente trocar uma ferramenta por outra.

Talvez a melhor arquitetura não seja aquela que tem uma solução especializada para cada pequeno problema.

Talvez seja aquela em que você consegue resolver os problemas reais com menos peças, sem perder o controle sobre o que acontece dentro do cluster.

E, convenhamos, se já temos trabalho suficiente administrando Kubernetes, eliminar algumas caixas da lista não parece uma má ideia.