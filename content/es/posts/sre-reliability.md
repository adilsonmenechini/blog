---
title: "SRE no es mantener todo en el aire: es decidir cuánta falla puede soportar tu arquitectura"
date: 2026-10-21
draft: false
tags: ["SRE", "DevOps", "Ingeniería de Confiabilidad", "Observabilidad", "Gestión de Incidentes", "SLO", "Cloud Native"]
summary: "Perseguir 100% de disponibilidad puede dejar a la organización más lenta, más cara y no siempre más confiable. SLOs, presupuestos de error, automatización y postmortems convierten la confiabilidad en una decisión compartida, no en una disputa de opiniones."
---

Existe una idea bastante difundida en el mundo de la infraestructura: el trabajo de quien opera sistemas es evitar que caigan. Cuantos menos incidentes, mejor. Cuanto mayor la disponibilidad, mejor. Y, si fuera posible, todo debería funcionar el 100% del tiempo.

Parece razonable. Al fin y al cabo, nadie quiere abrir una aplicación y encontrar una página de error, intentar un pago y recibir un timeout o descubrir que un servicio quedó indisponible durante el lanzamiento de un producto.

Pero existe un problema en esa lógica: perseguir disponibilidad a cualquier costo puede volver a una organización más lenta, más cara y, irónicamente, no siempre más confiable.

¿Cuánto tiempo pasa tu equipo mirando dashboards? ¿Cuántas alteraciones dejan de hacerse porque nadie quiere correr el riesgo de romper producción? ¿Cuántas veces ocurre un incidente y la primera reacción es descubrir quién hizo el deploy, en vez de entender por qué el sistema permitió que ese deploy causara un problema tan grande?

Esas preguntas revelan algo importante. La confiabilidad no es solo una propiedad de la infraestructura. También es una consecuencia de las decisiones de arquitectura, de los procesos de desarrollo y de la manera en que una organización lida con el riesgo.

Es en ese contexto que entra Site Reliability Engineering, o SRE.

La propuesta no es contratar un equipo para apagar incendios con más eficiencia. Es tratar la operación de sistemas como un problema de ingeniería de software: medir lo que importa, automatizar el trabajo repetitivo, establecer objetivos explícitos de confiabilidad y usar datos para decidir cuándo acelerar y cuándo reducir el ritmo de los cambios.

La pregunta deja de ser "¿cómo garantizar que nada falle nunca?" y pasa a ser otra:

¿Qué nivel de confiabilidad realmente necesitan nuestros usuarios, y cómo podemos alcanzarlo sin transformar cada cambio en una amenaza?

## 1. El problema no empieza en producción. Empieza en la manera como construimos software

Durante mucho tiempo, desarrollo y operaciones fueron tratados como disciplinas separadas.

El equipo de desarrollo recibía una demanda, implementaba funcionalidades y trataba de entregar el producto lo más rápido posible. Después, el sistema llegaba a producción y pasaba a ser responsabilidad de otro equipo.

Ese segundo equipo necesitaba lidiar con deploys, configuración de servidores, capacidad, monitoreo, incidentes y problemas cuyo contexto muchas veces estaba concentrado en la cabeza de quien escribió el código.

Es la famosa pared entre desarrollo y operaciones.

```text
Negocio
   |
   v
Desarrollo
   |
   | "Está listo. Pueden operarlo."
   v
Operaciones
   |
   v
Producción
   |
   v
Incidentes, alertas y mantenimiento
```

El problema de esa separación no es simplemente la falta de comunicación.

Es que los equipos pueden terminar optimizando objetivos diferentes.

Desarrollo es incentivado a entregar funcionalidades. Operaciones es incentivada a preservar la estabilidad. Una quiere cambiar el sistema; la otra necesita administrar los riesgos de esos cambios.

Si la aplicación falla, desarrollo puede decir que el ambiente está mal configurado. Operaciones puede argumentar que el código fue entregado sin considerar las condiciones reales de producción.

Los dos equipos pueden estar parcialmente correctos. Y el sistema sigue presentando problemas.

