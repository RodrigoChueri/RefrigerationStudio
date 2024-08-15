from shapely.geometry import LineString, Point

def encontrar_segmentos_de_reta(lado1, lado2):
    if("ignorar" in lado1 or "ignorar" in lado2):
        return None
    
    segmentos = []
    linestrings = []
    pares_usados = []
    p1 = lado1[0]
    p2 = lado1[1]
    q1 = lado2[0]
    q2 = lado2[1]
    if (intersecta(p1, p2, q1, q2) and (lado1 != lado2) and (p1 != q2 or p2!= q1)):
        intersecao = encontrar_intersecao(p1, p2, q1, q2)
        if intersecao:
            segmentos_intersecao = encontrar_intersecao(p1,p2,q1,q2)
            for segmento_intersecao in segmentos_intersecao:
                if segmento_intersecao not in segmentos:
                    segmentos.append(segmento_intersecao)
                    linestrings.append(LineString(segmento_intersecao))
    else:
        return "Manter"

    segmentos = RemoverRepetidos(segmentos)

    return segmentos


def EstáNaListaLinhas(line1, lines):
    está = False
    for linha in lines:
        intersection = line1.intersection(linha)
        if(intersection.geom_type != 'LineString'):
            None
        elif(intersection.length==0.0):
            None
        else:
            está = True
    
    return está




def intersecta(p1, p2, q1, q2):
    line1 = LineString([p1, p2])
    line2 = LineString([q1, q2])
    return line1.intersects(line2)

def encontrar_intersecao(p1, p2, q1, q2):
    line1 = LineString([p1, p2])
    line2 = LineString([q1, q2])
    intersection = line1.intersection(line2)
    if intersection.is_empty:
        return None
    elif intersection.geom_type == 'Point':
        return None
    elif intersection.geom_type == 'LineString':
        return GerarLadosInterceção(p1, p2, q1, q2)

def GerarLadosInterceção(p1, p2, q1, q2):
    lista_ = [p1, p2, q1, q2]
    ordenada = sorted(lista_, key=lambda x: (x[0], x[1]))
    lados = []
    for i in range(len(ordenada)):
        try:
            lado = [ordenada[i], ordenada[i+1]]
            lados.append(lado)
        except: None

    return lados
    # [(0, 0), (4, 0), (6, 0), (10, 0)]






def EncontrarParedes(paredes):
    paredes_novas = []
    i=0
    for parede1 in paredes:
        j=0
        for parede2 in paredes:
            intercecao = encontrar_segmentos_de_reta(parede1,parede2)
            if(intercecao == "Manter"):
                paredes_novas.extend([parede1])

            elif(intercecao == [] or intercecao == None):
                None
            else:
                paredes_novas.extend(intercecao)
                paredes[i] = ["ignorar"]

            j+=1
        i+=1


    paredes_novas = RemoverRepetidos(paredes_novas)
    paredes_novas = RemoverRepetidos_Parte2(paredes_novas)
    return paredes_novas

def RemoverRepetidos_Parte2(segmentos):
    paredes_novas = []
    ban_list = []
    for segmento in segmentos:
        for segmento_2 in segmentos:
            if([(10.0, 0.0), (10.0, 6.0)] == segmento and ([(10.0, 0.0), (10.0, 10.0)] == segmento_2 or [(10.0, 10.0), (10.0, 0.0)] == segmento_2)):
                None
            line1 = LineString(segmento)
            line2 = LineString(segmento_2)
            relação = DentroOuIntersecta(line1, line2)
            if(relação == "dentro"):
                ban_list.append(segmento_2)

            if([(10.0, 0.0), (10.0, 6.0)] == segmento and ([(10.0, 0.0), (10.0, 10.0)] == segmento_2 or [(10.0, 10.0), (10.0, 0.0)] == segmento_2)):
                None
                


    paredes_novas = []
    for elemento in segmentos:
        if elemento not in ban_list:
            paredes_novas.append(elemento)
    paredes_novas = RemoverRepetidos(paredes_novas)
    return paredes_novas

