# Todo: each object should be able to call an instance of this simulator for independent movement simulation
# Todo: minimum turning radius should be calculated based off of speed]
# http://people.clarkson.edu/~pmarzocc/AE429/AE-429-12.pdf

import defaultValues
import standardFuncs
import time
import logging

from maneuvers import straightLine, dubinsPath


def move(plane, communicator):
    timer = 0
    stop = False

    # Todo: Make an option for centralized/decentralized collision avoidance & movement
    # Move the plan in a straight line to the direction of the target waypoint
    while not stop and not plane.dead:

        # Simulate time by delaying planes update. Will need this for GUI.
        if defaultValues.SIMULATE_TIME:
            time.sleep(defaultValues.DELAY)
        timer += defaultValues.DELAY

        # find distance to target location

        clat = plane.cLoc.latitude
        clon = plane.cLoc.longitude
        calt = plane.cLoc.altitude

        tlat = plane.tLoc.latitude
        tlon = plane.tLoc.longitude
        talt = plane.tLoc.altitude

        # Todo: with each adjustment, calculate a distance travled


        # If plane distance is less than turning radius, check dubins path. This should be set on or off in settings.
        if plane.tdistance <= defaultValues.MIN_TURN_RAD:
            logging.info("UAV #%3i checking for dubins path." % plane.id)
            dubinsPath.takeDubinsPath(plane)
            pass

        #plane.cBearing = plane.tBearing
        plane.cElevation = plane.tElevation

        straightLine.straightline(plane)

        # This method of reading positions only works with centralized communication
        if defaultValues.CENTRALIZED:
            uav_positions = communicator.receive(plane)
            for elem in uav_positions:
                distance = standardFuncs.totalDistance(plane.cLoc, elem["cLoc"])
                if (distance < defaultValues.CRASH_DISTANCE and elem["ID"] != plane.id and elem["dead"] == False):
                    # time.sleep(random.uniform(0, .001))  # Just so that the console doesn't get screwed up
                    plane.dead = True
                    plane.killedBy = elem["ID"]
                    stop = True
                elif elem["ID"] == plane.id and elem["dead"] == True:
                    plane.dead = True
                    plane.killedBy = elem["killedBy"]
                    stop = True

        # No need to call receive function for decentralized. Incoming communication automatically stores information
        elif not defaultValues.CENTRALIZED:
            pass

        # Move through queue to next waypoint, or if done stop thread.
        if (plane.tdistance < defaultValues.WAYPOINT_DISTANCE) and (plane.wpAchieved <= plane.numWayPoints):
            plane.wpAchieved += 1
            if plane.wpAchieved < plane.numWayPoints:
                plane.nextwp()
        if plane.wpAchieved >= plane.numWayPoints: stop = True

        communicator.send(plane)

    # Todo: make this pretty
    if plane.dead: print "\r%-80s" % "UAV #%3i has crashed!!" % plane.id
    if plane.wpAchieved == plane.numWayPoints: print "\r%-80s" % "UAV #%3i reached all waypoints." % plane.id
