# Entrega — Consolidador de reservas de hotel

O CLI gerava um relatório com números errados por causa de **cinco defeitos**. Todos foram corrigidos com mudanças pontuais, sem alterar:

- o comando e os argumentos do CLI;
- o schema do relatório;
- os testes fornecidos;
- os arquivos `data/reservas_hoteis.csv` e `data/taxas_cambio.csv`.

Os valores monetários continuam sempre em `Decimal`, e o arredondamento continua só na serialização (2 casas, half-up).

## Defeitos corrigidos

| #   | Defeito            | Arquivo                                                       | Causa raiz (uma frase)                                                                                                                                                                                  | Commit    |
| --- | ------------------ | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| 1   | Conversão de moeda | `src/onfly_report/services/currency_converter.py`             | `convert_to_brl` dividia o valor pela taxa e fazia a conta em `float`, mas o README define `amount * rate_to_brl` e proíbe `float` em dinheiro.                                                         | `11b667e` |
| 2   | Noites de quarto   | `src/onfly_report/services/stay_calculator.py`                | `calculate_room_nights` subtraía só o dia do mês (`checkout.day - checkin.day`) em vez da diferença entre as datas, e por isso dava valores errados ou negativos em estadias que atravessam mês ou ano. | `7714701` |
| 3   | Leitura truncada   | `src/onfly_report/repositories/csv_reservation_repository.py` | O laço de leitura tinha um `if` que parava em 200 registros, e com isso 100 das 300 reservas do arquivo eram ignoradas.                                                                                 | `1445936` |
| 4   | Regra de status    | `src/onfly_report/services/status_policy.py`                  | `is_billable` tratava como faturável tudo que não fosse `CANCELLED` (inclusive `NO_SHOW`), mas pelo README só `CONFIRMED` é faturável.                                                                  | `85a5541` |
| 5   | Ranking de hotéis  | `src/onfly_report/services/report_builder.py`                 | O `top_hotels` era ordenado por `total_brl` crescente, então o corte pelo `--top` pegava os hotéis de **menor** valor.                                                                                  | `2a860ec` |

### Detalhe das correções

**1. Conversão de moeda**

```python
- return Decimal(str(float(amount) / float(rate)))
+ return amount * rate
```

Antes, 100.00 USD virava 18.45 BRL, quando o certo é 542.00. Como `amount` e `rate` já chegam como `Decimal`, a multiplicação direta já devolve o valor certo no tipo certo.

**2. Noites de quarto**

```python
- return (checkout.day - checkin.day) * rooms
+ return (checkout - checkin).days * rooms
```

Antes, de 30/01 a 02/02 dava −28 noites, quando o certo é 3. Subtrair dois objetos `date` dá um `timedelta`. O `.days` dele não conta o dia do check-out, como pede o README, e já considera mês, ano e ano bissexto.

**3. Leitura completa do arquivo**

```python
-                    if len(rows) == 200:
-                        break
```

Antes, `total_reservations` saía 200 em vez de 300, e as contagens por status batiam exatamente com as 200 primeiras linhas do CSV. O README define `total_reservations` como o número de reservas no arquivo.

**4. Regra de status**

```python
- return status != "CANCELLED"
+ return status == "CONFIRMED"
```

Antes, o `NO_SHOW` entrava em noites, valores, `by_month` e `top_hotels`. A lógica era uma lista de exclusão, então qualquer status desconhecido ou vazio também seria faturado. Agora é uma lista de inclusão: só `CONFIRMED` passa.

**5. Ranking de hotéis**

```python
- ranked_hotels = sorted(hotels.items(), key=lambda item: (item[1]["amount"], item[0]))
+ ranked_hotels = sorted(
+     hotels.items(), key=lambda item: (-item[1]["amount"], item[0])
+ )
```

Inverter o sinal do `Decimal` é exato e deixa o valor em ordem decrescente. O `hotel_id` continua crescente como critério de desempate. Não usei `reverse=True` porque ele também inverteria o desempate. Com H01 = 500, H03 = 500 e H02 = 900, `reverse=True` daria `H02, H03, H01`, enquanto o correto é `H02, H01, H03`.

