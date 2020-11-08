"""
 * Copyright 2020, Departamento de sistemas y Computación
 * Universidad de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * Contribución de:
 *
 * Dario Correal
 *
 """


import sys
import config
from App import controller
from DISClib.ADT import stack
import timeit
assert config

"""
La vista se encarga de la interacción con el usuario.
Presenta el menu de opciones  y  por cada seleccion
hace la solicitud al controlador para ejecutar la
operación seleccionada.
"""

# ___________________________________________________
#  Variables
# ___________________________________________________
servicefile ="201801-1-citibike-tripdata.csv"
initialStation = None
recursionLimit = 20000

# ___________________________________________________
#  Menu principal
# ___________________________________________________
def printMenu():
    print("\n")
    print("*******************************************")
    print("Bienvenido")
    print("0- Salir")
    print("1- Inicializar Analizador")
    print("2- Cargar información Analizador")
    print("3- REQ. 1: Cantidad de clusters de Viajes")
    print("4- REQ. 2: Ruta turística Circular ")
    print("5- REQ. 3: Estaciones críticas")
    print("6- REQ. 4: Ruta turística por resistencia")
    print("7- Req. 5: Recomendador de Rutas ")
    print("8- REQ. 6: Ruta de interés turístico ")
    print("9- REQ. 7: Identificación de Estaciones para Publicidad")
    print("10-REQ. 8: Identificación de Bicicletas para Mantenimiento")
    print("*******************************************")
"""
Menu principal
"""
def optionTwo():
    controller.loadTrips(cont)
    sys.setrecursionlimit(recursionLimit)
    print(cont)
while True:
    printMenu()
    inputs = input('Seleccione una opción para continuar\n>')
    if int(inputs[0]) == 1:
        print("\nInicializando....")
        cont=controller.init()
    elif int(inputs[0]) == 2:
        executiontime = timeit.timeit(optionTwo, number=1)
        print("Tiempo de ejecución: " + str(executiontime))

    elif int(inputs[0]) == 3:
        pass
    elif int(inputs[0]) == 4:
        pass
    elif int(inputs[0]) == 5:
        pass
    elif int(inputs[0]) == 6:
        pass
    elif int(inputs[0]) == 7:
        pass
    elif int(inputs[0]) == 8:
        pass
    elif int(inputs[0]) == 9:
        pass
    elif int(inputs[0]) == 10:
        pass
    else:
        sys.exit(0)
sys.exit(0)