DevOps surgió como un movimiento cultural y un conjunto de prácticas para reducir esas barreras, mejorar la colaboración y automatizar el ciclo de entrega y operación.

SRE lleva esa discusión a un modelo operacional más concreto. En vez de depender solo de colaboración y buenas intenciones, introduce mecanismos medibles para administrar la confiabilidad.

Entre ellos están los indicadores de servicio, los objetivos de nivel de servicio, los presupuestos de error, la automatización y el análisis de incidentes sin culpabilización.

El cambio fundamental es este: la responsabilidad por el comportamiento de un sistema en producción no termina cuando el código es entregado.

## 2. ¿SRE es DevOps con mecanismos concretos de ingeniería?

La definición clásica de SRE, asociada a Ben Treynor Sloss, de Google, describe la disciplina como el resultado de pedirle a un ingeniero de software que diseñe una función de operaciones.

Esa definición es interesante porque cambia el punto de partida.

En vez de tratar la operación como una secuencia de tareas manuales que necesitan ser ejecutadas correctamente por personas, SRE busca resolver problemas operacionales con ingeniería, software y automatización.

Eso incluye desarrollar herramientas, eliminar tareas repetitivas, proyectar sistemas resilientes, mejorar el monitoreo y crear procesos que reduzcan el impacto de las fallas.

SRE también es una función profesional. Un Site Reliability Engineer suele trabajar en la intersección entre desarrollo, infraestructura, sistemas distribuidos y operación de servicios.

Pero es importante no confundir las cosas: SRE no es sinónimo de DevOps, aunque ambos enfoques compartan principios y objetivos.

DevOps enfatiza la colaboración, la automatización y la integración entre las etapas del ciclo de vida del software. SRE ofrece un conjunto específico de prácticas para administrar la confiabilidad, como SLOs, *error budgets*, respuesta a incidentes y reducción de *toil*.

Un equipo puede adoptar prácticas de SRE sin crear inmediatamente un departamento llamado SRE. De la misma forma, contratar ingenieros con ese título no transforma automáticamente la cultura de la empresa.

Lo que importa es cómo se toman las decisiones y cómo la confiabilidad se incorpora al desarrollo del producto.

## 3. Disponibilidad del 100%: un objetivo que puede salir demasiado caro

Empecemos con una métrica conocida: disponibilidad.

En su forma más simple, podemos medir disponibilidad como la proporción de tiempo en que un servicio funciona correctamente.

Pero existe una diferencia entre un servidor estar encendido y un servicio estar disponible para sus usuarios.

Un servidor puede responder a un *health check* mientras la aplicación tarda varios segundos en procesar una solicitud. Una API puede responder normalmente, pero devolver datos incorrectos. Una plataforma puede seguir accesible mientras su funcionalidad de pago está completamente indisponible.

En sistemas distribuidos, medir apenas el tiempo de actividad de las máquinas no es suficiente.

Necesitamos medir el comportamiento del servicio desde una perspectiva que tenga sentido para el usuario.

Imagina una API que recibió 100 mil solicitudes válidas durante una ventana de medición. De esas, 99.900 se completaron con éxito dentro del límite de latencia definido.

Podemos expresar la disponibilidad observada, en ese ejemplo, como:

```
SLI = (99.900 / 100.000) × 100
```

El resultado es 99,9%.

Ese enfoque permite evaluar el resultado de las interacciones, en lugar de asumir que el servicio estaba disponible simplemente porque sus servidores estaban encendidos.

Claro que el indicador necesita definir qué solicitudes cuentan como válidas, qué respuestas representan éxito y qué período será analizado. Esas decisiones forman parte del contrato de medición.

Y aquí aparece la primera lección de SRE: no podemos administrar confiabilidad de manera seria si no acordamos sobre qué significa ser confiables.

### Los famosos nueves

Cuando discutimos disponibilidad, es común oír expresiones como tres nueves, cuatro nueves o cinco nueves.

Ellas representan diferentes niveles de disponibilidad:

| Disponibilidad | Indisponibilidad teórica en 30 días |
| --- | --- |
| 99% | 7 h 12 min |
| 99,9% | 43 min 12 s |
| 99,95% | 21 min 36 s |
| 99,99% | 4 min 19 s |
| 99,999% | 26 s |

*Valores aproximados para un período de 30 días, considerando una métrica de disponibilidad basada en tiempo.*

A primera vista, parece obvio que cinco nueves son mejores que tres. Técnicamente, representan una meta de disponibilidad más rigurosa. Pero eso no significa que sean siempre la elección correcta.

Elevar la disponibilidad puede exigir redundancia geográfica, replicación de datos, mecanismos de failover, tests adicionales, mayor capacidad ociosa y una arquitectura mucho más compleja.

Esas medidas pueden ser esenciales para un servicio financiero crítico. Para una herramienta interna que puede quedar indisponible por algunos minutos sin consecuencias relevantes, quizás representen un costo innecesario.

Además, disponibilidad basada en tiempo y disponibilidad basada en solicitudes no son métricas intercambiables. Una falla corta durante un pico de tráfico puede afectar muchos más usuarios que una falla más larga durante un período de baja demanda.

El objetivo no es elegir el mayor número posible de nueves. Es determinar qué nivel de confiabilidad atiende las necesidades reales del servicio.

## 4. SLI, SLO y SLA: tres siglas que no significan lo mismo

Una implementación de SRE empieza con definiciones claras. Y pocas cosas causan tanta confusión como esas tres siglas.

### SLI: Service Level Indicator

El SLI es el indicador que mide el comportamiento del servicio.

Puede representar la proporción de solicitudes bien sucedidas, la latencia de las respuestas, la tasa de errores u otra característica importante para los usuarios.

Ejemplos:

- Porcentaje de solicitudes HTTP completadas con éxito.
- Porcentaje de solicitudes que terminan en menos de 300 milisegundos.
- Porcentaje de operaciones de pago procesadas correctamente.
- Porcentaje de mensajes procesados dentro de un plazo definido.

Un buen SLI debe representar algo que realmente importa para la experiencia del usuario, no apenas algo fácil de recolectar.

### SLO: Service Level Objective

El SLO es el objetivo establecido para uno o más SLIs durante una ventana de medición.

Por ejemplo:

Por lo menos el 99,9% de las solicitudes válidas de la API deben completarse con éxito en una ventana móvil de 30 días.

Ahora tenemos algo que puede orientar decisiones.

Si el indicador empieza a alejarse de la meta, necesitamos investigar. Si el servicio permanece consistentemente dentro del objetivo, podemos evaluar si la arquitectura está adecuada o si existe espacio para mejorar la eficiencia operacional.

Un SLO no necesita tratar apenas de disponibilidad. Puede establecer objetivos separados para latencia, corrección de resultados o procesamiento dentro del plazo.

También es importante que el SLO sea definido con participación de ingeniería, producto y negocio. Una meta puramente técnica puede no representar lo que los usuarios realmente necesitan.

### SLA: Service Level Agreement

El SLA es un acuerdo formal de nivel de servicio, normalmente establecido con clientes o consumidores del servicio.

Puede definir compromisos, condiciones de medición, exclusiones y consecuencias cuando los niveles acordados no se cumplen.

Imagina que una plataforma ofrezca un SLA contractual de 99,9% de disponibilidad, mientras su equipo trabaja con un SLO interno más riguroso, del 99,95%.

El SLO interno crea un margen para administrar el riesgo antes de violar el compromiso contractual. El SLA, a su vez, establece las condiciones comerciales y las obligaciones perante el cliente.

En resumen:

| Concepto | Pregunta que responde |
| --- | --- |
| SLI | ¿Qué estamos midiendo? |
| SLO | ¿Qué resultado queremos alcanzar? |
| SLA | ¿Qué compromiso asumimos con el cliente? |

No basta crear un dashboard con gráficos coloridos. Sin un indicador relevante, una meta explícita y una comprensión de los compromisos asumidos, queda difícil decidir cuándo invertir en confiabilidad y cuándo priorizar otras mejoras.

