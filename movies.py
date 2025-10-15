import pygame as pg
import time
import numpy as np
from random import randrange

from RetroVoxel import *
from settings import *

def intro(screen):
	clock = pg.time.Clock()

	sound = pg.mixer.Sound("assets/intro/intro.wav")

	frames_anim = Anim(lambda x: x*sound.get_length()*60+1, sound.get_length(), False)

	run = True

	frames_anim.start()
	sound.play()
	
	while run:
		clock.tick()
		events = pg.event.get()

		for e in events:
			if e.type==pg.QUIT:
				pg.quit()
				exit()

		screen.fill((0,0,0))
		frame = pg.transform.scale(pg.image.load(f"assets/intro/{min(int(frames_anim()), 300)}.png"), screen.get_size())
		screen.blit(frame, frame.get_rect(center=screen.get_rect().center))
		pg.display.update()

		run = not frames_anim.is_stop()
		
def ending(screen):
	clock = pg.time.Clock()

	sound = pg.mixer.Sound("assets/ending/ending.wav")

	frames_anim = Anim(lambda x: x*sound.get_length()*60, sound.get_length(), False)

	run = True

	frames_anim.start()
	sound.play()
	
	while run:
		clock.tick()
		events = pg.event.get()

		for e in events:
			if e.type==pg.QUIT:
				pg.quit()
				exit()

		screen.fill((0,0,0))
		frame = pg.transform.scale(pg.image.load(f"assets/ending/{int(frames_anim())%360}.png"), screen.get_size())
		screen.blit(frame, frame.get_rect(center=screen.get_rect().center))
		pg.display.update()

		run = not frames_anim.is_stop()