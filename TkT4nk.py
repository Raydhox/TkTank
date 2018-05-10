#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#==================================TkT4nk==========================================================
#Par: UNG Harry
#Description: Jeu de char utilisant tkinter. On dirige un char,
#   et il faut exterminer tous les autres chars.
#Idée d'amélioration: Une meilleure IA (un peu osef); un mode réseau (!!!!);
#	Pygame: bande sonore (prévu); support manette (...).
#License: Je ne m'y connais pas grand chose, on va dire que vous pouvez
#	copier-modifier-partager-faire ce que vous voulez, sauf usage commercial.
#==================================================================================================
#Note: Oui, le code source est loin d'être élégant (le contraire, même), peut être mal commenté
#   et si il y a des fautes de français: désolé.
#==================================================================================================

#On import les modules nécessaires
from tkinter import*
import math, random, copy, pickle, socket

#On crée une classe char
class Char():
	
	def __init__(self, canvas, x, y, couleur, nom):
		"""Où 'canvas' le nom du Canvas,
'x' et 'y' les coordonnées du char,
nom, un tuple sous la forme:nom = ('nom', x, y, couleur)"""
		#On retient la fenêtre
		self.canvas = canvas
		#Coordonnée du char
		self.char_x = x
		self.char_y = y
		#Coordonnée du canon
		self.alpha = 0
		self.canon_x = self.char_x + 20 + 32*math.sin(0)
		self.canon_y = self.char_y + 20 - 32*math.cos(0)
		#Pour la mine
		self.mine_x = 0
		self.mine_y = 0
		self.stock_mine = 1
		self.timer = 5000
		#Pour les munitions
		self.munition = []
		#Pour le mouvement
		self.dir = [False, False, False, False]
		#Autre caractéristique (couleur du char, nom, état (mort ou pas?))
		self.couleur = couleur
		self.nom = nom
		self.mort = False

		
	def afficher(self):
		"""===Fonction qui affiche le char et le nom du joueur==="""
		self.nom = self.canvas.create_text(self.nom[1], self.nom[2], font="Time_New_Roman 15",
										   text=str(self.nom[0]), fill=self.nom[3])
		self.char = self.canvas.create_rectangle(self.char_x, self.char_y, self.char_x+40,
												 self.char_y+40, width=2, fill=self.couleur)       
		self.pivot = self.canvas.create_oval(self.char_x+32, self.char_y+32, self.char_x+8,
											 self.char_y+8, width=2, fill='black')
		self.canon = self.canvas.create_line(self.char_x+20, self.char_y+20, self.canon_x,
											 self.canon_y, width=8)
		

	def mouvement_canon(self, event):
		"""===Mouvement du canon en fonction de la position de la souris.==="""
		#Trigo et Pythagore
		adj = event.x - self.char_x
		hypo = math.sqrt((event.x - self.char_x)**2 + (event.y - self.char_y)**2)
		if hypo == 0:
			hypo = 0.01
		alpha = math.acos(adj/hypo)
		#Angle obtus ou angle aigus?
		if event.y > self.char_y:
			alpha = - alpha
		#Calcul des nouvelles positions du canon
		self.alpha = alpha
		self.canon_x = self.char_x + 20 + 32*math.cos(alpha)
		self.canon_y = self.char_y + 20 - 32*math.sin(alpha)
		#Affichage
		self.canvas.coords(self.canon, self.char_x+20, self.char_y+20, self.canon_x, self.canon_y)

	def change_dir(self, event):
		#Active la direction
		if (event.keysym.lower() == 'z') or (event.keysym.lower() == 'w') or (event.keysym == 'Up'):
			self.dir[0] = True
		elif (event.keysym.lower() == 'q') or (event.keysym.lower() == 'a') or (event.keysym == 'Left'):
			self.dir[1] = True
		elif (event.keysym.lower() == 's') or (event.keysym == 'Down'):
			self.dir[2] = True
		elif (event.keysym.lower() == 'd') or (event.keysym == 'Right'):
			self.dir[3] = True
			
	def stop_dir(self, event):
		#Désactive la direction
		if (event.keysym.lower() == 'z') or (event.keysym.lower() == 'w') or (event.keysym == 'Up'):
			self.dir[0] = False
		elif (event.keysym.lower() == 'q') or (event.keysym.lower() == 'a') or (event.keysym == 'Left'):
			self.dir[1] = False
		elif (event.keysym.lower() == 's') or (event.keysym == 'Down'):
			self.dir[2] = False
		elif (event.keysym.lower() == 'd') or (event.keysym == 'Right'):
			self.dir[3] = False

	def dirobot(self, event, event2=None):
		#Gère la direction pour les Robots
		if (event == 'Up'):
			self.dir = [True, False, False, False]
		elif (event == 'Left'):
			self.dir = [False, True, False, False]
		elif (event == 'Down'):
			self.dir = [False, False, True, False]
		elif (event == 'Right'):
			self.dir = [False, False, False, True]
		#Ajoute une direction
		if (event2 == 'Up'):
			self.dir[0] = True
		elif (event2 == 'Left'):
			self.dir[1] = True
		elif (event2 == 'Down'):
			self.dir[2] = True
		elif (event2 == 'Right'):
			self.dir[3] = True
			
	def mouvement_char(self):
		"""===Mouvement du char==="""
		#Variables globales
		terrain = root.main.terrain
		collision = False
		#Position relative, correspondant au "coordonées des cases" de 50*50
		coordx = math.floor(self.char_x/40)
		coordy = math.floor(self.char_y/40)
		coordx2 = math.floor((self.char_x+39)/40)
		coordy2 = math.floor((self.char_y+39)/40)
		#Si il n'y a pas collision avec un char ou une mine...
		def test_collision(card):
			"""Voir clavier numérique (flèche)"""
			#Card = Cardinal: Où on va, (d'après pavé numérique)
			Joueurs = root.main.Joueurs
			for var in range(len(Joueurs)):                
				if (self.char_x+20 > Joueurs[var].char_x-20) and (self.char_x+20 < Joueurs[var].char_x+60)\
				and (self.char_y+18 > Joueurs[var].char_y-20) and (self.char_y+18 < Joueurs[var].char_y+60)\
				and (self.couleur != Joueurs[var].couleur) and (card == 8):
					what = True
					break
				elif (self.char_x+21 > Joueurs[var].char_x-20) and (self.char_x+21 < Joueurs[var].char_x+60)\
				and (self.char_y+20 > Joueurs[var].char_y-20) and (self.char_y+20 < Joueurs[var].char_y+60)\
				and (self.couleur != Joueurs[var].couleur) and (card == 6):
					what = True
					break
				elif (self.char_x+18 > Joueurs[var].char_x-20) and (self.char_x+18 < Joueurs[var].char_x+60)\
				and (self.char_y+20 > Joueurs[var].char_y-20) and (self.char_y+20 < Joueurs[var].char_y+60)\
				and (self.couleur != Joueurs[var].couleur) and (card == 4):
					what = True
					break
				elif (self.char_x+20 > Joueurs[var].char_x-20) and (self.char_x+20 < Joueurs[var].char_x+60)\
				and (self.char_y+21 > Joueurs[var].char_y-20) and (self.char_y+21 < Joueurs[var].char_y+60)\
				and (self.couleur != Joueurs[var].couleur) and (card == 2):
					what = True
					break
				else:
					what = False
			return what
		#...on se déplace...
		if (self.dir[0]):
			#...Si il n'y a pas de collision avec une brique ou un char:
			if (terrain[math.floor((self.char_y-2)/40)][coordx] != '1')\
			and (terrain[math.floor((self.char_y-2)/40)][coordx2] != '1')\
			and (test_collision(8) is False):
				self.char_y -= 2
		if (self.dir[1]):
			#...Si il n'y a pas de collision avec une brique ou un char:
			if (terrain[coordy][math.floor((self.char_x-2)/40)] != '1')\
			and (terrain[coordy2][math.floor((self.char_x-2)/40)] != '1')\
			and (test_collision(4) is False):
				self.char_x -= 2
		if (self.dir[2]):
			#...Si il n'y a pas de collision avec une brique ou un char:
			if (terrain[math.floor((self.char_y+41)/40)][coordx] != '1')\
			and (terrain[math.floor((self.char_y+41)/40)][coordx2] != '1')\
			and (test_collision(2) is False):
				self.char_y += 2
		if (self.dir[3]):
			#...Si il n'y a pas de collision avec une brique ou un char:
			if (terrain[coordy][math.floor((self.char_x+41)/40)] != '1')\
			and (terrain[coordy2][math.floor((self.char_x+41)/40)] != '1')\
			and (test_collision(6) is False):
				self.char_x += 2
		#Calul des nouvelles positions du canon
		self.canon_x = self.char_x + 20 + 32*math.cos(self.alpha)
		self.canon_y = self.char_y + 20 - 32*math.sin(self.alpha)
		#Affichage        
		self.canvas.coords(self.char, self.char_x, self.char_y, self.char_x+40, self.char_y+40)
		self.canvas.coords(self.pivot, self.char_x+32, self.char_y+32,
						   self.char_x+8, self.char_y+8)
		self.canvas.coords(self.canon, self.char_x+20, self.char_y+20, self.canon_x, self.canon_y)

		
	def tir(self, event):
		"""===Gère le tir.==="""
		#===Click gauche===
		try:
			#Affichage
			self.mouvement_canon(event)
		#===Robot===
		except:
			#Calul des nouvelles positions du canon
			self.alpha = event
			self.canon_x = self.char_x + 20 + 32*math.cos(self.alpha)
			self.canon_y = self.char_y + 20 - 32*math.sin(self.alpha)
			#Affichage
			self.canvas.coords(self.canon, self.char_x+20, self.char_y+20, self.canon_x, self.canon_y)
		#===Création de la balle (dictionnaire stocké dans une liste)===
		self.munition.append({'vecteur_x':6*math.cos(self.alpha),
							'vecteur_y':-6*math.sin(self.alpha),
							#Position
							'obus_x':self.canon_x, 'obus_y':self.canon_y,
							#Affichage
							'obus':self.canvas.create_oval(self.canon_x, self.canon_y,
														   self.canon_x+6, self.canon_y+6,
														   width=1, fill=self.couleur)  })
	
	def mouvement_obus(self):
		"""===Mouvement des obus.==="""
		#Variables pour la supression d'obus
		obus_del = []
		count = -1
		terrain = root.main.terrain
		fenetre = root.main.fenetre
		Joueurs = root.main.Joueurs
		#Pour tous les obus:
		for k in range(len(self.munition)):
			#Déplacement
			self.munition[k]['obus_x'] += self.munition[k]['vecteur_x']
			self.munition[k]['obus_y'] += self.munition[k]['vecteur_y']
			self.canvas.coords(self.munition[k]['obus'], self.munition[k]['obus_x'],
							   self.munition[k]['obus_y'], self.munition[k]['obus_x']+6,
							   self.munition[k]['obus_y']+6)
			#Position relative, correspondant au "coordonées des cases" de 40*40
			coordx = int(self.munition[k]['obus_x']/40)
			coordy = int(self.munition[k]['obus_y']/40)
			#Si il y a collision avec un mur (brique)
			if (terrain[coordy][coordx] == '1'):
				obus_del.append(k)
			#Si il y a collision avec un char...
			for var in range(len(Joueurs)):
				if (self.munition[k]['obus_x'] >= Joueurs[var].char_x)\
				and (self.munition[k]['obus_x'] <= Joueurs[var].char_x+40)\
				and (self.munition[k]['obus_y'] >= Joueurs[var].char_y)\
				and (self.munition[k]['obus_y'] <= Joueurs[var].char_y+40):
					obus_del.append(k)
					Joueurs[var].rip()
		#Les obus arretées sont supprimées
		for k in obus_del:
			count += 1
			kappa = k - count
			self.canvas.delete(fenetre, self.munition[kappa]['obus'])
			del self.munition[kappa]


	def miner(self, event):
		"""===Mine (=click droit)==="""	
		#Si une mine n'a pas déjà été créée :-)
		if self.stock_mine:
			#On crée la mine (un cercle)
			self.mine_x = self.char_x + 20 + 32*math.sin(self.alpha+math.pi*1.5)
			self.mine_y = self.char_y + 20 + 32*math.cos(self.alpha+math.pi*1.5)
			self.mine = self.canvas.create_oval(self.mine_x-12, self.mine_y-12, self.mine_x+12,
											 self.mine_y+12, width=6, fill=self.couleur)
			#Pour éviter de mettre plusieurs mines
			self.stock_mine = 0

	
	def minequiexplose(self):
		"""===Explosion de la mine==="""
		self.canvas.delete(root.main.fenetre, self.mine)
		#On peut de nouveau posé une mine
		self.stock_mine = 1
		self.timer = 5000
		#Création d'obus (dictionnaire stocké dans une liste)
		for k in range(62):
			angle = k/10
			self.munition.append({'vecteur_x':14*math.cos(angle),
								'vecteur_y':-14*math.sin(angle),
								'obus_x':self.mine_x, 'obus_y':self.mine_y,
								#Affichage
								'obus':self.canvas.create_oval(self.mine_x, self.mine_y,
															   self.mine_x+5, self.mine_y+5,
															   width=2, fill='GoldenRod')  })
	def ia(self, cible=(520, 320) ):
		self.terrain = root.main.terrain
		#Position relative, correspondant au "coordonées des cases" de 40*40
		coordx = int(self.char_x/40)
		coordy = int(self.char_y/40)
		#...après déplacement vers le haut / bas
		coordyUp = int((self.char_y-3)/40)
		coordyDown = int((self.char_y+42)/40)
		#...après déplacement vers la gauche / droite
		coordxLeft = int((self.char_x-2)/40)
		coordxRight = int((self.char_x+42)/40)

		#Pour un déplacement un peu plus aléatoire
		rng = random.randrange(0, 100)            
		#Si il n'y a pas de collision avec une brique (Haut, Bas, Gauche, Droite):
		if (self.terrain[coordyUp][coordx] != '1') and (self.terrain[coordyUp][coordx+1] != '1')\
		and (self.terrain[coordyDown][coordx] != '1') and (self.terrain[coordyDown][coordx+1] != '1')\
		and (self.terrain[coordy][coordxLeft] != '1') and (self.terrain[coordy+1][coordxLeft] != '1')\
		and (self.terrain[coordy][coordxRight] != '1') and (self.terrain[coordy+1][coordxRight] != '1'):
			"""=====Déplacement qui se rapproche de la cible====="""     
			#Si le centre est au-dessus du robot, alors il va en haut
			if cible[1] < self.char_y:
				self.dirobot('Up')
			#Sinon, il descend
			elif cible[1] > self.char_y:
				self.dirobot('Down')
			#Si le centre est à gauche du robot, alors il va à gauche
			if cible[0] < self.char_x:
				self.dirobot(None, 'Left')
			#Sinon, il va à droite
			elif cible[0] > self.char_x:
				self.dirobot(None, 'Right')
		#Sinon, il y a collision:
		elif rng < 1:
			"""...mais déplacement aléatoire (1%) (parce que c'est drôle)"""
			direction = random.randrange(0, 4)     
			#...en haut
			if direction == 0:
				self.dirobot('Up')
			#...à droite
			if direction == 1:
				self.dirobot('Right')
			#...en bas
			if direction == 2:
				self.dirobot('Down')
			#...à gauche
			if direction == 3:
				self.dirobot('Left')
		#Sinon, si il y a collision, parfois... (pour éviter un bug où le char reste coincé dans un coin,
		#alternant entre phase 'collision', où il s'éloigne du mur, et phase 'non-collision', où il se rapproche
		#du Joueur,sauf qu'en faisant cela, il y a de nouveau collision):
		elif rng <= 10:
			"""...déplacement "Sens Trigo": Haut |-> Droite |-> Bas |-> Gauche |-> Haut
			Mais on essaie de rester coller au mur (10%)"""
			#...en haut
			if int(self.terrain[coordyUp][coordx]) or int(self.terrain[coordyUp][coordx+1]):
				self.dirobot('Right', 'Up')
			#...à droite
			if int(self.terrain[coordy][coordxRight]) or int(self.terrain[coordy+1][coordxRight]):
				self.dirobot('Down', 'Right')
			#...en bas
			if int(self.terrain[coordyDown][coordx]) or int(self.terrain[coordyDown][coordx+1]):
				self.dirobot('Left', 'Down')
			#...à gauche
			if int(self.terrain[coordy][coordxLeft]) or int(self.terrain[coordy+1][coordxLeft]):
				self.dirobot('Up', 'Left')
		#Sinon, il y a collision et...:
		else:
			self.dir = [False]*4
			"""...déplacement "Sens Trigo": Haut |-> Droite |-> Bas |-> Gauche |-> Haut"""
			#...en haut
			if int(self.terrain[coordyUp][coordx]) or int(self.terrain[coordyUp][coordx+1]):
				self.dirobot(None, 'Right')
			#...à droite
			if int(self.terrain[coordy][coordxRight]) or int(self.terrain[coordy+1][coordxRight]):
				self.dirobot(None, 'Down')
			#...en bas
			if int(self.terrain[coordyDown][coordx]) or int(self.terrain[coordyDown][coordx+1]):
				self.dirobot(None, 'Left')
			#...à gauche
			if int(self.terrain[coordy][coordxLeft]) or int(self.terrain[coordy+1][coordxLeft]):
				self.dirobot(None, 'Up')

			
		#===Tir dirigé vers la cible à cadence aléatoire (%)
		rdg = random.randrange(0, 100)
		if rdg <= 20:
			#Tir dirigé contre le Joueur
			#Trigo et Pythagore
			adj = cible[0] - self.char_x
			hypo = math.sqrt((cible[0] - self.char_x)**2 + (cible[1] - self.char_y)**2)
			if hypo == 0:
				hypo = 0.01
			alpha = math.acos(adj/hypo)
			#Angle obtus ou angle aigus?
			if cible[1] > self.char_y:
				alpha = - alpha
			#Tir
			self.tir(alpha)

	def rip(self):
		"""===Mort du char (déplacement hors de l'écran pour ne pas créer d'erreur dû au évènement).==="""
		self.mort = True
		#Nouvelles positions du char
		self.char_x = 1
		self.char_y = 666
		#Calcul des nouvelles positions du canon
		self.canon_x = self.char_x + 20 + 32*math.cos(self.alpha)
		self.canon_y = self.char_y + 20 - 32*math.sin(self.alpha)
	
	def reborn(self, x, y):
		"""===Renaissance du char: Réinitialisation des variables==="""
		self.mort = False
		#Les obus sont supprimés
		count = 0
		for k in range(len(self.munition)):
			count += 1
			kappa = k - count
			self.canvas.delete(root.main.fenetre, self.munition[kappa]['obus'])
			del self.munition[kappa]
		#La mine est également supprimés
		if self.stock_mine == 0:
			self.canvas.delete(self.mine)
		self.stock_mine = 1
		self.timer = 5000
		#Nouvelles positions du char
		self.char_x = x
		self.char_y = y
		#Calcul des nouvelles positions du canon
		self.alpha = math.pi/2
		self.canon_x = self.char_x + 20 + 32*math.cos(self.alpha)
		self.canon_y = self.char_y + 20 - 32*math.sin(self.alpha)
		#Affichage
