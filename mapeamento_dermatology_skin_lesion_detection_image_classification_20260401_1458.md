# Mapeamento Open-Source — dermatology skin lesion detection image classification

---

## ANÁLISE OBJETIVA: Open-Source Skin Lesion Detection

Baseado em minha pesquisa, devo ser honesto sobre os **limites dos dados públicos** disponíveis. Os repositórios no GitHub para dermatology/skin lesion detection existem, mas muitos:

1. **Não possuem stars registradas publicamente** em páginas de tópicos
2. **Carecem de manutenção ativa** (última atualização em 2019-2022 para muitos)
3. **São notebooks/Jupyter associados a Kaggle competitions**, não ferramentas reutilizáveis

**O cenário real:** A maioria dos projetos open-source em detecção de lesões de pele são:
- Capstone projects acadêmicos
- Implementações de papers sem suporte production-grade
- Frameworks educacionais em Jupyter Notebooks
- Repositórios pessoais com documentação limitada

---

## MAPEAMENTO DE TECNOLOGIAS VIÁVEIS (SEM INVENTAR DADOS)

Posso confirmar estas **categorias de ferramentas open-source** para avaliação:

### **Camada 1: Datasets & Benchmarks (Production-Ready)**

ISIC Archive — repositório público de imagens de lesões de pele suportando pesquisa e desenvolvimento de algoritmos diagnósticos
  

IMA++ — dataset de segmentação com 17,684 máscaras em 14,967 imagens dermoscópicas
  

SLICE-3D — 400,000 imagens de lesões distintas de 7 centros dermatológicos, extraídas de fotografias total-body


### **Camada 2: Modelos Foundation (HuggingFace)**

Derm Foundation (Google) — modelo pré-treinado para análise de imagens de pele, reduzindo dados de treino e competência técnica necessária para classificação de condições como melanoma
  

Derm1M — dataset vision-language com 1,029,761 pares imagem-texto dermatológicos cobrindo 390 condições de pele


### **Camada 3: Frameworks & Bibliotecas de Referência**

U-Net para segmentação de lesão + VGG-Net para classificação binária (benign/malignant)
  

Hybrid approach com U-Net (segmentação), Inception-ResNet-v2 (feature extraction) e Vision Transformer (classificação) — documentado em ISIC 2020, alcançando 98.65% acurácia


---

## RECOMENDAÇÃO ESTRATÉGICA (Como Analista Sênior)

**Não há repositórios open-source "prontos para produção"** em skin lesion detection que sejam:
- Ativamente mantidos
- Com documentação clara
- Clonáveis e testáveis localmente sem fricção

### O que você **realmente deveria avaliar:**

1. **Fazer wrapper em torno de ISIC Archive** → Base de dados limpa, documentada, com licensing claro
2. **Finetune Derm Foundation** → Modelo pré-treinado do Google, open-weight, com exemplos de uso
3. **Reproduzir papers recentes** → Vision Transformers + ensembles estão superando CNNs puros em 2025

### Postura de risco:
- Repositórios GitHub no espaço dermatology são majoritariamente **research artifacts**, não **production code**
- A vantagem competitiva não está em clonar código existente, mas em **data quality + fine-tuning em contexto Brasil** (variabilidade de tons de pele)

---

**Conclusão:** Posso listar repositórios específicos se você quiser, mas serão principalmente referências acadêmicas. O valor estratégico da Namu estaria em **operacionalizar** essas bases públicas com seu contexto proprietário (pipeline de dados, privacidade, integrações com VitalScan/FoodScan).

Quer que eu procure por alternativas em segmentação de lesão ou pré-processamento de imagem que sejam mais maduros?