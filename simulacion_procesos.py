import simpy
import random
import statistics
import matplotlib.pyplot as plt

random.seed(123)

def proceso(ambiente, nombre, ram, cpu, velocidad_cpu, tiempos):
    
    tiempo_llegada = ambiente.now
    
    memoria_necesaria = random.randint(1, 10)
    
    yield ram.get(memoria_necesaria)
    
    instrucciones_totales = random.randint(1, 10)
    instrucciones_restantes = instrucciones_totales
    
    while instrucciones_restantes > 0:
        
        with cpu.request() as solicitud_cpu:
            yield solicitud_cpu
            
            instrucciones_ejecutar = min(velocidad_cpu, instrucciones_restantes)
            yield ambiente.timeout(1)
            instrucciones_restantes -= instrucciones_ejecutar
        
        if instrucciones_restantes <= 0:
            break
            
        decision = random.randint(1, 21)
        
        if decision == 1:
            yield ambiente.timeout(2)
    
    yield ram.put(memoria_necesaria)
    tiempo_total = ambiente.now - tiempo_llegada
    tiempos.append(tiempo_total)


def generador_procesos(ambiente, ram, cpu, velocidad_cpu, num_procesos, intervalo, tiempos):
    
    for i in range(num_procesos):
        ambiente.process(proceso(ambiente, f"P{i}", ram, cpu, velocidad_cpu, tiempos))
        
        tiempo_espera = random.expovariate(1.0 / intervalo)
        yield ambiente.timeout(tiempo_espera)


def simular(intervalo, memoria_total, velocidad_cpu, numero_cpu, numero_procesos):

    ambiente = simpy.Environment()
    
    ram = simpy.Container(ambiente, init=memoria_total, capacity=memoria_total)
    cpu = simpy.Resource(ambiente, capacity=numero_cpu)
    
    tiempos = []
    
    ambiente.process(generador_procesos(ambiente, ram, cpu, velocidad_cpu, numero_procesos, intervalo, tiempos))
    
    ambiente.run()
    
    if len(tiempos) > 0:
        promedio = statistics.mean(tiempos)
        if len(tiempos) > 1:
            desviacion = statistics.stdev(tiempos)
        else:
            desviacion = 0
        return promedio, desviacion
    else:
        return 0, 0


print("=" * 60)
print("Simulación de los procesos de un sistema operativo")
print("=" * 60)

intervalos = [10, 5, 1]
num_procesos_lista = [25, 50, 100, 150, 200]

print("\n" + "=" * 60)
print("Se configurara los recursos básicos")
print("RAM = 100, CPU = 3 instrucciones/unidad, 1 CPU")
print("=" * 60)

resultados_base = {}

for intervalo in intervalos:
    print(f"\n Intervalo de los procesos {intervalo}")
    tiempos_promedio = []
    
    for num_procesos in num_procesos_lista:
        promedio, desviacion = simular(intervalo, 100, 3, 1, num_procesos)
        tiempos_promedio.append(promedio)
        print(f"Procesos: {num_procesos:3d} | Tiempo promedio: {promedio:6.2f} | Desv. estándar: {desviacion:6.2f}")
    
    resultados_base[intervalo] = tiempos_promedio

print("\n" + "=" * 60)
print("Probando distintas estrategias")
print("=" * 60)


print("\n--- Estrategia mayor memoria: Memoria = 200")
resultados_mem200 = {}

for intervalo in intervalos:
    print(f"\nIntervalo = {intervalo}")
    tiempos_promedio = []
    for num_procesos in num_procesos_lista:
        promedio, desviacion = simular(intervalo, 200, 3, 1, num_procesos)
        tiempos_promedio.append(promedio)
        print(f"  Procesos: {num_procesos:3d} | Tiempo: {promedio:6.2f}")
    resultados_mem200[intervalo] = tiempos_promedio


