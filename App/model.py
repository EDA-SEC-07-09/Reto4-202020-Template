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
    citibike["customers"] = gr.newGraph(
        datastructure="ADJ_LIST",
        directed=True,
        size=1000,
        comparefunction=compareStations,
    )
    citibike["info1"] = m.newMap(
        numelements=14000, maptype="PROBING", comparefunction=compareStations
    )
    citibike["info2"] = m.newMap(
        numelements=14000, maptype="PROBING", comparefunction=compareStations
    )
    citibike["arrival"] = m.newMap(
        numelements=14000, maptype="PROBING", comparefunction=compareStations
    )
    citibike["exit"] = m.newMap(
        numelements=14000, maptype="PROBING", comparefunction=compareStations
    )
    citibike["year1"] = m.newMap(
        numelements=14000, maptype="PROBING", comparefunction=compareStations
    )
    citibike["year2"] = m.newMap(
        numelements=14000, maptype="PROBING", comparefunction=compareStations
    )
    return citibike


def addTrip(citibike, trip):
    origin = trip["start station id"]
    destination = trip["end station id"]
    year = 2018 - int(trip["birth year"])
    duration = int(trip["tripduration"])
    suscriptor = trip["usertype"]
    addStation(citibike, origin)
    addStation(citibike, destination)
    addConnection(citibike, origin, destination, duration)
    addElements(citibike, trip, origin, destination)
    addViaje(citibike)
    addLlegadaSalida(citibike, origin, destination)
    addAños(citibike, origin, destination, year)
    if suscriptor == "Customer":
        addStation2(citibike, origin)
        addStation2(citibike, destination)
        addConnection2(citibike, origin, destination, year, suscriptor)


def addLlegadaSalida(citibike, st1, st2):
    if m.contains(citibike["arrival"], st1):
        ma = m.get(citibike["arrival"], st1)
        ma["value"] += 1
    else:
        m.put(citibike["arrival"], st1, 1)
    if m.contains(citibike["exit"], st2):
        ms = m.get(citibike["exit"], st2)
        ms["value"] += 1
    else:
        m.put(citibike["exit"], st2, 1)
    return citibike


def addAños(citibike, st1, st2, years):
    if m.contains(citibike["year1"], st1):
        mb = m.get(citibike["year1"], st1)
        mb["value"] += years
    else:
        m.put(citibike["year1"], st1, years)
    if m.contains(citibike["year2"], st2):
        mh = m.get(citibike["year2"], st2)
        mh["value"] += years
    else:
        m.put(citibike["year2"], st2, years)
    return citibike


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


def addStation2(citibike, stationid):
    if not gr.containsVertex(citibike["customers"], stationid):
        gr.insertVertex(citibike["customers"], stationid)
    return citibike


def addConnection2(citibike, origin, destination, years, subscriber):
    edge3 = gr.getEdge(citibike["customers"], origin, destination)
    if edge3 is None:
        gr.addEdge(citibike["customers"], origin, destination, years)
        edge3 = gr.getEdge(citibike["customers"], origin, destination)
        edge3["division"] = 1
    else:
        diferencial = incremental(edge3["weight"], edge3["division"], years)
        edge3["division"] += 1
        edge3["weight"] = int(diferencial)
    return citibike


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


def addElements(citibike, trip, id1, id2):
    lista = lt.newList("ARRAY_LIST", cmpfunction=compareRoutes)
    lt.addLast(lista, trip)
    element = lt.getElement(lista, 1)
    m.put(citibike["info1"], id1, element)
    m.put(citibike["info2"], id2, element)
    return citibike


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
    return ruta_final, vertice_inicio, vertice_final


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
        corre_hora = str(elemento["inicio"])
        corre_hora = datetime.datetime.strptime(corre_hora, "%H:%M:%S.%f")
        corre_hora = datetime.datetime.time(corre_hora)
        lt.addLast(horas_organizadas, corre_hora)
    mge.mergesort(horas_organizadas, comparador_horas)

    for i in range(1, lt.size(horas_organizadas) + 1):
        hora = lt.getElement(horas_organizadas, i)
        for e in range(1, lt.size(arcos) + 1):
            arco = lt.getElement(arcos, e)
            corre_hora = str(arco["inicio"])
            corre_hora = datetime.datetime.strptime(corre_hora, "%H:%M:%S.%f")
            corre_hora = datetime.datetime.time(corre_hora)
            arco["inicio"] = corre_hora
            if corre_hora == hora:
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


