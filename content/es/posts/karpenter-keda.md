---
title: "Kubernetes más barato y eficiente: combinando Karpenter y KEDA"
date: 2026-10-21
draft: false
tags: ["Kubernetes", "FinOps", "Autoscaling"]
summary: "Escalar la aplicación según la demanda y dimensionar la infraestructura detrás de ella son problemas distintos. Con KEDA y Karpenter trabajando juntos, el cluster escala cuando necesita, reduce cuando puede y cuesta menos para entregar el mismo resultado."
---

¿Ya te detuviste a pensar cuánto dinero puedes estar gastando con un cluster Kubernetes que queda encendido el día entero, incluso cuando casi no tiene trabajo que ejecutar?

Es un problema común en ambientes cloud. Provisionamos infraestructura para soportar picos de demanda, pero cuando el movimiento baja, seguimos pagando por recursos que no estamos usando.

La buena noticia es que podemos atacar ese problema en dos frentes: escalar las aplicaciones de acuerdo con la demanda y ajustar la infraestructura para atender exactamente lo que ellas necesitan.

Aquí entran KEDA y Karpenter.

## El problema no es solo tener máquinas demasiado grandes

Imagina una aplicación que procesa transacciones financieras recibidas por una cola de Amazon SQS.

Durante buena parte del día llegan pocas mensajes. En determinados horarios, sin embargo, el volumen aumenta bastante y necesitamos procesar todo rápido.

Si mantenemos decenas de pods y máquinas disponibles todo el tiempo, gastaremos dinero con capacidad ociosa.

Si provisionamos pocos recursos, corremos el riesgo de acumular mensajes y aumentar el tiempo de procesamiento.

Necesitamos encontrar un equilibrio entre costo, capacidad y desempeño.

E intentar resolver todo apenas aumentando o disminuyendo el número de máquinas no es suficiente.

## KEDA: escalar la aplicación de acuerdo con la demanda

KEDA (Kubernetes Event-Driven Autoscaling) permite escalar aplicaciones con base en eventos y métricas externas.

En lugar de mirar apenas CPU y memoria, podemos usar señales como:

- La cantidad de mensajes en una cola SQS.
- El lag de consumidores en Kafka.
- Métricas externas disponibilizadas por sistemas de monitoreo.
- Eventos provenientes de otros servicios soportados.

Imagina que nuestra aplicación consume mensajes de una cola SQS.

Cuando el volumen aumenta, KEDA disponibiliza las métricas para el Kubernetes Horizontal Pod Autoscaler (HPA), que ajusta la cantidad de réplicas conforme las reglas configuradas.

Cuando la demanda disminuye, la cantidad de pods puede reducirse. En escenarios compatibles, incluso podemos escalar a cero réplicas y volver a ejecutar cuando lleguen nuevos eventos.

Eso significa que no necesitamos mantener una aplicación procesadora activa cuando no hay trabajo, siempre que ella soporte ese modelo y que los requisitos de latencia lo permitan.

Pero existe un detalle importante: reducir la cantidad de pods no significa necesariamente reducir la cantidad de máquinas.

Si los pods desaparecen y los nodos siguen encendidos, seguiremos pagando por la infraestructura.

Es justamente ahí donde Karpenter entra en la historia.

## Karpenter: provisionar la infraestructura que realmente necesitamos

Karpenter actúa en otra capa: la infraestructura del cluster.

Cuando existen pods pendientes porque no hay capacidad disponible, él analiza los requisitos de esos workloads y busca provisionar nodos compatibles.

Esa decisión considera informaciones como:

- Requests de CPU y memoria de los pods.
- Familias y tamaños de instancias permitidos.
- Arquitecturas de procesador compatibles.
- Zonas de disponibilidad.
- Restricciones de capacidad y políticas de provisionamiento.
- Opciones de compra, como instancias On-Demand y Spot, cuando están configuradas.

La gran ventaja es no necesitar mantener manualmente un grupo de nodos para cada combinación de instancia que deseamos usar.

En ambientes AWS, por ejemplo, Karpenter puede seleccionar entre diferentes tipos de instancia permitidos por las configuraciones del cluster, en vez de depender exclusivamente de una estrategia basada en grupos fijos de Auto Scaling.

También puede consolidar workloads cuando eso sea seguro y económicamente ventajoso, reemplazando nodos subutilizados por una configuración más eficiente.

El objetivo no es simplemente crear más máquinas. Es disponibilizar la capacidad necesaria y evitar mantener recursos innecesarios.

## El mejor resultado ocurre cuando usamos los dos juntos

Ahora imagina el flujo completo.

Una cola empieza a recibir miles de mensajes.

