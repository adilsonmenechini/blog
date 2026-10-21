---
title: "SRE não é manter tudo no ar: é decidir quanto de falha sua arquitetura pode suportar"
date: 2026-10-21
draft: false
tags: ["SRE", "DevOps", "Reliability Engineering", "Observabilidade", "Gestão de Incidentes", "SLO", "Cloud Native"]
summary: "Perseguir 100% de disponibilidade pode deixar a organização mais lenta, mais cara e nem sempre mais confiável. SLOs, error budgets, automação e postmortems transformam confiabilidade em decisão compartilhada, não em disputa de opiniões."
---
{{< audio slug="sre-reliability" >}}


Existe uma ideia bastante difundida no mundo da infraestrutura: o trabalho de quem opera sistemas é evitar que eles caiam. Quanto menos incidentes, melhor. Quanto maior a disponibilidade, melhor. E, se fosse possível, tudo deveria funcionar 100% do tempo.

Parece razoável. Afinal, ninguém quer abrir um aplicativo e encontrar uma página de erro, tentar fazer um pagamento e receber um timeout ou descobrir que um serviço ficou indisponível durante o lançamento de um produto.

Mas existe um problema nessa lógica: perseguir disponibilidade a qualquer custo pode tornar uma organização mais lenta, mais cara e, ironicamente, nem sempre mais confiável.

Quanto tempo sua equipe passa olhando dashboards? Quantas alterações deixam de ser feitas porque ninguém quer correr o risco de quebrar produção? Quantas vezes um incidente acontece e a primeira reação é descobrir quem fez o deploy, em vez de entender por que o sistema permitiu que aquele deploy causasse um problema tão grande?

Essas perguntas revelam algo importante. Confiabilidade não é apenas uma propriedade da infraestrutura. É também uma consequência das decisões de arquitetura, dos processos de desenvolvimento e da maneira como uma organização lida com o risco.

É nesse contexto que entra Site Reliability Engineering, ou SRE.

A proposta não é contratar uma equipe para apagar incêndios com mais eficiência. É tratar a operação de sistemas como um problema de engenharia de software: medir o que importa, automatizar o trabalho repetitivo, estabelecer objetivos explícitos de confiabilidade e usar dados para decidir quando acelerar e quando reduzir o ritmo das mudanças.

A pergunta deixa de ser "como garantir que nada nunca falhe?" e passa a ser outra:

Qual nível de confiabilidade nossos usuários realmente precisam, e como podemos alcançá-lo sem transformar cada mudança em uma ameaça?

## 1. O problema não começa em produção. Começa na maneira como construímos software

Durante muito tempo, desenvolvimento e operações foram tratados como disciplinas separadas.

O time de desenvolvimento recebia uma demanda, implementava funcionalidades e tentava entregar o produto o mais rápido possível. Depois, o sistema chegava à produção e passava a ser responsabilidade de outra equipe.

Essa segunda equipe precisava lidar com deploys, configuração de servidores, capacidade, monitoramento, incidentes e problemas cujo contexto muitas vezes estava concentrado na cabeça de quem escreveu o código.

É a famosa parede entre desenvolvimento e operações.

```text
Negócio
   |
   v
Desenvolvimento
   |
   | "Está pronto. Pode operar."
   v
Operações
   |
   v
Produção
   |
   v
Incidentes, alertas e manutenção
```

O problema dessa separação não é simplesmente a falta de comunicação.

É que as equipes podem acabar otimizando objetivos diferentes.

Desenvolvimento é incentivado a entregar funcionalidades. Operações é incentivada a preservar a estabilidade. Uma quer mudar o sistema; a outra precisa administrar os riscos dessas mudanças.

Se a aplicação falha, desenvolvimento pode dizer que o ambiente está mal configurado. Operações pode argumentar que o código foi entregue sem considerar as condições reais de produção.

As duas equipes podem estar parcialmente certas. E o sistema continua apresentando problemas.

