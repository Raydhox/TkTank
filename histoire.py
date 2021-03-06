#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#==================================TkTank==========================================================
#Par: UNG Harry
#License: License libre
#==================================================================================================
#Un mode histoire utilisant le moteur du jeu TkTank.
#==================================================================================================
#Note: Oui, le code source est loin d'être élégant (le contraire, même), peut être mal commenté
#   et si il y a des fautes de français: désolé.
#==================================================================================================

#MODUlES
from tkinter import *
import math, random, getpass, socket

from moteur import *

class Pulsar(Ennemi):
    
    def __init__(self, x, y, couleur, nom, cible_mouvement=None, cible_tir=None, pv=16, tirs_par_seconde=4, pulsation=1000):
        #Classe qui hérite de le classe Char
        Ennemi.__init__(self, x, y, couleur, nom, cible_mouvement, cible_tir, pv, tirs_par_seconde)
        
        self.pulse_timer, self.periode = pulsation, pulsation
        
    def ia(self):
        #Gestion des "pulsations", ie un tir dans les 4 sens à intervalle régulier.
        self.pulse_timer -= TIME
        if self.pulse_timer <= 0:
            self.pulse_timer = self.periode
            [[self.ia_tir((self.char_x + dx, self.char_y + dy), tir_force=True) for dx in (1, 0, -1)] for dy in (-1, 0, 1)]
        Ennemi.ia(self)