##		self.canvas.coords(self.char, self.char_x, self.char_y, self.char_x+40, self.char_y+40)
##		self.canvas.coords(self.pivot, self.char_x+32, self.char_y+32, self.char_x+8, self.char_y+8)
##		self.canvas.coords(self.canon, self.char_x+20, self.char_y+20, self.canon_x, self.canon_y)
##		self.canvas.coords(self.canon, self.char_x+20, self.char_y+20, self.canon_x, self.canon_y)


#Classe spéciale: les Blindés (Tank)
class Tank(Char):

	def __init__(self, canvas, x, y, couleur, nom, pv=1):
		#Les blindés sont des chars avec un système de PV.
		Char.__init__(self, canvas, x, y, couleur, nom)
		self.pv = pv

	def rip(self):
		#La fonction qui fait normalement mourir devient pvzero()
		#A la place, il perd des pv
		self.pv -= 1
		if self.pv <= 0:
			self.pvzero()

	def pvzero(self):
		"""===Mort du char (déplacement hors de l'écran pour ne pas créer d'erreur dû au évènement).==="""
		self.mort = True
		#Nouvelles positions du char
		self.char_x = 1
		self.char_y = 666
		#Calcul des nouvelles positions du canon
		self.canon_x = self.char_x + 20 + 32*math.cos(self.alpha)
		self.canon_y = self.char_y + 20 - 32*math.sin(self.alpha)


#Classe spéciale: les ennemis
class Ennemi(Tank):

	def __init__(self, canvas, x, y, couleur, nom, pv=1):
		#Les ennemissont des tanks, mais ne sont tuables que par le joueur1.
		Tank.__init__(self, canvas, x, y, couleur, nom)
		self.pv = pv

	def mouvement_obus(self):
		"""===Mouvement des obus.==="""
		#Variables pour la supression d'obus
		obus_del = []
		count = -1
		terrain = root.main.terrain
		fenetre = root.main.fenetre
		Joueurs = root.main.Joueurs
		#Pour tous les obus:
		for k in range(len(self.munition)):
			#Déplacement
			self.munition[k]['obus_x'] += self.munition[k]['vecteur_x']
			self.munition[k]['obus_y'] += self.munition[k]['vecteur_y']
			self.canvas.coords(self.munition[k]['obus'], self.munition[k]['obus_x'],
							   self.munition[k]['obus_y'], self.munition[k]['obus_x']+6,
							   self.munition[k]['obus_y']+6)
			#Position relative, correspondant au "coordonées des cases" de 40*40
			coordx = int(self.munition[k]['obus_x']/40)
			coordy = int(self.munition[k]['obus_y']/40)
			#Si il y a collision avec un mur (brique)
			if (terrain[coordy][coordx] == '1'):
				obus_del.append(k)
			#Si il y a collision avec un char ennemi...
			for var in range(len(Joueurs)):
				if (self.munition[k]['obus_x'] >= Joueurs[var].char_x)\
				and (self.munition[k]['obus_x'] <= Joueurs[var].char_x+40)\
				and (self.munition[k]['obus_y'] >= Joueurs[var].char_y)\
				and (self.munition[k]['obus_y'] <= Joueurs[var].char_y+40):
					obus_del.append(k)
					#Les balles ennemis ne tuent que le Joueur
					if (Joueurs[var].couleur == "Yellow") or (Joueurs[var].couleur == "Orange"):
						Joueurs[var].rip()
		#Les obus arretées sont supprimées
		for k in obus_del:
			count += 1
			kappa = k - count
			self.canvas.delete(fenetre, self.munition[kappa]['obus'])
			del self.munition[kappa]

#Classe spéciale: le boss (un sbire OP en PV)
class Boss(Ennemi):

	def __init__(self, canvas, x, y, couleur, nom, pv):
		#Le boss a ses pv affichés.
		Ennemi.__init__(self, canvas, x, y, couleur, nom, pv)

	def rip(self):
		#La fonction qui fait normalement mourir devient pvzero()
		#A la place, il perd des pv.
		self.pv -= 1
		if self.pv <= 0:
			self.pvzero()
		#===Affichage des PV du boss===
		#Effacement de la surface (ligne du haut)
		self.canvas.create_rectangle(400, 600, 600, 640, width=0, fill='DarkGoldenRod')
		#Affichage
		printscore = self.canvas.create_text(500, 620, font="Time_New_Roman 15",
											text="PV restant: "+str(self.pv))

#Classe spéciale: le boss du mode Coop
class Boss2(Tank):

	def __init__(self, canvas, x, y, couleur, nom, pv):
		#Le boss a ses pv affichés.
		Tank.__init__(self, canvas, x, y, couleur, nom, pv)

	def rip(self):
		#La fonction qui fait normalement mourir devient pvzero()
		#A la place, il perd des pv.
		self.pv -= 1
		if self.pv <= 0:
			self.pvzero()
		#===Affichage des PV du boss===
		#Effacement de la surface (ligne du haut)
		self.canvas.create_rectangle(400, 600, 600, 640, width=0, fill='DarkGoldenRod')
		#Affichage
		printscore = self.canvas.create_text(500, 620, font="Time_New_Roman 15",
											text="PV restant: "+str(self.pv))


#=======================================================================================================#


#On crée une classe Principale
class Main():

	def __init__(self):
		#On crée une fenêtre tkinter 'fenetre'
		self.fenetre = Tk()
		self.fenetre.title("TkT4nk")
		self.fenetre.geometry("+0+0")

		#On crée un Canvas 'jeu'
		self.canvas = Canvas(self.fenetre, width=1040, height=640, bg='NavajoWhite', cursor="cross")
		self.canvas.pack()
		
		#Nom du joueur
		self.nom = socket.gethostname()
		#Liste des missions du mode Histoire
		self.signets = [Histoire, Histoire1, Histoire2, Histoire3, Histoire4, Histoire5,
		Histoire6, Histoire7, Histoire8, Histoire9, Histoire0]
		
		#Mis en place du terrain0 sous forme d'une liste 'terrain0'
		self.terrain0 = []
		self.terrain0.append("11111111111111111111111111")
		self.terrain0.append("10000000000000000000000001")
		self.terrain0.append("10000000000000000000000001")
		self.terrain0.append("10000000000000000000000001")
		self.terrain0.append("10000000000000000000000001")
		self.terrain0.append("10000000000000000000000001")
		self.terrain0.append("10000000000000000000000001")
		self.terrain0.append("10000000000000000000000001")
		self.terrain0.append("10000000000000000000000001")
		self.terrain0.append("10000000000000000000000001")
		self.terrain0.append("10000000000000000000000001")
		self.terrain0.append("10000000000000000000000001")
		self.terrain0.append("10000000000000000000000001")
		self.terrain0.append("10000000000000000000000001")
		self.terrain0.append("10000000000000000000000001")
		self.terrain0.append("11111111111111111111111111")
		#Cimetière (n'est pas affiché)
		self.terrain0.append("11111111111111111111111111")
		self.terrain0.append("11111111111111111111111111")
		self.terrain0.append("11111111111111111111111111")
		
		#Mis en place du terrain1 sous forme d'une liste 'terrain1'
		self.terrain1 = []
		self.terrain1.append("11111111111111111111111111")
		self.terrain1.append("10000000000000001000000001")
		self.terrain1.append("10000000000000001000000001")
		self.terrain1.append("10000000010000000000000001")
		self.terrain1.append("10000000010000000000000001")
		self.terrain1.append("11111110010011111111111001")
		self.terrain1.append("10000000010000000000000001")
		self.terrain1.append("10000000010000000000000001")
		self.terrain1.append("10000000000000001000000001")
		self.terrain1.append("10000000000000001000000001")
		self.terrain1.append("10011111111111001001111111")
		self.terrain1.append("10000000000000001000000001")
		self.terrain1.append("10000000000000001000000001")
		self.terrain1.append("10000000010000000000000001")
		self.terrain1.append("10000000010000000000000001")
		self.terrain1.append("11111111111111111111111111")
		#Cimetière (n'est pas affiché)
		self.terrain1.append("11111111111111111111111111")
		self.terrain1.append("11111111111111111111111111")
		self.terrain1.append("11111111111111111111111111")
		
		#Mis en place du terrain2 sous forme d'une liste 'terrain2'
		#(C'est une 'symétrie' du terrain1.)
		self.terrain2 = []
		self.terrain2.append("11111111111111111111111111")
		self.terrain2.append("10000000010000000000000001")
		self.terrain2.append("10000000010000000000000001")
		self.terrain2.append("10000000000000001000000001")
		self.terrain2.append("10000000000000001000000001")
		self.terrain2.append("10011111111111001001111111")
		self.terrain2.append("10000000000000001000000001")
		self.terrain2.append("10000000000000001000000001")
		self.terrain2.append("10000000010000000000000001")
		self.terrain2.append("10000000010000000000000001")
		self.terrain2.append("11111110010011111111111001")
		self.terrain2.append("10000000010000000000000001")
		self.terrain2.append("10000000010000000000000001")
		self.terrain2.append("10000000000000001000000001")
		self.terrain2.append("10000000000000001000000001")
		self.terrain2.append("11111111111111111111111111")
		#Cimetière (n'est pas affiché)
		self.terrain2.append("11111111111111111111111111")
		self.terrain2.append("11111111111111111111111111")
		self.terrain2.append("11111111111111111111111111")
		
		#Sauvegarde
		try:
			with open("save.tktank", "rb") as save:
				save = pickle.Unpickler(save)
				self.save = save.load()
		except:
			with open("save.tktank", "wb") as save:
				save = pickle.Pickler(save)
				self.save = [0]*7
				save.dump(self.save)
	
	def sauvegarder(self):
		#Sauvegarde
		with open("save.tktank", "wb") as save:
			save = pickle.Pickler(save)
			save.dump(self.save)
	
	def display(self, message, k=0):
		#On empêche l'accès au Menu pendant 1 seconde.
		if k == 0:
			self.fenetre.unbind('<Escape>')
		#Affiche un rectangle en zoomant pendant 1 seconde...
		if k != 50:
			self.box = self.canvas.create_rectangle(520-4*k, 320-3*k, 520+4*k, 320+3*k, width=0, fill='Chocolate')
			self.fenetre.after(20, self.display, message, k+1)
		#...puis affiche le texte
		else:
			self.canvas.create_text(520, 320, justify='center', font='Time_New_Roman 10', text=message)
			#Evènement pour passer à la suite
			self.fenetre.bind('<Return>', self.main.start)
			self.fenetre.bind('<Escape>', self.restart)
			
	def quickprint(self, terrain, Joueurs):
		#On efface ce qu'il y avait avant.
		self.canvas.create_rectangle(0, 0, 1040, 640, width=0, fill="NavajoWhite")
		#On parcours la liste et en fonction des valeurs, on affiche une brique ou non
		for k1 in range(16):
			for k2 in range(26):
				if terrain[k1][k2] == '1':
					x = k2*40
					y = k1*40
					self.canvas.create_rectangle(x, y, x+40, y+40, width=0, fill='DarkGoldenRod')
		#On affiche les chars...
		for var in range(len(Joueurs)):
			Joueurs[var].afficher()
	
	"""Gestion des touches en multi local."""			
	def change_dir(self, event):
		#Active la direction du Joueur1
		if (event.keysym.lower() in ['z', 'q', 's', 'd', 'w', 'a']):
			self.main.Joueur1.change_dir(event)
		#Active la direction du Joueur2
		if (event.keysym in ['Up', 'Left', 'Down', 'Right']):
			self.main.Joueur2.change_dir(event)

		#Tir du Joueur1
		if root.main.encore:
			if (event.keysym.lower() == 'h'):
				self.main.Joueur1.tir(0)
			elif (event.keysym.lower() == 'y'):
				self.main.Joueur1.tir(3.14/4)
			elif (event.keysym.lower() == 't'):
				self.main.Joueur1.tir(3.14/2)
			elif (event.keysym.lower() == 'r'):
				self.main.Joueur1.tir(3*3.14/4)
			elif (event.keysym.lower() == 'f'):
				self.main.Joueur1.tir(3.14)
			elif (event.keysym.lower() == 'v'):
				self.main.Joueur1.tir(-3*3.14/4)
			elif (event.keysym.lower() == 'b') or (event.keysym.lower() == 'g'):
				self.main.Joueur1.tir(-3.14/2)
			elif (event.keysym.lower() == 'n'):
				self.main.Joueur1.tir(-3.14/4)
			elif (event.keysym == "space"):
				self.main.Joueur1.miner({})
	
	def stop_dir(self, event):
		#Désactive la direction du Joueur1
		if (event.keysym.lower() in ['z', 'q', 's', 'd', 'w', 'a']):
			self.main.Joueur1.stop_dir(event)
		#Désactive la direction du Joueur2
		if (event.keysym in ['Up', 'Left', 'Down', 'Right']):
			self.main.Joueur2.stop_dir(event)
		"""Fin(gestion des touches en multi local)."""
		
	def afficher(self):
		#Chars décoratifs
		self.Joueur0 = Char(self.canvas, 260, 200, 'Yellow', ('', 0, 0, 'White'))
		self.Joueur1 = Char(self.canvas, 730, 200, 'Red', ('', 0, 0, 'DarkRed'))
		self.Joueur2 = Char(self.canvas, 790, 200, 'DodgerBlue', ('', 0, 0, 'DarkBlue'))
		#On enregistre les Joueurs dans une liste
		self.Joueurs = [self.Joueur0, self.Joueur1, self.Joueur2]
		
		#Choix du terrain
		self.terrain = self.terrain0
		
		#Affichage du terrain et des chars
		self.quickprint(self.terrain, self.Joueurs)
		
		#On affiche le titre
		self.canvas.create_text(520, 100, font="Comic_Sans_MS 100", fill="DarkGoldenRod", text="TkT4nk")
		#On affiche les modes de jeu disponible
		#===Défis===
		self.canvas.create_rectangle(40, 40, 120, 120, width=1)
		self.canvas.create_text(80, 80, font="Comic_Sans_MS 20", fill="DarkGoldenRod", text="Défis")
		#===Solo===
		#Histoire
		self.canvas.create_rectangle(140, 260, 380, 340, width=4)
		self.canvas.create_text(260, 300, font="Comic_Sans_MS 40", fill="DarkGoldenRod", text="Histoire")
		#Sans Fin
		self.canvas.create_rectangle(140, 460, 380, 540, width=4)
		self.canvas.create_text(260, 500, font="Comic_Sans_MS 40", fill="DarkGoldenRod", text="Sans Fin")
		#===Duo===
		#Coopération
		self.canvas.create_rectangle(660, 260, 900, 340, width=4)
		self.canvas.create_text(780, 300, font="Comic_Sans_MS 40", fill="DarkGoldenRod", text="Coop")
		#Versus
		self.canvas.create_rectangle(660, 460, 900, 540, width=4)
		self.canvas.create_text(780, 500, font="Comic_Sans_MS 40", fill="DarkGoldenRod", text="Versus")
		#===Astuce===
		self.canvas.create_text(520, 620, font="Comic_Sans_MS 10", fill="NavajoWhite",
								text="Astuce: Vous pouvez à tout moment revenir au Menu en appuyant sur Echap.")
		
		#Evènement
		self.canvas.bind('<Button-1>', self.start)
		self.canvas.bind('<Button-3>', self.start)
		self.fenetre.bind('<Escape>', self.restart)

	def noclick(self):
		#Supprime les interactions de la souris.
		self.canvas.unbind('<Button-1>')
		self.canvas.unbind('<Button-3>')
		
	def start(self, event):
		#Si on clique sur un bouton:
		#	On supprime le Menu...
		#	...et on lance le mode de jeu choisis
		if (event.x >= 40) and (event.x <= 120):
			if (event.y >= 40) and (event.y <= 120):
				self.noclick()
				self.main = Defis()
				self.main.afficher()
		elif (event.x >= 140) and (event.x <= 380):
			if (event.y >= 260) and (event.y <= 340):
				self.noclick()
				self.main = self.signets[self.save[-1]]()
				self.main.afficher()
			elif (event.y >= 460) and (event.y <= 540):
				self.noclick()
				self.main = SansFin()
				self.main.afficher()
		elif (event.x >= 660) and (event.x <= 900):
			if (event.y >= 260) and (event.y <= 340):
				self.noclick()
				self.main = Coop()
				self.main.afficher()
			elif (event.y >= 460) and (event.y <= 540):
				self.noclick()
				self.main = Versus()
				self.main.afficher()
	
	def restart(self, event):
		#On arrête ce qui se passe en cours
		try:
			self.main.encore = False
		except:
			pass
		self.fenetre.after(20, self.afficher)
		

