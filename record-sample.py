# $Id: simplecall.py 2171 2008-07-24 09:01:33Z bennylp $
#
# SIP account and registration sample. In this sample, the program
# will block to wait until registration is complete
#
# Copyright (C) 2003-2008 Benny Prijono <benny@prijono.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
import sys
import pjsua as pj
import threading
import time
import os

#os.setuid(1000)
voip_server = "10.8.0.1"
global name_sound_file

if len(sys.argv) < 2:
    print "Usages: python " + sys.argv[0] + " <record-file-name>"
    print sys.argv
    sys.exit(1)

name_sound_file = sys.argv[1]


# Logging callback
def log_cb(level, str, len):
    print str,


class MyAccountCallback(pj.AccountCallback):
    sem = None
    HANGUP = False

    def __init__(self, account):
        pj.AccountCallback.__init__(self, account)

    def wait(self):
        self.sem = threading.Semaphore(0)
        self.sem.acquire()

    def on_reg_state(self):
        if self.sem:
            if self.account.info().reg_status >= 200:
                self.sem.release()


# Callback to receive events from Call
class MyCallCallback(pj.CallCallback):
    recorder_slot_Id = None
    recorder_id = None
    record = False

    def __init__(self, call=None, record=False):
        pj.CallCallback.__init__(self, call)
        self.record = record
        print str(self.record) + "))))))))))"

    # Notification when call state has changed
    def on_state(self):
        print "Call is ", self.call.info().state_text,
        print "last code =", self.call.info().last_code,
        print "(" + self.call.info().last_reason + ")"
        if self.call.info().state == 6 and self.record == True:  # 6==DISCONNECTED
            c_slot = call.info().conf_slot
            lib.conf_disconnect(0, self.recorder_slot_Id)
            lib.recorder_destroy(self.recorder_id)
            self.record = False
            self.recorder_id = None
            self.recorder_slot_Id = None

    # Notification when call's media state has changed.
    def on_media_state(self):
        global lib
        prev = self.call.info().media_state
        prev = self.call.info().media_state

        if self.call.info().media_state == pj.MediaState.ACTIVE:
            # Connect the call to sound device
            call_slot = self.call.info().conf_slot
            lib.conf_connect(call_slot, 0)
            lib.conf_connect(0, call_slot)
            # print "Hello world, I can talk!"

            if self.record == True:
                self.recorder_id = lib.create_recorder(name_sound_file)
                self.recorder_slot_Id = lib.recorder_get_slot(self.recorder_id)
                lib.conf_connect(call_slot, self.recorder_slot_Id)
                print "Recording Call..."


try:
    # Create library instance
    lib = pj.Lib()

    # Init library with default config
    med_conf = pj.MediaConfig()
    med_conf.clock_rate = 8000
    med_conf.ec_options = 0
    med_conf.jb_max = 0
    med_conf.jb_min = 0

    lib.init(log_cfg=pj.LogConfig(level=7, callback=log_cb), media_cfg=med_conf)

    # Create UDP transport which listens to any available port
    transport = lib.create_transport(pj.TransportType.UDP, pj.TransportConfig(5080))

    RECORDING = True
    lib.start()

    # configure client account
    acc_cfg = pj.AccountConfig()
    # acc_cfg.id = "sip:1003@128.199.106.141"
    # acc_cfg.reg_uri = "sip:128.199.106.141"
    # acc_cfg.proxy = ["sip:128.199.106.141"]
    # acc_cfg.auth_cred = [pj.AuthCred("128.199.106.141", "1003", "killerbee#121")]
    acc_cfg.id = "sip:1003@" + voip_server
    acc_cfg.reg_uri = "sip:" + voip_server
    acc_cfg.proxy = ["sip:" + voip_server]
    acc_cfg.auth_cred = [pj.AuthCred(voip_server, "1003", "killerbee#121")]

    acc = lib.create_account(acc_cfg)
    acc_cb = MyAccountCallback(acc)
    acc.set_callback(acc_cb)
    acc_cb.wait()

    print "\n"
    print "Registration complete, status=", acc.info().reg_status, "(" + acc.info().reg_reason + ")"

    print "destination - (sip:xxx@host):"
    dst = "sip:999998@" + voip_server
    # Make call
    call = acc.make_call(dst, MyCallCallback(record=RECORDING))

    time.sleep(38)

    # We're done, shutdown the library
    lib.destroy()
    lib = None

except pj.Error, e:
    print "Exception: " + str(e)
    lib.destroy()
    lib = None
    sys.exit(1)
