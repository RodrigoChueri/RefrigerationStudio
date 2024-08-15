from math import *
# estudar https://www.mdpi.com/2071-1050/11/22/6443
#RB e RB2 são equivalentes, apenas com sinal do azimuth trocado como visto nos prints

class Angulo_Solar:
  def __init__(self):
    self.por_do_sol = False
    self.nascer_do_sol = False
  def antigo(t):

    d = 90
    a = 0.40928 * cos(2*pi/365 * (d+10)) # inclinação da terra ao longo do ano



    phi = 0   # latitude
    b = 365/4 # angulo 90 para parede e 0 para horizontal
    c  = 90 # angulo em relação ao norte
    w = pi/12 * (t-12)

    #mudando para rad
    phi = phi *2*pi/360
    b = b * 2*pi/360
    c = c * 2*pi/360


    ang_sol_com_normal_placa = asin ( 
          sin(a)*sin(phi)*cos(b) + 
          sin(a)*cos(phi)*sin(b)*cos(c) +
          cos(a)*cos(phi)*cos(w)*cos(b) -
          cos(a)*sin(phi)*cos(w)*sin(b)*cos(c) -
          cos(a)*sin(w)*sin(b)*sin(c)
        )


    It = max([0, sin(ang_sol_com_normal_placa) * 100])

    print(str(ang_sol_com_normal_placa*360/(2*pi)), " -> " ,str(b*360/(2*pi)))
    print(It)
    return It

  # https://www.hindawi.com/journals/jre/2013/307547/
  def Rb2(self, Declinação, Azimute, L, beta, w, t):
    Azimute = -Azimute
    if(t==6):
      t=6.5
      w = pi/12 * (t-12)
    
    if(t==18):
      t=17.5
      w = pi/12 * (t-12)

    if(t < 6 or t > 18):
      
      return 0

    Rb = cos(beta) - sin(beta)*(sin(Declinação)*cos(L)*cos(Azimute)-cos(Declinação)*sin(L)*cos(w)*cos(Azimute)- cos(Declinação)*sin(Azimute)*sin(w)) / ( sin(Declinação)*sin(L) + cos(Declinação) *cos(L) *cos(w) )

    return Rb
  # https://www.mdpi.com/2071-1050/11/22/6443
  def Rb(self, Declinação, Azimute, L, beta, w, t):


    cos_theta = sin(Declinação)*sin(L)*cos(beta)- sin(Declinação)*cos(L)*sin(beta)*cos(Azimute) + cos(Declinação)*cos(L)*cos(beta)*cos(w) + cos(Declinação)*sin(L)*sin(beta)*cos(Azimute)*cos(w) + cos(Declinação)*sin(beta)*sin(Azimute)*sin(w)
    #w12 = 0
    cos_theta_z = cos(Declinação)*cos(L)*cos(w) + sin(Declinação)*sin(L)
    Rb_ = cos_theta/cos_theta_z
    if(Rb_<0):
      Rb_=0
    if(Rb_>40):
      #print("Tendendo ao infinito: " + str(t) + "h")
      Rb_=40
    ang_altitude_sol = asin(sin( cos(L)*cos(Declinação)*cos(w)+sin(L)*sin(Declinação)))
    azimute_sol = acos(  (sin(ang_altitude_sol)*sin(L)-sin(Declinação))/(cos(ang_altitude_sol)*cos(L))    )
    diferença_angulos = abs(Azimute-azimute_sol)/2/pi*360
    if(t>=18 and Azimute==pi*3/2):
      None
    if(diferença_angulos>179):
      Rb_ = 0
    #print(Rb)
    return Rb_


  def HB(self, Hg, Hd, Rb):
    _HB = (Hg-Hd)*Rb

    #print("(" + str(Hg) + "-" + str(Hd) + ")*" + str(Rb))
    return _HB

  def HD(self, Rd_, Hd):
    return Rd_*Hd


  def Rd_LiuJordan(self, beta):
    Rd = (1+cos(beta))/2
    return Rd

  # HT = HB + HD + HR
  # HB é o raio direto na superficie, HD a rad difusa e HR a refletida
  def RadIncidente(self, hora, GHW, DHR, D, Azimute, beta, L_rad):


    Hg = GHW
    Hd = DHR
    #D = 120
    Declinação = 23.45 * sin( (284+D)/ 365 * 2 *  pi)
    # Azimute = 90
    # beta = 90
    # L = 0 # latitude
    t = hora
    w = pi/12 * (t-12)

    #mudando para rad
    Azimute = Azimute
    Azimute = Azimute * 2*pi/360
    Declinação = Declinação * 2*pi/360

    # primeiro achar o Rb
    Rb_ = self.Rb(Declinação, Azimute, L_rad, beta, w, t)
    Rb_2 = self.Rb2(Declinação, -Azimute, L_rad, beta, w, t)
    # achar a radiação direta (sem a difusa e relfetida)
    HB_ = max([self.HB(Hg,Hd,Rb_),0])
    #achar a radiação refletida
    HR_ = self.HR(beta, Hg) #onde é HB_ era Hg, mas acho que era Hg o correto
    # achar a rad difusa
    Rd_ = self.Rd_LiuJordan(beta)
    HD_ = self.HD(Rd_, Hd)

    # rad total 
    HT = HB_ + HD_ + HR_

    #if(t<6 or t>18):
    #  return 0,0,0,0
      

    #else:
    maximo = max([HT,0])
    return  maximo, Rb_, HB_, Rb_2

  #calculado em relação ao refletido pelo solo
  def HR(self, beta,Hg):
    refletancia_solo = 0.2
    _HR = Hg*refletancia_solo*(1-cos(beta))/2
    return _HR

  def LiuAndJordanModel():
    It = (Ig-Id)*Rb



if __name__ == '__main__':
  # testando para o dia 01/01/2008 na vila militar


  D = 120
  Azimute = 90
  beta = 90
  L = 0 # latitude
  #mudando para rad
  L_rad = L * 2 * pi / 360



  lista_radiacao =[
    [0,0,0],
    [0,0,0],
    [0,0,0],
    [0,0,0],
    [0,0,0],
    [0,0,0],
    [1,0,1],
    [54,0,53],
    [170,3,165],
    [330,24,296],
    [435,52,375],
    [539,102,432],
    [601,148,450],
    [603,159,436],
    [680,287,345],
    [553,184,295],
    [561,234,117],
    [228,29,134],
    [33,0,30],
    [0,0,0],
    [0,0,0],
    [0,0,0],
    [0,0,0],
    [0,0,0],
    [0,0,0],
    [0,0,0]
    
  ]
  print("HT,  Rb,  Theta")
  for t in range(25):
    if(t!=0):

      GHW = lista_radiacao[t][0]
      DNR = lista_radiacao[t][1]
      DHR = lista_radiacao[t][2]
      print(str(t), " : ", str(RadIncidente(t, GHW, DHR, D, Azimute, beta, L_rad)))