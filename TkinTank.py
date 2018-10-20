#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#==================================TkinTank==========================================================
#Par: UNG Harry
#	2nde-5: Initialisation du projet
#	TS4: Finalisation du prototype; le jeu fonctionne enfin.
#	MPSI2: Concaténation, amélioration.
#Description: Jeu de char utilisant tkinter. On dirige un char,
#   et il faut exterminer tous les autres chars. L'objectif finale est un jeu complet avec:
#   Un mode histoire, une multi local et réseau, le tout agrémenté de multitude d'option et de musique!
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
import math, random


#================================LES PERSONNAGES================================#
#On crée une classe char
class Char():
	
	def __init__(self, fenetre, canvas, x, y, couleur, nom, vitesse=2, relief=1):
		"""Où 'canvas' le nom du Canvas,
'x' et 'y' les coordonnées du char,
nom, un tuple sous la forme:nom = ('nom', x, y, couleur)"""
		#Le "monde" dans lequel évolue le char (fenêtre, canvas)
		self.fenetre = fenetre
		self.canvas = canvas
		#Données qui seront initialisées plus tard (dans la fonction afficher)
		self.terrain = None
		self.Joueurs = None
		#Coordonnée du char
		self.char_x, self.char_x0 = x, x
		self.char_y, self.char_y0 = y, y
		#Coordonnée du canon
		self.alpha = math.pi/2
		self.canon_x = self.char_x + 20 + 32*math.sin(0)
		self.canon_y = self.char_y + 20 - 32*math.cos(0)
		#Pour la mine
		self.mine = None
		self.mine_x = 0
		self.mine_y = 0
		self.stock_mine = 1
		self.timer = 5000
		#Pour les munitions
		self.munition = []
		#Pour le mouvement
		self.dir = [False, False, False, False]
		self.vitesse = vitesse
		#Autre caractéristique ( couleur du char, nom, état (mort ou pas?), relief (taille des bordures) )
		self.couleur = couleur
		self.nom = nom
		self.mort = False
		self.relief = relief

		
	def afficher(self, terrain, Joueurs):
		"""===Fonction qui affiche le char et le nom du joueur. Permet aussi d'initialiser quelques données.==="""
		#Les données
		self.terrain = terrain
		self.Joueurs = Joueurs
		#Affichage
		self.nom = self.canvas.create_text(self.nom[1], self.nom[2], font="Time_New_Roman 15",
										   text=str(self.nom[0]), fill=self.nom[3])
		self.char = self.canvas.create_rectangle(self.char_x, self.char_y, self.char_x+40,
												 self.char_y+40, width=self.relief, fill=self.couleur)       
		self.pivot = self.canvas.create_oval(self.char_x+32, self.char_y+32, self.char_x+8,
											 self.char_y+8, width=2*self.relief, fill='black')
		self.canon = self.canvas.create_line(self.char_x+20, self.char_y+20, self.canon_x,
											 self.canon_y, width=6+2*self.relief)
											 
	def option(self, vitesse=0, relief=0):
		"""Change les options du char."""
		if vitesse:
			self.vitesse = vitesse
		if relief:
			self.relief = relief
			self.canvas.itemconfig(self.char, width=self.relief)
			self.canvas.itemconfig(self.pivot, width=2*self.relief)
			self.canvas.itemconfig(self.canon, width=6+2*self.relief)
			try:
				self.canvas.itemconfig(self.mine, width=2+2*self.relief)
			except:
				pass
		

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
			
			
	def mouvement_char(self):
		"""===Mouvement du char==="""
		#Variables globales
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
			what = False
			for var in range(len(self.Joueurs)):                
				if (self.char_x+20 > self.Joueurs[var].char_x-20) and (self.char_x+20 < self.Joueurs[var].char_x+60)\
				and (self.char_y+18 > self.Joueurs[var].char_y-20) and (self.char_y+18 < self.Joueurs[var].char_y+60)\
				and (self.couleur != self.Joueurs[var].couleur) and (card == 8):
					what = True
					break
				elif (self.char_x+21 > self.Joueurs[var].char_x-20) and (self.char_x+21 < self.Joueurs[var].char_x+60)\
				and (self.char_y+20 > self.Joueurs[var].char_y-20) and (self.char_y+20 < self.Joueurs[var].char_y+60)\
				and (self.couleur != self.Joueurs[var].couleur) and (card == 6):
					what = True
					break
				elif (self.char_x+18 > self.Joueurs[var].char_x-20) and (self.char_x+18 < self.Joueurs[var].char_x+60)\
				and (self.char_y+20 > self.Joueurs[var].char_y-20) and (self.char_y+20 < self.Joueurs[var].char_y+60)\
				and (self.couleur != self.Joueurs[var].couleur) and (card == 4):
					what = True
					break
				elif (self.char_x+20 > self.Joueurs[var].char_x-20) and (self.char_x+20 < self.Joueurs[var].char_x+60)\
				and (self.char_y+21 > self.Joueurs[var].char_y-20) and (self.char_y+21 < self.Joueurs[var].char_y+60)\
				and (self.couleur != self.Joueurs[var].couleur) and (card == 2):
					what = True
					break
			return what
		#...on se déplace...
		if (self.dir[0] == True):
			#...Si il n'y a pas de collision avec une brique ou un char:
			if (self.terrain[math.floor((self.char_y-self.vitesse)/40)][coordx] != '1')\
			and (self.terrain[math.floor((self.char_y-self.vitesse)/40)][coordx2] != '1')\
			and (test_collision(8) is False):
				self.char_y -= self.vitesse
		if (self.dir[1] == True):
			#...Si il n'y a pas de collision avec une brique ou un char:
			if (self.terrain[coordy][math.floor((self.char_x-self.vitesse)/40)] != '1')\
			and (self.terrain[coordy2][math.floor((self.char_x-self.vitesse)/40)] != '1')\
			and (test_collision(4) is False):
				self.char_x -= self.vitesse
		if (self.dir[2] == True):
			#...Si il n'y a pas de collision avec une brique ou un char:
			if (self.terrain[math.floor((self.char_y+39+self.vitesse)/40)][coordx] != '1')\
			and (self.terrain[math.floor((self.char_y+39+self.vitesse)/40)][coordx2] != '1')\
			and (test_collision(2) is False):
				self.char_y += self.vitesse
		if (self.dir[3] == True):
			#...Si il n'y a pas de collision avec une brique ou un char:
			if (self.terrain[coordy][math.floor((self.char_x+39+self.vitesse)/40)] != '1')\
			and (self.terrain[coordy2][math.floor((self.char_x+39+self.vitesse)/40)] != '1')\
			and (test_collision(6) is False):
				self.char_x += self.vitesse
		#Calul des nouvelles positions du canon
		self.canon_x = self.char_x + 20 + 32*math.cos(self.alpha)
		self.canon_y = self.char_y + 20 - 32*math.sin(self.alpha)
		#Affichage        
		self.canvas.coords(self.char, self.char_x, self.char_y, self.char_x+40, self.char_y+40)
		self.canvas.coords(self.pivot, self.char_x+32, self.char_y+32,
						   self.char_x+8, self.char_y+8)
		self.canvas.coords(self.canon, self.char_x+20, self.char_y+20, self.canon_x, self.canon_y)

	def obus(self, vitesse, angle, coord_x, coord_y):
		"""Crée les obus sous forme de dictionnaire stocké dans une liste."""
		self.munition.append({	'vecteur_x':vitesse*math.cos(angle),
								'vecteur_y':-vitesse*math.sin(angle),
								'obus_x':coord_x, 'obus_y':coord_y,
								#Affichage
								'obus':self.canvas.create_oval(coord_x-3, coord_y-3,
															   coord_x+3, coord_y+3,
															   width=self.relief, fill=self.couleur)  })
														   
		
	def tir(self, event):
		"""===Gère le tir.==="""
		self.mouvement_canon(event)
		self.obus(3, self.alpha, self.canon_x, self.canon_y)
	
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
	
	def mouvement_obus(self):
		"""===Mouvement des obus.==="""
		#Variables pour la supression d'obus
		obus_del = []
		count = -1
		#Pour tous les obus:
		for k in range(len(self.munition)):
			#Déplacement
			self.munition[k]['obus_x'] += self.vitesse*self.munition[k]['vecteur_x']
			self.munition[k]['obus_y'] += self.vitesse*self.munition[k]['vecteur_y']
			self.canvas.coords(self.munition[k]['obus'], self.munition[k]['obus_x'],
							   self.munition[k]['obus_y'], self.munition[k]['obus_x']+6,
							   self.munition[k]['obus_y']+6)
			#Position relative, correspondant au "coordonées des cases" de 40*40
			coordx = int(self.munition[k]['obus_x']/40)
			coordy = int(self.munition[k]['obus_y']/40)
			#Si il y a collision avec un mur (brique)
			if (self.terrain[coordy][coordx] == '1'):
				obus_del.append(k)
			#Si il y a collision avec un char...
			for var in range(len(self.Joueurs)):
				if (self.munition[k]['obus_x'] >= self.Joueurs[var].char_x)\
				and (self.munition[k]['obus_x'] <= self.Joueurs[var].char_x+40)\
				and (self.munition[k]['obus_y'] >= self.Joueurs[var].char_y)\
				and (self.munition[k]['obus_y'] <= self.Joueurs[var].char_y+40):
					obus_del.append(k)
					self.Joueurs[var].rip()
		#Les obus arretées sont supprimées
		for k in obus_del:
			count += 1
			kappa = k - count
			self.canvas.delete(self.fenetre, self.munition[kappa]['obus'])
			del self.munition[kappa]


	def miner(self, event):
		"""===Mine (=click droit)==="""
		#On crée la mine (un cercle)...
		self.mine_x = self.char_x + 20 + 32*math.sin(self.alpha+math.pi*1.5)
		self.mine_y = self.char_y + 20 + 32*math.cos(self.alpha+math.pi*1.5)
		#...si ses extrémités...
		coordx = int((self.mine_x-12)/40)
		coordy = int((self.mine_y-12)/40)
		coordx2 = int((self.mine_x+12)/40)
		coordy2 = int((self.mine_y+12)/40)
		#...ne cogne pas un char...
		pas2collision_char = True
		for var in range(len(self.Joueurs)):
			if (self.mine_x >= self.Joueurs[var].char_x) and (self.mine_x <= self.Joueurs[var].char_x+40)\
			and (self.mine_y >= self.Joueurs[var].char_y) and (self.mine_y <= self.Joueurs[var].char_y+40):
				pas2collision_char = False
		#...ou un mur, ou si une mine a déjà été crée
		if (self.terrain[coordy][coordx] != '1') and (self.terrain[coordy2][coordx2] != '1')\
		and (pas2collision_char) and (self.stock_mine):
			self.mine = self.canvas.create_oval(self.mine_x-12, self.mine_y-12, self.mine_x+12,
											 self.mine_y+12, width=2+2*self.relief, fill=self.couleur)
			#Pour éviter de mettre plusieurs mines
			self.stock_mine = 0

	
	def minequiexplose(self):
		"""===Explosion de la mine==="""
		self.canvas.delete(self.fenetre, self.mine)
		#On peut de nouveau posé une mine
		self.stock_mine = 1
		self.timer = 5000
		#Création d'obus (dictionnaire stocké dans une liste)
		for k in range(69):
			self.obus(6, k*0.4, self.mine_x, self.mine_y)


	def rip(self):
		"""===Mort du char (déplacement hors de l'écran pour ne pas créer d'erreur dû au évènement).==="""
		self.mort = True
		#Nouvelles positions du char
		self.char_x = 1
		self.char_y = 666
		#Calcul des nouvelles positions du canon
		self.canon_x = self.char_x + 20 + 32*math.cos(self.alpha)
		self.canon_y = self.char_y + 20 - 32*math.sin(self.alpha)
		#Affichage
		self.canvas.coords(self.char, self.char_x, self.char_y, self.char_x+40, self.char_y+40)
		self.canvas.coords(self.pivot, self.char_x+32, self.char_y+32,
						   self.char_x+8, self.char_y+8)
		self.canvas.coords(self.canon, self.char_x+20, self.char_y+20, self.canon_x, self.canon_y)

	
	def reborn(self):
		"""===Renaissance du char: Réinitialisation des variables==="""
		self.mort = False
		#Les obus sont supprimés
		count = 0
		for k in range(len(self.munition)):
			count += 1
			kappa = k - count
			self.canvas.delete(self.fenetre, self.munition[kappa]['obus'])
			del self.munition[kappa]
		#La mine est également supprimés
		self.canvas.delete(self.fenetre, self.mine)
		self.stock_mine = 1
		self.timer = 5000
		#Nouvelles positions du char
		self.char_x = self.char_x0
		self.char_y = self.char_y0
		#Calcul des nouvelles positions du canon
		self.alpha = math.pi/2
		self.canon_x = self.char_x + 20 + 32*math.cos(self.alpha)
		self.canon_y = self.char_y + 20 - 32*math.sin(self.alpha)
		#Affichage
		self.canvas.coords(self.char, self.char_x, self.char_y, self.char_x+40, self.char_y+40)
		self.canvas.coords(self.pivot, self.char_x+32, self.char_y+32, self.char_x+8, self.char_y+8)
		self.canvas.coords(self.canon, self.char_x+20, self.char_y+20, self.canon_x, self.canon_y)
		self.canvas.coords(self.canon, self.char_x+20, self.char_y+20, self.canon_x, self.canon_y)


