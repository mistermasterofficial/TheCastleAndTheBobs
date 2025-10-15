import pygame as pg
import time
import numpy as np
from random import randrange

from RetroVoxel import *
from settings import *

class LoadingScreen:
	def __init__(self, screen):
		self.screen = screen
		self.clock = pg.time.Clock()
		self.is_run = False
	
	def draw(self):
		pass
	
	@thread
	def __call__(self):
		self.is_run = not self.is_run
		while self.is_run:
			self.clock.tick()
			self.screen.fill((0,0,0))
			self.draw()
			pg.display.update()

class MyLoadingScreen(LoadingScreen):
	def __init__(self, screen):
		super().__init__(screen)

		self.mytheme = MyTheme()
		self.gui = Container(self.screen.get_size(), (5,5), self.mytheme)
		self.duration = 2
		self.background_change_duration = 100

		self.anim_frames = [pg.image.load(f"assets/loading/{i}.png") for i in range(16)]
		self.background_frames = [pg.image.load(f"assets/loading/background/{i}.png") for i in range(12)]

		self.background = ImageLabel(self.gui, (0,0), (5,5), self.background_frames[0])
		self.label = Label(self.gui, (1,3), (1,1), loc["ui_loading"])
		self.anim_label = ImageLabel(self.gui, (3,3), (1,1), self.anim_frames[0])
	
	def draw(self):
		self.background.image = self.background_frames[int(anim_loop(self.background_change_duration)*len(self.background_frames))]
		self.anim_label.image = self.anim_frames[int(anim_loop(self.duration)*len(self.anim_frames))]

		self.screen.blit(self.gui.update([]), (0,0))

class MyHUD:
	def __init__(self, window_size):
		self.gui = Container(window_size, (50,50/(window_size[0]/window_size[1])), HUDTheme())
		self.anim_frames = [pg.image.load(f"assets/entity/bob/default_{i}.png") for i in range(6)]
		self.image = ImageLabel(self.gui, (1,1), (3,3), self.anim_frames[0])
		self.bob_info = Label(self.gui, (4,1), (3,3), "0")
	
	def update(self, scene):
		duration = 1
		self.image.image = self.anim_frames[int(anim_loop(duration)*len(self.anim_frames))]
		self.bob_info.text = str(scene.props["pickedup_bobs"])

class MyTooltip:
	def __init__(self, window_size):
		self.gui = Container(window_size, (3,5), TooltipTheme())
		self.tooltip_label = Label(self.gui, (1, 3), (1,1), "")
	
	def update(self, scene):
		self.tooltip_label.text = scene.props.get("tooltip", "")

class MyDialog:
	def __init__(self, window_size):
		self.gui = Container(window_size, (6,10), DialogTheme())

		self.index = 0
		def next():
			self.index+=1
		def last():
			self.index-=1
		
		self.label = Label(self.gui, (1, 6), (2,1), "")
		self.text = Text(self.gui, (1, 7), (4,2), "", (40, 5), "LEFT", is_wrap_word=True)
		Button(self.gui, (3, 9), (2,1), loc["dialog_next"], next)
		Button(self.gui, (1, 9), (2,1), loc["dialog_last"], last)

	def update(self, scene):
		if scene.props.get("is_dialog", False):
			text = scene.props["dialog_object"].properties["text"]
			if self.index<len(text) and self.index>=0:
				self.label.text = scene.props["dialog_object"].properties["label"]
				scene.props["dialog_object"].properties["index"] = self.index
				self.text.text = text[self.index]
			else:
				scene.props["dialog_object"].properties["index"] = -1
				self.label.text = ""
				scene.props["is_dialog"] = False
				scene.props["dialog_object"] = None
				self.index = 0

class MyTheme(BasicTheme):
	def __init__(self):
		super().__init__()

		self.font = pg.font.Font("assets/font.ttf", 36)

		self.hover_sound = pg.mixer.Sound("assets/sounds/hover2.wav")
		# self.hover_sound.set_volume(0)
		self.press_sound = pg.mixer.Sound("assets/sounds/press2.wav")
		# self.press_sound.set_volume(0)

		self.default_fg = (1,1,1)
		self.default_bg = (0,0,0)

		self.hover_fg = (255,255,255)
		self.hover_bg = (1,1,1)

		self.pressed_bg = (255,255,255)
		self.pressed_fg = (1,1,1)

class DialogTheme(BasicTheme):
	def __init__(self):
		super().__init__()

		self.font = pg.font.Font("assets/font.ttf", 36)

		self.hover_sound = pg.mixer.Sound("assets/sounds/hover1.wav")
		self.press_sound = pg.mixer.Sound("assets/sounds/press1.wav")

		self.default_fg = (255,255,255)
		self.default_bg = (1,1,1)

		self.hover_bg = (255,255,255)
		self.hover_fg = (1,1,1)

		self.pressed_fg = (255,255,255)
		self.pressed_bg = (1,1,1)

class TooltipTheme(BasicTheme):
	def __init__(self):
		super().__init__()

		self.font = pg.font.Font("assets/font.ttf", 36)

		self.default_fg = (255,255,255)
		self.default_bg = (1,1,1)

class HUDTheme(BasicTheme):
	def __init__(self):
		super().__init__()

		self.font = pg.font.Font("assets/font.ttf", 36)

		self.default_fg = (1,1,1)
		self.default_bg = (0,0,0)

class Panorama_Background:
	def __init__(self, images, duration):
		self.images = images
		self.duration = duration
		self.image_num = 0

	def __call__(self, window_size):
		image = pg.transform.scale(self.images[self.image_num], (self.images[self.image_num].get_width()/(self.images[self.image_num].get_height()/window_size[1]),window_size[1]))
		x = anim_loop(self.duration)
		screen = pg.Surface(window_size)
		screen.blit(image, (-x*image.get_width(),0))
		screen.blit(image, (-x*image.get_width()+image.get_width(),0))
		return screen
	
	def change_image(self):
		self.image_num = randrange(len(self.images))