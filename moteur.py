#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#==================================TkTank==========================================================
#Par: UNG Harry
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

#MODUlES
from tkinter import *
import math, random

#VARIABLES
TILE = 32
FONT = "Time_New_Roman"
FPS = 60
TIME = 1000 // FPS

#================================CHARS================================#
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
        self.timer, self.timer0 = 3000, 3000
        #Pour les munitions
        self.munition = []
        #Pour le mouvement
        self.dir = [False, False, False, False]
        self.vitesse = vitesse * 3*TILE / FPS
        #PV du char
        self.pv, self.pv2base = pv, pv
        #Autre caractéristique ( couleur du char, nom, état (mort ou pas?), relief (taille des bordures) )
        self.couleur = couleur
        self.nom = nom
        self.mort = False
        self.relief = relief

    def born(self, root, mission):
        """Créer le char et affiche son nom. Permet d'initialiser les données liés à son environnement."""
        #Le "monde" dans lequel évolue le char (fenêtre, canvas, terrain, Joueurs)
        self.fenetre = root.fenetre
        self.canvas = root.canvas
        self.terrain = mission.terrain
        self.Joueurs = mission.Joueurs
        self.graveyard = (mission.y+1)*TILE
        #Affichage
        #Nom
        self.id = self.canvas.create_text(self.nom[1], self.nom[2], font="{} {}".format(FONT, TILE//2),
                                           text="%s: %d PV" %(self.nom[0], self.pv), fill=self.nom[3])
        #Le "corps" du char
        self.char = self.canvas.create_rectangle(self.char_x, self.char_y, self.char_x+TILE,
                                                 self.char_y+TILE, width=self.relief, fill=self.couleur)
        #Les roues
        self.roue1 = self.canvas.create_rectangle(self.char_x, self.char_y, self.char_x+TILE//4,
                                             self.char_y+TILE, fill="DarkGrey")
        self.roue2 = self.canvas.create_rectangle(self.char_x+TILE-5*self.relief, self.char_y, self.char_x+TILE,
                                             self.char_y+TILE, fill="DarkGrey")
        #Le canon
        self.canon = self.canvas.create_line(self.char_x+TILE/2, self.char_y+TILE/2, self.canon_x,
                                             self.canon_y, width=TILE//5+2*self.relief)
        #Le pivot (cache une partie du canon, ce qui est voulu)
        self.pivot = self.canvas.create_oval(self.char_x+0.5*TILE, self.char_y+0.5*TILE, self.char_x+TILE//5,
                                             self.char_y+TILE//5, width=5*self.relief, fill=self.couleur)
        self.afficher()

    def afficher(self):
        """Fonction qui affiche le char."""
        #Nom
        self.canvas.itemconfig(self.id, text="%s: %d PV" %(self.nom[0], self.pv) )
        #Le "corps" du char
        self.canvas.coords(self.char, self.char_x, self.char_y, self.char_x+TILE, self.char_y+TILE)
        #Le canon
        self.canvas.coords(self.canon, self.char_x+TILE/2, self.char_y+TILE/2, self.canon_x, self.canon_y)
        #Le pivot
        self.canvas.coords(self.pivot, self.char_x+0.25*TILE, self.char_y+0.25*TILE, self.char_x+0.75*TILE, self.char_y+0.75*TILE)
        #Les roues
        if self.dir[1] or self.dir[3]:
            self.canvas.coords(self.roue1, self.char_x, self.char_y, self.char_x+TILE, self.char_y+TILE//6)
            self.canvas.coords(self.roue2, self.char_x, self.char_y+TILE-TILE//6, self.char_x+TILE, self.char_y+TILE)
        else:
            self.canvas.coords(self.roue1, self.char_x, self.char_y, self.char_x+TILE//6, self.char_y+TILE)
            self.canvas.coords(self.roue2, self.char_x+TILE-TILE//6, self.char_y, self.char_x+TILE, self.char_y+TILE)

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
        if (event.keysym == 'Up') or (event.keysym.lower() == 'z') or (event.keysym.lower() == 'w'):
            self.dir[0] = True
        elif (event.keysym == 'Left') or (event.keysym.lower() == 'q') or (event.keysym.lower() == 'a'):
            self.dir[1] = True
        elif (event.keysym == 'Down') or (event.keysym.lower() == 's'):
            self.dir[2] = True
        elif (event.keysym == 'Right') or (event.keysym.lower() == 'd'):
            self.dir[3] = True

    def stop_dir(self, event):
        #Désactive la direction
        if (event.keysym == 'Up') or (event.keysym.lower() == 'z') or (event.keysym.lower() == 'w'):
            self.dir[0] = False
        elif (event.keysym == 'Left') or (event.keysym.lower() == 'q') or (event.keysym.lower() == 'a'):
            self.dir[1] = False
        elif (event.keysym == 'Down') or (event.keysym.lower() == 's'):
            self.dir[2] = False
        elif (event.keysym == 'Right') or (event.keysym.lower() == 'd'):
            self.dir[3] = False


    def mouvement_char(self):
        """===Mouvement du char==="""
        #Variables globales
        collision = False
        #Position relative, correspondant au "coordonées des cases" de taille TILE*TILE
        #Côté haut-gauche du char
        coordx = math.floor(self.char_x / TILE)
        coordy = math.floor(self.char_y / TILE)
        #Côté bas-droite
        coordx2 = math.floor((self.char_x+TILE-1) / TILE)
        coordy2 = math.floor((self.char_y+TILE-1) / TILE)
        #Si il n'y a pas collision avec un char...
        def test_collision(card):
            """Voir clavier numérique (flèche)"""
            #Card = Cardinal: Où on va, (d'après pavé numérique)
            for var in range(len(self.Joueurs)):
                if (self.char_x > self.Joueurs[var].char_x-TILE) and (self.char_x < self.Joueurs[var].char_x+TILE)\
                and (self.char_y-self.vitesse > self.Joueurs[var].char_y-TILE) and (self.char_y-self.vitesse < self.Joueurs[var].char_y+TILE)\
                and (self.couleur != self.Joueurs[var].couleur) and (card == "Up"):
                    return True
                elif (self.char_x+self.vitesse > self.Joueurs[var].char_x-TILE) and (self.char_x+self.vitesse < self.Joueurs[var].char_x+TILE)\
                and (self.char_y > self.Joueurs[var].char_y-TILE) and (self.char_y < self.Joueurs[var].char_y+TILE)\
                and (self.couleur != self.Joueurs[var].couleur) and (card == "Right"):
                    return True
                elif (self.char_x-2 > self.Joueurs[var].char_x-TILE) and (self.char_x-+self.vitesse < self.Joueurs[var].char_x+TILE)\
                and (self.char_y > self.Joueurs[var].char_y-TILE) and (self.char_y < self.Joueurs[var].char_y+TILE)\
                and (self.couleur != self.Joueurs[var].couleur) and (card == "Left"):
                    return True
                elif (self.char_x > self.Joueurs[var].char_x-TILE) and (self.char_x < self.Joueurs[var].char_x+TILE)\
                and (self.char_y+self.vitesse > self.Joueurs[var].char_y-TILE) and (self.char_y+self.vitesse < self.Joueurs[var].char_y+TILE)\
                and (self.couleur != self.Joueurs[var].couleur) and (card == "Down"):
                    return True
            return False
        #...on se déplace...
        if (self.dir[0] == True):
            #...Si il n'y a pas de collision avec une brique ou un char:
            if (self.terrain[math.floor((self.char_y-self.vitesse)/TILE)][coordx] != '1')\
            and (self.terrain[math.floor((self.char_y-self.vitesse)/TILE)][coordx2] != '1')\
            and (test_collision("Up") is False):
                self.char_y -= self.vitesse
        if (self.dir[1] == True):
            #...Si il n'y a pas de collision avec une brique ou un char:
            if (self.terrain[coordy][math.floor((self.char_x-self.vitesse)/TILE)] != '1')\
            and (self.terrain[coordy2][math.floor((self.char_x-self.vitesse)/TILE)] != '1')\
            and (test_collision("Left") is False):
                self.char_x -= self.vitesse
        if (self.dir[2] == True):
            #...Si il n'y a pas de collision avec une brique ou un char:
            if (self.terrain[math.floor((self.char_y+TILE-1+self.vitesse)/TILE)][coordx] != '1')\
            and (self.terrain[math.floor((self.char_y+TILE-1+self.vitesse)/TILE)][coordx2] != '1')\
            and (test_collision("Down") is False):
                self.char_y += self.vitesse
        if (self.dir[3] == True):
            #...Si il n'y a pas de collision avec une brique ou un char:
            if (self.terrain[coordy][math.floor((self.char_x+TILE-1+self.vitesse)/TILE)] != '1')\
            and (self.terrain[coordy2][math.floor((self.char_x+TILE-1+self.vitesse)/TILE)] != '1')\
            and (test_collision("Right") is False):
                self.char_x += self.vitesse
        #Calul des nouvelles positions du canon
        self.canon_x = self.char_x + TILE/2 + 0.8*TILE*math.cos(self.alpha)
        self.canon_y = self.char_y + TILE/2 - 0.8*TILE*math.sin(self.alpha)
        #Affichage
        self.afficher()

    def obus(self, vitesse, angle, coord_x, coord_y):
        """Crée les obus sous forme de dictionnaire stocké dans une liste."""
        self.munition.append({  'vecteur_x':vitesse*math.cos(angle), 'vecteur_y':-vitesse*math.sin(angle),'obus_x':coord_x, 'obus_y':coord_y,
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
        #Si il n'y a plus de mine en stock : on ne fait rien.
        if self.stock_mine == 0 :
            return
        #Calcul des coordonnées de la mine.
        self.mine_x = self.char_x + 20 + 32*math.sin(self.alpha+math.pi*1.5)
        self.mine_y = self.char_y + 20 + 32*math.cos(self.alpha+math.pi*1.5)
        #On crée la mine (un cercle avec un timer).
        rayon_mine = 8
        self.mine = self.canvas.create_oval(self.mine_x-rayon_mine, self.mine_y-rayon_mine, self.mine_x+rayon_mine, self.mine_y+rayon_mine, width=2*self.relief, fill=self.couleur)
        self.compte_a_rebours  = self.canvas.create_text(self.mine_x, self.mine_y, font="Time_New_Roman {}".format(rayon_mine), text=str(self.timer//1000) )
        #Pour éviter de mettre plusieurs mines.
        self.stock_mine = 0

    def time_mine(self):
        """Rèduit le compteur de la mine."""
        if self.stock_mine == 0:
            self.timer -= TIME
            self.canvas.itemconfig(self.compte_a_rebours, text=str(str(1 + self.timer//1000)))
        if self.timer <= 0:
            self.minequiexplose()

    def minequiexplose(self):
        """===Explosion de la mine==="""
        self.canvas.delete(self.fenetre, self.mine)
        self.canvas.delete(self.fenetre, self.compte_a_rebours)
        #On peut de nouveau posé une mine
        self.stock_mine = 1
        self.timer = self.timer0
        #Création d'obus (dictionnaire stocké dans une liste)
        for k in range(100):
            self.obus(6, k*0.4, self.mine_x, self.mine_y)


    def rip(self):
        """===Mort du char (déplacement hors de l'écran pour ne pas créer d'erreur dû au évènement).==="""
        self.pv -= 1
        if self.pv <= 0:
            self.mort = True
            #Nouvelles positions du char
            self.char_x = TILE
            self.char_y = self.graveyard


    def reborn(self):
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
        if self.stock_mine == 0:
            self.canvas.delete(self.fenetre, self.mine)
            self.canvas.delete(self.fenetre, self.compte_a_rebours)
        self.stock_mine = 1
        self.timer = self.timer0
        #Nouvelles positions du char
        self.char_x = self.char_x0
        self.char_y = self.char_y0
        #Calcul des nouvelles positions du canon
        self.alpha = math.pi/2
        self.canon_x = self.char_x + 20 + 32*math.cos(self.alpha)
        self.canon_y = self.char_y + 20 - 32*math.sin(self.alpha)


class Ennemi(Char):

    def __init__(self, x, y, couleur, nom, cible_mouvement=None, cible_tir=None, pv=16, tirs_par_seconde=4):
        #Classe qui hérite de le classe Char
        Char.__init__(self, x, y, couleur, nom, pv)
        #Les mines des Ennemis explosent au bout de 5 secondes 
        self.timer0 = 5000
        self.tirs_par_seconde = tirs_par_seconde
        #Définit la cible que le bot cherche à tuer et à rejoindre.
        self.cible_mouvement = cible_mouvement
        self.cible_tir = cible_tir

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
            
    def position_cible(self, cible):
        """Récupère les coordonnées de la cible sous forme de tuple."""
        if type(cible) == tuple:
            return cible
        elif cible == None :
            return None
        #Sinon, la cible est un char :
        return (cible.char_x, cible.char_y)

    def ia_mouvement(self, cible_mouvement):
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
        if rng < 10:
            #Déplacement dans une direction aléatoire
            self.dirobot(['Up', 'Down', 'Left', 'Right'][random.randrange(0, 4)])
        #Sinon il n'y a pas de collision avec une brique (Haut, Bas, Gauche, Droite):
        elif (self.terrain[coordyUp][coordx] != '1') and (self.terrain[coordyUp][coordx2] != '1')\
        and (self.terrain[coordyDown][coordx] != '1') and (self.terrain[coordyDown][coordx2] != '1')\
        and (self.terrain[coordy][coordxLeft] != '1') and (self.terrain[coordy2][coordxLeft] != '1')\
        and (self.terrain[coordy][coordxRight] != '1') and (self.terrain[coordy2][coordxRight] != '1'):
            """=====Déplacement qui se rapproche de la cible====="""
            #Si le centre est au-dessus du robot, alors il va en haut
            if cible_mouvement[1] < self.char_y:
                self.dirobot('Up')
            #Sinon, il descend
            elif cible_mouvement[1] > self.char_y:
                self.dirobot('Down')
            #Si le centre est à gauche du robot, alors il va à gauche
            if cible_mouvement[0] < self.char_x:
                self.dirobot('Left')
            #Sinon, il va à droite
            elif cible_mouvement[0] > self.char_x:
                self.dirobot('Right')
        else:
            #Longe le mur selon un déplacement "Sens Trigo": Haut |-> Droite |-> Bas |-> Gauche |-> Haut
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

    def ia_tir(self, cible_tir, tir_force=False):
        #===Tir dirigé vers la cible à cadence aléatoire (%)==
        hasard = random.randrange(0, FPS)
        if hasard > self.tirs_par_seconde and not tir_force:
            return
        #Tir dirigé contre le Joueur
        #Trigo et Pythagore
        adj = cible_tir[0] - self.char_x
        hypo = math.sqrt((cible_tir[0] - self.char_x)**2 + (cible_tir[1] - self.char_y)**2)
        if hypo == 0:
            hypo = 0.01
        self.alpha = math.acos(adj/hypo)
        #Angle obtus ou angle aigus?
        if cible_tir[1] > self.char_y:
            self.alpha = - self.alpha
        #===Mouvement canon===
        #Calul des nouvelles positions du canon
        self.canon_x = self.char_x + TILE/2 + 0.8*TILE*math.cos(self.alpha)
        self.canon_y = self.char_y + TILE/2 - 0.8*TILE*math.sin(self.alpha)
        #Affichage
        #self.canvas.coords(self.canon, self.char_x+20, self.char_y+20, self.canon_x, self.canon_y)
        self.obus(3, self.alpha, self.canon_x, self.canon_y)

    def ia(self):
        cible_mouvement = self.position_cible(self.cible_mouvement)
        cible_tir = self.position_cible(self.cible_tir)

        if (cible_mouvement != None):
            self.ia_mouvement(cible_mouvement)
        if (cible_tir != None):
            self.ia_tir(cible_tir)


        


#================================LE JEU================================#

#On crée une classe char
class Main():

    def __init__(self, mission):
        #On crée une fenêtre tkinter 'fenetre'
        self.fenetre = Tk()
        self.fenetre.title("TkTank.py")
        #self.fenetre.geometry("+0+0")

        #Nombres de cases.
        self.x, self.y = (34, 21)

        #On crée un Canvas 'jeu'
        self.canvas = Canvas(self.fenetre, width=self.x*TILE, height=self.y*TILE, bg='NavajoWhite', cursor="cross")
        self.canvas.pack(side=TOP)

        #Mission : contient les données d'une partie.
        self.mission = mission

        #On lance le tout
        self.afficher()
        self.boucle()
        self.fenetre.mainloop()

    def afficher(self):
        #On parcours la liste et en fonction des valeurs, on affiche une brique ou non
        for i in range(self.y):
            for j in range(self.x):
                if self.mission.terrain[i][j] == '1':
                    x = j*TILE
                    y = i*TILE
                    self.canvas.create_rectangle(x, y, x+TILE, y+TILE, width=0, fill='DarkGoldenRod')
                    #Effet 3D
                    self.canvas.create_polygon((x, y+TILE, x+6, y+TILE+6, x+TILE+6, y+TILE+6, x+TILE, y+TILE), width=0, fill='SaddleBrown')
                    self.canvas.create_polygon((x+TILE, y, x+TILE+6, y+6, x+TILE+6, y+TILE+6, x+TILE, y+TILE), width=0, fill='SaddleBrown')
        #On affiche les chars...
        for var in range(len(self.mission.Joueurs)):
            self.mission.Joueurs[var].born(self, self.mission)
        #Afichage spécifique au niveau
        self.mission.affichage_specifique(self.canvas)
        #Evènements
        for event in self.mission.events:
            self.fenetre.bind(event[0], event[1])         

    def changement_mission(self):
        for event in self.mission.events:
            self.fenetre.unbind(event[0])
        self.mission = self.mission.mission_suivante
        self.canvas.delete("all")
        self.afficher()
                
    def boucle(self):
        """===Boucle principale du jeu.==="""
        if self.mission.boucle_active:
            #Mouvement des obus
            for var in range(len(self.mission.Joueurs)):
                self.mission.Joueurs[var].mouvement_obus()
            #Mine:
            for k in range(len(self.mission.Joueurs)):
                self.mission.Joueurs[k].time_mine()
            #Déplacement des robots + joueur
            for k in range(self.mission.nombre_ia):
                self.mission.Joueurs[-k-1].ia()
                #pass
        for k in range(len(self.mission.Joueurs)):
            self.mission.Joueurs[k].mouvement_char()
        #Il y a-t-il fin de partie?
        if self.mission.fin2partie(self.canvas):
            self.changement_mission()
        #C'est une boucle, donc c'est re-ti-par!
        self.fenetre.after(TIME, self.boucle)


#Exemple de la structure d'une mission.
class Mission:

    def __init__(self) :
        #Mis en place du terrain de jeu sous forme de liste 'terrain'
        self.terrain = ["1111111111111111111111111111111111",
                        "1000000000000000000000000000000001",
                        "1000000000000000000000000000000001",
                        "1000000000000000000000000000000001",
                        "1000000000000000000000000000000001",
                        "1000000000000000000000000000000001",
                        "1000000000000000000000000000000001",
                        "1000000000000000000000000000000001",
                        "1000000000000000000000000000000001",
                        "1000000000000000000000000000000001",
                        "1000000000000000000000000000000001",
                        "1000000000000000000000000000000001",
                        "1000000000000000000000000000000001",
                        "1000000000000000000000000000000001",
                        "1000000000000000000000000000000001",
                        "1000000000000000000000000000000001",
                        "1000000000000000000000000000000001",
                        "1000000000000000000000000000000001",
                        "1000000000000000000000000000000001",
                        "1000000000000000000000000000000001",
                        "1111111111111111111111111111111111"]
        #Cimetière (n'est pas affiché)
        for k in range(3):
            self.terrain.append("1111111111111111111111111111111111")        

        #Nombre de cases
        self.x, self.y = (34, 21)

        #On enregistre les Joueurs dans une liste
        self.Joueurs = []
        self.nombre_ia = 0

        #Évents
        self.events = ()
        
        self.mission_suivante = None
        self.boucle_active = True


    def affichage_specifique(self, canvas):
        pass

    def fin2partie(self, canvas):
        return False
        

#Exemple de la structure d'une mission.
class Demo(Mission):

    def __init__(self) :
        #Mis en place du terrain de jeu sous forme de liste 'terrain'
        Mission.__init__(self)
        
        #Mis en place du terrain de jeu sous forme de liste 'terrain'
        self.terrain = ["1111111111111111111111111111111111",
                        "1000000000000000000001000000000001",
                        "1000000000000000000001000000000001",
                        "1000000000000000000001000000000001",
                        "1000000000001000000000000000000001",
                        "1000000000001000000000000000000001",
                        "1000000000001000000000000000000001",
                        "1111111110001001111111100111110001",
                        "1000000000001000000000000000000001",
                        "1000000000001000000000000000000001",
                        "1000000000000000000000000000000001",
                        "1000000000000000000001000000000001",
                        "1000000000000000000001000000000001",
                        "1000111110011111110001000111111111",
                        "1000000000000000000001000000000001",
                        "1000000000000000000001000000000001",
                        "1000000000000000000001000000000001",
                        "1000000000001000000000000000000001",
                        "1000000000001000000000000000000001",
                        "1000000000001000000000000000000001",
                        "1111111111111111111111111111111111"]
        #Cimetière (n'est pas affiché)
        for k in range(3):
            self.terrain.append("1111111111111111111111111111111111")

        #On crée les chars
        self.Joueur1 = Char(2*TILE, 2*TILE, 'Yellow', ('Joueur', 3*TILE, TILE/2, 'White'))
        self.Joueur2 = Ennemi((self.x-3)*TILE, 2*TILE, 'Red', ('0rdi', (self.x-3)*TILE, TILE/2, 'DarkRed'), cible_mouvement=self.Joueur1, cible_tir=self.Joueur1)
        self.Joueur3 = Ennemi(2*TILE, (self.y-3)*TILE, 'LimeGreen', ('Ordi', 3*TILE, (self.y-0.5)*TILE, 'DarkGreen'), cible_mouvement=self.Joueur1, cible_tir=self.Joueur1)
        self.Joueur4 = Ennemi((self.x-3)*TILE, (self.y-3)*TILE, 'DodgerBlue', ('Ordi', (self.x-3)*TILE, (self.y-0.5)*TILE, 'DarkBlue'), cible_mouvement=self.Joueur1, cible_tir=self.Joueur1)
        #On enregistre les Joueurs dans une liste
        self.Joueurs = [self.Joueur1, self.Joueur2, self.Joueur3, self.Joueur4]

        self.nombre_ia = 3

        #Évents
        self.events = (('<Motion>', self.Joueur1.mouvement_canon),
                       ('<Button-1>', self.Joueur1.tir),
                       ('<Button-3>', self.Joueur1.miner),
                       ('<KeyPress>', self.Joueur1.change_dir),
                       ('<KeyRelease>', self.Joueur1.stop_dir))
        
        self.mission_suivante = self

        #Nombre de victoire et de défaites
        self.score = {"Defaite":0, "Victoire":0}

    def affichage_specifique(self, canvas):
        self.defaite = canvas.create_text(self.x*TILE/2, (self.y-0.5)*TILE, font="{} {}".format(FONT, TILE//2),
                                   text="Défaite(s): {}".format(self.score["Defaite"]) )
        self.victoire = canvas.create_text(self.x*TILE/2, TILE/2, font="{} {}".format(FONT, TILE//2),
                                   text="Victoire(s): {}".format(self.score["Victoire"]) )

    def fin2partie(self, canvas):
        #Si le joueur est mort...
        if (self.Joueur1.mort == True):
            #Réinitialisation
            for joueur in self.Joueurs:
                joueur.reborn()
            #Score défaite +1
            self.score["Defaite"] = self.score["Defaite"] + 1
            #Affichage
            canvas.itemconfig(self.defaite, text="Défaite(s): {}".format(self.score["Defaite"]) )
        #...ou si tous les ennemis sont morts
        if (self.Joueur2.mort == True) and (self.Joueur3.mort == True) and (self.Joueur4.mort == True):
            #Réinitialisation
            for joueur in self.Joueurs:
                joueur.reborn()
            #Score défaite +1
            self.score["Victoire"] = self.score["Victoire"] + 1
            #Affichage
            canvas.itemconfig(self.victoire, text="Victoire(s): {}".format(self.score["Victoire"]) )
        return False
        

#On lance le jeu
if __name__ == "__main__" :
    racine = Main(Demo())



















