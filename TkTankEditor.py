#!/usr/bin/env python
# -*- coding: utf-8 -*-

#==================================TkinTank==========================================================
#Par: UNG Harry
#Description: Permet de créer une map pour TkTank.
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
from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
import math, random

TILE = 32

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
        self.terrain.append("1111111111111111111111111111111111")
        self.terrain.append("1111111111111111111111111111111111")

        self.x, self.y = ( len(self.terrain[0]), len(self.terrain)-2 )

        try:
            filename = askopenfilename(defaultextension='*.tktank', filetypes=[('supported', ('*.tktank'))])
            with open(filename, "r") as f:
                self.terrain = []
                for k in range(self.y):
                    self.terrain.append(f.readline()[:self.x])
                self.terrain.append("1111111111111111111111111111111111")
                self.terrain.append("1111111111111111111111111111111111")
        except:
            pass

        #On crée un Canvas 'jeu'
        self.canvas = Canvas(self.fenetre, width=self.x*TILE, height=self.y*TILE, bg='NavajoWhite', cursor="cross")
        self.canvas.pack(side=LEFT)
        
    def montrer(self):
        """===Boucle principale du jeu.==="""
        #On parcours la liste et en fonction des valeurs, on affiche une brique ou non
        self.canvas.create_rectangle(0, 0, self.x*TILE, self.y*TILE, width=0, fill='NavajoWhite')
        for i in range(self.y):
            for j in range(self.x):
                if self.terrain[i][j] == '1':
                    x = j*TILE
                    y = i*TILE
                    self.canvas.create_rectangle(x, y, x+TILE, y+TILE, width=0, fill='DarkGoldenRod')
                    
    def change0(self, event):
        x, y = event.x//TILE, event.y//TILE
        if x and y and (x != self.x-1) and (y != self.y-1):
            self.terrain[y] = self.terrain[y][0:x] + "0" + self.terrain[y][x+1:]
        self.montrer()

    def change1(self, event):
        x, y = event.x//TILE, event.y//TILE
        self.terrain[y] = self.terrain[y][0:x] + "1" + self.terrain[y][x+1:]
        self.montrer()

    def save(self, event):
        filename = asksaveasfilename(defaultextension='*.tktank', filetypes=[('supported', ('*.tktank'))])
        with open(filename, 'w') as f:
            for k in range(self.y):
                f.write(self.terrain[k] + "\n")

    def afficher(self):
        #On parcours la liste et en fonction des valeurs, on affiche une brique ou non
        self.montrer()
        #Evènements
        self.canvas.bind('<Button-1>', self.change1)
        self.canvas.bind('<Button-2>', self.save)
        self.canvas.bind('<Button-3>', self.change0)
        #On lance le tout
        self.fenetre.mainloop()           


#On lance le jeu
racine = Main()
racine.afficher()




