class Ennemi(Char):
	
	def __init__(self, fenetre, canvas, x, y, couleur, nom, fps, relief, pv=1):
		#Classe qui hérite de le classe Char
		Char.__init__(self, fenetre, canvas, x, y, couleur, nom, fps, relief)
		self.pv, self.pv2base = pv, pv
	
	def dirobot(self, event):
		#Gère la direction pour les Robots
		if (event == 'Up'):
			self.dir[0] = True
			self.dir[2] = False
		elif (event == 'Left'):
			self.dir[1] = True
			self.dir[3] = False
		elif (event == 'Down'):
			self.dir[2] = True
			self.dir[0] = False
		elif (event == 'Right'):
			self.dir[3] = True
			self.dir[1] = False
	
	def ia(self, cible=(520, 320) ):
		#Position relative, correspondant au "coordonées des cases" de 40*40...
		coordx = int(self.char_x/40)
		coordy = int(self.char_y/40)
		coordx2 = int((self.char_x+39)/40)
		coordy2 = int((self.char_y+39)/40)
		#...après déplacement vers le haut / bas
		coordyUp = int((self.char_y-self.vitesse)/40)
		coordyDown = int((self.char_y+40+self.vitesse)/40)
		#...après déplacement vers la gauche / droite
		coordxLeft = int((self.char_x-self.vitesse)/40)
		coordxRight = int((self.char_x+40+self.vitesse)/40)

		#Pour un déplacement un peu plus aléatoire
		rng = random.randrange(0, 100)
		#Faible chance de déplcement aléatoire (parce que c'est drôle, et pour éviter de coller au mur):
		if rng < 3:     
			#Déplacement dans une direction aléatoire
			self.dirobot(['Up', 'Down', 'Left', 'Right'][random.randrange(0, 4)])        
		#Sinon il n'y a pas de collision avec une brique (Haut, Bas, Gauche, Droite):
		elif (self.terrain[coordyUp][coordx] != '1') and (self.terrain[coordyUp][coordx2] != '1')\
		and (self.terrain[coordyDown][coordx] != '1') and (self.terrain[coordyDown][coordx2] != '1')\
		and (self.terrain[coordy][coordxLeft] != '1') and (self.terrain[coordy2][coordxLeft] != '1')\
		and (self.terrain[coordy][coordxRight] != '1') and (self.terrain[coordy2][coordxRight] != '1'):
			"""=====Déplacement qui se rapproche de la cible====="""     
			#Si le centre est au-dessus du robot, alors il va en haut
			if cible[1] < self.char_y:
				self.dirobot('Up')
			#Sinon, il descend
			elif cible[1] > self.char_y:
				self.dirobot('Down')
			#Si le centre est à gauche du robot, alors il va à gauche
			if cible[0] < self.char_x:
				self.dirobot('Left')
			#Sinon, il va à droite
			elif cible[0] > self.char_x:
				self.dirobot('Right')
		else:
			"""...déplacement "Sens Trigo": Haut |-> Droite |-> Bas |-> Gauche |-> Haut"""
			#...en haut
			if int(self.terrain[coordyUp][coordx]) or int(self.terrain[coordyUp][coordx2]):
				self.dirobot('Right')
			#...à droite
			if int(self.terrain[coordy][coordxRight]) or int(self.terrain[coordy2][coordxRight]):
				self.dirobot('Down')
			#...en bas
			if int(self.terrain[coordyDown][coordx]) or int(self.terrain[coordyDown][coordx2]):
				self.dirobot('Left')
			#...à gauche
			if int(self.terrain[coordy][coordxLeft]) or int(self.terrain[coordy2][coordxLeft]):
				self.dirobot('Up')

			
		#===Tir dirigé vers le joueur à cadence aléatoire (%)
		rdg = random.randrange(0, 100)
		if rdg <= 20:
			#Tir dirigé contre le Joueur
			#Trigo et Pythagore
			adj = cible[0] - self.char_x
			hypo = math.sqrt((cible[0] - self.char_x)**2 + (cible[1] - self.char_y)**2)
			if hypo == 0:
				hypo = 0.01
			self.alpha = math.acos(adj/hypo)
			#Angle obtus ou angle aigus?
			if cible[1] > self.char_y:
				self.alpha = - self.alpha
			#===Mouvement canon===
			#Calul des nouvelles positions du canon
			self.canon_x = self.char_x + 20 + 32*math.cos(self.alpha)
			self.canon_y = self.char_y + 20 - 32*math.sin(self.alpha)
			#Affichage
			self.canvas.coords(self.canon, self.char_x+20, self.char_y+20, self.canon_x, self.canon_y)
			self.obus(3, self.alpha, self.canon_x, self.canon_y)
	
	"""Reprogramation des fonction gérant la mort du char."""
	def rip(self):
		self.pv -= 1
		if self.pv <= 0:
			Char.rip(self)
	
	def reborn(self):
		Char.reborn(self)
		self.pv = self.pv2base