DevOps surgiu como um movimento cultural e um conjunto de práticas para reduzir essas barreiras, melhorar a colaboração e automatizar o ciclo de entrega e operação.

SRE leva essa discussão a um modelo operacional mais concreto. Em vez de depender apenas de colaboração e boas intenções, introduz mecanismos mensuráveis para administrar a confiabilidade.

Entre eles estão os indicadores de serviço, os objetivos de nível de serviço, os orçamentos de erro, a automação e a análise de incidentes sem culpabilização.

A mudança fundamental é esta: a responsabilidade pelo comportamento de um sistema em produção não termina quando o código é entregue.

## 2. SRE é DevOps com mecanismos concretos de engenharia?

A definição clássica de SRE, associada a Ben Treynor Sloss, do Google, descreve a disciplina como o resultado de pedir a um engenheiro de software que projete uma função de operações.

Essa definição é interessante porque muda o ponto de partida.

Em vez de tratar a operação como uma sequência de tarefas manuais que precisam ser executadas corretamente por pessoas, SRE procura resolver problemas operacionais com engenharia, software e automação.

Isso inclui desenvolver ferramentas, eliminar tarefas repetitivas, projetar sistemas resilientes, melhorar o monitoramento e criar processos que reduzam o impacto de falhas.

SRE também é uma função profissional. Um Site Reliability Engineer costuma trabalhar na interseção entre desenvolvimento, infraestrutura, sistemas distribuídos e operação de serviços.

Mas é importante não confundir as coisas: SRE não é sinônimo de DevOps, embora as duas abordagens compartilhem princípios e objetivos.

DevOps enfatiza a colaboração, a automação e a integração entre as etapas do ciclo de vida do software. SRE oferece um conjunto específico de práticas para administrar a confiabilidade, como SLOs, *error budgets*, resposta a incidentes e redução de *toil*.

Uma equipe pode adotar práticas de SRE sem criar imediatamente um departamento chamado SRE. Da mesma forma, contratar engenheiros com esse título não transforma automaticamente a cultura da empresa.

O que importa é como as decisões são tomadas e como a confiabilidade é incorporada ao desenvolvimento do produto.

## 3. Disponibilidade de 100%: um objetivo que pode sair caro demais

Vamos começar com uma métrica conhecida: disponibilidade.

Em sua forma mais simples, podemos medir disponibilidade como a proporção de tempo em que um serviço está funcionando corretamente.

Mas existe uma diferença entre um servidor estar ligado e um serviço estar disponível para seus usuários.

Um servidor pode responder a um *health check* enquanto a aplicação demora vários segundos para processar uma requisição. Uma API pode responder normalmente, mas retornar dados incorretos. Uma plataforma pode continuar acessível enquanto sua funcionalidade de pagamento está completamente indisponível.

Em sistemas distribuídos, medir apenas o tempo de atividade das máquinas não é suficiente.

Precisamos medir o comportamento do serviço a partir de uma perspectiva que faça sentido para o usuário.

Imagine uma API que recebeu 100 mil requisições válidas durante uma janela de medição. Dessas, 99.900 foram concluídas com sucesso dentro do limite de latência definido.

Podemos expressar a disponibilidade observada, nesse exemplo, como:

```
SLI = (99.900 / 100.000) × 100
```

O resultado é 99,9%.

Essa abordagem permite avaliar o resultado das interações, em vez de assumir que o serviço estava disponível simplesmente porque seus servidores estavam ligados.

É claro que o indicador precisa definir quais requisições contam como válidas, quais respostas representam sucesso e qual período será analisado. Essas decisões fazem parte do contrato de medição.

E aqui aparece a primeira lição de SRE: não podemos administrar confiabilidade de maneira séria se não concordarmos sobre o que significa estar confiável.

### Os famosos noves

Quando discutimos disponibilidade, é comum ouvir expressões como três noves, quatro noves ou cinco noves.

Elas representam diferentes níveis de disponibilidade:

| Disponibilidade | Indisponibilidade teórica em 30 dias |
| --- | --- |
| 99% | 7 h 12 min |
| 99,9% | 43 min 12 s |
| 99,95% | 21 min 36 s |
| 99,99% | 4 min 19 s |
| 99,999% | 26 s |

*Valores aproximados para um período de 30 dias, considerando uma métrica de disponibilidade baseada em tempo.*

À primeira vista, parece óbvio que cinco noves são melhores do que três. Tecnicamente, representam uma meta de disponibilidade mais rigorosa. Mas isso não significa que sejam sempre a escolha correta.

Elevar a disponibilidade pode exigir redundância geográfica, replicação de dados, mecanismos de failover, testes adicionais, maior capacidade ociosa e uma arquitetura muito mais complexa.

Essas medidas podem ser essenciais para um serviço financeiro crítico. Para uma ferramenta interna que pode ficar indisponível por alguns minutos sem consequências relevantes, talvez representem um custo desnecessário.

Além disso, disponibilidade baseada em tempo e disponibilidade baseada em requisições não são métricas intercambiáveis. Uma falha curta durante um pico de tráfego pode afetar muito mais usuários do que uma falha mais longa durante um período de baixa demanda.

O objetivo não é escolher o maior número possível de noves. É determinar qual nível de confiabilidade atende às necessidades reais do serviço.

## 4. SLI, SLO e SLA: três siglas que não significam a mesma coisa

Uma implementação de SRE começa com definições claras. E poucas coisas causam tanta confusão quanto essas três siglas.

### SLI: Service Level Indicator

O SLI é o indicador que mede o comportamento do serviço.

Pode representar a proporção de requisições bem-sucedidas, a latência das respostas, a taxa de erros ou outra característica importante para os usuários.

Exemplos:

- Percentual de requisições HTTP concluídas com sucesso.
- Percentual de requisições que terminam em menos de 300 milissegundos.
- Percentual de operações de pagamento processadas corretamente.
- Percentual de mensagens processadas dentro de um prazo definido.

Um bom SLI deve representar algo que realmente importa para a experiência do usuário, não apenas algo que é fácil coletar.

### SLO: Service Level Objective

O SLO é o objetivo estabelecido para um ou mais SLIs durante uma janela de medição.

Por exemplo:

Pelo menos 99,9% das requisições válidas da API devem ser concluídas com sucesso em uma janela móvel de 30 dias.

Agora temos algo que pode orientar decisões.

Se o indicador começa a se afastar da meta, precisamos investigar. Se o serviço permanece consistentemente dentro do objetivo, podemos avaliar se a arquitetura está adequada ou se existe espaço para melhorar a eficiência operacional.

Um SLO não precisa tratar apenas de disponibilidade. Ele pode estabelecer objetivos separados para latência, correção de resultados ou processamento dentro do prazo.

Também é importante que o SLO seja definido com participação de engenharia, produto e negócio. Uma meta puramente técnica pode não representar o que os usuários realmente precisam.

### SLA: Service Level Agreement

O SLA é um acordo formal de nível de serviço, normalmente estabelecido com clientes ou consumidores do serviço.

Ele pode definir compromissos, condições de medição, exclusões e consequências quando os níveis acordados não são atendidos.

Imagine que uma plataforma ofereça um SLA contratual de 99,9% de disponibilidade, enquanto sua equipe trabalhe com um SLO interno mais rigoroso, de 99,95%.

O SLO interno cria uma margem para administrar o risco antes de violar o compromisso contratual. O SLA, por sua vez, estabelece as condições comerciais e as obrigações perante o cliente.

Em resumo:

| Conceito | Pergunta que responde |
| --- | --- |
| SLI | O que estamos medindo? |
| SLO | Qual resultado queremos alcançar? |
| SLA | Qual compromisso assumimos com o cliente? |

Não basta criar um dashboard com gráficos coloridos. Sem um indicador relevante, uma meta explícita e uma compreensão dos compromissos assumidos, fica difícil decidir quando investir em confiabilidade e quando priorizar outras melhorias.

