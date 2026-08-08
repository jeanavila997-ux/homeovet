#!/usr/bin/env python3
"""Testes automatizados do agente homeopático."""

import sys
sys.path.insert(0, '.')

from agente_homeopatico import carregar_remedios, buscar_remedios, similaridade

def teste_carregar_dados():
    print("=== TESTE 1: Carregar base de dados ===")
    remedios = carregar_remedios()
    print(f"Remédios carregados: {len(remedios)}")
    assert len(remedios) == 24, f"Esperado 24 remédios, encontrado {len(remedios)}"
    print("OK! Base carregada com sucesso.\n")
    return remedios

def teste_similaridade():
    print("=== TESTE 2: Similaridade de texto ===")
    s1 = similaridade('dor de cabeca', 'dor de cabeca')
    s2 = similaridade('nausea', 'nausea')
    s3 = similaridade('ansiedade', 'depressao')
    print(f"  dor de cabeca vs dor de cabeca: {s1:.2f}")
    print(f"  nausea vs nausea: {s2:.2f}")
    print(f"  ansiedade vs depressao: {s3:.2f}")
    assert s1 > 0.9, "Similaridade alta esperada"
    print("OK! Similaridade funcionando.\n")

def teste_busca_ansiedade(remedios):
    print("=== TESTE 3: Busca por sintomas - Ansiedade ===")
    resultados = buscar_remedios(remedios, 'ansiedade nervosismo', top_n=3)
    print(f"Resultados: {len(resultados)}")
    for r in resultados:
        print(f"  - {r['nome']} (score: {r['score_busca']:.2f})")
    assert len(resultados) > 0, "Deve encontrar resultados"
    print("OK! Busca funcionando.\n")

def teste_busca_trauma(remedios):
    print("=== TESTE 4: Busca por trauma/contusao ===")
    resultados = buscar_remedios(remedios, 'contusao hematoma dor muscular', top_n=3)
    for r in resultados:
        print(f"  - {r['nome']} (score: {r['score_busca']:.2f})")
    assert len(resultados) > 0
    assert resultados[0]['nome'] == 'Arnica Montana', "Arnica deve ser top 1 para trauma"
    print("OK!\n")

def teste_busca_ginecologica(remedios):
    print("=== TESTE 5: Busca ginecologica ===")
    resultados = buscar_remedios(remedios, 'menopausa calorao irritabilidade', top_n=3)
    for r in resultados:
        print(f"  - {r['nome']} (score: {r['score_busca']:.2f})")
    assert len(resultados) > 0
    print("OK!\n")

def teste_busca_digestivo(remedios):
    print("=== TESTE 6: Busca digestiva ===")
    resultados = buscar_remedios(remedios, 'azia indigestao gases', top_n=3)
    for r in resultados:
        print(f"  - {r['nome']} (score: {r['score_busca']:.2f})")
    assert len(resultados) > 0
    print("OK!\n")

def teste_busca_respiratorio(remedios):
    print("=== TESTE 7: Busca respiratoria ===")
    resultados = buscar_remedios(remedios, 'tosse seca gripe', top_n=3)
    for r in resultados:
        print(f"  - {r['nome']} (score: {r['score_busca']:.2f})")
    assert len(resultados) > 0
    print("OK!\n")

if __name__ == "__main__":
    remedios = teste_carregar_dados()
    teste_similaridade()
    teste_busca_ansiedade(remedios)
    teste_busca_trauma(remedios)
    teste_busca_ginecologica(remedios)
    teste_busca_digestivo(remedios)
    teste_busca_respiratorio(remedios)
    print("=" * 50)
    print("🎉 TODOS OS TESTES PASSARAM COM SUCESSO!")
    print("=" * 50)
