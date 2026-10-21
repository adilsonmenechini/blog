---
title: "El RCA no es llenar un formulario: es descubrir por qué el sistema permitió la falla"
date: 2026-10-21
draft: false
tags: ["SRE", "Gestión de Incidentes", "RCA", "Postmortem"]
summary: "Recuperar el servicio no elimina las condiciones que produjeron la falla. Un RCA solo tiene valor cuando transforma evidencias en cambios verificables en el sistema, el proceso o los controles, y no en un documento que explica el pasado."
---

## Introducción: el incidente terminó, ¿pero el problema quedó resuelto?

Un servicio queda indisponible. El equipo de operaciones recibe alertas, empieza a investigar y encuentra un problema aparentemente simple. Alguien reinicia un componente, el servicio vuelve a responder y los indicadores empiezan a normalizarse.

El equipo respira aliviado. El incidente se cierra.

Algunos días después, el mismo problema ocurre nuevamente.

La respuesta inicial funcionó, pero no explicó por qué ocurrió la falla, qué condiciones permitieron que se propagara o qué debería cambiar para evitar una nueva ocurrencia.

Ese es uno de los problemas más comunes en la resolución de incidentes: confundir la recuperación del servicio con la eliminación de las condiciones que produjeron la falla.

El análisis de causa raíz, conocido como RCA (*Root Cause Analysis*), existe para enfrentar ese problema. Su propósito no es producir un documento para cumplir un proceso interno, ni encontrar alguien a quien responsabilizar. Es reconstruir los acontecimientos, testear hipótesis e identificar cambios capaces de reducir la probabilidad de recurrencia.

La tesis de este artículo es simple: **un RCA solo tiene valor cuando transforma evidencias de un incidente en cambios verificables en el sistema, el proceso o los mecanismos de control.**

El resto es documentación sin garantía de aprendizaje.

## El problema de buscar culpables en vez de investigar sistemas

Cuando algo falla, existe una tendencia natural de buscar una explicación rápida.

Alguien ejecutó el comando errado. Un cambio fue publicado sin la validación esperada. Un procedimiento no fue seguido. Un alerta no fue atendido a tiempo.

Esas observaciones pueden ser verdaderas, pero no necesariamente explican el incidente.

Si una persona ejecutó una operación peligrosa, por ejemplo, la investigación todavía necesita preguntar por qué aquella operación era posible, qué protecciones deberían existir y por qué no impidieron o limitaron el impacto.

¿Había una revisión obligatoria? ¿El sistema exigía confirmación? ¿Existe un mecanismo de rollback? ¿El cambio estaba limitado a un ambiente? ¿Las señales de riesgo eran visibles antes de la ejecución?

La diferencia está entre identificar una acción asociada al incidente y explicar las condiciones que permitieron que ella produjera aquel resultado.

En ingeniería de confiabilidad, esa distinción es importante porque los sistemas reales están formados por personas, procesos, software, infraestructura, dependencias externas y decisiones tomadas a lo largo del tiempo.

Una falla rara vez necesita ser explicada por un único factor aislado.

Eso tampoco significa que las personas nunca deban ser responsabilizadas por sus decisiones. Significa que una investigación técnica no debe cerrar su análisis simplemente porque encontró una persona o una acción cercana al evento.

**Si el mismo error puede ocurrir nuevamente en las mismas condiciones, la investigación todavía necesita entender qué hace posible esa repetición.**

## El RCA es un método, no una colección de herramientas

Existen varias herramientas utilizadas en el análisis de causa raíz. Entre ellas están los cinco porqués, el diagrama de Ishikawa, también conocido como diagrama de causa y efecto, y el diagrama de Pareto para ayudar a priorizar problemas conforme los datos disponibles.

Cada una ofrece una manera distinta de organizar el razonamiento.

Los cinco porqués ayudan a profundizar una explicación inicial. El diagrama de Ishikawa permite organizar causas potenciales en categorías. El Pareto ayuda a identificar qué ocurrencias o categorías concentran una parcela relevante de los problemas observados.

Ninguna de esas herramientas, aislada, garantiza que la causa identificada esté correcta.