## 5. Error budget: o mecanismo que equilibra confiabilidade e velocidade

Aqui chegamos ao conceito que considero um dos mais importantes de SRE.

Se um serviço tem um SLO de 99,9%, o complemento até 100% é de 0,1%.

Esse complemento é a base do *error budget*, ou orçamento de erro, para uma meta de disponibilidade.

Em uma janela de 30 dias, se estivermos usando uma métrica baseada em tempo, 0,1% equivale a aproximadamente 43 minutos de indisponibilidade.

Isso não significa que a equipe deva obrigatoriamente ficar 43 minutos fora do ar. Significa que a meta admite uma determinada quantidade de falhas segundo a métrica e a janela definidas.

Para um SLO baseado em requisições, o orçamento será calculado a partir das requisições elegíveis, não diretamente dos minutos do mês.

Considere uma API que recebe um milhão de requisições válidas em uma janela e tem um SLO de 99,9% de sucesso.

O cálculo simplificado é:

```
Orçamento de erro = 1.000.000 × 0,001 = 1.000
```

Nesse cenário, até mil requisições malsucedidas podem ocorrer antes que o serviço ultrapasse o orçamento correspondente, considerando que esse seja o único indicador e que todos os eventos sejam contabilizados da mesma maneira.

O valor não deve ser interpretado como uma autorização para causar mil falhas deliberadamente. É um limite para administrar o risco acumulado.

### Por que isso muda a relação entre desenvolvimento e operações?

Sem um mecanismo compartilhado, a discussão tende a virar uma disputa de opiniões.

Desenvolvimento quer lançar uma funcionalidade. Operações teme que o deploy provoque uma indisponibilidade. Produto pressiona pelo prazo. A decisão depende de quem tem mais autoridade ou de quem está disposto a assumir o risco.

Com *error budgets*, existe uma referência comum.

Se o serviço está operando bem e possui orçamento disponível, a equipe pode continuar lançando mudanças, desde que utilize mecanismos de mitigação de risco.

Se o orçamento está sendo consumido rapidamente ou já foi esgotado, pode ser necessário reduzir o ritmo de mudanças arriscadas e priorizar a confiabilidade, mantendo as correções urgentes de segurança e outros trabalhos essenciais.

O orçamento transforma confiabilidade em um critério de decisão compartilhado, em vez de uma discussão abstrata entre equipes.

### O que acontece quando o orçamento acaba?

Uma política de SRE pode estabelecer que, quando o orçamento é esgotado, lançamentos que aumentam o risco sejam temporariamente suspensos até que a confiabilidade seja recuperada ou a política seja revista.

Isso não deve ser um ritual burocrático nem uma punição ao time de desenvolvimento.

É um mecanismo de governança baseado em evidências.

Também não devemos confundir orçamento disponível com permissão irrestrita para arriscar. Um serviço pode estar dentro do SLO e ainda apresentar uma vulnerabilidade de segurança grave ou um problema de integridade de dados que exige intervenção imediata.

Confiabilidade é multidimensional. O orçamento é uma ferramenta para administrar determinados riscos, não um substituto para o julgamento técnico.

## 6. Operação não deveria ser sinônimo de trabalho manual infinito

Existe uma forma de trabalho que parece inevitável em muitas equipes de infraestrutura: responder a alertas, reiniciar processos, executar scripts, ajustar configurações, coletar logs e repetir procedimentos que já foram realizados dezenas de vezes.

O problema não é toda atividade operacional ser manual. Existem situações em que a intervenção humana é necessária e desejável.

O problema é quando tarefas manuais, repetitivas e previsíveis consomem a maior parte do tempo de profissionais que poderiam estar resolvendo problemas estruturais.

Na terminologia de SRE, esse tipo de trabalho é conhecido como *toil*.

*Toil* é o trabalho operacional que tende a ser manual, repetitivo, reativo, automatizável e sem valor duradouro proporcional ao esforço. Ele também costuma crescer conforme o sistema cresce.