## Como investiguei

1. **Leitura do projeto antes de qualquer alteração.** Li o `README.md` como fonte de verdade e depois o código na ordem `models.py` → `repositories` → `services` → `cli.py`, para mapear o fluxo de dados:

   ```
   cli.py → ReportBuilder.build()
            ├─ CsvReservationRepository.read() → list[RawRow]       (lê o CSV, valida colunas)
            ├─ RowParser.parse()               → Reservation        (str → date/int/Decimal)
            ├─ CsvRateRepository.read()        → dict[str, Decimal] (moeda → taxa)
            ├─ contagem por status (todas as reservas)
            ├─ is_billable()          → filtra CONFIRMED
            ├─ calculate_room_nights()
            ├─ convert_to_brl()
            └─ agrega summary / by_month / top_hotels → format_money()
   cli.py → grava o JSON em --output e imprime o resumo
   ```

2. **Um defeito por passo.** Cada passo seguiu a mesma sequência:
   - rodar `python -m pytest -q` e identificar o teste e o caso que falhava, com o valor esperado e o obtido;
   - seguir o fluxo de dados desde a leitura até a função responsável;
   - testar a função isoladamente com casos extras, como virada de ano, status desconhecido e empates;
   - comparar o comportamento com a regra do README;
   - só então aplicar a correção pontual e rodar a suíte inteira de novo.

   Não deixei nenhum print ou log temporário no código.

3. **O defeito sem teste (leitura truncada).** Nenhum teste fornecido cobria esse caso. Contei as reservas de `data/reservas_hoteis.csv` (300, com IDs únicos de RSV-0001 a RSV-0300) e comparei com o `total_reservations` gerado pelo CLI (200). As contagens por status do relatório batiam exatamente com as das 200 primeiras linhas, o que levou ao limite fixo no repository.

4. **Verificação dos testes novos por mutação.** Numa cópia descartável do projeto, reintroduzi cada defeito, um de cada vez, e confirmei que pelo menos um teste falha em cada caso:

   | Defeito reintroduzido                            | Detectado por                                                                                           |
   | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
   | Câmbio dividido e em `float`                     | `test_currency`, `test_regression_report`, `test_regression_full_report`                                |
   | Noites com `.day`                                | `test_nights`, `test_regression_full_report`                                                            |
   | Limite de 200 linhas                             | `test_full_read`                                                                                        |
   | `status != "CANCELLED"`                          | `test_status_rules`, `test_status_aggregations`, `test_regression_report_without_billable_reservations` |
   | Ranking crescente                                | `test_top_hotels`, `test_regression_full_report`                                                        |
   | Ranking com `reverse=True` (desempate invertido) | `test_top_hotels_tie_breaks_by_hotel_id_ascending`, `test_regression_full_report`                       |
   | Arredondar cada item antes de somar              | `test_regression_rounds_half_up_only_on_serialization`                                                  |
   | Arredondamento half-even                         | `test_regression_rounds_half_up_only_on_serialization`                                                  |
   | `by_month` pelo mês do check-out                 | `test_regression_full_report`                                                                           |

## Testes adicionados

Os testes fornecidos (`test_currency.py`, `test_nights.py`, `test_regression_report.py`, `test_status_rules.py`, `test_top_hotels.py` e `helpers.py`) estão idênticos ao commit inicial. Todos os testes novos estão em arquivos próprios, separados por assunto, e usam o `run_cli` de `tests/helpers.py`.

