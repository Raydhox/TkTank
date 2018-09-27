#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#==================================TkTank==========================================================
#Par: UNG Harry, 2nde-5
#   TS4 (progression nulle en 1ère...)
#Descrition: Jeu de char utilisant tkinter. On dirige un char,
#   et il faut exterminer tous les autres chars. L'objectif finale est un jeu en réseau.
#   Et je rajouterai bien un mode histoire. Une meilleure IA serait aussi la bienvenue.
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
		terrain = main.terrain
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
			Joueurs = main.Joueurs
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
		if (self.dir[0] == True):
			#...Si il n'y a pas de collision avec une brique ou un char:
			if (terrain[math.floor((self.char_y-2)/40)][coordx] != '1')\
			and (terrain[math.floor((self.char_y-2)/40)][coordx2] != '1')\
			and (test_collision(8) is False):
				self.char_y -= 4
		if (self.dir[1] == True):
			#...Si il n'y a pas de collision avec une brique ou un char:
			if (terrain[coordy][math.floor((self.char_x-2)/40)] != '1')\
			and (terrain[coordy2][math.floor((self.char_x-2)/40)] != '1')\
			and (test_collision(4) is False):
				self.char_x -= 4
		if (self.dir[2] == True):
			#...Si il n'y a pas de collision avec une brique ou un char:
			if (terrain[math.floor((self.char_y+41)/40)][coordx] != '1')\
			and (terrain[math.floor((self.char_y+41)/40)][coordx2] != '1')\
			and (test_collision(2) is False):
				self.char_y += 4
		if (self.dir[3] == True):
			#...Si il n'y a pas de collision avec une brique ou un char:
			if (terrain[coordy][math.floor((self.char_x+41)/40)] != '1')\
			and (terrain[coordy2][math.floor((self.char_x+41)/40)] != '1')\
			and (test_collision(6) is False):
				self.char_x += 4
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
															   width=2, fill=self.couleur)  })
														   
		
	def tir(self, event):
		"""===Gère le tir.==="""
		self.mouvement_canon(event)
		self.obus(12, self.alpha, self.canon_x, self.canon_y)
	
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
		terrain = main.terrain
		fenetre = main.fenetre
		Joueurs = main.Joueurs
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
			#Ou si leur vitesse est nulle
			if self.munition[k]['vecteur_x'] + self.munition[k]['vecteur_y'] == 0:
				print("a")
				obus_del.append(k)
		#Les obus arretées sont supprimées
		for k in obus_del:
			count += 1
			kappa = k - count
			self.canvas.delete(fenetre, self.munition[kappa]['obus'])
			del self.munition[kappa]


	def mine(self, event):
		"""===Mine (=click droit)==="""
		terrain = main.terrain
		fenetre = main.fenetre
		Joueurs = main.Joueurs
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
		for var in range(len(Joueurs)):
			if (self.mine_x >= Joueurs[var].char_x) and (self.mine_x <= Joueurs[var].char_x+40)\
			and (self.mine_y >= Joueurs[var].char_y) and (self.mine_y <= Joueurs[var].char_y+40):
				pas2collision_char = False
		#...ou un mur, ou si une mine a déjà été crée
		if (terrain[coordy][coordx] != '1') and (terrain[coordy2][coordx2] != '1')\
		and (pas2collision_char) and (self.stock_mine):
			self.mine = self.canvas.create_oval(self.mine_x-12, self.mine_y-12, self.mine_x+12,
											 self.mine_y+12, width=6, fill=self.couleur)
			#Pour éviter de mettre plusieurs mines
			self.stock_mine = 0

	
	def minequiexplose(self):
		"""===Explosion de la mine==="""
		self.canvas.delete(main.fenetre, self.mine)
		#On peut de nouveau posé une mine
		self.stock_mine = 1
		self.timer = 5000
		#Création d'obus (dictionnaire stocké dans une liste)
		for k in range(69):
			self.obus(28, k*0.4, self.mine_x, self.mine_y)
			
			
	def ia(self, cible=(520, 320) ):
		self.terrain = main.terrain
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
		#Sinon, il y a collision, mais... (parce que c'est drôle):
		elif rng < 1:
			"""...déplacement aléatoire (1%)"""
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
		elif rng < 10:
			"""...déplacement "Sens Trigo": Haut |-> Droite |-> Bas |-> Gauche |-> Haut
			Mais on essaie de rester coller au mur (9%)"""
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
			self.obus(12, self.alpha, self.canon_x, self.canon_y)



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

	
	def reborn(self, x, y):
		"""===Renaissance du char: Réinitialisation des variables==="""
		self.mort = False
		#Les obus sont supprimés
		count = 0
		for k in range(len(self.munition)):
			count += 1
			kappa = k - count
			self.canvas.delete(main.fenetre, self.munition[kappa]['obus'])
			del self.munition[kappa]
		#La mine est également supprimés
		self.canvas.delete(main.fenetre, self.mine)
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
		self.canvas.coords(self.char, self.char_x, self.char_y, self.char_x+40, self.char_y+40)
		self.canvas.coords(self.pivot, self.char_x+32, self.char_y+32, self.char_x+8, self.char_y+8)
		self.canvas.coords(self.canon, self.char_x+20, self.char_y+20, self.canon_x, self.canon_y)
		self.canvas.coords(self.canon, self.char_x+20, self.char_y+20, self.canon_x, self.canon_y)


