
# -*- coding: utf-8 -*-
# https://www.reddit.com/r/Python/comments/anqkfy/this_can_be_made_with_python/

import numpy as np
import pylab as plt
from matplotlib import animation, lines

class AxAnimation() :

    def __init__(self, idx, ax, spx, spy) :
        self.idx = idx
        self.ax = ax

        self.speed_x = spx
        self.speed_y = spy
        self.xvalues, self.yvalues = self.positions()

        self.circle = plt.Circle((5, -5), 0.5, fc='red', axes=self.ax)
        self.line, = ax.plot(self.xvalues, self.yvalues, color="black")

    @staticmethod
    def init_ax(ax) :
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)

    def init_animate(self) :
        self.circle.center = (5, 5)
        self.ax.add_patch(self.circle)
        return self.line, self.circle

    def positions(self) :
        values = np.arange(0, 360)
        xvalues = 5 + 3 * np.sin(np.radians(values * self.speed_x))
        yvalues = 5 + 3 * np.cos(np.radians(values * self.speed_y))
        return xvalues, yvalues

    def animate(self, i) :
        self.circle.center = (self.xvalues[i], self.yvalues[i])
        self.line.set_data(self.xvalues[:i], self.yvalues[:i])
        return self.line, self.circle

def run() :

    n = 7

    fig, axes = plt.subplots(n, n, figsize=(6 ,6))
    animations = []

    for ridx, row in enumerate(axes, start=1) :
        for cidx, ax in enumerate(row, start=1) :
            AxAnimation.init_ax(ax)
            if ridx == cidx == 1 : continue

            if ridx == 1 or cidx == 1 :
                sridx = scidx = max((ridx, cidx))

            else :
                sridx, scidx = ridx, cidx

            aa = AxAnimation((ridx, cidx), ax, scidx, sridx)
            animations.append(aa)

    init_fun = lambda : [patch for aa in animations for patch in aa.init_animate()]
    anim_fun = lambda i : [patch for aa in animations for patch in aa.animate(i)]

    anim = animation.FuncAnimation(fig,
                                   func      = anim_fun,
                                   init_func = init_fun,
                                   frames    = 360,
                                   interval  = 30,
                                   blit      = True)

    plt.show()

if __name__ == "__main__" :
    run()