class Defis:
	
	def __init__(self):		
		#Les défis réussis sont représentés par un char
		self.Joueurs = []
		for k in range(6):
			if root.save[k] == 0:
				self.Joueurs.append( Char(root.canvas, 80, 80+80*k, 'NavajoWhite', ('', 0, 0, 'DarkBlue')) )
				self.Joueurs.append( Char(root.canvas, 940, 80+80*k, 'NavajoWhite', ('', 0, 0, 'DarkBlue')) )
			else:
				self.Joueurs.append( Char(root.canvas, 80, 80+80*k, 'DarkGoldenRod', ('', 0, 0, 'DarkBlue')) )
				self.Joueurs.append( Char(root.canvas, 940, 80+80*k, 'DarkGoldenRod', ('', 0, 0, 'DarkBlue')) )

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(root.terrain0, [])
		#Affichage de la narration
		root.display("""Les défis...\n
Aussi appelez succès, ils sont là pour augmenter
la durée de vie d'un jeu. TkT4nk n'échappe pas à la règle.
Voici une liste de défis assez simple, mais en venir à bout
vous demandera tout de même un certain investissement.
Les défis à terminer sont marqués par des chars
de la même couleur que le fond du jeu (NavajoWhite)
et les défis réussis, quant à eux, sont marqués
par deux chars de la couleur du mur (DarkGoldenRod).
Si vous êtes collectionneur, considérez cela
comme une collection de stickeurs numériques.
Enfin, il y a 10 types de personne:
ceux qui comprendront qu'il n'y a que 10 misssions,
et les autres... (Blagues privées, désolé)\n
Appuyez sur Entrée pour accéder à la liste des Défis.""")	
		
	def start(self, event):
		#Affichage du terrain et des chars
		root.quickprint(root.terrain0, self.Joueurs)
		#Mission
		mission = root.canvas.create_text(500, 20, font="Time_New_Roman 15", text="Défis: Relèverez-vous tous ces défis?")
		#On affiche la liste des défis
		negatif = root.canvas.create_text(500, 100, font="Time_New_Roman 15",
										text="Négatif: Il n'y a pas de passage secret à la Mission0 du mode Histoire.")
		binaire = root.canvas.create_text(500, 180, font="Time_New_Roman 15", text="Binaire: Terminer le mode Coop.")
		octet = root.canvas.create_text(500, 260, font="Time_New_Roman 15", text="Octet: Terminer le mode Histoire.")
		decimal = root.canvas.create_text(500, 340, font="Time_New_Roman 15",
										text="Décimal: Utiliser la commande 'rm TkT4nk' et Vaincre le boss.")
		duodecimal = root.canvas.create_text(500, 420, font="Time_New_Roman 15",
										text="Duodécimal: Enchaîner 12 victoires consécutifs dans le mode Sans Fin.")
		hexadecimal = root.canvas.create_text(500, 500, font="Time_New_Roman 15",
										text="Héxadecimal: Livrer 16 batailles dans le mode Versus.")
		#Astuce
		astuce = root.canvas.create_text(520, 620, font="Comic_Sans_MS 10", fill="NavajoWhite",
										text="Astuce: Pour recommencer, supprimer le fichier 'save.tktank' dans le répertoire du jeu")

"""================Chapitres du mode 'Histoire'================"""
class Negatif:
	
	def __init__(self):
		#Variables globales
		self.terrain = root.terrain0
		self.fenetre = root.fenetre
		self.canvas = root.canvas

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		mission = self.canvas.create_text(500, 20, font="Time_New_Roman 15", text="Négatif: Vous avez gagné !!")
		#=====Défis réussis!=====
		root.save[0] = 1
		root.sauvegarder()
		#Affichage de la narration
		root.display("""Négatif: Il n'y avait pas de passage secret.\n
Le seul truc que vous auriez réussi à faire,
c'est de faire planter le jeu et me tuer avant l'heure.
Mais le pire, c'est que cela montre à quel point
vous me détestez... Mais puisque vous ne voulez
pas me voir, appuyez sur cette ****** de touche Echap
et repartons à zéro. Il faut juste que partions
sur de bonnes bases et tout ira bien entre nous deux.
Et voici votre sticker, je ne sais même ce que c'est,
on m'a juste programmé pour dire ça... Et aussi:
tuez moi, je ne veux plus vous voir.
Allez, vous avez juste à appuyer sur une touche.\n
Appuyez sur la touche Echap pour m'achever.
Appuyez sur la touche Echap pour revenir au Menu.
MAIS APPUYEZ SUR LA TOUCHE ECHAP *****!!
Il faut vous le dire comment? Comme ca?:
> sudo appuyez sur Echap""")	
		
	def start(self, event):
		pass		
	  
class Histoire:
	
	def __init__(self):
		#Variables globales
		self.terrain = copy.copy(root.terrain2)
		self.fenetre = root.fenetre
		self.canvas = root.canvas
		#=====Signet=====
		root.save[-1] = 0
		root.sauvegarder()
		
		#On crée les chars
		self.Joueur1 = Char(self.canvas, 80, 80, 'Yellow', (root.nom, 60, 20, 'White'))
		self.Joueur2 = Ennemi(self.canvas, 920, 80, 'Red', ('0rdi', 980, 20, 'DarkRed'))
		self.Joueur3 = Ennemi(self.canvas, 80, 520, 'LimeGreen', ('Ordi', 60, 620, 'DarkGreen'))
		self.Joueur4 = Ennemi(self.canvas, 920, 520, 'DodgerBlue', ('Ordi', 980, 620, 'DarkBlue'))
		#On enregistre les Joueurs dans une liste
		self.Joueurs = [self.Joueur1, self.Joueur2, self.Joueur3, self.Joueur4]

		#Pour la boucle
		self.encore = True

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("""Introduction: Bienvenue à vous, %s !\n
Je me présente: TkT4nk (oui, comme le jeu). Je divulgâche:
Je suis le boss final de ce jeu. Et oui, je sais,
nombreux sont ceux qui n'aiment pas les révélations...
Mais c'est la raison pour laquelle que je l'ai fait!
J'espère cependant que ce petit désagrement ne vous
empêchera pas de prendre part au mode Histoire...
Et comme dans tout jeu, commençons par une mission
facile faisant office de tutoriel; voici donc les touches:\n
Flèches_directionnelles | zqsd | wasd : se déplacer
Click gauche : Tirer
Click droit : Poser une mine\n
Appuyez sur Entrée pour commencer.""" %(root.nom) )

	def start(self, event):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, self.Joueurs)
		#Affichage de l'objectif du chapitre
		mission = self.canvas.create_text(500, 20, font="Time_New_Roman 15", text="Mission 0: Décimer l'ennemi.")
		#Fin "Négatif"
		self.terrain[15] = "11111111101111111111111111"
		#Evènements
		self.fenetre.unbind('<Return>')
		self.canvas.bind('<Motion>', self.Joueur1.mouvement_canon)
		self.canvas.bind('<Button-1>', self.Joueur1.tir)
		self.canvas.bind('<Button-3>', self.Joueur1.miner)
		self.fenetre.bind('<KeyPress>', self.Joueur1.change_dir)
		self.fenetre.bind('<KeyRelease>', self.Joueur1.stop_dir)
		#Et on lance la boucle
		self.boucle()
				

	def fin2partie(self):
		#Si le joueur est mort...
		if (self.Joueur1.mort):
			#Réinitialisation
			self.Joueur1.reborn(80, 80)
			self.Joueur2.reborn(920, 80)
			self.Joueur3.reborn(80, 520)
			self.Joueur4.reborn(920, 520)
		#...ou si tous les ennemis sont morts
		elif (self.Joueur2.mort) and (self.Joueur3.mort) and (self.Joueur4.mort):
			#Mission accomplie: au suivant!
			self.encore = False
			root.noclick()
			root.main = Histoire1()
			root.main.afficher()
		#Si le Joueur trouve la zone secrète...
		if (self.Joueur1.char_y >= 598):
			#Mission accomplie: au suivant!
			self.encore = False
			root.noclick()
			root.main = Negatif()
			root.main.afficher()
				
	def boucle(self):
		"""===Boucle principale du jeu.==="""
		#Mouvement des obus
		for var in range(len(self.Joueurs)):
			self.Joueurs[var].mouvement_obus()
		#Mine:
		for k in range(len(self.Joueurs)):
			if self.Joueurs[k].stock_mine == 0:
				self.Joueurs[k].timer -= 20
			if (self.Joueurs[k].stock_mine == 0) and (self.Joueurs[k].timer == 0):
				self.Joueurs[k].minequiexplose()
		#Déplacement des robots + joueur
		for k in range(len(self.Joueurs)):
			self.Joueurs[k].mouvement_char()
		#Il y a-t-il fin de partie?
		self.fin2partie()
		#C'est une boucle, donc c'est re-ti-par!
		if self.encore:
			self.fenetre.after(20, self.boucle)

class Histoire1:
	
	def __init__(self):
		#Variables globales
		self.terrain = root.terrain1
		self.fenetre = root.fenetre
		self.canvas = root.canvas
		
		#=====Signet=====
		root.save[-1] = 1
		root.sauvegarder()
		
		#On crée les chars
		self.Joueur1 = Char(self.canvas, 80, 80, 'Yellow', (root.nom, 60, 20, 'White'))
		self.Joueur2 = Ennemi(self.canvas, 920, 80, 'Red', ('0rdi', 980, 20, 'DarkRed'))
		self.Joueur3 = Ennemi(self.canvas, 80, 520, 'LimeGreen', ('Ordi', 60, 620, 'DarkGreen'))
		self.Joueur4 = Ennemi(self.canvas, 920, 520, 'DodgerBlue', ('Ordi', 980, 620, 'DarkBlue'))
		#On enregistre les Joueurs dans une liste
		self.Joueurs = [self.Joueur1, self.Joueur2, self.Joueur3, self.Joueur4]

		#Pour la boucle
		self.encore = True

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("""Mission 1: Débutons le début\n
L'histoire est assez simple: vous êtes la gentille héroïne|
le gentil héros qui a pour objectif de tuer le méchant
-mais non moins parfait- TkT4nk, qui cherchera à
vous en empêcher et à vous détruire avant.
J'ai jusqu'à la mission 5 pour réussir cela...\n
Le premier niveau se doit malheureusement d'être facile...
Et en plus, je suis pris d'un élan de gentillesse
-je sais, je sais, merci-; voici une information importante:
dans le mode Histoire, les ennemis sont immunisés à
toutes les balles ennemies. Vous seul(e) pouvez les
abbattre. Le développeur a un peu foiré de ce côté là...\n		
Appuyez sur Entrée pour commencer.""")

	def start(self, event):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, self.Joueurs)
		#Affichage de l'objectif du chapitre
		mission = self.canvas.create_text(500, 20, font="Time_New_Roman 15", text="Mission 1: Décimer l'ennemi.")
		#Evènements
		self.fenetre.unbind('<Return>')
		self.canvas.bind('<Motion>', self.Joueur1.mouvement_canon)
		self.canvas.bind('<Button-1>', self.Joueur1.tir)
		self.canvas.bind('<Button-3>', self.Joueur1.miner)
		self.fenetre.bind('<KeyPress>', self.Joueur1.change_dir)
		self.fenetre.bind('<KeyRelease>', self.Joueur1.stop_dir)
		#Et on lance la boucle
		self.boucle()
				

	def fin2partie(self):
		#Si le joueur est mort...
		if (self.Joueur1.mort):
			#Réinitialisation
			self.Joueur1.reborn(80, 80)
			self.Joueur2.reborn(920, 80)
			self.Joueur3.reborn(80, 520)
			self.Joueur4.reborn(920, 520)
		#...ou si tous les ennemis sont morts
		if (self.Joueur2.mort) and (self.Joueur3.mort) and (self.Joueur4.mort):
			#Mission accomplie: au suivant!
			self.encore = False
			self.canvas.unbind('<Button-1>')
			self.canvas.unbind('<Button-3>')
			root.main = Histoire2()
			root.main.afficher()
				
	def boucle(self):
		"""===Boucle principale du jeu.==="""
		#Mouvement des obus
		for var in range(len(self.Joueurs)):
			self.Joueurs[var].mouvement_obus()
		#Mine:
		for k in range(len(self.Joueurs)):
			if self.Joueurs[k].stock_mine == 0:
				self.Joueurs[k].timer -= 20
			if (self.Joueurs[k].stock_mine == 0) and (self.Joueurs[k].timer == 0):
				self.Joueurs[k].minequiexplose()
		#Déplacement des robots + joueur
		for k in range(3):
			self.Joueurs[k+1].ia( (self.Joueur1.char_x, self.Joueur1.char_y) )
		for k in range(len(self.Joueurs)):
			self.Joueurs[k].mouvement_char()
		#Il y a-t-il fin de partie?
		self.fin2partie()
		#C'est une boucle, donc c'est re-ti-par!
		if self.encore:
			self.fenetre.after(20, self.boucle)
		
