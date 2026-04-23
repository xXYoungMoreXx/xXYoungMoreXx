# 🤝 Guia de Contribuição — Aethoria RPG Portfolio

Obrigado por seu interesse em contribuir com o Aethoria! Este é um projeto pessoal de portfólio, mas contribuições são bem-vindas.

## Como Contribuir

### 🐛 Reportar Bugs
1. Verifique se o bug já foi reportado em [Issues](../../issues)
2. Abra uma nova Issue com o template **Bug Report**
3. Inclua: comportamento esperado vs atual, passos para reproduzir, screenshot se possível

### 💡 Sugerir Funcionalidades
1. Abra uma Issue com o label `enhancement`
2. Descreva: o que, por que e como implementaria
3. Inclua exemplos de como ficaria no README

### 🔧 Contribuir com Código

```bash
# 1. Fork o repositório
# 2. Clone seu fork
git clone https://github.com/SEU_USUARIO/xXYoungMoreXx.git

# 3. Crie uma branch descritiva
git checkout -b feat/crafting-nova-receita

# 4. Faça suas mudanças no engine
# 5. Teste localmente
python3 -c "import ast; ast.parse(open('rpg/engine.py').read()); print('OK')"
python3 rpg/engine.py "rpg:norte" "test_user"

# 6. Commit com mensagem clara
git commit -m "feat: adiciona receita de Elixir Dracônico ao sistema de crafting"

# 7. Abra um Pull Request
```

### ✅ Checklist para PRs
- [ ] Código Python sem dependências externas (stdlib only)
- [ ] Nenhuma chave de API ou token hardcoded
- [ ] Testado localmente com `python3 rpg/engine.py "rpg:acao" "test"`
- [ ] README ou documentação atualizada se necessário
- [ ] Sem quebra de saves existentes (compatibilidade com `players/*.json`)

## Áreas onde contribuições são especialmente bem-vindas

| Área | Exemplos |
|------|----------|
| 🗺️ Lore | Novos diálogos de NPCs, rumores na taverna, descrições de locais |
| ⚔️ Mecânicas | Novas receitas de crafting, habilidades de skill tree, eventos mundiais |
| 🐛 Bugfixes | Correções no engine ou workflow |
| 📚 Documentação | Melhorias no SETUP.md, PRD.md ou este arquivo |
| 🎨 Portfólio | Sugestões para a seção de portfólio no README |

## Estilo de Código

- **Python**: PEP 8, mas priorize legibilidade sobre regras rígidas
- **Nomes**: variáveis descritivas em português ou inglês (consistente com o arquivo)
- **Sem dependências**: `stdlib` only — o engine deve rodar sem `pip install`
- **Eficiência**: lembre que cada action tem ~60s de orçamento de tempo

## Contato

Dúvidas sobre contribuição: **morekaik27@gmail.com** ou abra uma Issue com label `question`.
