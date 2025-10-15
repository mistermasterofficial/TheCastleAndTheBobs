def on_load(scene):
	from random import randrange
	import json

	class Exit_Board(NPC):
		def update(self, scene):
			super().update(scene)

			if self.properties["index"]>0:
				sys.exit()

	class Fly(NPC):
		def update(self, scene):
			super().update(scene)

			if self.properties["anim"].is_stop():
				self.properties["anim"].start()

			x = self.properties["anim"]()

			self.properties["is_fly_back"] = False
			if x>1:
				self.properties["is_fly_back"] = True
				x = 2 - x
			
			delta_pos = self.properties["end_pos"]-self.properties["start_pos"]

			moving_vec = delta_pos*x

			self.pos = self.properties["start_pos"]+moving_vec

			if self.properties["is_fly_back"]:
				self.texture_name = "fly_back_" + str(int(anim_loop(0.5)*2))
			else:
				self.texture_name = "fly_" + str(int(anim_loop(0.5)*2))

	class Knight(NPC):
		def update(self, scene):
			super().update(scene)

			if self.properties["text_num"]==0:
				self.properties["text"] = self.properties["first_text"]

				if self.properties["index"] in [0,1]:
					self.texture_name = "interested"
				elif self.properties["index"] in [2,3,8,11]:
					self.texture_name = "smile"
				elif self.properties["index"] in [4,9]:
					self.texture_name = "scary_smile"
				elif self.properties["index"] in [10]:
					self.texture_name = "command"
				elif self.properties["index"] in [5,6,7]:
					self.texture_name = "speaking"

				if self.properties["index"]==11:
					for c in scene.props["portal_to_start"]:
						scene.collision_field[c[2]][c[1]][c[0]] = 0
					self.properties["next_text_num"] = 1
			elif self.properties["text_num"]==1:
				self.properties["text"] = self.properties["second_text"]

				self.texture_name = "command"
			
			elif self.properties["text_num"]==2:
				self.properties["text"] = self.properties["third_text"]

				if self.properties["index"] in [0,1,2]:
					self.texture_name = "smile"
				elif self.properties["index"] in [3]:
					self.texture_name = "scary_smile"

				if self.properties["index"]==len(self.properties["text"])-1:
					scene.collision_field[scene.props["portal_to_end"][2]][scene.props["portal_to_end"][1]][scene.props["portal_to_end"][0]] = 0

			if scene.props["pickedup_bobs"]>=5:
				self.properties["next_text_num"] = 2

			if self.properties["index"]==-1:
				self.texture_name = "default"
				if self.properties["next_text_num"]!=self.properties["text_num"]:
					self.properties["text_num"]=deepcopy(self.properties["next_text_num"])

	class SleepingKnight(NPC):
		def update(self, scene):
			super().update(scene)

			duration = 2
			frames_num = 2
			self.texture_name = "default_"+str(int(anim_loop(duration)*frames_num))

	with open("maps/0.txt", "r") as f:
		data = json.load(f)

	scene.field = np.array(data["map"])
	scene.collision_field = np.full(np.shape(scene.field), 0)

	bobs = {
		"1":[],
		"2":[],
		"3":[],
		"4":[],
		"5":[]
	}

	scene.props["music_points"] = []

	for p in data["points"]:
		if p[3]=="collide":
			scene.collision_field[int(p[2])][int(p[1])][int(p[0])] = 1
		elif "collide_cell" in p[3]:
			cell = int(p[3].replace("collide_cell ", ""))
			for i in range(np.shape(scene.field)[0]):
				for j in range(np.shape(scene.field)[1]):
					for k in range(np.shape(scene.field)[2]):
						if scene.field[i][j][k]==cell:
							scene.collision_field[np.shape(scene.field)[0]-1-i][j][k] = 1
		elif p[3]=="start_pos":
			scene.camera.pos = vec3(p[0],p[1],p[2])
		elif "relief_cell" in p[3]:
			cell_id, relief = p[3].replace("relief_cell ", "").split(" ")
			cell_id, relief = int(cell_id), json.loads(relief)
			scene.collision.relief_cells.append(relief)
			for i in range(np.shape(scene.field)[0]):
				for j in range(np.shape(scene.field)[1]):
					for k in range(np.shape(scene.field)[2]):
						if scene.field[i][j][k]==cell_id:
							scene.collision_field[np.shape(scene.field)[0]-1-i][j][k] = len(scene.collision.relief_cells)+1
		elif "spawn_bob" in p[3]:
			bobs[p[3].replace("spawn_bob ", "")].append(vec3(int(p[0])+0.5,int(p[1])+0.5,int(p[2])))
		elif p[3]=="portal_to_end":
			scene.props["portal_to_end"] = (int(p[0]), int(p[1]), int(p[2]))
		elif p[3]=="portal_to_start":
			scene.props["portal_to_start"] = scene.props.get("portal_to_start", [])
			scene.props["portal_to_start"].append((int(p[0]), int(p[1]), int(p[2])))
		elif "spawn_decor" in p[3]:
			scene.spawn_entity(Decoration(p[3].replace("spawn_decor ", ""),
				{
					"0":pg.image.load(f"assets/entity/decoration/{p[3].replace('spawn_decor ', '')}.png")
				},
				"0",
				(1.5,1.5), vec3(int(p[0])+0.5,int(p[1])+0.5,int(p[2]))
			))
		elif "spawn_anim_decor" in p[3]:
			textures = []
			counter = 0
			try:
				while True:
					textures.append(pg.image.load(f"assets/entity/decoration/{p[3].replace('spawn_anim_decor ', '')}/{counter}.png"))
					counter+=1
			except:
				pass

			assets = {}
			for i in range(len(textures)):
				assets[str(i)] = textures[i]

			scene.spawn_entity(Decoration(p[3].replace("spawn_anim_decor ", ""),
				assets,
				"0",
				(1.5,1.5), vec3(int(p[0])+0.5,int(p[1])+0.5,int(p[2])),
				properties={
					"is_animated":True,
					"duration":1,
				}
			))
		elif p[3]=="exit_board":
			scene.spawn_entity(Exit_Board("exit_board",
				{
					"default":pg.image.load("assets/entity/decoration/exit_board.png")
				},
				"default",
				(1,1), vec3(*p[:3]),
				properties={
					"label":loc["exit_board_label"],
					"index":-1,
					"text":loc["exit_board_text"]
				}
			))
		elif "spawn_music" in p[3]:
			scene.props["music_points"].append(MusicPoint(p[3].split(" ")[1], float(p[3].split(" ")[2]), vec3(float(p[0]), float(p[1]), float(p[2]))))

	scene.camera.rotate(-90, 0)

	scene.props["pickedup_bobs"] = 0

	for b in bobs:
		scene.spawn_entity(Bob(bobs[b][randrange(len(bobs[b]))]))

	for c in scene.props["portal_to_start"]:
		scene.collision_field[c[2]][c[1]][c[0]] = 1

	scene.spawn_entity(NPC("bee",
		{
			"default":pg.image.load("assets/entity/npc/bee/default.png")
		},
		"default",
		(0.75,0.75), vec3(7.5,37.5,1),
		properties={
			"label":loc["bee_label"],
			"index":-1,
			"text":loc["bee_text"]
		}
	))

	scene.spawn_entity(Fly("fly",
		{
			"fly_0":pg.image.load("assets/entity/npc/fly/fly_0.png"),
			"fly_1":pg.image.load("assets/entity/npc/fly/fly_1.png"),
			"fly_back_0":pg.image.load("assets/entity/npc/fly/fly_back_0.png"),
			"fly_back_1":pg.image.load("assets/entity/npc/fly/fly_back_1.png")
		},
		"fly_0",
		(0.5,0.5), vec3(26.5,14.5,1.25),
		properties={
			"label":loc["fly_label"],
			"index":-1,
			"text":loc["fly_text"],
			"start_pos":vec3(26.5,14.5,1.25),
			"end_pos":vec3(31.5,14.5,1.25),
			"anim":Anim(lambda x: x*2, 5, True),
			"is_fly_back":False
		}
	))

	scene.spawn_entity(NPC("white_hat",
		{
			"default":pg.image.load("assets/entity/npc/white_hat/default.png")
		},
		"default",
		(1,1), vec3(39.5,37.5,1),
		properties={
			"label":loc["white_hat_label"],
			"index":-1,
			"text":loc["white_hat_text"]
		}
	))

	scene.spawn_entity(NPC("lamp_bourgeois",
		{
			"default":pg.image.load("assets/entity/npc/lamp/default.png")
		},
		"default",
		(1,1), vec3(13.5,15.5,1),
		properties={
			"label":loc["lamp_bourgeois_label"],
			"index":-1,
			"text":loc["lamp_bourgeois_text"]
		}
	))

	scene.spawn_entity(NPC("woodcutter",
		{
			"default":pg.image.load("assets/entity/npc/woodcutter/default.png")
		},
		"default",
		(1,1), vec3(4.5,58.5,1),
		properties={
			"label":loc["woodcutter_label"],
			"index":-1,
			"text":loc["woodcutter_text"]
		}
	))

	scene.spawn_entity(NPC("mystery_guy",
		{
			"default":pg.image.load("assets/entity/npc/mystery_guy/default.png")
		},
		"default",
		(0.75,0.75), vec3(5.5,70.5,1),
		properties={
			"label":loc["mystery_guy_label"],
			"index":-1,
			"text":loc["mystery_guy_first_text"]
		}
	))

	scene.spawn_entity(Knight("knight", 
		{
			"default":pg.image.load("assets/entity/npc/knight/default.png"),
			"interested":pg.image.load("assets/entity/npc/knight/interested.png"),
			"command":pg.image.load("assets/entity/npc/knight/command.png"),
			"scary_smile":pg.image.load("assets/entity/npc/knight/scary_smile.png"),
			"smile":pg.image.load("assets/entity/npc/knight/smile.png"),
			"speaking":pg.image.load("assets/entity/npc/knight/speaking.png")
		}, 
		"default",
		(1,1), vec3(22.5,36.5,1), 
		properties={
		"label":loc["knight_label"],
		"index":-1,
		"first_text":loc["knight_first_text"],
		"second_text":loc["knight_second_text"],
		"third_text":loc["knight_third_text"],
		"text_num":0,
		"next_text_num":0
		}
	))
	
	scene.spawn_entity(SleepingKnight("sleeping_knight", {
		"default_0":pg.image.load("assets/entity/npc/sleeping_knight/default_0.png"),
		"default_1":pg.image.load("assets/entity/npc/sleeping_knight/default_1.png")
		}, "default_0", (1,1), vec3(24.5,36.5,1),
		properties={
			"label":loc["sleeping_knight_label"],
			"index":-1,
			"text":loc["sleeping_knight_text"]
		}
	))
	
	scene.props["is_win"] = False

def on_run(scene):
	for p in scene.props["music_points"]:
		p.update(scene)

	scene.props["current_music"] = deepcopy(scene.props["music"])
	
	if int(scene.camera.pos[0])==scene.props["portal_to_end"][0] and int(scene.camera.pos[1])==scene.props["portal_to_end"][1] and int(scene.camera.pos[2])==scene.props["portal_to_end"][2]:
		scene.props["is_win"] = True

	point_a = deepcopy(scene.camera.pos)
	point_b = deepcopy(scene.camera.pos)
	point_b[2]-=point_b[2]%1
	while True:
		if scene.collision_field[int(point_b[2])-1][int(point_b[1])][int(point_b[0])]==1 or point_b[2]-1<0:
			break
		point_b[2]-=1
	scene.camera.pos = scene.collision.collide(point_a, point_b, scene.collision_field)

	if scene.props["pickedup_bobs"]>=5:
		e = scene.get_entity("mystery_guy")
		e.properties["text"] = loc["mystery_guy_second_text"]

def on_render(scene, screen):
	return screen