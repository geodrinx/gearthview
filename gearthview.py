# -*- coding: utf-8 -*-
"""
/***************************************************************************
 gearthview
                                 A QGIS plugin
 GEarth View
                              -------------------
        begin                : 2013-06-22
        public version       : 2014-09-18
        
        copyright            : (C) 2013 2014 2015  by geodrinx
        email                : geodrinx@gmail.com
        
        history              :
                                 
          Plugin Creation      Roberto Angeletti
          
          menu and icons         Aldo Scorza

          QgsRemoteControl       Matthias Ludwig 
          
          import ext-libs        Enrico Ferreguti    
                                 Victor Olaya

 ***************************************************************************/ 
http://localhost:5558/gaeta
http://localhost:5558/cesium/Apps/CesiumViewer
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import qgis

import sys, itertools, os, glob, subprocess, zipfile, zlib, tempfile
import platform

from math import *
import datetime
import time
import codecs


#from http.server import HTTPServer, CGIHTTPRequestHandler

#import BaseHTTPServer, CGIHTTPServer

# https://pypi.python.org/pypi/qrcode
#import qrcode

# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from gearthviewdialog import gearthviewDialog

if QGis.QGIS_VERSION_INT < 10900:
    from osgeo import gdal
    from osgeo import gdalnumeric
    from osgeo import gdalconst


### important
import qtreactor.qt4reactor as qt4reactor
try:
    qt4reactor.install()
except qt4reactor.ReactorAlreadyInstalledError:
    print "still installed, doing nothing"
except AttributeError:
    pass
except:
    raise

## INSTALL qt4reactor before importing the twisted stuff
from twisted.internet import reactor
from twisted.web import server 
from twisted.web.static import File   

from osgeo import gdal, ogr, osr

###

#----------------------------------------------------------------------------
def P3dPoints_Write(self, adesso):	
        
				iface = qgis.utils.iface

				layer = iface.mapCanvas().currentLayer()

				if(layer == None):
				  return(-1)

				crs = layer.crs()

				nomeLayer = str(layer.name())
				filePath = str(layer.source())
				direct = os.path.dirname(filePath)
				out_folder = direct + '/_3dPointsExport'
				
				if not os.path.exists(out_folder):
				   os.mkdir( out_folder )

                             
				nomeGML = ("/GEKml_3dPoints.csv")         				


        #  Apro il file WKT in scrittura
        
				kml=open(out_folder + nomeGML, 'w')

				kml.write ("X,Y,Z,ID,Name,Istr\n")
				# kml.write ("X,Y,Z,ID\n")

				layer = self.iface.mapCanvas().currentLayer()
				
				if layer:
				  if layer.type() == layer.VectorLayer:				
				    
				    name = layer.source();
				    nomeLayer = layer.name()
				    nomeLay   = nomeLayer.replace(" ","_")

#--------------------------------------------------------
				    if (adesso == "GEKml_Polygons"):
            
#				      print "CREO UN MEMORY LAYER DI POLIGONI"

				      geomType = ("Polygon" + '?crs=%s') %(crs.authid())
				      DronePlan = "GEKml_Extrusions"            
				      memLay_Tin = QgsVectorLayer(geomType, DronePlan, 'memory') 
				      memprovider_Tin = memLay_Tin.dataProvider()

				      memLay_Tin.updateExtents()
				      memLay_Tin.commitChanges()
				      QgsMapLayerRegistry.instance().addMapLayer(memLay_Tin)
				      res = memprovider_Tin.addAttributes( [ QgsField("ID",  QVariant.Int), QgsField("height", QVariant.Double), QgsField("baseZ",  QVariant.Double), QgsField("Name",  QVariant.String) ] )

				    idx = layer.fieldNameIndex('Name')

				    height = 0
				    baseZ  = 0
				    num = 0 				                				    				    
				    iter = layer.getFeatures()            				    
				    for feat in iter:

				      num = num + 1 				                  				      
				      # fetch geometry
				      geom = feat.geometry()

				      Name = feat.attributes()[idx]              

#				      print Name
				      
				      testoWKT = geom.exportToWkt() + "\n"

#				      print testoWKT

				      istr = testoWKT.split(' ')
				      Z = str(istr[3])
				      Z = Z.replace(',','')
				      istruz = str(num) + "," + Name + "," + str(istr[0])

#				      print istruz



				      if (str(istr[0]) == "PolygonZ" and adesso == "GEKml_Polygons"):

#				         print "---scrivo un elemento poligono"
                 
				         feature = QgsFeature()              

				         feature.setGeometry( geom ) 

				         feature.initAttributes(4)

				         ID = num

#  RoofType;	// 0 = flat, 1 = shed, 2 = gable, 3 = hip
# h ttp://wiki.openstreetmap.org/wiki/OSM-4D/Roof_table

#				         RoofType = Name

#				         if (height == 0 and Z > 0):
				         if (float(Z) > 0):
#				            print Z                 
				            height = float(Z)
                         				  
				         values = [(ID), (height), (baseZ), (Name)]                  

				         feature.setAttributes(values) 

				         memprovider_Tin.addFeatures([feature])


                                          
				      testoWKT = testoWKT.replace("PointZ (", "")
				      testoWKT = testoWKT.replace("LineStringZ (", "")
				      testoWKT = testoWKT.replace("PolygonZ ((", "")              

				      testoWKT = testoWKT.replace("Polygon ((", "")

				      testoWKT = testoWKT.replace(", ", ",istruzione\n")              
              
				      testoWKT = testoWKT.replace("))", ",istruzione")
				      testoWKT = testoWKT.replace(")", ",istruzione")
				      testoWKT = testoWKT.replace(" ", ",")
              
				      testoWKT = testoWKT.replace("istruzione", istruz)

				      kml.write (testoWKT)

				      if (str(istr[0]) == "PointZ" and adesso == "GEKml_Polygons"):
				         splitta = testoWKT.split(',')              
				         baseZ = splitta[2]

				      if (str(istr[0]) == "LineStringZ" and adesso == "GEKml_Polygons"):
				         splitta = testoWKT.split(',')              
				         height = splitta[7]
				        				        
				kml.close()

				if (adesso == "GEKml_Polygons"):
				   memLay_Tin.updateFields()
				   tumpdir = unicode(QFileInfo(QgsApplication.qgisUserDbFilePath()).path()) + "/python/plugins/gearthview/tump"           
				   nomeqml = tumpdir + "/GEKml_Extrusions.qml"            
				   nomeqml.replace("\\", "/")

				   result = memLay_Tin.loadNamedStyle(nomeqml)


				return(0)                       
"""
-----------------------------------------------------
LISTA DEI FILE DA SALVARE con un suffisso DATA_time
-----------------------------------------------------

gearthview/tump/_3dPointsExport/GEKml_3dPoints.csv
gearthview/tump/_3dPointsExport/GEKml_3dPoints.qml

gearthview/tump/GEKml_Polygons.kml

         memory/GEKml_Extrusions.shp
gearthview/tump/GEKml_Extrusions.qml

from PyQt4.QtGui import QMessageBox
from qgis.core import QgsProject

path_absolute = QgsProject.instance().readPath("./")
QMessageBox.information(None, "Title", "AP: " + unicode(path_absolute))

error = QgsVectorFileWriter.writeAsVectorFormat(_vlayer, "GEKml_Extrusions.shp","utf-8",None,"ESRI Shapefile")
if error == QgsVectorFileWriter.NoError:
    print "success!"
