import pygame as pg
import sys

pg.init()
pg.mixer.init()

import time
import numpy as np
from random import randrange

from RetroVoxel import *
from myclasses import *
from movies import *
from myui import *

class MyCamera(CameraController):
	def __init__(self, pos, distance, fov, ray_num, resolution):
		super().__init__(pos, distance, fov, ray_num, resolution)
		self.is_stay = True
	
	def render(self, field, assets, entities, aspect, fog_color=None, fog_distance=0.5, skybox=None):
		original_pos = deepcopy(self.pos)
		height = 0.5
		stay_dispersion = 0.05
		walk_dispersion = 0.05
		stay_dispersion_duration = 2
		walk_dispersion_duration = 0.75
		result_height = 0
		result_height += height
		if self.is_stay:
			result_height+=math.sin(anim_loop(stay_dispersion_duration)*2*math.pi)*stay_dispersion
		else:
			result_height+=math.sin(anim_loop(walk_dispersion_duration)*2*math.pi)*walk_dispersion
		self.pos[2]+=result_height
		result_screen = super().render(field, assets, entities, aspect, fog_color=fog_color, fog_distance=fog_distance, skybox=skybox)
		self.pos=original_pos
		return result_screen

	def update(self, scene, screen):
		center = screen.get_rect().center
		for e in scene.events:
			if e.type == pg.MOUSEMOTION:
				if abs(e.rel[0])>1:
					self.rotate(e.rel[0]*settings["sensitivity"], 0)
					pg.mouse.set_pos(center)
					pg.event.clear()
				if abs(e.rel[1])>1:
					self.rotate(0, -e.rel[1]*settings["sensitivity"])
					pg.mouse.set_pos(center)
					pg.event.clear()
		keys = pg.key.get_pressed()
		self.is_stay = True
		if keys[pg.K_w]:
			self.is_stay = False
			self.pos[:2] += self.move_vecs[0]*3 * scene.delta_time
		if keys[pg.K_a]:
			self.is_stay = False
			self.pos[:2] += self.move_vecs[1]*3 * scene.delta_time
		if keys[pg.K_s]:
			self.is_stay = False
			self.pos[:2] += self.move_vecs[2]*3 * scene.delta_time
		if keys[pg.K_d]:
			self.is_stay = False
			self.pos[:2] += self.move_vecs[3]*3 * scene.delta_time

class MyScene(Scene):
	def __init__(self, window_size, resolution, camera_distance, camera_fov, camera_ray_num, fog_color=None, fog_distance=0.5, skybox=None):
		super().__init__(window_size, resolution, camera_distance, camera_fov, camera_ray_num, fog_color=fog_color, fog_distance=fog_distance, skybox=skybox)
		self.camera = MyCamera(vec3(0,0,0), camera_distance, camera_fov, camera_ray_num, self.global_resolution)

