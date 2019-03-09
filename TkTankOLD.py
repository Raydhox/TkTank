#!/usr/bin/env python
# -*- coding: utf-8 -*-

#==================================TkinTank==========================================================
#Par: UNG Harry
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

TILE = 32
TIME = 40
#================================LES PERSONNAGES================================#
#On crée une classe char
class Char():

	def __init__(self, x, y, couleur, nom, pv=16, vitesse=1, relief=1):
		"""Où 'canvas' le nom du Canvas,
'x' et 'y' les coordonnées du char,
nom, un tuple sous la forme:nom = ('nom', x, y, couleur)"""
		#Données qui seront initialisées plus tard (dans la fonction afficher)
		self.terrain = None
		self.Joueurs = None
		#Coordonnée du char
		self.char_x, self.char_x0 = x, x
		self.char_y, self.char_y0 = y, y
		#Coordonnée du canon
		self.alpha = 0
		self.canon_x = self.char_x + TILE/2 + TILE*math.sin(0)
		self.canon_y = self.char_y + TILE/2 - TILE*math.cos(0)
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
		self.vitesse = vitesse*TILE/8
		#PV du char
		self.pv, self.pv2base = pv, pv
		#Autre caractéristique ( couleur du char, nom, état (mort ou pas?), relief (taille des bordures) )
		self.couleur = couleur
		self.nom = nom
		self.mort = False
		self.relief = relief

	def born(self, root):
		"""Créer le char et affiche son nom. Permet d'initialiser les données liés à son environnement."""
		#Le "monde" dans lequel évolue le char (fenêtre, canvas, terrain, Joueurs)
		self.fenetre = root.fenetre
		self.canvas = root.canvas
		self.terrain = root.terrain
		self.Joueurs = root.Joueurs
		self.graveyard = (root.y+1)*TILE
		#Affichage
		self.id = self.canvas.create_text(self.nom[1], self.nom[2], font="Time_New_Roman 15",
										   text="%s: %d PV" %(self.nom[0], self.pv), fill=self.nom[3])
		self.char = self.canvas.create_rectangle(self.char_x, self.char_y, self.char_x+TILE,
												 self.char_y+TILE, width=self.relief, fill=self.couleur)
		self.roue1 = self.canvas.create_rectangle(self.char_x, self.char_y, self.char_x+5*self.relief,
											 self.char_y+TILE, fill="DarkGrey")
		self.roue2 = self.canvas.create_rectangle(self.char_x+TILE-5*self.relief, self.char_y, self.char_x+TILE,
											 self.char_y+TILE, fill="DarkGrey")
		self.canon = self.canvas.create_line(self.char_x+TILE/2, self.char_y+TILE/2, self.canon_x,
											 self.canon_y, width=TILE//5+2*self.relief)
		self.pivot = self.canvas.create_oval(self.char_x+0.5*TILE, self.char_y+0.5*TILE, self.char_x+TILE//5,
											 self.char_y+TILE//5, width=5*self.relief, fill=self.couleur)
		self.afficher()

	def afficher(self):
		"""Fonction qui affiche le char."""
		self.canvas.itemconfig(self.id, text="%s: %d PV" %(self.nom[0], self.pv) )
		self.canvas.coords(self.char, self.char_x, self.char_y, self.char_x+TILE, self.char_y+TILE)
		self.canvas.coords(self.canon, self.char_x+TILE/2, self.char_y+TILE/2, self.canon_x, self.canon_y)
		self.canvas.coords(self.pivot, self.char_x+0.25*TILE, self.char_y+0.25*TILE, self.char_x+0.75*TILE, self.char_y+0.75*TILE)
		if self.dir[1] or self.dir[3]:
			self.canvas.coords(self.roue1, self.char_x, self.char_y, self.char_x+TILE, self.char_y+5*self.relief)
			self.canvas.coords(self.roue2, self.char_x, self.char_y+TILE-5*self.relief, self.char_x+TILE, self.char_y+TILE)
		else:
			self.canvas.coords(self.roue1, self.char_x, self.char_y, self.char_x+5*self.relief, self.char_y+TILE)
			self.canvas.coords(self.roue2, self.char_x+TILE-5*self.relief, self.char_y, self.char_x+TILE, self.char_y+TILE)

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
		coordx = math.floor(self.char_x / TILE)
		coordy = math.floor(self.char_y / TILE)
		coordx2 = math.floor((self.char_x+TILE-1) / TILE)
		coordy2 = math.floor((self.char_y+TILE-1) / TILE)
		#Si il n'y a pas collision avec un char ou une mine...
		def test_collision(card):
			"""Voir clavier numérique (flèche)"""
			#Card = Cardinal: Où on va, (d'après pavé numérique)
			what = False
			for var in range(len(self.Joueurs)):
				if (self.char_x > self.Joueurs[var].char_x-TILE) and (self.char_x < self.Joueurs[var].char_x+TILE)\
				and (self.char_y-2 > self.Joueurs[var].char_y-TILE) and (self.char_y-2 < self.Joueurs[var].char_y+TILE)\
				and (self.couleur != self.Joueurs[var].couleur) and (card == 8):
					what = True
					break
				elif (self.char_x+1 > self.Joueurs[var].char_x-TILE) and (self.char_x+1 < self.Joueurs[var].char_x+TILE)\
				and (self.char_y > self.Joueurs[var].char_y-TILE) and (self.char_y < self.Joueurs[var].char_y+TILE)\
				and (self.couleur != self.Joueurs[var].couleur) and (card == 6):
					what = True
					break
				elif (self.char_x-2 > self.Joueurs[var].char_x-TILE) and (self.char_x-2 < self.Joueurs[var].char_x+TILE)\
				and (self.char_y > self.Joueurs[var].char_y-TILE) and (self.char_y < self.Joueurs[var].char_y+TILE)\
				and (self.couleur != self.Joueurs[var].couleur) and (card == 4):
					what = True
					break
				elif (self.char_x > self.Joueurs[var].char_x-TILE) and (self.char_x < self.Joueurs[var].char_x+TILE)\
				and (self.char_y+1 > self.Joueurs[var].char_y-TILE) and (self.char_y+1 < self.Joueurs[var].char_y+TILE)\
				and (self.couleur != self.Joueurs[var].couleur) and (card == 2):
					what = True
					break
			return what
		#...on se déplace...
		if (self.dir[0] == True):
			#...Si il n'y a pas de collision avec une brique ou un char:
			if (self.terrain[math.floor((self.char_y-self.vitesse)/TILE)][coordx] != '1')\
			and (self.terrain[math.floor((self.char_y-self.vitesse)/TILE)][coordx2] != '1')\
			and (test_collision(8) is False):
				self.char_y -= self.vitesse
		if (self.dir[1] == True):
			#...Si il n'y a pas de collision avec une brique ou un char:
			if (self.terrain[coordy][math.floor((self.char_x-self.vitesse)/TILE)] != '1')\
			and (self.terrain[coordy2][math.floor((self.char_x-self.vitesse)/TILE)] != '1')\
			and (test_collision(4) is False):
				self.char_x -= self.vitesse
		if (self.dir[2] == True):
			#...Si il n'y a pas de collision avec une brique ou un char:
			if (self.terrain[math.floor((self.char_y+TILE-1+self.vitesse)/TILE)][coordx] != '1')\
			and (self.terrain[math.floor((self.char_y+TILE-1+self.vitesse)/TILE)][coordx2] != '1')\
			and (test_collision(2) is False):
				self.char_y += self.vitesse
		if (self.dir[3] == True):
			#...Si il n'y a pas de collision avec une brique ou un char:
			if (self.terrain[coordy][math.floor((self.char_x+TILE-1+self.vitesse)/TILE)] != '1')\
			and (self.terrain[coordy2][math.floor((self.char_x+TILE-1+self.vitesse)/TILE)] != '1')\
			and (test_collision(6) is False):
				self.char_x += self.vitesse
		#Calul des nouvelles positions du canon
		self.canon_x = self.char_x + TILE/2 + 0.8*TILE*math.cos(self.alpha)
		self.canon_y = self.char_y + TILE/2 - 0.8*TILE*math.sin(self.alpha)
		#Affichage
		self.afficher()

	def obus(self, vitesse, angle, coord_x, coord_y):
		"""Crée les obus sous forme de dictionnaire stocké dans une liste."""
		self.munition.append({	'vecteur_x':vitesse*math.cos(angle), 'vecteur_y':-vitesse*math.sin(angle),'obus_x':coord_x, 'obus_y':coord_y,
                                        'obus':self.canvas.create_oval(coord_x-3, coord_y-3, coord_x+3, coord_y+3, width=self.relief, fill=self.couleur)  })


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
		self.canon_x = self.char_x + TILE/2 + 0.8*TILE*math.cos(alpha)
		self.canon_y = self.char_y + TILE/2 - 0.8*TILE*math.sin(alpha)
		#Affichage
		#self.canvas.coords(self.canon, self.char_x+20, self.char_y+20, self.canon_x, self.canon_y)

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
			coordx = int(self.munition[k]['obus_x']/TILE)
			coordy = int(self.munition[k]['obus_y']/TILE)
			#Si il y a collision avec un mur (brique)
			if (self.terrain[coordy][coordx] == '1'):
				obus_del.append(k)
			#Si il y a collision avec un char...
			for var in range(len(self.Joueurs)):
				if (self.munition[k]['obus_x'] >= self.Joueurs[var].char_x)\
				and (self.munition[k]['obus_x'] <= self.Joueurs[var].char_x+TILE)\
				and (self.munition[k]['obus_y'] >= self.Joueurs[var].char_y)\
				and (self.munition[k]['obus_y'] <= self.Joueurs[var].char_y+TILE):
					obus_del.append(k)
					self.Joueurs[var].rip()
		#Les obus arretées sont supprimées
		for k in obus_del:
			count += 1
			self.canvas.delete(self.fenetre, self.munition[k-count]['obus'])
			del self.munition[k-count]


	def miner(self, event):
		"""===Mine (=click droit)==="""
		#On crée la mine (un cercle)...
		self.mine_x = self.char_x + 20 + 32*math.sin(self.alpha+math.pi*1.5)
		self.mine_y = self.char_y + 20 + 32*math.cos(self.alpha+math.pi*1.5)
##		#...si ses extrémités...
##		coordx = int((self.mine_x-12)/40)
##		coordy = int((self.mine_y-12)/40)
##		coordx2 = int((self.mine_x+12)/40)
##		coordy2 = int((self.mine_y+12)/40)
##		#...ne cogne pas un char...
##		pas2collision_char = True
##		for var in range(len(self.Joueurs)):
##			if (self.mine_x >= self.Joueurs[var].char_x) and (self.mine_x <= self.Joueurs[var].char_x+TILE)\
##			and (self.mine_y >= self.Joueurs[var].char_y) and (self.mine_y <= self.Joueurs[var].char_y+TILE):
##				pas2collision_char = False
##		#...ou un mur, ou si une mine a déjà été crée
##		if (self.terrain[coordy][coordx] != '1') and (self.terrain[coordy2][coordx2] != '1')\
##		and (pas2collision_char) and (self.stock_mine):
		self.mine = self.canvas.create_oval(self.mine_x-12, self.mine_y-12,
                                                self.mine_x+12, self.mine_y+12, width=2+2*self.relief, fill=self.couleur)
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
		self.pv -= 1
		if self.pv <= 0:
			self.mort = True
                        #Nouvelles positions du char
			self.char_x = TILE
			self.char_y = self.graveyard


	def reborn(self, x, y):
		"""===Renaissance du char: Réinitialisation des variables==="""
		self.mort = False
		self.pv = self.pv2base
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


class Ennemi(Char):

	def __init__(self, x, y, couleur, nom, pv=16):
		#Classe qui hérite de le classe Char
		Char.__init__(self, x, y, couleur, nom, pv)

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

	def ia(self, cible ):
		#Position relative, correspondant au "coordonées des cases" de TILE*TILE...
		coordx = int(self.char_x/TILE)
		coordy = int(self.char_y/TILE)
		coordx2 = int((self.char_x+TILE-1)/TILE)
		coordy2 = int((self.char_y+TILE-1)/TILE)
		#...après déplacement vers le haut / bas
		coordyUp = int((self.char_y-self.vitesse)/TILE)
		coordyDown = int((self.char_y+TILE+self.vitesse)/TILE)
		#...après déplacement vers la gauche / droite
		coordxLeft = int((self.char_x-self.vitesse)/TILE)
		coordxRight = int((self.char_x+TILE+self.vitesse)/TILE)

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
			self.canon_x = self.char_x + TILE/2 + 0.8*TILE*math.cos(self.alpha)
			self.canon_y = self.char_y + TILE/2 - 0.8*TILE*math.sin(self.alpha)
			#Affichage
			#self.canvas.coords(self.canon, self.char_x+20, self.char_y+20, self.canon_x, self.canon_y)
			self.obus(3, self.alpha, self.canon_x, self.canon_y)


#================================LE JEU================================#

#On crée une classe char
class Main():

    def __init__(self):
        #On crée une fenêtre tkinter 'fenetre'
        self.fenetre = Tk()
        self.fenetre.title("TkTank.py")
        self.fenetre.geometry("+0+0")
        
        #Mis en place du terrain de jeu sous forme de liste 'terrain'
        self.terrain = []
        self.terrain.append("1111111111111111111111111111111111")
        for k in range(19):
            self.terrain.append("1000000000000000000000000000000001")
        self.terrain.append("1111111111111111111111111111111111")
        #Cimetière (n'est pas affiché)
        for k in range(3):
            self.terrain.append("1111111111111111111111111111111111")

        self.x, self.y = ( len(self.terrain[0]), len(self.terrain)-3 )

        try:
            with open("terrain.txt", "r") as f:
                self.terrain = []
                for k in range(self.y):
                    self.terrain.append(f.readline()[:self.x])
                #Cimetière (n'est pas affiché)
                for k in range(3):
                    self.terrain.append("1111111111111111111111111111111111")
        except:
            pass

        #On crée un Canvas 'jeu'
        self.canvas = Canvas(self.fenetre, width=self.x*TILE, height=self.y*TILE, bg='NavajoWhite', cursor="cross")
        self.canvas.pack(side=TOP)

        #On crée les chars
        self.Joueur1 = Char(80, 80, 'Yellow', ('Joueur', 3*TILE, TILE/2, 'White'))
        self.Joueur2 = Ennemi(920, 80, 'Red', ('0rdi', (self.x-3)*TILE, TILE/2, 'DarkRed'))
        self.Joueur3 = Ennemi(80, 520, 'LimeGreen', ('Ordi', 3*TILE, (self.y-0.5)*TILE, 'DarkGreen'))
        self.Joueur4 = Ennemi(920, 520, 'DodgerBlue', ('Ordi', (self.x-3)*TILE, (self.y-0.5)*TILE, 'DarkBlue'))
        #On enregistre les Joueurs dans une liste
        self.Joueurs = [self.Joueur1, self.Joueur2, self.Joueur3, self.Joueur4]

        #Nombre de victoire et de défaites
        self.score = {"Défaite":0, "Victoire":0}        

    def afficher(self):
        #On parcours la liste et en fonction des valeurs, on affiche une brique ou non
        for i in range(self.y):
            for j in range(self.x):
                if self.terrain[i][j] == '1':
                    x = j*TILE
                    y = i*TILE
                    self.canvas.create_rectangle(x, y, x+TILE, y+TILE, width=0, fill='DarkGoldenRod')
        #On affiche les chars...
        for var in range(len(self.Joueurs)):
            self.Joueurs[var].born(self)
        #...et les scores
        printscore = self.canvas.create_text(self.x*TILE/2, (self.y-0.5)*TILE, font="Time_New_Roman 15",
                                   text="Défaite(s): "+str(self.score["Défaite"]))
        printscore = self.canvas.create_text(self.x*TILE/2, TILE/2, font="Time_New_Roman 15",
                                   text="Victoire(s): "+str(self.score["Victoire"]))
        #Evènements
        self.canvas.bind('<Motion>', self.Joueur1.mouvement_canon)
        self.canvas.bind('<Button-1>', self.Joueur1.tir)
        self.canvas.bind('<Button-3>', self.Joueur1.miner)
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
            self.canvas.create_rectangle(self.x*TILE//4, (self.y-1)*TILE, self.x*TILE*3//4, self.y*TILE, width=0, fill='DarkGoldenRod')
            #Affichage
            printscore = self.canvas.create_text(self.x*TILE/2, (self.y-0.5)*TILE, font="Time_New_Roman 15",
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
            self.canvas.create_rectangle(self.x*TILE//4, 0, self.x*TILE*3//4, TILE, width=0, fill='DarkGoldenRod')
            #Affichage
            printscore = self.canvas.create_text(self.x*TILE/2, TILE/2, font="Time_New_Roman 15",
                                   text="Victoire(s): "+str(self.score["Victoire"]))
                
                
    def boucle(self):
        """===Boucle principale du jeu.==="""
        #Mouvement des obus
        for var in range(len(self.Joueurs)):
            self.Joueurs[var].mouvement_obus()
        #Mine:
        for k in range(len(self.Joueurs)):
            if self.Joueurs[k].stock_mine == 0:
                self.Joueurs[k].timer -= TIME
            if (self.Joueurs[k].stock_mine == 0) and (self.Joueurs[k].timer == 0):
                self.Joueurs[k].minequiexplose()
        #Déplacement des robots + joueur
        for k in range(3):
            self.Joueurs[k+1].ia( (self.Joueur1.char_x, self.Joueur1.char_y) )
        for k in range(len(self.Joueurs)):
            self.Joueurs[k].mouvement_char()
        #Il y a-t-il fin de partie?
        self.fin2partie()
        #C'estune boucle, donc c'est re-ti-par!
        self.fenetre.after(TIME, self.boucle)


#On lance le jeu
racine = Main()
racine.afficher()
racine.boucle()
racine.fenetre.mainloop()



