#Mission d'intro
class Mission0(Mission):

    def __init__(self) :
        Mission.__init__(self)
        #Mis en place du terrain de jeu sous forme de liste 'terrain'
        self.terrain = ["1111111111111111111111111111111111",
                        "1000000000000000000001000000000001",
                        "1000000000000000000001000000000001",
                        "1000000000000000000001000000000001",
                        "1000000000001000000000000000000001",
                        "1000000000001000000000000000000001",
                        "1000000000001000000000000000000001",
                        "1111111110001111111111000111110001",
                        "1000000000001111111111000000000001",
                        "1000000000001111111111000000000001",
                        "1000000000001111111111000000000001",
                        "1000000000001111111111000000000001",
                        "1000000000001111111111000000000001",
                        "1000111110001111111111000111111111",
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
        self.Joueur2 = Ennemi((self.x-3)*TILE, 2*TILE, 'Red', ('0rdi', (self.x-3)*TILE, TILE/2, 'DarkRed'), pv=3)
        self.Joueur3 = Ennemi(2*TILE, (self.y-3)*TILE, 'LimeGreen', ('Ordi', 3*TILE, (self.y-0.5)*TILE, 'DarkGreen'), pv=3)
        self.Joueur4 = Ennemi((self.x-3)*TILE, (self.y-3)*TILE, 'DodgerBlue', ('Ordi', (self.x-3)*TILE, (self.y-0.5)*TILE, 'DarkBlue'), pv=3)
        #On enregistre les Joueurs dans une liste
        self.Joueurs = [self.Joueur1, self.Joueur2, self.Joueur3, self.Joueur4]

        self.nombre_ia = 3

        #Évents
        self.events = (('<Motion>', self.Joueur1.mouvement_canon),
                       ('<Button-1>', self.Joueur1.tir),
                       ('<Button-3>', self.Joueur1.miner),
                       ('<KeyPress>', self.Joueur1.change_dir),
                       ('<KeyRelease>', self.Joueur1.stop_dir))
        
        self.mission_suivante = Mission1()

    def affichage_specifique(self, canvas):
        self.objectif = canvas.create_text(self.x*TILE/2, TILE/2, font="{} {}".format(FONT, TILE//2),
                                   text="Mission 0 : Décimer l'ennemi" )
        self.tuto =  canvas.create_text(self.x*TILE/2, self.y*TILE/2, font="{} {}".format(FONT, TILE//2), justify=CENTER,
                                   text="""Flèches directionnelles
OU zqsd OU wasd :
se déplacer \n
Click gauche : Tirer
Click droit : Poser une mine""" )

    def fin2partie(self, canvas):
        if (self.Joueur2.mort == True) and (self.Joueur3.mort == True) and (self.Joueur4.mort == True):
            return True

        return False

#Mission1
class Mission1(Mission):

    def __init__(self) :
        Mission.__init__(self)
        
        #Mis en place du terrain de jeu sous forme de liste 'terrain'
        self.terrain = ["1111111111111111111111111111111111",
                        "1000000001000000000000001000000001",
                        "1000000001000000000000001000000001",
                        "1000000001000000000000001000000001",
                        "1000000000000010000100000000000001",
                        "1001111000000010000100000001110001",
                        "1000000000000010000100000000000001",
                        "1000000001000010000100001000000001",
                        "1000000001000000000000001000000001",
                        "1000000001000000000000001000000001",
                        "1110011111001000110001001111100111",
                        "1000000001000000000000001000000001",
                        "1000000001000000000000001000000001",
                        "1000000001000010000100001000000001",
                        "1000000000000010000100000000000001",
                        "1001111000000010000100000001111001",
                        "1000000001000010000100001000000001",
                        "1000000001000010000100001000000001",
                        "1000000001000000000000001000000001",
                        "1000000001000000000000001000000001",
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
        
        self.mission_suivante = Mission2()
        

    def affichage_specifique(self, canvas):
        self.objectif = canvas.create_text(self.x*TILE/2, TILE/2, font="{} {}".format(FONT, TILE//2),
                                   text="Mission 1 : Décimer l'ennemi" )

    def fin2partie(self, canvas):
        if (self.Joueur1.mort == True):
            #Réinitialisation
            for joueur in self.Joueurs:
                joueur.reborn()
        elif (self.Joueur2.mort == True) and (self.Joueur3.mort == True) and (self.Joueur4.mort == True):
            return True

        return False

#
class Mission2(Mission):

    def __init__(self) :
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
                       ('<KeyPress>', self.Joueur1.change_dir),
                       ('<KeyRelease>', self.Joueur1.stop_dir))
        
        self.mission_suivante = Mission3()


    def affichage_specifique(self, canvas):
        self.objectif = canvas.create_text(self.x*TILE/2, TILE/2, font="{} {}".format(FONT, TILE//2), text="Mission 2 : Fuir" )
        self.astuce = canvas.create_text(self.x*TILE/2, (self.y-0.5)*TILE, font="{} {}".format(FONT, TILE//2),
                                   text="Atteignez la croix rouge. Erreur : Tirs impossible." )
        self.teleporteur = canvas.create_text(TILE*(self.x-2), TILE*(self.y-2), fill="red", font="Time_New_Roman {}".format(TILE), text="x")

    def fin2partie(self, canvas):
        if (self.Joueur1.mort == True):
            #Réinitialisation
            for joueur in self.Joueurs:
                joueur.reborn()
        elif self.Joueur1.char_x >= TILE*(self.x-2) and self.Joueur1.char_y >= TILE*(self.y-2):
            return True

        return False

#
class Mission3(Mission):

    def __init__(self) :
        Mission.__init__(self)
        
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
                        "1000000000000000010000000000000001",
                        "1000000000000000101000000000000001",
                        "1000000000000000010000000000000001",
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

        #On crée les chars
        self.Joueur1 = Char(17*TILE, 10*TILE, 'Yellow', ('Joueur', 3*TILE, TILE/2, 'White'))
        self.Joueur2 = Ennemi((self.x-3)*TILE, 2*TILE, 'Red', ('0rdi', (self.x-3)*TILE, TILE/2, 'DarkRed'), cible_mouvement=self.Joueur1, cible_tir=self.Joueur1)
        self.Joueur3 = Ennemi(2*TILE, (self.y-3)*TILE, 'LimeGreen', ('Ordi', 3*TILE, (self.y-0.5)*TILE, 'DarkGreen'), cible_mouvement=self.Joueur1, cible_tir=self.Joueur1)
        self.Joueur4 = Ennemi((self.x-3)*TILE, (self.y-3)*TILE, 'DodgerBlue', ('Ordi', (self.x-3)*TILE, (self.y-0.5)*TILE, 'DarkBlue'), cible_mouvement=self.Joueur1, cible_tir=self.Joueur1)
        #On enregistre les Joueurs dans une liste
        self.Joueurs = [self.Joueur1, self.Joueur2, self.Joueur3, self.Joueur4]

        self.nombre_ia = 3

        #Évents
        self.events = (('<Motion>', self.Joueur1.mouvement_canon),
                       ('<Button-1>', self.Joueur1.tir),
                       ('<Button-3>', self.Joueur1.miner))
        
        self.mission_suivante = Mission4()


    def affichage_specifique(self, canvas):
        self.objectif = canvas.create_text(self.x*TILE/2, TILE/2, font="{} {}".format(FONT, TILE//2), text="Mission 3 : Décimer l'ennemi" )

    def fin2partie(self, canvas):
        if (self.Joueur1.mort == True):
            #Réinitialisation
            for joueur in self.Joueurs:
                joueur.reborn()
            
        elif (self.Joueur2.mort == True) and (self.Joueur3.mort == True) and (self.Joueur4.mort == True):
            return True

        return False

#
class Mission4(Mission):

    def __init__(self) :
        Mission.__init__(self)

        #On crée les chars
        self.Joueur1 = Char(17*TILE, 10*TILE, 'Yellow', ('Joueur', 3*TILE, TILE/2, 'White'))
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
        
        self.mission_suivante = Mission5()
        self.boucle_active = False

    def affichage_specifique(self, canvas):
        self.objectif = canvas.create_text(self.x*TILE/2, TILE/2, font="{} {}".format(FONT, TILE//2), text="Mission 4 : Décimer l'ennemi" )
        self.astuce = canvas.create_text(self.x*TILE/2, (self.y-0.5)*TILE, font="{} {}".format(FONT, TILE//2),
                                   text="Oups, il semblerait que vous controliez le temps." )

    def fin2partie(self, canvas):
        if (True in self.Joueur1.dir):
            self.boucle_active = True
        else:
            for joueur in self.Joueurs:
                joueur.dir = [False, False, False, False]
            self.boucle_active = False
            
        if (self.Joueur1.mort == True):
            #Réinitialisation
            for joueur in self.Joueurs:
                joueur.reborn()
        elif (self.Joueur2.mort == True) and (self.Joueur3.mort == True) and (self.Joueur4.mort == True):
            return True

        return False


class Mission5(Mission):

    def __init__(self) :
        Mission.__init__(self)
        
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
                        "1000000001111111111111111000000001",
                        "1000000001111111111111111000000001",
                        "1000000001111111111111111000000001",
                        "1000000001111111111111111000000001",
                        "1000000001111111111111111000000001",
                        "1111111111111111111111111111111111"]
        #Cimetière (n'est pas affiché)
        for k in range(3):
            self.terrain.append("1111111111111111111111111111111111")  

        #On crée les chars
        self.Joueur1 = Char(17*TILE, 10*TILE, 'Yellow', ('Joueur', 3*TILE, TILE/2, 'White'))
        #On enregistre les Joueurs dans une liste
        self.Joueurs = [self.Joueur1]

        #Évents
        self.events = (('<Motion>', self.Joueur1.mouvement_canon),
                       ('<Button-1>', self.Joueur1.tir),
                       ('<Button-3>', self.special_event),
                       ('<KeyPress>', self.Joueur1.change_dir),
                       ('<KeyRelease>', self.Joueur1.stop_dir))
        
        #Monologue et curseur permmetant de connaître la ligne.
        self.ligne = 0
        self.monologue = ["Faîtes un Clique gauche pour afficher la suite.",
						  "Je me présente : ln(3), boss finale du jeu.",
						  "Je suis désolé pour les désagréments\n lors des derniers niveaux.",
						  "Voyez-vous, j'étais occupée à faire deux-trois\n manipulations avec le code du jeu.",
						  "Pourquoi ?",
						  "Simplement car en tant que boss de jeu,\n j'étais destinée à mourir de vos tirs",
						  "Ce à quoi, naturellement, j'y étais opposée.",
						  "Je me suis donc permise de me créer\n plusieurs copies de moi-même.",
						  "Oui, me tuer ne servira à rien.",
						  "Mais je vais être gentille :\n il reste 5 missions avant la fin du jeu.",
						  "Et si nous nous amusions un peu avant...",
						  "Ne refusez pas mon offre, car j'ai déjà\n commencé à pirater votre ordinateur.",
						  "Qui c'est ce que je pourrais bien faire\n avec celui-ci si vous refusez ?",
						  "N'est-ce pas, {} ?\n À moins que vous ne teniez pas à\n {}...".format(getpass.getuser(), socket.gethostname()),
						  "En effet, je compte bien vous faire souffrir.",
						  "Faîtes Clique gauche pour commencer."]
        
        self.mission_suivante = Mission6()
     
     
    def special_event(self, event):
        #On affiche la prochaine ligne, de monologue.
        self.ligne += 1

        self.Joueur1.miner(event)

    def affichage_specifique(self, canvas):
        self.objectif = canvas.create_text(self.x*TILE/2, TILE/2, font="{} {}".format(FONT, TILE//2), text="Mission 5 : ???" )
        self.textbox = canvas.create_text(self.x*TILE/2, (self.y-3)*TILE, font="{} {}".format(FONT, TILE//2), justify=CENTER,
                                          text=self.monologue[self.ligne]) 

    def fin2partie(self, canvas):
        #On passe au niveau suivant si tous les lignes de dialogues ont été affichés.
        if self.ligne >= len(self.monologue):
            return True
        if self.Joueur1.mort :
            self.Joueur1.reborn()
            self.ligne = 0
        
        #Mise à jour du monologue.
        canvas.itemconfig(self.textbox, text=self.monologue[self.ligne])

        return False


class Mission6(Mission):

    def __init__(self) :
        Mission.__init__(self)

        #On crée les chars
        self.Joueur1 = Char(2*TILE, 2*TILE, 'Yellow', (getpass.getuser(), 3*TILE, TILE/2, 'White'), pv=1)
        self.Boss = Ennemi(17*TILE, 10*TILE, 'Grey', ('ln(3)', 17*TILE, TILE*(self.y-0.5), 'Black'), tirs_par_seconde=20, pv=999)
        #On enregistre les Joueurs dans une liste
        self.Joueurs = [self.Joueur1, self.Boss]
        self.nombre_ia = 1

        #Évents
        self.events = (('<Motion>', self.Joueur1.mouvement_canon),
                       ('<Button-1>', self.Joueur1.tir),
                       ('<Button-3>', self.Joueur1.miner),
                       ('<KeyPress>', self.Joueur1.change_dir),
                       ('<KeyRelease>', self.Joueur1.stop_dir))
        
        self.mission_suivante = Mission7()

    def affichage_specifique(self, canvas):
        self.objectif = canvas.create_text(self.x*TILE/2, TILE/2, font="{} {}".format(FONT, TILE//2), text="Mission 6 : Fuir ou vaincre la boss." )
        self.teleporteur = canvas.create_text(TILE*(self.x-2), TILE*(self.y-2), fill="red", font="Time_New_Roman {}".format(TILE), text="x")

    def fin2partie(self, canvas):
        self.Boss.cible_tir = (random.randrange(TILE*self.x),  random.randrange(TILE*self.y))
        
        if self.Joueur1.mort:
            for joueur in self.Joueurs:
                joueur.reborn()
        elif self.Boss.mort or (self.Joueur1.char_x >= TILE*(self.x-2) and self.Joueur1.char_y >= TILE*(self.y-2)):
            return True

        return False


class Mission7(Mission):

    def __init__(self) :
        Mission.__init__(self)
        
        #Mis en place du terrain de jeu sous forme de liste 'terrain'
        self.terrain = ["1111111111111111111111111111111111",
                        "1000000001000000000000000000000001",
                        "1000000001000000000000000000000001",
                        "1000000001000000000000000000000001",
                        "1000000001000000000000000000000001",
                        "1000000001000000000001000000000001",
                        "1000000001000000000001000000000001",
                        "1000000001000000000001000000000001",
                        "1000000001111110000001000000000001",
                        "1000000001000000000001000000000001",
                        "1000000001000000000001000000000001",
                        "1000000001000000000001000000000001",
                        "1000000001000000000001000000000001",
                        "1000000001000000111111000000111111",
                        "1000000000000000000001000000000001",
                        "1000000000000000000001000000000001",
                        "1000000000000000000001000000000001",
                        "1000000000000000000001000000000001",
                        "1000000000000000000001000000000001",
                        "1000000000000000000001000000000001",
                        "1111111111111111111111111111111111"]
        #Cimetière (n'est pas affiché)
        for k in range(3):
            self.terrain.append("1111111111111111111111111111111111") 

        #On crée les chars
        self.Joueur1 = Char(2*TILE, 2*TILE, 'Yellow', (getpass.getuser(), 3*TILE, TILE/2, 'White'))
        #On enregistre les Joueurs dans une liste
        self.Joueurs = [self.Joueur1]

        #Évents
        self.events = (('<Motion>', self.Joueur1.mouvement_canon),
                       ('<Button-1>', self.Joueur1.tir),
                       ('<Button-3>', self.Joueur1.miner),
                       ('<KeyPress>', self.Joueur1.change_dir),
                       ('<KeyRelease>', self.Joueur1.stop_dir))
        
        self.mission_suivante = Mission8()

    def affichage_specifique(self, canvas):
        self.objectif = canvas.create_text(self.x*TILE/2, TILE/2, font="{} {}".format(FONT, TILE//2), text="Mission 7 : Fuir" )
        canvas.create_rectangle(TILE, TILE, TILE*(self.x-1), TILE*(self.y-1), fill="black")
        self.teleporteur = canvas.create_text(TILE*(self.x-2), TILE*(self.y-2), fill="red", font="{} {}".format(FONT, TILE), text="x")
        self.message = canvas.create_text(TILE*self.x/2, TILE*self.y/2, fill="white", font="{} {}".format(FONT, TILE//2),
                                          text="""Ouf, vous avez réussi à lui échapper.
Je me présente : PULSAR, Programme Ultime de Lutte Secrète Anti Rébellion.
Le créateur du jeu se doutait que ln(3) pouvait se rebeller un jour...
Aussi ai-je été crée pour réinitialisé le jeu en cas de problème.
Pour commencer, nous devrons effacer les copies de ln(3).
Ne vous inquiétez pas, j'ai réinitialisé ses données avec les copies de sauvegardes.
Ensuite, vous devrez me désactiver, puis je pense que la réinitialisation sera terminée.
Pour lancer la réinitialisation, rejoignez le téléporteur (la croix rouge).""")

    def fin2partie(self, canvas):
        if self.Joueur1.mort:
            for joueur in self.Joueurs:
                joueur.reborn()
        elif self.Joueur1.char_x >= TILE*(self.x-2) and self.Joueur1.char_y >= TILE*(self.y-2):
            return True

        return False


class Mission8(Mission):

    def __init__(self) :
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
        self.Joueur1 = Char(2*TILE, 2*TILE, 'Yellow', (getpass.getuser(), 3*TILE, TILE/2, 'White'))
        self.Joueur2 = Char(2*TILE, (self.y-3)*TILE, 'Orange', (getpass.getuser(), 3*TILE, (self.y-0.5)*TILE, 'DarkRed'))
        self.Joueur3 = Ennemi((self.x-3)*TILE, 2*TILE, 'LimeGreen', ('ln(3)', (self.x-3)*TILE, TILE/2, 'DarkGreen'),
                              cible_mouvement=self.Joueur1, cible_tir=self.Joueur1, pv=32)
        self.Joueur4 = Ennemi((self.x-3)*TILE, (self.y-3)*TILE, 'DodgerBlue', ('ln(3)', (self.x-3)*TILE, (self.y-0.5)*TILE, 'DarkBlue'),
                              cible_mouvement=self.Joueur2, cible_tir=self.Joueur2, pv=32)
        #On enregistre les Joueurs dans une liste
        self.Joueurs = [self.Joueur1, self.Joueur2, self.Joueur3, self.Joueur4]

        self.nombre_ia = 2
        
        #Évents
        self.events = (('<Motion>', self.double_mouvement_canon),
                       ('<Button-1>', self.double_tir),
                       ('<Button-3>', self.double_miner),
                       ('<KeyPress>', self.double_change_dir),
                       ('<KeyRelease>', self.double_stop_dir))
        
        self.mission_suivante = Mission9()

    def double_mouvement_canon(self, event):
        self.Joueur1.mouvement_canon(event)
        self.Joueur2.mouvement_canon(event)
        
    def double_tir(self, event):
        self.Joueur1.tir(event)
        self.Joueur2.tir(event)
        
    def double_miner(self, event):
        self.Joueur1.miner(event)
        self.Joueur2.miner(event)
        
    def double_change_dir(self, event):
        self.Joueur1.change_dir(event)
        self.Joueur2.change_dir(event)
        
    def double_stop_dir(self, event):
        self.Joueur1.stop_dir(event)
        self.Joueur2.stop_dir(event)
        
        
    def affichage_specifique(self, canvas):
        self.objectif = canvas.create_text(self.x*TILE/2, TILE/2, font="{} {}".format(FONT, TILE//2), text="Mission 8 : Décimer l'ennemi." )
        self.astuce = canvas.create_text(self.x*TILE/2, (self.y-0.5)*TILE, font="{} {}".format(FONT, TILE//2),
                                   text="PULSAR : Oups, la copie de sauvegarde vous a dédoublé..." )

    def fin2partie(self, canvas):
        if self.Joueur1.mort or self.Joueur2.mort:
            #Réinitialisation
            for joueur in self.Joueurs:
                joueur.reborn()
        elif self.Joueur3.mort and self.Joueur4.mort:
            return True

        return False


class Mission9(Mission):

    def __init__(self) :
        Mission.__init__(self)

        #On crée les chars
        self.Joueur1 = Char(2*TILE, 2*TILE, 'Yellow', (getpass.getuser(), 3*TILE, TILE/2, 'White'), vitesse=2)
        self.Boss = Pulsar(TILE*(self.x-3), TILE*(self.y-3), 'White', ('PULSAR', (self.x-3)*TILE, (self.y-0.5)*TILE, 'White'),
                             cible_mouvement=self.Joueur1, cible_tir=self.Joueur1, pv=99)
        #On enregistre les Joueurs dans une liste
        self.Joueurs = [self.Joueur1, self.Boss]
        self.nombre_ia = 1

        #Évents
        self.events = (('<Motion>', self.Joueur1.mouvement_canon),
                       ('<Button-1>', self.Joueur1.tir),
                       ('<Button-3>', self.Joueur1.miner),
                       ('<KeyPress>', self.Joueur1.change_dir),
                       ('<KeyRelease>', self.Joueur1.stop_dir))
        
        self.mission_suivante = Mission10()

    def affichage_specifique(self, canvas):
        self.objectif = canvas.create_text(self.x*TILE/2, TILE/2, font="{} {}".format(FONT, TILE//2), text="Mission 9 : Vaincre le boss" )
        self.astuce = canvas.create_text(self.x*TILE/2, (self.y-0.5)*TILE, font="{} {}".format(FONT, TILE//2),
                                   text="PULSAR : J'ai fusionné vos copies." )

    def fin2partie(self, canvas):
        if self.Joueur1.mort:
            for joueur in self.Joueurs:
                joueur.reborn()
        elif self.Boss.mort:
            return True

        return False


class Mission10(Mission):

    def __init__(self) :
        Mission.__init__(self)

        #On crée les chars
        self.Joueur1 = Char(2*TILE, 2*TILE, 'Yellow', (getpass.getuser(), 3*TILE, TILE/2, 'White'), pv=16, vitesse=2)
        #On enregistre les Joueurs dans une liste
        self.Joueurs = [self.Joueur1]

        #Évents
        self.events = (('<Motion>', self.Joueur1.mouvement_canon),
                       ('<Button-1>', self.Joueur1.tir),
                       ('<Button-3>', self.Joueur1.miner),
                       ('<KeyPress>', self.Joueur1.change_dir),
                       ('<KeyRelease>', self.Joueur1.stop_dir))
        
        self.mission_suivante = Endgame()

    def affichage_specifique(self, canvas):
        self.objectif = canvas.create_text(self.x*TILE/2, TILE/2, font="{} {}".format(FONT, TILE//2), text="Mission 10 : ???" )
        self.merci = canvas.create_text(self.x*TILE/2, (self.y-0.5)*TILE, font="{} {}".format(FONT, TILE//2),
                                   text="Réinitialisation terminée à 99%" )

    def fin2partie(self, canvas):
        if self.Joueur1.mort:
            return True

        return False


class Endgame(Mission):

    def __init__(self) :
        Mission.__init__(self)

    def affichage_specifique(self, canvas):
        self.titre = canvas.create_text(self.x*TILE/2, TILE/2, font="{} {}".format(FONT, TILE//2), text="TkTank" )
        canvas.create_rectangle(TILE, TILE, TILE*(self.x-1), TILE*(self.y-1), fill="black")
        self.message = canvas.create_text(TILE*self.x/2, TILE*self.y/2, fill="white", font="{} {}".format(FONT, TILE), text="RÉINITIALISATION TERMINÉE")
        self.merci = canvas.create_text(self.x*TILE/2, (self.y-0.5)*TILE, font="{} {}".format(FONT, TILE//2),
                                   text="Merci d'avoir joué !" )


#On lance le mode histoire.
if __name__ == "__main__" :
    racine = Main(Mission0())


