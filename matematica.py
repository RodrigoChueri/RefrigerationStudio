from shapely.geometry import Polygon
import math

def remover_duplicadas_set(lista_tuplas):
  """
  Remove tuplas duplicadas de uma lista usando um conjunto.

  Argumentos:
    lista_tuplas: Uma lista de tuplas.

  Retorno:
    Uma lista de tuplas sem duplicatas.
  """
  conjunto_tuplas = set(lista_tuplas)
  lista_sem_duplicatas = list(conjunto_tuplas)
  return lista_sem_duplicatas

def is_float(string):
  try:
    float(string)
    return True
  except ValueError:
    if(string==""or string == " "):
      return True
    return False
  

def verificar_entradas_numeros_e_vazias(lista):
  for string in lista:
    if(is_float(string)==False):
      return False
  return True

def Area_entrada_str(figura):
    figura = figura.replace(" ","")
    pares_coordenadas = figura.split("),(")
    vertices = [(float(par.split(",")[0].replace("(","").replace(")","")), float(par.split(",")[1].replace("(","").replace(")",""))) for par in pares_coordenadas]
    pgon = Polygon(vertices) # Assuming the OP's x,y coordinates
    area = pgon.area

    return area