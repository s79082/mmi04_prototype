"""
Tracks hand movements to detect two gestures
"""

import leap
import time
import os

import numpy as np
from leap.datatypes import Hand, Palm
import leap.datatypes
import vector
from pyquaternion import Quaternion

def clear():
    os.system('cls')

def convert_vector(vec: leap.datatypes.Vector):
    """Converts a leapmotion Vector instance to a 3D vector from the `vector` library."""
    return vector.obj(
        x=vec.x,
        y=vec.y,
        z=vec.z
    )

def convert_quaternion(quaternion: leap.datatypes.Quaternion):
    """Converts a leapmotion Quaternion instance to a Quaternion from the `pyquaternion` library."""
    return Quaternion(quaternion.w, quaternion.x, quaternion.y, quaternion.z)

def bigger_than(value: int, compare: int):
    """Checks if a value is bigger than or smaller than the negative value"""
    return value < -compare or compare < value
    
def biggest_axis(vec: vector.Vector3D, axis: int):
    """Checks if the value of a selected axis of the Vector is bigger than the other ones"""
    vec = vector.obj(x=abs(vec.x), y=abs(vec.y), z=abs(vec.z))
    if axis == 0:
        return vec.x > vec.y and vec.x > vec.z
    if axis == 1:
        return vec.y > vec.x and vec.y > vec.z
    if axis == 2:
        return vec.z > vec.x and vec.z > vec.y
    if axis < 0 or 2 < axis:
        raise "Not a valid axis"

class MyListener(leap.Listener):
    # coordinate system: x: left to right; y: up and down; z: back and forth
    forward_axis = vector.obj(x=0, y=0, z=1)
    
    """ knob_value = 0
    knob_first: float = None
    knob_previous: Quaternion = None """
    
    volume_grab_counter = 0
    volume_grab_start: vector.VectorObject3D = None
    volume_grab_last_time = 0
    volume_grab_already_detected = False
    
    swipe_counter = 0
    swipe_start: vector.VectorObject3D = None
    swipe_last_time = 0
    swipe_already_detected = False
    
    def on_connection_event(self, event):
        print("Connected")

    def on_device_event(self, event):
        try:
            with event.device.open():
                info = event.device.get_info()
        except leap.LeapCannotOpenDeviceError:
            info = event.device.get_info()

        print(f"Found device {info.serial}")

    def on_tracking_event(self, event):
        #print(f"Frame {event.tracking_frame_id} with {len(event.hands)} hands.")
        hands: list[Hand] = event.hands;
        for hand in hands:
            palm: Palm = hand.palm;
            #hand_type = "left" if str(hand.type) == "HandType.Left" else "right"
            palm_position = convert_vector(palm.position)
            palm_direction = convert_vector(palm.direction)
            palm_orientation = convert_quaternion(palm.orientation).normalised
            palm_velocity = convert_vector(palm.velocity)
            #print(np.array([palm_position.x, palm_position.y, palm_position.z]))
            #print(hand.grab_strength)
            #return
            
            #print(palm_velocity.mag)
            # close hand to fist, move up or down
            if hand.grab_strength > 0.9:
                if self.volume_grab_start:
                    self.volume_grab_last_time = leap.get_now()
                    grab: vector.Vector3D = self.volume_grab_start.subtract(palm_position)
                    distance = grab.y
                    if bigger_than(distance, 60) and not self.volume_grab_already_detected:
                        grab_direction = "down" if distance > 0 else "up"
                        self.volume_grab_already_detected = True
                        print(f"{grab_direction} Swipe detected")
                    else:
                        pass
                        #print(distance)
                elif self.volume_grab_last_time + 2 * 10000 < leap.get_now() and palm_velocity.mag < 40:
                    self.volume_grab_start = palm_position
                    self.volume_grab_counter += 1
                    print(f"{self.volume_grab_counter} Volume Grab start")
            else:
                if self.volume_grab_start:
                    self.volume_grab_start = None
                    self.volume_grab_already_detected = False
                    print("Grab end")
            
            #print(np.array([palm_velocity.x, palm_velocity.y, palm_velocity.z]))
            # swipe left or right to skip or go to previous
            if (bigger_than(palm_velocity.x, 600) and biggest_axis(palm_velocity, 0)
                and vector.obj(x=0, y=1, z=0).is_perpendicular(palm_direction, 0.1)):
                if self.swipe_start:
                    self.swipe_last_time = leap.get_now()
                    grab: vector.Vector3D = self.swipe_start.subtract(palm_position)
                    distance = grab.x
                    if bigger_than(distance, 60) and not self.swipe_already_detected:
                        swipe_direction = "left" if distance > 0 else "right"
                        self.swipe_counter += 1
                        self.swipe_already_detected = True
                        print(f"{swipe_direction} Swipe detected")
                    else:
                        pass
                        #print(distance)
                elif self.swipe_last_time + 10000 < leap.get_now():
                    self.swipe_start = palm_position
                    #clear()
                    print("Swipe start")
                    #print(self.swipe_counter)
            else:
                if self.swipe_start:
                    self.swipe_start = None
                    self.swipe_already_detected = False
                    print("Swipe end")
                
            #print(f"{hand.grab_strength}")
            
            # for some reason the coordinate system of palm_direction has a really weard orientation
            #print(f"{palm_direction.x}\t{palm_direction.y}\t{palm_direction.z}\t")
            #print(f"{vector.obj(x=0, y=1, z=0).is_parallel(palm_direction, 0.2)}")
            
            # gesture hand like holding a volume knob, turn to increase or decrease volume
            """ fingers_pointing_forward = 0
            for index_digit in range(0, 5):
                digit = hand.digits[index_digit]
                # calculate vector of fingertip
                finger_tip = convert_vector(digit.distal.prev_joint) - convert_vector(digit.distal.next_joint)
                if self.forward_axis.is_parallel(finger_tip, 0.2):
                    fingers_pointing_forward += 1
            #print(f"pointing forwards: {fingers_pointing_forward}")
            #print(f"pointing forwards: {fingers_pointing_forward > 3}, {vector.obj(x=0, y=1, z=0).is_parallel(palm_direction, 0.5)}")
            if vector.obj(x=0, y=1, z=0).is_parallel(palm_direction, 0.5) and fingers_pointing_forward >= 3:
                if self.knob_previous:
                    distance = Quaternion.to_degrees(self.knob_previous.angle - palm_orientation.angle)
                    self.knob_value = np.clip(self.knob_value + distance, 0, 180)
                    self.knob_previous = palm_orientation
                    if self.knob_first is None:
                        self.knob_first = distance
                    print(f"pointing forwards: true; {self.knob_value}")
                else:
                    self.knob_previous = palm_orientation
                    print(f"pointing forwards: true")
            else:
                self.knob_previous = None """
                #print(f"pointing forwards: false")
                
                
                #print(f"{digit.bones}")
            #print(f"{palm.position.x}, {palm.position.y}, {palm.position.z}")
            #direction.dot()
            """ if hand.visible_time == 0:
                self.start = position
            else:
                move = self.start.subtract - position
                print(f"{move}") """
            # Detect swipe: hand grap_strength < 0.1 && vertical orientation && move far enough vertical

def main():
    my_listener = MyListener()

    connection = leap.Connection()
    connection.add_listener(my_listener)

    running = True

    with connection.open():
        #connection.set_tracking_mode(leap.TrackingMode.Desktop)
        connection.set_tracking_mode(leap.TrackingMode.ScreenTop)
        while running:
            try:
                time.sleep(1)
            except:
                running = False


if __name__ == "__main__":
    main()
