---
title: "RCA não é preencher um formulário: é descobrir por que o sistema permitiu a falha"
date: 2026-10-21
draft: false
tags: ["SRE", "Gestão de Incidentes", "RCA", "Postmortem"]
summary: "Recuperar o serviço não elimina as condições que produziram a falha. Uma RCA só tem valor quando transforma evidências em mudanças verificáveis no sistema, no processo ou nos controles, e não em um documento que explica o passado."
---

## Introdução: o incidente acabou, mas o problema foi resolvido?

Um serviço fica indisponível. O time de operações recebe alertas, começa a investigar e encontra um problema aparentemente simples. Alguém reinicia um componente, o serviço volta a responder e os indicadores começam a normalizar.

A equipe respira aliviada. O incidente é encerrado.

Alguns dias depois, o mesmo problema acontece novamente.

A resposta inicial funcionou, mas não explicou por que a falha aconteceu, quais condições permitiram que ela se propagasse ou o que deveria mudar para evitar uma nova ocorrência.

Esse é um dos problemas mais comuns na resolução de incidentes: confundir a recuperação do serviço com a eliminação das condições que produziram a falha.

A análise de causa raiz, conhecida como RCA (*Root Cause Analysis*), existe para enfrentar esse problema. Seu propósito não é produzir um documento para cumprir um processo interno, nem encontrar alguém para responsabilizar. É reconstruir os acontecimentos, testar hipóteses e identificar mudanças capazes de reduzir a probabilidade de recorrência.

A tese deste artigo é simples: **uma RCA só tem valor quando transforma evidências de um incidente em mudanças verificáveis no sistema, no processo ou nos mecanismos de controle.**

O restante é documentação sem garantia de aprendizado.

## O problema de procurar culpados em vez de investigar sistemas

Quando alguma coisa falha, existe uma tendência natural de procurar uma explicação rápida.

Alguém executou o comando errado. Uma alteração foi publicada sem a validação esperada. Um procedimento não foi seguido. Um alerta não foi atendido a tempo.

Essas observações podem ser verdadeiras, mas não necessariamente explicam o incidente.

Se uma pessoa executou uma operação perigosa, por exemplo, a investigação ainda precisa perguntar por que aquela operação era possível, quais proteções deveriam existir e por que elas não impediram ou limitaram o impacto.

Havia uma revisão obrigatória? O sistema exigia confirmação? Existia um mecanismo de rollback? A alteração estava limitada a um ambiente? Os sinais de risco eram visíveis antes da execução?

A diferença está entre identificar uma ação associada ao incidente e explicar as condições que permitiram que ela produzisse aquele resultado.

Em engenharia de confiabilidade, essa distinção é importante porque sistemas reais são formados por pessoas, processos, software, infraestrutura, dependências externas e decisões tomadas ao longo do tempo.

Uma falha raramente precisa ser explicada por um único fator isolado.

Isso também não significa que as pessoas nunca devam ser responsabilizadas por suas decisões. Significa que uma investigação técnica não deve encerrar sua análise simplesmente porque encontrou uma pessoa ou uma ação próxima do evento.

**Se o mesmo erro pode acontecer novamente nas mesmas condições, a investigação ainda precisa entender o que torna essa repetição possível.**

## RCA é um método, não uma coleção de ferramentas

Existem várias ferramentas utilizadas na análise de causa raiz. Entre elas estão os cinco porquês, o diagrama de Ishikawa, também conhecido como diagrama de causa e efeito, e o diagrama de Pareto para ajudar a priorizar problemas conforme os dados disponíveis.

Cada uma oferece uma maneira diferente de organizar o raciocínio.

Os cinco porquês ajudam a aprofundar uma explicação inicial. O diagrama de Ishikawa permite organizar causas potenciais em categorias. O Pareto ajuda a identificar quais ocorrências ou categorias concentram uma parcela relevante dos problemas observados.

Nenhuma dessas ferramentas, isoladamente, garante que a causa identificada esteja correta.

É possível preencher um diagrama inteiro com hipóteses que nunca foram verificadas. Também é possível fazer cinco perguntas e terminar em uma explicação superficial. Uma apresentação organizada não transforma uma suposição em evidência.