## 5. Error budget: el mecanismo que equilibra confiabilidad y velocidad

Aquí llegamos al concepto que considero uno de los más importantes de SRE.

Si un servicio tiene un SLO de 99,9%, el complemento hasta 100% es de 0,1%.

Ese complemento es la base del *error budget*, o presupuesto de error, para una meta de disponibilidad.

En una ventana de 30 días, si estamos usando una métrica basada en tiempo, 0,1% equivale aproximadamente a 43 minutos de indisponibilidad.

Eso no significa que el equipo deba obligatoriamente quedar 43 minutos fuera del aire. Significa que la meta admite una determinada cantidad de fallas según la métrica y la ventana definidas.

Para un SLO basado en solicitudes, el presupuesto será calculado a partir de las solicitudes elegibles, no directamente de los minutos del mes.

Considera una API que recibe un millón de solicitudes válidas en una ventana y tiene un SLO de 99,9% de éxito.

El cálculo simplificado es:

```
Presupuesto de error = 1.000.000 × 0,001 = 1.000
```

En ese escenario, hasta mil solicitudes mal sucedidas pueden ocurrir antes de que el servicio supere el presupuesto correspondiente, considerando que ese sea el único indicador y que todos los eventos sean contabilizados de la misma manera.

El valor no debe interpretarse como una autorización para causar mil fallas deliberadamente. Es un límite para administrar el riesgo acumulado.

### ¿Por qué eso cambia la relación entre desarrollo y operaciones?

Sin un mecanismo compartido, la discusión tiende a volverse una disputa de opiniones.

Desarrollo quiere lanzar una funcionalidad. Operaciones teme que el deploy provoque una indisponibilidad. Producto presiona por el plazo. La decisión depende de quién tiene más autoridad o de quién está dispuesto a asumir el riesgo.

Con *error budgets*, existe una referencia común.

Si el servicio está operando bien y posee presupuesto disponible, el equipo puede continuar lanzando cambios, siempre que utilice mecanismos de mitigación de riesgo.

Si el presupuesto está siendo consumido rápidamente o ya se agotó, puede ser necesario reducir el ritmo de cambios riesgosos y priorizar la confiabilidad, manteniendo las correcciones urgentes de seguridad y otros trabajos esenciales.

El presupuesto transforma la confiabilidad en un criterio de decisión compartido, en vez de una discusión abstracta entre equipos.

### ¿Qué ocurre cuando el presupuesto se acaba?

Una política de SRE puede establecer que, cuando el presupuesto se agota, los lanzamientos que aumentan el riesgo sean temporalmente suspendidos hasta que la confiabilidad se recupere o la política sea revisada.

Eso no debe ser un ritual burocrático ni un castigo al equipo de desarrollo.

Es un mecanismo de gobernanza basado en evidencias.

Tampoco debemos confundir presupuesto disponible con permiso irrestricto para arriesgar. Un servicio puede estar dentro del SLO y aún presentar una vulnerabilidad de seguridad grave o un problema de integridad de datos que exija intervención inmediata.

La confiabilidad es multidimensional. El presupuesto es una herramienta para administrar determinados riesgos, no un sustituto del juicio técnico.

## 6. La operación no debería ser sinónimo de trabajo manual infinito

Existe una forma de trabajo que parece inevitable en muchos equipos de infraestructura: responder a alertas, reiniciar procesos, ejecutar scripts, ajustar configuraciones, recolectar logs y repetir procedimientos que ya fueron realizados decenas de veces.

El problema no es que toda actividad operacional sea manual. Existen situaciones en que la intervención humana es necesaria y deseable.

El problema es cuando tareas manuales, repetitivas y previsibles consumen la mayor parte del tiempo de profesionales que podrían estar resolviendo problemas estructurales.

En la terminología de SRE, ese tipo de trabajo es conocido como *toil*.

*Toil* es el trabajo operacional que tiende a ser manual, repetitivo, reactivo, automatizable y sin valor duradero proporcional al esfuerzo. Él también suele crecer conforme el sistema crece.