"""
				



# ----------------------------------------------------
def startGeoDrink_Server(self):
 
				global serverStarted

				webServerDir = unicode(QFileInfo(QgsApplication.qgisUserDbFilePath()).path()) + "/python/plugins/gearthview/_WebServer/"        
				port = 5558

				from twisted.web.resource import Resource        

#				from twisted.web.twcgi import CGIScript
        
#				resource = CGIScript(webServerDir) 
        
#				if platform.system() == "Windows":            
#					os.startfile(webServerDir + 'QGIS_link.kmz')
						
#				if platform.system() == "Darwin":			
#					os.system("open " + str(webServerDir + 'QGIS_link.kmz'))
						
#				if platform.system() == "Linux":            
#					os.system("xdg-open " + str(webServerDir + 'QGIS_link.kmz'))
					
				GDX_Publisher(self)					
        
				if ( serverStarted == 0) :

					serverStarted = 1
					
					print ("Start GDX_Server Start --------!!!\n")

# ---------------------------------------------
					class FormPage(Resource):
					   def __init__(self, iface, pluginDir):
					      self.iface = iface
					      self.pluginDir = pluginDir
#					      site.addsitedir(os.path.abspath(os.path.dirname(pluginDir) + '/ext-libs'))
#					      print os.path.abspath(os.path.dirname(pluginDir))
               
					   def render_GET(self, request):

					      global lat,lon
					      global Zeta
					      global description

#------					      newdata = request.content.getvalue()
					      print request

#<GET /form?BBOX=16.3013171267662,38.63325421913416,16.62443680433362,38.86443091553171 HTTP/1.1>
#<GET /form?p=1&BBOX=-0.02411607307235109,-0.08678435516867355,0.149613182683106,0.06773426441872454 HTTP/1.1>
#<GET /form?p=0&bboxWest=12.13495518195707&%0A%09%09%09&bboxSouth=42.72418498839377&%0A%09%09%09&bboxEast=12.13932970664519&%0A%09%09%09&bboxNorth=42.72713741547008&%09%0A%09%09%09&lookatTerrainLon=12.13714248521776&%0A%09%09%09&lookatTerrainLat=42.7256612227012&%0A%09%09%09&lookatTerrainAlt=112.88& HTTP/1.1>
#<GET /form?p=0&BBOX=12.1356167437372,42.7264889613262,12.13701876665762,42.72743519322518&LookAt=12.13631776054357,42.72696207941286,205.39&LookatHeading=-0.002&LookatTilt=0&LookatTerrain=12.13631776055484,42.72696207945101,117.08&terrain=1 HTTP/1.1>
#<GET /form?p=0&BBOX=12.13560526927239,42.72643977188249,12.13703061697471,42.72740174642745&LookatTerrain=12.13631794864158,42.72692076136277,116.9&terrain=1 HTTP/1.1>
#<GET /form?p=1&BBOX=10.20045469843596,43.66302191930933,10.66672168693798,43.8667284090175&LookatTerrain=10.43397243010223,43.76510664670415,13.83&terrain=1&CAMERA=10.43397248408143,43.76510665598479,29287.22,0,-0.556&VIEW=60,38.141,1306,782 HTTP/1.1>

#<viewFormat>
#            BBOX=[bboxWest],[bboxSouth],[bboxEast],[bboxNorth];
#            LookatTerrain=[lookatTerrainLon],[lookatTerrainLat],[lookatTerrainAlt];
#            terrain=[terrainEnabled];
#            CAMERA=[lookatLon],[lookatLat],[lookatRange],[lookatTilt],[lookatHeading];
#            VIEW=[horizFov],[vertFov],[horizPixels],[vertPixels]
#</viewFormat>

					      stringa = str(request)
					      stringa = stringa.replace('<GET /form?','')                           
					      stringa = stringa.replace(' HTTP/1.1>','')
					      params = stringa.split('&')

					      param0 = params[0].replace('p=','')
					      pony  = param0

					      param1 = params[1].replace('BBOX=','')

					      bbox = param1.split(',')

					      kml = ( 
      '<?xml version="1.0" encoding="UTF-8"?>\n'
      '<kml xmlns="http://www.opengis.net/kml/2.2">\n')

					      if(pony == '3'):
                					         
					         kml = GDX_Publisher2(self, kml)
#					         print kml
					         return str(kml)

					      param2 = params[2].replace('LookatTerrain=','')
					      LookatTerrain = param2.split(',')

					      param3 = params[3].replace('terrain=','')
					      param4 = params[4].replace('CAMERA=','')
					      param5 = params[5].replace('VIEW=','')

					      CAMERA = param4.split(',')

					      lookatLon = float(CAMERA[0])
					      lookatLat = float(CAMERA[1])
					      lookatRange = float(CAMERA[2])
					      lookatTilt = float(CAMERA[3])
					      lookatHeading = float(CAMERA[4])
					      
#					      print("lookatLon %f")  %(lookatLon)
#					      print("lookatLat %f")  %(lookatLat)
#					      print("lookatRange %f")  %(lookatRange)
#					      print("lookatTilt %f")  %(lookatTilt)
#					      print("lookatHeading %f")  %(lookatHeading)                                                

					      west  = float(bbox[0])
					      south = float(bbox[1])
					      east  = float(bbox[2])
					      north = float(bbox[3])

					      lon = float(LookatTerrain[0])
					      lat = float(LookatTerrain[1])
					      Zeta = float(LookatTerrain[2])
     
#					      print ("Zeta = %f") %(Zeta)

#					      msg = ("LonLatH = %s, %s    elev = %s m      alt =  %s m") %(lon,lat,Zeta, lookatRange)
					      msg = ("LonLatH = %.7lf, %.7lf   elev = %s m     alt =  %s m") %(float(lon),float(lat),Zeta, lookatRange)
					      self.iface.mainWindow().statusBar().showMessage(msg)

#					      lon = ((east - west) / 2) + west
#					      lat = ((north - south) / 2) + south


					      if(pony != '0'):
					         kml = kml + (
      ' <Placemark>\n'
      '  <name>Z=%s</name>\n') %(Zeta)

					         kml = kml + (
      '	<Snippet maxLines="0"></Snippet>\n'
      '  <description>\n')      

					         qrCodeUrl = ("http://qrcode.kaywa.com/img.php?s=8&amp;d=%.7f,%.7f,%.2f") %(lat,lon,Zeta)

# http://w3w.co/   corrisponde a     https://map.what3words.com/

					         w3wUrl = ('<a href="https://map.what3words.com/%.7f,%.7f">w3w</a><br>') %(lat,lon)

#					         w3wUrl = ('<a href="http://w3w.co/%.7f,%.7f" target="_blank"><img width="300" height="100" alt="what3words" src="http://developer.what3words.com/wp-content/uploads/2014/12/w3w_logo_final.png" style="max-height: 44px;"></a><br>') %(lat,lon)

# h ttp://map.project-osrm.org/?z=17&center=41.210709%2C13.569338&loc=41.210602%2C13.568467&hl=en&alt=0
#					         osrmUrl = ('<a href="http://map.project-osrm.org/?z=17&center=%.7f%2C%.7f">W3W</a><br>') %(lat,lon)					         
#					         descript  = ('<html>lat  long  H<br><br>%.7f,%.7f,%.2f<br><br><table border=1 style="border-collapse:collapse; border-color:#000000;"cellpadding=0 cellspacing=0  width=250 style="FONT-SIZE: 11px; FONT-FAMILY: Verdana, Arial, Helvetica, sans-serif;"><tr><td bgcolor="#E3E1CA" align="right"><font COLOR="#FF0000"><b>CODE</b></font></td><td bgcolor="#E4E6CA"> <font COLOR="#008000">')  %(lat,lon,Zeta)


# h ttps://citymapper.com/roma/?start=41.901082099999996,12.501135900000008&saddr=Start%20Location&end=41.21271077541033,13.567997962236404&eaddr=End%20Location

# h ttps://www.google.co.uk/maps/dir/%2841.901082099999996,+12.501135900000008%29/%2841.21271077541033,+13.567997962236404%29/@41.5671699,12.555604,9z/data=!3m1!4b1!4m9!4m8!1m3!2m2!1d12.5011359!2d41.9010821!1m3!2m2!1d13.567998!2d41.2127108

					         descript  = ('<html>lat  long  H<br><br>%.7f,%.7f,%.2f<br><br>%s<table border=1 style="border-collapse:collapse; border-color:#000000;"cellpadding=0 cellspacing=0  width=250 style="FONT-SIZE: 11px; FONT-FAMILY: Verdana, Arial, Helvetica, sans-serif;"><tr><td bgcolor="#E3E1CA" align="right"><font COLOR="#FF0000"><b>CODE</b></font></td><td bgcolor="#E4E6CA"> <font COLOR="#008000">')  %(lat,lon,Zeta,w3wUrl)
                                      
					         qrCodeImg = ('<img alt="" src="%s" /></html>') %(qrCodeUrl)

					         description = descript + qrCodeImg

					         kml = kml + ('<![CDATA[%s')  %(description)
					         
					         kml = kml + (']]></description>\n')					            

					         kml = kml + ('  <Style>\n'
      '   <Icon>\n'
      '  	<href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle_highlight.png</href>\n'
      '   </Icon>\n' 
      '  </Style>\n')

					         kml = kml + (                        
      '  <Point>\n'
      '    <coordinates>%.7f,%.7f,%.2f</coordinates>\n'
      '  </Point>\n'
      ' </Placemark>\n') %( lon, lat, Zeta )

                                 
                          # Tag close KML ----
#					      kml = kml + ('</kml>')
      


					      canvas = self.iface.mapCanvas()
					      mapRenderer = canvas.mapRenderer()
					      srs = mapRenderer.destinationCrs()
				
					      crsSrc = QgsCoordinateReferenceSystem(4326)
					      crsDest = QgsCoordinateReferenceSystem(srs) 
					      xform = QgsCoordinateTransform(crsSrc, crsDest)
					      
   
					      GEraggio = (lookatRange - Zeta) / 2.
                
					      raggio = GEraggio
                                 
                
                # Calculate QgisViewBox from 3D geoCoords
                                 					      
#					      print ("raggio = %f") %(raggio)
                
					      ilMetroGeo = 0.000011922282515       

					      raggioGeo = raggio * ilMetroGeo

					      x1Geo = lon - float(raggioGeo)
					      y1Geo = lat - float(raggioGeo)             
					      x2Geo = lon + float(raggioGeo)
					      y2Geo = lat + float(raggioGeo)

					      pt1 = xform.transform(QgsPoint(x1Geo, y1Geo))
					      pt2 = xform.transform(QgsPoint(x2Geo, y2Geo))

					      x1 = pt1.x()
					      y1 = pt1.y()             
					      x2 = pt2.x()
					      y2 = pt2.y()               


					      box = QgsRectangle(x1, y1, x2, y2)

                                 
					      canvas = self.iface.mapCanvas()
                              
					      canvas.setExtent(box)

					      if QGis.QGIS_VERSION_INT >= 20801:                
					        canvas.setRotation(-lookatHeading)


					      canvas.refresh()
					      
					      if(pony == '2'):					         
					         QGEarth_addPoint(self)

					             
#					      print  'Content-Type: application/vnd.google-earth.kml+xml\n'

#					      kml_2 = GDX_Publisher2(self, kml)
#					      kml = kml + kml_2
					      
					      kml = kml + ('</kml>')
					      
					      return str(kml)					   
					   					   


					   def render_POST(self, request):

					      global lat,lon
					      global Zeta
					      global description

					      stringa = str(request)
					      stringa = stringa.replace('<GET /form?','')                           
					      stringa = stringa.replace(' HTTP/1.1>','')
					      params = stringa.split('&')

					      param0 = params[0].replace('p=','')
					      pony  = param0

					      param1 = params[1].replace('BBOX=','')

					      bbox = param1.split(',')

					      west  = float(bbox[0])
					      south = float(bbox[1])
					      east  = float(bbox[2])
					      north = float(bbox[3])

					      param2 = params[2].replace('LookatTerrain=','')
					      LookatTerrain = param2.split(',')

					      param3 = params[3].replace('terrain=','')
					      param4 = params[4].replace('CAMERA=','')
					      param5 = params[5].replace('VIEW=','')

					      CAMERA = param4.split(',')

					      lookatLon = float(CAMERA[0])
					      lookatLat = float(CAMERA[1])
					      lookatRange = float(CAMERA[2])
					      lookatTilt = float(CAMERA[3])
					      lookatHeading = float(CAMERA[4])

					      lon = float(LookatTerrain[0])
					      lat = float(LookatTerrain[1])
					      Zeta = float(LookatTerrain[2])

					      canvas = self.iface.mapCanvas()
					      mapRenderer = canvas.mapRenderer()
					      srs = mapRenderer.destinationCrs()
				
					      crsSrc = QgsCoordinateReferenceSystem(4326)
					      crsDest = QgsCoordinateReferenceSystem(srs) 
					      xform = QgsCoordinateTransform(crsSrc, crsDest)
					         
					      GEraggio = (lookatRange - Zeta) / 2.
                
					      raggio = GEraggio
                                 
                
                # Calculate QgisViewBox from 3D geoCoords
                                 					      
#					      print ("raggio = %f") %(raggio)
                
					      ilMetroGeo = 0.000011922282515       

					      raggioGeo = raggio * ilMetroGeo

					      x1Geo = lon - float(raggioGeo)
					      y1Geo = lat - float(raggioGeo)             
					      x2Geo = lon + float(raggioGeo)
					      y2Geo = lat + float(raggioGeo)

					      pt1 = xform.transform(QgsPoint(x1Geo, y1Geo))
					      pt2 = xform.transform(QgsPoint(x2Geo, y2Geo))

					      x1 = pt1.x()
					      y1 = pt1.y()             
					      x2 = pt2.x()
					      y2 = pt2.y()               

					      box = QgsRectangle(x1, y1, x2, y2)
                                 
					      canvas = self.iface.mapCanvas()
                              
					      canvas.setExtent(box)


					      canvas.refresh()

               
					      return ''

					root = Resource()
					root.putChild("form", FormPage(self.iface, self.plugin_dir))
					root.putChild("gaeta", File(webServerDir))

					cesiumDir = webServerDir + "cesium/"          
					root.putChild("cesium", File(cesiumDir))

					reactor.listenTCP(5558, server.Site(root))
					reactor.run()



#------------------------------------------------------------------------------
# Add the current GEarth point in QGis current drawing function ------------------------------------------
def QGEarth_addPoint(self):

				if ( serverStarted == 0) :
#						QMessageBox.critical(self.iface.mainWindow(), "You need to startQrCoding, before !!!", "")
						self.iface.messageBar().pushMessage("WARNING", "You need to startQrCoding, before !!!", level=QgsMessageBar.WARNING, duration=3)
						print ("You need to startQrCoding, before !!!\n")
						return

				global lat, lon
				global Zeta
				global description								      
						
#				print ("QGEarth %f %f") %(lat, lon) 

				canvas = self.iface.mapCanvas()
				layer = canvas.currentLayer()

				if layer:
				  if layer.type() == layer.VectorLayer:

				    provider = layer.dataProvider()
				    Edit = layer.isEditable()
            				  				
				    if ( Edit == 0 ):
#				       QMessageBox.critical(self.iface.mainWindow(), "WARNING: Layer not editable", str(layer.name()))
				       self.iface.messageBar().pushMessage("WARNING", "Layer not editable", level=QgsMessageBar.WARNING, duration=3) 
                                              
				       return
               
				    srs = layer.crs();
				    crsSrc = QgsCoordinateReferenceSystem(4326)
				    crsDest = QgsCoordinateReferenceSystem(srs) 
				    xform = QgsCoordinateTransform(crsSrc, crsDest)
				    pt = xform.transform(QgsPoint(lon, lat))
				
				    gPnt = QgsGeometry.fromPoint(QgsPoint(pt.x(),pt.y()))
				    
#				    print ("QGEarth %f %f %f %f") %(lat, lon, pt.x(), pt.y())               				    

				    feature = QgsFeature()
				    feature.setGeometry( gPnt )

#				    print ("description = <%s>") %(description)				    

				    feature.initAttributes(5)

				    adesso = str(datetime.datetime.now())
				    adesso = adesso.replace(" ","_")
				    adesso = adesso.replace(":","_")
				    adesso = adesso.replace(".","_")  
				    
				    res = provider.addAttributes( [ QgsField("name",  QVariant.String), QgsField("description", QVariant.String), QgsField("DateTime",  QVariant.String),QgsField("lat",  QVariant.Double), QgsField("lon",  QVariant.Double), QgsField("Z",  QVariant.String)] )

				    lat_ = float(lat)
				    lon_ = float(lon)
                       
#				    print feature.id()

				    name = ("%.7f,%.7f,%s") %(lat_, lon_, Zeta)

				    values = [(name), (description), adesso, lat_, lon_, Zeta]                  

				    feature.setAttributes(values) 

				    provider.addFeatures([feature])

				    layer.updateFields()
				    
				    layer.updateExtents()
				    
#				    layer.commitChanges()

				    canvas.refresh()

				else:

				    self.iface.messageBar().pushMessage("WARNING", "Creating a Point Layer...", level=QgsMessageBar.WARNING, duration=3)
				       
				    geomType = "Point" + '?crs=proj4:' + QgsProject.instance().readEntry("SpatialRefSys","/ProjectCRSProj4String")[0]
				    DronePlan = "GEarthView_Points"             
				    memLay = QgsVectorLayer(geomType, DronePlan, 'memory') 
				    provider = memLay.dataProvider()
				       
                                   
				    memLay.updateExtents()
				    memLay.commitChanges()
				    QgsMapLayerRegistry.instance().addMapLayer(memLay) 

# GDX_Publisher --------------------------------------

def GDX_Publisher(self):

#				print "GDX_Publisher -------------------------------\n"
        
				mapCanvas = self.iface.mapCanvas()
				
				tumpdir = unicode(QFileInfo(QgsApplication.qgisUserDbFilePath()).path()) + "/python/plugins/gearthview/tump"

				adesso = str(datetime.datetime.now())
				adesso = adesso.replace(" ","_")
				adesso = adesso.replace(":","_")
				adesso = adesso.replace(".","_")        				

#				print "adesso: <%s>\n" %(adesso)

# Prendo le coordinate della finestra attuale---------------------------------------
# 13.5702225179249876,41.2134192420407501 : 13.5768356834183166,41.2182110366311107
				text = mapCanvas.extent().toString()
				text1 = text.replace("," , " ")
				text2 = text1.replace(" : ", ",")
#				the_filter = "bbox($geometry, geomFromWKT ( 'LINESTRING(" + text2 + ")'))"
#				self.doPaste(the_filter) 				

# HERE IT DELETES THE OLD IMAGE ------------------------------------
# (if you comment these, images still remain ...  :)
				for filename in glob.glob(str(tumpdir + '/*.png')) :
				   os.remove( str(filename) )
				for filename in glob.glob(str(tumpdir + '/*.pngw')) :
				   os.remove( str(filename) )            
# ------------------------------------------------------------------				

    
				tname = 'ZIPPA'

				out_folder = tumpdir
				
				kml = codecs.open(out_folder + '/doc.kml', 'w', encoding='utf-8')
#				kml=open(out_folder + '/doc.kml', 'w')
				#

				iface = qgis.utils.iface

				if QGis.QGIS_VERSION_INT <= 120200: 

				   mapRenderer = mapCanvas.mapRenderer()
				   mapRect = mapRenderer.extent()
				   width = mapRenderer.width()
				   height = mapRenderer.height()
				   srs = mapRenderer.destinationCrs()

				   # create output image and initialize it
				   image = QImage(QSize(width, height), QImage.Format_ARGB32)

				   image.fill(0)
				
				   #adjust map canvas (renderer) to the image size and render
				   imagePainter = QPainter(image)
				
				   zoom = 1
				   target_dpi = int(round(zoom * mapRenderer.outputDpi()))				
				
				   mapRenderer.setOutputSize(QSize(width, height), target_dpi)
			
				   mapRenderer.render(imagePainter)
				   imagePainter.end()

				   xN = mapRect.xMinimum()
				   yN = mapRect.yMinimum()

				   nomePNG = ("QGisView_%lf_%lf_%s") % (xN, yN, adesso)
				
				   input_file = out_folder + "/" + nomePNG + ".png"
				
				   #Save the image
				   image.save(input_file, "png")

				else:   # ovvero  QGis.QGIS_VERSION_INT > 120200


           
				   mapRenderer = mapCanvas.mapRenderer()
				   mapRect = mapRenderer.extent()
				   width = mapRenderer.width()
				   height = mapRenderer.height()
				   srs = mapRenderer.destinationCrs()

				   xN = mapRect.xMinimum()
				   yN = mapRect.yMinimum()

				   mapSettings = QgsMapSettings()
				   mapSettings.setMapUnits(0)
				   mapSettings.setExtent(mapRect)
				   DPI = 300
				   mapSettings.setOutputDpi(DPI)

				   mapSettings.setOutputSize(QSize(width, height))

				   lst = []
				   layerTreeRoot = QgsProject.instance().layerTreeRoot()
				   for id in layerTreeRoot.findLayerIds():
				       node = layerTreeRoot.findLayer(id)
				       lst.append(id)
           
				   mapSettings.setLayers(lst)
           
				   mapSettings.setFlags(QgsMapSettings.Antialiasing | QgsMapSettings.UseAdvancedEffects | QgsMapSettings.ForceVectorOutput | QgsMapSettings.DrawLabeling)
				   image = QImage(QSize(width, height), QImage.Format_RGB32)

				   image.fill(0)

				   image.setDotsPerMeterX(DPI / 25.4 * 1000)
				   image.setDotsPerMeterY(DPI / 25.4 * 1000)
				   p = QPainter()
				   p.begin(image)
				   mapRenderer = QgsMapRendererCustomPainterJob(mapSettings, p)
				   mapRenderer.start()
				   mapRenderer.waitForFinished()
				   p.end()

				   nomePNG = ("QGisView_%lf_%lf_%s") % (xN, yN, adesso)
				   input_file = out_folder + "/" + nomePNG + ".png"
				
				   #Save the image
				   image.save(input_file, "png")


				# EndIf     # QGis.QGIS_VERSION_INT > 120200

				layer = mapCanvas.currentLayer()
				crsSrc = srs  # QgsCoordinateReferenceSystem(layer.crs())   # prendere quello attuale
				crsDest = QgsCoordinateReferenceSystem(4326)  # Wgs84LLH
				xform = QgsCoordinateTransform(crsSrc, crsDest)

				x1 = mapRect.xMinimum()
				y1 = mapRect.yMinimum()
				
				x2 = mapRect.xMaximum()
				y2 = mapRect.yMinimum()

				x3 = mapRect.xMaximum()
				y3 = mapRect.yMaximum()

				x4 = mapRect.xMinimum()
				y4 = mapRect.yMaximum()

				xc = (x1 + x3) / 2.
				yc = (y1 + y3) / 2.	

				pt1 = xform.transform(QgsPoint(x1, y1))				
				pt2 = xform.transform(QgsPoint(x2, y2))
				pt3 = xform.transform(QgsPoint(x3, y3))
				pt4 = xform.transform(QgsPoint(x4, y4))                				

				pt5 = xform.transform(QgsPoint(xc, yc))

				xc = pt5.x()
				yc = pt5.y()

				x1 = pt1.x()
				y1 = pt1.y()
				
				x2 = pt2.x()
				y2 = pt2.y()
				
				x3 = pt3.x()
				y3 = pt3.y()
				
				x4 = pt4.x()
				y4 = pt4.y()
				

				
				#Write kml header
				kml.write('<?xml version="1.0" encoding="UTF-8"?>\n')
				kml.write('<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">\n')				
				kml.write('    <Document>\n')
				kml.write('    	 <name>QGisView</name>\n')
				kml.write('    	 <Snippet maxLines="0"></Snippet>\n') 
#				loc = ("    	 <description><![CDATA[http://map.project-osrm.org/?loc=%.7lf,%.7lf&ly=1784084387]]></description>\n") %(yc, xc)
#				loc = ("    	 <description><![CDATA[http://map.project-osrm.org/?z=16&center=%.7lf,%.7lf&loc=&loc=&hl=en&ly=&alt=&df=&srv=]]></description>\n") %(yc, xc)
				loc = ("    	 <description><![CDATA[https://map.what3words.com/%.7lf,%.7lf]]></description>\n") %(yc, xc)

				kml.write(loc)
#
				
				
#				kml.write('    	 <description>http://map.project-osrm.org/?hl=it&loc=45.989486,12.778154&loc=45.985624,12.781076&z=16&center=45.984058,12.774417&alt=0&df=0&re=0&ly=-940622518</description>\n')
				
				kml.write('	     <open>1</open>\n')

				kml.write('	<Style id="sh_style">\n')
				kml.write('		<PolyStyle>\n')
				kml.write('			<color>7fff8080</color>\n')
				kml.write('		</PolyStyle>\n')
				kml.write('	</Style>\n')
				kml.write('	<StyleMap id="msn_style">\n')
				kml.write('		<Pair>\n')
				kml.write('			<key>normal</key>\n')
				kml.write('			<styleUrl>#sn_style</styleUrl>\n')
				kml.write('		</Pair>\n')
				kml.write('		<Pair>\n')
				kml.write('			<key>highlight</key>\n')
				kml.write('			<styleUrl>#sh_style</styleUrl>\n')
				kml.write('		</Pair>\n')
				kml.write('	</StyleMap>\n')
				kml.write('	<Style id="sn_style">\n')
				kml.write('		<PolyStyle>\n')
				kml.write('			<color>00ff8080</color>\n')
				kml.write('			<fill>0</fill>\n')
				kml.write('		</PolyStyle>\n')
				kml.write('	</Style>\n')
				kml.write('NEL MEZZO DEL CAMMIN DI NOSTRA VITA 1\n')   

				kml.write('	     <Style id="sh_ylw-pushpin">\n')
				kml.write('	     	<IconStyle>\n')
				kml.write('	     		<scale>1.2</scale>\n')
				kml.write('	     	</IconStyle>\n')
				kml.write('	     	<PolyStyle>\n')
				kml.write('	     		<fill>0</fill>\n')
				kml.write('	     	</PolyStyle>\n')
				kml.write('	     </Style>\n')
				kml.write('	     <Style id="sn_ylw-pushpin">\n')
				kml.write('	     	<PolyStyle>\n')
				kml.write('	     		<fill>0</fill>\n')
				kml.write('	     	</PolyStyle>\n')
				kml.write('	     </Style>\n')
				kml.write('	     <StyleMap id="msn_ylw-pushpin">\n')
				kml.write('	     	<Pair>\n')
				kml.write('	     		<key>normal</key>\n')
				kml.write('	     		<styleUrl>#sn_ylw-pushpin</styleUrl>\n')
				kml.write('	     	</Pair>\n')
				kml.write('	     	<Pair>\n')
				kml.write('	     		<key>highlight</key>\n')
				kml.write('	     		<styleUrl>#sh_ylw-pushpin</styleUrl>\n')
				kml.write('	     	</Pair>\n')
				kml.write('	     </StyleMap>\n')				
				kml.write('NEL MEZZO DEL CAMMIN DI NOSTRA VITA 2\n')

				kml.write('    <StyleMap id="msn_style">\n')
				kml.write('        <Pair>\n')
				kml.write('            <key>normal</key>\n')
				kml.write('            <styleUrl>#sn_style</styleUrl>\n')
				kml.write('        </Pair>\n')
				kml.write('        <Pair>\n')
				kml.write('            <key>highlight</key>\n')
				kml.write('            <styleUrl>#sh_style</styleUrl>\n')
				kml.write('        </Pair>\n')
				kml.write('    </StyleMap>\n')
				kml.write('NEL MEZZO DEL CAMMIN DI NOSTRA VITA 3\n')
				
				kml.write('	     	<Style id="hl">\n')
				kml.write('	     		<IconStyle>\n')
				kml.write('	     			<scale>0.7</scale>\n')
				kml.write('	     			<Icon>\n')
				kml.write('	     				<href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle_highlight.png</href>\n')
				kml.write('	     			</Icon>\n')
				kml.write('	     		</IconStyle>\n')
				kml.write('	     		<LabelStyle>\n')
				kml.write('	     			<scale>0.7</scale>\n')
				kml.write('	     		</LabelStyle>\n')							
				kml.write('	     		<ListStyle>\n')
				kml.write('	     		</ListStyle>\n')
				kml.write('	     	</Style>\n')
				kml.write('	     	<Style id="default">\n')
				kml.write('	     		<IconStyle>\n')
				kml.write('	     			<scale>0.7</scale>\n')
				kml.write('	     			<Icon>\n')
				kml.write('	     				<href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href>\n')
				kml.write('	     			</Icon>\n')
				kml.write('	     		</IconStyle>\n')
				kml.write('	     		<LabelStyle>\n')
				kml.write('	     			<scale>0.7</scale>\n')
				kml.write('	     		</LabelStyle>\n')			
				kml.write('	     		<ListStyle>\n')
				kml.write('	     		</ListStyle>\n')
				kml.write('	     	</Style>\n')
				kml.write('	     	<StyleMap id="default0">\n')
				kml.write('	     		<Pair>\n')
				kml.write('	     			<key>normal</key>\n')
				kml.write('	     			<styleUrl>#default</styleUrl>\n')
				kml.write('	     		</Pair>\n')
				kml.write('	     		<Pair>\n')
				kml.write('	     			<key>highlight</key>\n')
				kml.write('	     			<styleUrl>#hl</styleUrl>\n')
				kml.write('	     		</Pair>\n')
				kml.write('	     	</StyleMap>\n')
				kml.write('NEL MEZZO DEL CAMMIN DI NOSTRA VITA 4\n')				
				
				rotazio = 0.0
				if QGis.QGIS_VERSION_INT >= 20801:                
				   rotazio = -(mapCanvas.rotation())
				
				
				kml.write('      <Folder>\n')
				
				xc = (x1 + x3) / 2.
				yc = (y1 + y3) / 2.
				dx = (x3 - x1) * 75000. #100000.


				kml.write('    		<open>1</open>\n')    
				kml.write('    		<NetworkLink>\n')
				kml.write('    		   <name>QGIS_link</name>\n')
				kml.write('    		   <visibility>1</visibility>\n')
				kml.write('    		   <open>1</open>\n')
				kml.write('    		   <Link>\n')
				kml.write('    		      <href>../_WebServer/QGIS_link.kmz</href>\n')
				kml.write('    		   </Link>\n')
				kml.write('    		</NetworkLink>\n')        

        				
				kml.write('    		<LookAt>\n')
				stringazza = ("    		   <longitude>%lf</longitude>\n") %(xc)
				kml.write(stringazza)				
				stringazza = ("    		   <latitude>%lf</latitude>\n") %(yc)
				kml.write(stringazza)				
				kml.write('    		   <altitude>0</altitude>\n')

				stringazza = ("    		   <heading>%lf</heading>\n") %(rotazio)
				kml.write(stringazza)
        
				kml.write('    		   <tilt>0</tilt>\n')
				stringazza = ("    		   <range>%lf</range>\n") %(dx)
				kml.write(stringazza)				
				kml.write('    		   <gx:altitudeMode>relativeToGround</gx:altitudeMode>\n')
				kml.write('    		</LookAt>\n')

				kml.write('      <GroundOverlay>\n')
				kml.write('    	 <name>QGisView</name>\n')
        				
				kml.write('    	<Icon>\n')

#				nomePNG = ("QGisView_%lf_%lf_%s") % (xN, yN, adesso)
				stringazza = ("    	<href>%s.png</href>\n") % (nomePNG)
				kml.write(stringazza)
				kml.write('    		<viewBoundScale>1.0</viewBoundScale>\n')
				kml.write('    	</Icon>\n')
				kml.write('    	<gx:LatLonQuad>\n')
				kml.write('    		<coordinates>\n')

				stringazza =    ("%.7lf,%.7lf,0 %.7lf,%.7lf,0 %.7lf,%.7lf,0 %.7lf,%.7lf,0\n") % (x1, y1, x2, y2, x3, y3, x4, y4)        		
				kml.write(stringazza)				

				kml.write('    		</coordinates>\n')
				kml.write('    	</gx:LatLonQuad>\n')
				kml.write('    </GroundOverlay>\n')

#				#Write kml footer
#				kml.write('</kml>\n')
#				#Close kml file
#				kml.close()



				#Export tfw-file
				xScale = (mapRect.xMaximum() - mapRect.xMinimum()) /  image.width()
				yScale = (mapRect.yMaximum() - mapRect.yMinimum()) /  image.height()

							
				f = open(out_folder + "/" + nomePNG	+ ".pngw", 'w')				
				f.write(str(xScale) + '\n')
				f.write(str(0) + '\n')
				f.write(str(0) + '\n')
				f.write('-' + str(yScale) + '\n')
				f.write(str(mapRect.xMinimum()) + '\n')
				f.write(str(mapRect.yMaximum()) + '\n')
				f.write(str(mapRect.xMaximum()) + '\n')
				f.write(str(mapRect.yMinimum()))				
				f.close()
			

				nomeLay = "gearthview" 	 # foo default name		


#  Adesso scrivo il vettoriale
#  Prendo il sistema di riferimento del Layer selezionato ------------------
        
        
				layer = mapCanvas.currentLayer()
				if layer:
				  if layer.type() == layer.VectorLayer:				

#				    nele = -1
				    name = layer.source();
				    nomeLayer = layer.name()
				    nomeLay   = nomeLayer.replace(" ","_")

				    kml.write('    <Folder>\n')
				    stringazza =   ('			<name>%s</name>\n') % (nomeLay)
				    kml.write (stringazza)     				          
      				    
				    crsSrc = layer.crs();

				    crsDest = QgsCoordinateReferenceSystem(4326)  # Wgs84LLH
				    xform = QgsCoordinateTransform(crsSrc, crsDest)

#----------------------------------------------------------------------------
#  Trasformo la finestra video in coordinate layer, 
#     per estrarre solo gli elementi visibili
#----------------------------------------------------------------------------
#				    mapCanvas = iface.mapCanvas()
				    boundBox = mapCanvas.extent() 
                
				    xMin = float(boundBox.xMinimum())
				    yMin = float(boundBox.yMinimum())

				    xMax = float(boundBox.xMaximum())                
				    yMax = float(boundBox.yMaximum())
				    
				    
				    crs2 = mapCanvas.mapRenderer().destinationCrs()
				    crsSrc2  = QgsCoordinateReferenceSystem(crs2.authid())   
				    crsDest2 = QgsCoordinateReferenceSystem(layer.crs())   
				    xform2   = QgsCoordinateTransform(crsSrc2, crsDest2)
                              
				    pt0 = xform2.transform(QgsPoint(xMin, yMin))
				    pt1 = xform2.transform(QgsPoint(xMax, yMax))
				    
				    rect = QgsRectangle(pt0, pt1)
				    
#----------------------------------------------------------------------------


				    rq = QgsFeatureRequest(rect)

				    iter = layer.getFeatures(rq)				    
				    for feat in iter:
				    
#				      nele = nele + 1
				      nele = feat.id()

# Prendo il contenuto dei campi -------------
#				      fff = feat.fields()
#				      num = fff.count()
#				      for iii in range(num):
#				         print "%s " %(feat[iii])
# -------------------------------------------

# NathanW example code-----------------------------
#				      for feature in layer.getFeatures():
#				         for attr in feature:
#				            print attr
#
#				      for f in layer.pendingFields():
#				         print f.name()
#-------------------------------------------------
              				      
				      # fetch geometry
				      geom = feat.geometry()
				       # show some information about the feature

#				      print ("GeomType: %d") %(geom.type())

#  For MultiPoint    http://gis.stackexchange.com/questions/55067/how-to-convert-multipoint-layer-to-point
				      
				      if geom.type() == QGis.Point:
				        elem = geom.asPoint()
				        x1 = elem.x()
				        y1 = elem.y()

				        pt1 = xform.transform(QgsPoint(x1, y1))

				        kml.write ('	<Placemark>\n')
				        
				        stringazza =   ('		<name>%s</name>\n') % (nele)
				        kml.write (stringazza)	
                			        
				        kml.write ('	<styleUrl>#default0</styleUrl>\n')

# DESCRIPTION DATA-----------
				        kml.write ('	<Snippet maxLines="0"></Snippet>\n')
				        kml.write ('	<description><![CDATA[\n')				        
				        kml.write ('<html><body><table border="1">\n')
				        kml.write ('<tr><th>Field Name</th><th>Field Value</th></tr>\n')
 
 # Prendo il contenuto dei campi -------------
				        fff = feat.fields()
				        num = fff.count()                
				        iii = -1
				        for f in layer.pendingFields(): 				        
				           iii = iii + 1
				           
				           stringazza = ('<tr><td>%s</td><td>%s</td></tr>\n') %(f.name(),feat[iii])

				           kml.write (stringazza)					           
               	
				        kml.write ('</table></body></html>\n')
				        kml.write (']]></description>\n')
				        
#  VECCHIO METODO------------------------------------------------------------				        
				        kml.write ('		<Point>\n')
				        kml.write ('			<gx:drawOrder>1</gx:drawOrder>\n')
				        stringazza =   ('			<coordinates>%.7lf,%.7lf</coordinates>\n') % (pt1.x(), pt1.y())
				        kml.write (stringazza)                                  
				        kml.write ('		</Point>\n')
#  VECCHIO METODO------------------------------------------------------------

#  NUOVO METODO------------------------------------------------------------
#				        testo = geom.exportToWkt() 
#				        geometra = ogr.CreateGeometryFromWkt(testo)
#				        testoKML = geometra.ExportToKML()
#				        kml.write (testoKML)
#  NUOVO METODO------------------------------------------------------------

				        kml.write ('	</Placemark>\n')


				      elif geom.type() == QGis.Line:

				        kml.write ('	<Placemark>\n')
                	
				        stringazza =   ('		<name>%s</name>\n') % (nele)
				        kml.write (stringazza)

# DESCRIPTION DATA-----------
				        kml.write ('	<Snippet maxLines="0"></Snippet>\n')
				        kml.write ('	<description><![CDATA[\n')				        
				        kml.write ('<html><body><table border="1">\n')
				        kml.write ('<tr><th>Field Name</th><th>Field Value</th></tr>\n')
 
 # Prendo il contenuto dei campi -------------
				        fff = feat.fields()
				        num = fff.count()                
				        iii = -1
				        for f in layer.pendingFields(): 				        
				           iii = iii + 1
				           
				           stringazza = ('<tr><td>%s</td><td>%s</td></tr>\n') %(f.name(),feat[iii])

				           kml.write (stringazza)					           
               	
				        kml.write ('</table></body></html>\n')
				        kml.write (']]></description>\n')
				        
#  VECCHIO METODO------------------------------------------------------------               			        
#				        kml.write ('		<LineString>\n')
#				        kml.write ('			<tessellate>1</tessellate>\n')
#				        kml.write ('			<coordinates>\n')
				        
#				        elem = geom.asPolyline()
				         
#				        for p1 in elem:
#				          x1,y1 = p1.x(),p1.y()

#				          pt1 = xform.transform(QgsPoint(x1, y1))
                                               
#				          stringazza =   ('%.7lf,%.7lf \n') % (pt1.x(), pt1.y())
#				          kml.write (stringazza)
				          
#				        kml.write ('			</coordinates>\n')                   
#				        kml.write ('		</LineString>\n')
#  VECCHIO METODO------------------------------------------------------------

#  NUOVO METODO------------------------------------------------------------
				        wkt = layer.crs().toWkt()
				        source = osr.SpatialReference()
				        source.ImportFromWkt(wkt)

				        target = osr.SpatialReference()
				        target.ImportFromEPSG(4326)

				        transform = osr.CoordinateTransformation(source, target)

				        testo = geom.exportToWkt() 
#				        print testo
				        testo = testo.replace("LineStringZ (", "LineString (")
				        testo = testo.replace(" 0,", ",")
				        testo = testo.replace(" 0)", ")")                
				        geometra = ogr.CreateGeometryFromWkt(testo)
				        geometra.Transform(transform)                
				        testoKML = geometra.ExportToKML()
				        kml.write (testoKML)
#  NUOVO METODO------------------------------------------------------------                
                
				        kml.write ('	</Placemark>\n')


				      elif geom.type() == QGis.Polygon:

				        kml.write ('	<Placemark>\n')
				        stringazza =   ('		<name>%s</name>\n') % (nele)
				        kml.write (stringazza)				        
				        kml.write ('		<styleUrl>#msn_style</styleUrl>\n')
				        
# DESCRIPTION DATA-----------
				        kml.write ('	<Snippet maxLines="0"></Snippet>\n')
				        kml.write ('	<description><![CDATA[\n')				        
				        kml.write ('<html><body><table border="1">\n')
				        kml.write ('<tr><th>Field Name</th><th>Field Value</th></tr>\n')
 
 # Prendo il contenuto dei campi -------------
				        fff = feat.fields()
				        num = fff.count()                
				        iii = -1
                
				        height = ',0 '
				        extrusion = '<Polygon>'                                

				        for f in layer.pendingFields(): 				        
				           iii = iii + 1
				           
				           stringazza = ('<tr><td>%s</td><td>%s</td></tr>\n') %(f.name(),feat[iii])

				           # Se esiste un campo "height" prendi il valore e impostalo
                   
				           if (f.name() == "height"):
				              height = ',' + str(feat[iii]) + ' '
				              extrusion = '<Polygon><extrude>1</extrude><altitudeMode>relativeToGround</altitudeMode>'

				           kml.write (stringazza)					           
               	
				        kml.write ('</table></body></html>\n')
				        kml.write (']]></description>\n')
				        
				        
				        

#  VECCHIO METODO------------------------------------------------------------                				        
#				        kml.write ('		<Polygon>\n')
#				        kml.write ('			<tessellate>1</tessellate>\n')
#				        kml.write ('     <outerBoundaryIs>\n')
#				        kml.write ('        <LinearRing>\n')
#				        kml.write ('         <coordinates>\n')
              
#				        elem = geom.asPolygon()

# http://qgis.spatialthoughts.com/2012/11/tip-count-number-of-vertices-in-layer.html				        
#				        if geom.isMultipart():
#				          print "MULTIPART !!!"
#				          elem = geom.asMultiPolygon()

##				          for polygon in elem:
##				             for ring in polygon:
## 				                print ("Pezzo con %d vertici") %(len(ring))

                            			        			        
#				        for iii in range (len(elem)):

#				          if (iii == 1):				          
#				            kml.write ('         </coordinates>\n')
#				            kml.write ('         </LinearRing>\n')
#				            kml.write ('         </outerBoundaryIs>\n')
#				            kml.write ('         <innerBoundaryIs>\n')
#				            kml.write ('         <LinearRing>\n')
#				            kml.write ('         <coordinates>\n')

#				          if (iii > 1):				          
#				            kml.write ('         </coordinates>\n')
#				            kml.write ('         </LinearRing>\n')
#				            kml.write ('         </innerBoundaryIs>\n')
#				            kml.write ('         <innerBoundaryIs>\n')
#				            kml.write ('         <LinearRing>\n')
#				            kml.write ('         <coordinates>\n')	
				        
#				          for jjj in range (len(elem[iii])):
				                         
#				            x1,y1 = elem[iii][jjj][0], elem[iii][jjj][1]

#				            if geom.isMultipart():
#				               pt1 = xform.transform(x1)
#				            else:				            
#				               pt1 = xform.transform(QgsPoint(x1, y1))
                          
#				            stringazza =   ('%.7lf,%.7lf,0 \n') % (pt1.x(), pt1.y())
#				            kml.write (stringazza)

#				        if (iii == 0):
#				           kml.write ('         </coordinates>\n')
#				           kml.write ('        </LinearRing>\n')
#				           kml.write ('     </outerBoundaryIs>\n')
#				           kml.write ('   </Polygon>\n')

#				        if (iii > 0):
#				           kml.write ('         </coordinates>\n')
#				           kml.write ('        </LinearRing>\n')
#				           kml.write ('     </innerBoundaryIs>\n')
#				           kml.write ('   </Polygon>\n')	
#  VECCHIO METODO------(chi lascia la vecchia strada...)-------------------


#  NUOVO METODO------------------------------------------------------------
				        wkt = layer.crs().toWkt()
				        source = osr.SpatialReference()
				        source.ImportFromWkt(wkt)

				        target = osr.SpatialReference()
				        target.ImportFromEPSG(4326)

				        transform = osr.CoordinateTransformation(source, target)

				        testo = geom.exportToWkt() 
#				        print testo
				        istr = testo.split(' ')
#				        print istr[0] 
#				        print istr[3]
                        
				        testo = testo.replace("PolygonZ (", "Polygon (")
				        testo = testo.replace(" 0,", ",")
				        testo = testo.replace(" 0)", ")")                                                
				        geometra = ogr.CreateGeometryFromWkt(testo)
				        geometra.Transform(transform)                
				        testoKML = geometra.ExportToKML()
#				        print testoKML
     
				        testoKML = testoKML.replace('<Polygon>',extrusion)
                                   
				        # Se non è un "PolygonZ", aggiungi la coordinata di estrusione                               
				        #  altrimenti, utilizza la sua Z
               
				        if(istr[0] != "PolygonZ" or istr[3] == '0,'):

				           testoKML = testoKML.replace(' ', height)
				           stringazza = height + '</coordinates>'
				           testoKML = testoKML.replace('</coordinates>', stringazza)
                                
#				        print testoKML
				        kml.write (testoKML)
#  NUOVO METODO------------------------------------------------------------ 

                  				        
				        kml.write ('	</Placemark>\n')
				        
				    kml.write ('  </Folder>\n')
					    
				    
				kml.write ('</Folder>\n')

				stringazza = ('<Schema name="%s" id="%s">\n') % (nomeLay, nomeLay)
				kml.write (stringazza)				
				kml.write ('	<SimpleField name="id" type="string"></SimpleField>\n')
				kml.write ('</Schema>\n')		
				
				kml.write ('</Document>\n')        
				kml.write ('</kml>\n')
				kml.close()



#http://cesiumjs.org/Cesium/Build/Apps/CesiumViewer/index.html?src=
				
				if platform.system() == "Windows":            
						os.startfile(out_folder + '/doc.kml')
						
				if platform.system() == "Darwin":			
						os.system("open " + str(out_folder + '/doc.kml'))
						
				if platform.system() == "Linux":            
						os.system("xdg-open " + str(out_folder + '/doc.kml'))		




# GDX_Publisher2 --------------------------------------

def GDX_Publisher2(self, kml):

#				print "GDX_Publisher2 --------------\n"

				mapCanvas = self.iface.mapCanvas()
				
				tumpdir = unicode(QFileInfo(QgsApplication.qgisUserDbFilePath()).path()) + "/python/plugins/gearthview/tump"

				adesso = str(datetime.datetime.now())
				adesso = adesso.replace(" ","_")
				adesso = adesso.replace(":","_")
				adesso = adesso.replace(".","_")        				


				text = mapCanvas.extent().toString()
				text1 = text.replace("," , " ")
				text2 = text1.replace(" : ", ",")
			

# HERE IT DELETES THE OLD IMAGE ------------------------------------
# (if you comment these, images still remain ...  :)
				for filename in glob.glob(str(tumpdir + '/*.png')) :
				   os.remove( str(filename) )
				for filename in glob.glob(str(tumpdir + '/*.pngw')) :
				   os.remove( str(filename) )            
# ------------------------------------------------------------------				

    
				tname = 'ZIPPA'

				out_folder = tumpdir
				

				iface = qgis.utils.iface

				mapRenderer = mapCanvas.mapRenderer()
				mapRect = mapRenderer.extent()
				width = mapRenderer.width()
				height = mapRenderer.height()
				srs = mapRenderer.destinationCrs()

				# create output image and initialize it
				image = QImage(QSize(width, height), QImage.Format_ARGB32)
				image.fill(0)
				
				#adjust map canvas (renderer) to the image size and render
				imagePainter = QPainter(image)
				
				zoom = 1
				target_dpi = int(round(zoom * mapRenderer.outputDpi()))				
				
				mapRenderer.setOutputSize(QSize(width, height), target_dpi)
			
				mapRenderer.render(imagePainter)
				imagePainter.end()

				xN = mapRect.xMinimum()
				yN = mapRect.yMinimum()

				nomePNG = ("QGisView_%lf_%lf_%s") % (xN, yN, adesso)
				
				input_file = out_folder + "/" + nomePNG + ".png"
				
				#Save the image
				image.save(input_file, "png")

				layer = mapCanvas.currentLayer()
				crsSrc = srs  # QgsCoordinateReferenceSystem(layer.crs())   # prendere quello attuale
				crsDest = QgsCoordinateReferenceSystem(4326)  # Wgs84LLH
				xform = QgsCoordinateTransform(crsSrc, crsDest)


				x1 = mapRect.xMinimum()
				y1 = mapRect.yMinimum()
				
				x2 = mapRect.xMaximum()
				y2 = mapRect.yMinimum()

				x3 = mapRect.xMaximum()
				y3 = mapRect.yMaximum()

				x4 = mapRect.xMinimum()
				y4 = mapRect.yMaximum()

				xc = (x1 + x3) / 2.
				yc = (y1 + y3) / 2.	

				pt1 = xform.transform(QgsPoint(x1, y1))				
				pt2 = xform.transform(QgsPoint(x2, y2))
				pt3 = xform.transform(QgsPoint(x3, y3))
				pt4 = xform.transform(QgsPoint(x4, y4))                				

				pt5 = xform.transform(QgsPoint(xc, yc))

				xc = pt5.x()
				yc = pt5.y()

				x1 = pt1.x()
				y1 = pt1.y()
				
				x2 = pt2.x()
				y2 = pt2.y()
				
				x3 = pt3.x()
				y3 = pt3.y()
				
				x4 = pt4.x()
				y4 = pt4.y()
				
#				kml = ""
				
				#Write kml header
				
#				kml = kml + ('<?xml version="1.0" encoding="UTF-8"?>\n')
#				kml = kml + ('<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">\n')				
				kml = kml + ('    <Document>\n')

#				kml = kml + ('    	 <name>QGisView</name>\n')
#				kml = kml + ('    	 <Snippet maxLines="0"></Snippet>\n') 
#				loc = ("    	 <description><![CDATA[http://map.project-osrm.org/?loc=%.7lf,%.7lf&ly=1784084387]]></description>\n") %(yc, xc)
#				kml = kml + (loc)
#				kml = kml + ('	     <open>0</open>\n')

				kml = kml + ('	     <Style id="sh_ylw-pushpin">\n')
				kml = kml + ('	     	<IconStyle>\n')
				kml = kml + ('	     		<scale>1.2</scale>\n')
				kml = kml + ('	     	</IconStyle>\n')
				kml = kml + ('	     	<PolyStyle>\n')
				kml = kml + ('	     		<fill>0</fill>\n')
				kml = kml + ('	     	</PolyStyle>\n')
				kml = kml + ('	     </Style>\n')
				kml = kml + ('	     <Style id="sn_ylw-pushpin">\n')
				kml = kml + ('	     	<PolyStyle>\n')
				kml = kml + ('	     		<fill>0</fill>\n')
				kml = kml + ('	     	</PolyStyle>\n')
				kml = kml + ('	     </Style>\n')
				kml = kml + ('	     <StyleMap id="msn_ylw-pushpin">\n')
				kml = kml + ('	     	<Pair>\n')
				kml = kml + ('	     		<key>normal</key>\n')
				kml = kml + ('	     		<styleUrl>#sn_ylw-pushpin</styleUrl>\n')
				kml = kml + ('	     	</Pair>\n')
				kml = kml + ('	     	<Pair>\n')
				kml = kml + ('	     		<key>highlight</key>\n')
				kml = kml + ('	     		<styleUrl>#sh_ylw-pushpin</styleUrl>\n')
				kml = kml + ('	     	</Pair>\n')
				kml = kml + ('	     </StyleMap>\n')				
				
				kml = kml + ('	     	<Style id="hl">\n')
				kml = kml + ('	     		<IconStyle>\n')
				kml = kml + ('	     			<scale>0.7</scale>\n')
				kml = kml + ('	     			<Icon>\n')
				kml = kml + ('	     				<href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle_highlight.png</href>\n')
				kml = kml + ('	     			</Icon>\n')
				kml = kml + ('	     		</IconStyle>\n')
				kml = kml + ('	     		<LabelStyle>\n')
				kml = kml + ('	     			<scale>0.7</scale>\n')
				kml = kml + ('	     		</LabelStyle>\n')							
				kml = kml + ('	     		<ListStyle>\n')
				kml = kml + ('	     		</ListStyle>\n')
				kml = kml + ('	     	</Style>\n')
				kml = kml + ('	     	<Style id="default">\n')
				kml = kml + ('	     		<IconStyle>\n')
				kml = kml + ('	     			<scale>0.7</scale>\n')
				kml = kml + ('	     			<Icon>\n')
				kml = kml + ('	     				<href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href>\n')
				kml = kml + ('	     			</Icon>\n')
				kml = kml + ('	     		</IconStyle>\n')
				kml = kml + ('	     		<LabelStyle>\n')
				kml = kml + ('	     			<scale>0.7</scale>\n')
				kml = kml + ('	     		</LabelStyle>\n')			
				kml = kml + ('	     		<ListStyle>\n')
				kml = kml + ('	     		</ListStyle>\n')
				kml = kml + ('	     	</Style>\n')
				kml = kml + ('	     	<StyleMap id="default0">\n')
				kml = kml + ('	     		<Pair>\n')
				kml = kml + ('	     			<key>normal</key>\n')
				kml = kml + ('	     			<styleUrl>#default</styleUrl>\n')
				kml = kml + ('	     		</Pair>\n')
				kml = kml + ('	     		<Pair>\n')
				kml = kml + ('	     			<key>highlight</key>\n')
				kml = kml + ('	     			<styleUrl>#hl</styleUrl>\n')
				kml = kml + ('	     		</Pair>\n')
				kml = kml + ('	     	</StyleMap>\n')
				
				
#				kml = kml + ('      <Folder>\n')
				
				xc = (x1 + x3) / 2.
				yc = (y1 + y3) / 2.
				dx = (x3 - x1) * 75000. #100000.
        				
#				kml = kml + ('    		<LookAt>\n')
#				stringazza = ("    		   <longitude>%lf</longitude>\n") %(xc)
#				kml = kml + (stringazza)				
#				stringazza = ("    		   <latitude>%lf</latitude>\n") %(yc)
#				kml = kml + (stringazza)				
#				kml = kml + ('    		   <altitude>0</altitude>\n')
#				kml = kml + ('    		   <heading>0.00</heading>\n')
#				kml = kml + ('    		   <tilt>0</tilt>\n')
#				stringazza = ("    		   <range>%lf</range>\n") %(dx)
#				kml = kml + (stringazza)				
#				kml = kml + ('    		   <gx:altitudeMode>relativeToGround</gx:altitudeMode>\n')
#				kml = kml + ('    		</LookAt>\n')

#				kml = kml + ('      <GroundOverlay>\n')
#				kml = kml + ('    	 <name>QGisView</name>\n')
        				
#				kml = kml + ('    	<Icon>\n')

#				stringazza = ("    	<href>%s.png</href>\n") % (nomePNG)
#				kml = kml + (stringazza)
#				kml = kml + ('    		<viewBoundScale>1.0</viewBoundScale>\n')
#				kml = kml + ('    	</Icon>\n')
#				kml = kml + ('    	<gx:LatLonQuad>\n')
#				kml = kml + ('    		<coordinates>\n')

#				stringazza =    ("%.7lf,%.7lf,0 %.7lf,%.7lf,0 %.7lf,%.7lf,0 %.7lf,%.7lf,0\n") % (x1, y1, x2, y2, x3, y3, x4, y4)        		
#				kml = kml + (stringazza)				

#				kml = kml + ('    		</coordinates>\n')
#				kml = kml + ('    	</gx:LatLonQuad>\n')
#				kml = kml + ('    </GroundOverlay>\n')

#				#Write kml footer
#				kml = kml + ('</kml>\n')
#				#Close kml file
#				kml.close()



				#Export tfw-file
#				xScale = (mapRect.xMaximum() - mapRect.xMinimum()) /  image.width()
#				yScale = (mapRect.yMaximum() - mapRect.yMinimum()) /  image.height()

							
#				f = open(out_folder + "/" + nomePNG	+ ".pngw", 'w')				
#				f.write(str(xScale) + '\n')
#				f.write(str(0) + '\n')
#				f.write(str(0) + '\n')
#				f.write('-' + str(yScale) + '\n')
#				f.write(str(mapRect.xMinimum()) + '\n')
#				f.write(str(mapRect.yMaximum()) + '\n')
#				f.write(str(mapRect.xMaximum()) + '\n')
#				f.write(str(mapRect.yMinimum()))				
#				f.close()
			

				nomeLay = "gearthview" 	 # foo default name		


#  Adesso scrivo il vettoriale
#  Prendo il sistema di riferimento del Layer selezionato ------------------
        
        
				layer = mapCanvas.currentLayer()
				if layer:
				  if layer.type() == layer.VectorLayer:				

				    name = layer.source();
				    nomeLayer = layer.name()
				    nomeLay   = nomeLayer.replace(" ","_")

				    kml = kml + ('    <Folder>\n')
				    stringazza =   ('			<name>%s</name>\n') % (nomeLay)
				    kml = kml +  (stringazza)     				          
      				    
				    crsSrc = layer.crs();

				    crsDest = QgsCoordinateReferenceSystem(4326)  # Wgs84LLH
				    xform = QgsCoordinateTransform(crsSrc, crsDest)


				    boundBox = mapCanvas.extent() 
                
				    xMin = float(boundBox.xMinimum())
				    yMin = float(boundBox.yMinimum())

				    xMax = float(boundBox.xMaximum())                
				    yMax = float(boundBox.yMaximum())
				    
				    
				    crs2 = mapCanvas.mapRenderer().destinationCrs()
				    crsSrc2  = QgsCoordinateReferenceSystem(crs2.authid())   
				    crsDest2 = QgsCoordinateReferenceSystem(layer.crs())   
				    xform2   = QgsCoordinateTransform(crsSrc2, crsDest2)
                              
				    pt0 = xform2.transform(QgsPoint(xMin, yMin))
				    pt1 = xform2.transform(QgsPoint(xMax, yMax))
				    
				    rect = QgsRectangle(pt0, pt1)
				    


				    rq = QgsFeatureRequest(rect)

				    iter = layer.getFeatures(rq)				    
				    for feat in iter:
				    
				      nele = feat.id()

              				      
				      # fetch geometry
				      geom = feat.geometry()
				       # show some information about the feature

#				      print ("GeomType: %d") %(geom.type())
				      
				      if geom.type() == QGis.Point:
				        elem = geom.asPoint()
				        x1 = elem.x()
				        y1 = elem.y()

				        pt1 = xform.transform(QgsPoint(x1, y1))

				        kml = kml +  ('	<Placemark>\n')
				        
				        stringazza =   ('		<name>%s</name>\n') % (nele)
				        kml = kml +  (stringazza)	
                			        
				        kml = kml +  ('	<styleUrl>#default0</styleUrl>\n')

# DESCRIPTION DATA-----------
				        kml = kml +  ('	<Snippet maxLines="0"></Snippet>\n')
				        kml = kml +  ('	<description><![CDATA[\n')				        
				        kml = kml +  ('<html><body><table border="1">\n')
				        kml = kml +  ('<tr><th>Field Name</th><th>Field Value</th></tr>\n')
 
 # Prendo il contenuto dei campi -------------
				        fff = feat.fields()
				        num = fff.count()                
				        iii = -1
				        for f in layer.pendingFields(): 				        
				           iii = iii + 1
				           
				           stringazza = ('<tr><td>%s</td><td>%s</td></tr>\n') %(f.name(),feat[iii])

				           kml = kml +  (stringazza)					           
               	
				        kml = kml +  ('</table></body></html>\n')
				        kml = kml +  (']]></description>\n')
				        
# DESCRIPTION DATA-----------

				        
				        kml = kml +  ('		<Point>\n')
				        kml = kml +  ('			<gx:drawOrder>1</gx:drawOrder>\n')
				        stringazza =   ('			<coordinates>%.7lf,%.7lf</coordinates>\n') % (pt1.x(), pt1.y())
				        kml = kml +  (stringazza)                                  
				        kml = kml +  ('		</Point>\n')
				        kml = kml +  ('	</Placemark>\n')


				      elif geom.type() == QGis.Line:

				        kml = kml +  ('	<Placemark>\n')
                	
				        stringazza =   ('		<name>%s</name>\n') % (nele)
				        kml = kml +  (stringazza)

# DESCRIPTION DATA-----------
				        kml = kml +  ('	<Snippet maxLines="0"></Snippet>\n')
				        kml = kml +  ('	<description><![CDATA[\n')				        
				        kml = kml +  ('<html><body><table border="1">\n')
				        kml = kml +  ('<tr><th>Field Name</th><th>Field Value</th></tr>\n')
 
 # Prendo il contenuto dei campi -------------
				        fff = feat.fields()
				        num = fff.count()                
				        iii = -1
				        for f in layer.pendingFields(): 				        
				           iii = iii + 1
				           
				           stringazza = ('<tr><td>%s</td><td>%s</td></tr>\n') %(f.name(),feat[iii])

				           kml = kml +  (stringazza)					           
               	
				        kml = kml +  ('</table></body></html>\n')
				        kml = kml +  (']]></description>\n')
				        
				                        			        
				        kml = kml +  ('		<LineString>\n')
				        kml = kml +  ('			<tessellate>1</tessellate>\n')
				        kml = kml +  ('			<coordinates>\n')
				        
				        elem = geom.asPolyline()
				         
				        for p1 in elem:
				          x1,y1 = p1.x(),p1.y()

				          pt1 = xform.transform(QgsPoint(x1, y1))
                                               
				          stringazza =   ('%.7lf,%.7lf \n') % (pt1.x(), pt1.y())
				          kml = kml +  (stringazza)
				          
				        kml = kml +  ('			</coordinates>\n')                   
				        kml = kml +  ('		</LineString>\n')
				        kml = kml +  ('	</Placemark>\n')


				      elif geom.type() == QGis.Polygon:

				        kml = kml +  ('	<Placemark>\n')
				        stringazza =   ('		<name>%s</name>\n') % (nele)
				        kml = kml +  (stringazza)				        
				        kml = kml +  ('		<styleUrl>#msn_style</styleUrl>\n')
				        
# DESCRIPTION DATA-----------
				        kml = kml +  ('	<Snippet maxLines="0"></Snippet>\n')
				        kml = kml +  ('	<description><![CDATA[\n')				        
				        kml = kml +  ('<html><body><table border="1">\n')
				        kml = kml +  ('<tr><th>Field Name</th><th>Field Value</th></tr>\n')
 
 # Prendo il contenuto dei campi -------------
				        fff = feat.fields()
				        num = fff.count()                
				        iii = -1
				        for f in layer.pendingFields(): 				        
				           iii = iii + 1
				           
				           stringazza = ('<tr><td>%s</td><td>%s</td></tr>\n') %(f.name(),feat[iii])

				           kml = kml +  (stringazza)					           
               	
				        kml = kml +  ('</table></body></html>\n')
				        kml = kml +  (']]></description>\n')
				        
# DESCRIPTION DATA-----------				        
				        
                				        
				        kml = kml +  ('		<Polygon>\n')
				        kml = kml +  ('			<tessellate>1</tessellate>\n')
				        kml = kml +  ('     <outerBoundaryIs>\n')
				        kml = kml +  ('        <LinearRing>\n')
				        kml = kml +  ('         <coordinates>\n')
              
				        elem = geom.asPolygon()

# h ttp://qgis.spatialthoughts.com/2012/11/tip-count-number-of-vertices-in-layer.html				        
				        if geom.isMultipart():
				          print "MULTIPART !!!"
				          elem = geom.asMultiPolygon()

				          for polygon in elem:
				             for ring in polygon:
				                print ("Pezzo con %d vertici") %(len(ring))

                     
                            			        			        
				        for iii in range (len(elem)):

				          if (iii == 1):				          
				            kml = kml +  ('         </coordinates>\n')
				            kml = kml +  ('         </LinearRing>\n')
				            kml = kml +  ('         </outerBoundaryIs>\n')
				            kml = kml +  ('         <innerBoundaryIs>\n')
				            kml = kml +  ('         <LinearRing>\n')
				            kml = kml +  ('         <coordinates>\n')

				          if (iii > 1):				          
				            kml = kml +  ('         </coordinates>\n')
				            kml = kml +  ('         </LinearRing>\n')
				            kml = kml +  ('         </innerBoundaryIs>\n')
				            kml = kml +  ('         <innerBoundaryIs>\n')
				            kml = kml +  ('         <LinearRing>\n')
				            kml = kml +  ('         <coordinates>\n')	
				        
				          for jjj in range (len(elem[iii])):
				                         
				            x1,y1 = elem[iii][jjj][0], elem[iii][jjj][1]

				            if geom.isMultipart():
				               pt1 = xform.transform(x1)
				            else:				            
				               pt1 = xform.transform(QgsPoint(x1, y1))
                          
				            stringazza =   ('%.7lf,%.7lf,0 \n') % (pt1.x(), pt1.y())
				            kml = kml +  (stringazza)

				        if (iii == 0):
				           kml = kml +  ('         </coordinates>\n')
				           kml = kml +  ('        </LinearRing>\n')
				           kml = kml +  ('     </outerBoundaryIs>\n')
				           kml = kml +  ('   </Polygon>\n')

				        if (iii > 0):
				           kml = kml +  ('         </coordinates>\n')
				           kml = kml +  ('        </LinearRing>\n')
				           kml = kml +  ('     </innerBoundaryIs>\n')
				           kml = kml +  ('   </Polygon>\n')	
                  				        
				        kml = kml +  ('	</Placemark>\n')
				        
				    kml = kml +  ('  </Folder>\n')
					    
				    
#				kml = kml +  ('</Folder>\n')

#				stringazza = ('<Schema name="%s" id="%s">\n') % (nomeLay, nomeLay)
#				kml = kml +  (stringazza)				
#				kml = kml +  ('	<SimpleField name="id" type="string"></SimpleField>\n')
#				kml = kml +  ('</Schema>\n')		
				
				kml = kml +  ('</Document>\n')        
				kml = kml +  ('</kml>\n')
                
				return 	kml			
	

# ----------------------------------------------------
class gearthview:


    def __init__(self, iface):

        global serverStarted
        serverStarted = 0
        
        global lat, lon
        lat  = 0.00
        lon  = 0.00

        # Save reference to the QGIS interface
        self.iface = iface
        # Create the dialog and keep reference
        self.dlg = gearthviewDialog()
        # initialize plugin directory
        self.plugin_dir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "python/plugins/gearthview"
        # initialize locale
        localePath = ""

        if QGis.QGIS_VERSION_INT < 10900:        
           locale = QSettings().value("locale/userLocale").toString()[0:2]
        else:
           locale = QSettings().value("locale/userLocale")[0:2]

        if QFileInfo(self.plugin_dir).exists():
            localePath = self.plugin_dir + "/i18n/gearthview_" + locale + ".qm"

        if QFileInfo(localePath).exists():
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


# ----------------------------------------------------
###modified by Aldo Scorza (start)
    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(QIcon(self.plugin_dir + "/iconG.png"),QCoreApplication.translate(u"GEarthView", "GEarthView"), self.iface.mainWindow())
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)
        # connect the action to the run method

        self.PasteFromGEaction = QAction(QIcon(self.plugin_dir + "/iconQG.png"),QCoreApplication.translate(u"GEarthView", "PasteFromGE"), self.iface.mainWindow())
        QObject.connect(self.PasteFromGEaction, SIGNAL("triggered()"), self.PasteFromGE)


#        self.QRcodingAction= QAction(QIcon(self.plugin_dir + "/iconQR.png"), QCoreApplication.translate(u"&GEarthView", "GE_QRcoding"), self.iface.mainWindow())
#        QObject.connect(self.QRcodingAction, SIGNAL("triggered()"), self.startQrCoding)

#        self.QGEarthAction= QAction(QIcon(self.plugin_dir + "/iconQG.png"), QCoreApplication.translate(u"&GEarthView", "PointFromGE"), self.iface.mainWindow())
#        QObject.connect(self.QGEarthAction, SIGNAL("triggered()"), self.QGEarth)        

        self.aboutAction= QAction(QIcon(self.plugin_dir + "/iconA.png"), QCoreApplication.translate(u"&GEarthView", "About"), self.iface.mainWindow())
        QObject.connect(self.aboutAction, SIGNAL("triggered()"), self.about)

        
        self.toolBar = self.iface.mainWindow().findChild(QObject, 'Geodrinx')
        if not self.toolBar :
          self.toolBar = self.iface.addToolBar("Geodrinx")
          self.toolBar.setObjectName("Geodrinx")

        self.GECombo = QMenu(self.iface.mainWindow())
        self.GECombo.addAction(self.action)
        self.GECombo.addAction(self.PasteFromGEaction)

#        self.GECombo.addAction(self.QRcodingAction)        
#        self.GECombo.addAction(self.QGEarthAction)

        self.GECombo.addAction(self.aboutAction)
        
        self.toolButton = QToolButton()
        self.toolButton.setMenu( self.GECombo )
        self.toolButton.setDefaultAction( self.action )
        self.toolButton.setPopupMode( QToolButton.InstantPopup )
        
        self.toolBar.addWidget(self.toolButton)
        self.GECombo.setToolTip("GEarthView")         
        
        # Add toolbar button and menu item

        self.iface.addPluginToWebMenu(u"&GEarthView", self.action)
        
        self.iface.addPluginToWebMenu(u"GEarthView", self.PasteFromGEaction)

#        self.iface.addPluginToWebMenu(u"&GEarthView", self.QRcodingAction)

#        self.iface.addPluginToWebMenu(u"&GEarthView", self.QGEarthAction)        
        
        self.iface.addPluginToWebMenu(u"&GEarthView", self.aboutAction) 

# ---------------------------------------------------------
    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginWebMenu(u"&GEarthView", self.action)
        self.iface.removePluginWebMenu(u"&GEarthView", self.PasteFromGEaction)
        self.iface.removePluginWebMenu(u"&GEarthView", self.aboutAction)

#        QObject.disconnect(self.action)
#        QObject.disconnect(self.PasteFromGEaction)
#        QObject.disconnect(self.aboutAction)
#        self.toolBar.setVisible( false )
        #virtual void QgisInterface::removeToolBarIcon 	( 	QAction *  	qAction	) 	
        #self.toolBar.removeAction(self.action)
        #self.toolBar.removeAction(self.PasteFromGEaction)
        #self.toolBar.removeAction(self.aboutAction)
        #del self.GECombo
        self.toolBar.removeAction(self.action)
        if not self.toolBar.actions() :
          del self.toolBar       
        #self.iface.removeToolBarIcon(self.action)

###modified by Aldo Scorza (end)\


# ----------------------------------------------------
    def PasteFromGE(self):


        mapCanvas = self.iface.mapCanvas()
           
        copyText = QApplication.clipboard().text()


#---------       Fix bug paste multiholes  -------------------------

        copyText = copyText.replace("\t\t\t\t</LinearRing>\n\t\t\t\t<LinearRing>", "\t\t\t\t</LinearRing>\n\t\t\t</innerBoundaryIs>\n\t\t\t<innerBoundaryIs>\n\t\t\t\t<LinearRing>")

        copyText = copyText.replace("\t\t\t\t\t</LinearRing>\n\t\t\t\t\t<LinearRing>", "\t\t\t\t</LinearRing>\n\t\t\t</innerBoundaryIs>\n\t\t\t<innerBoundaryIs>\n\t\t\t\t<LinearRing>")

#---------       Fix bug paste multiholes  -------------------------

#        print copyText

        tumpdir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/gearthview/tump"

#<Point>         GEKml_Points.kml
#<LineString>    GEKml_Lines.kml
#<Polygon>       GEKml_Polygons.kml


        # Tolgo i livelli precedenti
#        QgsMapLayerRegistry.instance().removeMapLayer("GEKml_Points")        
#        QgsMapLayerRegistry.instance().removeMapLayer("GEKml_Lines")        
#        QgsMapLayerRegistry.instance().removeMapLayer("GEKml_Polygons")

        for iLayer in range(mapCanvas.layerCount()):
          layer = mapCanvas.layer(iLayer)
          if (layer.name() == "GEKml_Points") or (layer.name() == "GEKml_Lines") or (layer.name() == "GEKml_Polygons"):
             QgsMapLayerRegistry.instance().removeMapLayer(layer.id())
        

        GEKml_Points   = copyText.find("<Point>")
        GEKml_Lines    = copyText.find("<LineString>")
        GEKml_Polygons = copyText.find("<Polygon>")        


        if (GEKml_Polygons > 0):        

           salvalo2 = codecs.open(tumpdir + "/GEKml_Polygons.kml", 'w', encoding='utf-8')
           salvalo2.write (copyText)

           salvalo2.close()                

           vlayer = QgsVectorLayer(tumpdir + "/GEKml_Polygons.kml", "GEKml_Polygons", "ogr")
           QgsMapLayerRegistry.instance().addMapLayer(vlayer)


        if (GEKml_Lines > 0):        

           salvalo2 = codecs.open(tumpdir + "/GEKml_Lines.kml", 'w', encoding='utf-8')
           salvalo2.write (copyText)

           salvalo2.close()                

           vlayer = QgsVectorLayer(tumpdir + "/GEKml_Lines.kml", "GEKml_Lines", "ogr")
           QgsMapLayerRegistry.instance().addMapLayer(vlayer)


        if (GEKml_Points > 0):        

           salvalo2 = codecs.open(tumpdir + "/GEKml_Points.kml", 'w', encoding='utf-8')
           salvalo2.write (copyText)

           salvalo2.close()                

           vlayer = QgsVectorLayer(tumpdir + "/GEKml_Points.kml", "GEKml_Points", "ogr")
           QgsMapLayerRegistry.instance().addMapLayer(vlayer)   


#  Dalla versione 2.14  QGIS permette di esportare anche la coordinata Z ---

        if QGis.QGIS_VERSION_INT >= 21400:

           giaFatto = 0
           if (GEKml_Polygons > 0):
              ret = P3dPoints_Write(self, "GEKml_Polygons")
              giaFatto = 1

           if (GEKml_Lines > 0 and giaFatto == 0):
              ret = P3dPoints_Write(self, "GEKml_Lines")
              giaFatto = 1
              
           if (GEKml_Points > 0 and giaFatto == 0):
              ret = P3dPoints_Write(self, "GEKml_Points")
              giaFatto = 1              

           nomecsv = tumpdir + "/_3dPointsExport/GEKml_3dPoints.csv"
           nomecsv.replace("\\", "/") 
           uri = """file:///""" + nomecsv + """?"""
           uri += """type=csv&"""
           uri += """trimFields=no&"""
           uri += """xField=X&"""
           uri += """yField=Y&"""
           uri += """spatialIndex=yes&"""
           uri += """subsetIndex=no&"""
           uri += """watchFile=no&"""
           uri += """crs=epsg:4326"""

           for iLayer in range(mapCanvas.layerCount()):
               layer = mapCanvas.layer(iLayer)
               if (layer): 
                   if layer.name() == "GEKml_3dPoints":
                     QgsMapLayerRegistry.instance().removeMapLayer(layer.id())                  
                   if layer.name() == "GEKml_Extrusions":
                     QgsMapLayerRegistry.instance().removeMapLayer(layer.id())
                       
           vlayer = QgsVectorLayer(uri, "GEKml_3dPoints", "delimitedtext")

           QgsMapLayerRegistry.instance().addMapLayer(vlayer)

           nomeqml = tumpdir + "/_3dPointsExport/GEKml_3dPoints.qml"            
           nomeqml.replace("\\", "/")

           result = vlayer.loadNamedStyle(nomeqml)            

