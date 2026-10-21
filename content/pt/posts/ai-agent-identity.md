---
title: "Seus agentes de IA não precisam de API Keys. Precisam de identidade."
date: 2026-10-21
draft: false
tags: ["Agentes de IA", "Segurança", "SPIFFE", "Zero Trust"]
summary: "API keys armazenadas em variáveis de ambiente não provam quem execute o que. Com SPIFFE e SPIRE, identidade passa a ser uma propriedade verificável do workload, o que muda completamente a segurança de agentes autônomos."
---

Estamos construindo sistemas de IA que executam código, consultam bancos de dados, chamam APIs, acessam serviços em nuvem e delegam tarefas para outros agentes. Em alguns casos, esses sistemas já operam com autonomia suficiente para executar sequências inteiras de ações sem que um humano aprove cada etapa.

Mas existe um problema básico nessa arquitetura: como esses agentes provam quem são?

Na maioria dos sistemas tradicionais, a resposta é decepcionantemente simples: alguém coloca uma API key em uma variável de ambiente, injeta um token no container ou configura uma credencial permanente no serviço. O agente recebe acesso e começa a trabalhar.

Isso funciona até o momento em que alguma coisa dá errado.

Um prompt malicioso convence o agente a chamar uma ferramenta indevida. Uma vulnerabilidade permite ler variáveis de ambiente. Um container comprometido expõe suas credenciais. De repente, um segredo criado para um serviço específico pode ser usado por alguém que não deveria ter acesso a ele.

O problema não é apenas o modelo de IA. É a arquitetura de identidade que colocamos ao redor dele.

A solução passa por uma ideia antiga em segurança de infraestrutura, mas que ganha uma importância nova com agentes autônomos: identidade não deveria ser um segredo armazenado dentro de uma aplicação. Deveria ser uma propriedade verificável do workload que está executando.

É aqui que entram SPIFFE e SPIRE.

## O problema de colocar segredos dentro de agentes

Imagine um agente responsável por pesquisar documentos, consultar um banco vetorial e executar ferramentas por meio do Model Context Protocol, o MCP.

Para realizar seu trabalho, ele precisa de algumas permissões:

- Consultar uma API interna.
- Pesquisar documentos de determinado cliente.
- Invocar ferramentas específicas.
- Acessar um serviço hospedado na nuvem.

A abordagem convencional é entregar credenciais ao agente e confiar que ele vai utilizá-las corretamente.

Só que um agente de IA não é uma aplicação tradicional no sentido operacional. Ele interpreta instruções, recebe conteúdo externo, seleciona ferramentas e pode produzir sequências de chamadas que seus desenvolvedores não anteciparam.

Um atacante não precisa necessariamente comprometer o servidor inteiro. Dependendo das permissões disponíveis, basta induzir o agente a executar uma ação indevida.

Se uma credencial permanente estiver acessível ao processo, o atacante poderá tentar extraí-la ou abusar dela. E, se conseguir copiá-la, a credencial pode continuar utilizável mesmo depois que a execução original terminar.

Existe ainda outro problema: uma API key normalmente identifica uma credencial, não a integridade do processo que a utiliza. Ela não prova, por si só, qual binário está executando, em qual container ele está, a qual namespace pertence ou se deveria ter acesso àquele recurso.

A pergunta correta deixa de ser apenas "qual é a chave deste agente?" e passa a ser:

Como o sistema pode verificar a identidade deste workload e decidir, a cada conexão, o que ele está autorizado a fazer?

## SPIFFE e SPIRE: identidade como infraestrutura

SPIFFE significa Secure Production Identity Framework for Everyone. É uma especificação para identificar workloads de maneira padronizada.

SPIRE é uma implementação dessa arquitetura. Ele fornece os mecanismos necessários para atestar workloads, emitir identidades criptográficas e distribuir informações de confiança.

A peça central é o SVID, ou SPIFFE Verifiable Identity Document.

Um SVID pode ser um certificado X.509 ou um token JWT assinado. Em vez de depender de uma chave permanente embutida na aplicação, o workload recebe uma identidade emitida dinamicamente depois de passar pelas verificações configuradas.

Uma identidade SPIFFE pode ter a seguinte forma:

```
spiffe://example.org/agent/mcp-executor
```

Esse identificador representa uma identidade dentro de um domínio de confiança. Ele não é uma senha: sua utilidade depende das credenciais criptográficas associadas e das políticas aplicadas pelos serviços que o aceitam.