Imagine que uma equipe precise executar manualmente um procedimento de verificação para cada novo serviço implantado. Se existem dez serviços, talvez o processo seja administrável. Se existem centenas, a equipe pode acabar gastando uma parte crescente do seu tempo apenas repetindo o mesmo trabalho.

Uma automação bem projetada pode executar as verificações, registrar os resultados, alertar quando necessário e manter o procedimento consistente.

O benefício não é simplesmente economizar alguns minutos.

É permitir que a equipe invista tempo em melhorias que reduzam a probabilidade de falhas, simplifiquem a arquitetura e diminuam o custo operacional futuro.

Por isso, automatizar não deve significar transformar qualquer tarefa em código sem avaliar sua utilidade. A automação precisa ser confiável, observável, mantida e proporcional ao problema.

O objetivo é reduzir o trabalho repetitivo para liberar capacidade de engenharia.

## 7. Monitoramento: alertar pessoas apenas quando elas precisam agir

Ter milhares de métricas não significa ter um sistema bem monitorado.

É possível construir dashboards impressionantes e, ainda assim, descobrir uma indisponibilidade pelo próprio cliente.

Também é possível configurar tantos alertas que ninguém consiga distinguir os eventos importantes do ruído.

O monitoramento precisa responder a uma pergunta fundamental: o serviço está atendendo às necessidades dos usuários?

Para isso, é útil acompanhar indicadores de tráfego, latência, erros e saturação, além de sinais específicos da aplicação e dos objetivos de serviço.

Mas medir não é suficiente. Precisamos definir o que fazer quando os indicadores se afastam do esperado.

Uma regra prática é separar as saídas do monitoramento de acordo com a urgência:

- **Alerta imediato**: alguém precisa agir agora para mitigar um impacto relevante.
- **Ticket ou tarefa**: existe um problema que precisa ser investigado, mas não exige intervenção imediata.
- **Log ou registro**: a informação precisa estar disponível para diagnóstico e análise posterior.

Se tudo gera um alerta urgente, nada é realmente urgente.

O resultado é a fadiga de alertas: profissionais passam a ignorar notificações porque muitas delas não exigem ação ou não representam impacto relevante.

Uma equipe de SRE deve trabalhar para que os alertas estejam associados a consequências reais, especialmente quando há risco de violação de SLO.

O objetivo não é eliminar a participação humana. É reservar a atenção humana para situações em que ela realmente faz diferença.

## 8. Capacidade e performance: escalar não é simplesmente adicionar máquinas

Outro aspecto importante de SRE é planejar a capacidade do sistema.

Aplicações crescem por diferentes motivos. A base de usuários aumenta, novas funcionalidades são lançadas, campanhas de marketing elevam o tráfego e eventos sazonais provocam picos de demanda.

Se a equipe só reage quando os recursos chegam ao limite, o planejamento já falhou.

Por outro lado, provisionar capacidade excessiva sem necessidade também tem um custo. Recursos ociosos consomem dinheiro, aumentam a complexidade e podem esconder ineficiências.

O desafio é encontrar um equilíbrio entre capacidade suficiente para atender à demanda e margem para absorver variações inesperadas.

Imagine uma API que normalmente recebe mil requisições por segundo, mas pode chegar a cinco mil durante uma campanha.

Antes de aumentar a infraestrutura cinco vezes, precisamos entender como a aplicação se comporta sob carga.

O banco de dados suporta o volume adicional? O pool de conexões é suficiente? Existe algum serviço dependente com limite de capacidade? Os mecanismos de cache ajudam ou criam uma concentração de carga? Os testes de carga reproduzem o comportamento real?

Escalar horizontalmente uma aplicação não resolve automaticamente gargalos em dependências compartilhadas.

O planejamento precisa considerar cenários de crescimento, testes de capacidade, custos, limites técnicos e mecanismos de degradação controlada.