#================================LE JEU================================#

#On crée une classe "Racine" qui contient (+ ou -) le moteur du jeu.
class Root():

	def __init__(self, Menu):
		#On crée une fenêtre tkinter 'fenetre'
		self.fenetre = Tk()
		self.fenetre.config(width=1040, height=640, bg="NavajoWhite")
		self.fenetre.title("TkTank.py")
		self.fenetre.geometry("+0+0")
		
		#Gestion du temps
		#(Soit ici, 50 images par secondes)
		self.fps = 20
		#Gestion des graphismes
		self.relief = 1

		#On crée un Canvas 'jeu'
		self.canvas = Canvas(self.fenetre, width=1040, height=640, bg='NavajoWhite', cursor="cross")
		self.canvas.place(relx=0.5, rely=0.5, anchor=CENTER)#side=LEFT)
		
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
		
		#Liste des terrains disponibles
		self.terrains = (self.terrain0, self.terrain1,self.terrain2) 
		
		
		#Lançe le menu principal (dans la démo, il n'y a pas de menu)
		self.Main0 = Menu
		self.main = Menu(self.fenetre, self.canvas, self.terrains, self.fps, self.relief)
		self.main.commencer()
		
		#Echap permet de revenir sur le Menu pincipal
		self.fenetre.bind('<Escape>', self.gotoMenu)
		
	def gotoMenu(self, event):
		#Lançe le menu...
		self.main = self.Main0(self.fenetre, self.canvas, self.terrains, self.fps, self.relief)
		#...et l'affiche
		self.canvas.create_rectangle(0, 0, 1040, 640, width=0, fill="NavajoWhite")
		self.main.commencer()
	
	def optionvit(self, event):
		if self.fps > 10:
			self.fps = int(self.fps/2)
		else:
			self.fps = 40
		#print(int(1000/self.fps))
		for var in range(len(self.Joueurs)):
			self.main.Joueurs[var].option(vitesse=int(self.fps/10))
	
	def optionrel(self, event):
		if self.main.Joueur1.relief < 3:
			relief = self.main.Joueur1.relief + 1
		else:
			relief = 1
		for var in range(len(self.main.Joueurs)):
			self.main.Joueurs[var].option(relief=relief)
	
	def afficher(canvas, terrain, Joueurs):
		#On parcours la liste et en fonction des valeurs, on affiche une brique ou non
		for k1 in range(16):
			for k2 in range(26):
				if terrain[k1][k2] == '1':
					x = k2*40
					y = k1*40
					canvas.create_rectangle(x, y, x+40, y+40, width=0, fill='DarkGoldenRod')
		#On affiche les chars...
		for var in range(len(Joueurs)):
			Joueurs[var].afficher(terrain, Joueurs)
	
	def boucle(self):
		#Mouvement des obus
		for var in range( len(self.main.Joueurs) ):
			self.main.Joueurs[var].mouvement_obus()
		#Mine:
		for k in range( len(self.main.Joueurs) ):
			if self.main.Joueurs[k].stock_mine == 0:
				self.main.Joueurs[k].timer -= self.fps
			if (self.main.Joueurs[k].stock_mine == 0) and (self.main.Joueurs[k].timer <= 0):
				self.main.Joueurs[k].minequiexplose()
		#Déplacement des robots + joueur
		for k in range( len(self.main.Joueurs)-1 ):
			try:
				self.main.Joueurs[k+1].ia( (self.main.Joueur1.char_x, self.main.Joueur1.char_y) )
			except:
				pass
		for k in range( len(self.main.Joueurs) ):
			self.main.Joueurs[k].mouvement_char()
		#Il y a-t-il fin de partie?
		self.main.recommencer()
		#Si l'ont change de chapitre
		if self.main.fin2partie():
			self.main = self.main.fin2partie()
			#On efface ce qu'il y avait avant.
			self.canvas.create_rectangle(0, 0, 1040, 640, width=0, fill="NavajoWhite")
			#Et on lance le  nouveau chapitre
			self.main.commencer()
		#C'est une boucle, donc c'est re-ti-par!
		self.fenetre.after(self.fps, self.boucle)
		