def EstacionesCriticas(citibike):
    arrival1 = None
    exits1 = None
    less1 = None
    arrival2 = None
    exits2 = None
    less2 = None
    arrival3 = None
    exits3 = None
    less3 = None
    llegadas = citibike["arrival"]
    salidas = citibike["exit"]
    mapa1 = citibike["info1"]
    mapa2 = citibike["info2"]
    vertices = gr.vertices(citibike["graph"])
    stopiterator = it.newIterator(vertices)
    EstacionesTop = {
        "Estación top de llegada 1": None,
        "Estación top de llegada 2": None,
        "Estación top de llegada 3": None,
        "Estación top de salida 1": None,
        "Estación top de salida 2": None,
        "Estación top de salida 3": None,
        "Estación top menos utilizada 1": None,
        "Estación top menos utilizada 2": None,
        "Estación top menos utilizada 3": None,
    }
    while it.hasNext(stopiterator):
        element = it.next(stopiterator)
        rec1 = m.get(llegadas, element)
        rec2 = m.get(salidas, element)
        if rec1 != None:
            llegada = rec1["value"]
        else:
            llegada = 0

        if rec2 != None:
            salida = rec2["value"]
        else:
            salida = 0
        elementos = llegada + salida
        uno = m.get(mapa1, element)
        if uno != None:
            a = uno["value"]
            if a["start station id"] == element:
                station = a["start station name"]
        dos = m.get(mapa2, element)
        if dos != None:
            b = dos["value"]
            if b["end station id"] == element:
                station = b["end station name"]
        if EstacionesTop["Estación top de salida 1"] == None or arrival1 < llegada:
            if arrival2 == None and arrival1 == None:
                arrival1 = llegada
            elif arrival2 == None and arrival1 != None:
                arrival2 = arrival1
                EstacionesTop["Estación top de salida 2"] = EstacionesTop[
                    "Estación top de salida 1"
                ]
                arrival1 = llegada
            elif arrival2 != None and arrival1 != None:
                if arrival2 < arrival1:
                    arrival3 = arrival2
                    EstacionesTop["Estación top de salida 3"] = EstacionesTop[
                        "Estación top de salida 2"
                    ]
                    arrival2 = arrival1
                    EstacionesTop["Estación top de salida 2"] = EstacionesTop[
                        "Estación top de salida 1"
                    ]
                arrival1 = llegada
            EstacionesTop["Estación top de salida 1"] = station
        elif EstacionesTop["Estación top de salida 2"] == None or arrival2 < llegada:
            if arrival3 == None and arrival2 == None:
                arrival2 = llegada
            elif arrival3 == None and arrival2 != None:
                arrival3 = arrival2
                EstacionesTop["Estación top de salida 3"] = EstacionesTop[
                    "Estación top de salida 2"
                ]
                arrival2 = llegada
            elif arrival3 != None and arrival2 != None:
                if arrival3 < arrival2:
                    arrival3 = arrival2
                    EstacionesTop["Estación top de salida 3"] = EstacionesTop[
                        "Estación top de salida 2"
                    ]
                arrival2 = llegada
            EstacionesTop["Estación top de salida 2"] = station
        elif EstacionesTop["Estación top de salida 3"] == None or arrival3 < llegada:
            arrival3 = llegada
            EstacionesTop["Estación top de salida 3"] = station

        if EstacionesTop["Estación top de llegada 1"] == None or exits1 < salida:
            if exits2 == None and exits1 == None:
                exits1 = salida
            elif exits2 == None and exits1 != None:
                exits2 = exits1
                EstacionesTop["Estación top de llegada 2"] = EstacionesTop[
                    "Estación top de llegada 1"
                ]
                exits1 = salida
            elif exits2 != None and exits1 != None:
                if exits2 < exits1:
                    exits3 = exits2
                    EstacionesTop["Estación top de llegada 3"] = EstacionesTop[
                        "Estación top de llegada 2"
                    ]
                    exits2 = exits1
                    EstacionesTop["Estación top de llegada 2"] = EstacionesTop[
                        "Estación top de llegada 1"
                    ]
                exits1 = salida
            EstacionesTop["Estación top de llegada 1"] = station
        elif EstacionesTop["Estación top de llegada 2"] == None or exits2 < salida:
            if exits3 == None and exits2 == None:
                exits2 = salida
            elif exits3 == None and exits2 != None:
                exits3 = exits2
                EstacionesTop["Estación top de llegada 3"] = EstacionesTop[
                    "Estación top de llegada 2"
                ]
                exits2 = salida
            elif exits3 != None and exits2 != None:
                if exits3 < exits2:
                    exits3 = exits2
                    EstacionesTop["Estación top de llegada 3"] = EstacionesTop[
                        "Estación top de llegada 2"
                    ]
                exits2 = salida
            EstacionesTop["Estación top de llegada 2"] = station
        elif EstacionesTop["Estación top de llegada 3"] == None or exits3 < salida:
            exits3 = salida
            EstacionesTop["Estación top de llegada 3"] = station

        if EstacionesTop["Estación top menos utilizada 1"] == None or (
            less1 > elementos
        ):
            if less2 == None and less1 == None:
                less1 = elementos
            elif less2 == None and less1 != None:
                less2 = less1
                EstacionesTop["Estación top menos utilizada 2"] = EstacionesTop[
                    "Estación top menos utilizada 1"
                ]
                less1 = elementos
            elif less2 != None and less1 != None:
                if less2 > less1:
                    less3 = less2
                    EstacionesTop["Estación top menos utilizada 3"] = EstacionesTop[
                        "Estación top menos utilizada 2"
                    ]
                    less2 = less1
                    EstacionesTop["Estación top menos utilizada 2"] = EstacionesTop[
                        "Estación top menos utilizada 1"
                    ]
                less1 = elementos
            EstacionesTop["Estación top menos utilizada 1"] = station
        elif EstacionesTop["Estación top menos utilizada 2"] == None or (
            less2 > elementos
        ):
            if less3 == None and less2 == None:
                less2 = elementos
            elif less3 == None and less2 != None:
                less3 = less2
                EstacionesTop["Estación top menos utilizada 3"] = EstacionesTop[
                    "Estación top menos utilizada 2"
                ]
                less2 = elementos
            elif less3 != None and less2 != None:
                if less3 > less2:
                    less3 = less2
                    EstacionesTop["Estación top menos utilizada 3"] = EstacionesTop[
                        "Estación top menos utilizada 2"
                    ]
                less2 = elementos
            EstacionesTop["Estación top menos utilizada 2"] = station
        elif EstacionesTop["Estación top menos utilizada 3"] == None or (
            less3 > elementos
        ):
            less3 = elementos
            EstacionesTop["Estación top menos utilizada 3"] = station
    return EstacionesTop