Também é importante preparar o sistema para falhas. Uma arquitetura que opera exatamente no limite de sua capacidade normal pode entrar em colapso quando perde um nó ou precisa absorver o tráfego de outra instância.

Margem de capacidade tem custo. A falta dela também.

SRE procura tomar essa decisão com base em medições e no impacto que diferentes cenários teriam sobre os usuários.

## 9. Mudanças em produção: pequenas alterações também podem causar grandes incidentes

Uma linha de configuração, uma atualização de dependência ou uma mudança aparentemente trivial pode afetar um sistema inteiro.

O risco depende do contexto, da arquitetura, das dependências e das condições em que a mudança é aplicada.

Por isso, gerenciamento de mudanças não deve ser entendido apenas como um formulário de aprovação antes de cada deploy.

O objetivo é reduzir o risco e o impacto das alterações.

Entre as práticas úteis estão:

- Testes automatizados e validações antes da implantação.
- Deploys progressivos, expondo a mudança inicialmente a uma parcela do tráfego.
- Monitoramento dos indicadores de serviço durante a implantação.
- Rollback automatizado ou procedimentos de recuperação bem definidos.
- Feature flags para separar a implantação do código da ativação da funcionalidade.
- Análise de risco proporcional ao impacto potencial da mudança.

Essas técnicas ajudam a detectar problemas cedo e limitar o número de usuários afetados.

Imagine uma nova versão de uma API. Em vez de substituir todas as instâncias de uma só vez, podemos disponibilizar a versão para uma pequena porcentagem do tráfego, observar erros e latência e aumentar gradualmente a exposição.

Se os indicadores piorarem, a equipe pode interromper a progressão ou reverter a versão antes que o impacto se amplie.

O importante é entender que mudanças seguras não são mudanças que nunca falham. São mudanças projetadas para que falhas sejam detectadas e contidas rapidamente.

## 10. Incidentes: primeiro recupere o serviço, depois investigue

Quando um sistema cai, existe uma tendência natural de procurar imediatamente a causa.

Alguém quer descobrir qual commit foi responsável, quem executou o deploy ou qual configuração estava errada.

Essas perguntas podem ser relevantes durante a investigação. Mas, enquanto o serviço continua indisponível, a prioridade é reduzir o impacto sobre os usuários.

Em uma resposta a incidentes, é importante estabelecer responsabilidades claras, comunicar o estado do problema e executar ações de mitigação.

Às vezes, a solução imediata será reverter uma mudança. Em outros casos, será necessário desabilitar uma funcionalidade, desviar tráfego, aumentar a capacidade ou restaurar dados.

A prioridade é recuperar o serviço com segurança. A investigação mais profunda pode continuar depois que a situação estiver estabilizada.

Isso não significa ignorar a causa. Significa separar duas atividades que exigem objetivos diferentes: mitigar o incidente e aprender com ele.

### O postmortem não é um tribunal

Depois de um incidente significativo, uma equipe pode produzir um *postmortem*: um documento que registra o que aconteceu, qual foi o impacto, como o sistema se comportou e quais ações podem reduzir a probabilidade ou a gravidade de recorrências.

Uma boa análise inclui uma linha do tempo, os sinais observados, as decisões tomadas, as condições que contribuíram para o incidente e os itens de melhoria identificados.

Mas existe um princípio cultural importante: o postmortem deve ser conduzido sem culpabilização.

Isso não significa ausência de responsabilidade. Significa evitar que a investigação se limite a apontar uma pessoa como causa do problema.

Se um engenheiro executou um comando perigoso, precisamos entender por que esse comando estava disponível, quais proteções existiam, se havia revisão, se o procedimento estava documentado e por que o sistema permitiu que uma única ação causasse aquele impacto.

A análise muda quando a pergunta deixa de ser "quem errou?" e passa a ser "quais condições tornaram esse resultado possível?".

Talvez o procedimento fosse ambíguo. Talvez o ambiente não tivesse uma validação automática. Talvez o sistema não oferecesse um rollback seguro. Talvez a pressão operacional tenha incentivado uma decisão que parecia razoável com as informações disponíveis.

