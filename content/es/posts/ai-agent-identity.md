---
title: "Tus agentes de IA no necesitan API keys. Necesitan identidad."
date: 2026-10-21
draft: false
tags: ["Agentes IA", "Seguridad", "SPIFFE", "Zero Trust"]
summary: "Las API keys almacenadas en variables de entorno no prueban quién ejecuta qué. Con SPIFFE y SPIRE, la identidad pasa a ser una propiedad verificable del workload, lo que cambia por completo la seguridad de los agentes autónomos."
---

Estamos construyendo sistemas de IA que ejecutan código, consultan bases de datos, llaman APIs, acceden servicios en la nube y delegan tareas a otros agentes. En algunos casos, estos sistemas ya operan con autonomía suficiente para ejecutar secuencias completas de acciones sin que una persona apruebe cada paso.

Pero existe un problema básico en esta arquitectura: ¿cómo prueban estos agentes quién son?

En la mayoría de los sistemas tradicionales, la respuesta es decepcionantemente simple: alguien pone una API key en una variable de entorno, inyecta un token en el container o configura una credencial permanente en el servicio. El agente recibe acceso y empieza a trabajar.

Eso funciona hasta que algo sale mal.

Un prompt malicioso convence al agente de llamar una herramienta indebida. Una vulnerabilidad permite leer variables de entorno. Un container comprometido expone sus credenciales. De pronto, un secreto creado para un servicio específico puede ser usado por alguien que no debería tener acceso a él.

El problema no es solo el modelo de IA. Es la arquitectura de identidad que colocamos a su alrededor.

La solución pasa por una idea antigua en seguridad de infraestructura que gana un protagonismo nuevo con agentes autónomos: la identidad no debería ser un secreto almacenado dentro de una aplicación. Debería ser una propiedad verificable del workload que está ejecutando.

Aquí entran SPIFFE y SPIRE.

## El problema de poner secretos dentro de agentes

Imagina un agente responsable de investigar documentos, consultar una base de datos vectorial y ejecutar herramientas a través del Model Context Protocol, el MCP.

Para hacer su trabajo, necesita un conjunto de permisos:

- Consultar una API interna.
- Buscar documentos de un determinado cliente.
- Invocar herramientas específicas.
- Acceder a un servicio alojado en la nube.

El enfoque convencional es entregar credenciales al agente y confiar en que las usará correctamente.

Pero un agente de IA no es una aplicación tradicional en el sentido operacional. Interpreta instrucciones, recibe contenido externo, elige herramientas y puede producir secuencias de llamadas que sus desarrolladores no anticiparon.

Un atacante no necesita necesariamente comprometer el servidor entero. Dependiendo de los permisos disponibles, basta inducir al agente a ejecutar una acción indebida.

Si una credencial permanente es accesible al proceso, el atacante podrá intentar extraerla o abusar de ella. Y si logra copiarla, la credencial puede seguir en uso incluso después de que la ejecución original termine.

Existe otro problema: una API key normalmente identifica una credencial, no la integridad del proceso que la usa. No prueba, por sí sola, qué binario está ejecutando, en qué container está, a qué namespace pertenece o si debería tener acceso a ese recurso.

La pregunta correcta deja de ser solo "¿cuál es la clave de este agente?" y pasa a ser:

¿Cómo puede el sistema verificar la identidad de este workload y decidir, en cada conexión, qué está autorizado a hacer?

## SPIFFE y SPIRE: identidad como infraestructura

SPIFFE significa Secure Production Identity Framework for Everyone. Es una especificación para identificar workloads de manera estandarizada.

SPIRE es una implementación de esa arquitectura. Aporta los mecanismos necesarios para atestar workloads, emitir identidades criptográficas y distribuir información de confianza.

La pieza central es el SVID, o SPIFFE Verifiable Identity Document.

Un SVID puede ser un certificado X.509 o un token JWT firmado. En lugar de depender de una clave permanente incrustada en la aplicación, el workload recibe una identidad emitida dinámicamente después de pasar las verificaciones configuradas.

Una identidad SPIFFE puede tener la siguiente forma:

```
spiffe://example.org/agent/mcp-executor
```

Ese identificador representa una identidad dentro de un dominio de confianza. No es una contraseña: su utilidad depende de las credenciales criptográficas asociadas y de las políticas aplicadas por los servicios que lo aceptan.

El flujo general funciona así:

1. El servidor SPIRE verifica la identidad del nodo en que el workload está ejecutando.
2. El agente SPIRE local identifica atributos del proceso o container que solicita credenciales.
3. El servidor compara esos atributos con las reglas de registro autorizadas.
4. Si las condiciones se cumplen, el workload recibe un SVID de corta duración.
5. El workload usa esa identidad para autenticarse ante servicios que confían en la autoridad emisora.

El detalle importante es que la aplicación no necesita cargar una clave permanente para probar su identidad. Puede obtener y renovar sus credenciales dinámicamente por medio del agente SPIRE local.

Eso cambia la manera en que pensamos la autenticación.

## ¿Qué ocurre dentro del SPIRE Server?

El SPIRE Server es el plano de control responsable de administrar la confianza y emitir identidades.

Su implementación en Go está organizada en componentes especializados.

El servidor inicializa sus endpoints gRPC, integra plugins, accede al almacenamiento de registros y mantiene los mecanismos de autoridad certificadora necesarios para firmar credenciales.

El proceso de emisión de identidad depende de algunas etapas distintas.

### 1. Primero, el nodo debe probar su identidad

Antes de confiar en un agente, el sistema necesita verificar la infraestructura en la que está ejecutando.

En Kubernetes, eso puede envolver tokens proyectados de service accounts. En ambientes de nube, se pueden usar documentos de identidad de instancias o mecanismos equivalentes soportados por los plugins de atestación.

El servidor valida las evidencias de acuerdo con el mecanismo configurado y establece la identidad del nodo.

A partir de ahí, el agente SPIRE puede comunicarse con el servidor usando su identidad y un canal autenticado.

### 2. Después, el proceso debe ser identificado

Un nodo confiable no significa que todos los procesos ejecutados en él sean confiables.

El agente SPIRE consulta atributos del workload, que pueden incluir namespace, service account, imagen del container y otras propiedades soportadas por el ambiente.

Esos atributos se comparan con los registros de identidad autorizados.

Es posible, por ejemplo, distinguir un ejecutor de herramientas de un agente responsable de consultar documentos, incluso si ambos ejecutan en el mismo cluster.

La seguridad depende de la calidad de esos selectores, de la integridad de la atestación y de la precisión de las reglas configuradas.

### 3. Finalmente, el servidor emite la credencial

Cuando la solicitud es autorizada, el SPIRE Server firma el SVID apropiado.

Para X.509, el resultado es un certificado que puede usarse en conexiones TLS mutuas. Para JWT, el resultado es un token firmado que puede ser presentado a servicios compatibles.

El certificado o token tiene una validez limitada. La aplicación debe renovar sus credenciales cuando sea necesario, en vez de depender indefinidamente de un secreto estático.

SPIRE también administra la rotación de las claves de firma y la distribución de los bundles de confianza.

Es infraestructura de identidad, no solo un generador de tokens.

## ¿Qué cambia en la comunicación entre agentes?

Considera un agente orquestador que necesita llamar un servidor MCP responsable de ejecutar herramientas internas.

En la arquitectura convencional, el servidor MCP puede exigir una API key compartida o un token configurado manualmente.

Con SPIFFE/SPIRE, ambos workloads pueden presentar identidades verificables por medio de certificados X.509.

Durante una conexión mTLS:

1. El cliente presenta su identidad criptográfica.
2. El servidor presenta la suya.
3. Los dos lados validan los certificados y la cadena de confianza.
4. Las políticas de autorización determinan si esa identidad puede ejecutar la operación solicitada.

Esto da autenticación mutua y cifrado en tránsito, y reduce la dependencia de secretos compartidos.

Pero hay una distinción fundamental: autenticar un agente no significa autorizar todas sus acciones.

Un agente identificado como `mcp-executor` aún puede estar autorizado a llamar solo determinadas herramientas. El servidor MCP debe verificar esa restricción y aplicarla de verdad.

La identidad responde "¿quién está llamando?". La autorización responde "¿qué puede hacer esa identidad?".

Mezclar las dos cosas es una manera bastante eficiente de crear una arquitectura aparentemente segura que sigue concediendo permisos excesivos.

## ¿Y cuando el agente necesita acceder a la nube?

El problema no termina en las llamadas entre servicios internos.

Los agentes frecuentemente necesitan acceder a servicios administrados, almacenamientos, colas y plataformas de IA alojadas en nubes públicas.