1. KEDA identifica el aumento de la demanda y disponibiliza las métricas para el HPA.
2. El HPA aumenta la cantidad deseada de pods.
3. Si no hay capacidad suficiente, algunos pods quedan pendientes.
4. Karpenter identifica la necesidad y provisiona nodos compatibles.
5. Cuando las nuevas máquinas quedan disponibles, el scheduler distribuye los pods.
6. Después de que la cola se procesa y la demanda disminuye, KEDA reduce las réplicas.
7. Karpenter puede consolidar o remover nodos que dejaron de ser necesarios, respetando sus políticas y las restricciones de los workloads.

Cada herramienta resuelve una parte distinta del problema.

KEDA reacciona a la demanda de la aplicación. Karpenter ajusta la capacidad de la infraestructura para acomodar esa demanda.

Esa combinación permite trabajar con escalabilidad en dos capas, en vez de intentar resolver todo con una única herramienta.

## ¿Y las instancias Spot? ¿Vale la pena usarlas?

Las instancias Spot pueden reducir bastante el costo de workloads tolerantes a interrupciones, pero exigen planificación.

Karpenter puede trabajar con opciones Spot y On-Demand, siempre que estén permitidas en las configuraciones de los NodePools.

Cuando una interrupción Spot es anunciada y el mecanismo de interrupción está debidamente configurado, Karpenter puede intentar reemplazar la capacidad afectada.

Eso no significa que la interrupción será invisible. El reemplazo depende de la disponibilidad de capacidad, de las configuraciones del cluster y del tiempo necesario para iniciar y preparar los nuevos nodos.

Por eso, las aplicaciones críticas deben considerar tolerancia a fallos, múltiples zonas de disponibilidad, tratamiento de interrupciones y reprocesamiento seguro de mensajes.

La estrategia más eficiente no es usar Spot en todo. Es identificar qué workloads consiguen aprovechar esa modalidad sin comprometer los requisitos del negocio.

## Escalar a cero también exige cuidado

Existe otro punto interesante en esta arquitectura: la posibilidad de mantener determinadas aplicaciones sin réplicas cuando no hay demanda.

Para procesadores de colas, eso puede representar un ahorro relevante.

Pero escalar a cero no es gratuito ni instantáneo.

Cuando llega un nuevo evento, puede haber un intervalo hasta que KEDA solicite nuevas réplicas, Kubernetes agende los pods y Karpenter provisione nodos en caso de que no exista capacidad disponible.

Si la aplicación necesita responder en milisegundos, tal vez sea necesario mantener alguna capacidad mínima precalentada.

Si procesa tareas asíncronas y tolera algunos segundos o minutos de espera, escalar a cero puede ser una estrategia excelente.

La decisión depende del perfil del workload, no apenas de la posibilidad técnica de apagarlo.

## ¿Qué realmente hace la diferencia en la reducción de costos?

Instalar KEDA y Karpenter no garantiza por sí solo una cuenta menor.

El resultado depende de cómo configuramos y operamos el cluster.

Algunas prácticas hacen bastante diferencia:

- Definir requests de CPU y memoria coherentes con el consumo real de las aplicaciones.
- Configurar disparadores de escalabilidad que representen la demanda del negocio.
- Permitir flexibilidad de instancias sin violar los requisitos de compatibilidad.
- Usar Spot en los workloads adecuados.
- Configurar políticas de consolidación que respeten disponibilidad e interrupciones.
- Medir costos, utilización, latencia y tiempo de procesamiento antes y después de los cambios.

También es importante observar que KEDA y Karpenter no sustituyen el dimensionamiento correcto de las aplicaciones. Si los requests están incorrectos o los disparadores mal configurados, la automatización puede tomar decisiones inadecuadas.

La meta no debe ser simplemente reducir el número de máquinas. Debe ser reducir el costo por unidad de trabajo procesada, manteniendo el desempeño y la confiabilidad esperados.

## Al final, la idea es simple

Kubernetes ofrece mecanismos poderosos de escalabilidad, pero la eficiencia financiera depende de ajustar la aplicación y la infraestructura de forma coordinada.

KEDA ayuda a responder la pregunta: ¿cuántas réplicas necesitamos para procesar la demanda actual?

Karpenter ayuda a responder otra: ¿qué infraestructura necesitamos para ejecutar esas réplicas?

Cuando combinamos los dos, conseguimos aproximar el consumo de recursos a la demanda real, aprovechando mejor la capacidad disponible y reduciendo desperdicios.

Porque, al final de cuentas, no basta tener un cluster que escala.

El objetivo es tener un cluster que escala cuando necesita, reduce cuando puede y cuesta menos para entregar el mismo resultado.
