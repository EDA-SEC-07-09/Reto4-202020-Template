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
    citibike["customers"] = gr.newGraph(datastructure='ADJ_LIST',
                                  directed=True,
                                  size=1000,
                                  comparefunction=compareStations)
    citibike["info1"] = m.newMap(numelements=14000,maptype="PROBING",comparefunction=compareStations)
    citibike["info2"] = m.newMap(numelements=14000,maptype="PROBING",comparefunction=compareStations)
    citibike["arrival"] = m.newMap(numelements=14000,maptype="PROBING",comparefunction=compareStations)
    citibike["exit"] = m.newMap(numelements=14000,maptype="PROBING",comparefunction=compareStations)
    citibike["year1"] = m.newMap(numelements=14000,maptype="PROBING",comparefunction=compareStations)
    citibike["year2"] = m.newMap(numelements=14000,maptype="PROBING",comparefunction=compareStations)
    return citibike

def addTrip(citibike, trip):
    origin = trip["start station id"]
    destination = trip["end station id"]
    year= 2018-int(trip["birth year"])
    duration = int(trip["tripduration"])
    suscriptor=trip["usertype"]
    addStation(citibike, origin)
    addStation(citibike, destination)
    addConnection(citibike, origin, destination, duration)
    addElements(citibike, trip, origin, destination)
    addViaje(citibike)
    addLlegadaSalida(citibike,origin,destination)
    addAños(citibike,origin,destination,year)
    if suscriptor=="Customer":
        addStation2(citibike, origin)
        addStation2(citibike, destination)
        addConnection2(citibike, origin, destination, year, suscriptor)
        

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

def addAños(citibike,st1,st2,years):
    if m.contains(citibike["year1"],st1):
        mb=m.get(citibike["year1"],st1)
        mb["value"]+=years
    else:
        m.put(citibike["year1"],st1,years)
    if m.contains(citibike["year2"],st2):
        mh=m.get(citibike["year2"],st2)
        mh["value"]+=years
    else:
        m.put(citibike["year2"],st2,years)
    return citibike
    
def addStation(citibike, stationid):
    """
    Adiciona una estación como un vertice del grafo
    """
    if not gr.containsVertex(citibike["graph"], stationid):
            gr.insertVertex(citibike["graph"], stationid)
    return citibike

def addStation2(citibike, stationid):
    if not gr.containsVertex(citibike["customers"], stationid):
        gr.insertVertex(citibike["customers"], stationid)
    return citibike

def incremental(promediada,division,suma):
    promedio_nuevo=((promediada*division)+suma)/(division+1)
    return promedio_nuevo

def addConnection2(citibike, origin, destination, years, subscriber):
    edge3 = gr.getEdge(citibike["customers"], origin, destination)
    if edge3 is None:
        gr.addEdge(citibike["customers"], origin, destination, years)
        edge3 = gr.getEdge(citibike["customers"], origin, destination)
        edge3["division"]=1
    else:
        diferencial=incremental(edge3["weight"],edge3["division"],years)
        edge3["division"]+=1
        edge3["weight"]=int(diferencial)
    return citibike

def addConnection(citibike, origin, destination, duration):
    """
    Adiciona un arco entre dos estaciones
    """
    edge = gr.getEdge(citibike["graph"], origin, destination)
    
    if edge is None:
        gr.addEdge(citibike["graph"], origin, destination, duration)
        edge = gr.getEdge(citibike["graph"], origin, destination)
        edge["division"]=1
    else:
        duracion=incremental(edge["weight"],edge["division"],duration)
        edge["division"]+=1
        edge["weight"]=duracion 
    return citibike