class Game:
	def __init__(self):
		self.WINDOW_SIZE = (pg.display.Info().current_w, pg.display.Info().current_h)
		self.screen = pg.display.set_mode(self.WINDOW_SIZE, pg.FULLSCREEN)
		pg.display.set_icon(pg.image.load("assets/icon.png"))
		pg.display.set_caption("The Castle and The Bobs")

		intro(self.screen)
		
		self.mytheme = MyTheme()
		self.loading_screen = MyLoadingScreen(self.screen)
		self.loading_screen()

		self.clock = pg.time.Clock()
		self.framerate = 30
		resolution = 8
		self.main_scene = MyScene(self.WINDOW_SIZE, resolution, settings["render_distance"], settings["render_fov"], settings["render_ray_num"], fog_color=(63,63,63), fog_distance=0.5, skybox=pg.image.load("assets/skybox.png"))

		counter = 0
		while True:
			try:
				self.main_scene.load_model(f"models/{counter}.png")
				counter+=1
			except:
				break
		
		self.main_scene.load_script("main", globals())

		self.gui = ContainerGroup({
			"start_menu":Container(self.WINDOW_SIZE, (11,7), self.mytheme),
			"credits":Container(self.WINDOW_SIZE, (11,7), self.mytheme),
			"main":Container(self.WINDOW_SIZE, (1,1), self.mytheme),
			"escape_menu":Container(self.WINDOW_SIZE, (11,7), self.mytheme)
			}, "start_menu")
		
		self.hud = MyHUD(self.WINDOW_SIZE)
		self.tooltip = MyTooltip(self.WINDOW_SIZE)
		self.dialog = MyDialog(self.WINDOW_SIZE)

		self.start_menu_screen = ImageLabel(self.gui.containers["start_menu"], (0,0), (11,7), self.screen)
		self.credits_screen = ImageLabel(self.gui.containers["credits"], (0,0), (11,7), self.screen)
		self.main_scene_screen = ImageLabel(self.gui.containers["main"], (0,0), (1,1), self.screen)
		self.escape_menu_screen = ImageLabel(self.gui.containers["escape_menu"], (0,0), (11,7), self.screen)

		def change_container(name):
			self.loading_screen()
			self.gui.change_container(name)
			self.loading_screen()

		ImageLabel(self.gui.containers["start_menu"], (1, 1), (7,1), pg.image.load("assets/logo_label.png"))
		Button(self.gui.containers["start_menu"], (1, 3), (3,1), loc["ui_start"], lambda: change_container("main"))
		Button(self.gui.containers["start_menu"], (1, 4), (3,1), loc["ui_credits"], lambda: self.gui.change_container("credits"))
		Button(self.gui.containers["start_menu"], (1, 5), (3,1), loc["ui_exit"], lambda: sys.exit())

		ImageLabel(self.gui.containers["credits"], (6,1), (4,2), pg.image.load("assets/logo_mm.png"))
		ImageLabel(self.gui.containers["credits"], (1,1), (4,2), pg.image.load("assets/logo.png"))
		Text(self.gui.containers["credits"], (1,3), (9,2), "License: GNU GPL v3.\nFonts: Vlaanderen Square NF, PerfectDOSVGA437.\nPowered by RetroVoxel and Pygame.\n© Mister Master 2023", (40,5), "CENTER", is_wrap_word=True)
		Button(self.gui.containers["credits"], (4, 5), (3,1), loc["ui_back"], lambda: self.gui.change_container("start_menu"))

		ImageLabel(self.gui.containers["escape_menu"], (1, 1), (7,1), pg.image.load("assets/logo_label.png"))
		Button(self.gui.containers["escape_menu"], (1, 3), (3,1), loc["ui_continue"], lambda: self.gui.change_container("main"))
		Button(self.gui.containers["escape_menu"], (1, 4), (3,1), loc["ui_exit"], lambda: change_container("start_menu"))

		self.panorama = Panorama_Background([
			pg.image.load("assets/panorama_background/0.png"),
			pg.image.load("assets/panorama_background/1.png"),
			pg.image.load("assets/panorama_background/2.png"),
			pg.image.load("assets/panorama_background/3.png"),
			pg.image.load("assets/panorama_background/4.png"),
			pg.image.load("assets/panorama_background/5.png"),
			pg.image.load("assets/panorama_background/6.png"),
			pg.image.load("assets/panorama_background/7.png"),
			pg.image.load("assets/panorama_background/8.png"),
			pg.image.load("assets/panorama_background/9.png"),
			pg.image.load("assets/panorama_background/10.png"),
			pg.image.load("assets/panorama_background/11.png")
		], 60)

		self.run = True

		self.main_scene.render()

		self.main_scene.props["current_music"] = "0.wav"

		for i in range(pg.mixer.get_num_channels()):
			ch = pg.mixer.Channel(i)
			ch.set_volume(settings["sound_volume"]/100)
		pg.mixer.music.set_volume(settings["music_volume"]/100)

		self.loading_screen()

	def logic(self, events):
		self.main_scene.delta_time = self.clock.get_time()/1000

		if self.gui.name=="main":
			self.main_scene.is_stop = False
			self.main_scene.is_stop_camera = False
			if self.main_scene.props.get("is_dialog", False):
				self.main_scene.is_stop_camera = True
		else:
			if not self.main_scene.is_stop:
				self.panorama.change_image()
			self.main_scene.is_stop_camera = True
			self.main_scene.is_stop = True
			self.start_menu_screen.image = self.panorama(self.WINDOW_SIZE)
			self.credits_screen.image = self.start_menu_screen.image
		
		pg.mouse.set_visible(self.main_scene.is_stop_camera)

		self.main_scene.props["tooltip"] = ""

		self.main_scene.update(events, self.screen, globals())

		self.dialog.update(self.main_scene)
		self.tooltip.update(self.main_scene)
		self.hud.update(self.main_scene)

		if self.main_scene.props.get("is_win", False):
			pg.mixer.music.pause()
			ending(self.screen)
			self.main_scene.load_script("main", globals())
			self.loading_screen()
			self.gui.change_container("start_menu")
			self.loading_screen()
			pg.mixer.music.unpause()

		if not self.gui.name in "main escape_menu":
			self.main_scene.props["current_music"] = "0"
		
		if self.main_scene.props.get("current_music", "0")!=self.main_scene.props.get("old_music", ""):
			pg.mixer.music.unload()
			pg.mixer.music.load("assets/ost/"+self.main_scene.props.get("current_music", "0")+".wav")
			pg.mixer.music.play(loops=-1)
			self.main_scene.props["old_music"] = deepcopy(self.main_scene.props.get("current_music", "0"))

		for e in events:
			if e.type == pg.KEYDOWN:
				if e.key == pg.K_ESCAPE:
					if self.gui.name in "main":
						self.gui.change_container("escape_menu")
					elif self.gui.name=="escape_menu":
						self.gui.change_container("main")
				if e.key == pg.K_F2:
					intro(self.screen)
				if e.key == pg.K_F3:
					self.loading_screen()
					waiting = True
					while waiting:
						for ev in pg.event.get():
							if ev.type == pg.KEYDOWN:
								if ev.key == pg.K_F3:
									self.loading_screen()
									waiting = False
				if e.key == pg.K_F4:
					pg.image.save(self.screen, f"screenshots/{str(time.time())}.png")
				if e.key == pg.K_F5:
					pg.image.save(self.main_scene.panorama(), f"panorama/{str(time.time())}.png")

	def visual(self, events):
		self.screen.fill((0, 0, 0))

		if self.gui.name in "main": 
			img = self.main_scene.render(); img.set_colorkey((0,0,0))
			self.main_scene_screen.image = img
			self.escape_menu_screen.image = img
		self.screen.blit(self.gui.update(events), (0,0))
		if self.gui.name in "main":
			self.screen.blit(self.hud.gui.update(events), (0,0))
			if self.main_scene.props.get("tooltip", "")!="":
				self.screen.blit(self.tooltip.gui.update(events), (0,0))
			if self.main_scene.props.get("is_dialog", False)!=False:
				self.screen.blit(self.dialog.gui.update(events), (0,0))

		pg.display.update()

	def mainloop(self):
		while self.run:

			if isinstance(self.framerate, type(None)):
				self.clock.tick()
			else:
				self.clock.tick(self.framerate)

			events = pg.event.get()
			for e in events:
				if e.type == pg.QUIT:
					self.run = False

			self.logic(events)
			self.visual(events)

		pg.quit()

if __name__ == '__main__':
	root = Game()
	root.mainloop()