#!/usr/bin/python

# Import modules for CGI handling 
import sys
import cgi, cgitb 
import httplib

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
# Create instance of FieldStorage 
form = cgi.FieldStorage() 

# Get data from fields
receiver = getField( form, 'receiver', '192.168.1.218' )
state = getField( form, 'state', 'Standby' )
zone = getField( form, 'zone', 'Zone_4' )
source = getField( form, 'source', 'AV1' )
volume = 0

rc = sendCommand( receiver, state, zone, source, volume )

print "Content-type:text/plain\r\n\r\n"
print rc[ 1 ]
