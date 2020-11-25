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
from DISClib.ADT import list as lt
from DISClib.DataStructures import mapentry as me
from DISClib.ADT import orderedmap as om
from DISClib.ADT import map as m
from DISClib.ADT.graph import gr
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
    for trip in input_file:
        model.addtomap(citibike, trip)
        model.add_lat_lo(citibike, trip)
        model.addTrip(citibike, trip)
    return citibike


# ___________________________________________________
#  Funciones para consultas
# ___________________________________________________


def requerimento2(citibike, estacion, rango1, rango2):
    xd = model.revisar(citibike, estacion, rango1, rango2)
    final_v2 = lt.newList("ARRAY_LIST")
    final = []
    for i in range(1, lt.size(xd) + 1):
        revisa = []
        elemento = lt.getElement(xd, i)
        for e in range(1, lt.size(elemento) + 1):
            elemento_2 = lt.getElement(elemento, e)
            revisa.append(elemento_2)
        if revisa not in final:
            final.append(revisa)
    for i in final:
        lt.addLast(final_v2, i)
    return final_v2


def requerimento6(citibike, lat1, lon1, lat2, lon2):
    xd = model.ruta_interes_turistico(citibike, lat1, lon1, lat2, lon2)
    return xd


def bono8(citibike, fecha, ide):
    xd = model.para_mantenimiento(citibike, fecha, ide)
    return xd


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
