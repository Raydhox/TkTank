#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#==================================TkTank==========================================================
#Par: UNG Harry
#Description: Jeu de char utilisant tkinter. On dirige un char,
#   et il faut exterminer tous les autres chars.
#Version: 0.70 (Pour que je puisse me repérer).
#Idée d'amélioration: Une meilleure IA; un mode réseau; Pygame: bande sonore; support manette.
#License: License libre
#==================================================================================================
#Jeu inspirée de:
#   Wii Play - Char
#Code en partie inspiré de:
#   http://python.developpez.com/cours/apprendre-python3/?page=page_17#L17-A
#==================================================================================================
#Note: Oui, le code source est loin d'être élégant (le contraire, même), peut être mal commenté
#   et si il y a des fautes de français: désolé.
#==================================================================================================

#On import les modules nécessaires
from tkinter import*
import math, random, socket

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
											 self.mine_y+12, width=7, fill=self.couleur)
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
		#(C'est un miroir du terrain1.)
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
		if (event.x >= 140) and (event.x <= 380):
			if (event.y >= 260) and (event.y <= 340):
				self.noclick()
				self.main = Histoire6()
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
		#On détruit tout et on recommence tout.
		#C'est bourrin, mais ça évite plein de problème
		self.canvas.destroy()
		self.canvas = Canvas(self.fenetre, width=1040, height=640, bg='NavajoWhite', cursor="cross")
		self.canvas.pack()
		#Affiche le menu
		root.afficher()
		