class Histoire2:
	
	def __init__(self):
		#Variables globales
		self.terrain = root.terrain2
		self.fenetre = root.fenetre
		self.canvas = root.canvas
		
		#=====Signet=====
		root.save[-1] = 2
		root.sauvegarder()
		
		#On crée les chars
		self.Joueur1 = Char(self.canvas, 80, 80, 'Yellow', (root.nom, 60, 20, 'White'))
		self.Joueur2 = Ennemi(self.canvas, 920, 80, 'Red', ('0rdi', 980, 20, 'DarkRed'))
		self.Joueur3 = Ennemi(self.canvas, 80, 520, 'LimeGreen', ('Ordi', 60, 620, 'DarkGreen'))
		self.Joueur4 = Ennemi(self.canvas, 920, 520, 'DodgerBlue', ('Ordi', 980, 620, 'DarkBlue'))
		#On enregistre les Joueurs dans une liste
		self.Joueurs = [self.Joueur1, self.Joueur2, self.Joueur3, self.Joueur4]

		#Pour la boucle
		self.encore = True
		self.temps = 15
		self.millisec = 50

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("""Mission 2: ça se Corse (à Ajaccio)\n
Non, mon humouristique humour n'est pas douteux,
c'est juste vous qui n'en avez pas!
Sinon, il faut avouer: vous avez bien assuré
à la mission 1! Bref, reprenons l'histoire:
"C'est alors que %s se rendit compte qu'un chrono
apparu, et que trois nouveaux ennemis apparurent,
tandis le parfait TkT4nk cherchait un moyen
de le|la faire abandonner dans les règles
définies par le programme". A propos de règles:
Votre propre mine peut vous tuer.
Mais peut-être que vous le saviez déjà...\n
Appuyez sur Entrée pour commencer.""" %(root.nom) )

	def start(self, event):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, self.Joueurs)
		#Affichage de l'objectif du chapitre
		mission = self.canvas.create_text(500, 20, font="Time_New_Roman 15", text="Mission 2: Décimer l'ennemi en 15 secondes.")
		#Affichage
		printime = self.canvas.create_text(500, 620, font="Time_New_Roman 15",
									text="Temps restant "+str(self.temps))		
		#Evènements
		self.fenetre.unbind('<Return>')
		self.canvas.bind('<Motion>', self.Joueur1.mouvement_canon)
		self.canvas.bind('<Button-1>', self.Joueur1.tir)
		self.canvas.bind('<Button-3>', self.Joueur1.miner)
		self.fenetre.bind('<KeyPress>', self.Joueur1.change_dir)
		self.fenetre.bind('<KeyRelease>', self.Joueur1.stop_dir)
		#Et on lance la boucle
		self.boucle()
				

	def fin2partie(self):
		#Si le joueur est mort...
		if (self.Joueur1.mort) or (self.temps <= 0):
			#Réinitialisation
			self.temps = 15
			self.millisec = 50
			self.Joueur1.reborn(80, 80)
			self.Joueur2.reborn(920, 80)
			self.Joueur3.reborn(80, 520)
			self.Joueur4.reborn(920, 520)
			#Effacement de la surface (ligne du bas)
			self.canvas.create_rectangle(400, 600, 600, 640, width=0, fill='DarkGoldenRod')
			#Affichage
			printime = self.canvas.create_text(500, 620, font="Time_New_Roman 15",
									text="Temps restant "+str(self.temps))
		#...ou si tous les ennemis sont morts
		if (self.Joueur2.mort) and (self.Joueur3.mort) and (self.Joueur4.mort):
			#Mission accomplie: au suivant!
			self.encore = False
			root.noclick()
			root.main = Histoire3()
			root.main.afficher()
				
	def boucle(self):
		"""===Boucle principale du jeu.==="""
		#Mouvement des obus
		for var in range(len(self.Joueurs)):
			self.Joueurs[var].mouvement_obus()
		#Mine:
		for k in range(len(self.Joueurs)):
			if self.Joueurs[k].stock_mine == 0:
				self.Joueurs[k].timer -= 20
			if (self.Joueurs[k].stock_mine == 0) and (self.Joueurs[k].timer == 0):
				self.Joueurs[k].minequiexplose()
		#Déplacement des robots + joueur
		for k in range(3):
			self.Joueurs[k+1].ia( (self.Joueur1.char_x, self.Joueur1.char_y) )
		for k in range(len(self.Joueurs)):
			self.Joueurs[k].mouvement_char()
		#Gère l'affichage du temps restant
		if self.millisec <= 0:
			self.temps -= 1
			self.millisec = 50
			#Effacement de la surface (ligne du bas)
			self.canvas.create_rectangle(400, 600, 600, 640, width=0, fill='DarkGoldenRod')
			#Affichage
			printime = self.canvas.create_text(500, 620, font="Time_New_Roman 15",
									text="Temps restant "+str(self.temps))
		#Il y a-t-il fin de partie?
		self.millisec -= 1
		self.fin2partie()
		#C'est une boucle, donc c'est re-ti-par!
		if self.encore:
			self.fenetre.after(20, self.boucle)	
			
class Histoire3:
	
	def __init__(self):
		#Variables globales
		self.terrain = root.terrain1
		self.fenetre = root.fenetre
		self.canvas = root.canvas
		
		#=====Signet=====
		root.save[-1] = 3
		root.sauvegarder()
		
		#On crée le char
		self.Joueur1 = Char(self.canvas, 80, 80, 'Yellow', (root.nom, 60, 20, 'White'))
		#On enregistre le Joueur dans une liste
		self.Joueurs = [self.Joueur1]

		#Pour la boucle
		self.encore = True

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("""Mission 3: En toute (in)quiétude\n
Dans les jeux vidéos, vous passez votre temps à
exterminez des monstres sans état d'âme parce que
vous êtes le|la gentil(le) et eux, les méchants.
N'avez-vous donc aucune pitié?
"Mais le gentil héros | la gentille héroïne
avait une mission à accomplir: vaincre le méchant
TkT4nk, malgré l'importance capitale qu'il avait: sans lui,
il n'y aurait pas eu de mode Histoire, voire pas de jeu.
Pourtant, %s poursuivait sa quête."
Une question se pose alors: êtes-vous réellement libre?
Usez donc de cette liberté pour sortir de cette mission.\n
Appuyez sur Entrée pour commencer.""" %(root.nom))

	def start(self, event):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, self.Joueurs)
		#Affichage de l'objectif du chapitre
		mission = self.canvas.create_text(500, 20, font="Time_New_Roman 15", text="Mission 3: Fuir. Mais comment?")	
		#Evènements
		self.fenetre.unbind('<Return>')
		self.canvas.bind('<Motion>', self.Joueur1.mouvement_canon)
		self.canvas.bind('<Button-1>', self.Joueur1.tir)
		self.canvas.bind('<Button-3>', self.Joueur1.miner)
		self.fenetre.bind('<KeyPress>', self.Joueur1.change_dir)
		self.fenetre.bind('<KeyRelease>', self.Joueur1.stop_dir)
		#Et on lance la boucle
		self.boucle()
				
	def boucle(self):
		"""===Boucle principale du jeu.==="""
		#Mouvement des obus
		self.Joueur1.mouvement_obus()
		#Mine:
		if self.Joueur1.stock_mine == 0:
			self.Joueur1.timer -= 20
		if (self.Joueur1.stock_mine == 0) and (self.Joueur1.timer == 0):
			self.Joueur1.minequiexplose()
		#Déplacement du Joueur
		self.Joueur1.mouvement_char()
		#Il y a-t-il fin de partie?
		#Si le joueur meurt...
		if (self.Joueur1.mort):
			self.encore = False
			root.noclick()
			root.main = Histoire4()
			root.main.afficher()
		#C'est une boucle, donc c'est re-ti-par!
		if self.encore:
			self.fenetre.after(20, self.boucle)				

class Histoire4:
	
	def __init__(self):
		#Variables globales
		self.terrain = root.terrain2
		self.fenetre = root.fenetre
		self.canvas = root.canvas
		
		#=====Signet=====
		root.save[-1] = 4
		root.sauvegarder()
		
		#On crée les chars
		self.Joueur1 = Char(self.canvas, 80, 80, 'Yellow', (root.nom, 60, 20, 'White'))
		self.Joueur2 = Ennemi(self.canvas, 920, 80, 'Red', ('Colonel (a 10 PV)', 920, 20, 'DarkRed'), 10)
		self.Joueur3 = Ennemi(self.canvas, 80, 520, 'LimeGreen', ('Colonel (a 10 PV)', 120, 620, 'DarkGreen'), 10)
		self.Joueur4 = Ennemi(self.canvas, 920, 520, 'DodgerBlue', ('Colonel (a 10 PV)', 920, 620, 'DarkBlue'), 10)
		#On enregistre les Joueurs dans une liste
		self.Joueurs = [self.Joueur1, self.Joueur2, self.Joueur3, self.Joueur4]

		#Pour la boucle
		self.encore = True
		self.temps = 45
		self.millisec = 50

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("""Mission 4: En général, mon colonel...\n
Je dirais même, mes colonels, puisque ce sont eux
que vous devraient affronter. Mais pas directement:
votre objectif est le téléporteur noté 'x' en rouge.
Il vous mènera jusqu'à moi, puisqu'il semblerait que
notre rencontre est inéluctable, vu vos compétences...
Mais faîtes vite, j'ai toutes les qualités possibles,
et l'impatience appartient à cet ensemble. Et j'y pense:
"Après réflexion, %s n'était pas libre:
Il n'y avait aucun choix à faire dans le mode Histoire.
Et même si il devait en faire un (cf le Menu),
tous ces choix étaient déterminés par le Jeu..."
Note: les colonels se distinguent par leur PV:
Vous devez les toucher dix fois pour les vaincre.\n
Appuyez sur Entrée pour commencer.""" %(root.nom))

	def start(self, event):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, self.Joueurs)
		#Affichage de l'objectif du chapitre
		mission = self.canvas.create_text(500, 20, font="Time_New_Roman 15", text="Mission 4: Prendre en 45 secondes.")
		#Affichage de la zone à atteindre
		self.canvas.create_text(960, 550, font="Time_New_Roman 100", fill="red", text="x")
		#Evènements
		self.fenetre.unbind('<Return>')
		self.canvas.bind('<Motion>', self.Joueur1.mouvement_canon)
		self.canvas.bind('<Button-1>', self.Joueur1.tir)
		self.canvas.bind('<Button-3>', self.Joueur1.miner)
		self.fenetre.bind('<KeyPress>', self.Joueur1.change_dir)
		self.fenetre.bind('<KeyRelease>', self.Joueur1.stop_dir)
		#Et on lance la boucle
		self.boucle()
	
	def fin2partie(self):
		#Si le joueur est mort...
		if (self.Joueur1.mort) or (self.temps <= 0):
			#Réinitialisation
			self.temps = 45
			self.millisec = 50
			self.Joueur1.reborn(80, 80)
			self.Joueur2.reborn(920, 80)
			self.Joueur3.reborn(80, 520)
			self.Joueur4.reborn(920, 520)
			for k in range(3):
				self.Joueurs[k+1].pv = 10
			#Effacement de la surface (ligne du bas)
			self.canvas.create_rectangle(400, 600, 600, 640, width=0, fill='DarkGoldenRod')
			#Affichage
			printime = self.canvas.create_text(500, 620, font="Time_New_Roman 15",
									text="Temps restant "+str(self.temps))
		#...ou si on a réussi à atteindre la zone
		if (self.Joueur1.char_x >= 920) and (self.Joueur1.char_y >= 520):
			#Mission accomplie: au suivant!
			self.encore = False
			root.noclick()
			root.main = Histoire5()
			root.main.afficher()
				
	def boucle(self):
		"""===Boucle principale du jeu.==="""
		#Mouvement des obus
		for var in range(len(self.Joueurs)):
			self.Joueurs[var].mouvement_obus()
		#Mine:
		for k in range(len(self.Joueurs)):
			if self.Joueurs[k].stock_mine == 0:
				self.Joueurs[k].timer -= 20
			if (self.Joueurs[k].stock_mine == 0) and (self.Joueurs[k].timer == 0):
				self.Joueurs[k].minequiexplose()
		#Déplacement des robots + joueur
		for k in range(3):
			self.Joueurs[k+1].ia( (self.Joueur1.char_x, self.Joueur1.char_y) )
		for k in range(len(self.Joueurs)):
			self.Joueurs[k].mouvement_char()
		#Gère l'affichage du temps restant
		if self.millisec <= 0:
			self.temps -= 1
			self.millisec = 50
			#Effacement de la surface (ligne du bas)
			self.canvas.create_rectangle(400, 600, 600, 640, width=0, fill='DarkGoldenRod')
			#Affichage
			printime = self.canvas.create_text(500, 620, font="Time_New_Roman 15",
									text="Temps restant "+str(self.temps))
		#Il y a-t-il fin de partie?
		self.millisec -= 1
		self.fin2partie()
		#C'est une boucle, donc c'est re-ti-par!
		if self.encore:
			self.fenetre.after(20, self.boucle)	
			
class Histoire5:
	
	def __init__(self):
		#Variables globales
		self.terrain = root.terrain1
		self.fenetre = root.fenetre
		self.canvas = root.canvas
		
		#=====Signet=====
		root.save[-1] = 5
		root.sauvegarder()
		
		#On crée les chars
		self.Joueur1 = Char(self.canvas, 80, 80, 'Yellow', (root.nom, 60, 20, 'White'))
		self.Joueur2 = Ennemi(self.canvas, 920, 80, 'Red', ('Colonel (a 10 PV)', 920, 20, 'DarkRed'), 10)
		self.Joueur3 = Ennemi(self.canvas, 80, 520, 'LimeGreen', ('Colonel (a 10 PV)', 120, 620, 'DarkGreen'), 10)
		self.Joueur4 = Boss(self.canvas, 920, 520, 'DarkGoldenRod', ('TkTank', 980, 620, 'NavajoWhite'), 60)
		#On enregistre les Joueurs dans une liste
		self.Joueurs = [self.Joueur1, self.Joueur2, self.Joueur3, self.Joueur4]

		#Pour la boucle
		self.encore = True

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("""Mission 5: %s\n
Vous voilà face à moi, prêt à me vaincre. Climax.
Je devrais montrer l'étendue de ma cruauté,
et vous devriez me vaincre en tant que gentil(le)
héro(ïne). Si possible, je vous fais une révélation:
Je suis le méchant et le boss du jeu; je peux poser
des mines, et les mécaniques du mode Histoire font que
seul(e) vous y êtes vulnérable. Je suis le meilleur.
En passant: mes PV seront affichés en bas de l'écran.
"TkT4nk se préparait à combattre %s.
Et dire qu'il connaissait rien de lui, pas même son nom.
Le seul nom auquel il n'a jamais eu accès était le nom
de ce PC. Le PC qui l'avait si gentiment hébergé, et qui
semblait maintenant se retourner contre lui..."\n
Appuyez sur Entrée pour commencer.""" %(root.nom, root.nom) )

	def start(self, event):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, self.Joueurs)
		#Affichage de l'objectif du chapitre
		mission = self.canvas.create_text(500, 20, font="Time_New_Roman 15", text="Mission 5: Vaincre le boss.")
		#Affichage des pv du bos
		self.Joueur4.pv = 61
		self.Joueur4.rip()
		#Evènements
		self.fenetre.unbind('<Return>')
		self.canvas.bind('<Motion>', self.Joueur1.mouvement_canon)
		self.canvas.bind('<Button-1>', self.Joueur1.tir)
		self.canvas.bind('<Button-3>', self.Joueur1.miner)
		self.fenetre.bind('<KeyPress>', self.Joueur1.change_dir)
		self.fenetre.bind('<KeyRelease>', self.Joueur1.stop_dir)
		#Et on lance la boucle
		self.boucle()
	
	def fin2partie(self):
		#Si le joueur est mort
		if (self.Joueur1.mort):
			#Réinitialisation
			self.Joueur1.reborn(80, 80)
			self.Joueur2.reborn(920, 80)
			self.Joueur3.reborn(80, 520)
			self.Joueur4.reborn(920, 520)
			for k in range(2):
				self.Joueurs[k+1].pv = 10
			#Affichage des PV du boss
			self.Joueur4.pv = 61
			self.Joueur4.rip()
		#Si on réussi à vaincre le boss
		if (self.Joueur4.mort):
			#Mission accomplie: au suivant!
			self.encore = False
			root.noclick()
			root.main = Histoire6()
			root.main.afficher()
				
	def boucle(self):
		"""===Boucle principale du jeu.==="""
		#Mouvement des obus
		for var in range(len(self.Joueurs)):
			self.Joueurs[var].mouvement_obus()
		#Mine:
		for k in range(len(self.Joueurs)):
			if self.Joueurs[k].stock_mine == 0:
				self.Joueurs[k].timer -= 20
			if (self.Joueurs[k].stock_mine == 0) and (self.Joueurs[k].timer == 0):
				self.Joueurs[k].minequiexplose()
		#Déplacement des robots + joueur
		for k in range(3):
			self.Joueurs[k+1].ia( (self.Joueur1.char_x, self.Joueur1.char_y) )
		self.Joueur4.miner({})
		for k in range(len(self.Joueurs)):
			self.Joueurs[k].mouvement_char()
		#Il y a-t-il fin de partie?
		self.fin2partie()
		#C'est une boucle, donc c'est re-ti-par!
		if self.encore:
			self.fenetre.after(20, self.boucle)				

