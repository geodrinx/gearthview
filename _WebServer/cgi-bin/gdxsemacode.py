#!/usr/bin/python

#!/usr/bin/env python
#!/usr/bin/python
#!c:/ms4w/apps/python25/python.exe

import cgi
import string
import httplib
            
server = 'localhost'
            
                                                                                                                                                                                                                                                                                           
if __name__ == "__main__":                                                                                                                                                                                                                                                                                                       


   url = cgi.FieldStorage() 

   bbox = url["BBOX"].value
   bbox = bbox.split(',')
   west = float(bbox[0])
   south = float(bbox[1])
   east = float(bbox[2])
   north = float(bbox[3])

   lon = ((east - west) / 2) + west
   lat = ((north - south) / 2) + south


   kml = ( 
      '<?xml version="1.0" encoding="UTF-8"?>\n'
      '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
      ' <Placemark>\n'
      '  <name>Point</name>\n'
      '	<Snippet maxLines="0"></Snippet>\n'
      '  <description>\n')
      
   kml = kml + ('<![CDATA[<html>lat  long<br><br>%.14f,%.14f<br><br><table border=1 style="border-collapse:collapse; border-color:#000000;"cellpadding=0 cellspacing=0  width=250 style="FONT-SIZE: 11px; FONT-FAMILY: Verdana, Arial, Helvetica, sans-serif;"><tr><td bgcolor="#E3E1CA" align="right"><font COLOR="#FF0000"><b>CODE</b></font></td><td bgcolor="#E4E6CA"> <font COLOR="#008000">\n')  %(lat,lon)

   qrCodeUrl = ("http://qrcode.kaywa.com/img.php?s=8&amp;d=%.14f,%.14f") %(lat,lon)
   
   kml = kml + ('<img alt="" src="%s" /></html>]]></description>\n') %(qrCodeUrl)   


   kml = kml + ('  <Style>\n'
      '   <Icon>\n'
      '  	<href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle_highlight.png</href>\n'
      '   </Icon>\n' 
      '  </Style>\n'   
      '  <Point>\n'
      '    <coordinates>%.14f,%.14f</coordinates>\n'
      '  </Point>\n'
      ' </Placemark>\n'
      '</kml>'
      ) %( lon, lat)

   print 'Content-Type: application/vnd.google-earth.kml+xml\n'
   print kml
   
#   h ttp://localhost:8000/cgi-bin/helloworld.py?BBOX=12.66229588907776,40.84152608870524,14.45499302666336,41.68905890740719
   
   f = open('./QGEarth.log', 'w')

   string = ('%.14f\n%.14f\n%.14f\n%.14f\n%.14f\n%.14f\n%s') % (west, south, east, north, lon, lat, qrCodeUrl)
   f.write (string)         
   
   f.close()   
