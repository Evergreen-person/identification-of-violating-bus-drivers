from event import Event, EventType

class Person:

    def __init__(self, track, frame_id, last_points = 50, is_show = False, count_to_be_shown = 25, age = 10):
        self.track_id = track.track_id
        init_box = track.to_tlbr()
        self.boxes = [init_box]
        self.centers = [(int(((init_box[0])+(init_box[2]))/2), int(((init_box[1])+(init_box[3]))/2))]
        self.is_deleted = track.is_deleted()
        self.last_points = last_points
        self.is_show = False
        self.count_to_be_shown = count_to_be_shown
        self.counter = count_to_be_shown
        self.is_confirmed = track.is_confirmed
        self.time_since_update = 0
        self.first_meet = frame_id
        self.last_meet = frame_id
        self.crossed = []
        self.frame_now = frame_id
        self.age = age
        self.events = []

    def update(self, track, frame_id):
        self.time_since_update = 0
        self.frame_now = frame_id
        if track.is_deleted():
            self.is_confirmed = False
            self.is_deleted = True
        elif not track.time_since_update > 1:
            bbox = track.to_tlbr()
            self.boxes.append(bbox)
            self.centers.append((int(((bbox[0])+(bbox[2]))/2), int(((bbox[1])+(bbox[3]))/2)))
            self.is_confirmed = track.is_confirmed()
            self.last_meet = frame_id

    def set_crossed(self, bus_id, frame_id):
        self.crossed.append({
            'bus_id': bus_id,
            'frame_id': frame_id
        })

    def check(self):
        for last_crossed in self.crossed[:1]:
                if (last_crossed['frame_id'] <= self.first_meet + 3):
                    self.events.append(Event(last_crossed['frame_id'], self.track_id, EventType.PersonGoingOut, last_crossed["bus_id"]))
                    break
        for last_crossed in reversed(self.crossed[-1:]):
            if (last_crossed['frame_id'] >= self.last_meet - 3):
                self.events.append(Event(self.frame_now, self.track_id, EventType.PersonGoingInto, last_crossed["bus_id"]))
                break

    def tick(self):
        if self.time_since_update >= self.age and not self.is_deleted:
            self.is_deleted = True
            self.check()
        self.time_since_update += 1   