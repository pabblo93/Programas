import hashlib
import time
import matplotlib.pyplot as plt

# Función para calcular el hash
def calculate_hash(index, previous_hash, timestamp, data, nonce):
    value = str(index) + str(previous_hash) + str(timestamp) + str(data) + str(nonce)
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

# Función para minar un bloque con prueba de trabajo
def mine_block(index, previous_hash, timestamp, data, difficulty):
    nonce = 0
    start_time = time.time()  # Inicia el cronómetro
    while True:
        hash = calculate_hash(index, previous_hash, timestamp, data, nonce)
        if hash.startswith('0' * difficulty):  # Verifica si el hash cumple la dificultad
            end_time = time.time()  # Termina el cronómetro
            return nonce, hash, end_time - start_time  # Retorna el tiempo de minería
        nonce += 1

# Configuración del experimento
index = 1
previous_hash = '0'
timestamp = int(time.time())
data = "Prueba de rendimiento de minería"
# Lista para guardar los tiempos de minería
difficulties = range(2, 12)  # Dificultades de 3 a 15
mining_times = []

# Bucle para minar bloques con diferentes dificultades
for difficulty in difficulties:
    print(f"Minando con dificultad: {difficulty}...")
    _, _, mining_time = mine_block(index, previous_hash, timestamp, data, difficulty)
    mining_times.append(mining_time)
    print(f"Tiempo de minería para dificultad {difficulty}: {mining_time:.2f} segundos")

# Crear la gráfica de tiempo vs dificultad
plt.figure(figsize=(10, 12))
plt.plot(difficulties, mining_times, marker='o', linestyle='-', color='b')
plt.title('Tiempo de Minería vs Dificultad')
plt.xlabel('Dificultad')
plt.ylabel('Tiempo de Minería (segundos)')
plt.grid(True)
plt.xticks(difficulties)
plt.savefig('output_plot.png')  # Guardar el gráfico en un archivo
plt.show()

# Comparación de dificultades reales
dificultad_real = {
    3: "Similar a Bitcoin en 2010",
    5: "Similar a Bitcoin en 2011",
    8: "Similar a Bitcoin en 2013 (inicio del uso de GPUs)",
    10: "Similar a Bitcoin en 2014 (inicio del uso de ASICs)",
    12: "Simulación a gran escala pero aún menor que Bitcoin actual",
    15: "Extremadamente difícil, comparable a niveles de dificultad actuales en blockchains reales"
}

print("\nComparación de dificultades reales:")
for dificultad, descripcion in dificultad_real.items():
    print(f"Dificultad {dificultad}: {descripcion}")

import sys

# Abrimos el archivo en modo escritura
with open('output.txt', 'w') as f:
    # Redirigimos stdout y stderr al archivo
    sys.stdout = f
    sys.stderr = f

    # Bucle para minar bloques con diferentes dificultades
    for difficulty in difficulties:
        print(f"Minando con dificultad: {difficulty}...")
        _, _, mining_time = mine_block(index, previous_hash, timestamp, data, difficulty)
        mining_times.append(mining_time)
        print(f"Tiempo de minería para dificultad {difficulty}: {mining_time:.2f} segundos")
    
    # Imprimir los valores de difficulties y mining_times en el archivo
    print("\nValores de difficulties:", list(difficulties))
    print("Valores de mining_times:", mining_times)

    # Volvemos a la salida estándar y errores normales
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__