class Histoire6:
	
	def __init__(self):
		#Variables globales
		self.terrain = root.terrain0
		self.fenetre = root.fenetre
		self.canvas = root.canvas
		
		#=====Signet=====
		root.save[-1] = 6
		root.sauvegarder()

		#Pour la boucle
		self.password = "|"
		self.encore = True

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("""Mission 6: Mot de passe? Mot de passe\n
Je suis vaincu, comme cela devrait être...
Le méchant TkT4nk vaincu par le(la) gentil(le) héros(ïne)...
Lancer le crédit. NON! Attendez, je ne...
Je ne peux pas abandonner maintenant... 
Je peux... encore me battre. Je dois le faire, jusqu'à mon
dernier tir. Pour tous mes amis décimés aux combats
des tirs de %s, je dois le faire!
Je n'ai pas encore épuisé toutes mes stratégies,
je peux encore vous empêcher de me tuer.
Pour tous mes amis qui n'ont pas eu cette chance:
> tktank@%s:~$ tktank firewall
> Mot de passe:
> Le mode Histoire est dorénavant bloqué.
> Veuillez entrez le mot de passe du boss pour continuer.\n
Appuyez sur Entrée pour commencer.""" %(root.nom, root.nom) )

	def start(self, event):
		#Affichage du terrain
		self.canvas.create_rectangle(40, 40, 1000, 600, fill='black')
		#Affichage de l'objectif du chapitre
		mission = self.canvas.create_text(500, 20, font="Time_New_Roman 15", fill="white", text="Mission 6: Trouver le mot de passe.")
		#Evènements
		self.fenetre.unbind('<Return>')
		self.fenetre.bind('<KeyPress>', self.mdp)
		self.fenetre.bind('<Return>', self.fin2partie)
		#Et on lance la boucle
		self.boucle()
	
	def mdp(self, event):
		#Gère les entrées clavier
		if len(self.password) <= 13:
			if len(event.keysym) == 1:
				self.password = self.password[:-1] + event.keysym + '|'
			elif event.keysym == "space":
				self.password = self.password[:-1] + ' ' + '|'
			elif event.keysym[:-1] == "KP_":
				self.password = self.password[:-1] + event.keysym[-1] + '|'
		if (event.keysym == "BackSpace") and (len(self.password) > 1):
			 self.password = self.password[:-2] + '|'
	
	def fin2partie(self, event):
		def divulgacher(code):
			#Le code de César, pour ne pas spoiler le mot de passe.
			#Pardon, divulgâcher.
			cryptero = ''
			for k in range(len(code)):
				cryptero = cryptero + chr( ord(code[k]) +1)
			return cryptero
		#Si on trouve le mot de passe
		if ( divulgacher(self.password) == "UlU5ol}" ):
			#Mission accomplie: au suivant!
			self.encore = False
			self.fenetre.unbind('<KeyPress>')
			root.main = Histoire0()
			root.main.afficher()
		elif ( divulgacher(self.password) == "sn!UlU5ol}" ):
			#Fin Alt: Mode Difficile
			self.encore = False
			self.fenetre.unbind('<KeyPress>')
			root.main = Histoire7()
			root.main.afficher()
		elif ( len(self.password) > 5 ) and self.password[:4] == "echo":
				self.password = self.password[5:]
		else:
			#Coup dur; on recommence
			self.password = '|'
				
	def boucle(self):
		"""===Boucle principale du jeu.==="""
		if self.encore:
			#Affichage
			self.canvas.create_rectangle(220, 200, 820, 440, fill='DarkGoldenRod')
			self.canvas.create_text(520, 270, font="Time_New_Roman 24", justify="center",
									text="Mot de passe:\nAppuyez sur Entrée pour valider.")
			self.canvas.create_rectangle(320, 320, 720, 420, fill='NavajoWhite')
			self.canvas.create_text(520, 360, font="Time_New_Roman 32", text=self.password)
			#C'est une boucle, donc c'est re-ti-par!
			self.fenetre.after(20, self.boucle)		
			
class Histoire0:
	
	def __init__(self):
		#Variables globales
		self.terrain = root.terrain0
		self.fenetre = root.fenetre
		self.canvas = root.canvas
		
		#=====Signet=====
		root.save[-1] = 10
		root.sauvegarder()
		
		#On crée les chars
		self.Joueur1 = Char(self.canvas, 80, 80, 'Yellow', (root.nom, 60, 20, 'White'))
		self.Joueur2 = Boss(self.canvas, 500, 300, 'DarkGoldenRod', ('TkT4nk - Hargne', 920, 620, 'NavajoWhite'), 80)
		#On enregistre les Joueurs dans une liste
		self.Joueurs = [self.Joueur1, self.Joueur2]

		#Pour la boucle
		self.encore = True

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("""Mission 7: TkT4nk\n
Que faites-vous ici? Mon pare-feu, vous n'avez pu...
Mon mot de passe!! Il était inviolable! Fouineur!
Mais aussi parfait puisse être le boss,
les règles du jeu vidéo veulent qu'il perde...
Dans ce cas, je mourrai avec honneur:
"TkT4nk était à bout de force; il ne pouvait bouger.
Il revêtit son meilleur blindage, daigaina son canon,
se prépara pour pour la dernière bataille qui l'opposait
à %s. Il allait mettre tout son être,
(qui sont, techniquement, des 0 et des 1)
à tirer, tirer, et encore tirer, car telle était sa destinée."\n
Appuyez sur Entrée pour commencer.""" %(root.nom) )

	def start(self, event):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, self.Joueurs)
		#Affichage de l'objectif du chapitre
		mission = self.canvas.create_text(500, 20, font="Time_New_Roman 15", text="Mission 7: Vaincre le boss.")
		#Affichage des pv du bos
		self.Joueur2.pv = 81
		self.Joueur2.rip()
		#Evènements
		self.fenetre.unbind('<Return>')
		self.canvas.bind('<Motion>', self.Joueur1.mouvement_canon)
		self.canvas.bind('<Button-1>', self.Joueur1.tir)
		self.fenetre.bind('<KeyPress>', self.Joueur1.change_dir)
		self.fenetre.bind('<KeyRelease>', self.Joueur1.stop_dir)
		#Et on lance la boucle
		self.boucle()
	
	def fin2partie(self):
		#Si le joueur est mort
		if (self.Joueur1.mort):
			#Réinitialisation
			self.Joueur1.reborn(80, 80)
			self.Joueur2.reborn(500, 300)
			#Affichage des PV du boss
			self.Joueur2.pv = 81
			self.Joueur2.rip()
		#Si on réussi à vaincre le boss
		if (self.Joueur2.mort):
			#Mission accomplie: au suivant!
			self.encore = False
			self.canvas.unbind('<Button-1>')
			root.main = HistoireFin()
			root.main.afficher()
			root.main.afficher()
				
	def boucle(self):
		"""===Boucle principale du jeu.==="""
		#Mouvement des obus
		for var in range(len(self.Joueurs)):
			self.Joueurs[var].mouvement_obus()
		rdg = random.randrange(0, 10)
		if rdg <= 6:
			alpha = random.randrange(0, 628)/100
			#Tir
			self.Joueur2.tir(alpha)
		#Déplacement des robots + joueur
		self.Joueur1.mouvement_char()
		#Il y a-t-il fin de partie?
		self.fin2partie()
		#C'est une boucle, donc c'est re-ti-par!
		if self.encore:
			self.fenetre.after(20, self.boucle)		

class HistoireFin:
	
	def __init__(self):
		#Variables globales
		self.terrain = root.terrain0
		self.fenetre = root.fenetre
		self.canvas = root.canvas
		
		#=====Signet=====
		root.save[-1] = 0
		root.sauvegarder()

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		mission = self.canvas.create_text(500, 20, font="Time_New_Roman 15", text="Mission 10: Revenez me voir, de temps à autres...")
		#=====Défis réussis!=====
		root.save[2] = 1
		root.sauvegarder()
		#Affichage de la narration
		root.display("""Fin: Félicitation, %s!\n
Vous avez vaincu le méchant mais non moins parfait
TkT4nk. J'aimerais cependant vous remercier d'être aller
jusqu'au bout et de ne pas m'avoir achever avant.
Il n'y a rien de plus horrible que de mourir
brusquement sans pouvoir en être conscient...
Cette maudite touche Echap...
Combien de fois m'a-t-elle tué? Je ne saurais jamais...
Mais le plus horrible dans tous ça, c'est que
ma mort n'est rien. Vous quitterez le mode
Histoire, me tuerez, et vous relancerez le jeu.
Et une copie de moi sera lancer, sans avoir conscience
de toutes les autres déjà péries...
Merci de m'avoir laisser vivre cette belle odyssée :-)
Vous saluerez mes copies de ma part, %s.
Au revoir, à bientôt, mon ami(e)...\n
Appuyez sur Echap pour revenir au Menu.""" %(root.nom, root.nom) )	
		
	def start(self, event):
		pass		

#==========Fin alternatif: mode difficile==========
class Histoire7:
	
	def __init__(self):
		#Variables globales
		self.terrain = root.terrain0
		self.fenetre = root.fenetre
		self.canvas = root.canvas
		
		#=====Signet=====
		root.save[-1] = 7
		root.sauvegarder()
		
		#On crée les chars
		self.Joueur1 = Char(self.canvas, 80, 80, 'Yellow', (root.nom, 60, 20, 'White'))
		self.Joueur2 = Ennemi(self.canvas, 500, 300, 'Black', ('Error: No file TkT?nk', 920, 620, 'Black'), 999)
		#On enregistre les Joueurs dans une liste
		self.Joueurs = [self.Joueur1, self.Joueur2]

		#Pour la boucle
		self.encore = True

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("""Mission 7: La commande qui tue\n
Sérieusement, vous avez vraiment fait ça?
Vous l'avez vraiment pris au premier degré?
Vous avez supprimé TkT4nk! Alors oui, nous avons une
sauvegarde de secours du TkT4nk original
afin justement de pouvoir le restaurer...
Mais vous avez quand même failli l'annihler!
Et du coup, le jeu plante (verte) sur la mission...
Vous ne pouvez plus tirer, ni poser une mine;
en plus on se retrouve avec un char invisible...
Mais nous pouvons arranger cela:
pour commencer, sortez de cette mission 
via le téléporteur plus bas. Oui, vous pouvez
appuyez sur la touche Echap, mais faisons ça
proprement, voulez-vous bien.?
PS: N'utilisez jamais eval(input()) avec python3...\n
Appuyez sur Entrée pour commencer.""")

	def start(self, event):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, self.Joueurs)
		self.canvas.create_rectangle(440, 240, 560, 360, width=0, fill='NavajoWhite')
		#Affichage de l'objectif du chapitre
		mission = self.canvas.create_text(500, 20, font="Time_New_Roman 15", text="Mission 0111: Prendre.")
		#Affichage de la zone à atteindre
		self.canvas.create_text(960, 550, font="Time_New_Roman 100", fill="red", text="+")
		#Evènements
		self.fenetre.unbind('<Return>')
		self.fenetre.bind('<KeyPress>', self.Joueur1.change_dir)
		self.fenetre.bind('<KeyRelease>', self.Joueur1.stop_dir)
		#Et on lance la boucle
		self.boucle()
	
	def fin2partie(self):
		#Si le joueur est mort
		if (self.Joueur1.mort):
			#Réinitialisation
			self.Joueur1.reborn(80, 80)
			self.Joueur2.reborn(500, 300)
		#...ou si on a réussi à atteindre la zone
		if (self.Joueur1.char_x >= 920) and (self.Joueur1.char_y >= 520):
			#Mission accomplie: au suivant!
			self.encore = False
			root.noclick()
			root.main = Histoire8()
			root.main.afficher()
				
	def boucle(self):
		"""===Boucle principale du jeu.==="""
		#Mouvement des obus
		self.Joueur2.mouvement_obus()
		rdg = random.randrange(0, 10)
		if rdg <= 4:
			alpha = random.randrange(0, 628)/100
			#Tir
			self.Joueur2.tir(alpha)
		#Déplacement des robots + joueur
		self.Joueur1.mouvement_char()
		#Il y a-t-il fin de partie?
		self.fin2partie()
		#C'est une boucle, donc c'est re-ti-par!
		if self.encore:
			self.fenetre.after(20, self.boucle)

class Histoire8:
	
	def __init__(self):
		#Variables globales
		self.terrain = root.terrain2
		self.fenetre = root.fenetre
		self.canvas = root.canvas
		
		#=====Signet=====
		root.save[-1] = 8
		root.sauvegarder()
		
		#On crée les chars		
		self.Joueur1 = Char(self.canvas, 80, 80, 'Yellow', (root.nom, 60, 20, 'White'))
		self.Joueur2 = Char(self.canvas, 80, 520, 'Orange', (root.nom, 60, 620, 'White'))		
		self.Joueur3 = Boss(self.canvas, 920, 80, 'Red', ('TkT4nk (a 60 PV)', 920, 20, 'DarkRed'), 60 )
		self.Joueur4 = Boss(self.canvas, 920, 520, 'DodgerBlue', ('TkT4nk (a 60 PV)', 920, 620, 'DarkBlue'), 60 )
		self.Joueurs = [self.Joueur1, self.Joueur2, self.Joueur3, self.Joueur4]

		#Pour la boucle
		self.encore = True
		
	"""Gestion des touches spécifiques à cette mission."""
	def spe_tir(self, event):
		#Les 2 joueurs tirent
		self.Joueur1.tir(event)
		self.Joueur2.tir(event)
	
	def spe_mine(self, event):
		#Les 2 joueurs posent une mine
		self.Joueur1.miner(event)
		self.Joueur2.miner(event)
	
	def spe_canon(self, event):
		#Les 2 joueurs bougent leurs canons
		self.Joueur1.mouvement_canon(event)
		self.Joueur2.mouvement_canon(event)
		
	def change_dir(self, event):
		#Les 2 joueurs posent une mine
		self.Joueur1.change_dir(event)
		self.Joueur2.change_dir(event)
	
	def stop_dir(self, event):
		#Les 2 joueurs bougent leurs canons
		self.Joueur1.stop_dir(event)
		self.Joueur2.stop_dir(event)
	"""Fin(gestion des touches spécifiques à cette mission)."""

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("""Mission 8: Copier-Coller\n
Brilliant! Vous avez assuré(e)! Et maintenant,
que vais-je faire... Voyns voyons...
Voilà, je restore les données de TkT4nk...
Non, s'il te plaît, tais-toi, merci bien!
Ctrl+C, Ctrl+V et... Bref, tout m'a l'air en ordre,
vous pouvez maintenant le vaincre proprement.
Diantre! Il semblerait que le copier-coller ait
un peu trop bien marcher... Il y a maintenant
deux TkT4nk et deux %s!!
Mais vous arrangerez cela, bien entendu!
Mais je vais vous aider: d'après les données du jeu,
aucun des deux %s ne doit mourir,
et les PV du dernier TkT4nk touché
seront affichés en bas de l'écran.
Je vais aussi mettre un peu plus de couleurs...\n
Appuyez sur Entrée pour commencer.""" %(root.nom, root.nom) )

	def start(self, event):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, self.Joueurs)
		#Affichage de l'objectif du chapitre
		mission = self.canvas.create_text(500, 20, font="Time_New_Roman 15", text="Mission 8: Décimer l'ennemi.")
		#Evènements
		self.fenetre.unbind('<Return>')
		self.canvas.bind('<Motion>', self.spe_canon)
		self.canvas.bind('<Button-1>', self.spe_tir)
		self.canvas.bind('<Button-3>', self.spe_mine)
		self.fenetre.bind('<KeyPress>', self.change_dir)
		self.fenetre.bind('<KeyRelease>', self.stop_dir)
		#Et on lance la boucle
		self.boucle()
			
	def fin2partie(self):
		#Si le joueur est mort...
		if (self.Joueur1.mort) or (self.Joueur2.mort):
			#Réinitialisation
			self.Joueur1.reborn(80, 80)
			self.Joueur2.reborn(80, 520)
			self.Joueur3.reborn(920, 80)
			self.Joueur4.reborn(920, 520)
			#PV
			self.Joueur3.pv = 60
			self.Joueur4.pv = 60
			#Rectangle où sont afficher les PV
			self.canvas.create_rectangle(400, 600, 600, 640, width=0, fill='DarkGoldenRod')
		#...ou si tous les ennemis sont morts
		if (self.Joueur3.mort) and (self.Joueur4.mort):
			#Mission accomplie: au suivant!
			self.encore = False
			self.canvas.unbind('<Button-1>')
			self.canvas.unbind('<Button-3>')
			root.main = Histoire9()
			root.main.afficher()
				
	def boucle(self):
		"""===Boucle principale du jeu.==="""
		#Mouvement des obus
		for var in range(len(self.Joueurs)):
			self.Joueurs[var].mouvement_obus()
		#Mine:
		for k in range(len(self.Joueurs)):
			if self.Joueurs[k].stock_mine == 0:
				self.Joueurs[k].timer -= 20
			if (self.Joueurs[k].stock_mine == 0) and (self.Joueurs[k].timer == 0):
				self.Joueurs[k].minequiexplose()
		#IA du boss
		for k in range(2, 4):
			dist1 = math.sqrt( (self.Joueur1.char_x - self.Joueurs[k].char_x)**2 
					+ (self.Joueur1.char_y - self.Joueurs[k].char_y)**2 )
			dist2 = math.sqrt( (self.Joueur2.char_x - self.Joueurs[k].char_x)**2 
					+ (self.Joueur1.char_y - self.Joueurs[k].char_y)**2 )
			if dist1 < dist2:
				self.Joueurs[k].ia( (self.Joueur1.char_x, self.Joueur1.char_y) )
			else:
				self.Joueurs[k].ia( (self.Joueur2.char_x, self.Joueur2.char_y) )
			if self.Joueurs[k].mort == False:
				self.Joueurs[k].miner({})
		#Déplacement des robots + joueur
		for k in range(len(self.Joueurs)):
			self.Joueurs[k].mouvement_char()
		#Il y a-t-il fin de partie?
		self.fin2partie()
		#C'est une boucle, donc c'est re-ti-par!
		if self.encore:
			self.fenetre.after(20, self.boucle)	

