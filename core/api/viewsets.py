from rest_framework import viewsets
from rest_framework import views
from core.api import serializers
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from core import models, formulas
from categorias import models as categorias_models
from pedidos import models as models_pedidos
from payments import models as models_payments


from datetime import datetime

class UsuarioViewSets(views.APIView):
    def post(self, request):
        if not 'user' in request.data:
            return Response(data={'plano_alimentar': False,'erro': 'Você precisa enviar o usuário'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.data['user']
        if not models.Usuario.objects.filter(usuario=user).exists():
            return Response(data={'plano_alimentar': False,'erro': 'Usuário não encontrado'}, status=status.HTTP_400_BAD_REQUEST)

        dados = dict(models.Usuario.objects.filter(usuario=user).values('nome', 'sobrenome','tipo_plano', 'avaliacoes', 'dias_restantes')[0])

        return Response(data=dados, status=status.HTTP_200_OK)
    
class LoginViewSets(views.APIView):

    def post(self, request):
        user=request.data['user']
        senha=request.data['senha']
        usuario_encontrado = models.Usuario.objects.filter(usuario=user).first()
        if usuario_encontrado:
            lista = models.Usuario.objects.get(usuario=user)
            if lista.senha != senha:
                return Response(data={'login': False,'erro': 'Senha incorreta!'}, status=status.HTTP_400_BAD_REQUEST)
            return Response(data={'login': True}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(data={'login': False,'erro': 'Usuário não encontrado'}, status=status.HTTP_400_BAD_REQUEST)

class PlanoAlimentarViewset(views.APIView):

    def put(self, request):
        if not 'user' in request.data:
            return Response(data={'plano_alimentar': False,'erro': 'Você precisa enviar o usuário'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.data['user']
        if not models.Usuario.objects.filter(usuario=user).exists():
            return Response(data={'plano_alimentar': False,'erro': 'Usuário não encontrado'}, status=status.HTTP_400_BAD_REQUEST)

        if not models.PlanoAlimentar.objects.filter(user=user).exists():
            return Response(data={'plano_alimentar': False,'erro': 'Este usuário ainda não realizou nenhuma Avaliação'}, status=status.HTTP_400_BAD_REQUEST)

        usuario_encontrado = models.PlanoAlimentar.objects.filter(user=user).exists()
        if usuario_encontrado:
            if request.data['todos']:
                usuario = models.PlanoAlimentar.objects.filter(user=user)
                serializer = serializers.PlanoAlimentarSerializer(usuario, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                usuario = models.PlanoAlimentar.objects.filter(user=user).last()
                serializer = serializers.PlanoAlimentarSerializer(usuario, many=False)
                return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        #verificando se existe "user" no request
        if not 'user' in request.data:
            return Response(data={'plano_alimentar': False,'erro': 'Você precisa enviar o usuário'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.data['user']

        #verificando se o usuário concluiu seu cadastro
        if not models.Usuario.objects.filter(usuario=user).exists():
            return Response(data={'plano_alimentar': False,'erro': 'Usuário não encontrado', 'categoria': ""}, status=status.HTTP_400_BAD_REQUEST)

        if dict(models.Usuario.objects.filter(usuario=user).values()[0])['dados_pessoais_id'] == None:
            return Response(data={'plano_alimentar': False,'erro': 'O usuário precisa responder todas as questões antes de ter acesso ao plano alimentar.', "categoria": ""}, status=status.HTTP_400_BAD_REQUEST)
        
        sexo = dict(categorias_models.DadosPessoais.objects.filter(user=user).values()[0])["sexo"]
        usuario = dict(models.Usuario.objects.filter(usuario=user).values()[0])
        for k, v in usuario.items():
            if sexo == 'masculino':
                if v == None and (k != 'ciclo_menstrual_id' and k!= "plano_alimentar_id"):
                    categoria_faltante = str(k).split('_')[0]
                    return Response(data={'plano_alimentar': False,'erro': 'O usuário precisa responder todas as questões antes de ter acesso ao plano alimentar.', 'categoria': f"{categoria_faltante}"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if v == None and k!= "plano_alimentar_id":
                    categoria_faltante = str(k).split('_')[0]
                    return Response(data={'plano_alimentar': False,'erro': 'O usuário precisa responder todas as questões antes de ter acesso ao plano alimentar.', 'categoria': f"{categoria_faltante}"}, status=status.HTTP_400_BAD_REQUEST)
        #verificando se o usuário tem avaliações disponíveis
        avaliacoes = dict(models.Usuario.objects.filter(usuario=user).values()[0])['avaliacoes']
        if avaliacoes < 1:
            return Response(data={'plano_alimentar': False,'erro': 'O usuário não possui avaliações restantes', 'categoria': ""}, status=status.HTTP_400_BAD_REQUEST)

        
        ver = formulas.verifica_usuario(user)
        if not ver:
            return Response(data={'plano_alimentar': False,'erro': 'O usuário não possui dias restantes de acesso ao sistema', 'categoria': ""}, status=status.HTTP_400_BAD_REQUEST)
        
        usuario = models.Usuario.objects.get(usuario=user)
        usuario.avaliacoes = avaliacoes - 1
        usuario.save()
        dados_pessoais = dict(categorias_models.DadosPessoais.objects.filter(user=user).values()[0])
        #atribuindo a um dicionário "infos" os dados do usuário pertinentes à fórmula
        dados_antropometricos = dict(categorias_models.Antropometricos.objects.filter(usuario=user).values()[0])
        exercicios = dict(categorias_models.Exercicios.objects.filter(usuario=user).values()[0])
        horarios = dict(categorias_models.Horarios.objects.filter(usuario=user).values()[0])
        infos = {
            'idade': int((datetime.now().date() - dados_pessoais['nascimento']).days // 365.25),
            'sexo': dados_pessoais['sexo'],
            'altura': float(dados_pessoais['altura']),
            'abdomen': float(dados_antropometricos['abdomen']),
            'pulso': float(dados_antropometricos['pulso']),
            'peso': float(dados_antropometricos['peso']),
            'quadril': float(dados_antropometricos['quadril'])
        }
        
        parte = formulas.parte_a(infos['peso'], infos['abdomen'], infos['pulso'], infos['sexo'], infos['quadril'], infos['altura'])
        
        ga = formulas.gordura_atual(infos['peso'], parte, infos['sexo'])
        gi = formulas.gordura_ideal(infos["sexo"], infos['idade'])
        pa = formulas.peso_ajustado(infos['peso'], parte, gi)
        variaveis = list(models.Variaveis.objects.all().values())[0]
        kcal = formulas.calorias_sem_treino(infos['sexo'], infos['altura'], infos['peso'], pa, infos['idade'], variavel_1=variaveis['var_1'], variavel_2=variaveis['var_2'], variavel_3=variaveis['var_3'], variavel_4=variaveis['var_4'], variavel_5=variaveis['var_5'], variavel_6=variaveis['var_6'])
        kcal_simples = kcal
        treino = 'n'
        if float(exercicios['treino']) != 0.0:
            treino = 's'
            kcal = formulas.calorias_com_treino(kcal, float(exercicios['treino']), pa, exercicios['tempo_exercicio'])
            if float(exercicios["treino_secundario"]):
                kcal = formulas.cal_com_treino_duplo(kcal, float(exercicios["treino_secundario"]), pa, exercicios['tempo_exercicio_secundario'])
        #criando o plano alimentar
        plano = {
            'user': user,
            'pescoco': dados_antropometricos['pescoco'],
            'cintura': dados_antropometricos['cintura'],
            'quadril': dados_antropometricos['quadril'],
            'pulso': dados_antropometricos['pulso'],
            'abdomen': dados_antropometricos['abdomen'],
            'peso': dados_antropometricos['peso'],
            'percentual_gordura': ga,
            'gordura_corporal': float(ga/100) * float(dados_antropometricos['peso']),
            'treino': treino,
            'horario_treino': horarios['treino'],
            'café_da_manha': horarios['cafe_da_manha'],
            'almoco': horarios['almoco'],
            'lanche_1': horarios['lanche_manha'],
            'lanche_2': horarios['lanche_tarde_1'],
            'lanche_3': horarios['lanche_tarde_2'],
        }
        plano_alimentar = models.PlanoAlimentar(
            user = plano['user'],
            pescoco = plano['pescoco'],
            cintura = plano['cintura'],
            quadril = plano['quadril'],
            pulso = plano['pulso'],
            abdomen = plano['abdomen'],
            peso = plano['peso'],
            percentual_gordura = plano['percentual_gordura'],
            gordura_corporal = plano['gordura_corporal'],
            treino = plano['treino'],
            horario_treino = plano['horario_treino'],
            café_da_manha = plano['café_da_manha'],
            almoco = plano['almoco'],
            data_realizacao= datetime.now(),
            kcal= (kcal//100)*100,
            kcal_simples=(kcal_simples//100)*100,
            lanche_1 = horarios['lanche_manha'],
            lanche_2 = horarios['lanche_tarde_1'],
            lanche_3 = horarios['lanche_tarde_2'],
            horario_janta = horarios["jantar"]
        )
        plano_alimentar.save()
        return Response(data={'plano_alimentar': True, "erro": "", "categoria": ""}, status=status.HTTP_201_CREATED)

class MaterialApoioViewSet(views.APIView):

    def put(self, request):
        user = request.data['user']
        ver = formulas.verifica_usuario(user)
        if not ver:
            return Response(data={'erro': 'O usuário não possui dias restantes de acesso ao sistema'}, status=status.HTTP_400_BAD_REQUEST)
        
        mats = models.MaterialDeApoio.objects.all()
        serializer = serializers.MaterialApoioSerializer(mats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CalculadoraViewSet(views.APIView):
    def put(self, request):

        #verificações
        if request.data["sexo"] != "masculino" and request.data["sexo"] != "feminino":
            return Response(data={'sexo': 'valor deve ser "masculino" ou "feminino".'}, status=status.HTTP_400_BAD_REQUEST)
        if isinstance(request.data["peso"], str):
            return Response(data={'peso': 'deve ser int ou float'}, status=status.HTTP_400_BAD_REQUEST)
        if isinstance(request.data["abdomen"], str):
            return Response(data={'abdomen': 'deve ser int ou float'}, status=status.HTTP_400_BAD_REQUEST)
        if isinstance(request.data["punho"], str):
            return Response(data={'punho': 'deve ser int ou float'}, status=status.HTTP_400_BAD_REQUEST)
        if isinstance(request.data["altura"], str) or isinstance(request.data["altura"], float):
            return Response(data={'altura': 'deve ser int'}, status=status.HTTP_400_BAD_REQUEST)
        if isinstance(request.data["quadril"], str):
            return Response(data={'quadril': 'deve ser int ou float'}, status=status.HTTP_400_BAD_REQUEST)
        if isinstance(request.data["idade"], str):
            return Response(data={'idade': 'deve ser int'}, status=status.HTTP_400_BAD_REQUEST)


        #pegando valores post
        sexo = request.data["sexo"]
        peso = float(request.data["peso"])
        abdomen = float(request.data["abdomen"])
        punho = float(request.data["punho"])
        altura = float(request.data["altura"])
        quadril = float(request.data["quadril"])
        idade = int(request.data["idade"])

        parte = formulas.parte_a(peso, abdomen, punho, sexo, quadril, altura)
        ga = round(formulas.gordura_atual(peso, parte, sexo), 1)
        #calcular massa_magra_real (peso - (peso * percentual_gordura_atual))
        MM_real = round(peso - (peso * ga/100), 1)
        #pegar gordura ideal
        gordura_i = formulas.gordura_ideal(sexo, idade)
        print(gordura_i)
        
        fator_multiplicação = 1 + gordura_i/100
        peso_ideal = round(MM_real *fator_multiplicação, 1)
        peso_gordura_ideal =  round(peso_ideal - MM_real, 1)

        #gordura e peso perfeitos
        gordura_p = formulas.gordura_perfeita(sexo, idade)
        fator_multiplicação = 1 + gordura_p/100
        peso_perfeito = round(MM_real *fator_multiplicação, 1)
        peso_gordura_perfeita =  round(peso_perfeito - MM_real, 1)
        context = {
            "percentual_gordura_atual": ga,
            "peso_atual": peso,
            "peso_ideal": peso_ideal,
            "peso_perfeito": peso_perfeito,
            "MM_real": MM_real,
            "peso_gordura_real": round(peso - MM_real, 1),
            "peso_gordura_ideal":round((gordura_i*MM_real)/(100-gordura_i),1),
            "peso_gordura_perfeita": round((gordura_p*MM_real)/(100-gordura_p),1),
            "gordura_ideal": gordura_i,
            "gordura_perfeita": gordura_p,
            "perder_bom": round(round(peso - MM_real, 1) - round((gordura_i*MM_real)/(100-gordura_i),1), 2),
            "perder_perfeito": round(round(peso - MM_real, 1) - round((gordura_p*MM_real)/(100-gordura_p),1), 2)
        }
        return Response(data=context, status=status.HTTP_200_OK)

class PlanosOferecidosViewSet(views.APIView):
    def put(self, request):
        pacs = models_pedidos.PacoteDeVenda.objects.filter().exclude(id=1)
        serializer = serializers.PacoteDeVendaSerializer(pacs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CriaPedidoViewSet(views.APIView):
    def post(self, request):
        serializer = serializers.CriaPedidoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            id = models_pedidos.Pedidos.objects.filter().first().id
            return  Response(data={'created': True, "id_pedido": id}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CriaPaymentViewSet(views.APIView):
    def post(self, request):
        serializer = serializers.CriaPaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            id = models_payments.Payments.objects.filter().first().id
            return  Response(data={'created': True, "id_pedido": id}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RelatorioEvolucao(views.APIView):
    def put(self, request):
        user = request.data["user"]
        if not categorias_models.DadosPessoais.objects.filter(usuario=user).exists():
            return Response({'erro': 'Usuário com esse nome de usuário não existe.'}, status=status.HTTP_400_BAD_REQUEST)

        #verificando se o usuário concluiu seu cadastro
        sexo = dict(categorias_models.DadosPessoais.objects.filter(user=user).values()[0])["sexo"]
        altura = dict(categorias_models.DadosPessoais.objects.filter(user=user).values()[0])["altura"]
        idade = int((datetime.now().date() - dict(categorias_models.DadosPessoais.objects.filter(user=user).values()[0])["nascimento"]).days // 365.25)
        usuario = dict(models.Usuario.objects.filter(usuario=user).values()[0])
        for k, v in usuario.items():
            if sexo == 'masculino':
                if v == None and k != 'ciclo_menstrual_id':
                    categoria_faltante = str(k).split('_')[0]
                    return Response({'erro': 'Usuário ainda não preencheu todo o questionário.'}, status=status.HTTP_400_BAD_REQUEST)

            else:
                if v == None:
                    categoria_faltante = str(k).split('_')[0]
                    return Response({'erro': 'Usuário ainda não preencheu todo o questionário.'}, status=status.HTTP_400_BAD_REQUEST)


    
        
        ver = formulas.verifica_usuario(user)
        if not ver:
            return Response({'erro': 'Usuário não possui mais permissão para acessar o sistema'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            pass

        usuario = dict(models.Usuario.objects.filter(usuario=user).values()[0])

        planos = list(models.PlanoAlimentar.objects.filter(user=user).values().order_by("data_realizacao"))[:6]
        if len(planos) <2:
            return Response({'erro': 'Usuário precisa ter feito ao menos duas avaliações para poder acessar A evolução'}, status=status.HTTP_400_BAD_REQUEST)

        datas_lista = [plano['data_realizacao'].strftime('%d/%m/%Y') for plano in planos]
        datas_planos = {}
        for i in range(len(datas_lista)):
            datas_planos[f'data_{i+1}'] = datas_lista[i]
        consultas = {}
        riscos = {}
        i = 1
        for plano in planos:
            ### Consultas ###
            consultas[f'peso_{i}'] = round(plano['peso'], 2 if len(str(plano['peso']).split('.')[0])< 3 else 1)
            consultas[f'per_gordura_{i}'] = round(plano['percentual_gordura'], 1)
            consultas[f'massa_magra_{i}'] = round(float(plano['peso']) - float(plano['gordura_corporal']), 1)
            consultas[f'peso_gordura_{i}'] = round(plano['gordura_corporal'],2 if len(str(plano['gordura_corporal']).split('.')[0])<2 else 1)
            consultas[f'cintura_{i}'] = round(plano['cintura'], 2 if len(str(plano['cintura']).split('.')[0])<3 else 1)
            consultas[f'abdomen_{i}'] = round(plano['abdomen'], 2 if len(str(plano['abdomen']).split('.')[0])<3 else 1)
            consultas[f'quadril_{i}'] = round(plano['quadril'], 2 if len(str(plano['quadril']).split('.')[0])<3 else 1)
            

            ### Riscos ###
            riscos[f'quadril_{i}'] = formulas.calcula_quadril(sexo, float(plano['quadril']), float(altura))
            riscos[f'cintura_{i}'] = formulas.calcula_cintura(altura, plano['cintura'])
            riscos[f'abdomen_{i}'] = formulas.calcula_abdomen(sexo, plano['abdomen'])
            riscos[f'cintura_quadril_{i}'] = formulas.cintura_quadril(sexo,idade, float(plano['quadril']), float(altura))

            i+=1
        
        #Pegando Kcal
        ultimo_plano = planos[-1]


        #Comparação 2 últimos planos
        ultimos = planos[-2:]
        datas = {}
        i = 1
        for plano in ultimos:
            datas[f'data_{i}'] = plano['data_realizacao'].strftime('%d/%m/%Y')
            i+=1


        kcals = {}
        #pegando os valores caloricos
        parte = formulas.parte_a(planos[-1]['peso'], planos[-1]['abdomen'], planos[-1]['pulso'], sexo, planos[-1]['quadril'], altura)
        gi = formulas.gordura_ideal(sexo, idade)
        pa = formulas.peso_ajustado(planos[-1]['peso'], parte, gi)
        kcals['kcal_1'] = int(((pa*30)//100)*100)
        kcals['kcal_2'] = int(planos[-1]['kcal'])
        mes_realizacao = int(planos[-1]['data_realizacao'].strftime('%m'))
        meses = {
            1: 'JANEIRO',
            2: 'FEVEREIRO',
            3: 'MARÇO',
            4: 'ABRIL',
            5: 'MAIO',
            6: 'JUNHO',
            7: 'JULHO',
            8: 'AGOSTO',
            9: 'SETEMBRO',
            10: 'OUTUBRO',
            11: 'NOVEMBRO',
            12: 'DEZEMBRO',
        }
        kcals['mes'] = meses[mes_realizacao]
        #Pegando as diferenças
        diferencas = {}

        #diferenca de peso
        diferenca_peso = float(planos[-1]['peso']) - float(planos[-2]['peso'])
        diferenca_peso = round(diferenca_peso, 2 if len(str(diferenca_peso).split('.')[0]) < 2 else 1)
        if diferenca_peso == 0:
            diferenca_peso_estado = 'MANUTENCAO'
        elif 0 < diferenca_peso < 5:
            diferenca_peso_estado = 'LEVE AUMENTO'
        elif diferenca_peso >= 5:
            diferenca_peso_estado = 'GRANDE AUMENTO'
        elif -5 < diferenca_peso < 0:
            diferenca_peso_estado = 'LEVE DIMINUICAO'
        elif diferenca_peso <= -5:
            diferenca_peso_estado = 'GRANDE DIMINUICAO'
        diferenca_peso = str(diferenca_peso) if diferenca_peso >= 0 else f'-{str(diferenca_peso)}'
        diferencas['peso'] = diferenca_peso
        diferencas['peso_descricao'] = diferenca_peso_estado


        #diferenca de % gordura
        diferenca_percentual_gordura = float(planos[-1]['percentual_gordura']) - float(planos[-2]['percentual_gordura'])
        diferenca_percentual_gordura = round(diferenca_percentual_gordura, 2 if len(str(diferenca_percentual_gordura).split('.')[0]) < 2 else 1)
        if diferenca_percentual_gordura == 0:
            diferenca_percentual_gordura_estado = 'MANUTENCAO'
        elif 0 < diferenca_percentual_gordura < 0.1:
            diferenca_percentual_gordura_estado = 'LEVE AUMENTO'
        elif diferenca_percentual_gordura >= 0.1:
            diferenca_percentual_gordura_estado = 'AUMENTO'
        elif -0.1 < diferenca_percentual_gordura < 0:
            diferenca_percentual_gordura_estado = 'LEVE DIMINUICAO'
        elif diferenca_percentual_gordura < -0.1:
            diferenca_percentual_gordura_estado = 'DIMINUICAO'
        diferenca_percentual_gordura = str(diferenca_percentual_gordura) if diferenca_percentual_gordura >= 0 else f'-{str(diferenca_percentual_gordura)}'
        diferencas['percentual_gordura'] = diferenca_percentual_gordura
        diferencas['percentual_gordura_descricao'] = diferenca_percentual_gordura_estado

        #diferenca de peso da gordura
        diferenca_peso_gordura = float(planos[-1]['gordura_corporal']) - float(planos[-2]['gordura_corporal'])
        diferenca_peso_gordura = round(diferenca_peso_gordura, 2 if len(str(diferenca_peso_gordura).split('.')[0]) < 2 else 1)
        if diferenca_peso_gordura == 0:
            diferenca_peso_gordura_estado = 'MANUTENCAO'
        elif 0 < diferenca_peso_gordura < 0.1:
            diferenca_peso_gordura_estado = 'LEVE AUMENTO'
        elif diferenca_peso_gordura >= 0.1:
            diferenca_peso_gordura_estado = 'AUMENTO'
        elif -0.1 <= diferenca_peso_gordura < 0:
            diferenca_peso_gordura_estado = 'LEVE DIMINUICAO'
        elif diferenca_peso_gordura < -0.1:
            diferenca_peso_gordura_estado = 'DIMINUICAO'
        diferenca_peso_gordura = str(diferenca_peso_gordura) if diferenca_peso_gordura >= 0 else f'-{str(diferenca_peso_gordura)}'
        diferencas['peso_gordura'] = diferenca_peso_gordura
        diferencas['peso_gordura_descricao'] = diferenca_peso_gordura_estado


        #diferenca de Massa Magra
        diferenca_MM = (float(planos[-1]['peso']) - float(planos[-1 ]['gordura_corporal'])) - (float(planos[-2]['peso']) - float(planos[-2]['gordura_corporal']))
        diferenca_MM = round(diferenca_MM, 2 if len(str(diferenca_MM).split('.')[0]) < 2 else 1)
        if diferenca_MM == 0:
            diferenca_MM_estado = 'MANUTENCAO'
        elif 0 < diferenca_MM <= 0.1:
            diferenca_MM_estado = 'LEVE AUMENTO'
        elif diferenca_MM > 0.1:
            diferenca_MM_estado = 'AUMENTO'
        elif -0.1 <= diferenca_MM < 0:
            diferenca_MM_estado = 'LEVE DIMINUICAO'
        elif diferenca_MM < -0.1:
            diferenca_MM_estado = 'DIMINUICAO'
        diferenca_MM = str(diferenca_MM) if diferenca_MM >= 0 else f'-{str(diferenca_MM)}'
        diferencas['peso_MM'] = diferenca_MM
        diferencas['peso_MM_descricao'] = diferenca_MM_estado


        #Pegando a meta de evolução
        per_gordura_inicial = round(float(planos[-2]['percentual_gordura']), 2 if len(str(planos[-2]['percentual_gordura']).split('.')[0]) <2 else 1)
        per_gordura_atual = round(float(planos[-1]['percentual_gordura']), 2 if len(str(planos[-2]['percentual_gordura']).split('.')[0]) <2 else 1)
        per_gordura_meta = formulas.gordura_ideal(sexo, idade)

        valores = {
            'meta_1': per_gordura_inicial,
            'meta_1_estado': 'OK'
        }
        i = 2
        for _ in range(65):
            if per_gordura_inicial >= per_gordura_meta:
                per_gordura_inicial -= 0.3
                valores[f'meta_{i}'] = round(per_gordura_inicial, 2 if len(str(per_gordura_inicial).split('.')[0]) < 2 else 1)
                if per_gordura_atual <= per_gordura_inicial:
                    valores[f'meta_{i}_estado'] = 'OK'
                else:
                    valores[f'meta_{i}_estado'] = '__'
            else:
                valores[f'meta_{i}'] = '____'
                valores[f'meta_{i}_estado'] = '__'
            i+=1
        print(datas_planos)

        context = {
            "nome_pessoa": usuario["nome"],
            "sobrenome_pessoa": usuario["sobrenome"],
            'datas_planos': datas_planos,
            'consultas': consultas,
            'riscos': riscos,
            'datas': datas,
            'diferencas': diferencas,
            'valores': valores,
            'kcals': kcals
        }
        return Response(context, status=status.HTTP_200_OK)
