from django.shortcuts import render, redirect
from .models import Empresas, Documento, Metricas
from django.contrib import messages
from django.contrib.messages import constants
from investidores.models import PropostaInvestimento
from django.utils import timezone
from datetime import timedelta

def cadastrar_empresa(request):
    # Validação de segurança (importante!!!): o usuário só pode acessar a url cadastrar_empresa se ele estiver logado, se não ele é redirecionado à pág de login
    # Validação de segurança
    if not request.user.is_authenticated:  
        print("Usuário não autenticado")
        return redirect('/usuarios/logar')
    print(f"Usuário autenticado: {request.user}")

    if request.method == "GET":
        return render(request, 'cadastrar_empresa.html', {'tempo_existencia': Empresas.tempo_existencia_choices, 'areas': Empresas.area_choices })
    elif request.method == "POST":
        nome = request.POST.get('nome')
        cnpj = request.POST.get('cnpj')
        site = request.POST.get('site')
        tempo_existencia = request.POST.get('tempo_existencia')
        descricao = request.POST.get('descricao')
        data_final = request.POST.get('data_final')
        percentual_equity = request.POST.get('percentual_equity')
        estagio = request.POST.get('estagio')
        area = request.POST.get('area')
        publico_alvo = request.POST.get('publico_alvo')
        valor = request.POST.get('valor')
        pitch = request.FILES.get('pitch')
        logo = request.FILES.get('logo')

        # validação de campos (ver se o usuario preencheu todos os campos corretamente)

        # Validação dos campos
        if not all([nome, cnpj, site, tempo_existencia, descricao, data_final, percentual_equity, estagio, area, publico_alvo, valor, pitch, logo]):
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
            return redirect('/empresarios/cadastrar_empresa')

        try:
            empresa = Empresas(
                user=request.user,
                nome=nome,
                cnpj=cnpj,
                site=site,
                tempo_existencia=tempo_existencia,
                descricao=descricao,
                data_final_captacao=data_final,
                percentual_equity=percentual_equity,
                estagio=estagio,
                area=area,
                publico_alvo=publico_alvo,
                valor=valor,
                pitch=pitch,
                logo=logo
            )
            empresa.save()
        except Exception as error:
            messages.add_message(request, constants.ERROR, 'Erro interno do sistema')
            print(error)
            return redirect('/empresarios/cadastrar_empresa')
        
        messages.add_message(request, constants.SUCCESS, 'Empresa criada com sucesso')
        return redirect('/empresarios/cadastrar_empresa')


def listar_empresas(request):
    # Validação de segurança
    if not request.user.is_authenticated:  
        print("Usuário não autenticado")
        return redirect('/usuarios/logar')
    print(f"Usuário autenticado: {request.user}")  # print para ver as logs pelo terminal

    if request.method == "GET":
        # filtros das empresas
        empresa_query = request.GET.get('empresa', '')  # verifica se foi feito um filtro de pesquisa
        if empresa_query:  # se foi, as empresas do usuário que contém os caracteres digitados são mostradas
            empresas = Empresas.objects.filter(user=request.user, nome__icontains=empresa_query)
        else:
            empresas = Empresas.objects.filter(user=request.user)  # mostra apenas as empresas do usuário logado, sem filtro de pesquisa
        
        return render(request, 'listar_empresas.html', {'empresas': empresas, 'empresa_query': empresa_query})


def empresa(request, id):
    # Validação de segurança
    if not request.user.is_authenticated:  
        print("Usuário não autenticado")
        return redirect('/usuarios/logar')
    print(f"Usuário autenticado: {request.user}")

    empresa = Empresas.objects.get(id=id)  # seleciona a empresa correspondente ao id

    if empresa.user != request.user:
        messages.add_message(request, constants.ERROR, "Você não pode acessar outras empresas sem autorização")
        return redirect(f'/empresarios/listar_empresas')

    if request.method == "GET":
        documentos = Documento.objects.filter(empresa=empresa)
        proposta_investimentos = PropostaInvestimento.objects.filter(empresa=empresa)

        # percentual vendido da empresa
        percentual_vendido = 0
        for pi in proposta_investimentos:
            if pi.status == 'PA':  # propostas aceitas
                percentual_vendido += pi.percentual

        # total em reais que já foi captado de todas as propostas aceitas
        total_captado = sum(proposta_investimentos.filter(status='PA').values_list('valor', flat=True))

        # valuation atual
        valuation_atual = (100 * float(total_captado)) / float(percentual_vendido) if percentual_vendido != 0 else 0

        proposta_investimentos_enviada = proposta_investimentos.filter(status='PE')
        print(f"Propostas de investimentos atuais: {proposta_investimentos_enviada.count()}")
        return render(request, 'empresa.html', {'empresa': empresa, 'documentos': documentos, 'proposta_investimentos_enviada': proposta_investimentos_enviada, 
                                                'percentual_vendido': int(percentual_vendido), 'total_captado': total_captado, 'valuation_atual': valuation_atual})