# FINE  QGis.QGIS_VERSION_INT >= 21400 ----------------------

                                             
        vlayer.triggerRepaint()
            
        mapCanvas.refresh()   


# ----------------------------------------------------
#    def startQrCoding(self):
#				startGeoDrink_Server(self) 

				    

#  ------- OLD CODE ------------------------------------------------------
#				webServerDir = unicode(QFileInfo(QgsApplication.qgisUserDbFilePath()).path()) + "python/plugins/gearthview/_WebServer/"
#				f = open(webServerDir + 'QGEarth.log', 'r')
#				strings = f.readlines()
#				west       = float(strings[0])
#				south      = float(strings[1])
#				east       = float(strings[2])
#				north      = float(strings[3])
#				lon        = float(strings[4])
#				lat        = float(strings[5])
##				qrCodeUrl  = strings[6]
##				img = qrcode.make('Some data here')
##				print img
#				canvas = self.iface.mapCanvas()
#				mapRenderer = canvas.mapRenderer()
#				srs = mapRenderer.destinationCrs()				
#				crsSrc = QgsCoordinateReferenceSystem(4326)
#				crsDest = QgsCoordinateReferenceSystem(srs) 
#				xform = QgsCoordinateTransform(crsSrc, crsDest)
#				pt1 = xform.transform(QgsPoint(west, south))
#				pt2 = xform.transform(QgsPoint(east, north))        							
#				box = QgsRectangle(pt1.x(), pt1.y(), pt2.x(), pt2.y())
#				self.iface.mapCanvas().setExtent(box)
#				self.iface.mapCanvas().refresh()
#				f.close() 
#  ------- OLD CODE ------------------------------------------------------				
	           
               

