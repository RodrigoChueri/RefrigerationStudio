import psychrolib as psy
import numpy as np

import psychrolib


def exemplo1():
    # Set the unit system, for example to SI (can be either SI or IP) - this needs to be done only once
    psychrolib.SetUnitSystem(psychrolib.SI)
    # Calculate the dew point temperature for a dry bulb temperature of 25 C and a relative humidity of 80%
    TDewPoint = psychrolib.GetTDewPointFromRelHum(25.0, 0.80)
    print(f'TDewPoint: {TDewPoint} degree C')

def exemplo2():

    psychrolib.SetUnitSystem(psychrolib.SI)

    # Defina as condições iniciais
    temperatura_bulbo_seco_inicial = 25.0  # em °C
    umidade_relativa_inicial = 0.5  # em %
    pressao_atmosferica = 101325  # em kPa (pressão atmosférica padrão)

    # Calcule a umidade absoluta
    umidade_absoluta = psychrolib.GetHumRatioFromRelHum(temperatura_bulbo_seco_inicial, umidade_relativa_inicial, pressao_atmosferica)

    # Suponha que você forneça uma quantidade de energia e deseje saber a nova temperatura de bulbo seco
    # (Vamos supor que você fornecerá uma quantidade de energia que elevará a temperatura em 5°C)
    energia_fornecida = 1000.0  # em kJ
    delta_temperatura = 5.0  # em °C
    nova_temperatura_bulbo_seco = temperatura_bulbo_seco_inicial + delta_temperatura

    # Calcule a umidade relativa para a nova temperatura de bulbo seco
    nova_umidade_relativa = psychrolib.GetRelHumFromHumRatio(nova_temperatura_bulbo_seco, umidade_absoluta, pressao_atmosferica)

    print("Nova temperatura de bulbo seco:", nova_temperatura_bulbo_seco, "°C")
    print("Nova umidade relativa:", nova_umidade_relativa, "%")

def exemplo3():
    psychrolib.SetUnitSystem(psychrolib.SI)
    T_bulbo_seco = 25
    umidade_relativa = 0.5
    h = psychrolib.GetMoistAirEnthalpy(T_bulbo_seco,umidade_relativa)
    c = psychrolib.Heat
    print("entalpia a " + str(T_bulbo_seco) + "°C e umidade relativa de "+ str(umidade_relativa) + " = " + str(h) + " J kg⁻¹")
    
exemplo3()