Por isso, a ferramenta precisa estar subordinada ao método.

Uma RCA consistente deve partir dos fatos, reconstruir a sequência dos acontecimentos, formular hipóteses, buscar evidências que as sustentem ou contradigam e estabelecer ações coerentes com as causas encontradas.

O método organiza a investigação. As ferramentas ajudam a executá-la.

Não existe obrigação de utilizar todas as ferramentas em todos os incidentes. A escolha deve considerar a complexidade do problema, a disponibilidade de dados e o nível de profundidade necessário.

## Quando vale a pena fazer uma RCA?

A RCA é especialmente útil quando um incidente tem impacto significativo, apresenta recorrência, revela uma fragilidade importante ou deixa dúvidas sobre os mecanismos de prevenção e recuperação.

Isso não significa que toda falha operacional precise gerar uma investigação extensa.

Uma interrupção pequena, bem compreendida e facilmente corrigida pode exigir apenas o registro adequado e uma ação pontual. Já uma falha recorrente, uma indisponibilidade relevante ou um incidente com múltiplos fatores pode justificar uma investigação mais estruturada.

A profundidade deve ser proporcional ao risco, ao impacto e à incerteza.

Também é importante entender o papel temporal da RCA: ela é normalmente uma investigação posterior a um evento. Durante um incidente ativo, a prioridade costuma ser conter o impacto, restaurar o serviço e preservar as evidências necessárias para compreender o que aconteceu.

A investigação não deve atrasar uma recuperação urgente.

Depois da estabilização, a equipe pode aprofundar a análise e decidir quais mudanças são necessárias para reduzir a possibilidade de recorrência.

A RCA também não substitui práticas preventivas, testes de resiliência, análise de riscos ou monitoramento contínuo. Ela complementa essas atividades ao usar a experiência de uma falha real para melhorar o sistema.

## As seis etapas de uma análise de causa raiz

Uma investigação precisa ter começo, desenvolvimento e resultado. Na prática, podemos organizá-la em seis etapas.

### 1. Organizar a equipe de investigação

Uma RCA não deve depender exclusivamente da pessoa que estava de plantão ou do profissional que conhece melhor o componente afetado.

É importante reunir pessoas com diferentes perspectivas sobre o sistema: quem opera a plataforma, quem desenvolve a aplicação, quem conhece a infraestrutura e, quando necessário, especialistas em segurança, arquitetura, redes ou fornecedores.

O tamanho do grupo depende do problema. A equipe deve ser suficientemente pequena para permitir uma discussão produtiva, mas suficientemente diversa para evitar uma investigação limitada a uma única visão.

Também é importante definir responsabilidades: quem conduz a análise, quem fornece as evidências, quem decide sobre as mudanças e quem acompanha sua implementação.

A participação da liderança pode ser necessária para disponibilizar recursos e remover impedimentos. Sem esse apoio, uma investigação pode identificar corretamente uma fragilidade e terminar sem conseguir corrigi-la.

### 2. Reconstruir o que aconteceu

Antes de explicar uma falha, precisamos estabelecer os fatos.

Isso inclui registrar o impacto observado, os serviços afetados, o horário de início, a sequência dos acontecimentos, as alterações recentes e o momento em que o serviço foi recuperado.

Em ambientes de software, as fontes podem incluir:

- Logs de aplicação e infraestrutura.
- Métricas de latência, tráfego, erros e saturação.
- Traces distribuídos e dependências entre serviços.
- Eventos do Kubernetes e do provedor de nuvem.
- Histórico de deploys, alterações de configuração e mudanças de infraestrutura.
- Alertas, registros de atendimento e comunicações operacionais.

A cronologia é especialmente importante porque acontecimentos próximos no tempo nem sempre possuem uma relação causal.

Uma publicação pode ter ocorrido antes do incidente sem ter provocado a falha. Um aumento de latência pode ser a causa de um erro subsequente ou apenas outro efeito do mesmo problema.

A investigação precisa separar o que foi observado do que está sendo inferido.