def DentroOuIntersecta(segmento: LineString, linha_maior: LineString):
    p1 = Point(segmento.coords[0])
    p2 = Point(segmento.coords[-1])
    # Verificando se os estão dentro da linha maior ou ao menos um vertice batendo no vertice da linha maior e outro dentro da linha maior 
    ambos_vertices_contidos = False
    if(p1.within(linha_maior) and p2.within(linha_maior)):
        ambos_vertices_contidos = True
    if(p1 == Point(linha_maior.coords[0]) and p2.within(linha_maior)):
        ambos_vertices_contidos = True
    if(p1 == Point(linha_maior.coords[1]) and p2.within(linha_maior)):
        ambos_vertices_contidos = True   
    if(p2 == Point(linha_maior.coords[0]) and p1.within(linha_maior)):
        ambos_vertices_contidos = True
    if(p2 == Point(linha_maior.coords[1]) and p1.within(linha_maior)):
        ambos_vertices_contidos = True

    if segmento.intersects(linha_maior) and ambos_vertices_contidos:

        return("dentro")

    elif segmento.intersects(linha_maior):
        intercecao = segmento.intersection(linha_maior).geom_type

        if intercecao == 'Point':

            return("apenas ponta")
        else:

            return("intersecta")
    
    else:

        return("fora")

def IdenticoOuNão(segmento: LineString, linha_maior: LineString):
    p1 = Point(segmento.coords[0])
    p2 = Point(segmento.coords[-1])
    # Verificando se os estão dentro da linha maior ou ao menos um vertice batendo no vertice da linha maior e outro dentro da linha maior 

    if(p1 == Point(linha_maior.coords[0]) and p2 == Point(linha_maior.coords[1])):
        return True

    if(p1 == Point(linha_maior.coords[1]) and p2 == Point(linha_maior.coords[0])):
        return True



def RemoverRepetidos(segmentos):
    novos_segmentos = []
    pares = []
    #Remove dois vertices de valores iguais numa parede e paredes identicas de pontos invertidos
    for segmento in segmentos:
        if segmento[0]!=segmento[1] and segmento not in novos_segmentos and segmento not in pares:
            novos_segmentos.append(segmento)
            pares.append( [segmento[0], segmento[1]] )
            pares.append( [segmento[1], segmento[0]] )

    for segmento in novos_segmentos:
        if(segmento ):
            None

    return novos_segmentos




def AutoGerenciamentoParedes(tabela_paredes, tabela_ambientes):
    paredes = []
    for parede in tabela_paredes:
        vertices = parede[2]
        paredes.append(vertices)
    paredes = EncontrarParedes(paredes)

    # aqui temos os lados mais basicos sem divisão carregando os ammbientes que pertecem, será usado para comparar com os lados achados
    lados_fundamentais_poligono = LadosFundamentais(tabela_ambientes)
    tabela_paredes = IdentificarAmbientesParedes(paredes, lados_fundamentais_poligono)

    return tabela_paredes


def IdentificarAmbientesParedes(paredes, lados_fundamentais_poligono):
    tabela_paredes = []
    for parede in paredes:
        parede_line = LineString(parede)
        ambientes = ""
        for i, item in enumerate(lados_fundamentais_poligono):
            lado_poligono_line = LineString(item[1])
            print( "parede: ",str(parede_line) , " lado fundamental: ", str(lado_poligono_line))
            relação = DentroOuIntersecta(parede_line, lado_poligono_line)
            identico = IdenticoOuNão(parede_line, lado_poligono_line)
            if relação == "dentro" or identico == True:

                ambiente = lados_fundamentais_poligono[i][0]
                ambientes+=ambiente + ";"
        ambientes = ambientes[:-1]
        tabela_paredes.append([ambientes, parede])
    return tabela_paredes