O objetivo é transformar o aprendizado em mudanças concretas, com responsáveis e acompanhamento.

Um postmortem sem ações efetivas corre o risco de se tornar apenas documentação de um incidente que voltará a acontecer.

## 11. Como começar a implementar SRE sem transformar a empresa inteira

A adoção de SRE não precisa começar com uma reorganização corporativa, uma nova equipe ou uma plataforma complexa de observabilidade.

Na verdade, começar pequeno costuma ser mais útil.

Escolha um serviço relevante, com usuários identificáveis e um problema operacional que a equipe consiga observar.

Depois, avance em etapas.

### Passo 1: defina o que significa sucesso para o usuário

Identifique as operações mais importantes do serviço. Para uma API de pagamentos, pode ser concluir pagamentos corretamente dentro de um limite de latência. Para uma plataforma de conteúdo, pode ser entregar páginas sem erros e dentro de um tempo aceitável.

Evite começar por métricas de infraestrutura que não estejam claramente ligadas à experiência do usuário.

### Passo 2: escolha um SLI e estabeleça um SLO

Comece com um indicador que possa ser medido de maneira consistente.

Defina a meta, a janela de medição e as condições que determinam o que será considerado sucesso.

Não tente resolver todas as dimensões de confiabilidade de uma vez. Uma meta simples e útil é melhor do que um conjunto de objetivos que ninguém consegue interpretar.

### Passo 3: torne o orçamento de erro visível

Calcule o orçamento correspondente ao SLO e acompanhe sua evolução.

O time precisa entender não apenas se está dentro da meta, mas também a velocidade com que o orçamento está sendo consumido.

Um orçamento que desaparece rapidamente é um sinal para investigar, mesmo que a meta ainda não tenha sido ultrapassada.

### Passo 4: melhore os alertas

Configure alertas que exijam ação humana quando houver risco relevante para o serviço.

Reduza notificações redundantes, documente os procedimentos de resposta e defina quando um evento deve ser tratado como incidente.

### Passo 5: identifique e elimine toil

Observe o trabalho diário da equipe. Quais atividades são repetitivas? Quais tarefas dependem de alguém consultar manualmente um dashboard? Quais procedimentos poderiam ser automatizados com segurança?

Priorize as automações que reduzam risco, frequência de intervenção e tempo gasto em tarefas sem valor duradouro.

### Passo 6: crie uma rotina de aprendizado

Depois de incidentes relevantes, registre o que aconteceu e transforme as conclusões em melhorias verificáveis.

Acompanhe se as ações foram concluídas e se realmente reduziram a probabilidade ou o impacto de falhas semelhantes.

### Passo 7: amplie com evidências

Quando o modelo funcionar para o primeiro serviço, documente os resultados e compartilhe o aprendizado.

Use dados para mostrar o que melhorou: redução de incidentes, recuperação mais rápida, menor consumo de trabalho manual ou maior previsibilidade dos deploys.

Assim, a expansão de SRE passa a ser uma decisão baseada em resultados, e não apenas na adoção de uma nova terminologia.

## 12. Afinal, preciso ser desenvolvedor para trabalhar com SRE?

Não existe uma única trajetória profissional para SRE.

Pessoas com experiência em sistemas operacionais, redes, infraestrutura, cloud, observabilidade ou desenvolvimento podem construir uma carreira na área.

Mas existe uma diferença entre conhecer os princípios de SRE e exercer uma função de engenharia de confiabilidade que exige desenvolver e manter software.

Em uma posição de SRE, programação, automação, depuração e compreensão do comportamento de aplicações são frequentemente fundamentais. Também é necessário entender sistemas distribuídos, redes, capacidade, monitoramento e resposta a incidentes.

Não é obrigatório ter começado a carreira como desenvolvedor de aplicações. Entretanto, depender exclusivamente de procedimentos manuais limita o tipo de problema que você conseguirá resolver.