def addElements(citibike, trip, id1, id2):
    lista=lt.newList("ARRAY_LIST",cmpfunction=compareRoutes)
    lt.addLast(lista,trip)
    element=lt.getElement(lista,1)
    m.put(citibike["info1"],id1,element)
    m.put(citibike["info2"],id2,element)
    return citibike

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
    mapa1=citibike["info1"]
    mapa2=citibike["info2"]
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
        uno=m.get(mapa1,element)
        if uno!=None:
            a=uno["value"]
            if a["start station id"]==element:
                station=a["start station name"]
        dos=m.get(mapa2,element)
        if dos!=None:
            b=dos["value"]
            if b["end station id"]==element:
                station=b["end station name"]
        if EstacionesTop["Estación top de salida 1"]==None or arrival1<llegada: 
            if arrival2==None and arrival1==None:
                arrival1=llegada
            elif arrival2==None and arrival1!=None:
                arrival2=arrival1
                EstacionesTop["Estación top de salida 2"]=EstacionesTop["Estación top de salida 1"]
                arrival1=llegada
            elif arrival2!=None and arrival1!=None:
                if arrival2<arrival1:
                    arrival3=arrival2
                    EstacionesTop["Estación top de salida 3"]=EstacionesTop["Estación top de salida 2"]
                    arrival2=arrival1
                    EstacionesTop["Estación top de salida 2"]=EstacionesTop["Estación top de salida 1"]
                arrival1=llegada
            EstacionesTop["Estación top de salida 1"]=station
        elif EstacionesTop["Estación top de salida 2"]==None or arrival2<llegada:
            if arrival3==None and arrival2==None:
                arrival2=llegada
            elif arrival3==None and arrival2!=None:
                arrival3=arrival2
                EstacionesTop["Estación top de salida 3"]=EstacionesTop["Estación top de salida 2"]
                arrival2=llegada
            elif arrival3!=None and arrival2!=None:
                if arrival3<arrival2:
                    arrival3=arrival2
                    EstacionesTop["Estación top de salida 3"]=EstacionesTop["Estación top de salida 2"]
                arrival2=llegada
            EstacionesTop["Estación top de salida 2"]=station   
        elif EstacionesTop["Estación top de salida 3"]==None or arrival3<llegada:  
            arrival3=llegada
            EstacionesTop["Estación top de salida 3"]=station

        if EstacionesTop["Estación top de llegada 1"]==None or exits1<salida:
            if exits2==None and exits1==None:
                exits1=salida
            elif exits2==None and exits1!=None:
                exits2=exits1
                EstacionesTop["Estación top de llegada 2"]=EstacionesTop["Estación top de llegada 1"]
                exits1=salida
            elif exits2!=None and exits1!=None:
                if exits2<exits1:
                    exits3=exits2
                    EstacionesTop["Estación top de llegada 3"]=EstacionesTop["Estación top de llegada 2"]
                    exits2=exits1
                    EstacionesTop["Estación top de llegada 2"]=EstacionesTop["Estación top de llegada 1"]      
                exits1=salida
            EstacionesTop["Estación top de llegada 1"]=station
        elif EstacionesTop["Estación top de llegada 2"]==None or exits2<salida:
            if exits3==None and exits2==None:
                exits2=salida
            elif exits3==None and exits2!=None:
                exits3=exits2
                EstacionesTop["Estación top de llegada 3"]=EstacionesTop["Estación top de llegada 2"]
                exits2=salida
            elif exits3!=None and exits2!=None:
                if exits3<exits2:
                    exits3=exits2
                    EstacionesTop["Estación top de llegada 3"]=EstacionesTop["Estación top de llegada 2"]
                exits2=salida
            EstacionesTop["Estación top de llegada 2"]=station
        elif EstacionesTop["Estación top de llegada 3"]==None or exits3<salida:
            exits3=salida
            EstacionesTop["Estación top de llegada 3"]=station

        if EstacionesTop["Estación top menos utilizada 1"]==None or (less1>elementos):
            if less2==None and less1==None:
                less1=elementos
            elif less2==None and less1!=None:
                less2=less1
                EstacionesTop["Estación top menos utilizada 2"]=EstacionesTop["Estación top menos utilizada 1"]
                less1=elementos
            elif less2!=None and less1!=None:
                if less2>less1:
                    less3=less2
                    EstacionesTop["Estación top menos utilizada 3"]=EstacionesTop["Estación top menos utilizada 2"]
                    less2=less1
                    EstacionesTop["Estación top menos utilizada 2"]=EstacionesTop["Estación top menos utilizada 1"]   
                less1=elementos
            EstacionesTop["Estación top menos utilizada 1"]=station
        elif EstacionesTop["Estación top menos utilizada 2"]==None or (less2>elementos):
            if less3==None and less2==None:
                less2=elementos
            elif less3==None and less2!=None:
                less3=less2
                EstacionesTop["Estación top menos utilizada 3"]=EstacionesTop["Estación top menos utilizada 2"]
                less2=elementos
            elif less3!=None and less2!=None:
                if less3>less2:
                    less3=less2
                    EstacionesTop["Estación top menos utilizada 3"]=EstacionesTop["Estación top menos utilizada 2"]
                less2=elementos
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
        cont=0
        if lt.size(aux)==0:
            tamaño=1
        else:
            tamaño=lt.size(aux)
        if element!=StationId:
            while it.hasNext(iterator) and alarm==False and duracion<=int(MaxTime):
                cont+=1
                i=it.newIterator(aux)
                elem=it.next(iterator)
                duracion+=int(elem["weight"])
                while it.hasNext(i) and alarm==False:
                    vertex=it.next(i)
                    if vertex==elem["vertexB"]:
                        alarm=True   
                if alarm==False and duracion<=int(MaxTime):
                    lt.addLast(aux,elem["vertexB"]) 
                    lt.addLast(aux2,elem)
                else: 
                    if cont!=1:
                        tamfinal=lt.size(aux)
                        i=tamaño-cont+1
                        while i<=tamfinal:
                            lt.deleteElement(aux,i)
                            aux2=lt.newList("ARRAY_LIST",compareRoutes)
                            tamfinal=lt.size(aux)
        if duracion<=int(MaxTime) and alarm==False and lt.size(aux2)!=0:
            lt.addLast(lista,aux2)
    return lista