Es posible llenar un diagrama entero con hipótesis que nunca fueron verificadas. También es posible hacer cinco preguntas y terminar en una explicación superficial. Una presentación organizada no transforma una suposición en evidencia.

Por eso, la herramienta debe estar subordinada al método.

Un RCA consistente debe partir de los hechos, reconstruir la secuencia de los acontecimientos, formular hipótesis, buscar evidencias que las sustenten o las contradigan y establecer acciones coherentes con las causas encontradas.

El método organiza la investigación. Las herramientas ayudan a ejecutarla.

No existe obligación de utilizar todas las herramientas en todos los incidentes. La elección debe considerar la complejidad del problema, la disponibilidad de datos y el nivel de profundidad necesario.

## ¿Cuándo vale la pena hacer un RCA?

El RCA es especialmente útil cuando un incidente tiene impacto significativo, presenta recurrencia, revela una fragilidad importante o deja dudas sobre los mecanismos de prevención y recuperación.

Eso no significa que toda falla operacional necesite generar una investigación extensa.

Una interrupción pequeña, bien comprendida y fácilmente corregida puede exigir apenas el registro adecuado y una acción puntual. Una falla recurrente, una indisponibilidad relevante o un incidente con múltiples factores puede justificar una investigación más estructurada.

La profundidad debe ser proporcional al riesgo, al impacto y a la incertidumbre.

También es importante entender el papel temporal del RCA: él es normalmente una investigación posterior a un evento. Durante un incidente activo, la prioridad suele ser contener el impacto, restaurar el servicio y preservar las evidencias necesarias para comprender qué ocurrió.

La investigación no debe atrasar una recuperación urgente.

Después de la estabilización, el equipo puede profundizar el análisis y decidir qué cambios son necesarios para reducir la posibilidad de recurrencia.

El RCA tampoco sustituye prácticas preventivas, tests de resiliencia, análisis de riesgos o monitoreo continuo. Él complementa esas actividades al usar la experiencia de una falla real para mejorar el sistema.

## Las seis etapas de un análisis de causa raíz

Una investigación necesita comienzo, desarrollo y resultado. En la práctica, podemos organizarla en seis etapas.

### 1. Organizar el equipo de investigación

Un RCA no debe depender exclusivamente de la persona que estaba de guardia o del profesional que mejor conoce el componente afectado.

Es importante reunir personas con diferentes perspectivas sobre el sistema: quien opera la plataforma, quien desarrolla la aplicación, quien conoce la infraestructura y, cuando sea necesario, especialistas en seguridad, arquitectura, redes o proveedores.

El tamaño del grupo depende del problema. El equipo debe ser suficientemente pequeño para permitir una discusión productiva, pero suficientemente diverso para evitar una investigación limitada a una única visión.

También es importante definir responsabilidades: quien conduce el análisis, quien provee las evidencias, quien decide sobre los cambios y quien acompaña su implementación.

La participación del liderazgo puede ser necesaria para disponibilizar recursos y remover impedimentos. Sin ese apoyo, una investigación puede identificar correctamente una fragilidad y terminar sin conseguir corregirla.

### 2. Reconstruir qué ocurrió

Antes de explicar una falla, necesitamos establecer los hechos.

Eso incluye registrar el impacto observado, los servicios afectados, el horario de inicio, la secuencia de los acontecimientos, los cambios recientes y el momento en que el servicio fue recuperado.

En ambientes de software, las fuentes pueden incluir:

- Logs de aplicación e infraestructura.
- Métricas de latencia, tráfico, errores y saturación.
- Traces distribuidos y dependencias entre servicios.
- Eventos del Kubernetes y del proveedor de nube.
- Historial de deploys, alteraciones de configuración y cambios de infraestructura.
- Alertas, registros de atención y comunicaciones operacionales.

La cronología es especialmente importante porque acontecimientos cercanos en el tiempo no siempre poseen una relación causal.

Una publicación puede haber ocurrido antes del incidente sin haber provocado la falla. Un aumento de latencia puede ser la causa de un error subsecuente o apenas otro efecto del mismo problema.

La investigación necesita separar lo observado de lo que está siendo inferido.