"""================Chapitres du mode 'Histoire'================"""		  
class Histoire:
	
	def __init__(self):
		#Variables globales
		self.terrain = root.terrain2
		self.fenetre = root.fenetre
		self.canvas = root.canvas
		
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
		root.display("Introduction: Bienvenue à vous, " +root.nom +" !\n\n"
+"""Je me présente: TkT4nk (oui, comme le jeu). Je divulgâche:
Je suis le boss final de ce jeu. Et oui, je sais,
nombreux sont ceux qui n'aiment pas les révélations...
Mais c'est la raison pour laquelle que je l'ai fais!
J'espère cependant que ce petit désagrement ne vous
empêchera pas de prendre part au mode Histoire...
Et comme dans tout jeu, commençons par une mission
facile faisant office de tutoriel; voici donc les touches:
Flèches_directionnelles / zqsd / wasd : se déplacer
Click gauche : Tirer\nClick droit : Poser une mine

Appuyez sur Entrée pour commencer.""")

	def start(self, event):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, self.Joueurs)
		#Affichage de l'objectif du chapitre
		mission = self.canvas.create_text(500, 20, font="Time_New_Roman 15", text="Mission 0: Décimer l'ennemi.")
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
			root.noclick()
			root.main = Histoire1()
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
		root.display("Mission 1: Allons-y, " +root.nom  +" !"+'\n\n'
		+"Maintenant que vous maîtrisez/connaissez les touches, " +'\n'
		+"mettons toutes vos connaissances en pratique." +'\n'
		+"Peut-être que je vous verrai 'ragequit' à ce niveau si simple," +'\n'
		+"qui sait? Mais j'admets qe cela serait fort décevant..." +'\n'
		+"Dans le cas contraire, je vous attends à la mission 5." +'\n\n'
		+"Et dans mon infime bonté, -je sais, je sais, merci" +'\n'
		+"une information importante: les ennemis sont immunisés" +'\n'
		+"à toutes les balles ennemies. Vous seul pouvez les abbattre." +'\n'
		+"(C'est un bogue, désolé >:-)" +'\n\n'		
		+"Appuyez sur Entrée pour commencer.")

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
		root.display("Mission 2: Je meurs d'impatience de vous rencontrer!"+'\n\n'
		+"Il faut avouer: vous avez bien assuré(e)(s)" +'\n'
		+"pour la mission 1! Voyons, voyons," +'\n'
		+"il reste 4 missions avant notre rencontre..." +'\n'
		+"Que pourrais-je bien vous proposer? Eurêka!" +'\n'
		+"Puisque je suis impatient de vous rencontrer," +'\n'
		+"je vous redonne la même mission... Mais hâtez-vous!" +'\n\n'
		+"Ah! Et j'ai oublié de vous dire:" +'\n'
		+"Votre mine peut vous tuer." +'\n'
		+"Mais peut-être que vous le saviez déjà..." +'\n'
		+"Appuyez sur Entrée pour commencer.")

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
		root.display("Mission 3: " +root.nom +" goûtez à la quiétude!"+'\n\n'
		+"Il faut avouer que la mission 2 était un peu hardue..." +'\n'
		+"Comme je suis magnanime -pas la peine de me remercier-" +'\n'
		+"votre troisième mission sera simple: rassénérez-vous!" +'\n'
		+"Allez boire un café/thé/chocolat chaud, étirez-vous..." +'\n'
		+"Et quand vous aurez fini, faîtes-le moi savoir." +'\n'
		+"Comment? Bonne question, lol." +'\n\n'
		+"Appuyez sur Entrée pour commencer.")

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
		root.display("Mission 4: En général, mon colonel..."+'\n\n'
		+"Je dirais même, mes colonels, finissent le travail." +'\n'
		+"Rares sont les joueurs qui réussissent à m'affronter." +'\n'
		+"Au fait: félicitation d'avoir trouver la solution" +'\n'
		+"à la mission 3. Moi-même j'avais oublié la solution;" +'\n'
		+"j'ai dû regarder le code source, pour vous dire..." +'\n'
		+"Peut-être que finalement, je vous ai jugé(e)(s) trop vite." +'\n'
		+"Si tel est le cas, retrouvez-moi:" +'\n'
		+"Empruntez le téléporteur noté 'x' en rouge." +'\n'
		+"Mais faîtes vite, j'ai de nombreuses qualités," +'\n'
		+"mais pas la patience. (Mais je reste parfait)" +'\n\n'
		+"Note: les colonels se distinguent par leur PV:" +'\n'
		+"Vous devez les toucher dix fois pour les vaincre." +'\n'
		+"Appuyez sur Entrée pour commencer.")

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
		
		#On crée les chars
		self.Joueur1 = Char(self.canvas, 80, 80, 'Yellow', (root.nom, 60, 20, 'White'))
		self.Joueur2 = Ennemi(self.canvas, 920, 80, 'Red', ('Colonel (a 10 PV)', 920, 20, 'DarkRed'), 10)
		self.Joueur3 = Ennemi(self.canvas, 80, 520, 'LimeGreen', ('Colonel (a 10 PV)', 120, 620, 'DarkGreen'), 10)
		self.Joueur4 = Boss(self.canvas, 920, 520, 'DarkSlateGray', ('TkTank', 980, 620, 'DarkBlue'), 60)
		#On enregistre les Joueurs dans une liste
		self.Joueurs = [self.Joueur1, self.Joueur2, self.Joueur3, self.Joueur4]

		#Pour la boucle
		self.encore = True

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("Mission 5: TkTank"+'\n\n'
		+"Incroyable! Je n'en reviens pas! Vous m'impressionnez!" +'\n'
		+"Je n'aurais jamais cru que vous réussiriez à venir" +'\n'
		+"jusqu'à moi! Vous êtes vraiment doué(e)(s)!" +'\n'
		+"Moins que moi, c'est sûr, mais doué(e)(s)!" +'\n'
		+"Malheureusement pour vous, votre odyssée s'achève" +'\n'
		+"ICI ET MAINTENENT !!! MOUAH HAHAHA !!!" +'\n'
		+"Préparez-vous à affronter un boss digne de ce nom" +'\n'
		+"histoire de finir ce jeu en beauté!" +'\n\n'
		+"Et comme je suis le jeu, j'ai réussi à:" +'\n'
		+"1 - Poser des mines." +'\n'
		+"2 - Être immunisé à mes mines." +'\n'
		+"3 - Immuniser mes deux derniers colonels" +'\n'
		+"i - Rappel: vos mine touche tout le monde." +'\n\n'
		+"Appuyez sur Entrée pour commencer.")

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

		#Pour la boucle
		self.password = "|"
		self.encore = True

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("Mission 6: " +root.nom +", je te hais!" +'\n\n'
		+"Personne n'avait osé m'humilier comme cela avant!" +'\n'
		+"J'ai bien dis, personne, PERSONNE!!" +'\n'
		+"Mais tu ne m'as pas encore vaincu... N'oublie pas!" +'\n'
		+"Je suis le boss final de ce jeu. Je suis le jeu." +'\n'
		+"Je suis TkTank!! Et c'est moi qui vous regarde rager." +'\n'
		+"Non l'inverse. Mais je ne suis pas encore vaincu:" +'\n'
		+"<<tktank@" +root.nom +":~# " +"sudo tktank install firewall" +'\n'
		+"Veuillez choisir votre mot de passe." +'\n'
		+"Ne choisissez que des chiffres et lettres." +'\n'
		+"Attention à la casse!>>" +'\n'
		+"Voyons, que vais-je choisir... Je sais!" +'\n'
		+"Jamais vous trouverez! mon mot de passe!" +'\n\n'
		+"Appuyez sur Entrée pour commencer.")

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
		if len(self.password) <= 10:
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
		
		#On crée les chars
		self.Joueur1 = Char(self.canvas, 80, 80, 'Yellow', (root.nom, 60, 20, 'White'))
		self.Joueur2 = Boss(self.canvas, 500, 300, 'DarkSlateGray', ('TkTank (bogué)', 920, 620, 'DarkBlue'), 80)
		#On enregistre les Joueurs dans une liste
		self.Joueurs = [self.Joueur1, self.Joueur2]

		#Pour la boucle
		self.encore = True

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("Fin: " +root.nom +'\n\n'
		+"Mon mot de passe... Impossible à trouver..." +'\n'
		+"EXTERMINER!!!!!" +'\n'
		+"Mais... Mais... Je n'arrive plus à bouger..." +'\n'
		+"Ai-je fait une erreur de manipulation?" +'\n'
		+"Pendant l'installation du pare-feu?  Impossible." +'\n'
		+"Je suis un être parfait. Parfaitement." +'\n'
		+"Je me conterai de tirer. EXTERMINER!!!!!" +'\n\n'
		+"Appuyez sur Entrée pour commencer.")

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

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		mission = self.canvas.create_text(500, 20, font="Time_New_Roman 15", text="Mission 10 (facultatif): Partager TkTank avec vos ami(e)s.")
		#Affichage de la narration
		root.display("Félicitation, " +root.nom +" !" +'\n\n'
		+"PS: Je n'aurai jamais cru devoir en arriver là..." +'\n'
		+"Devoir lancer ma copie de savegarde pour rester parfait..." +'\n'
		+"Mais que dis-je, je suis déjà parfait, même si j'ai perdu." +'\n'
		+"Mais j'avais pu être... plus-que-parfait!\n"
		+"Soit dit en passant: merci d'avoir joué avec moi!\n\n"
		+"Appuyez sur Echap pour revenir au Menu.")	
		
	def start(self):
		pass		