class Menu(Root):

	def __init__(self, fenetre, canvas, terrains, fps, relief):
		#Données globales
		self.fenetre, self.canvas, self.terrains, self.fps, self.relief = fenetre, canvas, terrains, fps, relief
		self.terrain = terrains[0]
		
		#Chars décoratifs
		self.Joueur0 = Char(self.fenetre, self.canvas, 260, 200, 'Yellow', ('', 0, 0, 'White'), int(fps/10), relief)
		self.Joueur1 = Char(self.fenetre, self.canvas, 730, 200, 'Red', ('', 0, 0, 'DarkRed'), int(fps/10), relief)
		self.Joueur2 = Char(self.fenetre, self.canvas, 790, 200, 'DodgerBlue', ('', 0, 0, 'DarkBlue'), int(fps/10), relief)
		#On enregistre les Joueurs dans une liste
		self.Joueurs = [self.Joueur0, self.Joueur1, self.Joueur2]
		
		#Le mode de jeu choisi par le joueur
		self.choix = 0
		
	def commencer(self):
		Root.afficher(self.canvas, self.terrain, self.Joueurs)	
		#On affiche le titre
		self.canvas.create_text(520, 100, font="Comic_Sans_MS 100", fill="DarkGoldenRod", text="TkT4nk")
		#On affiche les modes de jeu disponible
		#===Défis===
		self.canvas.create_rectangle(40, 40, 120, 120, width=1)
		self.canvas.create_text(80, 80, font="Comic_Sans_MS 16", fill="DarkGoldenRod", text="Options")
		#===Solo===
		#Histoire
		self.canvas.create_rectangle(140, 260, 380, 340, width=4)
		self.canvas.create_text(260, 300, font="Comic_Sans_MS 40", fill="DarkGoldenRod", text="")#"Histoire")
		#Sans Fin
		self.canvas.create_rectangle(140, 460, 380, 540, width=4)
		self.canvas.create_text(260, 500, font="Comic_Sans_MS 40", fill="DarkGoldenRod", text="Démo")
		#===Duo===
		#Coopération
		self.canvas.create_rectangle(660, 260, 900, 340, width=4)
		self.canvas.create_text(780, 300, font="Comic_Sans_MS 40", fill="DarkGoldenRod", text="")#"Coop")
		#Versus
		self.canvas.create_rectangle(660, 460, 900, 540, width=4)
		self.canvas.create_text(780, 500, font="Comic_Sans_MS 40", fill="DarkGoldenRod", text="")#"Versus")
		#===Astuce===
		self.canvas.create_text(520, 620, font="Comic_Sans_MS 10", fill="NavajoWhite",
								text="Astuce: Vous pouvez à tout moment revenir au Menu en appuyant sur Echap.")
		
		#Evènement
		self.canvas.bind('<Button-1>', self.start)
		self.canvas.bind('<Button-3>', self.start)
		
	def start(self, event):
		#Si on clique sur un bouton:
		#	On supprime le Menu...
		#	...et on lance le mode de jeu choisis
		if (event.x >= 40) and (event.x <= 120):
			if (event.y >= 40) and (event.y <= 120):
				self.choix = 0
		elif (event.x >= 140) and (event.x <= 380):
			if (event.y >= 260) and (event.y <= 340):
				self.choix = 0
			elif (event.y >= 460) and (event.y <= 540):
				self.choix = Demo( self.fenetre, self.canvas, self.terrains, self.fps, self.relief )
		elif (event.x >= 660) and (event.x <= 900):
			if (event.y >= 260) and (event.y <= 340):
				self.choix = 0
			elif (event.y >= 460) and (event.y <= 540):
				self.choix = 0
				
		
	
	def fin2partie(self):
		return self.choix
	
	def recommencer(self):
		return 0

