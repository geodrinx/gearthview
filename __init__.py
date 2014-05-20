# -*- coding: utf-8 -*-
"""
/***************************************************************************
 gearthview
                                 A QGIS plugin
 GEarth View
                             -------------------
        begin                : 2012-12-14
        copyright            : (C) 2012 by geodrinx
        email                : geodrinx@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


def name():
    return "GEarthView"


def description():
    return "GEarth View"


def version():
    return "Version 1.0.5"


def icon():
    return "icon.png"


def qgisMinimumVersion():
    return "2.0"

def author():
    return "geodrinx"

def email():
    return "geodrinx@gmail.com"

def classFactory(iface):
    # load gearthview class from file gearthview
    from gearthview import gearthview
    return gearthview(iface)