Imagina que un equipo necesite ejecutar manualmente un procedimiento de verificación para cada nuevo servicio implantado. Si existen diez servicios, quizás el proceso sea administrable. Si existen cientos, el equipo puede terminar gastando una parte creciente de su tiempo apenas repitiendo el mismo trabajo.

Una automatización bien proyectada puede ejecutar las verificaciones, registrar los resultados, alertar cuando sea necesario y mantener el procedimiento consistente.

El beneficio no es simplemente economizar algunos minutos.

Es permitir que el equipo invierta tiempo en mejoras que reduzcan la probabilidad de fallas, simplifiquen la arquitectura y disminuyan el costo operacional futuro.

Por eso, automatizar no debe significar transformar cualquier tarea en código sin evaluar su utilidad. La automatización necesita ser confiable, observable, mantenida y proporcional al problema.

El objetivo es reducir el trabajo repetitivo para liberar capacidad de ingeniería.

## 7. Monitoreo: alertar personas apenas cuando necesitan actuar

Tener miles de métricas no significa tener un sistema bien monitoreado.

Es posible construir dashboards impresionantes y, aun así, descubrir una indisponibilidad por el propio cliente.

También es posible configurar tantos alertas que nadie consiga distinguir los eventos importantes del ruido.

El monitoreo necesita responder una pregunta fundamental: ¿el servicio está atendiendo las necesidades de los usuarios?

Para eso, es útil acompañar indicadores de tráfico, latencia, errores y saturación, además de señales específicas de la aplicación y de los objetivos de servicio.

Pero medir no es suficiente. Necesitamos definir qué hacer cuando los indicadores se alejan de lo esperado.

Una regla práctica es separar las salidas del monitoreo de acuerdo con la urgencia:

- **Alerta inmediata**: alguien necesita actuar ahora para mitigar un impacto relevante.
- **Ticket o tarea**: existe un problema que necesita ser investigado, pero no exige intervención inmediata.
- **Log o registro**: la información necesita estar disponible para diagnóstico y análisis posterior.

Si todo genera un alerta urgente, nada es realmente urgente.

El resultado es la fatiga de alertas: profesionales pasan a ignorar notificaciones porque muchas de ellas no exigen acción o no representan impacto relevante.

Un equipo de SRE debe trabajar para que los alertas estén asociados a consecuencias reales, especialmente cuando hay riesgo de violación de SLO.

El objetivo no es eliminar la participación humana. Es reservar la atención humana para situaciones en que ella realmente hace diferencia.

## 8. Capacidad y performance: escalar no es simplemente agregar máquinas

Otro aspecto importante de SRE es planear la capacidad del sistema.

Las aplicaciones crecen por diferentes motivos. La base de usuarios aumenta, nuevas funcionalidades son lanzadas, campañas de marketing elevan el tráfico y eventos estacionales provocan picos de demanda.

Si el equipo solo reacciona cuando los recursos llegan al límite, la planificación ya falló.

Por otro lado, provisionar capacidad excesiva sin necesidad también tiene un costo. Recursos ociosos consumen dinero, aumentan la complejidad y pueden esconder ineficiencias.

El desafío es encontrar un equilibrio entre capacidad suficiente para atender la demanda y margen para absorber variaciones inesperadas.

Imagina una API que normalmente recibe mil solicitudes por segundo, pero puede llegar a cinco mil durante una campaña.

Antes de aumentar la infraestructura cinco veces, necesitamos entender cómo la aplicación se comporta bajo carga.

¿El banco de datos soporta el volumen adicional? ¿El pool de conexiones es suficiente? ¿Existe algún servicio dependiente con límite de capacidad? ¿Los mecanismos de cache ayudan o crean una concentración de carga? ¿Los tests de carga reproducen el comportamiento real?

Escalar horizontalmente una aplicación no resuelve automáticamente cuellos de botella en dependencias compartidas.

La planificación necesita considerar escenarios de crecimiento, tests de capacidad, costos, límites técnicos y mecanismos de degradación controlada.