Outro ponto importante é preservar os dados. Logs podem expirar, métricas podem ter retenção limitada e eventos temporários podem desaparecer. Registrar a cronologia enquanto as evidências estão disponíveis reduz a dependência da memória dos participantes.

### 3. Identificar causas potenciais

Com a sequência dos acontecimentos estabelecida, a equipe pode começar a formular hipóteses.

Imagine um serviço que apresenta erros depois de uma alteração de infraestrutura. Entre as hipóteses possíveis estão uma configuração incorreta, uma limitação de capacidade, uma falha de conectividade ou um comportamento inesperado de uma dependência externa.

Nesse momento, a equipe não precisa escolher imediatamente uma única explicação.

O diagrama de Ishikawa pode ajudar a organizar essas possibilidades. Os cinco porquês podem aprofundar as hipóteses mais relevantes.

O cuidado fundamental é não confundir uma hipótese plausível com uma causa demonstrada.

Para cada explicação proposta, a equipe deve perguntar: que evidência esperamos encontrar se essa hipótese estiver correta? Que observação poderia contradizê-la? Temos dados suficientes para diferenciá-la das alternativas?

Esse processo reduz o risco de selecionar a primeira explicação que parece razoável e construir toda a investigação em torno dela.

### 4. Identificar as causas fundamentais

Uma causa fundamental deve explicar uma parte relevante da sequência que produziu o incidente e apontar para condições que possam ser tratadas.

Isso não significa que sempre exista uma única causa raiz.

Em sistemas distribuídos, diferentes fatores podem interagir: uma dependência fica lenta, uma fila cresce, os timeouts se acumulam e a capacidade disponível deixa de ser suficiente. O impacto final pode depender da combinação desses fatores.

A investigação deve buscar relações causais sustentadas por evidências, sem forçar uma explicação única quando os dados apontam para múltiplas contribuições.

Também é necessário distinguir a causa imediata das condições subjacentes.

Um processo pode ter sido encerrado por falta de memória. Esse é um mecanismo próximo da falha. A investigação ainda precisa verificar por que o consumo cresceu, por que a capacidade foi insuficiente e quais controles poderiam ter detectado ou limitado o problema.

A análise termina quando a equipe possui uma explicação suficientemente sustentada para orientar ações concretas, não quando encontra uma frase curta para preencher o campo "causa raiz".

### 5. Implementar ações corretivas

Uma RCA sem plano de ação dificilmente produzirá uma melhoria duradoura.

As ações precisam estar relacionadas às causas identificadas e possuir responsáveis, prazos e critérios de conclusão.

Dependendo do incidente, elas podem incluir:

- Corrigir uma configuração ou um defeito de software.
- Introduzir validações automáticas em pipelines de CI/CD.
- Ajustar limites de recursos, timeouts ou políticas de retry.
- Melhorar a gestão de mudanças e os mecanismos de rollback.
- Criar alertas para sinais que não estavam sendo observados.
- Introduzir controles de acesso ou proteções contra operações perigosas.
- Melhorar procedimentos operacionais e a documentação de recuperação.

A prioridade deve ser dada às ações que efetivamente alteram as condições do problema.

Treinamento e documentação podem ser necessários, mas não devem substituir controles técnicos quando estes são viáveis e adequados.

Por exemplo, se uma operação destrutiva pode ser executada por engano, simplesmente pedir que todos tenham mais atenção pode ser insuficiente. Uma validação, uma restrição de permissão ou uma confirmação adicional pode reduzir a dependência de comportamento perfeito.

### 6. Verificar se as ações funcionaram

Implementar uma correção não é o mesmo que demonstrar sua eficácia.

Uma alteração pode ter sido concluída e ainda assim não resolver a causa identificada. Pode reduzir a frequência do problema sem eliminá-lo. Ou pode introduzir outro risco que não estava presente anteriormente.

Por isso, a equipe deve definir como avaliar o resultado.

Os critérios podem incluir a ausência de recorrência durante uma janela de observação adequada, a redução de uma taxa de erro, a melhoria de um SLO ou a comprovação de que um mecanismo de proteção bloqueia o comportamento indesejado.