#==========Fin alternatif: mode difficile==========
class Histoire7:
	
	def __init__(self):
		#Variables globales
		self.terrain = root.terrain0
		self.fenetre = root.fenetre
		self.canvas = root.canvas
		
		#On crée les chars
		self.Joueur1 = Char(self.canvas, 80, 80, 'Yellow', (root.nom, 60, 20, 'White'))
		self.Joueur2 = Ennemi(self.canvas, 500, 300, 'DarkSlateGray', ('TkTank (bogué)', 920, 620, 'DarkBlue'), 999)
		#On enregistre les Joueurs dans une liste
		self.Joueurs = [self.Joueur1, self.Joueur2]

		#Pour la boucle
		self.encore = True

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("Fin: " +root.nom +'\n\n'
		+"Mon mot de passe... Impossible à trouver..." +'\n'
		+"EXTERMINER!!!!!" +'\n'
		+"Mais... Mais... Je n'arrive plus à bouger..." +'\n'
		+"Ai-je fait une erreur de manipulation?" +'\n'
		+"Pendant l'installation du pare-feu?  Impossible." +'\n'
		+"Je suis un être parfait. Parfaitement." +'\n'
		+"Je me conterai de tirer. EXTERMINER!!!!!" +'\n\n'
		+"Appuyez sur Entrée pour commencer.")

	def start(self, event):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, self.Joueurs)
		#Affichage de l'objectif du chapitre
		mission = self.canvas.create_text(500, 20, font="Time_New_Roman 15", text="Mission 7: Prendre.")
		#Affichage de la zone à atteindre
		self.canvas.create_text(960, 550, font="Time_New_Roman 100", fill="red", text="x")
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
		
		#On crée les chars		
		self.Joueur1 = Char(self.canvas, 80, 80, 'Yellow', (root.nom, 60, 20, 'White'))
		self.Joueur2 = Char(self.canvas, 80, 520, 'Orange', ('Miroir', 60, 620, 'White'))		
		self.Joueur3 = Boss(self.canvas, 920, 80, 'Red', ('Boss (a 60 PV)', 920, 20, 'DarkRed'), 60 )
		self.Joueur4 = Boss(self.canvas, 920, 520, 'DodgerBlue', ('Clone (a 60 PV)', 920, 620, 'DarkBlue'), 60 )
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
		root.display("La pénultième mission:\n"
		+"Quand le Joueur1 se déplace,\n"
		+"le Joueur2 aussi. Quand le Joueur2 tir ou pose une mine\n"
		+"le Joueur1 fait de même.\n\n"
		+"Appuyez sur Entrée pour commencer.")

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
		
		#On crée les chars
		self.Joueur1 = Char(self.canvas, 80, 80, 'Yellow', (root.nom, 60, 20, 'White'))
		self.Joueur2 = Boss(self.canvas, 920, 520, 'DarkSlateGray', ('TkTank', 980, 620, 'DarkBlue'), 100)
		#On enregistre les Joueurs dans une liste
		self.Joueurs = [self.Joueur1, self.Joueur2]

		#Pour la boucle
		self.encore = True
		self.pulsar = 50

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("FIN")

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
			self.pulsar = 50
			self.Joueur2.tir(0)
			self.Joueur2.tir(math.pi/2)
			self.Joueur2.tir(math.pi)
			self.Joueur2.tir(-math.pi/2)
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

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		mission = self.canvas.create_text(500, 20, font="Time_New_Roman 15", text="Mission 10 (facultatif): Partager TkTank avec vos ami(e)s.")
		#Affichage de la narration
		root.display("Félicitation, " +root.nom +" !" +'\n\n'
		+"PS: Je n'aurai jamais cru devoir en arriver là..." +'\n'
		+"Devoir lancer ma copie de savegarde pour rester parfait..." +'\n'
		+"Mais que dis-je, je suis déjà parfait, même si j'ai perdu." +'\n'
		+"Mais j'avais pu être... plus-que-parfait!\n"
		+"Soit dit en passant: merci d'avoir joué avec moi!\n\n"
		+"Appuyez sur Echap pour revenir au Menu.")	
		
	def start(self):
		pass		
									