También es importante preparar el sistema para fallas. Una arquitectura que opera exactamente en el límite de su capacidad normal puede entrar en colapso cuando pierde un nodo o necesita absorber el tráfico de otra instancia.

Margen de capacidad tiene costo. La falta de él también.

SRE procura tomar esa decisión con base en mediciones y en el impacto que diferentes escenarios tendrían sobre los usuarios.

## 9. Cambios en producción: pequeñas alteraciones también pueden causar grandes incidentes

Una línea de configuración, una actualización de dependencia o un cambio aparentemente trivial puede afectar un sistema entero.

El riesgo depende del contexto, de la arquitectura, de las dependencias y de las condiciones en que el cambio es aplicado.

Por eso, la gestión de cambios no debe entenderse apenas como un formulario de aprobación antes de cada deploy.

El objetivo es reducir el riesgo y el impacto de las alteraciones.

Entre las prácticas útiles están:

- Tests automatizados y validaciones antes de la implantación.
- Deploys progresivos, exponiendo el cambio inicialmente a una parcela del tráfico.
- Monitoreo de los indicadores de servicio durante la implantación.
- Rollback automatizado o procedimientos de recuperación bien definidos.
- Feature flags para separar la implantación del código de la activación de la funcionalidad.
- Análisis de riesgo proporcional al impacto potencial del cambio.

Esas técnicas ayudan a detectar problemas temprano y limitar el número de usuarios afectados.

Imagina una nueva versión de una API. En vez de sustituir todas las instancias de una sola vez, podemos disponibilizar la versión para un pequeño porcentaje del tráfico, observar errores y latencia y aumentar gradualmente la exposición.

Si los indicadores empeoran, el equipo puede interrumpir la progresión o revertir la versión antes de que el impacto se amplíe.

Lo importante es entender que los cambios seguros no son cambios que nunca fallan. Son cambios proyectados para que fallas sean detectadas y contenidas rápidamente.

## 10. Incidentes: primero recupere el servicio, después investigue

Cuando un sistema cae, existe una tendencia natural de buscar inmediatamente la causa.

Alguien quiere descubrir qué commit fue responsable, quién ejecutó el deploy o qué configuración estaba errada.

Esas preguntas pueden ser relevantes durante la investigación. Pero, mientras el servicio sigue indisponible, la prioridad es reducir el impacto sobre los usuarios.

En una respuesta a incidentes, es importante establecer responsabilidades claras, comunicar el estado del problema y ejecutar acciones de mitigación.

A veces, la solución inmediata será revertir un cambio. En otros casos, será necesario deshabilitar una funcionalidad, desviar tráfico, aumentar la capacidad o restaurar datos.

La prioridad es recuperar el servicio con seguridad. La investigación más profunda puede continuar después de que la situación esté estabilizada.

Eso no significa ignorar la causa. Significa separar dos actividades que exigen objetivos diferentes: mitigar el incidente y aprender de él.

### El postmortem no es un tribunal

Después de un incidente significativo, un equipo puede producir un *postmortem*: un documento que registra qué ocurrió, cuál fue el impacto, cómo se comportó el sistema y qué acciones pueden reducir la probabilidad o la gravedad de recurrencias.

Un buen análisis incluye una línea de tiempo, las señales observadas, las decisiones tomadas, las condiciones que contribuyeron al incidente y los ítems de mejora identificados.

Pero existe un principio cultural importante: el postmortem debe ser conducido sin culpabilización.

Eso no significa ausencia de responsabilidad. Significa evitar que la investigación se limite a apuntar una persona como causa del problema.

Si un ingeniero ejecutó un comando peligroso, necesitamos entender por qué ese comando estaba disponible, qué protecciones existían, si había revisión, si el procedimiento estaba documentado y por qué el sistema permitió que una única acción causara aquel impacto.

El análisis cambia cuando la pregunta deja de ser "¿quién erró?" y pasa a ser "¿qué condiciones hicieron posible ese resultado?".