A janela de avaliação precisa considerar a frequência esperada do evento. Um problema que ocorria diariamente pode permitir uma avaliação relativamente rápida. Uma falha que aparece apenas em determinadas condições sazonais pode exigir um acompanhamento muito maior.

Por fim, o conhecimento precisa ser transferido para quem mantém o sistema. As mudanças, os riscos remanescentes e os procedimentos relevantes devem fazer parte da operação normal, e não permanecer restritos ao grupo que conduziu a investigação.

Sem essa transferência, a organização corre o risco de perder o aprendizado quando as pessoas mudam de equipe.

## Um exemplo prático: o serviço voltou, mas a causa continua presente

Considere um cenário ilustrativo de uma aplicação executada em Kubernetes.

Após uma publicação, o serviço começa a apresentar aumento de latência e erros. Algumas instâncias reiniciam e o time percebe que a disponibilidade caiu.

A equipe realiza o rollback e o serviço se recupera.

A primeira conclusão poderia ser: "o deploy causou o incidente".

Essa afirmação é uma hipótese inicial, não uma conclusão suficiente.

A investigação precisa correlacionar o horário da publicação com métricas, logs, eventos dos pods e alterações de configuração. Também precisa verificar se o problema aparece exclusivamente na nova versão ou se há alguma condição de infraestrutura ou dependência que explique o comportamento.

Suponha que a análise das evidências confirme a seguinte sequência:

1. Uma alteração introduziu um comportamento que elevou o consumo de memória sob determinada carga.
2. Os pods ultrapassaram os limites de memória configurados e foram encerrados pelo mecanismo de proteção do sistema.
3. A capacidade restante não foi suficiente para absorver o tráfego durante os reinícios.
4. A aplicação não havia sido validada com um teste representativo daquela carga antes da publicação.

Nesse cenário, o rollback restaurou o serviço, mas não corrigiu o defeito nem a lacuna de validação.

O plano de ação poderia incluir corrigir o comportamento que elevou o consumo, adicionar um teste de carga que reproduza a condição relevante e estabelecer critérios de observação durante a implantação.

As ações devem ser definidas conforme as evidências reais do incidente; este exemplo não representa um diagnóstico universal para reinícios de pods.

O ponto central é que a investigação não parou no evento mais visível. Ela conectou o comportamento da aplicação, a capacidade da plataforma e os controles existentes antes da publicação.

É essa conexão que permite propor melhorias que vão além de repetir o rollback na próxima ocorrência.

## Como o RCA se conecta à engenharia de confiabilidade

Em SRE (*Site Reliability Engineering*), a investigação de incidentes deve contribuir para a confiabilidade do serviço.

Isso significa relacionar o aprendizado a indicadores e objetivos observáveis, como SLIs, SLOs, disponibilidade, latência, taxa de erros e tempo de recuperação.

Uma ação corretiva deve ser avaliada não apenas pela sua conclusão administrativa, mas pelo efeito que produz no sistema.

Se uma mudança pretende reduzir a duração das indisponibilidades, por exemplo, o time precisa definir como observar essa redução. Se pretende detectar uma falha antes que ela afete os usuários, deve verificar se o novo mecanismo realmente gera um sinal útil e acionável.

A RCA também ajuda a identificar trabalho operacional repetitivo que pode ser eliminado por automação, melhorar procedimentos de resposta e orientar testes de resiliência.

O objetivo não é apenas reduzir o número de incidentes. É tornar as falhas menos prováveis, limitar seu impacto e melhorar a capacidade de recuperação quando elas acontecerem.

Uma investigação bem conduzida também pode revelar limitações que não serão resolvidas por uma alteração isolada. Dependências externas, decisões arquiteturais e restrições de negócio podem exigir um plano gradual, com riscos explicitamente documentados.

A confiabilidade melhora quando o aprendizado do incidente influencia as decisões de engenharia posteriores.

## O que a inteligência artificial pode mudar na RCA?

Uma organização pode realizar boas investigações e, mesmo assim, perder parte do conhecimento produzido.

