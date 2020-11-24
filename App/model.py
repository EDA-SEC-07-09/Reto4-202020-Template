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
from DISClib.DataStructures import listiterator as it
from DISClib.Algorithms.Graphs import scc
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Graphs import dijsktra as djk
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
    citibike={"graph":None, "viajes":0, "info":None}
    citibike["graph"] = gr.newGraph(datastructure='ADJ_LIST',
                                  directed=True,
                                  size=1000,
                                  comparefunction=compareStations)
    citibike["years"] = gr.newGraph(datastructure='ADJ_LIST',
                                  directed=True,
                                  size=1000,
                                  comparefunction=compareStations)
    citibike["info"] = m.newMap(numelements=14000,maptype="PROBING",comparefunction=compareStations)
    citibike["arrival"] = m.newMap(numelements=14000,maptype="PROBING",comparefunction=compareStations)
    citibike["exit"] = m.newMap(numelements=14000,maptype="PROBING",comparefunction=compareStations)
    return citibike

def addTrip(citibike, trip):
    origin = trip["start station id"]
    destination = trip["end station id"]
    year= 2018-int(trip["birth year"])
    duration = int(trip["tripduration"])
    suscriptor=trip["usertype"]
    addStation(citibike, origin)
    addStation(citibike, destination)
    addConnection(citibike, origin, destination, duration, year,suscriptor)
    addElements(citibike, trip, origin, destination)
    addViaje(citibike)
    addLlegadaSalida(citibike,origin,destination)

def addLlegadaSalida(citibike,st1,st2):
    if m.contains(citibike["arrival"],st1):
        ma=m.get(citibike["arrival"],st1)
        ma["value"]+=1
    else:
        m.put(citibike["arrival"],st1,1)
    if m.contains(citibike["exit"],st2):
        ms=m.get(citibike["exit"],st2)
        ms["value"]+=1
    else:
        m.put(citibike["exit"],st2,1)
    return citibike

def addStation(citibike, stationid):
    """
    Adiciona una estación como un vertice del grafo
    """
    if not gr.containsVertex(citibike["graph"], stationid):
            gr.insertVertex(citibike["graph"], stationid)
            gr.insertVertex(citibike["years"], stationid)
    return citibike

def incremental(promediada,division,suma):
    promedio_nuevo=((promediada*division)+suma)/(division+1)
    return promedio_nuevo

def addConnection(citibike, origin, destination, duration, years, subscriber):
    """
    Adiciona un arco entre dos estaciones
    """
    edge = gr.getEdge(citibike["graph"], origin, destination)
    edge2 = gr.getEdge(citibike["years"], origin, destination)
    if edge is None:
        gr.addEdge(citibike["graph"], origin, destination, duration)
        edge = gr.getEdge(citibike["graph"], origin, destination)
        edge["division"]=1
    else:
        duracion=incremental(edge["weight"],edge["division"],duration)
        edge["division"]+=1
        edge["weight"]=duracion

    if edge2 is None:
        gr.addEdge(citibike["years"], origin, destination, years)
        edge2 = gr.getEdge(citibike["years"], origin, destination)
        edge2["division"]=1
        edge2["suscripcion"]=subscriber
    else:
        diferencia=incremental(edge2["weight"],edge2["division"],years)
        edge2["division"]+=1
        edge2["weight"]=int(diferencia) 
    return citibike

def addElements(citibike, trip, id1, id2):
    lista=lt.newList("ARRAY_LIST",cmpfunction=compareRoutes)
    lt.addLast(lista,trip)
    element=lt.getElement(lista,1)
    m.put(citibike["info"],id1,element)
    m.put(citibike["info"],id2,element)
    return citibike["info"]

def addViaje(citibike):
    citibike["viajes"]+=1
    return citibike["viajes"]

# ==============================
# Funciones de consulta
# ==============================
def CantidadCluster(citibike,station1,station2):
    clusteres={"No. de clusteres:":None,"Las estaciones están en el mismo cluster:":None}
    sc = scc.KosarajuSCC(citibike["graph"])
    cant = scc.connectedComponents(sc)
    cond = sameCC(sc,station1,station2)
    clusteres["No. de clusteres:"]=cant
    clusteres["Las estaciones están en el mismo cluster:"]=cond
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