# ----------------------------------------------------
    def about(self):
        infoString = QCoreApplication.translate('GEarthView', "GEarthView Plugin<br>This plugin displays QGis view into Google Earth.<br>Author:  Bob MaX (aka: geodrinx)<br>Mail: <a href=\"mailto:geodrinx@gmail.com\">geodrinx@gmail.com</a><br>Web: <a href=\"http://exporttocanoma.blogspot.it\">exporttocanoma.blogspot.it</a><br></b>.")
#        infoString = QCoreApplication.translate('GEarthView', "GEarthView Plugin<br>This plugin displays QGis view into Google Earth.<br>Author:  Bob MaX (aka: geodrinx)<br>Mail: <a href=\"mailto:geodrinx@gmail.com\">geodrinx@gmail.com</a><br>Web: <a href=\"http://exporttocanoma.blogspot.it\">exporttocanoma.blogspot.it</a><br>" + "<b>Do yo like this plugin? Please consider <a href=\"https://www.paypal.com\">donating</a></b>.")    
#        infoString = "GEarthView plugin \n\ndisplays QGis view into Google Earth\n\ntested on Windows and MacOSX\n\ngeodrinx@gmail.com"
        QMessageBox.information(self.iface.mainWindow(), "About GEarthView plugin",infoString)

