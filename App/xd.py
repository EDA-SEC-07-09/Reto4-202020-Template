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
import config
from DISClib.ADT.graph import gr
from DISClib.ADT import map as m
from DISClib.ADT import list as lt
from DISClib.ADT import stack as sta
from DISClib.ADT import orderedmap as om
from DISClib.DataStructures import listiterator as it
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dfs as dfs
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Graphs import dijsktra as djk
import datetime
from DISClib.Utils import error as error

assert config

"""
En este archivo definimos los TADs que vamos a usar y las operaciones
de creacion y consulta sobre las estructuras de datos.
"""

# -----------------------------------------------------
#                       API
# -----------------------------------------------------

# Funciones para agregar informacion al grafo
def newAnalyzer():
    citibike = {"graph": None, "viajes": 0, "mapa_fecha": None}
    citibike["graph"] = gr.newGraph(
        datastructure="ADJ_LIST",
        directed=True,
        size=1000,
        comparefunction=compareStations,
    )
    citibike["mapa_fecha"] = om.newMap("BST", compara_fechas)
    return citibike


def addTrip(citibike, trip):
    origin = trip["start station id"]
    destination = trip["end station id"]
    duration = int(trip["tripduration"])
    addStation(citibike, origin)
    addStation(citibike, destination)
    addConnection(citibike, origin, destination, duration)
    addViaje(citibike)


def addStation(citibike, stationid):
    """
    Adiciona una estación como un vertice del grafo
    """
    if not gr.containsVertex(citibike["graph"], stationid):
        gr.insertVertex(citibike["graph"], stationid)
    return citibike


def addtomap(citibike, trip):
    fecha = trip["starttime"]
    fecha = transformador_fecha(fecha, 1)
    existe = om.get(citibike["mapa_fecha"], fecha)
    if existe is None:
        mapa = structure_map()
        llave = trip["bikeid"]
        ruta = gr.newGraph(
            datastructure="ADJ_LIST",
            directed=True,
            size=1000,
            comparefunction=compareStations,
        )
        addTripV2(ruta, trip)
        m.put(mapa, llave, ruta)
        om.put(citibike["mapa_fecha"], fecha, mapa)
    else:
        llave = trip["bikeid"]
        existe = me.getValue(existe)
        existev2 = m.get(existe, llave)
        if existev2 is None:
            ruta = gr.newGraph(
                datastructure="ADJ_LIST",
                directed=True,
                size=1000,
                comparefunction=compareStations,
            )
            addTripV2(ruta, trip)
            m.put(existe, llave, ruta)
        else:
            grafo = me.getValue(existev2)
            addTripV2(grafo, trip)


def addTripV2(citibike, trip):
    origin = trip["start station id"]
    destination = trip["end station id"]
    duration = int(trip["tripduration"])
    hora_inicio = transformador_fecha(trip["starttime"], 2)
    hora_final = transformador_fecha(trip["stoptime"], 2)
    addStationV2(citibike, origin)
    addStationV2(citibike, destination)
    addConnectionV2(citibike, origin, destination, duration, hora_inicio, hora_final)


def addStationV2(grafo, vertex):
    if not gr.containsVertex(grafo, vertex):
        gr.insertVertex(grafo, vertex)
    return grafo


def addConnectionV2(grafo, origin, destination, weight, hora_inicio, hora_final):
    edge = gr.getEdge(grafo, origin, destination)
    if edge is None:
        gr.addEdge(grafo, origin, destination, weight)
        edge = gr.getEdge(grafo, origin, destination)
        edge["division"] = 1
        edge["inicio"] = hora_inicio
        edge["final"] = hora_final
    else:
        duracion = incremental(edge["weight"], edge["division"], weight)
        inicio = incrementalV2(edge["inicio"], edge["division"], hora_inicio)
        final = incrementalV2(edge["final"], edge["division"], hora_final)

        edge["division"] += 1
        edge["weight"] = duracion
        edge["final"] = final
        edge["inicio"] = inicio
    return grafo


def addConnection(citibike, origin, destination, duration):
    """
    Adiciona un arco entre dos estaciones
    """
    edge = gr.getEdge(citibike["graph"], origin, destination)
    if edge is None:
        gr.addEdge(citibike["graph"], origin, destination, duration)
        edge = gr.getEdge(citibike["graph"], origin, destination)
        edge["division"] = 1
    else:
        duracion = incremental(edge["weight"], edge["division"], duration)
        edge["division"] += 1
        edge["weight"] = duracion
    return citibike


def addViaje(citibike):
    citibike["viajes"] += 1
    return citibike["viajes"]