Relatórios ficam espalhados em documentos, sistemas de chamados, ferramentas de observabilidade e canais de comunicação. Meses depois, outro time enfrenta um sintoma semelhante sem saber que uma situação parecida já foi investigada.

É aqui que a inteligência artificial pode ajudar.

Se os registros das RCA estiverem organizados e acessíveis, uma solução baseada em recuperação de informações, como RAG (*Retrieval-Augmented Generation*), pode localizar investigações anteriores, resumir hipóteses já avaliadas e relacionar incidentes que compartilham características relevantes.

Um agente também pode ajudar a estruturar uma cronologia, identificar lacunas em um relatório ou sugerir perguntas para aprofundar uma hipótese.

Essas capacidades podem reduzir o tempo gasto procurando informações e facilitar o reaproveitamento do conhecimento operacional.

Mas existe uma diferença importante entre apoiar uma investigação e determinar sua conclusão.

Um modelo de linguagem pode produzir uma explicação convincente sem que ela seja sustentada pelas evidências disponíveis. Pode associar incidentes que compartilham sintomas, mas possuem causas diferentes. Também pode ignorar detalhes específicos do ambiente se esses dados não estiverem presentes no contexto recuperado.

Por isso, uma implementação responsável precisa preservar a origem das informações, permitir a verificação das evidências e distinguir claramente fatos, hipóteses e recomendações geradas pelo modelo.

A IA não deve transformar uma hipótese em causa raiz apenas porque consegue explicá-la bem.

Ela também não substitui a instrumentação necessária para investigar o sistema. Se não existem métricas, logs ou registros de mudanças adequados, um modelo não consegue recuperar com segurança aquilo que nunca foi observado.

O maior benefício potencial está em combinar dados operacionais confiáveis, documentação estruturada e capacidade de recuperação de conhecimento.

Nesse cenário, cada incidente pode contribuir para tornar as próximas investigações mais rápidas e fundamentadas.

## Os limites de uma RCA

A análise de causa raiz não é uma garantia de que um incidente nunca voltará a acontecer.

Uma investigação pode ser limitada pela ausência de dados, pela complexidade do sistema ou pela dificuldade de reproduzir determinadas condições. Uma mudança pode reduzir um risco sem eliminar todos os caminhos possíveis para a falha.

Em problemas crônicos, com múltiplos fatores e variações difíceis de observar, pode ser necessário complementar a RCA com análise estatística, monitoramento mais detalhado, experimentos controlados ou métodos de melhoria contínua.

Também existe o risco de transformar o processo em burocracia: relatórios extensos, reuniões improdutivas e planos de ação que nunca são verificados.

Uma análise mais longa não é necessariamente uma análise melhor.

O nível de rigor deve ser suficiente para sustentar as conclusões e orientar decisões proporcionais ao risco. Quando as evidências não permitem determinar uma causa com segurança, reconhecer a incerteza é melhor do que fabricar uma resposta definitiva.

O resultado de uma RCA deve ser entendido como uma explicação sustentada pelas evidências disponíveis, sujeita a revisão caso novas informações relevantes apareçam.

## Conclusão: o aprendizado precisa sobreviver ao incidente

Uma organização não demonstra maturidade operacional porque possui um formulário de RCA, um processo documentado ou uma reunião obrigatória após cada falha.

Ela demonstra maturidade quando consegue transformar incidentes em mudanças concretas, acompanhar os resultados dessas mudanças e compartilhar o conhecimento produzido.

Isso exige disciplina para reconstruir os fatos, disposição para questionar explicações iniciais, colaboração entre diferentes áreas e compromisso com a implementação das ações.

Exige também aceitar que nem toda falha terá uma explicação simples e que nem toda ação será suficiente na primeira tentativa.

A análise de causa raiz não serve para recontar o que aconteceu. Serve para entender quais condições tornaram o incidente possível e decidir o que precisa mudar.

Se o serviço voltou, mas as condições que produziram a falha continuam presentes, o trabalho ainda não terminou.

**O verdadeiro resultado de uma RCA não é o documento que explica o passado. É a melhoria verificável que muda o comportamento futuro do sistema.**