#On crée une classe char
class Main():

	def __init__(self):
		#On crée une fenêtre tkinter 'fenetre'
		self.fenetre = Tk()
		self.fenetre.title("TkTank.py")
		self.fenetre.geometry("+0+0")
		
		#Gestion du temps
		#(Soit ici, 25 images par secondes)
		self.fps = 40

		#On crée un Canvas 'jeu'
		self.canvas = Canvas(self.fenetre, width=1040, height=640, bg='NavajoWhite', cursor="cross")
		self.canvas.pack(side=LEFT)
		
		#Mis en place du terrain de jeu sous forme de liste 'terrain'
		self.terrain = []
		self.terrain.append("11111111111111111111111111")
		self.terrain.append("10000000000000001000000001")
		self.terrain.append("10000000000000001000000001")
		self.terrain.append("10000000010000000000000001")
		self.terrain.append("10000000010000000000000001")
		self.terrain.append("11111110010011111111111001")
		self.terrain.append("10000000010000000000000001")
		self.terrain.append("10000000010000000000000001")
		self.terrain.append("10000000000000001000000001")
		self.terrain.append("10000000000000001000000001")
		self.terrain.append("10011111111111001001111111")
		self.terrain.append("10000000000000001000000001")
		self.terrain.append("10000000000000001000000001")
		self.terrain.append("10000000010000000000000001")
		self.terrain.append("10000000010000000000000001")
		self.terrain.append("11111111111111111111111111")
		#Cimetière (n'est pas affiché)
		self.terrain.append("11111111111111111111111111")
		self.terrain.append("11111111111111111111111111")
		
