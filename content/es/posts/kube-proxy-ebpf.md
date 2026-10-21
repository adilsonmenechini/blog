---
title: "¿Realmente necesita Kubernetes del kube-proxy? Qué cambia cuando eBPF asume el networking"
date: 2026-10-21
draft: false
tags: ["Kubernetes", "Cilium", "eBPF", "Redes", "Linux", "Rendimiento", "Cloud Native"]
summary: "¿El kube-proxy es obligatorio? Con eBPF, Cilium implementa el reenvío de Services directamente en el kernel Linux. Antes de remover componentes, entiende el camino del paquete, dónde el modelo tradicional sale caro y cuándo vale la pena migrar."
---

Durante años, tratar el kube-proxy como una pieza obligatoria de cualquier cluster Kubernetes parecía tan natural como instalar un runtime de containers o configurar un CNI. Creas un cluster, instalas los componentes de red, y el kube-proxy está ahí, haciendo su trabajo en silencio.

Pero ¿y si una parte importante de esa arquitectura pudiera eliminarse?

Es exactamente lo que algunas implementaciones modernas de networking para Kubernetes están haciendo. Con eBPF, proyectos como Cilium consiguen implementar el reenvío de tráfico de Services directamente en el kernel Linux, sin depender del kube-proxy y de sus reglas tradicionales de iptables.

La promesa es interesante: menos procesamiento innecesario, mayor control sobre el camino de los paquetes, observabilidad integrada y una arquitectura que puede escalar mejor en determinados escenarios.

Solo que existe un detalle importante. Cambiar una arquitectura por otra no es automáticamente una optimización. Antes de salir removiendo componentes del cluster, necesitamos entender el problema que estamos intentando resolver.

Vamos a acompañar el camino de un paquete, entender dónde el modelo tradicional empieza a salir caro, descubrir qué hace realmente eBPF y, finalmente, responder a la pregunta que interesa: ¿cuándo vale la pena abandonar el kube-proxy?

## 1. La ilusión de la Service IP

Empecemos por lo básico.

En Kubernetes, cuando creamos un Service, normalmente recibimos una dirección IP virtual, conocida como ClusterIP.

Imagina esta configuración:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mi-api
spec:
  selector:
    app: mi-api
  ports:
    - port: 80
      targetPort: 8080
  type: ClusterIP
```

El Service puede recibir una dirección como `10.96.0.100`. Esa dirección representa la entrada lógica para un conjunto de Pods, y no necesariamente una dirección configurada en una interfaz de red.

Si tres Pods atienden al Service, el cliente no necesita conocer las direcciones individuales de ellos. Accede al Service, y la infraestructura de red reenvía la conexión a uno de los backends elegibles.

Es una abstracción conveniente. El consumidor conoce una dirección estable, mientras los Pods pueden nacer, morir, cambiar de IP y ser reemplazados sin exigir que cada cliente actualice su configuración.

Pero alguien necesita transformar esa abstracción en tráfico de verdad.

Tradicionalmente, esa es una de las responsabilidades del kube-proxy.

Él acompaña las informaciones de Services y EndpointSlices por la API del Kubernetes y programa mecanismos de reenvío en el nodo. Dependiendo del modo utilizado, eso involucra reglas de iptables, IPVS u otro mecanismo compatible con la implementación.

En el modo iptables, por ejemplo, las reglas permiten reconocer el destino virtual, seleccionar un backend y realizar la traducción de dirección necesaria.

El camino simplificado queda así:

```text
Cliente
   |
   v
Service IP: 10.96.0.100:80
   |
   v
Reglas de reenvío en el nodo
   |
   v
Selección de un backend
   |
   v