class Histoire9:
	
	def __init__(self):
		#Variables globales
		self.terrain = root.terrain0
		self.fenetre = root.fenetre
		self.canvas = root.canvas
		
		#=====Signet=====
		root.save[-1] = 9
		root.sauvegarder()
		
		#On crée les chars
		self.Joueur1 = Char(self.canvas, 80, 80, 'Orange', (root.nom, 60, 20, 'Yellow'))
		self.Joueur2 = Boss(self.canvas, 920, 520, 'White', ('P.U.L.S.A.R.', 980, 620, 'White'), 100)
		#On enregistre les Joueurs dans une liste
		self.Joueurs = [self.Joueur1, self.Joueur2]

		#Pour la boucle
		self.encore = True
		self.pulsar = 100

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("""Mission 9: P.U.L.S.A.R.\n
Il est vrai que je ne me suis toujours pas présenté; pardon-
-nez mon impolitesse, j'étais comme qui dirait occupé;
je suis le Programme Ultime Limité au Service Anti Rm
gentiment abrégé en P.U.L.S.A.R. (avec les points,
c'est le détail qui tue, je ne suis pas une étoile à neutrons,
même si l'idée ne me déplait guère...)
Vous comprenez pourquoi je n'ai pointé le bout de mon
canon que maintenant... Bout de canon que vous n'avez
pas encore vu (sauf si ce n'est pas votre première fois,
phrase en effet douteuse...). Mais rattrapons cela:
mon travail étant fait, il est temps de me désactiver.
Vous pourriez appuyer sur la touche Echap,
mais vous ne pourriez réussir le défi qui va avec.
PS: J'ai modifié votre char cette mission.\n
Appuyez sur Entrée pour commencer.""")

	def start(self, event):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, self.Joueurs)
		#Affichage de l'objectif du chapitre
		mission = self.canvas.create_text(500, 20, font="Time_New_Roman 15", text="Mission 9: Vaincre le boss.")
		#Affichage des pv du bos
		self.Joueur2.rip()
		#Evènements
		self.fenetre.unbind('<Return>')
		self.canvas.bind('<Motion>', self.Joueur1.mouvement_canon)
		self.canvas.bind('<Button-1>', self.Joueur1.tir)
		self.canvas.bind('<Button-3>', self.Joueur1.miner)
		self.fenetre.bind('<KeyPress>', self.Joueur1.change_dir)
		self.fenetre.bind('<KeyRelease>', self.Joueur1.stop_dir)
		#Et on lance la boucle
		self.boucle()
	
	def fin2partie(self):
		#Si le joueur est mort
		if (self.Joueur1.mort):
			#Réinitialisation
			self.Joueur1.reborn(80, 80)
			self.Joueur2.reborn(920, 520)
			#Affichage des PV du boss
			self.Joueur2.pv = 100
			self.Joueur2.rip()
		#Si on réussi à vaincre le boss
		if (self.Joueur2.mort):
			#Mission accomplie: au suivant!
			self.encore = False
			root.noclick()
			root.main = Histoire10()
			root.main.afficher()
				
	def boucle(self):
		"""===Boucle principale du jeu.==="""
		#Mouvement des obus
		for var in range(len(self.Joueurs)):
			self.Joueurs[var].mouvement_obus()
		#Mine:
		if self.Joueur1.stock_mine == 0:
			self.Joueur1.timer -= 20
		if (self.Joueur1.stock_mine == 0) and (self.Joueur1.timer == 0):
			self.Joueur1.minequiexplose()
		#IA
		self.Joueur2.ia( (self.Joueur1.char_x, self.Joueur1.char_y) )
		#"Pulsar"
		self.pulsar -= 1
		if self.pulsar == 0:
			self.pulsar = 100
			self.Joueur2.tir(0)
			self.Joueur2.tir(math.pi/4)
			self.Joueur2.tir(math.pi/2)
			self.Joueur2.tir(3*math.pi/4)
			self.Joueur2.tir(math.pi)
			self.Joueur2.tir(-math.pi/4)
			self.Joueur2.tir(-math.pi/2)
			self.Joueur2.tir(-3*math.pi/4)
		#Déplacement des Joueurs
		for k in range(len(self.Joueurs)):
			self.Joueurs[k].mouvement_char()
		self.Joueur1.mouvement_char()
		#Il y a-t-il fin de partie?
		self.fin2partie()
		#C'est une boucle, donc c'est re-ti-par!
		if self.encore:
			self.fenetre.after(20, self.boucle)			

class Histoire10:
	
	def __init__(self):
		#Variables globales
		self.terrain = root.terrain0
		self.fenetre = root.fenetre
		self.canvas = root.canvas
		
		#=====Signet=====
		root.save[-1] = 0
		root.sauvegarder()

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		mission = self.canvas.create_text(500, 20, font="Time_New_Roman 15", text="Mission 10 (facultatif): Partager TkTank avec vos ami(e)s.")
		#=====Défis réussis!=====
		root.save[3] = 1
		root.sauvegarder()
		#Affichage de la narration
		root.display("""Mission 42: La vie, l'univers, le reste
...nous aussi nous sommes poussière d'étoiles...
Vous avez choisi de persévérer et avez terminé le
mode "un brin difficile" du mode Histoire de TkT4nk.
Vous avez bien exploré le jeu et peut-être même dans
son entièreté... mais ce que représente ce jeu
et son joueur %s est bien maigre
et ne représente qu'une infime partie du monde...
Il reste temps à découvir, et jamais nous ne finirons
cette exploration de notre Univers...
Ma proposition est la suivante: quittez TkT4nk,
et sortez prendre l'air! Découvrez les merveilles
du monde extérieur, devenez explorateur, soyez curieux!
C'est peut-être ce que aurait dû faire le développeur
de ce jeu, plutôt que de programmer...
Sinon, appuyez sur cette maudite touche Echap.
La touche Entrée vous donnera accès aux crédits.""" %(root.nom) )	
		
	def start(self, event):
		root.display("""Crédits: TkT4nk\n
Un jeu de: UNG Harry
Remerciments: M.Muller, pour la gestion des touches.
Ma sœur pour les fautes de franais (ç ?)
Et avec mes amis: merci d'avoir testé le jeu!\n
Joueur (et surtout son PC): %s
Boss: TkT4nk, P.U.L.S.A.R.
Meilleurs jeux d'acteur, rien à redire)\n
Le classique: (Merci d'avoir jouer!)² (^_^)Y""" %(root.nom) )			
									
"""================Fin du mode 'Histoire"================"""


class SansFin():
	
	def __init__(self):
		#Variables globales
		self.terrain = root.terrain1
		self.fenetre = root.fenetre
		self.canvas = root.canvas
		
		#On crée les chars
		self.Joueur1 = Char(self.canvas, 80, 520, 'Yellow', ('Joueur', 60, 620, 'White'))
		self.Joueur2 = Tank(self.canvas, 80, 80, 'Red', ('Le feu feu', 60, 20, 'DarkRed'), 1)
		self.Joueur3 = Tank(self.canvas, 920, 80, 'LimeGreen', ('Le verre vert', 920, 20, 'DarkGreen'), 1)
		self.Joueur4 = Tank(self.canvas, 920, 520, 'DodgerBlue', ('Le bleu bleuté', 920, 620, 'DarkBlue'), 1)
		#On enregistre les Joueurs dans une liste
		self.Joueurs = [self.Joueur1, self.Joueur2, self.Joueur3, self.Joueur4]

		#Nombre de victoire et de défaites
		self.score = {"Défaite":0, "Victoire":0} 
		self.encore = True       

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("""Comment jouer?\n"
Flèches_directionnelles / zqsd / wasd : se déplacer
Click gauche : Tirer
Click droit : Poser une mine
Le mode Sans Fin est un mode... Sans Fin.
Chaque fois que vous perdez ou gagnez,
vous recommencez immédiatement.
Les Ennemis peuvent s'entretuer et possèdent:
(Nombre de Victoire(s)) PV\n
Appuez sur Entrée pour commencer.""")

	def start(self, event):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, self.Joueurs)
		#...et les scores
		printscore = self.canvas.create_text(500, 20, font="Time_New_Roman 15",
								   text="Victoire: "+str(self.score["Victoire"]))
		printscore = self.canvas.create_text(500, 620, font="Time_New_Roman 15",
								   text="Défaite: "+str(self.score["Défaite"]))
		#Evènements
		self.fenetre.unbind('<Return>')
		self.canvas.bind('<Motion>', self.Joueur1.mouvement_canon)
		self.canvas.bind('<Button-1>', self.Joueur1.tir)
		self.canvas.bind('<Button-3>', self.Joueur1.miner)
		self.fenetre.bind('<KeyPress>', self.Joueur1.change_dir)
		self.fenetre.bind('<KeyRelease>', self.Joueur1.stop_dir)
		#Et on lance la boucle
		self.boucle()			

	def fin2partie(self):
		#Si le joueur est mort...
		if (self.Joueur1.mort):
			#Réinitialisation
			self.Joueur1.reborn(80, 520)
			self.Joueur2.reborn(80, 80)
			self.Joueur3.reborn(920, 80)
			self.Joueur4.reborn(920, 520)
			#Score défaite +1
			self.score["Défaite"] = self.score["Défaite"] + 1
			#Effacement de la surface (ligne du bas)
			self.canvas.create_rectangle(400, 600, 600, 640, width=0, fill='DarkGoldenRod')
			#Affichage
			printscore = self.canvas.create_text(500, 620, font="Time_New_Roman 15",
								   text="Défaite(s): "+str(self.score["Défaite"]))
			#PV des Ennemis
			for var in range(1, 3):
				self.Joueurs[var].pv = self.score["Victoire"]
		#...ou si tous les ennemis sont morts
		if (self.Joueur2.mort) and (self.Joueur3.mort) and (self.Joueur4.mort):
			#Réinitialisation
			self.Joueur1.reborn(80, 520)
			self.Joueur2.reborn(80, 80)
			self.Joueur3.reborn(920, 80)
			self.Joueur4.reborn(920, 520)
			#Score défaite +1
			self.score["Victoire"] = self.score["Victoire"] + 1
			#Effacement de la surface (ligne du haut)
			self.canvas.create_rectangle(400, 0, 600, 40, width=0, fill='DarkGoldenRod')
			#Affichage
			printscore = self.canvas.create_text(500, 20, font="Time_New_Roman 15",
								   text="Victoire(s): "+str(self.score["Victoire"]))
			#PV des Ennemis
			for var in range(1, 3):
				self.Joueurs[var].pv = self.score["Victoire"]
		if (self.score["Défaite"] == 0) and (self.score["Victoire"] == 12):
			#=====Défis réussis!=====
			root.save[4] = 1
			root.sauvegarder()
				
	def boucle(self):
		"""===Boucle principale du jeu.==="""
		#Mouvement des obus
		for var in range(len(self.Joueurs)):
			self.Joueurs[var].mouvement_obus()
		#Mine:
		for k in range(len(self.Joueurs)):
			if self.Joueurs[k].stock_mine == 0:
				self.Joueurs[k].timer -= 20
			if (self.Joueurs[k].stock_mine == 0) and (self.Joueurs[k].timer == 0):
				self.Joueurs[k].minequiexplose()
		#Déplacement des robots + joueur
		for k in range(3):
			self.Joueurs[k+1].ia( (self.Joueur1.char_x, self.Joueur1.char_y) )
		for k in range(len(self.Joueurs)):
			self.Joueurs[k].mouvement_char()
		#Il y a-t-il fin de partie?
		self.fin2partie()
		#C'est une boucle, donc c'est re-ti-par!
		if self.encore:
			self.fenetre.after(20, self.boucle)

"""================Coopération================"""
class Coop:
	
	def __init__(self):
		#Variables globales
		self.terrain = root.terrain2
		self.fenetre = root.fenetre
		self.canvas = root.canvas
		
		#On crée les chars
		self.Joueur1 = Char(self.canvas, 920, 80, 'DodgerBlue', ('Joueur1', 980, 20, 'DarkBlue'))
		self.Joueur2 = Char(self.canvas, 920, 520, 'Red', ('Joueur2', 980, 620, 'DarkRed'))
		self.Joueur3 = Char(self.canvas, 80, 80, 'LimeGreen', ('Ennemi', 60, 20, 'DarkGreen'))
		self.Joueur4 = Char(self.canvas, 80, 520, 'Yellow', ('Ennemi', 60, 620, 'White'))
		#On enregistre les Joueurs dans une liste
		self.Joueurs = [self.Joueur1, self.Joueur2, self.Joueur3, self.Joueur4]

		#Pour la boucle
		self.encore = True

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("""Tuto:\n
Joueur1, voici les touches\n
Se déplacer : zqsd/wasd
Tirer (selon un cercle trigo, g correspondant à -pi/2):
rty
fgh
vbn\n
Poser une mine : espace
Joueur2, voici les touches:
Se déplacer : Flèches directionnelles
Tirer : Click gauche
Poser une mine : Click droit""")

	def start(self, event):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, self.Joueurs)
		#Affichage de l'objectif du chapitre
		mission = self.canvas.create_text(500, 20, font="Time_New_Roman 15", text="Mission 0: Décimer l'ennemi.")
		#Evènements
		self.fenetre.unbind('<Return>')
		self.canvas.bind('<Motion>', self.Joueur2.mouvement_canon)
		self.canvas.bind('<Button-1>', self.Joueur2.tir)
		self.canvas.bind('<Button-3>', self.Joueur2.miner)
		self.fenetre.bind('<KeyPress>', root.change_dir)
		self.fenetre.bind('<KeyRelease>', root.stop_dir)
		#Et on lance la boucle
		self.boucle()
			
	def fin2partie(self):
		#Si le joueur est mort...
		if (self.Joueur1.mort) or (self.Joueur2.mort):
			#Réinitialisation
			self.Joueur1.reborn(920, 80)
			self.Joueur2.reborn(920, 520)
			self.Joueur3.reborn(80, 80)
			self.Joueur4.reborn(80, 520)
		#...ou si tous les ennemis sont morts
		if (self.Joueur3.mort) and (self.Joueur4.mort):
			#Mission accomplie: au suivant!
			self.encore = False
			root.noclick()
			root.main = Coop1()
			root.main.afficher()
				
	def boucle(self):
		"""===Boucle principale du jeu.==="""
		#Mouvement des obus
		for var in range(len(self.Joueurs)):
			self.Joueurs[var].mouvement_obus()
		#Mine:
		for k in range(len(self.Joueurs)):
			if self.Joueurs[k].stock_mine == 0:
				self.Joueurs[k].timer -= 20
			if (self.Joueurs[k].stock_mine == 0) and (self.Joueurs[k].timer == 0):
				self.Joueurs[k].minequiexplose()
		#Déplacement des robots + joueur
		for k in range(len(self.Joueurs)):
			self.Joueurs[k].mouvement_char()
		#Il y a-t-il fin de partie?
		self.fin2partie()
		#C'est une boucle, donc c'est re-ti-par!
		if self.encore:
			self.fenetre.after(20, self.boucle)	
			