Almacenar claves permanentes de IAM dentro de containers es una alternativa particularmente riesgosa.

Un enfoque mejor es usar federación de identidad.

El agente solicita un JWT SVID destinado a la audiencia esperada por el proveedor de nube. El servicio de identidad de la nube valida el emisor, la firma, la audiencia y las condiciones de confianza configuradas. Si todo está correcto, el token puede ser canjeado por credenciales temporales con permisos limitados.

El resultado es una cadena de confianza entre el workload y el servicio de nube, sin necesidad de distribuir una clave permanente para cada agente.

Esta configuración exige integración explícita con el proveedor, políticas de confianza adecuadas y permisos de mínimo privilegio. No basta emitir cualquier JWT y esperar que la nube lo acepte.

Aun así, ese modelo es mucho más interesante que copiar secretos para decenas de aplicaciones.

## La identidad no resuelve todo

Sería tentador concluir que, después de instalar SPIRE, el problema de seguridad de los agentes está resuelto.

No lo está.

Si un agente legítimo es manipulado por prompt injection, todavía puede intentar ejecutar acciones que están dentro de los permisos que recibió. Un SVID válido no impide que un proceso autorizado tome una mala decisión.

SPIRE reduce ciertos riesgos de identidad y de exposición de credenciales, pero no reemplaza las demás capas de seguridad.

Un despliegue serio necesita combinar:

- Identidades específicas por workload.
- Credenciales de corta duración.
- Permisos mínimos por herramienta y servicio.
- Atestación y reglas de registro rigurosas.
- Protección de las claves de firma, preferentemente con integración a sistemas apropiados de gestión de claves.
- Auditoría de emisión de credenciales y operaciones administrativas.
- Controles de entrada, validación de argumentos y límites de ejecución para las herramientas.
- Tests que verifiquen el aislamiento entre tenants.

También es necesario recordar que un workload comprometido puede usar su identidad legítima mientras siga válida y autorizada. Revocación, contención y respuesta a incidentes siguen siendo necesarias.

La identidad criptográfica es una capa de la arquitectura de seguridad, no un sustituto de ella.

## La arquitectura que hace sentido para agentes autónomos

Un despliegue práctico puede empezar con el SPIRE Server, los agentes distribuidos en los nodos y registros específicos para cada tipo de workload.

Las aplicaciones usan SDKs compatibles con SPIFFE para obtener sus SVIDs por el socket Unix local. Los servicios internos validan las identidades y aplican políticas de autorización. Cuando es necesario, la federación permite extender la confianza a otros dominios o proveedores de nube.

En producción también entran en escena la persistencia de los registros, la disponibilidad del plano de control, la gestión de claves, la rotación de credenciales, la distribución de bundles y la observabilidad.

El objetivo no es solo hacer funcionar el primer certificado. Es garantizar que la infraestructura siga segura cuando haya cientos de agentes, varios tenants, múltiples ambientes y cambios constantes en los workloads.

Ese es el momento en que la identidad deja de ser un detalle de configuración y pasa a ser una capacidad central de la plataforma.

## El próximo problema no es emitir credenciales. Es limitar la autonomía.

Los agentes de IA están facilitando construir sistemas que ejecutan tareas antes reservadas a operadores humanos o a aplicaciones rígidamente programadas.

Pero autonomía operacional no debería significar acceso irrestrito.

Cuántas más herramientas puede invocar un agente, más importante se vuelve distinguir su identidad, su contexto y sus permisos. La seguridad debe acompañar al agente durante la ejecución, en vez de depender de un secreto distribuido en el momento del deploy.

SPIFFE y SPIRE ofrecen una base sólida para este modelo: identidades verificables, credenciales temporarias y relaciones de confianza explícitas entre workloads.

Esto no elimina el prompt injection, los bugs ni las decisiones incorrectas. Elimina o reduce significativamente una clase de riesgos causada por credenciales permanentes e identidad mal definida.

El cambio de mentalidad es simple, aunque la implementación exija cuidado:

Deja de preguntar qué API key entregar al agente. Empieza a preguntar cómo prueba quién es, por qué recibió esa identidad y qué acciones está autorizada a ejecutar esa identidad.

En una infraestructura con agentes autónomos, esa diferencia deja de ser apenas una buena práctica. Pasa a formar parte del diseño fundamental del sistema.