def EstacionesCriticas (citibike):
    arrival1=None
    exits1=None
    less1=None
    arrival2=None
    exits2=None
    less2=None
    arrival3=None
    exits3=None
    less3=None
    llegadas=citibike["arrival"]
    salidas=citibike["exit"]
    mapa=citibike["info"]
    vertices=gr.vertices(citibike["graph"])
    stopiterator=it.newIterator(vertices)
    EstacionesTop={"Estación top de llegada 1":None,
    "Estación top de llegada 2":None,
    "Estación top de llegada 3":None,
    "Estación top de salida 1":None,
    "Estación top de salida 2":None,
    "Estación top de salida 3":None,
    "Estación top menos utilizada 1":None,
    "Estación top menos utilizada 2":None,
    "Estación top menos utilizada 3":None}
    while it.hasNext(stopiterator):
        element = it.next(stopiterator)
        rec1=m.get(llegadas,element)
        rec2=m.get(salidas,element)
        if rec1!=None:
            llegada=rec1["value"]
        else:
            llegada=0
        if rec2!=None:
            salida=rec2["value"]
        else:
            salida=0
        elementos=llegada+salida
        uno=m.get(mapa,element)
        a=uno["value"]
        print (element,",",llegada)
        if a["start station id"]==element:
            station=a["start station name"]
        elif a["end station id"]==element:
            station=a["end station name"]

        if EstacionesTop["Estación top de llegada 1"]==None or arrival1<llegada:
            arrival2=arrival1
            arrival1=llegada
            EstacionesTop["Estación top de llegada 2"]=EstacionesTop["Estación top de llegada 1"]
            EstacionesTop["Estación top de llegada 1"]=station
        elif EstacionesTop["Estación top de llegada 2"]==None or arrival2<llegada:
            arrival3=arrival2
            arrival2=llegada
            EstacionesTop["Estación top de llegada 3"]=EstacionesTop["Estación top de llegada 2"]
            EstacionesTop["Estación top de llegada 2"]=station
        elif EstacionesTop["Estación top de llegada 3"]==None or arrival3<llegada:
            arrival3=llegada
            EstacionesTop["Estación top de llegada 3"]=station

        if EstacionesTop["Estación top de salida 1"]==None or exits1<salida:
            exits2=exits1
            exits1=salida
            EstacionesTop["Estación top de salida 2"]=EstacionesTop["Estación top de salida 1"]
            EstacionesTop["Estación top de salida 1"]=station
        elif EstacionesTop["Estación top de salida 2"]==None or exits2<salida:
            exits3=exits2
            exits2=salida
            EstacionesTop["Estación top de salida 3"]=EstacionesTop["Estación top de salida 2"]
            EstacionesTop["Estación top de salida 2"]=station
        elif EstacionesTop["Estación top de salida 3"]==None or exits3<salida:
            exits3=salida
            EstacionesTop["Estación top de salida 3"]=station

        if EstacionesTop["Estación top menos utilizada 1"]==None or (less1>elementos):
            less2=less1
            less1=elementos
            EstacionesTop["Estación top menos utilizada 2"]=EstacionesTop["Estación top menos utilizada 1"]
            EstacionesTop["Estación top menos utilizada 1"]=station
        elif EstacionesTop["Estación top menos utilizada 2"]==None or (less2>elementos):
            less3=less2
            less2=elementos
            EstacionesTop["Estación top menos utilizada 3"]=EstacionesTop["Estación top menos utilizada 2"]
            EstacionesTop["Estación top menos utilizada 2"]=station
        elif EstacionesTop["Estación top menos utilizada 3"]==None or (less3>elementos):
            less3=elementos
            EstacionesTop["Estación top menos utilizada 3"]=station
    return EstacionesTop

def Resistencia (citibike, StationId, MaxTime):
    lista=lt.newList("ARRAY_LIST",compareRoutes)
    aux=lt.newList("ARRAY_LIST",compareRoutes)
    vertices=gr.vertices(citibike["graph"])
    stopiterator=it.newIterator(vertices)
    dijk=djk.Dijkstra(citibike["graph"],StationId)
    while it.hasNext(stopiterator):
        element=it.next(stopiterator)
        ruta=djk.pathTo(dijk,element)
        iterator=it.newIterator(ruta)
        duracion=0
        alarm=False
        aux2=lt.newList("ARRAY_LIST",compareRoutes)
        while it.hasNext(iterator) and alarm==False and duracion<=int(MaxTime):
            i=it.newIterator(aux)
            elem=it.next(iterator)
            duracion+=int(elem["weight"])
            while it.hasNext(i) and alarm==False:
                vertex=it.next(i)
                if vertex==elem["vertexB"]:
                    alarm=True
            lt.addLast(aux,elem["vertexB"]) 
            lt.addLast(aux2,elem) 
        if duracion<=int(MaxTime):
            lt.addLast(lista,aux2)
    return lista
 
def EstacionesParaPublicidad(citibike,e1,e2):
    mapa=citibike["info"]
    arcos=gr.edges(citibike["years"])
    stopiterator=it.newIterator(arcos)
    lista=lt.newList("ARRAY_LIST",compareRoutes)
    trip=0
    while it.hasNext(stopiterator):
        element = it.next(stopiterator)
        edad = element["weight"]
        suscriptor = element["suscripcion"]
        viajes=element["division"]
        dicc={}
        if (e1<=edad<=e2) and suscriptor=="Customer" and viajes>trip:
            lista=lt.newList("ARRAY_LIST",compareRoutes)
            trip=viajes
            a=m.get(mapa,element["vertexA"])
            b=m.get(mapa,element["vertexB"])
            c=a["value"]
            d=b["value"]
            st1=c["start station name"]
            st2=d["end station name"]
            dicc={st1:trip,st2:trip}
            lt.addLast(lista,dicc)
        elif (e1<=edad<=e2) and suscriptor=="Customer" and viajes==trip:
            a=m.get(mapa,element["vertexA"])
            b=m.get(mapa,element["vertexB"])
            c=a["value"]
            d=b["value"]
            st1=c["start station name"]
            st2=d["end station name"]
            dicc={st1:trip,st2:trip}
            lt.addLast(lista,dicc)
    return lista
            
# ==============================
# Funciones Helper
# ==============================

# ==============================
# Funciones de Comparacion
# ==============================
def compareStations(estacion1,estacion2):
    estacion2=me.getKey(estacion2)
    if (estacion1 == estacion2):
        return 0
    elif (estacion1 > estacion2):
        return 1
    else:
        return -1

def compareRoutes(route1, route2):
    if (route1 == route2):
        return 0
    elif (route1 > route2):
        return 1
    else:
        return -1