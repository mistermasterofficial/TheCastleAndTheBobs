import pygame as pg
import time
import numpy as np
from random import randrange

from RetroVoxel import *
from settings import *

class MusicPoint(Entity):
	def __init__(self, filename, distance, pos):
		self.filename = filename
		self.distance = distance
		self.pos = pos
	
	def update(self, scene):
		if lenght2(scene.camera.pos[:2]-self.pos[:2])<=self.distance:
			scene.props["music"] = self.filename

class NPC(Entity):
	def update(self, scene):
		distance = lenght2(lenght2(scene.camera.pos[:2]-self.pos[:2])*scene.camera.main_vec[:2]+scene.camera.pos[:2]-self.pos[:2])
		max_distance = 1
		if distance<=self.size[0]/2 and lenght2(scene.camera.pos[:2]-self.pos[:2])<=max_distance and not scene.props.get("is_dialog", False):
			scene.props["tooltip"] = loc["dialog_start_tooltip"]
		
		if lenght2(scene.camera.pos[:2]-self.pos[:2])<=max_distance and not scene.props.get("is_dialog", False):
			for e in scene.events:
				if e.type==pg.MOUSEBUTTONUP:
					if e.button==1:
						scene.props["dialog_object"]=self
						scene.props["is_dialog"]=True
						pg.mouse.set_pos((scene.window_size[0]//2,scene.window_size[1]//2))
	
class Decoration(Entity):
	def update(self, scene):
		if self.properties.get("is_animated", False):
			self.texture_name = str(int(len(self.assets)*anim_loop(self.properties["duration"])))

class Bob(Entity):
	def __init__(self, pos, properties={}):
		size = 0.5
		super().__init__(f"Bob",{
				"default_0":pg.image.load(f"assets/entity/bob/default_0.png"),
				"default_1":pg.image.load(f"assets/entity/bob/default_1.png"),
				"default_2":pg.image.load(f"assets/entity/bob/default_2.png"),
				"default_3":pg.image.load(f"assets/entity/bob/default_3.png"),
				"default_4":pg.image.load(f"assets/entity/bob/default_4.png"),
				"default_5":pg.image.load(f"assets/entity/bob/default_5.png"),
			},"default_0",(size,size),pos,properties=properties)
		self.original_pos = deepcopy(pos)
		self.pickup_sound = pg.mixer.Sound("assets/sounds/pickup.wav")
		
	def update(self, scene):
		max_distance = 0.5

		anim_duration = 1.5
		jump_duration = 5
		jump_height = 0.125
		self.texture_name = f"default_{int(anim_loop(anim_duration)*6)}"
		self.pos[2] = self.original_pos[2]+(math.sin(anim_loop(jump_duration)*2*math.pi)+1)/2*jump_height

		distance = lenght2(lenght2(scene.camera.pos[:2]-self.pos[:2])*scene.camera.main_vec[:2]+scene.camera.pos[:2]-self.pos[:2])
		if distance<=self.size[0]/2 and lenght2(scene.camera.pos[:2]-self.pos[:2])<=max_distance:
			scene.props["tooltip"] = loc["pickup_bob_tooltip"]

		if lenght2(scene.camera.pos[:2]-self.pos[:2])<=max_distance:
			for e in scene.events:
				if e.type==pg.MOUSEBUTTONUP:
					if e.button==1:
						scene.props["pickedup_bobs"]+=1
						self.pickup_sound.play()
						scene.entities.remove(self)