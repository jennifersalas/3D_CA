import logging
import threading
import time

import standardFuncs
import defaultValues

standardFuncs.logger()


# Make a single thread object to listen for telemetry updates.
class synchronizer(threading.Thread):
    def __init__(self, numPlanes):
        threading.Thread.__init__(self, name="Global Communicator")
        # pass the class object through the plane generator to modify these values
        self.uavsInAir = numPlanes

        self.msg = {"ID": 0, "Location": ""}

        self.startTime = time.time()
        self.lastUpdate = time.time()

        # For reading the message
        self.readCounter = 0
        self.readLock = threading.RLock()
        self.broadcast = threading.Event()
        self.readTurn = threading.Event()

        self.broadcast.clear()
        self.readTurn.clear()

        # For writing the message
        self.broadcastCounter = 0
        self.msgLock = threading.RLock()
        self.broadcastWrite = threading.Event()
        self.turn = threading.Event()

        self.broadcastWrite.set()
        self.turn.clear()

        self.msgRcd = threading.Event()

        self.start()

    # Keep track of how many threads have updated location and notify all threads if all have completed one cycle.
    def run(self):
        logging.info("Global communicator initiated: %s" % self)
        startTime = self.lastUpdate
        try:
            while self.uavsInAir != 0:

<<<<<<< HEAD
=======
                if self.broadcastCounter == self.uavsInAir:
                    self.broadcastCounter = 0
                    logging.info("##########All UAVs wrote a message")
                    self.turn.set()

>>>>>>> origin/master
                if self.readCounter >= self.uavsInAir:
                    self.readCounter = 0
                    self.msgRcd.set()
                    self.broadcastWrite.set()
                    self.readTurn.set()

<<<<<<< HEAD
                if time.time() - self.lastUpdate > defaultValues.COMM_KILL_TIME:
=======
                # Break if no updates within 4 seconds or no UAVs in air
                if (time.time() - self.lastUpdate > defaultValues.COMM_KILL_TIME):
>>>>>>> origin/master
                    logging.info("Communication timed out.")
                    print "Communication timed out."
                    break

        except KeyboardInterrupt:
            logging.info("Program interrupted by user.")
        time.sleep(.1)
        if self.uavsInAir == 0:
<<<<<<< HEAD
            print "NO UAVS AIR."
=======
            logging.info("NO UAVS AIR.")
>>>>>>> origin/master
        else:
            print "UAVs in air: %i" % self.uavsInAir
            print 'Read counter: %i' % self.readCounter
            print 'Read turn event: %s' % self.readTurn.isSet()
            print 'Broadcast Event: %s' % self.broadcast.isSet()

            print 'Broadcast counter: %i' % self.broadcastCounter
            print 'Broadcast write event: %s' % self.broadcastWrite.isSet()
            print 'Broadcast turn event: %s' % self.turn.isSet()
        logging.info("Time elapsed: %.2fs" % (self.lastUpdate - startTime))


# In planeGenerator, each plane object will start its own communication thread to update and receive telemetry.
class communicate(threading.Thread):
    def __init__(self, plane, synchronizer):
        self.plane = plane
        self.synch = synchronizer

        threading.Thread.__init__(self, name="UAV #%i Comm" % self.plane.id)
        self.setDaemon(True)
        self.start()
        self.msgCounter = 0

    def run(self):
        while True:
            # Wait for a broadcast from UAV
            # logging.info("Com #%3i waiting for next broadcast." % self.plane.id)
            self.synch.broadcast.wait()
<<<<<<< HEAD

            # logging.info("Com #%3i waiting for readLock" % self.plane.id)
            self.synch.readLock.acquire()
            # logging.info("Com #%3i acquired readLock" % self.plane.id)
=======
            self.synch.readLock.acquire()
            # logging.info("Com #%3i acquired readLock" % self.plane.id)

>>>>>>> origin/master
            # Read the message
            self.plane.threatMap(self.synch.msg)
            logging.info("Com #%3i received message #%i from UAV # %i" % (
                self.plane.id, self.synch.msg["#"], self.synch.msg["ID"]))
            self.plane.threatMap(self.synch.msg)
            # Increment counter for new read turn
            self.synch.readCounter += 1

            # logging.info("Com #%3i released readLock" % self.plane.id)
<<<<<<< HEAD

=======
>>>>>>> origin/master
            self.synch.readLock.release()
            #logging.info("Com #%3i waiting for next read turn." % self.plane.id)
            self.synch.readTurn.wait()
            if self.plane.dead or self.plane.wpAchieved >= self.plane.numWayPoints:
                break

    def update(self):
        # Wait for it to be ok to broadcast
        self.synch.msgLock.acquire()
        self.synch.broadcastWrite.wait()
        self.synch.turn.clear()
        self.synch.lastUpdate = time.time()

        # Send Message
        if self.plane.dead:
            self.synch.uavsInAir -= 1
            logging.info("UAV #%3i crashed." % self.plane.id)
        if self.plane.wpAchieved == self.plane.numWayPoints:
            self.synch.uavsInAir -= 1
            logging.info("UAV #%3i reached all waypoints." % self.plane.id)
        else:
            self.synch.broadcastCounter += 1
            self.msgCounter += 1
<<<<<<< HEAD
            self.synch.msg = {"ID": self.plane.id, "Location": self.plane.cLoc, "#": self.msgCounter, "Dead" : self.plane.dead, "KilledBy" : self.plane.killedBy}
=======
            self.synch.msg = {"ID": self.plane.id, "Location": self.plane.cLoc, "#": self.msgCounter}
>>>>>>> origin/master

        logging.info("UAV #%3i broadcasting message." % self.plane.id)

        # Alert UAV Comms of message
        self.synch.broadcast.set()

        logging.info("Waiting for all Comms to receive message.")
        self.synch.msgRcd.wait()
        self.synch.msgRcd.clear()
        self.synch.broadcast.clear()
        logging.info("UAV #%3i confirmed UAV Comms received message" % self.plane.id)

        logging.info("**********UAV #%3i end of broadcast turn." % self.plane.id)

        self.synch.msgLock.release()
        self.synch.turn.wait()
