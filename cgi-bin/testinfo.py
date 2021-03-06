#!/usr/bin/python

# Import modules for CGI handling 
import sys
import cgi, cgitb 
import httplib

import xml.etree.ElementTree as ET

#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------
def httpSender( httpConn, xmlDoc ):
    httpConn.request( 'POST', '/YamahaRemoteControl/ctrl', xmlDoc )
    response = httpConn.getresponse()
    if response.status == httplib.OK:
        rr = response.read()
        print >> sys.stderr, "httpSender: CGI output: %s" % rr
        return ( 0, rr )
    else:
        print >> sys.stderr, "httpSender: CGI request failed: %d" % response.status
        return ( -1, response.read() )

#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------
def sendCommand( receiverAddress, onOff, zone, source, vol ):
    print >> sys.stderr, "sendCommand: Zone: %s, State: %s, Source: %s, Volume: %d" % ( zone, onOff, source, vol )

    httpServ = httplib.HTTPConnection( receiverAddress, 80 )
    print >> sys.stderr, "sendCommand: created server address is %s" % receiverAddress

    httpServ.connect()
    print >> sys.stderr, "sendCommand: Connected."

    xmlCmd = ( "<YAMAHA_AV cmd=\"PUT\"> <%s> <Power_Control><Power>%s</Power></Power_Control></%s> </YAMAHA_AV>" % ( zone, onOff, zone ) )

    # dbg( "Command: %s" % xmlCmd )

    print >> sys.stderr, "sendCommand: sending: %s" % xmlCmd
    rc = httpSender( httpServ, xmlCmd )
    if rc[ 0 ] != 0:
        httpServ.close()
        return rc

    # Save the output from the first command
    tmp = rc[ 1 ]

    if source != "" and onOff == "On":
        if vol == 0:
            volString = ""
        else:
            volString = "<Volume><Lvl><Val>%d</Val><Exp>1</Exp><Unit>dB</Unit></Lvl></Volume>" % vol

        # print >> sys.stderr, "sendCommand: Volume string: %s" % volString

        xmlCmd = ( "<YAMAHA_AV cmd=\"PUT\"> <%s> <Input> <Input_Sel>%s</Input_Sel> </Input> %s </%s> </YAMAHA_AV>" % ( zone, source, volString, zone ) )
        print >> sys.stderr, "sendCommand: sending: %s" % xmlCmd
        rc = httpSender( httpServ, xmlCmd )

        tmp = tmp + '\n' + rc[ 1 ]

        print >> sys.stderr, "sendCommand: complete, rc: %d, result: %s" % ( rc[ 0 ], rc[ 1 ] )

    httpServ.close()

    return ( rc[ 0 ], tmp )

#------------------------------------------------------------------------------
# Get the info for the indicated zone
#------------------------------------------------------------------------------
def getInfo( receiverAddress, zone ):
    httpServ = httplib.HTTPConnection( receiverAddress, 80 )
    print >> sys.stderr, "getInfo: created server address is %s" % receiverAddress

    httpServ.connect()
    print >> sys.stderr, "getInfo: Connected."

    xmlCmd = ( "<YAMAHA_AV cmd=\"GET\"> <%s> <Basic_Status>GetParam</Basic_Status> </%s> </YAMAHA_AV>" % ( zone, zone ) )

    print >> sys.stderr, "getInfo: sending: %s" % xmlCmd
    rc = httpSender( httpServ, xmlCmd )
    print >> sys.stderr, "getInfo: Got: %s" % rc[ 1 ]

    httpServ.close()

    tree = ET.fromstring( rc[ 1 ] )

    power = tree.find( zone + "/Basic_Status/Power_Control/Power" )
    print power.text
    source = tree.find( zone + "/Basic_Status/Input/Input_Sel" )
    print source.text
    level = tree.find( zone + "/Basic_Status/Volume/Lvl/Val" )
    print level.text
    scale = tree.find( zone + "/Basic_Status/Volume/Lvl/Exp" )
    print scale.text

    return ( power.text, source.text, level.text, scale.text )


#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------
def getField( form, name, def_val ):
    if name not in form:
        print >> sys.stderr, "getField: default for %s is %s" % ( name, str( def_val ) )
        return def_val
    else:
        val = form.getvalue( name )
        print >> sys.stderr, "getField: for %s got %s" % ( name, str( val ) )
        return val


#==========================================================================
#
#==========================================================================

receiverAddress = "192.168.1.218"

if 0:
    httpServ = httplib.HTTPConnection( receiverAddress, 80 )
    print >> sys.stderr, "sendCommand: created server address is %s" % receiverAddress
    
    httpServ.connect()
    print >> sys.stderr, "sendCommand: Connected."
    
    zone = "Zone_3"
    
    xmlCmd = ( "<YAMAHA_AV cmd=\"GET\"> <%s> <Basic_Status>GetParam</Basic_Status> </%s> </YAMAHA_AV>" % ( zone, zone ) )
    
    print >> sys.stderr, "sendCommand: sending: %s" % xmlCmd
    rc = httpSender( httpServ, xmlCmd )
    print >> sys.stderr, "Got: %s" % rc[ 1 ]
    
    httpServ.close()
    
    # tree = ET.ElementTree( ET.fromstring( rc[ 1 ] ) )
    tree = ET.fromstring( rc[ 1 ] )
    # print >> sys.stderr, tree.tag
    # print >> sys.stderr, tree.attrib
    
    # for child in tree:
        # print(child.tag, child.attrib)
    
    # zone_data = tree.find( zone )
    
    power = tree.find( zone + "/Basic_Status/Power_Control/Power" )
    print power.text
    source = tree.find( zone + "/Basic_Status/Input/Input_Sel" )
    print source.text

main_zone = getInfo( receiverAddress, "Main_Zone" )
zone_2 = getInfo( receiverAddress, "Zone_2" )
zone_3 = getInfo( receiverAddress, "Zone_3" )

print main_zone
print zone_2
print zone_3