#    def unload(self):
#        # Remove the plugin menu item and icon
#        self.iface.removePluginWebMenu(u"&GEarthView", self.action)
##        self.iface.removePluginMenu(u"&GEarthView", self.PasteFromGEaction)        
#        self.iface.removeToolBarIcon(self.action)

    def doPaste(self,text):
        text = str(text)
        QApplication.clipboard().setText(text)
        msg = "Copied text: "+text[:30]
        if len(text) > 30:
          msg = msg + "... ("+str(len(text))+" chars)"
        self.iface.mainWindow().statusBar().showMessage(msg)

# ------------------------------------------------------------------
    def QGEarth(self):
        QGEarth_addPoint(self)

# ------------------------------------------------------------------
    # run method that performs all the real work
    def run(self):

        webServerDir = unicode(QFileInfo(QgsApplication.qgisUserDbFilePath()).path()) + "/python/plugins/gearthview/_WebServer/"

        if ( serverStarted == 0) :
           startGeoDrink_Server(self)
        else:
#           if platform.system() == "Windows":            
#              os.startfile(webServerDir + 'QGIS_link.kmz')
#
#           if platform.system() == "Darwin":			
#              os.system("open " + str(webServerDir + 'QGIS_link.kmz'))
#
#           if platform.system() == "Linux":            
#              os.system("xdg-open " + str(webServerDir + 'QGIS_link.kmz'))
#
           GDX_Publisher(self)


        # EndIf

	