O fluxo geral funciona assim:

1. O servidor SPIRE verifica a identidade do nó em que o workload está executando.
2. O agente SPIRE local identifica atributos do processo ou container que solicita credenciais.
3. O servidor compara esses atributos com as regras de registro autorizadas.
4. Se as condições forem satisfeitas, o workload recebe um SVID de curta duração.
5. O workload utiliza essa identidade para autenticar-se perante serviços que confiam na autoridade emissora.

O detalhe importante é que a aplicação não precisa carregar uma chave permanente para provar sua identidade. Ela pode obter e renovar suas credenciais dinamicamente por meio do agente SPIRE local.

Isso muda a maneira como pensamos sobre autenticação.

## O que acontece dentro do SPIRE Server?

O SPIRE Server é o plano de controle responsável por administrar a confiança e emitir identidades.

Sua implementação em Go é organizada em componentes especializados.

O servidor inicializa seus endpoints gRPC, integra plugins, acessa o armazenamento de registros e mantém os mecanismos de autoridade certificadora necessários para assinar credenciais.

O processo de emissão de identidade depende de algumas etapas distintas.

### 1. Primeiro, o nó precisa provar sua identidade

Antes de confiar em um agente, o sistema precisa verificar a infraestrutura em que ele está executando.

No Kubernetes, isso pode envolver tokens projetados de contas de serviço. Em ambientes de nuvem, podem ser utilizados documentos de identidade de instâncias ou mecanismos equivalentes suportados pelos plugins de atestação.

O servidor valida as evidências de acordo com o mecanismo configurado e estabelece a identidade do nó.

Depois disso, o agente SPIRE pode se comunicar com o servidor usando sua identidade e um canal autenticado.

### 2. Depois, o processo precisa ser identificado

Um nó confiável não significa que todos os processos executados nele sejam confiáveis.

O agente SPIRE consulta atributos do workload, que podem incluir namespace, conta de serviço, imagem do container e outras propriedades suportadas pelo ambiente.

Esses atributos são comparados com os registros de identidade autorizados.

É possível, por exemplo, distinguir um executor de ferramentas de um agente responsável por consultar documentos, mesmo que ambos executem no mesmo cluster.

A segurança depende da qualidade desses seletores, da integridade da atestação e da precisão das regras configuradas.

### 3. Finalmente, o servidor emite a credencial

Quando a solicitação é autorizada, o SPIRE Server assina o SVID apropriado.

Para X.509, isso resulta em um certificado que pode ser utilizado em conexões TLS mútuas. Para JWT, resulta em um token assinado que pode ser apresentado a serviços compatíveis.

O certificado ou token possui uma validade limitada. A aplicação precisa renovar suas credenciais conforme necessário, em vez de depender indefinidamente de um segredo estático.

O SPIRE também administra a rotação das chaves de assinatura e a distribuição dos bundles de confiança.

É uma infraestrutura de identidade, não apenas um gerador de tokens.

## O que muda na comunicação entre agentes?

Considere um agente orquestrador que precisa chamar um servidor MCP responsável por executar ferramentas internas.

Na arquitetura convencional, o servidor MCP pode exigir uma API key compartilhada ou um token configurado manualmente.

Com SPIFFE/SPIRE, ambos os workloads podem apresentar identidades verificáveis por meio de certificados X.509.

Durante uma conexão mTLS:

1. O cliente apresenta sua identidade criptográfica.
2. O servidor apresenta a própria identidade.
3. Os dois lados validam os certificados e a cadeia de confiança.
4. As políticas de autorização determinam se aquela identidade pode executar a operação solicitada.

Isso fornece autenticação mútua e criptografia no transporte, além de reduzir a dependência de segredos compartilhados.

Mas existe uma distinção fundamental: autenticar um agente não significa autorizar todas as suas ações.

Um agente identificado como `mcp-executor` ainda pode estar autorizado a chamar apenas determinadas ferramentas. O servidor MCP precisa verificar essa restrição e aplicá-la de verdade.

A identidade responde "quem está chamando?". A autorização responde "o que essa identidade pode fazer?".

Misturar as duas coisas é uma maneira bastante eficiente de criar uma arquitetura aparentemente segura que continua concedendo permissões excessivas.

## E quando o agente precisa acessar a nuvem?

O problema não termina nas chamadas entre serviços internos.

Agentes frequentemente precisam acessar serviços gerenciados, armazenamentos, filas e plataformas de IA hospedadas em nuvens públicas.

