# Declaração

**Ferramenta:** Claude (app desktop), com acesso de leitura e escrita à pasta Meu/onfly, concedido por mim.

**Modelo:** Opus 5.5 com esforço médio

## O que a IA fez

- **Leu e mapeou o projeto** na ordem que pedi e resumiu o fluxo de dados.
- **Encontrou os cinco defeitos** e comprovou cada um com o valor esperado e o obtido:
  - câmbio dividido pela taxa e em `float`;
  - noites calculadas pelo dia do mês, com `.day`;
  - leitura cortada em 200 linhas;
  - `NO_SHOW` sendo faturado;
  - ranking em ordem crescente.
- **Aplicou as correções dos passos 1 a 4**, sempre depois da minha aprovação.
- **Sugeriu e escreveu testes extras** para casos que os fornecidos não cobriam.
- **Validou os testes** reintroduzindo cada defeito para ver se eles o pegavam.
- **Reorganizou os testes** em arquivos próprios, quando eu pedi.
- **Fez o rascunho do `README-ENTREGA.md`** a partir dos meus commits.

## O que eu fiz

- **Preparei o ambiente e o Git:** commit do projeto original e uma branch separada para abrir PR.
- **Planejei as etapas** e defini como a IA deveria responder.
- **Transformei o limite de 200 linhas num passo próprio**, já que nenhum teste fornecido pegava esse defeito.
- **Escolhi quais testes entrariam** entre os sugeridos e pedi para checar a cobertura existente, para não duplicar.
- **Corrigi o ranking eu mesma** e adicionei os testes de desempate e de `--top`.
- **Revisei cada diff** antes de commitar.
- **Escrevi as mensagens de commit.**
- **Revisei** o `README-ENTREGA.md`.
- **Escrevi esta declaração** e pedi que a IA não mexesse nela.
- **Coloquei** os testes propostos pelo Claude e aqueles pensados por mim dentro dos arquivos fornecidos do mesmo tema. Tinha entendido que a regra protegia a lógica dos testes, e não o arquivo em si. Após o aviso da IA sobre essa prática, reli o README.md diversas vezes, refleti um pouco e notei que no início dos arquivos de testes possuía uma mensagem dizendo """Testes fornecidos""". Por isso, decidi seguir o Claude e pedi para ele juntar as funções que adicionei em arquivos de testes fornecidos e movê-los para outro arquivo, cujo nome deveria seguir o padrão do projeto e ser test_ + tópico geral que será testado por esse(s) teste(s) (ex.: contrato/contract, regressão/regression).
