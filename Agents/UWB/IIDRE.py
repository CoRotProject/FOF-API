from __future__ import print_function
import sys
sys.path.insert(0, '..')
import logging
import serial
import serial.threaded
import threading
try:
    import queue
except ImportError:
    import Queue as queue

class ATException(Exception):
    pass

class ATProtocol(serial.threaded.LineReader):
    TERMINATOR = b'\r\n'
    def __init__(self):
        super(ATProtocol, self).__init__()
        self.alive = True
        self.responses = queue.Queue()
        self.events = queue.Queue()
        self._event_thread = threading.Thread(target=self._run_event)
        self._event_thread.daemon = True
        self._event_thread.name = 'at-event'
        self._event_thread.start()
        self.lock = threading.Lock()

    def stop(self):
        """
        Stop the event processing thread, abort pending commands, if any.
        """
        self.alive = False
        self.events.put(None)
        self.responses.put('<exit>')

    def _run_event(self):
        """
        Process events in a separate thread so that input thread is not
        blocked.
        """
        while self.alive:
            try:
                self.handle_event(self.events.get())
            except:
                logging.exception('_run_event')

    def handle_line(self, line):
        """
        Handle input from serial port, check for events.
        """
        if line.startswith('+'):
            self.events.put(line)
        else:
            self.responses.put(line)

    def handle_event(self, event):
        """
        Spontaneous message received.
        """
        print('event received:', event)

    def command(self, command, response='OK', timeout=5):
        """
        Set an AT command and wait for the response.
        """
        with self.lock:  # ensure that just one thread is sending commands at once
            self.write_line(command)
            lines = []
            while True:
                try:
                    line = self.responses.get(timeout=timeout)
                    #~ print("%s -> %r" % (command, line))
                    if line == response:
                        return lines
                    else:
                        lines.append(line)
                except queue.Empty:
                    raise ATException('AT command timeout ({!r})'.format(command))
    
    
    