Quizás el procedimiento fuera ambiguo. Quizás el ambiente no tuviera una validación automática. Quizás el sistema no ofreciera un rollback seguro. Quizás la presión operacional haya incentivado una decisión que parecía razonable con las informaciones disponibles.

El objetivo es transformar el aprendizaje en cambios concretos, con responsables y acompañamiento.

Un postmortem sin acciones efectivas corre el riesgo de volverse apenas documentación de un incidente que volverá a ocurrir.

## 11. Cómo empezar a implementar SRE sin transformar la empresa entera

La adopción de SRE no necesita empezar con una reorganización corporativa, un nuevo equipo o una plataforma compleja de observabilidad.

En verdad, empezar pequeño suele ser más útil.

Elige un servicio relevante, con usuarios identificables y un problema operacional que el equipo consiga observar.

Después, avanza en etapas.

### Paso 1: define qué significa éxito para el usuario

Identifica las operaciones más importantes del servicio. Para una API de pagos, puede ser completar pagos correctamente dentro de un límite de latencia. Para una plataforma de contenido, puede ser entregar páginas sin errores y dentro de un tiempo aceptable.

Evita empezar por métricas de infraestructura que no estén claramente ligadas a la experiencia del usuario.

### Paso 2: elige un SLI y establece un SLO

Empieza con un indicador que pueda ser medido de manera consistente.

Define la meta, la ventana de medición y las condiciones que determinan qué será considerado éxito.

No intentes resolver todas las dimensiones de confiabilidad de una vez. Una meta simple y útil es mejor que un conjunto de objetivos que nadie consigue interpretar.

### Paso 3: vuelve visible el presupuesto de error

Calcula el presupuesto correspondiente al SLO y acompaña su evolución.

El equipo necesita entender no apenas si está dentro de la meta, sino también la velocidad con que el presupuesto está siendo consumido.

Un presupuesto que desaparece rápidamente es una señal para investigar, incluso si la meta todavía no ha sido superada.

### Paso 4: mejora los alertas

Configura alertas que exijan acción humana cuando haya riesgo relevante para el servicio.

Reduce notificaciones redundantes, documenta los procedimientos de respuesta y define cuándo un evento debe ser tratado como incidente.

### Paso 5: identifica y elimina toil

Observa el trabajo diario del equipo. ¿Qué actividades son repetitivas? ¿Qué tareas dependen de alguien consultar manualmente un dashboard? ¿Qué procedimientos podrían ser automatizados con seguridad?

Prioriza las automatizaciones que reduzcan riesgo, frecuencia de intervención y tiempo gastado en tareas sin valor duradero.

### Paso 6: crea una rutina de aprendizaje

Después de incidentes relevantes, registra qué ocurrió y transforma las conclusiones en mejoras verificables.

Acompaña si las acciones fueron concluidas y si realmente redujeron la probabilidad o el impacto de fallas semejantes.

### Paso 7: amplía con evidencias

Cuando el modelo funcione para el primer servicio, documenta los resultados y comparte el aprendizaje.

Usa datos para mostrar qué mejoró: reducción de incidentes, recuperación más rápida, menor consumo de trabajo manual o mayor previsibilidad de los deploys.

Así, la expansión de SRE pasa a ser una decisión basada en resultados, y no apenas en la adopción de una nueva terminología.

## 12. Al final, ¿necesito ser desarrollador para trabajar con SRE?

No existe una única trayectoria profesional para SRE.

Personas con experiencia en sistemas operacionales, redes, infraestructura, cloud, observabilidad o desarrollo pueden construir una carrera en el área.

Pero existe una diferencia entre conocer los principios de SRE y ejercer una función de ingeniería de confiabilidad que exige desarrollar y mantener software.

En una posición de SRE, programación, automatización, depuración y comprensión del comportamiento de aplicaciones son frecuentemente fundamentales. También es necesario entender sistemas distribuidos, redes, capacidad, monitoreo y respuesta a incidentes.

No es obligatorio haber empezado la carrera como desarrollador de aplicaciones. Sin embargo, depender exclusivamente de procedimientos manuales limita el tipo de problema que vendrás a resolver.

