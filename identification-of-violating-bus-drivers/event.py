class EventType:
    BusMoving = 1
    BusStopping = 2
    PersonGoingOut = 3
    PersonGoingInto = 4

class Event:
    
    def __init__(self, frame_id, track_id, event, opposite_track_id = None):
        self.frame_id = frame_id
        self.track_id = track_id,
        self.event = event
        self.opposite_track_id = opposite_track_id

    def get_time_of_event(self, fps):
        return self.frame_id / fps

    def message(self):
        if self.event is EventType.BusMoving:
            return f'[FRAME_ID={self.frame_id}] Bus {self.track_id} starts moving'
        elif self.event is EventType.BusStopping:
            return f'[FRAME_ID={self.frame_id}] Bus {self.track_id} stops'
        elif self.event is EventType.PersonGoingInto and self.opposite_track_id is not None:
            return f'[FRAME_ID={self.frame_id}] Person {self.track_id} enters the bus {self.opposite_track_id}'
        elif self.event is EventType.PersonGoingOut and self.opposite_track_id is not None:
            return f'[FRAME_ID={self.frame_id}] Person {self.track_id} gets off the bus {self.opposite_track_id}'