Um profissional de infraestrutura que aprende a escrever ferramentas, automatizar processos e investigar o comportamento interno de aplicações está desenvolvendo competências diretamente úteis para SRE.

Da mesma forma, um desenvolvedor que aprende sobre produção, observabilidade, resiliência e gestão de incidentes amplia sua capacidade de projetar software operável.

O objetivo não é transformar todas as pessoas em especialistas em tudo. É reduzir as barreiras entre construir, entregar e operar sistemas.

## 13. Confiabilidade é uma decisão de produto, não apenas de infraestrutura

Existe uma conclusão importante por trás de todos esses conceitos.

SLOs, *error budgets*, automação, planejamento de capacidade e postmortems não são ferramentas isoladas. Eles formam um modelo para tomar decisões melhores sobre sistemas em produção.

O SLI mostra o comportamento observado. O SLO define o nível de serviço que queremos oferecer. O SLA formaliza determinados compromissos com clientes. O error budget ajuda a administrar o risco de mudanças. A automação reduz trabalho repetitivo. Os postmortems transformam falhas em oportunidades de melhoria.

Tudo isso converge para uma pergunta: como entregar valor aos usuários de maneira sustentável?

Um serviço não precisa ter a maior disponibilidade tecnicamente possível. Precisa ter a disponibilidade apropriada para suas necessidades e seus riscos.

Uma aplicação crítica pode justificar investimentos consideráveis em redundância e recuperação. Uma ferramenta interna pode aceitar uma janela de manutenção planejada se o impacto for baixo e o custo de disponibilidade contínua for desproporcional.

Essas decisões não devem ser tomadas isoladamente pela equipe de infraestrutura. Produto, engenharia, negócio e operação precisam compreender os compromissos envolvidos.

Também não basta declarar que falhas são normais e usar isso como desculpa para negligenciar a qualidade. A filosofia de SRE não reduz a importância da confiabilidade; ela exige que a confiabilidade seja definida, medida e administrada de maneira explícita.

O objetivo é evitar tanto a imprudência quanto o excesso de conservadorismo.

## Conclusão: o melhor SRE não é aquele que nunca recebe um alerta

É aquele que ajuda a construir um sistema que precisa de menos intervenções manuais, que torna seus problemas visíveis antes que se tornem crises e que permite à equipe responder a falhas sem transformar cada incidente em uma busca por culpados.

SRE muda a conversa entre desenvolvimento e operações porque substitui parte dos conflitos de opinião por objetivos compartilhados e dados observáveis.

Em vez de exigir disponibilidade absoluta, definimos metas realistas. Em vez de proibir mudanças por medo, administramos o risco com orçamentos de erro e mecanismos de implantação seguros. Em vez de repetir tarefas operacionais indefinidamente, investimos em automação. E, quando algo falha, investigamos as condições que permitiram o problema e melhoramos o sistema.

Minha recomendação é começar com um serviço, medir o que realmente importa e usar os resultados para orientar os próximos passos.

Não é necessário implantar uma estrutura completa de SRE para começar a praticar engenharia de confiabilidade. É necessário reconhecer que a operação faz parte do ciclo de vida do software e que as decisões sobre confiabilidade precisam considerar tanto a experiência dos usuários quanto o custo de manter o sistema.

A pergunta que deixo é esta: se sua equipe passasse a próxima semana sem precisar apagar nenhum incêndio, o que ela finalmente conseguiria construir para que a semana seguinte também fosse assim?

## Referências para aprofundamento

- [Google SRE Book: Site Reliability Engineering](https://sre.google/sre-book/table-of-contents/)
- [Google SRE: Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)
- [Google SRE: Production Services Best Practices](https://sre.google/workbook/table-of-contents/)
- [Google Cloud: SLI, SLO e SLA](https://sre.google/workbook/implementing-slos/)
- [Google SRE: Introdução à engenharia de confiabilidade](https://sre.google/sre-book/introduction/)