def Resistencia(citibike, StationId, MaxTime):
    lista = lt.newList("ARRAY_LIST", compareRoutes)
    aux = lt.newList("ARRAY_LIST", compareRoutes)
    vertices = gr.vertices(citibike["graph"])
    stopiterator = it.newIterator(vertices)
    dijk = djk.Dijkstra(citibike["graph"], StationId)
    while it.hasNext(stopiterator):
        element = it.next(stopiterator)
        ruta = djk.pathTo(dijk, element)
        iterator = it.newIterator(ruta)
        duracion = 0
        alarm = False
        aux2 = lt.newList("ARRAY_LIST", compareRoutes)
        cont = 0
        if lt.size(aux) == 0:
            tamaño = 1
        else:
            tamaño = lt.size(aux)
        if element != StationId:
            while it.hasNext(iterator) and alarm == False and duracion <= int(MaxTime):
                cont += 1
                i = it.newIterator(aux)
                elem = it.next(iterator)
                duracion += int(elem["weight"])
                while it.hasNext(i) and alarm == False:
                    vertex = it.next(i)
                    if vertex == elem["vertexB"]:
                        alarm = True
                if alarm == False and duracion <= int(MaxTime):
                    lt.addLast(aux, elem["vertexB"])
                    lt.addLast(aux2, elem)
                else:
                    if cont != 1:
                        tamfinal = lt.size(aux)
                        i = tamaño - cont + 1
                        while i <= tamfinal:
                            lt.deleteElement(aux, i)
                            aux2 = lt.newList("ARRAY_LIST", compareRoutes)
                            tamfinal = lt.size(aux)
        if duracion <= int(MaxTime) and alarm == False and lt.size(aux2) != 0:
            lt.addLast(lista, aux2)
    return lista