print("\n--- Estrategia, CPU más rapido (6 instrucciones/unidad)")
resultados_cpurapido = {}

for intervalo in intervalos:
    print(f"\nIntervalo = {intervalo}")
    tiempos_promedio = []
    for num_procesos in num_procesos_lista:
        promedio, desviacion = simular(intervalo, 100, 6, 1, num_procesos)
        tiempos_promedio.append(promedio)
        print(f"  Procesos: {num_procesos:3d} | Tiempo: {promedio:6.2f}")
    resultados_cpurapido[intervalo] = tiempos_promedio


print("\n Estrategia 2 CPUs")
resultados_2cpus = {}

for intervalo in intervalos:
    print(f"\nIntervalo = {intervalo}")
    tiempos_promedio = []
    for num_procesos in num_procesos_lista:
        promedio, desviacion = simular(intervalo, 100, 3, 2, num_procesos)
        tiempos_promedio.append(promedio)
        print(f"  Procesos: {num_procesos:3d} | Tiempo: {promedio:6.2f}")
    resultados_2cpus[intervalo] = tiempos_promedio


print("\n" + "=" * 60)
print("Generar gráficasS")
print("=" * 60)

colores = ['blue', 'red', 'green', 'purple']
estrategias = ['Base', 'Memoria 200', 'CPU Rápido', '2 CPUs']


for i, intervalo in enumerate(intervalos):
    plt.figure(figsize=(10, 6))
    
    # Graficar cada estrategia
    plt.plot(num_procesos_lista, resultados_base[intervalo], 'o-', color=colores[0], label='Base', linewidth=2)
    plt.plot(num_procesos_lista, resultados_mem200[intervalo], 's-', color=colores[1], label='Memoria 200', linewidth=2)
    plt.plot(num_procesos_lista, resultados_cpurapido[intervalo], '^-', color=colores[2], label='CPU Rápido', linewidth=2)
    plt.plot(num_procesos_lista, resultados_2cpus[intervalo], 'd-', color=colores[3], label='2 CPU', linewidth=2)
    
    # Configurar la gráfica
    plt.xlabel('Número de Procesos', fontsize=12)
    plt.ylabel('Tiempo Promedio', fontsize=12)
    plt.title(f'Intervalo {intervalo})', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.xlim(0, 210)
    
    # Guardar la gráfica
    nombre_archivo = f'grafica_intervalo_{intervalo}.png'
    plt.savefig(nombre_archivo)
    print(f"Gráfica guardada: {nombre_archivo}")
    plt.show()


print("\n" + "=" * 60)
print("Análisis")
print("=" * 60)


print("\n--- Para carga ALTA (intervalo=1, 200 procesos) ---")
tiempo_base = resultados_base[1][4] 
tiempo_mem200 = resultados_mem200[1][4]
tiempo_cpurapido = resultados_cpurapido[1][4]
tiempo_2cpus = resultados_2cpus[1][4]

print(f"Base:        {tiempo_base:.2f}")
print(f"Memoria 200: {tiempo_mem200:.2f} (mejora: {(1 - tiempo_mem200/tiempo_base)*100:.1f}%)")
print(f"CPU Rápido:  {tiempo_cpurapido:.2f} (mejora: {(1 - tiempo_cpurapido/tiempo_base)*100:.1f}%)")
print(f"2 CPUs:      {tiempo_2cpus:.2f} (mejora: {(1 - tiempo_2cpus/tiempo_base)*100:.1f}%)")

mejoras = {
    'Memoria 200': (1 - tiempo_mem200/tiempo_base)*100,
    'CPU Rápido': (1 - tiempo_cpurapido/tiempo_base)*100,
    '2 CPUs': (1 - tiempo_2cpus/tiempo_base)*100
}
mejor = max(mejoras, key=mejoras.get)

print(f"\n La mejor estrategia es: {mejor} con mejora de {mejoras[mejor]:.1f}%")