Un profesional de infraestructura que aprende a escribir herramientas, automatizar procesos e investigar el comportamiento interno de aplicaciones está desarrollando competencias directamente útiles para SRE.

De la misma forma, un desarrollador que aprende sobre producción, observabilidad, resiliencia y gestión de incidentes amplía su capacidad de proyectar software operable.

El objetivo no es transformar todas las personas en especialistas en todo. Es reducir las barreras entre construir, entregar y operar sistemas.

## 13. La confiabilidad es una decisión de producto, no apenas de infraestructura

Existe una conclusión importante detrás de todos esos conceptos.

SLOs, *error budgets*, automatización, planificación de capacidad y postmortems no son herramientas aisladas. Ellos forman un modelo para tomar mejores decisiones sobre sistemas en producción.

El SLI muestra el comportamiento observado. El SLO define el nivel de servicio que queremos ofrecer. El SLA formaliza determinados compromisos con clientes. El error budget ayuda a administrar el riesgo de cambios. La automatización reduce trabajo repetitivo. Los postmortems transforman fallas en oportunidades de mejora.

Todo eso converge para una pregunta: ¿cómo entregar valor a los usuarios de manera sostenible?

Un servicio no necesita tener la mayor disponibilidad técnicamente posible. Necesita tener la disponibilidad apropiada para sus necesidades y sus riesgos.

Una aplicación crítica puede justificar inversiones considerables en redundancia y recuperación. Una herramienta interna puede aceptar una ventana de mantenimiento planeada si el impacto es bajo y el costo de disponibilidad continua es desproporcionado.

Esas decisiones no deben ser tomadas de manera aislada por el equipo de infraestructura. Producto, ingeniería, negocio y operación necesitan comprender los compromisos envueltos.

Tampoco basta declarar que las fallas son normales y usar eso como excusa para negligenciar la calidad. La filosofía de SRE no reduce la importancia de la confiabilidad; ella exige que la confiabilidad sea definida, medida y administrada de manera explícita.

El objetivo es evitar tanto la imprudencia como el exceso de conservadurismo.

## Conclusión: el mejor SRE no es aquel que nunca recibe un alerta

Es quien ayuda a construir un sistema que necesita menos intervenciones manuales, que vuelve visibles sus problemas antes de que se vuelvan crisis y que permite al equipo responder a fallas sin transformar cada incidente en una búsqueda por culpables.

SRE cambia la conversación entre desarrollo y operaciones porque sustituye parte de los conflictos de opinión por objetivos compartidos y datos observables.

En vez de exigir disponibilidad absoluta, definimos metas realistas. En vez de prohibir cambios por miedo, administramos el riesgo con presupuestos de error y mecanismos de implantación seguros. En vez de repetir tareas operacionales indefinidamente, invertimos en automatización. Y, cuando algo falla, investigamos las condiciones que permitieron el problema y mejoramos el sistema.

Mi recomendación es empezar con un servicio, medir lo que realmente importa y usar los resultados para orientar los próximos pasos.

No es necesario implantar una estructura completa de SRE para empezar a practicar ingeniería de confiabilidad. Es necesario reconocer que la operación forma parte del ciclo de vida del software y que las decisiones sobre confiabilidad necesitan considerar tanto la experiencia de los usuarios como el costo de mantener el sistema.

La pregunta que dejo es esta: si tu equipo pasara la próxima semana sin necesitar apagar ningún incendio, ¿qué finalmente conseguiría construir para que la semana siguiente también fuera así?

## Referencias para profundizar

- [Google SRE Book: Site Reliability Engineering](https://sre.google/sre-book/table-of-contents/)
- [Google SRE: Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)
- [Google SRE: Production Services Best Practices](https://sre.google/workbook/table-of-contents/)
- [Google Cloud: SLI, SLO y SLA](https://sre.google/workbook/implementing-slos/)
- [Google SRE: Introducción a la ingeniería de confiabilidad](https://sre.google/sre-book/introduction/)