Pod: 10.244.1.10:8080
```

La Service IP no necesita existir como dirección atribuida a una interfaz para funcionar. El plano de datos implementa el comportamiento necesario para que el tráfico destinado a él sea reenviado correctamente.

Es una solución elegante. Y funcionó durante años en clusters de todos los tamaños.

Entonces, ¿cuál es el problema?

## 2. Cuando una solución simple empieza a salir caro

Imagina un cluster con miles de Services, decenas de miles de Pods y una cantidad enorme de endpoints cambiando constantemente.

El problema no es simplemente el número de Pods. El costo depende de la cantidad de reglas, del formato de ellas, de la frecuencia de las alteraciones, de la distribución de los endpoints y del camino recorrido por los paquetes.

En el modo tradicional basado en iptables, el kube-proxy mantiene reglas que representan Services y sus backends. En clusters grandes, esa configuración puede crecer significativamente.

Y existe un costo adicional: cuando la configuración cambia, las reglas necesitan ser reconciliadas y actualizadas. En determinados escenarios, eso puede aumentar el tiempo de convergencia y consumir CPU durante operaciones de actualización.

Aquí está la distinción que importa: una cosa es reenviar un paquete; otra es mantener miles de destinos virtuales, decenas de miles de endpoints y sus alteraciones representados de manera eficiente.

El iptables no es simplemente una lista ingenua que siempre recorre todas las reglas para cada paquete. El costo real depende de la organización de las chains, de los mecanismos utilizados por el kernel, de las reglas generadas y del camino de ejecución. Aun así, el volumen de reglas y el trabajo de actualización pueden volverse un cuello de botella en determinadas topologías.

Tampoco sirve mirar apenas el reenvío de paquetes. Un cluster puede presentar problemas durante actualizaciones en masa incluso cuando su latencia normal parece perfectamente aceptable.

Es por eso que, en infraestructura de gran escala, necesitamos mirar dos dimensiones distintas:

- **Plano de datos**: ¿cuánto cuesta procesar el tráfico mientras circula?
- **Plano de control de red**: ¿cuánto cuesta mantener el estado y actualizar las reglas cuando la infraestructura cambia?

Una arquitectura puede ser eficiente en una dimensión y mala en la otra.

Y aquí entra eBPF.

## 3. eBPF: poner la lógica de red dentro del kernel

eBPF significa extended Berkeley Packet Filter. A pesar del nombre histórico, su utilización moderna va mucho más allá de la filtración de paquetes.

Él permite ejecutar programas verificados dentro del kernel Linux, asociados a puntos de ejecución específicos. Dependiendo del tipo de programa y del hook utilizado, esos programas pueden inspeccionar tráfico, aplicar políticas, recolectar métricas e implementar partes del reenvío de red.

El detalle importante es que no estamos hablando de ejecutar una aplicación convencional en el espacio de usuario para tomar una decisión sobre cada paquete.

El programa eBPF se ejecuta en el kernel, cerca del punto en que la decisión necesita ocurrir.

Eso permite implementar caminos de datos especializados, evitando determinadas etapas de procesamiento presentes en otras arquitecturas.

Una de las estructuras utilizadas es el eBPF map.

Piensa en un map como una estructura de datos accesible a los programas eBPF, capaz de almacenar informaciones como asociaciones entre Services y backends, estado de conexiones o datos necesarios para la aplicación de políticas.

Un mapa puede usar una tabla hash, por ejemplo. En ese caso, una consulta promedio puede presentar un costo cercano a `O(1)`, considerando una tabla bien dimensionada y operaciones de hash adecuadas.

Pero atención: eso no significa que todo el procesamiento de red pasa a tener complejidad `O(1)`. La consulta al mapa es solo una etapa. El camino completo todavía puede involucrar selección de backend, estado de conexión, políticas, encapsulamiento, ruteo y otras operaciones.

La ventaja no es una promesa matemática universal. Es la posibilidad de construir un camino de datos más directo y especializado para el problema en cuestión.

## 4. Cilium y el camino hasta el Pod

Cilium usa eBPF para implementar funcionalidades de networking, seguridad y observabilidad en Kubernetes.

En una configuración compatible, él puede sustituir el kube-proxy, asumiendo el reenvío de tráfico de los Services por medio de sus propios programas y estructuras de datos en el kernel.

El flujo conceptual cambia de:

```text
Cliente
   |
   v
Service IP
   |
   v
Reglas del kube-proxy
   |
   v
Procesamiento de NAT y selección
   |
   v
Pod de destino
```

Para algo semejante a:

```text
Cliente
   |
   v
Service IP
   |
   v
Hook eBPF en el camino del paquete
   |
   v
Consulta a las estructuras de datos
   |
   v
Selección del backend
   |
   v
