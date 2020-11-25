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
from DISClib.ADT import list as lt
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
servicefile = "201801-1-citibike-tripdata.csv"
initialStation = None
recursionLimit = 30000

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
    numedges = controller.totalConnections(cont)
    numvertex = controller.totalStations(cont)
    print("Numero de viajes:" + str(cont["viajes"]))
    print("Numero de vertices: " + str(numvertex))
    print("Numero de arcos: " + str(numedges))
    print("El limite de recursion actual: " + str(sys.getrecursionlimit()))
    sys.setrecursionlimit(recursionLimit)
    print("El limite de recursion se ajusta a: " + str(recursionLimit))


def optionThree():
    id1 = input("Ingrese una estación de origen:")
    id2 = input("Ingrese una estación de destino:")
    print(controller.CantidadCluster(cont, id1, id2))


def optionFour():
    estacion = input("Digite la estación desde la cual desea partir.\n")
    rango1 = int(input("Limite inferior del rango:\n"))
    rango2 = int(input("Limite superior del rango:\n"))
    todo = controller.requerimento2(cont, estacion, rango1, rango2)

    print("-----------------------------------")
    print("Cantidad de rutas:", lt.size(todo))
    print("-----------------------------------")
    for i in range(1, lt.size(todo) + 1):
        print("Ruta:", i)
        print("-----------------------------------")
        elemento = lt.getElement(todo, i)
        tiempo = 0
        for e in elemento:
            print(e["vertexA"], "------------>", e["vertexB"])
            tiempo += e["weight"]
        print("En:", round(tiempo, 3), "minutos")
        print("-----------------------------------")


def optionEight():
    lat1 = float(input("Latitud inicial:\n"))
    lon1 = float(input("Longitud inicial:\n"))
    lat2 = float(input("Latitud final:\n"))
    lon2 = float(input("Longitud final:\n"))
    todo = controller.requerimento6(
        cont,
        lat1,
        lon1,
        lat2,
        lon2,
    )
    estacion_inicial = todo[1]
    estacion_final = todo[2]
    print("----------------------------")
    print("Estacion Inicial", estacion_inicial, "Estación Final:", estacion_final)
    total = 0
    print("-----------------------------------")
    for i in range(1, lt.size(todo[0]) + 1):
        elemento = lt.getElement(todo[0], i)
        print(elemento["vertexA"] + "-------->" + elemento["vertexB"])
        total += elemento["weight"]
    print("-----------------------------------")
    print("En un tiempo de:", round(total / 60, 2), "minutos")
    print("-----------------------------------")


def optionTen():
    fecha = input("Digite la fecha en el sig formato DD-MM-YYYY\n")
    ide = input("Digite la ID de la bicicleta\n")
    todo = controller.bono8(cont, fecha="2018-01-03", ide="31256")
    print("---------------------------------")
    print("Ruta")
    print("---------------------------------")
    for i in range(1, lt.size(todo[2]) + 1):
        elemento = lt.getElement(todo[2], i)
        print(elemento["vertexA"] + "------>" + elemento["vertexB"])
    print("---------------------------------")
    print("Tiempo estacionada:", round(todo[1] / 60 ** 2, 4), "Horas")
    print("Tiempo usada", round(todo[0] / (60 ** 2), 4), "Horas")
    print("---------------------------------")


while True:
    printMenu()
    inputs = input("Seleccione una opción para continuar\n>")
    if int(inputs) == 1:
        print("\nInicializando....")
        cont = controller.init()

    elif int(inputs) == 2:
        executiontime = timeit.timeit(optionTwo, number=1)
        print("Tiempo de ejecución: " + str(executiontime))

    elif int(inputs) == 3:
        executiontime = timeit.timeit(optionThree, number=1)
        print("Tiempo de ejecución: " + str(executiontime))

    elif int(inputs) == 4:
        executiontime = timeit.timeit(optionFour, number=1)
        print("Tiempo de ejecución: " + str(executiontime))
    elif int(inputs) == 5:
        pass
    elif int(inputs) == 6:
        pass
    elif int(inputs) == 7:
        pass
    elif int(inputs) == 8:
        executiontime = timeit.timeit(optionEight, number=1)
        print("Tiempo de ejecución: " + str(executiontime))
    elif int(inputs) == 9:
        pass
    elif int(inputs) == 10:
        executiontime = timeit.timeit(optionTen, number=1)
        print("Tiempo de ejecución: " + str(executiontime))
    else:
        sys.exit(0)
sys.exit(0)