##        #Mis en place du terrain de jeu sous forme de liste 'terrain'
##        self.terrain = []
##        self.terrain.append("11111111111111111111111111")
##        self.terrain.append("10000000010000000000000001")
##        self.terrain.append("10000000010000000000000001")
##        self.terrain.append("10000000000000001000000001")
##        self.terrain.append("10000000000000001000000001")
##        self.terrain.append("10011111111111001001111111")
##        self.terrain.append("10000000000000001000000001")
##        self.terrain.append("10000000000000001000000001")
##        self.terrain.append("10000000010000000000000001")
##        self.terrain.append("10000000010000000000000001")
##        self.terrain.append("11111110010011111111111001")
##        self.terrain.append("10000000010000000000000001")
##        self.terrain.append("10000000010000000000000001")
##        self.terrain.append("10000000000000001000000001")
##        self.terrain.append("10000000000000001000000001")
##        self.terrain.append("11111111111111111111111111")
##        #Cimetière (n'est pas affiché)
##        self.terrain.append("11111111111111111111111111")
##        self.terrain.append("11111111111111111111111111")

		#On crée les chars
		self.Joueur1 = Char(self.canvas, 80, 80, 'Yellow', ('Joueur', 60, 20, 'White'))
		self.Joueur2 = Char(self.canvas, 920, 80, 'Red', ('0rdi', 980, 20, 'DarkRed'))
		self.Joueur3 = Char(self.canvas, 80, 520, 'LimeGreen', ('Ordi', 60, 620, 'DarkGreen'))
		self.Joueur4 = Char(self.canvas, 920, 520, 'DodgerBlue', ('Ordi', 980, 620, 'DarkBlue'))
		#On enregistre les Joueurs dans une liste
		self.Joueurs = [self.Joueur1, self.Joueur2, self.Joueur3, self.Joueur4]

		#Nombre de victoire et de défaites
		self.score = {"Défaite":0, "Victoire":0}        

	def afficher(self):
		#On parcours la liste et en fonction des valeurs, on affiche une brique ou non
		for k1 in range(16):
			for k2 in range(26):
				if self.terrain[k1][k2] == '1':
					x = k2*40
					y = k1*40
					self.canvas.create_rectangle(x, y, x+40, y+40, width=0, fill='DarkGoldenRod')
		#On affiche les chars...
		for var in range(len(self.Joueurs)):
			self.Joueurs[var].afficher()
		#...et les scores
		printscore = self.canvas.create_text(500, 20, font="Time_New_Roman 15",
								   text="Victoire: "+str(self.score["Victoire"]))
		printscore = self.canvas.create_text(500, 620, font="Time_New_Roman 15",
								   text="Défaite: "+str(self.score["Défaite"]))
		#Evènements
		self.canvas.bind('<Motion>', self.Joueur1.mouvement_canon)
		self.canvas.bind('<Button-1>', self.Joueur1.tir)
		self.canvas.bind('<Button-3>', self.Joueur1.mine)
		self.fenetre.bind('<KeyPress>', self.Joueur1.change_dir)
		self.fenetre.bind('<KeyRelease>', self.Joueur1.stop_dir)
		#Et on lance la boucle
		self.boucle()
		#On lance le tout
		self.fenetre.mainloop()
				

	def fin2partie(self):
		#Si le joueur est mort...
		if (self.Joueur1.mort == True):
			#Réinitialisation
			self.Joueur1.reborn(80, 80)
			self.Joueur2.reborn(920, 80)
			self.Joueur3.reborn(80, 520)
			self.Joueur4.reborn(920, 520)
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
			self.Joueur1.reborn(80, 80)
			self.Joueur2.reborn(920, 80)
			self.Joueur3.reborn(80, 520)
			self.Joueur4.reborn(920, 520)
			#Score défaite +1
			self.score["Victoire"] = self.score["Victoire"] + 1
			#Effacement de la surface (ligne du haut)
			self.canvas.create_rectangle(400, 0, 600, 40, width=0, fill='DarkGoldenRod')
			#Affichage
			printscore = self.canvas.create_text(500, 20, font="Time_New_Roman 15",
								   text="Victoire(s): "+str(self.score["Victoire"]))
				
				
	def boucle(self):
		"""===Boucle principale du jeu.==="""
		#Mouvement des obus
		for var in range(len(self.Joueurs)):
			self.Joueurs[var].mouvement_obus()
		#Mine:
		for k in range(len(self.Joueurs)):
			if self.Joueurs[k].stock_mine == 0:
				self.Joueurs[k].timer -= self.fps
			if (self.Joueurs[k].stock_mine == 0) and (self.Joueurs[k].timer <= 0):
				self.Joueurs[k].minequiexplose()
		#Déplacement des robots + joueur
		for k in range(3):
			self.Joueurs[k+1].ia( (self.Joueur1.char_x, self.Joueur1.char_y) )
		for k in range(len(self.Joueurs)):
			self.Joueurs[k].mouvement_char()
		#Il y a-t-il fin de partie?
		self.fin2partie()
		#C'estune boucle, donc c'est re-ti-par!
		self.fenetre.after(self.fps, self.boucle)


#On lance le jeu
main = Main()
main.afficher()



































