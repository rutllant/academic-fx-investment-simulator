# Manual d'usuari · Academic FX Investment Simulator

Aquest manual està pensat per a persones sense coneixements previs d'inversió o mercat de divises.

> **Important:** és un simulador educatiu. No opera amb diners reals, no utilitza palanquejament i no constitueix assessorament financer. Els tipus del BCE són tipus de referència informatius, no preus reals d'execució.

## 1. Què fa el simulador?

Compara quatre maneres de gestionar una cartera de divises:

- **Agent tècnic:** segueix regles mecàniques basades en EMA, RSI i MACD.
- **Holders:** converteixen el capital inicial a una sola divisa i la mantenen.
- **Agents aleatoris:** prenen decisions a l'atzar i serveixen com a grup de control.
- **Inversors humans:** permet importar decisions de persones mitjançant CSV.

El programa fa un **backtest**: aplica aquestes decisions a dades històriques per veure què hauria passat. No prediu el futur.

## 2. Conceptes bàsics

**Divisa:** moneda com EUR, USD, GBP, JPY o CHF.

**Tipus de canvi:** valor d'una moneda expressat en una altra. Per exemple, USD/EUR indica el valor d'un dòlar en euros.

**Divisa de referència:** moneda en què es valora tota la cartera. Si és EUR, capital inicial, capital final i posicions s'expressen en euros.

**CASH:** part de la cartera que es manté en la divisa de referència.

## 3. Font de dades: BCE

El simulador utilitza els tipus de canvi de referència diaris del Banc Central Europeu.

El BCE publica quantes unitats de cada divisa equivalen a un euro. Si la cartera utilitza una altra moneda de referència, el programa deriva un **tipus creuat**.

Exemple hipotètic:

- 1 EUR = 1,15 USD
- 1 EUR = 0,86 GBP

Aleshores:

**1 GBP ≈ 1,15 / 0,86 = 1,337 USD**

Aquests tipus són adequats per a comparacions acadèmiques reproduïbles, però no inclouen exactament spread, slippage, swap, interessos o preus intradia.

## 4. Mercat i cartera

### Divisa de referència

Escull la moneda amb què es valorarà tota la cartera. EUR és una opció senzilla per començar.

### Divises

Selecciona les monedes en què l'agent podrà convertir part del capital, per exemple USD, GBP, JPY o CHF.

### Capital inicial

Quantitat virtual amb què comencen totes les estratègies.

### Cost de conversió

Percentatge que simula de manera simplificada el cost de canviar de divisa. No representa necessàriament la tarifa d'un broker concret.

### Dates

Defineixen el període del backtest. El programa utilitza també observacions anteriors per poder calcular els indicadors des del primer dia de l'avaluació.

## 5. EMA

EMA significa **Exponential Moving Average**.

Compara una mitjana curta amb una de llarga. Si, per exemple, EMA20 > EMA50, la regla interpreta que la tendència recent és superior a la de més llarg termini i suma els punts configurats.

No garanteix que el tipus de canvi continuï pujant.

## 6. RSI

RSI significa **Relative Strength Index** i oscil·la entre 0 i 100.

Si configurem RSI(14) entre 50 i 70, la regla suma punts quan el valor es troba dins d'aquest interval.

## 7. MACD

MACD significa **Moving Average Convergence Divergence**.

El simulador suma punts quan la línia MACD està per damunt de la seva línia de senyal. És una regla de tendència/momentum, no una predicció.

## 8. Puntuació mínima

Cada regla aporta punts. Una divisa només és elegible si arriba a la puntuació mínima definida.

Una puntuació alta fa l'agent més selectiu; una de baixa, més permissiu.

## 9. Pes màxim per divisa

Limita la concentració.

Amb 10.000 EUR i un pes màxim del 40 %, cap divisa pot rebre inicialment més de 4.000 EUR de valor en un reequilibri. La resta pot quedar en CASH.

## 10. Reequilibri

És un canvi en la composició de la cartera.

Exemple:

- abans: USD 40 %, GBP 40 %, CASH 20 %
- després: JPY 40 %, CHF 40 %, CASH 20 %

Els canvis generen el cost de conversió configurat.

## 11. Holders

Cada holder converteix el capital inicial a una sola divisa i la manté fins al final.

Serveix per comparar si les regles tècniques aporten alguna cosa respecte a una estratègia passiva.

## 12. Agents aleatoris

No utilitzen EMA, RSI ni MACD.

En cada data de decisió seleccionen a l'atzar quantes divises mantenir i quines, respectant el mateix pes màxim que l'agent tècnic.

Se'n poden simular de 100 a 10.000.

Les opcions de decisió són cada 1, 5, 10 o 20 sessions. Amb dades de dies laborables, 5 sessions s'aproxima a una setmana i 20 a un mes.

## 13. Resultats

**Capital final:** valor final de la cartera.

**Rendibilitat:** variació percentual del capital.

**Drawdown màxim:** caiguda més gran des d'un màxim anterior.

**Volatilitat:** intensitat de les oscil·lacions. El simulador l'anualitza amb 252 sessions.

**Índex Sharpe:** relaciona rendibilitat i volatilitat. No és una nota universal ni una garantia.

**Reequilibris:** nombre de canvis de cartera.

**Percentil:** posició de l'agent respecte de la distribució dels agents aleatoris. Percentil 90 vol dir que ha quedat per sobre d'aproximadament el 90 % dels agents d'aquella simulació; no vol dir que tingui un 90 % de probabilitats de guanyar en el futur.

## 14. Gràfics

L'**histograma** mostra la distribució de rendibilitats dels agents aleatoris i la posició de l'agent tècnic.

La gràfica **agent vs holders** mostra com evoluciona la rendibilitat acumulada de cada estratègia, no només el resultat final.

## 15. Inversors humans

El CSV té tres columnes:

| Columna | Significat |
|---|---|
| participant | Nom o codi |
| date | Data |
| choice | Divisa o CASH |

Exemple:

```csv
participant,date,choice
Persona 1,2026-01-02,USD
Persona 1,2026-02-02,GBP
Persona 1,2026-03-02,CASH
```

L'última decisió es manté fins que se'n registra una de nova.

## 16. Configuració senzilla per aprendre

| Paràmetre | Exemple |
|---|---|
| Referència | EUR |
| Divises | USD, GBP, JPY, CHF |
| Capital | 10.000 EUR |
| Cost | 0,10 % |
| Període | 2 anys |
| EMA/RSI/MACD | activats |
| Holders | USD, GBP, JPY |
| Agents aleatoris | 1.000 |
| Decisió aleatòria | cada 5 sessions |

És només un exemple pedagògic, no una recomanació d'inversió.

## 17. Què no simula?

La v0.1.0 no incorpora:

- palanquejament;
- posicions curtes;
- marge;
- CFD o futurs;
- spreads variables;
- slippage;
- swaps;
- interessos;
- ordres intradia.

Aquesta simplicitat és intencionada per facilitar una comparació acadèmica transparent.

## 18. Errors habituals

**«Ha guanyat diners, per tant funciona.»** No necessàriament: cal comparar amb controls i risc.

**«Ha superat l'atzar, per tant sempre ho farà.»** No: el resultat només correspon al període i configuració utilitzats.

**«Puc ajustar els paràmetres fins que surti bé.»** Fer-ho després de veure les dades pot generar **overfitting** o sobreajustament.

## 19. Per al TDR

Abans del test principal convé congelar i documentar:

1. versió del simulador;
2. divisa de referència;
3. divises seleccionades;
4. període;
5. capital inicial;
6. cost de conversió;
7. EMA, RSI i MACD;
8. puntuació mínima;
9. pes màxim;
10. holders;
11. nombre d'agents aleatoris;
12. freqüència de decisió.

Si es canvien les regles després d'observar el resultat, cal considerar-les una nova estratègia i provar-les en un altre període.

**Versió del manual:** Academic FX Investment Simulator v0.1.0.
