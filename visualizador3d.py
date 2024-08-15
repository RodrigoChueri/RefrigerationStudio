from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt
def ex1():
    fig = plt.figure()
    ax = Axes3D(fig, auto_add_to_figure=False)
    fig.add_axes(ax)
    x = [0,1,1,0]
    y = [0,0,1,1]
    z = [0,1,0,1]
    verts = [list(zip(x,y,z))]
    ax.add_collection3d(Poly3DCollection(verts))
    plt.show()

def ex2():
    P1 = [0,0,0]
    P2 = [0,1,0]
    P3 = [1,0,1]
    P4 = [0,1,1]
    P5 = [1,1,1]
    P6 = [1,1,0]
    P7 = [1,0,0]
    P8 = [0,0,1]
    lista_pontos = [P1,P2,P3,P4,P5,P6,P7,P8]
    fig = plt.figure()
    ax = Axes3D(fig, auto_add_to_figure=False)
    fig.add_axes(ax)

    x=[]
    y=[]
    z=[]
    for ponto in lista_pontos:
        x.append(ponto[0])
        y.append(ponto[1])
        z.append(ponto[2])
    vertices = [list(zip(x,y,z))]
    ax.add_collection3d(Poly3DCollection(vertices))
    plt.show()

ex2()