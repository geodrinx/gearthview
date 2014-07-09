# -*- coding: utf-8 -*-
"""
/***************************************************************************
 gearthview
                                 A QGIS plugin
 GEarth View
                              -------------------
        begin                : 2013-06-22
        copyright            : (C) 2013 by geodrinx
        email                : geodrinx@gmail.com
        
        history              :
                                 
          Plugin Creation      Roberto Angeletti
          
          menu and icons         Aldo Scorza
                             
 ***************************************************************************/

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


# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from gearthviewdialog import gearthviewDialog

if QGis.QGIS_VERSION_INT < 10900:
    from osgeo import gdal
    from osgeo import gdalnumeric
    from osgeo import gdalconst



class gearthview:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # Create the dialog and keep reference
        self.dlg = gearthviewDialog()
        # initialize plugin directory
        self.plugin_dir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/gearthview"
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

###modified by Aldo Scorza (start)
    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(QIcon(self.plugin_dir + "/iconG.png"),QCoreApplication.translate(u"GEarthView", "GEarthView"), self.iface.mainWindow())
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)
        # connect the action to the run method

        self.PasteFromGEaction = QAction(QIcon(self.plugin_dir + "/iconP.png"),QCoreApplication.translate(u"GEarthView", "PasteFromGE"), self.iface.mainWindow())
        QObject.connect(self.PasteFromGEaction, SIGNAL("triggered()"), self.PasteFromGE)

        self.aboutAction= QAction(QIcon(self.plugin_dir + "/iconA.png"), QCoreApplication.translate(u"&GEarthView", "About"), self.iface.mainWindow())
        QObject.connect(self.aboutAction, SIGNAL("triggered()"), self.about)


        
        self.toolBar = self.iface.mainWindow().findChild(QObject, 'Geodrinx')
        if not self.toolBar :
          self.toolBar = self.iface.addToolBar("Geodrinx")
          self.toolBar.setObjectName("Geodrinx")

        self.GECombo = QMenu(self.iface.mainWindow())
        self.GECombo.addAction(self.action)
        self.GECombo.addAction(self.PasteFromGEaction)
        self.GECombo.addAction(self.aboutAction)
        
        self.toolButton = QToolButton()
        self.toolButton.setMenu( self.GECombo )
        self.toolButton.setDefaultAction( self.action )
        self.toolButton.setPopupMode( QToolButton.InstantPopup )
        
        self.toolBar.addWidget(self.toolButton)
        self.GECombo.setToolTip("GEarthView")         
        
        # Add toolbar button and menu item
        #self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToWebMenu(u"&GEarthView", self.action)

        #------PasteFromGEaction---------------------------------
    
        #self.PasteFromGEaction = QAction(
        #    QIcon(":/plugins/gearthview/icon2.png"), 
        #    QCoreApplication.translate(u"GEarthView", "PasteFromGE"), self.iface.mainWindow())
        #QObject.connect(self.PasteFromGEaction, SIGNAL("activated()"), self.PasteFromGE)
         
        self.iface.addPluginToWebMenu(u"GEarthView", self.PasteFromGEaction)
        
        
        #------ABOUT---------------------------------
           
        #self.aboutAction=QAction(QIcon(":/gearthview/about_icon.png"), QCoreApplication.translate(u"&GEarthView", "&About"), self.iface.mainWindow())
        #QObject.connect(self.aboutAction, SIGNAL("activated()"), self.about)
         
        self.iface.addPluginToWebMenu(u"&GEarthView", self.aboutAction)        

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

    def PasteFromGE(self):
   
        copyText = QApplication.clipboard().text()

#        print("CLIPBOARD: %s\n") %(copyText)

        tempdir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "python/plugins/gearthview/temp"
        
#        salvalo2 = open(tempdir + "/doc2.kml",'w')
        salvalo2 = codecs.open(tempdir + "/doc2.kml", 'w', encoding='utf-8')
        salvalo2.write (copyText)

        salvalo2.close()                

        vlayer = QgsVectorLayer(tempdir + "/doc2.kml", "GEKml", "ogr")

        trovato = 0
        for iLayer in range(self.iface.mapCanvas().layerCount()):
          layer = self.iface.mapCanvas().layer(iLayer)
          if layer.name() == "GEKml":
            trovato = 1

        if (trovato == 0):        
          QgsMapLayerRegistry.instance().addMapLayer(vlayer)   


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

    # run method that performs all the real work
    def run(self):

				tempdir = unicode(QFileInfo(QgsApplication.qgisUserDbFilePath()).path()) + "/python/plugins/gearthview/temp"

				adesso = str(datetime.datetime.now())
				adesso = adesso.replace(" ","_")
				adesso = adesso.replace(":","_")
				adesso = adesso.replace(".","_")        				

#				print "adesso: <%s>\n" %(adesso)

# Prendo le coordinate della finestra attuale---------------------------------------
# 13.5702225179249876,41.2134192420407501 : 13.5768356834183166,41.2182110366311107
				text = self.iface.mapCanvas().extent().toString()
				text1 = text.replace("," , " ")
				text2 = text1.replace(" : ", ",")
				the_filter = "bbox($geometry, geomFromWKT ( 'LINESTRING(" + text2 + ")'))"
				self.doPaste(the_filter) 				

# HERE IT DELETES THE OLD IMAGE ------------------------------------
# (if you comment these, images still remain ...  :)
				for filename in glob.glob(str(tempdir + '/*.png')) :
				   os.remove( str(filename) )
				for filename in glob.glob(str(tempdir + '/*.pngw')) :
				   os.remove( str(filename) )            
# ------------------------------------------------------------------				

    
				tname = 'ZIPPA'

				out_folder = tempdir
				
				kml = codecs.open(out_folder + '/doc.kml', 'w', encoding='utf-8')
#				kml=open(out_folder + '/doc.kml', 'w')
				#

				iface = qgis.utils.iface
				canvas = iface.mapCanvas()
				mapRenderer = canvas.mapRenderer()
				mapRect = mapRenderer.extent()
				width = mapRenderer.width()
				height = mapRenderer.height()
				srs = mapRenderer.destinationCrs()

				# create output image and initialize it
				image = QImage(QSize(width, height), QImage.Format_ARGB32)
#				image.fill(qRgb(255,255,255))
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

				layer = iface.mapCanvas().currentLayer()
				crsSrc = srs  # QgsCoordinateReferenceSystem(layer.crs())   # prendere quello attuale
				crsDest = QgsCoordinateReferenceSystem(4326)  # Wgs84LLH
				xform = QgsCoordinateTransform(crsSrc, crsDest)

#				print ("%s\n") %(crsSrc.proj4String())

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

				loc = ("    	 <description>http://map.project-osrm.org/?loc=%.9lf,%.9lf</description>\n") %(yc, xc)

				kml.write(loc)
#
				
				
#				kml.write('    	 <description>http://map.project-osrm.org/?hl=it&loc=45.989486,12.778154&loc=45.985624,12.781076&z=16&center=45.984058,12.774417&alt=0&df=0&re=0&ly=-940622518</description>\n')
				
				kml.write('	     <open>0</open>\n')

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
				
				
				
				
				kml.write('      <Folder>\n')
				
				xc = (x1 + x3) / 2.
				yc = (y1 + y3) / 2.
				dx = (x3 - x1) * 75000. #100000.
        				
				kml.write('    		<LookAt>\n')
				stringazza = ("    		   <longitude>%lf</longitude>\n") %(xc)
				kml.write(stringazza)				
				stringazza = ("    		   <latitude>%lf</latitude>\n") %(yc)
				kml.write(stringazza)				
				kml.write('    		   <altitude>0</altitude>\n')
				kml.write('    		   <heading>0.00</heading>\n')
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

				stringazza =    ("%.9lf,%.9lf,0 %.9lf,%.9lf,0 %.9lf,%.9lf,0 %.9lf,%.9lf,0\n") % (x1, y1, x2, y2, x3, y3, x4, y4)        		
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
        
        
				layer = self.iface.mapCanvas().currentLayer()
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

				    boundBox = iface.mapCanvas().extent() 
                
				    xMin = float(boundBox.xMinimum())
				    yMin = float(boundBox.yMinimum())

				    xMax = float(boundBox.xMaximum())                
				    yMax = float(boundBox.yMaximum())
				    
				    
				    crs2 = self.iface.mapCanvas().mapRenderer().destinationCrs()
				    crsSrc2  = QgsCoordinateReferenceSystem(crs2.authid())   
				    crsDest2 = QgsCoordinateReferenceSystem(layer.crs())   
				    xform2   = QgsCoordinateTransform(crsSrc2, crsDest2)
                              
				    pt0 = xform2.transform(QgsPoint(xMin, yMin))
				    pt1 = xform2.transform(QgsPoint(xMax, yMax))
				    
				    rect = QgsRectangle(pt0, pt1)
				    
#----------------------------------------------------------------------------

#				    rq = QgsFeatureRequest(iface.mapCanvas().extent())

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
				        
# DESCRIPTION DATA-----------

# EXTENDED DATA -------------			
#				        stringazza =   ('		<ExtendedData><SchemaData schemaUrl="#%s">\n') % (nomeLay)
#				        kml.write (stringazza)                 	        
#
##				        stringazza = ('				<SimpleData name="id">%d</SimpleData>\n') %(nele)
##				        kml.write (stringazza)
#
## Prendo il contenuto dei campi -------------
#				        fff = feat.fields()
#				        num = fff.count()                
#				        iii = -1
#				        for f in layer.pendingFields(): 				        
#				           iii = iii + 1
#				           
#				           stringazza = ('				<SimpleData name="%s">%s</SimpleData>\n') %(f.name(),feat[iii])
#
#				           kml.write (stringazza)					           
#                				        
#				        kml.write ('		</SchemaData></ExtendedData>\n')				        
# EXTENDED DATA -------------
				        
				        kml.write ('		<Point>\n')
				        kml.write ('			<gx:drawOrder>1</gx:drawOrder>\n')
				        stringazza =   ('			<coordinates>%.9lf,%.9lf</coordinates>\n') % (pt1.x(), pt1.y())
				        kml.write (stringazza)                                  
				        kml.write ('		</Point>\n')
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
				        
# DESCRIPTION DATA-----------
				        
# EXTENDED DATA -------------			
#				        stringazza =   ('		<ExtendedData><SchemaData schemaUrl="#%s">\n') % (nomeLay)
#				        kml.write (stringazza)                 	        
#
##				        stringazza = ('				<SimpleData name="id">%d</SimpleData>\n') %(nele)
##				        kml.write (stringazza)
#
## Prendo il contenuto dei campi -------------
#				        fff = feat.fields()
#				        num = fff.count()                
#				        iii = -1
#				        for f in layer.pendingFields(): 				        
#				           iii = iii + 1
#				           
#				           stringazza = ('				<SimpleData name="%s">%s</SimpleData>\n') %(f.name(),feat[iii])
#
#				           kml.write (stringazza)					           
#                				        
#				        kml.write ('		</SchemaData></ExtendedData>\n')				        
# EXTENDED DATA -------------
                			        
				        kml.write ('		<LineString>\n')
				        kml.write ('			<tessellate>1</tessellate>\n')
				        kml.write ('			<coordinates>\n')
				        
				        elem = geom.asPolyline()
				         
				        for p1 in elem:
				          x1,y1 = p1.x(),p1.y()

				          pt1 = xform.transform(QgsPoint(x1, y1))
                                               
				          stringazza =   ('%.9lf,%.9lf \n') % (pt1.x(), pt1.y())
				          kml.write (stringazza)
				          
				        kml.write ('			</coordinates>\n')                   
				        kml.write ('		</LineString>\n')
				        kml.write ('	</Placemark>\n')


				      elif geom.type() == QGis.Polygon:

				        kml.write ('	<Placemark>\n')
				        stringazza =   ('		<name>%s</name>\n') % (nele)
				        kml.write (stringazza)				        
				        kml.write ('		<styleUrl>#msn_ylw-pushpin</styleUrl>\n')
				        
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
				        
# DESCRIPTION DATA-----------				        
				        
# EXTENDED DATA -------------			
#				        stringazza =   ('		<ExtendedData><SchemaData schemaUrl="#%s">\n') % (nomeLay)
#				        kml.write (stringazza)                 	        
#
##				        stringazza = ('				<SimpleData name="id">%d</SimpleData>\n') %(nele)
##				        kml.write (stringazza)
#
## Prendo il contenuto dei campi -------------
#				        fff = feat.fields()
#				        num = fff.count()                
#				        iii = -1
#				        for f in layer.pendingFields(): 				        
#				           iii = iii + 1
#				           
#				           stringazza = ('				<SimpleData name="%s">%s</SimpleData>\n') %(f.name(),feat[iii])
#
#				           kml.write (stringazza)					           
#                				        
#				        kml.write ('		</SchemaData></ExtendedData>\n')				        
# EXTENDED DATA -------------
                				        
				        kml.write ('		<Polygon>\n')
				        kml.write ('			<tessellate>1</tessellate>\n')
				        kml.write ('     <outerBoundaryIs>\n')
				        kml.write ('        <LinearRing>\n')
				        kml.write ('         <coordinates>\n')
              
				        elem = geom.asPolygon()

				        for iii in range (len(elem)):

				          if (iii == 1):				          
				            kml.write ('         </coordinates>\n')
				            kml.write ('         </LinearRing>\n')
				            kml.write ('         </outerBoundaryIs>\n')
				            kml.write ('         <innerBoundaryIs>\n')
				            kml.write ('         <LinearRing>\n')
				            kml.write ('         <coordinates>\n')

				          if (iii > 1):				          
				            kml.write ('         </coordinates>\n')
				            kml.write ('         </LinearRing>\n')
				            kml.write ('         </innerBoundaryIs>\n')
				            kml.write ('         <innerBoundaryIs>\n')
				            kml.write ('         <LinearRing>\n')
				            kml.write ('         <coordinates>\n')	
				        
				          for jjj in range (len(elem[iii])):
				                         
				            x1,y1 = elem[iii][jjj][0], elem[iii][jjj][1]
				            
				            pt1 = xform.transform(QgsPoint(x1, y1))
                           
				            stringazza =   ('%.9lf,%.9lf,0 \n') % (pt1.x(), pt1.y())
				            kml.write (stringazza)

				        if (iii == 0):
				           kml.write ('         </coordinates>\n')
				           kml.write ('        </LinearRing>\n')
				           kml.write ('     </outerBoundaryIs>\n')
				           kml.write ('   </Polygon>\n')

				        if (iii > 0):
				           kml.write ('         </coordinates>\n')
				           kml.write ('        </LinearRing>\n')
				           kml.write ('     </innerBoundaryIs>\n')
				           kml.write ('   </Polygon>\n')	
                   				        
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
				
				if platform.system() == "Windows":            
						os.startfile(out_folder + '/doc.kml')
						
				if platform.system() == "Darwin":			
						os.system("open " + str(out_folder + '/doc.kml'))
						
				if platform.system() == "Linux":            
						os.system("xdg-open " + str(out_folder + '/doc.kml'))			