if __name__ == '__main__':
    import time

    class IIDRE(ATProtocol):
        """
        Example communication with IIDRE  module.
        """
        def __init__(self):
            super(IIDRE, self).__init__()
            self.event_responses = queue.Queue()
            self._awaiting_response_for = None

        def connection_made(self, transport):
            super(IIDRE, self).connection_made(transport)
            # our adapter enables the module with RTS=low ?????? ?????
            self.transport.serial.rts = False
            time.sleep(0.3)
            self.transport.serial.reset_input_buffer()

        def handle_event(self, event):
            """Handle events and command responses starting with '+...'"""
            if event.startswith('+RRBDRES') and self._awaiting_response_for.startswith('AT+JRBD'):
                rev = event[9:9 + 12]
                mac = ':'.join('{:02X}'.format(ord(x)) for x in rev.decode('hex')[::-1])
                self.event_responses.put(mac)
            else:
                logging.warning('unhandled event: {!r}'.format(event))

        def command_with_event_response(self, command):
            """Send a command that responds with '+...' line"""
            with self.lock:  # ensure that just one thread is sending commands at once
                self._awaiting_response_for = command
                self.transport.write(b'{}\r\n'.format(command.encode(self.ENCODING, self.UNICODE_HANDLING)))
                response = self.event_responses.get()
                self._awaiting_response_for = None
                return response

        def reset(self):
            self.command("AT+RESET=<0>", response='OK')   

        def get_mac_address(self):
            # requests hardware / calibration info as event
            return self.command_with_event_response("AT+JRBD")

        def get_id(self):
            return self.command("AT+ID?", response='OK')

        def get_firmware_ver(self):
            return self.command("AT+VER?", response='OK')

        def get_nodes(self):
            return self.command("AT+NODE?", response='OK')

        def Write_node(self,DEVICE_UID,add,DEVICE_TYPE):
            if add == True:
                signe= '+'
            else:
                signe= '-'

            return self.command("AT+NODE=<"+signe+"><"+DEVICE_UID+">,<"+DEVICE_TYPE+">", response='OK')

        def get_anchor_pos(self):
            return self.command("AT+POS?", response='OK')
        
        def set_coordinates_anchor(self,ANCHOR_UID,x,y,z):
            return self.command("AT+POS=<"+str(ANCHOR_UID)+">,<"+str(x)+">,<"+str(y)+">,<"+str(z)+">", response='OK')
        
        def get_tag_pos(self):
            return self.command("AT+MPOS?", response='OK',timeout=5)

        def get_nbr_com_anchor(self):
            return self.command("AT+NBTRY?", response='OK')

        def get_UWB_configuration(self):
            return self.command("AT+CFG?", response='OK')
        
        def set_UWB_configuration(self,CHAN,PRF,TRXCODE,BR,PLEN,PAC,TX_GAIN):
            return self.command("AT+CFG=<"+str(CHAN)+">,<"+str(PRF)+">,<"+str(TRXCODE)+">,<"+str(BR)+">\
                ,<"+str(PLEN)+">,<"+str(PAC)+">,<"+str(TX_GAIN)+">", response='OK')

        def get_chan(self):
            return self.command("AT+CHAN?", response='OK')
        
        def set_chan(self,CHANNEL):
            return self.command("AT+CHAN=<"+str(CHANNEL)+">", response='OK')
        
        def get_pulse_frequency(self):
            return self.command("AT+PRF?", response='OK')
        
        def get_TRXcode(self):
            return self.command("AT+TRXCODE?", response='OK')
            
        def get_baudrate(self):
            return self.command("AT+BR?", response='OK')
        
        def get_emisison_gain(self):
            return self.command("AT+PWR?", response='OK')
        
        def get_mbr_dis_muserd_anchor(self):
            return self.command("AT+NBDIST?", response='OK')

        def get_tag_positions_format(self):
            return self.command("AT+FMT?", response='OK')
        
        def get_imu(self):
            return self.command("AT+IMU?", response='OK')
        
        def set_imu(self,status):
            return self.command("AT+IMU=<"+str(status)+">", response='OK')
        
        def set_trace(self,status):
            return self.command("AT+TRACE=+"+str(status), response='OK')
        







    #ser = serial.serial_for_url('spy://COM8', baudrate=115200, timeout=5)
    ser = serial.Serial("/dev/ttyACM1")
    #~ ser = serial.Serial('COM1', baudrate=115200, timeout=1)
    with serial.threaded.ReaderThread(ser, IIDRE) as IIDRE_module:
        #IIDRE_module.reset()
        #print("reset OK")
        print("get the ID", IIDRE_module.get_imu())
        #print("get nodes",IIDRE_module.set_imu("CALIB"))
        #print("get nodes",IIDRE_module.set_trace("DIMU"))
        #print("set_coordinates_anchor",IIDRE_module.set_coordinates_anchor(1,1,1,2))
        #print("get_anchor_pos", IIDRE_module.get_anchor_pos())
        #print("get_UWB_configuration", IIDRE_module.get_UWB_configuration())
        #print("get_UWB_configuration", IIDRE_module.get_tag_positions_format())


        #print("the number of attempts realized by the tag",IIDRE_module.get_nbr_com_anchor())
        #IIDRE_module.Write_node(DEVICE_UID='4D144137',add=False,DEVICE_TYPE='2')
        #IIDRE_module.Write_node(DEVICE_UID='D141C33',add=True,DEVICE_TYPE='2')

        #IIDRE_module.Write_node(DEVICE_UID='0D02CEA0',add=True,DEVICE_TYPE='3')
        #IIDRE_module.Write_node(DEVICE_UID='5564488D',add=True,DEVICE_TYPE='1')
        #IIDRE_module.Write_node(DEVICE_UID='1564489F',add=True,DEVICE_TYPE='1')
        #IIDRE_module.Write_node(DEVICE_UID='556448A5',add=True,DEVICE_TYPE='1')
        #IIDRE_module.Write_node(DEVICE_UID='5561D22E',add=True,DEVICE_TYPE='1')
        '''try:
            test=IIDRE_module.stop()
            while True:
                time.sleep(10)
        except (KeyboardInterrupt, SystemExit):
            IIDRE_module.stop()
            print(test)
            print("killed")'''