Armazenar chaves permanentes de IAM dentro de containers é uma alternativa particularmente arriscada.

Uma abordagem melhor é utilizar federação de identidade.

O agente solicita um JWT SVID destinado ao público esperado pelo provedor de nuvem. O serviço de identidade da nuvem valida o emissor, a assinatura, a audiência e as condições de confiança configuradas. Se tudo estiver correto, o token pode ser trocado por credenciais temporárias com permissões limitadas.

O resultado é uma cadeia de confiança entre o workload e o serviço de nuvem, sem a necessidade de distribuir uma chave permanente para cada agente.

Essa configuração exige integração explícita com o provedor, políticas de confiança adequadas e permissões de menor privilégio. Não basta emitir qualquer JWT e esperar que a nuvem o aceite.

Ainda assim, o modelo é muito mais interessante do que copiar segredos para dezenas de aplicações.

## Identidade não resolve tudo

Seria tentador concluir que, depois de instalar SPIRE, o problema de segurança dos agentes está resolvido.

Não está.

Se um agente legítimo for manipulado por prompt injection, ele ainda poderá tentar executar ações que estão dentro das permissões que recebeu. Um SVID válido não impede que um processo autorizado tome uma decisão ruim.

SPIRE reduz determinados riscos de identidade e de exposição de credenciais, mas não substitui as demais camadas de segurança.

Uma implantação séria precisa combinar:

- Identidades específicas por workload.
- Credenciais de curta duração.
- Permissões mínimas por ferramenta e serviço.
- Atestação e regras de registro rigorosas.
- Proteção das chaves de assinatura, preferencialmente com integração a sistemas de gerenciamento de chaves apropriados.
- Auditoria de emissão de credenciais e operações administrativas.
- Controles de entrada, validação de argumentos e limites de execução para ferramentas.
- Testes que verifiquem o isolamento entre tenants.

Também é necessário lembrar que um workload comprometido pode utilizar sua identidade legítima enquanto ela continuar válida e autorizada. Revogação, contenção e resposta a incidentes continuam sendo necessárias.

A identidade criptográfica é uma camada da arquitetura de segurança, não uma substituta para ela.

## A arquitetura que faz sentido para agentes autônomos

Uma implantação prática pode começar com o SPIRE Server, os agentes distribuídos pelos nós e registros específicos para cada tipo de workload.

As aplicações utilizam SDKs compatíveis com SPIFFE para obter seus SVIDs pelo socket Unix local. Os serviços internos validam as identidades e aplicam políticas de autorização. Quando necessário, a federação permite estender a confiança a outros domínios ou provedores de nuvem.

Em produção, também entram em cena a persistência dos registros, a disponibilidade do plano de controle, o gerenciamento das chaves, a rotação de credenciais, a distribuição de bundles e a observabilidade.

O objetivo não é apenas fazer o primeiro certificado funcionar. É garantir que a infraestrutura continue segura quando houver centenas de agentes, vários tenants, múltiplos ambientes e mudanças constantes nos workloads.

Esse é o momento em que identidade deixa de ser um detalhe de configuração e passa a ser uma capacidade central da plataforma.

## O próximo problema não é emitir credenciais. É limitar a autonomia.

Agentes de IA estão tornando mais simples construir sistemas que executam tarefas antes reservadas a operadores humanos ou a aplicações rigidamente programadas.

Mas autonomia operacional não deveria significar acesso irrestrito.

Quanto mais ferramentas um agente pode invocar, mais importante se torna distinguir sua identidade, seu contexto e suas permissões. A segurança precisa acompanhar o agente durante a execução, em vez de depender de um segredo distribuído no momento do deploy.

SPIFFE e SPIRE oferecem uma base sólida para esse modelo: identidades verificáveis, credenciais temporárias e relações de confiança explícitas entre workloads.

Isso não elimina prompt injection, bugs ou decisões incorretas. Elimina, ou reduz significativamente, uma classe de riscos causada por credenciais permanentes e identidade mal definida.

A mudança de mentalidade é simples, embora a implementação exija cuidado:

Pare de perguntar qual API key entregar ao agente. Comece perguntando como ele prova quem é, por que recebeu aquela identidade e quais ações essa identidade está autorizada a executar.

Em uma infraestrutura com agentes autônomos, essa diferença deixa de ser apenas uma boa prática. Passa a fazer parte do desenho fundamental do sistema.