def RecomendadorRutas(citibike,e1,e2):
    mapa1=citibike["info1"]
    mapa2=citibike["info2"]
    mapa3=citibike["arrival"]
    mapa4=citibike["exit"]
    mapa5=citibike["year1"]
    mapa6=citibike["year2"]    
    arcos=gr.edges(citibike["graph"])
    recorrerarcos=it.newIterator(arcos)
    maxviajesllegada=0
    maxviajessalida=0
    route=lt.newList("ARRAY_LIST",compareRoutes)
    edadfinal1=None
    edadfinal2=None
    id1=None
    id2=None
    while it.hasNext(recorrerarcos):
        arc = it.next(recorrerarcos)
        get1=m.get(mapa3,arc["vertexA"])
        get2=m.get(mapa4,arc["vertexB"])
        get3=m.get(mapa5,arc["vertexA"])
        get4=m.get(mapa6,arc["vertexB"])
        viajesllegada=get1["value"]
        viajessalida=get2["value"]
        edad1=int(get3["value"]/viajesllegada)
        edad2=int(get4["value"]/viajessalida)
        if (e1<=edad1<=e2) and viajesllegada>maxviajesllegada:
            edadfinal1=edad1
            maxviajesllegada=viajesllegada
            id1=arc["vertexA"]
        if (e1<=edad2<=e2) and viajessalida>maxviajessalida:
            edadfinal2=edad2
            maxviajessalida=viajessalida
            id2=arc["vertexB"]
    if id1!=None and id2!=None:
        g1=m.get(mapa1,id1)
        g2=m.get(mapa2,id2)
        v1=g1["value"]
        v2=g2["value"]
        nombre1=v1["start station name"]
        nombre2=v2["end station name"]
        cadena1="Estación de inicio:"+nombre1
        lt.addLast(route,cadena1)
        cadena2="Estación de llegada:"+nombre2
        lt.addLast(route,cadena2)
        cadena3="Estaciones a recorrer:"
        lt.addLast(route,cadena3)
        dijkstra=djk.Dijkstra(citibike["graph"],id1)
        ruta=djk.pathTo(dijkstra,id2)
        recorrerruta=it.newIterator(ruta)
        i=0
        while it.hasNext(recorrerruta):
            i+=1
            segmento=it.next(recorrerruta)
            getter2=m.get(mapa2,segmento["vertexB"])
            value2=getter2["value"]
            station2=value2["end station name"]
            if segmento["vertexB"]!=id2 and i!=1:
                lt.addLast(route,station2)
            elif segmento["vertexB"]==id2 and i==1:
                lt.addLast(route,"Es un camino directo")
    else:
        lt.addLast(route,"No hay ruta")
    return route

 
def EstacionesParaPublicidad(citibike,e1,e2):
    mapa1=citibike["info1"]
    mapa2=citibike["info2"]
    arcos=gr.edges(citibike["customers"])
    stopiterator=it.newIterator(arcos)
    lista=lt.newList("ARRAY_LIST",compareRoutes)
    trip=0
    while it.hasNext(stopiterator):
        element = it.next(stopiterator)
        edad = element["weight"]
        viajes=element["division"]
        dicc={}
        if (e1<=edad<=e2)  and viajes>trip:
            lista=lt.newList("ARRAY_LIST",compareRoutes)
            trip=viajes
            a=m.get(mapa1,element["vertexA"])
            b=m.get(mapa2,element["vertexB"])
            c=a["value"]
            d=b["value"]
            st1=c["start station name"]
            st2=d["end station name"]
            dicc={st1:trip,st2:trip}
            lt.addLast(lista,dicc)
        elif (e1<=edad<=e2) and viajes==trip:
            a=m.get(mapa1,element["vertexA"])
            b=m.get(mapa2,element["vertexB"])
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