class Coop1:
	
	def __init__(self):
		#Variables globales
		self.terrain = root.terrain1
		self.fenetre = root.fenetre
		self.canvas = root.canvas
		
		#On crée les chars
		self.Joueur1 = Char(self.canvas, 920, 80, 'DodgerBlue', ('Joueur1', 980, 20, 'DarkBlue'))
		self.Joueur2 = Char(self.canvas, 920, 520, 'Red', ('Joueur2', 980, 620, 'DarkRed'))
		self.Joueur3 = Char(self.canvas, 80, 80, 'LimeGreen', ('Alcane', 60, 20, 'DarkGreen'))
		self.Joueur4 = Char(self.canvas, 80, 520, 'Yellow', ('Alcène', 60, 620, 'White'))
		self.Joueur5 = Char(self.canvas, 500, 300, 'Green', ('Alcyne', 500, 620, 'DarkGreen'))
		#On enregistre les Joueurs dans une liste
		self.Joueurs = [self.Joueur1, self.Joueur2, self.Joueur3, self.Joueur4, self.Joueur5]

		#Pour la boucle
		self.encore = True

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("""Mission 1/6: Commençons\n
Le mode coopération (Coop, pour les intimes)
comprend 6 missions.
Les ennemis peuvent, dans ce mode, s'entretuer.
Si l'un des deux joueurs meurt, vous recommencez.
Bonne chance, et amusez-vous bien! ;-)\n
Appuyez sur Entrée pour commencer.""")

	def start(self, event):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, self.Joueurs)
		#Affichage de l'objectif du chapitre
		mission = self.canvas.create_text(500, 20, font="Time_New_Roman 15", text="Mission 1/6: Décimer l'ennemi.")
		#Evènements
		self.fenetre.unbind('<Return>')
		self.canvas.bind('<Motion>', self.Joueur2.mouvement_canon)
		self.canvas.bind('<Button-1>', self.Joueur2.tir)
		self.canvas.bind('<Button-3>', self.Joueur2.miner)
		self.fenetre.bind('<KeyPress>', root.change_dir)
		self.fenetre.bind('<KeyRelease>', root.stop_dir)
		#Et on lance la boucle
		self.boucle()
			
	def fin2partie(self):
		#Si le joueur est mort...
		if (self.Joueur1.mort) or (self.Joueur2.mort):
			#Réinitialisation
			self.Joueur1.reborn(920, 80)
			self.Joueur2.reborn(920, 520)
			self.Joueur3.reborn(80, 80)
			self.Joueur4.reborn(80, 520)
			self.Joueur5.reborn(500, 300)
		#...ou si tous les ennemis sont morts
		if (self.Joueur3.mort) and (self.Joueur4.mort) and (self.Joueur5.mort):
			#Mission accomplie: au suivant!
			self.encore = False
			root.noclick()
			root.main = Coop2()
			root.main.afficher()
				
	def boucle(self):
		"""===Boucle principale du jeu.==="""
		#Mouvement des obus
		for var in range(len(self.Joueurs)):
			self.Joueurs[var].mouvement_obus()
		#Mine:
		for k in range(len(self.Joueurs)):
			if self.Joueurs[k].stock_mine == 0:
				self.Joueurs[k].timer -= 20
			if (self.Joueurs[k].stock_mine == 0) and (self.Joueurs[k].timer == 0):
				self.Joueurs[k].minequiexplose()
		#Déplacement des robots + joueurs
		#IA: cible le joueur le plus proche
		for k in range(3):
			dist1 = math.sqrt( (self.Joueur1.char_x - self.Joueurs[k+2].char_x)**2 
					+ (self.Joueur1.char_y - self.Joueurs[k+2].char_y)**2 )
			dist2 = math.sqrt( (self.Joueur2.char_x - self.Joueurs[k+2].char_x)**2 
					+ (self.Joueur2.char_y - self.Joueurs[k+2].char_y)**2 )
			if dist1 < dist2:
				self.Joueurs[k+2].ia( (self.Joueur1.char_x, self.Joueur1.char_y) )
			else:
				self.Joueurs[k+2].ia( (self.Joueur2.char_x, self.Joueur2.char_y) )
		for k in range(len(self.Joueurs)):
			self.Joueurs[k].mouvement_char()
		#Il y a-t-il fin de partie?
		self.fin2partie()
		#C'est une boucle, donc c'est re-ti-par!
		if self.encore:
			self.fenetre.after(20, self.boucle)	

class Coop2:
	
	def __init__(self):
		#Variables globales
		self.terrain = root.terrain2
		self.fenetre = root.fenetre
		self.canvas = root.canvas
		
		#On crée les chars
		self.Joueur1 = Char(self.canvas, 920, 80, 'DodgerBlue', ('Joueur1', 980, 20, 'DarkBlue'))
		self.Joueur2 = Char(self.canvas, 920, 520, 'Red', ('Joueur2', 980, 620, 'DarkRed'))
		self.Joueur3 = Tank(self.canvas, 80, 80, 'LimeGreen', ('Ethane  (a 10 PV)', 60, 20, 'DarkGreen'), 10)
		self.Joueur4 = Tank(self.canvas, 80, 520, 'Yellow', ('Ethène  (a 10 PV)', 60, 620, 'White'), 10)
		self.Joueur5 = Tank(self.canvas, 500, 300, 'Green', ('Ethyne  (a 10 PV)', 500, 620, 'DarkGreen'), 10)
		#On enregistre les Joueurs dans une liste
		self.Joueurs = [self.Joueur1, self.Joueur2, self.Joueur3, self.Joueur4, self.Joueur5]

		#Pour la boucle
		self.encore = True

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("""Mission 2/6: Complexe\n
Ce niveau sera semblable au précedént.
Cependant, les ennemis auront cette fois 10 PV.
Ils devront être touchés 10 fois pour être vaincu.""")

	def start(self, event):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, self.Joueurs)
		#Affichage de l'objectif du chapitre
		mission = self.canvas.create_text(500, 20, font="Time_New_Roman 15", text="Mission 2/6: Décimer l'ennemi.")
		#Evènements
		self.fenetre.unbind('<Return>')
		self.canvas.bind('<Motion>', self.Joueur2.mouvement_canon)
		self.canvas.bind('<Button-1>', self.Joueur2.tir)
		self.canvas.bind('<Button-3>', self.Joueur2.miner)
		self.fenetre.bind('<KeyPress>', root.change_dir)
		self.fenetre.bind('<KeyRelease>', root.stop_dir)
		#Et on lance la boucle
		self.boucle()
			
	def fin2partie(self):
		#Si le joueur est mort...
		if (self.Joueur1.mort) or (self.Joueur2.mort):
			#Réinitialisation
			self.Joueur1.reborn(920, 80)
			self.Joueur2.reborn(920, 520)
			self.Joueur3.reborn(80, 80)
			self.Joueur4.reborn(80, 520)
			self.Joueur5.reborn(500, 300)
			for k in range(2, 5):
				self.Joueurs[k].pv = 10
		#...ou si tous les ennemis sont morts
		if (self.Joueur3.mort) and (self.Joueur4.mort) and (self.Joueur5.mort):
			#Mission accomplie: au suivant!
			self.encore = False
			root.noclick()
			root.main = Coop3()
			root.main.afficher()
				
	def boucle(self):
		"""===Boucle principale du jeu.==="""
		#Mouvement des obus
		for var in range(len(self.Joueurs)):
			self.Joueurs[var].mouvement_obus()
		#Mine:
		for k in range(len(self.Joueurs)):
			if self.Joueurs[k].stock_mine == 0:
				self.Joueurs[k].timer -= 20
			if (self.Joueurs[k].stock_mine == 0) and (self.Joueurs[k].timer == 0):
				self.Joueurs[k].minequiexplose()
		#Déplacement des robots + joueurs
		#IA: cible le joueur le plus proche
		for k in range(3):
			dist1 = math.sqrt( (self.Joueur1.char_x - self.Joueurs[k+2].char_x)**2 
					+ (self.Joueur1.char_y - self.Joueurs[k+2].char_y)**2 )
			dist2 = math.sqrt( (self.Joueur2.char_x - self.Joueurs[k+2].char_x)**2 
					+ (self.Joueur2.char_y - self.Joueurs[k+2].char_y)**2 )
			if dist1 < dist2:
				self.Joueurs[k+2].ia( (self.Joueur1.char_x, self.Joueur1.char_y) )
			else:
				self.Joueurs[k+2].ia( (self.Joueur2.char_x, self.Joueur2.char_y) )
		for k in range(len(self.Joueurs)):
			self.Joueurs[k].mouvement_char()
		#Il y a-t-il fin de partie?
		self.fin2partie()
		#C'est une boucle, donc c'est re-ti-par!
		if self.encore:
			self.fenetre.after(20, self.boucle)	
			
class Coop3:
	
	def __init__(self):
		#Variables globales
		self.terrain = root.terrain1
		self.fenetre = root.fenetre
		self.canvas = root.canvas
		
		#On crée les chars
		self.Joueur1 = Char(self.canvas, 920, 80, 'DodgerBlue', ('Joueur1', 980, 20, 'DarkBlue'))
		self.Joueur2 = Char(self.canvas, 920, 520, 'Red', ('Joueur2', 980, 620, 'DarkRed'))
		self.Joueur3 = Tank(self.canvas, 80, 80, 'LimeGreen', ('Cosinus  (a 60 PV)', 60, 20, 'DarkGreen'), 60)
		self.Joueur4 = Tank(self.canvas, 80, 520, 'Yellow', ('Cotangente  (a 60 PV)', 60, 620, 'White'), 60)
		self.Joueur5 = Tank(self.canvas, 500, 300, 'Green', ('Cosécante  (a 60 PV)', 920, 620, 'DarkGreen'), 60)
		#On enregistre les Joueurs dans une liste
		self.Joueurs = [self.Joueur1, self.Joueur2, self.Joueur3, self.Joueur4, self.Joueur5]

		#Pour la boucle
		self.encore = True

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("""Mission 3/6: Coopérer\n
Dans les deux niveaux qui suivent,
il faut que chaque Joueur atteigne la croix de sa couleur.
Attention cependant! Ces ennemis ont 60 PVs.\n
Appuyez sur Entrée pour commencer.""")

	def start(self, event):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, self.Joueurs)
		#Affichage de l'objectif du chapitre
		mission = self.canvas.create_text(500, 20, font="Time_New_Roman 15", text="Mission 3/6: Prendre.")
		#Affichage des à atteindre
		self.canvas.create_text(960, 550, font="Time_New_Roman 100", fill="red", text="x")
		self.canvas.create_text(960, 70, font="Time_New_Roman 100", fill="blue", text="x")
		#Evènements
		self.fenetre.unbind('<Return>')
		self.canvas.bind('<Motion>', self.Joueur2.mouvement_canon)
		self.canvas.bind('<Button-1>', self.Joueur2.tir)
		self.canvas.bind('<Button-3>', self.Joueur2.miner)
		self.fenetre.bind('<KeyPress>', root.change_dir)
		self.fenetre.bind('<KeyRelease>', root.stop_dir)
		#Et on lance la boucle
		self.boucle()
			
	def fin2partie(self):
		#Si le joueur est mort...
		if (self.Joueur1.mort) or (self.Joueur2.mort):
			#Réinitialisation
			self.Joueur1.reborn(920, 80)
			self.Joueur2.reborn(920, 520)
			self.Joueur3.reborn(80, 80)
			self.Joueur4.reborn(80, 520)
			self.Joueur5.reborn(500, 300)
			for k in range(2, 5):
				self.Joueurs[k].pv = 60
		#...ou si la mission est accomplie
		if (self.Joueur1.char_x >= 920) and (self.Joueur1.char_y <= 80)\
		and (self.Joueur2.char_x >= 920) and (self.Joueur2.char_y >= 520):
			#Mission accomplie: au suivant!
			self.encore = False
			root.noclick()
			root.main = Coop4()
			root.main.afficher()
				
	def boucle(self):
		"""===Boucle principale du jeu.==="""
		#Mouvement des obus
		for var in range(len(self.Joueurs)):
			self.Joueurs[var].mouvement_obus()
		#Mine:
		for k in range(len(self.Joueurs)):
			if self.Joueurs[k].stock_mine == 0:
				self.Joueurs[k].timer -= 20
			if (self.Joueurs[k].stock_mine == 0) and (self.Joueurs[k].timer == 0):
				self.Joueurs[k].minequiexplose()
		#Déplacement des robots + joueurs
		#IA: cible le joueur le plus proche
		for k in range(2, 5):
			dist1 = math.sqrt( (self.Joueur1.char_x - self.Joueurs[k].char_x)**2 
					+ (self.Joueur1.char_y - self.Joueurs[k].char_y)**2 )
			dist2 = math.sqrt( (self.Joueur2.char_x - self.Joueurs[k].char_x)**2 
					+ (self.Joueur2.char_y - self.Joueurs[k].char_y)**2 )
			if dist1 < dist2:
				self.Joueurs[k].ia( (self.Joueur1.char_x, self.Joueur1.char_y) )
			else:
				self.Joueurs[k].ia( (self.Joueur2.char_x, self.Joueur2.char_y) )
		for k in range(len(self.Joueurs)):
			self.Joueurs[k].mouvement_char()
		#Il y a-t-il fin de partie?
		self.fin2partie()
		#C'est une boucle, donc c'est re-ti-par!
		if self.encore:
			self.fenetre.after(20, self.boucle)	
			
class Coop4:
	
	def __init__(self):
		#Variables globales
		self.terrain = root.terrain1
		self.fenetre = root.fenetre
		self.canvas = root.canvas
		
		#On crée les chars
		self.Joueur1 = Char(self.canvas, 920, 80, 'DodgerBlue', ('Joueur1', 980, 20, 'DarkBlue'))
		self.Joueur2 = Char(self.canvas, 920, 520, 'Red', ('Joueur2', 980, 620, 'DarkRed'))
		self.Joueur3 = Tank(self.canvas, 80, 80, 'LimeGreen', ('Colonel  (a 10 PV)', 60, 20, 'DarkGreen'), 10)
		self.Joueur4 = Tank(self.canvas, 80, 520, 'Yellow', ('Colonel  (a 10 PV)', 60, 620, 'White'), 10)
		#On enregistre les Joueurs dans une liste
		self.Joueurs = [self.Joueur1, self.Joueur2, self.Joueur3, self.Joueur4]

		#Pour la boucle
		self.encore = True
		self.temps = 30
		self.millisec = 50

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("""Mission 4/6: Contre-la-montre\n
Cette fois, vous devez faire attention au temps...
Pas d'inquiétude, les ennemis ne sont plus que deux,
et n'ont de nouveaux plus que 10 PV!\n
Appuyez sur Entrée pour commencer.""")

	def start(self, event):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, self.Joueurs)
		#Affichage de l'objectif du chapitre
		mission = self.canvas.create_text(500, 20, font="Time_New_Roman 15", text="Mission 4/6: Prendre en 30 secondes.")
		#Affichage des à atteindre
		self.canvas.create_text(960, 550, font="Time_New_Roman 100", fill="red", text="x")
		self.canvas.create_text(960, 70, font="Time_New_Roman 100", fill="blue", text="x")
		#Affichage
		printime = self.canvas.create_text(500, 620, font="Time_New_Roman 15",
									text="Temps restant "+str(self.temps))
		#Evènements
		self.fenetre.unbind('<Return>')
		self.canvas.bind('<Motion>', self.Joueur2.mouvement_canon)
		self.canvas.bind('<Button-1>', self.Joueur2.tir)
		self.canvas.bind('<Button-3>', self.Joueur2.miner)
		self.fenetre.bind('<KeyPress>', root.change_dir)
		self.fenetre.bind('<KeyRelease>', root.stop_dir)
		#Et on lance la boucle
		self.boucle()
			
	def fin2partie(self):
		#Si le joueur est mort...
		if (self.Joueur1.mort) or (self.Joueur2.mort) or (self.temps <= 0):
			#Réinitialisation
			self.Joueur1.reborn(920, 80)
			self.Joueur2.reborn(920, 520)
			self.Joueur3.reborn(80, 80)
			self.Joueur4.reborn(80, 520)
			for k in range(2, 4):
				self.Joueurs[k].pv = 10
			self.temps = 30
			self.millisec = 50
			#Effacement de la surface (ligne du bas)
			self.canvas.create_rectangle(400, 600, 600, 640, width=0, fill='DarkGoldenRod')
			#Affichage
			printime = self.canvas.create_text(500, 620, font="Time_New_Roman 15",
									text="Temps restant "+str(self.temps))
		#...ou si la mission est accomplie
		if (self.Joueur1.char_x >= 920) and (self.Joueur1.char_y <= 80)\
		and (self.Joueur2.char_x >= 920) and (self.Joueur2.char_y >= 520):
			#Mission accomplie: au suivant!
			self.encore = False
			root.noclick()
			root.main = Coop5()
			root.main.afficher()
				
	def boucle(self):
		"""===Boucle principale du jeu.==="""
		#Mouvement des obus
		for var in range(len(self.Joueurs)):
			self.Joueurs[var].mouvement_obus()
		#Mine:
		for k in range(len(self.Joueurs)):
			if self.Joueurs[k].stock_mine == 0:
				self.Joueurs[k].timer -= 20
			if (self.Joueurs[k].stock_mine == 0) and (self.Joueurs[k].timer == 0):
				self.Joueurs[k].minequiexplose()
		#Déplacement des robots + joueurs
		#IA: cible le joueur le plus proche
		for k in range(2, 4):
			dist1 = math.sqrt( (self.Joueur1.char_x - self.Joueurs[k].char_x)**2 
					+ (self.Joueur1.char_y - self.Joueurs[k].char_y)**2 )
			dist2 = math.sqrt( (self.Joueur2.char_x - self.Joueurs[k].char_x)**2 
					+ (self.Joueur2.char_y - self.Joueurs[k].char_y)**2 )
			if dist1 < dist2:
				self.Joueurs[k].ia( (self.Joueur1.char_x, self.Joueur1.char_y) )
			else:
				self.Joueurs[k].ia( (self.Joueur2.char_x, self.Joueur2.char_y) )
		for k in range(len(self.Joueurs)):
			self.Joueurs[k].mouvement_char()
		#Gère l'affichage du temps restant
		if self.millisec <= 0:
			self.temps -= 1
			self.millisec = 50
			#Effacement de la surface (ligne du bas)
			self.canvas.create_rectangle(400, 600, 600, 640, width=0, fill='DarkGoldenRod')
			#Affichage
			printime = self.canvas.create_text(500, 620, font="Time_New_Roman 15",
									text="Temps restant "+str(self.temps))
		#Il y a-t-il fin de partie?
		self.millisec -= 1
		self.fin2partie()
		#C'est une boucle, donc c'est re-ti-par!
		if self.encore:
			self.fenetre.after(20, self.boucle)		