class Demo(Root):
	
	def __init__(self, fenetre, canvas, terrains, fps, relief):
		self.fenetre, self.canvas, self.terrains, self.fps, self.relief = fenetre, canvas, terrains, fps, relief
		self.terrain = terrains[1]
		#On crée les chars
		self.Joueur1 = Char(self.fenetre, self.canvas, 80, 80, 'Yellow', ('Joueur', 60, 20, 'White'), int(fps/10), relief)
		self.Joueur2 = Ennemi(self.fenetre, self.canvas, 920, 80, 'Red', ('0rdi', 980, 20, 'DarkRed'), int(fps/10), relief)
		self.Joueur3 = Ennemi(self.fenetre, self.canvas, 80, 520, 'LimeGreen', ('Ordi', 60, 620, 'DarkGreen'), int(fps/10), relief)
		self.Joueur4 = Ennemi(self.fenetre, self.canvas, 920, 520, 'DodgerBlue', ('Ordi', 980, 620, 'DarkBlue'), int(fps/10), relief)
		#On enregistre les Joueurs dans une liste
		self.Joueurs = [self.Joueur1, self.Joueur2, self.Joueur3, self.Joueur4]

		#Nombre de victoire et de défaites
		self.score = {"Défaite":0, "Victoire":0}
		
	def commencer(self):
		#Affichage élémentaire (terrain et chars)
		Root.afficher(self.canvas, self.terrain, self.Joueurs)
		#...et les scores
		printscore = self.canvas.create_text(500, 20, font="Time_New_Roman 15",
								   text="Victoire: "+str(self.score["Victoire"]))
		printscore = self.canvas.create_text(500, 620, font="Time_New_Roman 15",
								   text="Défaite: "+str(self.score["Défaite"]))
		#Evènements
		self.canvas.bind('<Motion>', self.Joueur1.mouvement_canon)
		self.canvas.bind('<Button-1>', self.Joueur1.tir)
		self.canvas.bind('<Button-3>', self.Joueur1.miner)
		self.fenetre.bind('<KeyPress>', self.Joueur1.change_dir)
		self.fenetre.bind('<KeyRelease>', self.Joueur1.stop_dir)
		#self.fenetre.bind('<Control_L>', Root.optionvit)
		#self.fenetre.bind('<Alt_L>', Root.optionrel)
	
	def fin2partie(self):
		return 0
	
	def recommencer(self):
		#Si le joueur est mort...
		if (self.Joueur1.mort == True):
			#Réinitialisation
			for var in range(len(self.Joueurs)):
				self.Joueurs[var].reborn()
			#Score défaite +1
			self.score["Défaite"] = self.score["Défaite"] + 1
			#Effacement de la surface (ligne du haut)
			self.canvas.create_rectangle(400, 600, 600, 640, width=0, fill='DarkGoldenRod')
			#Affichage
			printscore = self.canvas.create_text(500, 620, font="Time_New_Roman 15",
								   text="Défaite(s): "+str(self.score["Défaite"]))
		#...ou si tous les ennemis sont morts
		if (self.Joueur2.mort == True) and (self.Joueur3.mort == True) and (self.Joueur4.mort == True):
			#Réinitialisation
			for var in range(len(self.Joueurs)):
				self.Joueurs[var].reborn()
			#Score défaite +1
			self.score["Victoire"] = self.score["Victoire"] + 1
			#Effacement de la surface (ligne du haut)
			self.canvas.create_rectangle(400, 0, 600, 40, width=0, fill='DarkGoldenRod')
			#Affichage
			printscore = self.canvas.create_text(500, 20, font="Time_New_Roman 15",
								   text="Victoire(s): "+str(self.score["Victoire"]))
			

#On lance le jeu
racine = Root(Menu)
racine.boucle()
racine.fenetre.mainloop()



