def RecomendadorRutas(citibike, e1, e2):
    mapa1 = citibike["info1"]
    mapa2 = citibike["info2"]
    mapa3 = citibike["arrival"]
    mapa4 = citibike["exit"]
    mapa5 = citibike["year1"]
    mapa6 = citibike["year2"]
    arcos = gr.edges(citibike["graph"])
    recorrerarcos = it.newIterator(arcos)
    maxviajesllegada = 0
    maxviajessalida = 0
    route = lt.newList("ARRAY_LIST", compareRoutes)
    edadfinal1 = None
    edadfinal2 = None
    id1 = None
    id2 = None
    while it.hasNext(recorrerarcos):
        arc = it.next(recorrerarcos)
        get1 = m.get(mapa3, arc["vertexA"])
        get2 = m.get(mapa4, arc["vertexB"])
        get3 = m.get(mapa5, arc["vertexA"])
        get4 = m.get(mapa6, arc["vertexB"])
        viajesllegada = get1["value"]
        viajessalida = get2["value"]
        edad1 = int(get3["value"] / viajesllegada)
        edad2 = int(get4["value"] / viajessalida)
        if (e1 <= edad1 <= e2) and viajesllegada > maxviajesllegada:
            edadfinal1 = edad1
            maxviajesllegada = viajesllegada
            id1 = arc["vertexA"]
        if (e1 <= edad2 <= e2) and viajessalida > maxviajessalida:
            edadfinal2 = edad2
            maxviajessalida = viajessalida
            id2 = arc["vertexB"]
    if id1 != None and id2 != None:
        g1 = m.get(mapa1, id1)
        g2 = m.get(mapa2, id2)
        v1 = g1["value"]
        v2 = g2["value"]
        nombre1 = v1["start station name"]
        nombre2 = v2["end station name"]
        cadena1 = "Estación de inicio:" + nombre1
        lt.addLast(route, cadena1)
        cadena2 = "Estación de llegada:" + nombre2
        lt.addLast(route, cadena2)
        cadena3 = "Estaciones a recorrer:"
        lt.addLast(route, cadena3)
        dijkstra = djk.Dijkstra(citibike["graph"], id1)
        ruta = djk.pathTo(dijkstra, id2)
        recorrerruta = it.newIterator(ruta)
        i = 0
        while it.hasNext(recorrerruta):
            i += 1
            segmento = it.next(recorrerruta)
            getter2 = m.get(mapa2, segmento["vertexB"])
            value2 = getter2["value"]
            station2 = value2["end station name"]
            if segmento["vertexB"] != id2 and i != 1:
                lt.addLast(route, station2)
            elif segmento["vertexB"] == id2 and i == 1:
                lt.addLast(route, "Es un camino directo")
    else:
        lt.addLast(route, "No hay ruta")
    return route


def EstacionesParaPublicidad(citibike, e1, e2):
    mapa1 = citibike["info1"]
    mapa2 = citibike["info2"]
    arcos = gr.edges(citibike["customers"])
    stopiterator = it.newIterator(arcos)
    lista = lt.newList("ARRAY_LIST", compareRoutes)
    trip = 0
    while it.hasNext(stopiterator):
        element = it.next(stopiterator)
        edad = element["weight"]
        viajes = element["division"]
        dicc = {}
        if (e1 <= edad <= e2) and viajes > trip:
            lista = lt.newList("ARRAY_LIST", compareRoutes)
            trip = viajes
            a = m.get(mapa1, element["vertexA"])
            b = m.get(mapa2, element["vertexB"])
            c = a["value"]
            d = b["value"]
            st1 = c["start station name"]
            st2 = d["end station name"]
            dicc = {st1: trip, st2: trip}
            lt.addLast(lista, dicc)
        elif (e1 <= edad <= e2) and viajes == trip:
            a = m.get(mapa1, element["vertexA"])
            b = m.get(mapa2, element["vertexB"])
            c = a["value"]
            d = b["value"]
            st1 = c["start station name"]
            st2 = d["end station name"]
            dicc = {st1: trip, st2: trip}
            lt.addLast(lista, dicc)
    return lista


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
                    juntos["weight"] += 20
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


def compareRoutes(route1, route2):
    if route1 == route2:
        return 0
    elif route1 > route2:
        return 1
    else:
        return -1