Otro punto importante es preservar los datos. Los logs pueden expirar, las métricas pueden tener retención limitada y los eventos temporales pueden desaparecer. Registrar la cronología mientras las evidencias están disponibles reduce la dependencia de la memoria de los participantes.

### 3. Identificar causas potenciales

Con la secuencia de los acontecimientos establecida, el equipo puede empezar a formular hipótesis.

Imagina un servicio que presenta errores después de una alteración de infraestructura. Entre las hipótesis posibles están una configuración incorrecta, una limitación de capacidad, una falla de conectividad o un comportamiento inesperado de una dependencia externa.

En ese momento, el equipo no necesita elegir inmediatamente una única explicación.

El diagrama de Ishikawa puede ayudar a organizar esas posibilidades. Los cinco porqués pueden profundizar las hipótesis más relevantes.

El cuidado fundamental es no confundir una hipótesis plausible con una causa demostrada.

Para cada explicación propuesta, el equipo debe preguntar: ¿qué evidencia esperamos encontrar si esa hipótesis está correcta? ¿Qué observación podría contradecirla? ¿Tenemos datos suficientes para diferenciarla de las alternativas?

Ese proceso reduce el riesgo de seleccionar la primera explicación que parece razonable y construir toda la investigación alrededor de ella.

### 4. Identificar las causas fundamentales

Una causa fundamental debe explicar una parte relevante de la secuencia que produjo el incidente y apuntar a condiciones que puedan ser tratadas.

Eso no significa que siempre exista una única causa raíz.

En sistemas distribuidos, diferentes factores pueden interactuar: una dependencia queda lenta, una cola crece, los timeouts se acumulan y la capacidad disponible deja de ser suficiente. El impacto final puede depender de la combinación de esos factores.

La investigación debe buscar relaciones causales sustentadas por evidencias, sin forzar una explicación única cuando los datos apuntan a múltiples contribuciones.

También es necesario distinguir la causa inmediata de las condiciones subyacentes.

Un proceso puede haber sido finalizado por falta de memoria. Ese es un mecanismo cercano a la falla. La investigación todavía necesita verificar por qué el consumo creció, por qué la capacidad fue insuficiente y qué controles podrían haber detectado o limitado el problema.

El análisis termina cuando el equipo tiene una explicación suficientemente sustentada para orientar acciones concretas, no cuando encuentra una frase corta para llenar el campo "causa raíz".

### 5. Implementar acciones correctivas

Un RCA sin plan de acción difícilmente producirá una mejora duradera.

Las acciones necesitan estar relacionadas con las causas identificadas y poseer responsables, plazos y criterios de conclusión.

Dependiendo del incidente, pueden incluir:

- Corregir una configuración o un defecto de software.
- Introducir validaciones automáticas en pipelines de CI/CD.
- Ajustar límites de recursos, timeouts o políticas de retry.
- Mejorar la gestión de cambios y los mecanismos de rollback.
- Crear alertas para señales que no estaban siendo observadas.
- Introducir controles de acceso o protecciones contra operaciones peligrosas.
- Mejorar procedimientos operacionales y la documentación de recuperación.

La prioridad debe darse a las acciones que efectivamente alteran las condiciones del problema.

Capacitación y documentación pueden ser necesarias, pero no deben sustituir controles técnicos cuando estos son viables y adecuados.

Por ejemplo, si una operación destructiva puede ser ejecutada por error, pedir apenas que todos tengan más atención puede ser insuficiente. Una validación, una restricción de permiso o una confirmación adicional puede reducir la dependencia del comportamiento perfecto.

### 6. Verificar si las acciones funcionaron

Implementar una corrección no es lo mismo que demostrar su eficacia.

Un cambio puede haber sido concluido y aun así no resolver la causa identificada. Puede reducir la frecuencia del problema sin eliminarlo. O puede introducir otro riesgo que no estaba presente anteriormente.

Por eso, el equipo debe definir cómo evaluar el resultado.

Los criterios pueden incluir la ausencia de recurrencia durante una ventana de observación adecuada, la reducción de una tasa de error, la mejora de un SLO o la comprobación de que un mecanismo de protección bloquea el comportamiento indeseado.

