from django.shortcuts import render, redirect
from empresarios.models import Empresas, Documento
from .models import PropostaInvestimento
from django.contrib import messages
from django.contrib.messages import constants
from django.http import Http404

def sugestao(request):
    if not request.user.is_authenticated:  
        print("Usuário não autenticado")
        return redirect('/usuarios/logar')
    print(f"Usuário autenticado: {request.user}")  # print para ver as logs pelo terminal
    areas = Empresas.area_choices
    if request.method == "GET":   
        return render(request, 'sugestao.html', {'areas': areas})
    elif request.method == "POST":
        tipo = request.POST.get('tipo')
        area = request.POST.getlist('area')  # "getlist" ao inves de "get" porque é um formulário de múltiplas escolhas
        valor = request.POST.get('valor')

        if tipo == 'C':
            empresas = Empresas.objects.filter(tempo_existencia='+5').filter(estagio="E")
        elif tipo == 'D':
            empresas = Empresas.objects.filter(tempo_existencia__in=['-6', '+6', '+1']).exclude(estagio="E")
        # TODO: criar um tipo genérico (ou mediano) para empresas que não atendem nenhuma das duas opções
        
        empresas = empresas.filter(area__in=area)
        
        # o user precisa comprar no mínimo 1% do valor total da empresa
        empresas_selecionadas = []
        for empresa in empresas:
            percentual = (float(valor) * 100) / float(empresa.valuation)
            if percentual >= 1:
                empresas_selecionadas.append(empresa)

        return render(request, 'sugestao.html', {'empresas': empresas_selecionadas, 'areas': areas})

def ver_empresa(request, id):
    empresa = Empresas.objects.get(id=id)  # seleciona a empresa com o id que o usuário clicou
    documentos = Documento.objects.filter(empresa=empresa)  # traz os documentos da empresa

    # percentual vendido da empresa:
    proposta_investimentos = PropostaInvestimento.objects.filter(empresa=empresa).filter(status='PA')
    percentual_vendido = 0
    for pi in proposta_investimentos:
        percentual_vendido += pi.percentual   

    # Calcula se o percentual vendido é superior a 80%:
    limiar = (80 * empresa.percentual_equity) / 100
    concretizado = False
    if percentual_vendido >= limiar:
        concretizado = True
        print(f"Concretizado foi setado para: {concretizado}") 

    percentual_disponivel = empresa.percentual_equity - percentual_vendido    

    # TODO: Listar as métricas dinamicamente (indicadores - cac)
    return render(request, 'ver_empresa.html', {'empresa': empresa, 'documentos': documentos, 'percentual_vendido': int(percentual_vendido), 'concretizado': concretizado, 'percentual_disponivel': percentual_disponivel})


def realizar_proposta(request, id):
    valor = request.POST.get('valor')
    percentual = request.POST.get('percentual')
    empresa = Empresas.objects.get(id=id)

    propostas_aceitas = PropostaInvestimento.objects.filter(empresa=empresa).filter(status='PA')  # empresas com propostas aceitas
    total = 0

    for pa in propostas_aceitas:
        total = total + pa.percentual

    if total + float(percentual)  > empresa.percentual_equity:
        messages.add_message(request, constants.ERROR, 'O percentual solicitado ultrapassa o percentual máximo.')
        return redirect(f'/investidores/ver_empresa/{id}')


    valuation = (100 * int(valor)) / int(percentual)

    if valuation < (int(empresa.valuation) / 2):
        messages.add_message(request, constants.ERROR, f'Seu valuation proposto foi R${valuation} e deve ser no mínimo R${empresa.valuation/2}')
        return redirect(f'/investidores/ver_empresa/{id}')

    pi = PropostaInvestimento(
        valor = valor,
        percentual = percentual,
        empresa = empresa,
        investidor = request.user,
    )

    pi.save()

    #messages.add_message(request, constants.SUCCESS, f'Proposta enviada com sucesso')
    return redirect(f'/investidores/assinar_contrato/{pi.id}')

def assinar_contrato(request, id):
    pi = PropostaInvestimento.objects.get(id=id)
    if pi.status != "AS":
        raise Http404()
    
    if request.method == "GET":
        return render(request, 'assinar_contrato.html', {'pi': pi})
    elif request.method == "POST":
        selfie = request.FILES.get('selfie')
        rg = request.FILES.get('rg')
        print(request.FILES)
        

        pi.selfie = selfie
        pi.rg = rg
        pi.status = 'PE'
        pi.save()

        messages.add_message(request, constants.SUCCESS, f'Contrato assinado com sucesso, sua proposta foi enviada a empresa.')
        return redirect(f'/investidores/ver_empresa/{pi.empresa.id}')