| Arquivo                          | Teste                                                           | O que verifica (regra do README)                                                                                                                                                                                 |
| -------------------------------- | --------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `test_full_read.py`              | `test_reads_all_reservations`                                   | Arquivo com 250 linhas: tudo entra no relatório, sem limite fixo de leitura (`total_reservations` = número de reservas no arquivo).                                                                              |
| `test_status_aggregations.py`    | `test_no_show_is_excluded_from_by_month_and_top_hotels`         | `NO_SHOW` conta no `summary`, mas não entra em `by_month` nem em `top_hotels`.                                                                                                                                   |
| `test_top_hotels_ranking.py`     | `test_top_hotels_tie_breaks_by_hotel_id_ascending`              | Hotéis com o mesmo `total_brl` são desempatados por `hotel_id` crescente.                                                                                                                                        |
| `test_top_hotels_ranking.py`     | `test_top_larger_than_hotel_count_returns_only_existing_hotels` | Com `--top` maior que o número de hotéis faturáveis, vêm só os hotéis existentes, sem erro, sem itens vazios e sem hotéis que só têm reservas `CANCELLED`.                                                       |
| `test_contract.py`               | `test_report_contract_version_and_generated_at`                 | `report_version == "1.0"` e `generated_at` em ISO 8601 com offset fixo `-03:00`.                                                                                                                                 |
| `test_sample_matches_readme.py`  | `test_validation_sample_matches_readme`                         | `data/exemplo-validacao.csv` reproduz as tabelas de validação do README (`summary`, `by_month` e `top_hotels` completos).                                                                                        |
| `test_regression_full_report.py` | `test_regression_full_report`                                   | Relatório completo de ponta a ponta. Cobre BRL, USD e EUR, mais de um quarto, viradas de mês e de ano, `CANCELLED` e `NO_SHOW`, agregação por hotel, empate no corte do `--top`, meses ordenados e schema exato. |
| `test_regression_full_report.py` | `test_regression_rounds_half_up_only_on_serialization`          | Os valores exatos são somados e arredondados só na saída, com half-up.                                                                                                                                           |
| `test_regression_full_report.py` | `test_regression_report_without_billable_reservations`          | Sem reservas `CONFIRMED`: totais zerados, média `"0.00"`, `by_month` e `top_hotels` vazios.                                                                                                                      |

## Como validar

Requisitos: Python 3.11+ e as dependências de `requirements-dev.txt`.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

# testes
python -m pytest -q

# amostra de validação (compare com a tabela do README)
PYTHONPATH=src python -m onfly_report \
  --input data/exemplo-validacao.csv \
  --rates data/taxas_cambio.csv \
  --output output/exemplo.json

# relatório completo
PYTHONPATH=src python -m onfly_report \
  --input data/reservas_hoteis.csv \
  --rates data/taxas_cambio.csv \
  --output output/report.json
```

### Resultados obtidos

**Testes:**

```
$ python -m pytest -q
..............                                                           [100%]
14 passed
```

São os 5 testes fornecidos, sem alteração, mais 9 testes adicionais.

**Amostra de validação:** bate com todas as tabelas do README.

```
Reservas: 12 | Confirmadas: 9 | Noites: 28 | Total BRL: 7566.00
```

**Relatório completo:**

```
Reservas: 300 | Confirmadas: 235 | Noites: 1347 | Total BRL: 396170.00
```

| Campo                      | Antes das correções | Depois    |
| -------------------------- | ------------------- | --------- |
| `total_reservations`       | 200                 | 300       |
| `confirmed_reservations`   | 153                 | 235       |
| `cancelled_reservations`   | 22                  | 31        |
| `no_show_reservations`     | 25                  | 34        |
| `total_room_nights`        | 1046                | 1347      |
| `total_amount_brl`         | 297716.73           | 396170.00 |
| `average_nightly_rate_brl` | 284.62              | 294.11    |

Os valores "antes" foram medidos depois das correções 1 e 2. Com o código original, os números eram ainda mais distorcidos, por causa da conversão de moeda invertida e das noites negativas.

Os códigos de saída seguem o contrato. Por exemplo, um arquivo de entrada inexistente devolve `2`.

## Uso de IA

Usei IA neste projeto. A exportação da sessão e a declaração (ferramenta, modelo e divisão do trabalho entre IA e autora) ficam em `entrega/uso-de-ia/`.