# ==============================
# Funciones de consulta
# ==============================
def CantidadCluster(citibike, station1, station2):
    clusteres = {
        "No. de clusteres:": None,
        "Las estaciones están en el mismo cluster:": None,
    }
    sc = scc.KosarajuSCC(citibike["graph"])
    cant = scc.connectedComponents(sc)
    cond = sameCC(sc, station1, station2)
    clusteres["No. de clusteres:"] = cant
    clusteres["Las estaciones están en el mismo cluster:"] = cond
    return clusteres


def sameCC(sc, station1, station2):
    return scc.stronglyConnected(sc, station1, station2)


def totalConnections(citibike):
    """
    Retorna el total arcos del grafo
    """
    return gr.numEdges(citibike["graph"])


def totalStations(citibike):
    """
    Retorna el total de estaciones (vertices) del grafo
    """
    return gr.numVertices(citibike["graph"])


def revisar(citibike, estacion, rango1, rango2):
    revisar = scc.KosarajuSCC(citibike["graph"])
    estacion_base = m.get(revisar["idscc"], estacion)
    valores = m.keySet(revisar["idscc"])
    elegidos = lt.newList("ARRAY_LIST")
    for i in range(1, lt.size(valores) + 1):
        llave = lt.getElement(valores, i)
        if me.getValue(m.get(revisar["idscc"], llave)) == me.getValue(estacion_base):
            lt.addLast(elegidos, llave)
    grafo_SCC = {
        "graph": gr.newGraph(
            datastructure="ADJ_LIST",
            directed=True,
            size=lt.size(elegidos) + 1,
            comparefunction=compareStations,
        )
    }
    for i in range(1, lt.size(elegidos) + 1):
        vertex = lt.getElement(elegidos, i)
        adyacentes = gr.adjacentEdges(citibike["graph"], vertex)
        for o in range(lt.size(adyacentes) + 1):
            arco_adyacente = lt.getElement(adyacentes, o)
            for e in range(1, lt.size(elegidos) + 1):
                comprueba = lt.getElement(elegidos, e)
                if arco_adyacente["vertexB"] == comprueba:
                    addStation(grafo_SCC, vertex)
                    addStation(grafo_SCC, comprueba)
                    addConnection(
                        grafo_SCC, vertex, comprueba, arco_adyacente["weight"]
                    )

    search = dfs.DepthFirstSearch(grafo_SCC["graph"], estacion)
    anexo = djk.Dijkstra(grafo_SCC["graph"], estacion)
    arcos = gr.edges(grafo_SCC["graph"])
    elegidos = []

    caminos_candidatos_DFS = lt.newList("ARRAY_LIST")
    caminos_candidatos_DJK = lt.newList("ARRAY_LIST")
    for i in range(1, lt.size(arcos) + 1):
        arco = lt.getElement(arcos, i)
        if arco["vertexB"] == estacion:
            elegidos.append(arco["vertexA"])

    for i in elegidos:
        caminoDFS_pila = dfs.pathTo(search, i)
        caminoDFS_lista = lt.newList("ARRAY_LIST")
        caminoDJK_pila = djk.pathTo(anexo, i)
        caminoDJK_list = lt.newList("ARRAY_LIST")
        caminoDJK_final = lt.newList("ARRAY_LIST")

        for e in range(1, lt.size(caminoDJK_pila) + 1):
            add = sta.pop(caminoDJK_pila)
            lt.addLast(caminoDJK_list, add)
        for e in range(1, lt.size(caminoDFS_pila) + 1):
            add = sta.pop(caminoDFS_pila)
            lt.addLast(caminoDFS_lista, add)

        if lt.size(caminoDJK_list) > 0:
            for e in range(1, lt.size(caminoDJK_list) + 1):
                elemento = lt.getElement(caminoDJK_list, e)
                if e == 1:
                    lt.addLast(caminoDJK_final, elemento["vertexA"])
                    lt.addLast(caminoDJK_final, elemento["vertexB"])
                else:
                    lt.addLast(caminoDJK_final, elemento["vertexB"])

        if lt.size(caminoDJK_final) > 0:
            lt.addLast(caminoDJK_final, estacion)
            lt.addLast(caminos_candidatos_DJK, caminoDJK_final)

        if lt.size(caminoDFS_lista) > 0:
            lt.addLast(caminoDFS_lista, estacion)
            lt.addLast(caminos_candidatos_DFS, caminoDFS_lista)
    caminos_finales_pesos = lt.newList("ARRAY_LIST")

    caminos_candidatos(
        caminos_candidatos_DJK, grafo_SCC, caminos_finales_pesos, rango1, rango2
    )

    caminos_candidatos(
        caminos_candidatos_DFS, grafo_SCC, caminos_finales_pesos, rango1, rango2
    )
    return caminos_finales_pesos