La ventana de evaluación necesita considerar la frecuencia esperada del evento. Un problema que ocurría diariamente puede permitir una evaluación relativamente rápida. Una falla que aparece apenas en determinadas condiciones estacionales puede exigir un acompañamiento mucho mayor.

Por fin, el conocimiento necesita ser transferido a quienes mantienen el sistema. Los cambios, los riesgos remanentes y los procedimientos relevantes deben formar parte de la operación normal, y no permanecer restringidos al grupo que condujo la investigación.

Sin esa transferencia, la organización corre el riesgo de perder el aprendizaje cuando las personas cambian de equipo.

## Un ejemplo práctico: el servicio volvió, pero la causa sigue presente

Considera un escenario ilustrativo de una aplicación ejecutada en Kubernetes.

Tras una publicación, el servicio empieza a presentar aumento de latencia y errores. Algunas instancias se reinician y el equipo percibe que la disponibilidad cayó.

El equipo realiza el rollback y el servicio se recupera.

La primera conclusión podría ser: "el deploy causó el incidente".

Esa afirmación es una hipótesis inicial, no una conclusión suficiente.

La investigación necesita correlacionar el horario de la publicación con métricas, logs, eventos de los pods y alteraciones de configuración. También necesita verificar si el problema aparece exclusivamente en la nueva versión o si hay alguna condición de infraestructura o dependencia que explique el comportamiento.

Supón que el análisis de las evidencias confirma la siguiente secuencia:

1. Un cambio introdujo un comportamiento que elevó el consumo de memoria bajo determinada carga.
2. Los pods superaron los límites de memoria configurados y fueron finalizados por el mecanismo de protección del sistema.
3. La capacidad restante no fue suficiente para absorber el tráfico durante los reinicios.
4. La aplicación no había sido validada con un test representativo de aquella carga antes de la publicación.

En ese escenario, el rollback restauró el servicio, pero no corrigió el defecto ni la brecha de validación.

El plan de acción podría incluir corregir el comportamiento que elevó el consumo, agregar un test de carga que reproduzca la condición relevante y establecer criterios de observación durante la implantación.

Las acciones deben ser definidas conforme las evidencias reales del incidente; este ejemplo no representa un diagnóstico universal para reinicios de pods.

El punto central es que la investigación no paró en el evento más visible. Ella conectó el comportamiento de la aplicación, la capacidad de la plataforma y los controles existentes antes de la publicación.

Es esa conexión la que permite proponer mejoras que van más allá de repetir el rollback en la próxima ocurrencia.

## Cómo se conecta el RCA a la ingeniería de confiabilidad

En SRE (*Site Reliability Engineering*), la investigación de incidentes debe contribuir a la confiabilidad del servicio.

Eso significa relacionar el aprendizaje con indicadores y objetivos observables, como SLIs, SLOs, disponibilidad, latencia, tasa de errores y tiempo de recuperación.

Una acción correctiva debe ser evaluada no apenas por su conclusión administrativa, sino por el efecto que produce en el sistema.

Si un cambio pretende reducir la duración de las indisponibilidades, por ejemplo, el equipo necesita definir cómo observar esa reducción. Si pretende detectar una falla antes de que afecte a los usuarios, debe verificar que el nuevo mecanismo realmente genere una señal útil y accionable.

El RCA también ayuda a identificar trabajo operacional repetitivo que puede eliminarse por automatización, mejorar procedimientos de respuesta y orientar tests de resiliencia.

El objetivo no es apenas reducir el número de incidentes. Es hacer las fallas menos probables, limitar su impacto y mejorar la capacidad de recuperación cuando ocurran.

Una investigación bien conducida también puede revelar limitaciones que no serán resueltas por una alteración aislada. Dependencias externas, decisiones arquitectónicas y restricciones de negocio pueden exigir un plan gradual, con riesgos explícitamente documentados.

La confiabilidad mejora cuando el aprendizaje del incidente influye en las decisiones de ingeniería posteriores.

## ¿Qué puede cambiar la inteligencia artificial en el RCA?

Una organización puede realizar buenas investigaciones y, aun así, perder parte del conocimiento producido.