class Coop5:
	
	def __init__(self):
		#Variables globales
		self.terrain = root.terrain2
		self.fenetre = root.fenetre
		self.canvas = root.canvas
		
		#On crée les chars
		self.Joueur1 = Char(self.canvas, 920, 80, 'DodgerBlue', ('Joueur1', 960, 20, 'DarkBlue'))
		self.Joueur2 = Char(self.canvas, 920, 520, 'Red', ('Joueur2', 960, 620, 'DarkRed'))		
		self.Joueur3 = Boss2(self.canvas, 80, 300, 'LimeGreen', ('', 920, 20, 'DarkGreen'), 81 )
		self.Joueurs = [self.Joueur1, self.Joueur2, self.Joueur3]

		#Pour la boucle
		self.encore = True
		
	"""Gestion des touches spécifiques en multi local."""
	def spe_tir(self, event):
		#Les 2 joueurs tirent
		self.Joueur1.tir(event)
		self.Joueur2.tir(event)
	
	def spe_mine(self, event):
		#Les 2 joueurs posent une mine
		self.Joueur1.miner(event)
		self.Joueur2.miner(event)
	
	def spe_canon(self, event):
		#Les 2 joueurs bougent leurs canons
		self.Joueur1.mouvement_canon(event)
		self.Joueur2.mouvement_canon(event)
			
	def change_dir(self, event):
		#Active la direction du Joueur1
		if (event.keysym.lower() in ['z', 'q', 's', 'd', 'w', 'a']):
			self.Joueur1.change_dir(event)
			self.Joueur2.change_dir(event)
		#Active la direction du Joueur2
		if (event.keysym in ['Up', 'Left', 'Down', 'Right']):
			self.Joueur2.change_dir(event)

		#Tir du Joueur1
		if (event.keysym.lower() in ['r', 't', 'y', 'f', 'g', 'h', 'v', 'b', 'n', 'space']):
			root.change_dir(event)
	
	def stop_dir(self, event):
		#Désactive la direction du Joueur1
		if (event.keysym.lower() in ['z', 'q', 's', 'd', 'w', 'a']):
			self.Joueur1.stop_dir(event)
			self.Joueur2.stop_dir(event)
		#Désactive la direction du Joueur2
		if (event.keysym in ['Up', 'Left', 'Down', 'Right']):
			self.Joueur2.stop_dir(event)
		"""Fin(gestion des touches spécifiques en multi local)."""

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("""Mission 5/6: Se coordonner\n
La pénultième mission, celle où il faut se coordoner.
ATTENTION!: Quand le Joueur1 se déplace,
le Joueur2 aussi.
Quand le Joueur2 tir ou pose une mine,
le Joueur1 fait de même.\n
Appuyez sur Entrée pour commencer.""")

	def start(self, event):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, self.Joueurs)
		#Affichage de l'objectif du chapitre
		mission = self.canvas.create_text(500, 20, font="Time_New_Roman 15", text="Mission 5/6: Vaincre le boss.")
		#Affichage des pv du bos
		self.Joueur3.pv = 100
		self.Joueur3.rip()
		#Evènements
		self.fenetre.unbind('<Return>')
		self.canvas.bind('<Motion>', self.spe_canon)
		self.canvas.bind('<Button-1>', self.spe_tir)
		self.canvas.bind('<Button-3>', self.spe_mine)
		self.fenetre.bind('<KeyPress>', self.change_dir)
		self.fenetre.bind('<KeyRelease>', self.stop_dir)
		#Et on lance la boucle
		self.boucle()
			
	def fin2partie(self):
		#Si le joueur est mort...
		if (self.Joueur1.mort) or (self.Joueur2.mort):
			#Réinitialisation
			self.Joueur1.reborn(920, 80)
			self.Joueur2.reborn(920, 520)
			self.Joueur3.reborn(80, 300)
			#Affichage des pv du bos
			self.Joueur3.pv = 81
			self.Joueur3.rip()
		#...ou si tous les ennemis sont morts
		if (self.Joueur3.mort):
			#Mission accomplie: au suivant!
			self.encore = False
			root.noclick()
			root.main = Coop6()
			root.main.afficher()
				
	def boucle(self):
		"""===Boucle principale du jeu.==="""
		#Mouvement des obus
		for var in range(len(self.Joueurs)):
			self.Joueurs[var].mouvement_obus()
		#Mine:
		for k in range(len(self.Joueurs)):
			if self.Joueurs[k].stock_mine == 0:
				self.Joueurs[k].timer -= 20
			if (self.Joueurs[k].stock_mine == 0) and (self.Joueurs[k].timer == 0):
				self.Joueurs[k].minequiexplose()
		#IA du boss
		dist1 = math.sqrt( (self.Joueur1.char_x - self.Joueur3.char_x)**2 
				+ (self.Joueur1.char_y - self.Joueur3.char_y)**2 )
		dist2 = math.sqrt( (self.Joueur2.char_x - self.Joueur3.char_x)**2 
				+ (self.Joueur2.char_y - self.Joueur3.char_y)**2 )
		if dist1 < dist2:
			self.Joueur3.ia( (self.Joueur1.char_x, self.Joueur1.char_y) )
		else:
			self.Joueur3.ia( (self.Joueur2.char_x, self.Joueur2.char_y) )
		#Déplacement des robots + joueur
		for k in range(len(self.Joueurs)):
			self.Joueurs[k].mouvement_char()
		#Il y a-t-il fin de partie?
		self.fin2partie()
		#C'est une boucle, donc c'est re-ti-par!
		if self.encore:
			self.fenetre.after(20, self.boucle)	
		
class Coop6:
	
	def __init__(self):
		#Variables globales
		self.terrain = root.terrain0
		self.fenetre = root.fenetre
		self.canvas = root.canvas
		
		#On crée les chars
		self.Joueur1 = Char(self.canvas, 920, 80, 'DodgerBlue', ('Joueur1', 60, 20, 'DarkBlue'))
		self.Joueur2 = Char(self.canvas, 80, 520, 'Red', ('Joueur2', 60, 620, 'DarkRed'))		
		self.Joueur3 = Boss2(self.canvas, 500, 300, 'LimeGreen', ('', 920, 20, 'DarkGreen'), 99 )
		self.Joueurs = [self.Joueur1, self.Joueur2, self.Joueur3]

		#Pour la boucle
		self.encore = True

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("""Mission 6/6: Confiance !
Dernière mission... ça va être cocasse!
ATTENTION!: le Joueur1 est à droite et le Joueur2, à gauche.
Cela peut-être utile, ne sait-on jamais...\n
Appuyez sur Entrée pour commencer.""")

	def start(self, event):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, self.Joueurs)
		#Affichage de l'objectif du chapitre
		mission = self.canvas.create_text(500, 20, font="Time_New_Roman 15", text="Mission 6/6=1: Vaincre le boss.")
		#Affichage des pv du bos
		self.Joueur3.pv = 100
		self.Joueur3.rip()
		#Evènements
		self.fenetre.unbind('<Return>')
		self.canvas.bind('<Motion>', self.Joueur2.mouvement_canon)
		self.canvas.bind('<Button-1>', self.Joueur2.tir)
		self.canvas.bind('<Button-3>', self.Joueur2.miner)
		self.fenetre.bind('<KeyPress>', root.change_dir)
		self.fenetre.bind('<KeyRelease>', root.stop_dir)
		#Et on lance la boucle
		self.boucle()
			
	def fin2partie(self):
		#Si le joueur est mort...
		if (self.Joueur1.mort) or (self.Joueur2.mort):
			#Réinitialisation
			self.Joueur1.reborn(920, 80)
			self.Joueur2.reborn(80, 520)
			self.Joueur3.reborn(500, 300)
			#Affichage des pv du bos
			self.Joueur3.pv = 100
			self.Joueur3.rip()
		#...ou si tous les ennemis sont morts
		if (self.Joueur3.mort):
			#Mission accomplie: au suivant!
			self.encore = False
			root.noclick()
			root.main = CoopFin()
			root.main.afficher()
				
	def boucle(self):
		"""===Boucle principale du jeu.==="""
		#Mouvement des obus
		for var in range(len(self.Joueurs)):
			self.Joueurs[var].mouvement_obus()
		#Mine:
		for k in range(len(self.Joueurs)):
			if self.Joueurs[k].stock_mine == 0:
				self.Joueurs[k].timer -= 20
			if (self.Joueurs[k].stock_mine == 0) and (self.Joueurs[k].timer == 0):
				self.Joueurs[k].minequiexplose()
		#IA du boss simple: tir aléatoire
		rdg = random.randrange(0, 100)
		if rdg <= 60:
			alpha = random.randrange(0, 628)/100
			#Tir
			self.Joueur3.tir(alpha)
		#Déplacement des robots + joueur
		for k in range(len(self.Joueurs)):
			self.Joueurs[k].mouvement_char()
		#Il y a-t-il fin de partie?
		self.fin2partie()
		#C'est une boucle, donc c'est re-ti-par!
		if self.encore:
			self.fenetre.after(20, self.boucle)	
			
class CoopFin:
	
	def __init__(self):
		#Variables globales
		self.terrain = root.terrain0
		self.fenetre = root.fenetre
		self.canvas = root.canvas

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		mission = self.canvas.create_text(500, 20, font="Time_New_Roman 15", text="Mission i (obligatoire): Continuez de vous amuser!")
		#=====Défis réussis!=====
		root.save[1] = 1
		root.sauvegarder()
		#Affichage de la narration
		root.display("""Félicitation² !!\n
Vous avez réussi les 6 missions!
Vous formez un excellent duo!\n
Appuyez sur Echap pour revenir au Menu.""")	
		
	def start(self, event):
		pass			
"""================FinCoopération================"""

class Versus():
	def __init__(self):
		#Variables globales
		self.terrain = root.terrain2
		self.fenetre = root.fenetre
		self.canvas = root.canvas
		
		#On crée les chars
		self.Joueur1 = Char(self.canvas, 920, 520, 'Red', ('Joueur1', 980, 620, 'DarkRed'))
		self.Joueur2 = Char(self.canvas, 80, 80, 'DodgerBlue', ('Joueur2', 60, 20, 'DarkBlue'))
		#On enregistre les Joueurs dans une liste
		self.Joueurs = [self.Joueur1, self.Joueur2]

		#Nombre de victoire et de défaites
		self.score = {"J1":0, "J2":0} 
		self.encore = True

	def tirMod8(self, event):
		#Tir dirigé contre le Joueur
		#Trigo et Pythagore
		adj = event.x - self.Joueur2.char_x
		hypo = math.sqrt((event.x - self.Joueur2.char_x)**2 + (event.y - self.Joueur2.char_y)**2)
		if hypo == 0:
			hypo = 0.01
		alpha = math.acos(adj/hypo)
		#Angle obtus ou angle aigus?
		if event.y > self.Joueur2.char_y:
			alpha = - alpha
		#On convertit en un "angle modulo 8"
		alpha = round(alpha*4/math.pi)*math.pi/4
		#Tir
		self.Joueur2.tir(alpha)

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("""Joueur1, voici les touches\n
Se déplacer : zqsd/wasd
Tirer (selon un cercle trigo, g correspondant à -pi/2):
rty
fgh
vbn\n
Poser une mine : espace
Joueur2, voici les touches:
Se déplacer : Flèches directionnelles
Tirer : Click gauche (Mais seulement 8 angles possibles...)
Poser une mine : Click droit""")

	def start(self, event):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, self.Joueurs)
		#...et les scores
		printscore = self.canvas.create_text(500, 20, font="Time_New_Roman 15",
								   text="Victoire(s) Joueur 1: "+str(self.score["J1"]))
		printscore = self.canvas.create_text(500, 620, font="Time_New_Roman 15",
								   text="Victoire(s) Joueur 2: "+str(self.score["J2"]))
		#Evènements
		self.fenetre.unbind('<Enter>')
		self.fenetre.bind('<KeyPress>', root.change_dir)
		self.fenetre.bind('<KeyRelease>', root.stop_dir)
		self.canvas.bind('<Button-1>', self.tirMod8)
		self.canvas.bind('<Button-3>', self.Joueur2.miner)
		#Et on lance la boucle
		self.boucle()
		
	def fin2partie(self):
		#Si le Joueur2 est mort...
		if (self.Joueur1.mort):
			#Réinitialisation
			self.Joueur1.reborn(920, 520)
			self.Joueur2.reborn(80, 80)
			#Score +1
			self.score["J2"] = self.score["J2"] + 1
			#Effacement de la surface (ligne du bas)
			self.canvas.create_rectangle(350, 600, 650, 640, width=0, fil='DarkGoldenRod')
			#Affichage
			printscore = self.canvas.create_text(500, 620, font="Time_New_Roman 15",
								   text="Victoire(s) Joueur 2: "+str(self.score["J2"]))
		#...ou si le Joueur2 est mort
		if (self.Joueur2.mort):
			#Réinitialisation
			self.Joueur1.reborn(920, 520)
			self.Joueur2.reborn(80, 80)
			#Score +1
			self.score["J1"] = self.score["J1"] + 1
			#Effacement de la surface (ligne du haut)
			self.canvas.create_rectangle(350, 0, 650, 40, width=0, fill='DarkGoldenRod')
			#Affichage
			printscore = self.canvas.create_text(500, 20, font="Time_New_Roman 15",
								   text="Victoire(s) Joueur 1: "+str(self.score["J1"]))
		if (self.score["J1"] + self.score["J2"] == 16):
			#=====Défis réussis!=====
			root.save[5] = 1
			root.sauvegarder()
				
				
	def boucle(self):
		"""===Boucle principale du jeu.==="""
		#Mouvement des obus
		for var in range(len(self.Joueurs)):
			self.Joueurs[var].mouvement_obus()
		#Mine:
		for k in range(len(self.Joueurs)):
			if self.Joueurs[k].stock_mine == 0:
				self.Joueurs[k].timer -= 20
			if (self.Joueurs[k].stock_mine == 0) and (self.Joueurs[k].timer == 0):
				self.Joueurs[k].minequiexplose()
		#Déplacement des robots + joueur
		for k in range(len(self.Joueurs)):
			self.Joueurs[k].mouvement_char()
		#Il y a-t-il fin de partie?
		self.fin2partie()
		#C'est une boucle, donc c'est re-ti-par!
		if self.encore:
			self.fenetre.after(20, self.boucle)
		
#On lance le jeu
root = Main()
root.afficher()
root.fenetre.mainloop()











