# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 19:03:16 2024

@author: pablo
"""
###Utilizamos hashlib para calcular hashes utilizando el algoritmo SHA-256, y time para obtener la marca de tiempo actual.
import hashlib  # Biblioteca para funciones de hash
import time     # Biblioteca para funciones de tiempo

# Definición de la clase Block. Esta clase define la estructura de un bloque en la blockchain. Cada bloque tiene un índice,
#el hash del bloque anterior, una marca de tiempo, datos, y su propio hash.
class Block:
    def __init__(self, index, previous_hash, timestamp, data, hash):
        self.index = index                  # Índice del bloque en la cadena
        self.previous_hash = previous_hash  # Hash del bloque anterior
        self.timestamp = timestamp          # Marca de tiempo de creación del bloque
        self.data = data                    # Datos contenidos en el bloque
        self.hash = hash                    # Hash del bloque actual

# Función para calcular el hash de un bloque. Esta función toma los atributos de un bloque y los concatena en una cadena. 
#Luego, calcula y retorna el hash SHA-256 de esta cadena.

def calculate_hash(index, previous_hash, timestamp, data):
    value = str(index) + str(previous_hash) + str(timestamp) + str(data)  # Concatenar los valores del bloque
    return hashlib.sha256(value.encode('utf-8')).hexdigest()  # Calcular y retornar el hash SHA-256

# Función para crear el bloque génesis (primer bloque de la cadena). 
#Esta función crea el bloque génesis, el primer bloque de la cadena. Tiene un índice de 0, un hash previo de "0",
# una marca de tiempo actual y datos estáticos ("Genesis Block").
def create_genesis_block():
    return Block(0, "0", int(time.time()), "Genesis Block", calculate_hash(0, "0", int(time.time()), "Genesis Block"))

# Función para crear un nuevo bloque basado en el bloque anterior. Esta función crea un nuevo bloque basado en el bloque anterior,
#generando un nuevo índice, una marca de tiempo actual, el hash del bloque anterior y calculando el hash del nuevo bloque.
def create_new_block(previous_block, data):
    index = previous_block.index + 1  # Incrementar el índice
    timestamp = int(time.time())      # Obtener la marca de tiempo actual
    previous_hash = previous_block.hash  # Obtener el hash del bloque anterior
    hash = calculate_hash(index, previous_hash, timestamp, data)  # Calcular el hash del nuevo bloque
    return Block(index, previous_hash, timestamp, data, hash)  # Crear y retornar el nuevo bloque

# Función para verificar la integridad de la cadena de bloques. Esta función verifica la integridad de la cadena de bloques. 
#Recorre la cadena y verifica que el hash de cada bloque sea correcto y que el hash del bloque anterior coincida con el 
#almacenado en el bloque actual.
def is_chain_valid(blockchain):
    for i in range(1, len(blockchain)):  # Iterar a través de la cadena de bloques
        current_block = blockchain[i]
        previous_block = blockchain[i - 1]

        # Verificar si el hash del bloque actual es correcto
        if current_block.hash != calculate_hash(current_block.index, current_block.previous_hash, current_block.timestamp, current_block.data):
            return False
        # Verificar si el hash del bloque anterior coincide
        if current_block.previous_hash != previous_block.hash:
            return False
    return True

# Crear la cadena de bloques y agregar el bloque génesis
blockchain = [create_genesis_block()]

# Agregar algunos bloques a la cadena con datos de ejemplo
blockchain.append(create_new_block(blockchain[-1], "Segundo bloque de datos"))
blockchain.append(create_new_block(blockchain[-1], "Tercer bloque de datos"))
blockchain.append(create_new_block(blockchain[-1], "Cuarto bloque de datos"))

# Verificar la integridad de la cadena de bloques
print("Blockchain válida:", is_chain_valid(blockchain))

# Imprimir la información de cada bloque en la cadena de bloques
for block in blockchain:
    print(f"Índice: {block.index}")
    print(f"Hash previo: {block.previous_hash}")
    print(f"Hash: {block.hash}")
    print(f"Datos: {block.data}")
    print(f"Timestamp: {block.timestamp}")
    print("----------")

#Aquí, creamos la cadena de bloques comenzando con el bloque génesis, y luego añadimos algunos bloques adicionales.
# Verificamos la integridad de la cadena y luego imprimimos la información de cada bloque.

#Este ejemplo ilustra los conceptos básicos de cómo se forma y se valida una blockchain. 
#Es una versión simplificada y no incluye características avanzadas como la prueba de trabajo (Proof of Work), 
#la minería de bloques, o la descentralización real entre múltiples nodos.