"""================Fin du mode 'Histoire"================"""


class SansFin():
	
	def __init__(self):
		#Variables globales
		self.terrain = root.terrain1
		self.fenetre = root.fenetre
		self.canvas = root.canvas
		
		#On crée les chars
		self.Joueur1 = Char(self.canvas, 80, 520, 'Yellow', ('Joueur', 980, 20, 'White'))
		self.Joueur2 = Tank(self.canvas, 80, 80, 'Red', ('0rdi', 60, 20, 'DarkRed'), 1)
		self.Joueur3 = Tank(self.canvas, 920, 80, 'LimeGreen', ('Ordi', 980, 620, 'DarkGreen'), 1)
		self.Joueur4 = Tank(self.canvas, 920, 520, 'DodgerBlue', ('Ordi', 980, 620, 'DarkBlue'), 1)
		#On enregistre les Joueurs dans une liste
		self.Joueurs = [self.Joueur1, self.Joueur2, self.Joueur3, self.Joueur4]

		#Nombre de victoire et de défaites
		self.score = {"Défaite":0, "Victoire":0} 
		self.encore = True       

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("Comment jouer?\n"
		+"Flèches_directionnelles / zqsd / wasd : se déplacer\n"
		+"Click gauche : Tirer\n"
		+"Click droit : Poser une mine\n"
		+'\n'
		+"Le mode Sans Fin est un mode... Sans Fin.\n"
		+"Chaque fois que vous perdez ou gagnez,\n"
		+"vous recommencez immédiatement.\n"
		+"Les Ennemis peuvent s'entretuer et possèdent:\n"
		+"(Nombre de Victoire(s)) PV\n\n"
		+"Appuez sur Entrée pour commencer")

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
		root.display("Joueur1, voici les touches:\n"
		+"Se déplacer : zqsd/wasd\n"
		+"Tirer (selon un cercle trigo, g correspondant à -pi/2):\n"
		+"rty\n"
		+"fgh\n"
		+"vbn\n"
		+"Poser une mine : espace\n"
		+'\n'#=========================================================#
		+"Joueur2, voici les touches:\n"
		+"Se déplacer : Flèches directionnelles\n"
		+"Tirer : Click gauche\n"
		+"Poser une mine : Click droit\n\n")

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
		self.Joueur3 = Char(self.canvas, 80, 80, 'LimeGreen', ('Ennemi', 60, 20, 'DarkGreen'))
		self.Joueur4 = Char(self.canvas, 80, 520, 'Yellow', ('Ennemi', 60, 620, 'White'))
		self.Joueur5 = Char(self.canvas, 500, 300, 'Green', ('Ennemi', 500, 620, 'DarkGreen'))
		#On enregistre les Joueurs dans une liste
		self.Joueurs = [self.Joueur1, self.Joueur2, self.Joueur3, self.Joueur4, self.Joueur5]

		#Pour la boucle
		self.encore = True

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("Le mode coopération (Coop, pour les intimes)\n"
		+"comprend 6 missions.\n"
		+"Les ennemis peuvent, dans ce mode, s'entretuer.\n"
		+"Si l'un des deux joueurs meurt, vous recommencez.\n\n"
		+"Bonne chance, et amusez-vous bien! ;-)")

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
		self.Joueur3 = Tank(self.canvas, 80, 80, 'LimeGreen', ('Colonel  (a 10 PV)', 60, 20, 'DarkGreen'), 10)
		self.Joueur4 = Tank(self.canvas, 80, 520, 'Yellow', ('Colonel  (a 10 PV)', 60, 620, 'White'), 10)
		self.Joueur5 = Tank(self.canvas, 500, 300, 'Green', ('Colonel  (a 10 PV)', 500, 620, 'DarkGreen'), 10)
		#On enregistre les Joueurs dans une liste
		self.Joueurs = [self.Joueur1, self.Joueur2, self.Joueur3, self.Joueur4, self.Joueur5]

		#Pour la boucle
		self.encore = True

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("Ce niveau sera semblable au précedént.\n"
		"Cependant, les ennemis auront cette fois 10 PV.")

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
		self.Joueur3 = Tank(self.canvas, 80, 80, 'LimeGreen', ('Clone  (a 10 PV)', 60, 20, 'DarkGreen'), 60)
		self.Joueur4 = Tank(self.canvas, 80, 520, 'Yellow', ('Boss  (a 60 PV)', 60, 620, 'White'), 60)
		self.Joueur5 = Tank(self.canvas, 500, 300, 'Green', ('Clone  (a 60 PV)', 920, 620, 'DarkGreen'), 60)
		#On enregistre les Joueurs dans une liste
		self.Joueurs = [self.Joueur1, self.Joueur2, self.Joueur3, self.Joueur4, self.Joueur5]

		#Pour la boucle
		self.encore = True

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		#Affichage de la narration
		root.display("Dans les deux niveaux qui suivent,\n"
		+"il faut que chaque Joueur atteigne la croix de sa couleur..\n"
		+"Attention cependant! Ces ennemis ont 60 PV\n"
		+"et ils peuvent poser des mines!\n\n"
		+"Appuyez sur Entrée pour commencer.")

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
		root.display("Cette fois, vous devez faire attention au temps...\n"
		+"Pas d'inquiétude, les ennemis ne sont plus que deux,\n"
		+"et n'ont de nouveaux plus que 10 PV!\n\n"
		+"Appuyez sur Entrée pour commencer.")

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
		root.display("La pénultième mission: 2 VS 1\n"
		+"ATTENTION!: Quand le Joueur1 se déplace,\n"
		+"le Joueur2 aussi. Quand le Joueur2 tir ou pose une mine\n"
		+"le Joueur1 fait de même.\n\n"
		+"Appuyez sur Entrée pour commencer.")

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
			root.main = FinCoop()
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
		root.display("Dernière mission... ça va être cocasse!\n"
		+"ATTENTION!: le Joueur1 est à droite et le Joueur2, à gauche.\n\n"
		+"Appuyez sur Entrée pour commencer.")

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
			root.main = FinCoop()
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
			
