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
    citibike={"graph":None, "viajes":0}
    citibike["graph"] = gr.newGraph(datastructure='ADJ_LIST',
                                  directed=True,
                                  size=1000,
                                  comparefunction=compareStations)
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

def incremental(promediada,division,suma):
    promedio_nuevo=((promediada*division)+suma)/(division+1)
    return promedio_nuevo

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
        duracion=incremental(edge["weight"],edge["division"],duration+edge["weight"])
        edge["division"]+=1
        edge["weight"]=duracion      
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