def add_doc(request, id):
    # Validação de segurança
    if not request.user.is_authenticated:  
        print("Usuário não autenticado")
        return redirect('/usuarios/logar')
    print(f"Usuário autenticado: {request.user}")

    empresa = Empresas.objects.get(id=id)
    titulo = request.POST.get('titulo')
    arquivo = request.FILES.get('arquivo')
    extensao = arquivo.name.split('.')

    #garante que o usuário não altere o id da empresa para enviar documentos para outra empresa
    if empresa.user != request.user:
        messages.add_message(request, constants.ERROR, "Você não pode acessar outras empresas sem autorização")
        return redirect(f'/empresarios/listar_empresas')

    # garante o envio apenas de pdfs
    if extensao[1] != 'pdf':
        messages.add_message(request, constants.ERROR, "Envie apenas PDF's")
        return redirect(f'/empresarios/empresa/{empresa.id}')
    
    if not arquivo:
        messages.add_message(request, constants.ERROR, "Envie um arquivo")
        return redirect(f'/empresarios/empresa/{empresa.id}')
        
    documento = Documento(
        empresa=empresa,
        titulo=titulo,
        arquivo=arquivo
    )
    documento.save()
    messages.add_message(request, constants.SUCCESS, "Arquivo cadastrado com sucesso")
    return redirect(f'/empresarios/empresa/{empresa.id}')
    

def excluir_dc(request, id):
    # Validação de segurança
    if not request.user.is_authenticated:  
        print("Usuário não autenticado")
        return redirect('/usuarios/logar')
    print(f"Usuário autenticado: {request.user}")

    documento = Documento.objects.get(id=id)
    if documento.empresa.user != request.user:
        messages.add_message(request, constants.ERROR, "Esse documento não é seu")
        return redirect(f'/empresarios/empresa/{empresa.id}')
    
    documento.delete()
    messages.add_message(request, constants.SUCCESS, "Documento excluído com sucesso")
    return redirect(f'/empresarios/empresa/{documento.empresa.id}')


def add_metrica(request, id):
    # Validação de segurança
    if not request.user.is_authenticated:  
        print("Usuário não autenticado")
        return redirect('/usuarios/logar')
    print(f"Usuário autenticado: {request.user}")

    empresa = Empresas.objects.get(id=id)
    titulo = request.POST.get('titulo')
    valor = request.POST.get('valor')
    
    metrica = Metricas(
        empresa=empresa,
        titulo=titulo,
        valor=valor
    )
    metrica.save()

    messages.add_message(request, constants.SUCCESS, "Métrica cadastrada com sucesso")
    return redirect(f'/empresarios/empresa/{empresa.id}')


def gerenciar_proposta(request, id):
    # Validação de segurança
    if not request.user.is_authenticated:  
        print("Usuário não autenticado")
        return redirect('/usuarios/logar')
    print(f"Usuário autenticado: {request.user}")

    acao = request.GET.get('acao')
    pi = PropostaInvestimento.objects.get(id=id)

    if acao == 'aceitar':
        messages.add_message(request, constants.SUCCESS, 'Proposta aceita')
        pi.status = 'PA'
    elif acao == 'recusar':
        messages.add_message(request, constants.SUCCESS, 'Proposta recusada')
        pi.status = 'PR'


    pi.save()
    return redirect(f'/empresarios/empresa/{pi.empresa.id}')