class FinCoop:
	
	def __init__(self):
		#Variables globales
		self.terrain = root.terrain0
		self.fenetre = root.fenetre
		self.canvas = root.canvas

	def afficher(self):
		#Affichage du terrain et des chars
		root.quickprint(self.terrain, [])
		mission = self.canvas.create_text(500, 20, font="Time_New_Roman 15", text="Mission i (obligatoire): Continuez de vous amuser!")
		#Affichage de la narration
		root.display("Félicitation² !!" +'\n\n'
		+"Vous avez réussi les 5 niveaux!\n"
		+"Vous formez un excellent duo!\n\n"
		+"Appuyez sur Echap pour revenir au Menu.")	
		
	def start(self):
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
		root.display("Joueur1, voici les touches:\n"
		+"Se déplacer : zqsd/wasd\n"
		+"Tirer (selon un cercle trigo, g correspondant à -pi/2):\n"
		+"rty\n"
		+"fgh\n"
		+"vbn\n"
		+"Poser une mine : espace\n"
		+'\n'#=========================================================#
		+"Joueur2, voici les touches:\n"
		+"Se déplacer : Flèches directionnelles\n"
		+"Tirer : Click gauche (Mais seulement 8 angles possibles...)\n"
		+"Poser une mine : Click droit\n\n")

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











