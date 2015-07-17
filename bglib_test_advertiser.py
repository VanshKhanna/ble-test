""" Bluegiga BGAPI/BGLib implementation
=======================================
Using Python interface library, bglib.
=======================================
"""
from pymongo import MongoClient
import bglib, serial, time, datetime, signal

signal.alarm(3);

# creat connection to the database
#client = MongoClient('mongodb://Ubuntu:Ubuntu@ds053312.mongolab.com:53312/shop')
client = MongoClient('mongodb://localhost:9000/shop')
db = client.shop
collection = db.hello

# to keep track of the number of packets received
count = 0

#posts = db.posts

# handler for API parser timeout
def my_timeout(sender, args):
    print "BGAPI parser times out. Make sure the BLE device is in a known/idle state."

# callback for disconnection
def on_disconnection(connection, reason):
    ble.send_command(ser, ble.ble_cmd_gap_set_mode(2, 2))
    ble.check_activity(ser, 1)


# handler to print scan responses with a timestamp
def my_ble_evt_gap_scan_response(sender, args):
    #print "gap_scan_response",
    global count
    t = datetime.datetime.now()
    count += 1;
    disp_list = []
    #disp_list.append("%ld.%03ld" % (time.mktime(t.timetuple()), t.microsecond/1000))
    disp_list.append("%ld" % (int(round(time.time()*1000))))
    disp_list.append("%d" % args["rssi"])
    disp_list.append("%d" % args["packet_type"])
    disp_list.append("%s" % ''.join(['%02X' % b for b in args["sender"][::-1]]))
    disp_list.append("%d" % args["address_type"])
    disp_list.append("%d" % args["bond"])
    disp_list.append("%s" % ''.join(['%02X' % b for b in args["data"]]))
    disp_list.append("%d" % count)
    #print ' '.join(disp_list)
    
    device_addr = ''.join(['%02X' % b for b in args["sender"][::-1]])
    collection.update(
            { "_id":device_addr},
            { 
                #"$addToSet": { "tags": {"$each": ["colors"]} }, 
                "$inc" : {"count":1}
            },
             upsert= True
    )

def main():
    port_name = "/dev/ttyACM0"
    baud_rate = 115200
    packet_mode = False

    # create BGLib object
    ble = bglib.BGLib()
    ble.packet_mode = packet_mode

    # add handler for the BGAPI timeout condition
    ble.on_timeout += my_timeout

    # add handler for the ble_evt_connection_disconnected
    ble.ble_evt_connection_disconnected += on_disconnection

    ble.ble_evt_gap_scan_response += my_ble_evt_gap_scan_response
    
    # creat serial port object and flush buffers
    ser = serial.Serial(port=port_name, baudrate=baud_rate, timeout=1)
    ser.flushInput()
    ser.flushOutput()

    # stop advertising if advertising already
    ble.send_command(ser, ble.ble_cmd_gap_set_mode(0, 0))
    ble.check_activity(ser, 1)

    # set advertising parameters
    ble.send_command(ser, ble.ble_cmd_gap_set_adv_parameters(320, 480, 7))
    while ble.check_activity(ser): pass
   
    #start advertising
    ble.send_command(ser, ble.ble_cmd_gap_set_mode(2, 2))
    
    # set scan parameters
    ble.send_command(ser, ble.ble_cmd_gap_set_scan_parameters(0xC8, 0xC8, 0))
    ble.check_activity(ser, 1)

    # start scanning now
    ble.send_command(ser, ble.ble_cmd_gap_discover(2))
    ble.check_activity(ser, 1)
    
    while (1):
       ble.check_activity(ser)
       time.sleep(0.01) 

if __name__ == '__main__':
    main()
