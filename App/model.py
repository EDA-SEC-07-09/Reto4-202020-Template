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
from math import radians, cos, sin, asin, sqrt
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
from DISClib.Algorithms.Sorting import mergesort as mge
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
    citibike = {"graph": None, "viajes": 0, "mapa_fecha": None, "mapa_lat_lon": None}
    citibike["graph"] = gr.newGraph(
        datastructure="ADJ_LIST",
        directed=True,
        size=1000,
        comparefunction=compareStations,
    )
    citibike["mapa_fecha"] = om.newMap("BST", compara_fechas)
    citibike["mapa_lat_lon"] = m.newMap(
        maptype="PROBING", comparefunction=compareStations
    )
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
            size=50,
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
                size=50,
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


def EXadd_lat_lon(mapa, llave, valor):
    existe = m.get(mapa, llave)
    if existe is None:
        m.put(mapa, llave, valor)


def add_lat_lo(citibike, trip):
    mapa = citibike["mapa_lat_lon"]

    estacion_inicio = trip["start station id"]
    latitud_inicio = trip["start station latitude"]
    longitud_inicio = trip["start station longitude"]
    llave = latitud_inicio + "," + longitud_inicio

    estacion_final = trip["end station id"]
    latitud_final = trip["end station latitude"]
    longitud_final = trip["end station longitude"]
    llavev2 = latitud_final + "," + longitud_final

    existe = m.get(mapa, "todos")

    if existe is None:
        lista_owo = lt.newList("ARRAY_LIST")
        a_ver = []
        if llave not in a_ver:
            a_ver.append(llave)
        if llavev2 not in a_ver:
            a_ver.append(llavev2)

        lt.addLast(lista_owo, a_ver)
        for i in a_ver:
            lt.addLast(lista_owo, i)
        m.put(mapa, "todos", lista_owo)
    else:
        existe = me.getValue(existe)
        lista = lt.getElement(existe, 1)
        lt.removeFirst(existe)
        no_estan = []
        if llave not in lista:
            lista.append(llave)
            no_estan.append(llave)
        if llavev2 not in lista:
            lista.append(llavev2)
            no_estan.append(llavev2)

        lt.addFirst(existe, lista)
        for i in no_estan:
            lt.addLast(existe, i)
    EXadd_lat_lon(mapa, llave, estacion_inicio)
    EXadd_lat_lon(mapa, llavev2, estacion_final)


def addViaje(citibike):
    citibike["viajes"] += 1
    return citibike["viajes"]


# ==============================
# Funciones de consulta
# ==============================
def ruta_interes_turistico(citibike, lat1, lon1, lat2, lon2):
    elegido_inicial = {"coincidencia": None, "cantidad": None}
    elegido_final = {"coincidencia": None, "cantidad": None}
    ruta_final = lt.newList("ARRAY_LIST")

    lista = me.getValue(m.get(citibike["mapa_lat_lon"], "todos"))
    lista = lt.getElement(lista, 1)
    for i in lista:
        a_ver = i.split(",")
        latitud = float(a_ver[0])
        longitud = float(a_ver[1])
        distancia_entre_puntos = distance(lat1, latitud, lon1, longitud)
        if elegido_inicial["coincidencia"] is None:
            elegido_inicial["coincidencia"] = i
            elegido_inicial["cantidad"] = distancia_entre_puntos
        else:
            if distancia_entre_puntos < elegido_inicial["cantidad"]:
                elegido_inicial["coincidencia"] = i
                elegido_inicial["cantidad"] = distancia_entre_puntos

    for i in lista:
        a_ver = i.split(",")
        latitud = float(a_ver[0])
        longitud = float(a_ver[1])
        distancia_entre_puntos = distance(lat2, latitud, lon2, longitud)
        if elegido_final["coincidencia"] is None:
            elegido_final["coincidencia"] = i
            elegido_final["cantidad"] = distancia_entre_puntos
        else:
            if distancia_entre_puntos < elegido_final["cantidad"]:
                elegido_final["coincidencia"] = i
                elegido_final["cantidad"] = distancia_entre_puntos
    vertice_inicio = me.getValue(
        m.get(citibike["mapa_lat_lon"], elegido_inicial["coincidencia"])
    )
    vertice_final = me.getValue(
        m.get(citibike["mapa_lat_lon"], elegido_final["coincidencia"])
    )
    ruta = djk.Dijkstra(citibike["graph"], vertice_inicio)
    ruta = djk.pathTo(ruta, vertice_final)
    for i in range(1, lt.size(ruta) + 1):
        owo = sta.pop(ruta)
        lt.addLast(ruta_final, owo)
    return ruta_final,vertice_inicio,vertice_final


def para_mantenimiento(citibike, fecha, ide):
    fecha = str_to_python_time(fecha)
    arbol = om.get(citibike["mapa_fecha"], fecha)
    arbol = me.getValue(arbol)
    mapa = m.get(arbol, ide)
    grafo = me.getValue(mapa)
    arcos = gr.edges(grafo)
    horas_organizadas = lt.newList("ARRAY_LIST")
    camino_organizado = lt.newList("ARRAY_LIST")
    for i in range(1, lt.size(arcos) + 1):
        elemento = lt.getElement(arcos, i)
        lt.addLast(horas_organizadas, elemento["inicio"])
    mge.mergesort(horas_organizadas, comparador_horas)
    for i in range(1, lt.size(horas_organizadas) + 1):
        hora = lt.getElement(horas_organizadas, i)
        for e in range(1, lt.size(arcos) + 1):
            arco = lt.getElement(arcos, e)
            if arco["inicio"] == hora:
                lt.addLast(camino_organizado, arco)
    for i in range(1, lt.size(camino_organizado) + 1):
        elemento = lt.getElement(camino_organizado, i)
        if i == 1:
            parqueada = conver_to_seconds(elemento["inicio"])
            usada = conver_to_seconds(elemento["final"]) - conver_to_seconds(
                elemento["inicio"]
            )
        else:

            usada += conver_to_seconds(elemento["final"]) - conver_to_seconds(
                elemento["inicio"]
            )

            parqueada += conver_to_seconds(elemento["inicio"]) - conver_to_seconds(
                (lt.getElement(camino_organizado, i - 1))["final"]
            )
        if i == lt.size(camino_organizado):
            resta = conver_to_seconds("23:59:59")
            parqueada += resta - conver_to_seconds(elemento["final"])

    return (usada, parqueada, camino_organizado)


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


def suma_fechas(fecha1, fecha2):
    suma = fecha2 + fecha1
    return suma


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


def str_to_python_time(string):
    xd = datetime.datetime.strptime(string, "%Y-%m-%d")
    xd = datetime.datetime.date(xd)
    return xd


def str_to_python_hora(hora):
    xd = datetime.datetime.strptime(hora, "%H:%M:%S")
    xd = datetime.datetime.time(xd)
    return xd


def distance(lat1, lat2, lon1, lon2):

    # The math module contains a function named
    # radians which converts from degrees to radians.
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2

    c = 2 * asin(sqrt(a))

    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371

    # calculate the result
    return c * r


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


def comparador_horas(hora1, hora2):
    if hora1 < hora2:
        return True
    else:
        return False


def compara_fechas(fecha1, fecha2):
    if fecha1 == fecha2:
        return 0
    elif fecha1 > fecha2:
        return 1
    else:
        return -1