Los informes quedan esparcidos en documentos, sistemas de tickets, herramientas de observabilidad y canales de comunicación. Meses después, otro equipo enfrenta un síntoma semejante sin saber que una situación parecida ya fue investigada.

Aquí es donde la inteligencia artificial puede ayudar.

Si los registros de los RCA están organizados y accesibles, una solución basada en recuperación de información, como RAG (*Retrieval-Augmented Generation*), puede localizar investigaciones anteriores, resumir hipótesis ya evaluadas y relacionar incidentes que comparten características relevantes.

Un agente también puede ayudar a estructurar una cronología, identificar brechas en un informe o sugerir preguntas para profundizar una hipótese.

Esas capacidades pueden reducir el tiempo gastado buscando informaciones y facilitar el reaproveitamiento del conocimiento operacional.

Pero existe una diferencia importante entre apoyar una investigación y determinar su conclusión.

Un modelo de lenguaje puede producir una explicación convincente sin que ella sea sustentada por las evidencias disponibles. Puede asociar incidentes que comparten síntomas, pero poseen causas diferentes. También puede ignorar detalles específicos del ambiente si esos datos no están presentes en el contexto recuperado.

Por eso, una implementación responsable necesita preservar el origen de las informaciones, permitir la verificación de las evidencias y distinguir claramente hechos, hipótesis y recomendaciones generadas por el modelo.

La IA no debe transformar una hipótesis en causa raíz apenas porque consigue explicarla bien.

Ella tampoco sustituye la instrumentación necesaria para investigar el sistema. Si no existen métricas, logs o registros de cambios adecuados, un modelo no consigue recuperar con seguridad aquello que nunca fue observado.

El mayor beneficio potencial está en combinar datos operacionales confiables, documentación estructurada y capacidad de recuperación de conocimiento.

En ese escenario, cada incidente puede contribuir para hacer las próximas investigaciones más rápidas y fundamentadas.

## Los límites de un RCA

El análisis de causa raíz no es una garantía de que un incidente nunca volverá a ocurrir.

Una investigación puede ser limitada por la ausencia de datos, por la complejidad del sistema o por la dificultad de reproducir determinadas condiciones. Un cambio puede reducir un riesgo sin eliminar todos los caminos posibles para la falla.

En problemas crónicos, con múltiples factores y variaciones difíciles de observar, puede ser necesario complementar el RCA con análisis estadístico, monitoreo más detallado, experimentos controlados o métodos de mejora continua.

También existe el riesgo de transformar el proceso en burocracia: informes extensos, reuniones improductivas y planes de acción que nunca son verificados.

Un análisis más largo no es necesariamente un análisis mejor.

El nivel de rigor debe ser suficiente para sustentar las conclusiones y orientar decisiones proporcionales al riesgo. Cuando las evidencias no permiten determinar una causa con seguridad, reconocer la incertidumbre es mejor que fabricar una respuesta definitiva.

El resultado de un RCA debe entenderse como una explicación sustentada por las evidencias disponibles, sujeta a revisión en caso de que aparezcan nuevas informaciones relevantes.

## Conclusión: el aprendizaje necesita sobrevivir al incidente

Una organización no demuestra madurez operacional porque posee un formulario de RCA, un proceso documentado o una reunión obligatoria después de cada falla.

Ella demuestra madurez cuando consigue transformar incidentes en cambios concretos, acompañar los resultados de esos cambios y compartir el conocimiento producido.

Eso exige disciplina para reconstruir los hechos, disposición para cuestionar explicaciones iniciales, colaboración entre diferentes áreas y compromiso con la implementación de las acciones.

También exige aceptar que no toda falla tendrá una explicación simple y que no toda acción será suficiente en el primer intento.

El análisis de causa raíz no sirve para recontar qué ocurrió. Sirve para entender qué condiciones hicieron posible el incidente y decidir qué necesita cambiar.

Si el servicio volvió, pero las condiciones que produjeron la falla siguen presentes, el trabajo todavía no terminó.

**El verdadero resultado de un RCA no es el documento que explica el pasado. Es la mejora verificable que cambia el comportamiento futuro del sistema.**
