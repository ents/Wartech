# coding=utf-8
from collections import defaultdict
import random
import json
from logic_modules.eye import *
from main.models import User
from main.views import is_authorized, JsonResponse


def test_fight(request):
    if not is_authorized(request):
        return JsonResponse(request, {"ok": False, "error_reason": "Not authorized"})

    user = User.objects.get(pk=request.session["user_id"])
    robots = user.robots.all()
    arena = Arena.objects.all()[0]
    journal = fight(robots, robots, arena)
    return JsonResponse(request, {"ok": True, "journal": journal})


class Battlefield(dict):
    def __init__(self, arena, fight_journal):
        super(Battlefield, self).__init__()
        self.arena = arena
        self.fight_journal = fight_journal
        for i, kind in enumerate(json.loads(arena.terrain)):
            x, y = self.translate_point_to_hexagone(i)
            self[x, y] = kind

    def translate_point_to_hexagone(self, i):
        x, y = divmod(i, self.arena.width)
        y = -(y//2)
        return x, y

    def place_fighter_at_random_position(self, fighter):
        counter = 1000
        while counter:
            counter -= 1
            x, y = self.translate_point_to_hexagone(random.randint(0, len(self.arena) - 1))
            if self[x, y] == Arena.EMPTY:
                self[x, y] = fighter
                fighter.x, fighter.y = x, y
                fighter.direction = random.randint(0, 5)
                self.fight_journal.append("%s placed at (%s, %s)" % (fighter.name, x, y))
                break
        if not counter:
            raise Exception("cannot place fighter: not enough space")

    def get_visual_object_at(self, x, y):
        type = 'error'
        object = None
        if (x, y) in self:
            item = self[x, y]
            object = item
            if isinstance(item, Fighter):
                type = 'fighter'
            elif isinstance(item, int):
                type = 'nature'
        return {'type': type, 'object': object}

    def move_fighter(self, fighter):
        dx, dy = fighter.goto
        x, y = fighter.x + dx, fighter.y + dy
        if self[x, y] == Arena.EMPTY:
            self.fight_journal.append("%s moving (%s, %s)" % (fighter.name, dx, dy))
            self[fighter.x, fighter.y] = Arena.EMPTY
            self[x, y] = fighter
            fighter.x, fighter.y = x, y
        else:
            self.fight_journal.append("%s fails to move (%s, %s)" % (fighter.name, x, y))


class Fighter(object):
    def __init__(self, robot, teamid):
        self.robot = robot
        self.teamid = teamid
        slots = defaultdict(list)
        for module in self.robot.hull.modules:
            slots[module.proto.slot].append(module)
        self.slots = slots
        self.sensors = [SensorWrapper(self, module) for module in slots['sensor']]
        self.analyzers = [AnalyzerWrapper(self, module) for module in slots['analyzer']]
        self.decision = DecisionMaker(slots['decision'])
        self.motion = MotionWrapper(slots['motion'])
        self.weapon = [WeaponModuleWrapper(module) for module in slots['weapon']]
        self.health = 100

    def process(self, battlefield):
        data = defaultdict(list)
        for module in self.sensors:
            data.update(module.process(battlefield))
        for module in self.analyzers:
            data.update(module.process(data))
        commands = self.decision.process(data, self.weapon, self.motion)
        self.goto = commands['goto']
        return commands['shoot']

    def bullet_hit(self, bullet):
        self.health -= 10
        return -10

    @property
    def alive(self):
        return self.health > 0

    @property
    def name(self):
        return "R%s.%s" % (self.teamid, self.robot.id)


def fight(arena, *teams):
    fight_journal = []

    battlefield = Battlefield(arena, fight_journal)
    fighters = []
    for robots in teams:
        teamid = id(robots)
        for robot in robots:
            fighter = Fighter(robot, teamid)
            fighters.append(fighter)

    for fighter in fighters:
        battlefield.place_fighter_at_random_position(fighter)

    idle_counter = 0
    while True:
        if not fighters:
            fight_journal.append("Fight finished: no more alive fighters found")
            break

        idle = True
        shoots = []
        for fighter in fighters:
            if fighter.alive:
                bullets = fighter.process(battlefield)
                for bullet in bullets:
                    target = bullet['target']
                    fight_journal.append("%s fires at %s" % (fighter.name, target.name))
                shoots.extend(bullets)
        for shoot in shoots:
            target = battlefield[shoot['target_position']]
            if isinstance(target, Fighter):
                idle = False
                bullet = shoot['bullet']
                hit = target.bullet_hit(bullet)
                fight_journal.append("%s received %s damage" % (target.name, hit))

        for fighter in list(fighters):
            if fighter.alive:
                battlefield.move_fighter(fighter)
            else:
                fight_journal.append("%s is dead" % fighter.name)
                fighters.remove(fighter)

        if idle:
            idle_counter += 1
        if idle_counter > 100:
            fight_journal.append("Fight finished: 100 cycles without shooting&hitting. It's really boring")
    return fight_journal