# ==============================
# Funciones Helper
# ==============================
def conver_to_seconds(hora):
    if type(hora) == "datetime.time":
        convertido = datetime.time.strftime(hora, "%H:%M:%S.%f")
    else:
        convertido = str(hora)
    convertido = convertido.split(":")

    convertido[0] = int(convertido[0]) * 3600
    convertido[1] = int(convertido[1]) * 60
    convertido[2] = float(convertido[2])

    suma = 0
    for i in convertido:
        suma += i
    return suma


def transformador_fecha(fecha, num):
    fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S.%f")
    if num == 1:
        xd = fecha.date()
    else:
        xd = fecha.time()
    return xd


def incremental(promediada, division, suma):
    promedio_nuevo = ((promediada * division) + suma) / (division + 1)
    return promedio_nuevo


def incrementalV2(promediada, division, suma):
    promediada = conver_to_seconds(promediada)
    suma = conver_to_seconds(suma)
    promedio_nuevo = ((promediada * division) + suma) / (division + 1)
    promedio_nuevo = datetime.timedelta(seconds=promedio_nuevo)
    return promedio_nuevo


def caminos_candidatos(caminox, grafo, final, rango1, rango2):
    for i in range(1, lt.size(caminox) + 1):
        camino = lt.getElement(caminox, i)
        CAM = lt.newList("ARRAY_LIST")
        total = 0
        for e in range(1, lt.size(camino) + 1):
            if e > 1:
                verticeA = lt.getElement(camino, e - 1)
                verticeB = lt.getElement(camino, e)
                juntos = gr.getEdge(grafo["graph"], verticeA, verticeB)
                if lt.size(CAM) == 0:
                    juntos["weight"] /= 60
                    juntos["weight"] += 40
                else:
                    juntos["weight"] /= 60
                    juntos["weight"] += 20
                total += juntos["weight"]
                lt.addLast(CAM, juntos)
        if total >= rango1 and total <= rango2:
            lt.addLast(final, CAM)


def structure_map():
    mapa = m.newMap(maptype="CHAINING", comparefunction=compareStations)
    return mapa


# ==============================
# Funciones de Comparacion
# ==============================
def compareStations(estacion1, estacion2):
    estacion2 = me.getKey(estacion2)
    if estacion1 == estacion2:
        return 0
    elif estacion1 > estacion2:
        return 1
    else:
        return -1


def compara_fechas(fecha1, fecha2):
    if fecha1 == fecha2:
        return 0
    elif fecha1 > fecha2:
        return 1
    else:
        return -1


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

import config as cf
import os
from App import model
import csv

"""
El controlador se encarga de mediar entre la vista y el modelo.
Existen algunas operaciones en las que se necesita invocar
el modelo varias veces o integrar varias de las respuestas
del modelo en una sola respuesta.  Esta responsabilidad
recae sobre el controlador.
"""

# ___________________________________________________
#  Inicializacion del catalogo
# ___________________________________________________


def init():
    """
    Llama la funcion de inicializacion  del modelo.
    """
    # analyzer es utilizado para interactuar con el modelo
    analyzer = model.newAnalyzer()
    return analyzer


# ___________________________________________________
#  Funciones para la carga de datos y almacenamiento
#  de datos en los modelos
# ___________________________________________________


def loadTrips(citibike):
    for filename in os.listdir(cf.data_dir):
        if filename.endswith(".csv"):
            print("Cargando archivo: " + filename)
            loadFile(citibike, filename)
    return citibike


def loadFile(citibike, tripfile):
    tripfile = cf.data_dir + tripfile
    input_file = csv.DictReader(open(tripfile, encoding="utf-8"), delimiter=",")
    a_ver = input("¿Desea que se carguen las dependencias del Bono?,Si o No\n")
    for trip in input_file:
        if a_ver == "Si":
            model.addTrip(citibike, trip)
            model.addtomap(citibike, trip)
        elif a_ver == "No":
            model.addTrip(citibike, trip)
    return citibike


# ___________________________________________________
#  Funciones para consultas
# ___________________________________________________


def totalStations(citibike):
    """
    Total de paradas de bicicleta
    """
    return model.totalStations(citibike)


def totalConnections(citibike):
    """
    Total de enlaces entre las paradas
    """
    return model.totalConnections(citibike)


def CantidadCluster(citibike, id1, id2):
    return model.CantidadCluster(citibike, id1, id2)


grafo_vacio = init()
loadTrips(grafo_vacio)

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


while True:
    printMenu()
    inputs = input("Seleccione una opción para continuar\n>")
    if int(inputs[0]) == 1:
        print("\nInicializando....")
        cont = controller.init()

    elif int(inputs[0]) == 2:
        executiontime = timeit.timeit(optionTwo, number=1)
        print("Tiempo de ejecución: " + str(executiontime))

    elif int(inputs[0]) == 3:
        executiontime = timeit.timeit(optionThree, number=1)
        print("Tiempo de ejecución: " + str(executiontime))

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