# aqui temos os lados mais basicos sem divisão carregando os ammbientes que pertecem, será usado para comparar com os lados achados
def LadosFundamentais(tabela_ambientes):

    tabela_paredes = []
    lados_polig = []
    for item in tabela_ambientes:
        nome_ambiente = item[0]
        vertices = item[5]
        for i_vertice in range(len(vertices)):
            p1 = vertices[i_vertice]
            p2 = vertices[(i_vertice + 1) % len(vertices)]
            parede = [nome_ambiente,[p1,p2]]
            lados_polig.append(parede) 


    return (lados_polig)
        





def exemplo1():

    paredes = [[(0.0, 0.0 ), (0.0, 10.0)], 
           [(0.0, 10.0), (10.0,10.0)], 
           [(10.0,10.0), (10.0, 0.0)],
           [(10.0, 0.0), (0.0,  0.0)],
             

           [(10.0, 5.0), (10.0, 7.0)], 
           [(10.0, 7.0), (20.0, 7.0)], 
           [(20.0, 7.0), (20.0, 5.0)],
           [(20.0, 5.0), (10.0, 5.0)],

           
           [(0.0,10.0),   (5.0,  15.0)],
           [(5.0,15.0),   (10.0, 10.0)],
           [(10.0, 10.0), (0.0,  10.0)]
           ]
    print(EncontrarParedes(paredes))


def exemplo2():
    paredes = [
           [(0.0, 0.0 ), (0.0, 10.0)], 
           [(0.0, 10.0), (10.0,10.0)], 
           [(10.0,10.0), (10.0, 0.0)],
           [(10.0, 0.0), (0.0,  0.0)],
        

           [(10.0,2.0) , (10.0, 6.0)],
           [(10.0,6.0),  (20.0, 6.0)],
           [(20.0,6.0),  (20.0,2.0)],
           [(20.0,2.0),  (10.0,2.0)],

           [(10.0,6.0), (10.0,10.0)],
           [(10.0,10.0), (20.0,10.0)],
           [(20.0,10.0), (20.0,6.0)],
           [(20.0,6.0), (10.0, 6.0)]

            ]
    resultado = EncontrarParedes(paredes)
    print("entrada:")
    for i, item in enumerate(paredes):
        print(f"{i}: {item}")
    print("\nresultado:")
    for i, item in enumerate(resultado):
        print(f"{i}: {item}")
    print("Qntd final de lados: " + str(len(resultado)))


def exemplo3():
    # Definindo os polígonos de entrada
    poligono1 = [(0.0, 0.0), (0.0, 10.0), (10.0,10.0), (10.0,0.0)]
    poligono2 = [(10.0, 5.0), (10.0, 7.0), (20.0,7.0), (20.0,5.0)]
    poligono3 = [(0.0,10.0), (5.0,15.0), (10,10)]

    tabela_paredes = []

    for i in range(len(poligono1)):
        p1 = poligono1[i]
        p2 = poligono1[(i + 1) % len(poligono1)]
        parede = ["ambiente1",0,[p1,p2]]
        tabela_paredes.append(parede) 
    for i in range(len(poligono2)):
        p1 = poligono2[i]
        p2 = poligono2[(i + 1) % len(poligono2)]
        parede = ["ambiente2",0,[p1,p2]]
        tabela_paredes.append(parede) 
    for i in range(len(poligono3)):
        p1 = poligono3[i]
        p2 = poligono3[(i + 1) % len(poligono3)]
        parede = ["ambiente3",0,[p1,p2]]
        tabela_paredes.append(parede) 


    ambiente1 = ["ambiente1", 0,0,0,0,str(poligono1)]
    ambiente2 = ["ambiente2", 0,0,0,0,str(poligono2)]
    ambiente3 = ["ambiente3", 0,0,0,0,str(poligono3)]
    tabela_ambientes = [ambiente1, ambiente2, ambiente3]



    resultado = AutoGerenciamentoParedes(tabela_paredes, tabela_ambientes)
    print("entrada:")
    for i, item in enumerate(tabela_ambientes):
        print(f"{i}: {item}")
    print("\nresultado:")
    for i, item in enumerate(resultado):
        print(f"{i}: {item}")
    print("Qntd final de lados: " + str(len(resultado)))

exemplo3()
