import json
import random
from battles.models import Arena
from battles.views import Battlefield


class SensorWrapper(object):
    def __init__(self, fighter, module):
        self.fighter = fighter
        self.module = module

    def process(self, battlefield):
        return []


class EyeModule(SensorWrapper):
    def process(self, battlefield):
        """
        module should contain parameter 'field_of_vision'
        looking like following:

        {
            'field_of_vision':{
                1: {
                    'from': 0 //zero denotes user
                    'direction': 0
                },
                2: {
                    'from': 0
                    'direction': 1
                },
                3: {
                    'from': 2 //from point 2
                    'direction': 0
                }
            }
        }

        result if list of objects with their relative position:

        {
            'visual': [
                {
                    'position': (1, 0),
                    'object': object
                },
                {
                    'position': (0, 1),
                    'object': object
                },
                {
                    'position': (1, 1),
                    'object': object
                }
            ]
        }

        """
        fighter_x, fighter_y, fighter_direction = self.fighter.x, self.fighter.y, self.fighter.direction
        parameters = json.loads(self.module.proto.parameters)
        field_of_vision = parameters['field_of_vision']
        result = []
        for key in xrange(1, 1000):
            if key not in field_of_vision:
                break
            item = field_of_vision[key]
            delta_direction = (item['direction'] + fighter_direction) % 6
            delta_vector = Battlefield.DIRECTIONS[delta_direction]
            delta_source = item['from']
            if delta_source == 0:
                start_x, start_y = 0, 0
            elif delta_source < key:
                start_x, start_y = result[delta_source + 1]['position']
            else:
                break
            x, y = start_x + delta_vector[0], start_y + delta_vector[1]

            result.append({
                'position': (x, y),
                'object': battlefield.get_visual_object_at(fighter_x + x, fighter_y + y)
            })
        return {'visual': result}


class AnalyzerWrapper(object):
    def __init__(self, fighter, module):
        self.fighter = fighter
        self.module = module

    def process(self, data):
        return {}


class ObjectDetectorModule(AnalyzerWrapper):
    def process(self, data):
        if 'visual' in data:
            data['objects'] = self.process_visual(data['visual'])

    def process_visual(self, data):
        result = []
        for item in data:
            type = item['object']['type']
            if type == 'fighter':
                result.append(item)
            elif isinstance(item['object'], int):
                if item['object'] != Arena.EMPTY:
                    result.append(item)
        return result


class FriendOrFoeModule(AnalyzerWrapper):
    def process(self, data):
        if 'objects' in data:
            self.process_visual(data['objects'])

    def process_visual(self, data):
        result = []
        for item in data:
            type = item['object']['type']
            if type == 'fighter':
                fighter = item['object']['object']
                item['is_friend'] = fighter.teamid == self.fighter.teamid
                result.append(item)
        return result


class RangeFinderModule(AnalyzerWrapper):
    def process(self, data):
        if 'objects' in data:
            self.process_visual(data['objects'])

    def process_visual(self, data):
        result = []
        for item in data:
            x, y = item['position']
            item['distance'] = max(abs(x), abs(y), abs(x + y))
        return result


class RandomRovingModule(AnalyzerWrapper):
    def process(self, data):
        direction = random.randint(0, 6)
        if not 'goto' in data:
            data['goto'] = []
        data['goto'].append({'vector': Battlefield.DIRECTIONS[direction], 'priority': 0})


class WeaponModuleWrapper(object):
    def __init__(self, fighter, module):
        self.fighter = fighter
        self.module = module

    def process(self, data, weapon):
        return []


class GetTargetsInFirezoneModule(WeaponModuleWrapper):
    def process(self, data, weapon):
        result = []
        if 'objects' in data:
            for object in data['objects']:
                if 'distance' in object and object['distance'] <= weapon.range:
                    if object['type'] == 'fighter' and 'is_friend' in object and not object['is_friend']:
                        result.append(object)
        weapon.targets = result


class DecisionMaker(object):
    def __init__(self, fighter):
        self.fighter = fighter

    def process(self, data, weapons, motion):
        commands = {'shoot': [], 'goto': (0, 0)}
        can_fire = False
        for weapon in weapons:
            if hasattr(weapon, 'targets') and weapon.targets:
                target = random.choice(weapon.targets)
                commands['shoot'].append({'weapon': weapon, 'position': target['position']})
                can_fire = True
        if not can_fire:
            if 'goto' in data and data['goto']:
                commands['goto'] = random.choice(data['goto'])['vector']