Pod de destino
```

El segundo diagrama es deliberadamente simplificado. Los hooks utilizados, las operaciones ejecutadas y la necesidad de NAT dependen de la configuración y del camino del tráfico. Cilium no elimina mágicamente todo procesamiento de red, ni significa que cada paquete recorre siempre una única consulta a un mapa.

Lo que ofrece es una implementación alternativa del plano de datos, con control más directo sobre las decisiones de reenvío.

En vez de depender del kube-proxy para mantener las reglas tradicionales de Services, Cilium acompanha el estado relevante del Kubernetes y programa sus estructuras y sus programas eBPF.

El resultado es una arquitectura en la cual el procesamiento puede evitar parte del trabajo asociado al camino convencional.

Y no estamos hablando apenas de rendimiento.

## 5. Más que velocidad: seguridad y observabilidad

Una de las ventajas interesantes de Cilium es que el mismo ecosistema de eBPF puede utilizarse para diferentes necesidades de infraestructura.

### Políticas de red

Cilium ofrece políticas de red que permiten controlar qué workloads pueden comunicarse, con base en atributos como identidad, labels, dirección del tráfico y otros criterios soportados.

Eso ayuda a implementar segmentación entre servicios y reducir la superficie de comunicación permitida.

Naturalmente, la seguridad depende de las políticas configuradas, del modelo de identidad, de los puntos de aplicación y de los caminos efectivamente cubiertos. Instalar Cilium no significa que toda la red estará automáticamente protegida.

### Observabilidad con Hubble

Hubble usa la infraestructura de observabilidad de Cilium para exponer informaciones sobre flujos de red y comunicación entre workloads.

En vez de investigar un problema exclusivamente a partir de logs de aplicación y capturas manuales de paquetes, podemos obtener visibilidad sobre conexiones, decisiones de política y flujos observados.

Especialmente útil en ambientes en los cuales decenas o cientos de servicios se comunican y el problema no está necesariamente dentro de la aplicación.

### Balanceo de carga

Cilium también implementa mecanismos de balanceo para tráfico destinado a Services, con estrategias y comportamientos que dependen de la configuración.

La selección de backend puede ocurrir en el plano de datos, utilizando informaciones mantenidas en el kernel.

Eso no significa que todas las estrategias estén disponibles en cualquier configuración, ni que un algoritmo específico sea siempre superior. La afinidad de sesión, la distribución de carga, el estado de conexiones y los requisitos de la aplicación siguen influyendo en la elección.

El punto central es que networking, seguridad y observabilidad pueden compartir una arquitectura integrada.

Eso puede simplificar la operación, pero también aumenta la importancia de comprender la implementación, los requisitos del kernel y las herramientas de diagnóstico utilizadas.

## 6. ¿Qué significa realmente eliminar el kube-proxy?

Aquí vale evitar una confusión común.

El kube-proxy no es el Kubernetes entero. Es un componente que implementa parte del comportamiento de red asociado a los Services.

El Kubernetes sigue necesitando sus mecanismos de control, sus objetos Service y EndpointSlice y una implementación de red capaz de conectar los workloads.

Cuando Cilium opera en modo de sustitución del kube-proxy, asume las responsabilidades correspondientes de reenvío que fueron configuradas para ese modo.

Eso no significa eliminar el CNI, remover todos los mecanismos de NAT o hacer que todo el tráfico deje de pasar por el kernel.

Tampoco significa que el iptables desaparezca completamente del nodo. Él puede seguir siendo utilizado por otras partes del sistema operativo, por herramientas de firewall o por componentes que no forman parte del camino de Services sustituido por Cilium.

La expresión *kube-proxy replacement* es más precisa que interpretar el cambio como una máquina Linux completamente libre de iptables.

La distinción es importante porque la arquitectura no se resume a remover un proceso. Es necesario entender qué responsabilidades fueron transferidas, cuáles permanecen y cómo el nuevo camino es implementado.

## 7. Entonces, ¿cuánto mejora el desempeño?

Esa es la pregunta que suele aparecer después de una demostración impresionante.

La respuesta honesta es: depende.

Cilium puede reducir determinados costos de reenvío, mejorar el comportamiento en escenarios con gran cantidad de Services y ofrecer ventajas en cargas de trabajo específicas. Pero no existe un porcentaje universal de ganancia que pueda aplicarse a cualquier cluster.

El resultado depende de factores como:

- Cantidad de Services y endpoints.
- Tasa de creación, remoción y actualización de workloads.
- Volumen de tráfico y tamaño de los paquetes.
- Tráfico dentro del mismo nodo o entre nodos.
- Necesidad de encapsulamiento y traducción de direcciones.
- Configuración de políticas de seguridad.
- Modelo de balanceo de carga.
- Versión del kernel Linux y de Cilium.
- Hardware, drivers y configuración de la infraestructura.

Si el cluster está limitado por consultas al banco de datos, procesamiento de la aplicación o latencia de una dependencia externa, cambiar el plano de datos de red puede producir poca o ninguna ganancia perceptible para el usuario.

De la misma forma, no tiene sentido presumir que cualquier configuración tradicional sea lenta. Un cluster pequeño, con pocas reglas y baja tasa de alteración, puede funcionar muy bien con kube-proxy.

Antes de decidir, yo mediría por lo menos cuatro cosas:

1. CPU consumida por los componentes de networking.
2. Latencia y throughput del tráfico relevante.
3. Tiempo de convergencia después de cambios en los Services y endpoints.
4. Comportamiento del cluster durante picos de creación y remoción de workloads.

Los benchmarks necesitan representar la carga real y comparar configuraciones equivalentes. También es necesario probar conectividad, políticas, acceso externo, DNS y los modos de tráfico utilizados por la aplicación.

Sin esas medidas, cambiar la arquitectura puede ser apenas una manera más sofisticada de cambiar algo que no era el problema.

## 8. ¿Cuándo vale la pena adoptar Cilium?

La decisión depende menos de una disputa entre tecnologías y más de las necesidades del ambiente.

### Cluster pequeño o convencional

Si operas un cluster con pocas decenas de nodos, una cantidad moderada de Services y una aplicación que no presenta cuellos de botella de networking, no hay razón automática para migrar.

El kube-proxy sigue siendo una opción válida. Una implementación tradicional puede ser simple, predecible y suficiente para el trabajo.

### Cluster grande y con muchos cambios

Si el ambiente tiene gran volumen de Services y endpoints, actualizaciones frecuentes, presión de CPU relacionada a la red o problemas de convergencia, vale investigar alternativas.

En ese escenario, Cilium puede ofrecer beneficios tanto en el reenvío como en la forma de mantener el estado de la red.

Pero la decisión debe venir acompañada de mediciones y tests de carga, no apenas de la cantidad de nodos.

### Ambientes que exigen seguridad y visibilidad

Incluso cuando el desempeño no es el principal problema, los recursos de políticas de red, identidad y observabilidad pueden justificar la adopción.

En ese caso, la comparación necesita considerar la arquitectura de seguridad existente, la experiencia operacional del equipo y los requisitos de auditoría y diagnóstico.

En cualquier escenario, la migración necesita considerar compatibilidad con el kernel, configuración del CNI, balanceo, ruteo, integración con firewalls y procedimientos de recuperación.

Un cambio en el plano de datos de red afecta una parte fundamental de la infraestructura. Lo ideal es probar en un ambiente representativo, validar los caminos de tráfico y planear una estrategia de reversión.

## 9. La lección es mayor que el kube-proxy

Lo más interesante de este cambio no es simplemente trocar iptables por eBPF.

Es percibir que componentes considerados fundamentales en una arquitectura pueden ser sustituidos cuando entendemos exactamente qué problema resuelven y cuánto cuesta mantenerlos.

El kube-proxy cumplió, y todavía puede cumplir, un papel importante en Kubernetes. El modelo tradicional no fue un error. Fue una solución práctica para implementar una abstracción necesaria.

eBPF permite explorar otro punto de integración con el kernel y construir caminos de datos especializados. Cilium aprovecha esa posibilidad para combinar networking, seguridad y observabilidad en una implementación integrada.

Eso no vuelve obsoleta toda arquitectura anterior, ni transforma eBPF en una solución universal. Significa que ahora tenemos otras opciones, con diferentes costos y beneficios.

Mi conclusión es simple: no cambies el kube-proxy porque alguien prometió que eBPF es más rápido. Entiende el camino de los paquetes, identifica el cuello de botella, mide el comportamiento del cluster y solo entonces elige la arquitectura.

La mejor infraestructura no es necesariamente la que usa la tecnología más reciente. Es la que resuelve el problema real con el menor costo operacional, desempeño adecuado y complejidad que tu equipo consigue administrar.

Y queda una pregunta para llevar adelante: si conseguimos repensar una parte tan tradicional del networking de Kubernetes al aproximar la lógica de decisión al kernel, ¿qué otros cuellos de botella de la infraestructura estamos aceptando apenas porque siempre fueron implementados de esa manera?

## Referencias para profundizar

- [Cilium: documentación oficial](https://docs.cilium.io/)
- [Cilium: kube-proxy replacement](https://docs.cilium.io/en/stable/network/kubernetes/kubeproxy-free/)
- [Cilium: visión general de eBPF](https://docs.cilium.io/en/stable/bpf/)
- [Kubernetes: Services, Load Balancing y Networking](https://kubernetes.io/docs/concepts/services-networking/service/)
- [Linux Kernel: documentación de eBPF](https://docs.kernel.org/bpf/)
