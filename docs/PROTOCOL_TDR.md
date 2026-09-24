# Protocol experimental suggerit · Agent FX TDR v0.1.0

## Pregunta de recerca

Una estratègia sistemàtica basada en indicadors tècnics aplicada a una cartera de divises produeix resultats diferents dels d'una estratègia aleatòria sota les mateixes condicions de capital, univers de divises, límit de pes i costos de conversió?

## Hipòtesis

- **H0:** l'agent tècnic no obté un resultat diferenciat de la distribució dels agents aleatoris.
- **H1:** l'agent tècnic presenta resultats diferenciats respecte de la distribució aleatòria, considerant conjuntament rendibilitat i risc.

Per evitar formular una conclusió per avançat, convé que la hipòtesi operativa es pugui contrastar tant si l'agent supera com si no supera els controls.

## Font de dades

El simulador utilitza els **tipus de canvi de referència diaris del Banc Central Europeu (BCE)**.

El BCE expressa cada sèrie com a unitats de divisa estrangera per euro. Quan la moneda de referència de la cartera no és EUR, el programa calcula un tipus creuat:

```text
valor d'1 unitat de la divisa A en la divisa R
= tipus BCE de R per EUR / tipus BCE d'A per EUR
```

Exemple: si el BCE publica 1 EUR = 1,15 USD i 1 EUR = 0,86 GBP, llavors:

```text
1 GBP ≈ 1,15 / 0,86 = 1,337 USD
```

Els tipus del BCE són de referència i no s'han d'interpretar com a preus reals d'execució.

## Abast del model

La v0.1.0 treballa amb una cartera de divises simple:

- sense palanquejament;
- sense posicions curtes;
- sense futurs ni CFD;
- sense swaps;
- sense interessos sobre cash;
- sense cost overnight.

El cost de conversió introduït per l'usuari és una simplificació metodològica dels costos de canviar divises.

## Controls

1. **Holders:** cada holder converteix el capital inicial a una única divisa al principi i la manté durant tot el període.
2. **Agents aleatoris:** 100–10.000 simulacions sobre el mateix univers de divises, amb el mateix pes màxim i el mateix cost de conversió.
3. **Participants humans:** persones que registren amb data si prefereixen una divisa determinada o CASH.

## Regles de l'agent

Abans del període de test s'han de definir:

- períodes i puntuació de l'EMA;
- període, interval i puntuació del RSI;
- paràmetres i puntuació del MACD;
- puntuació mínima perquè una divisa sigui elegible;
- pes màxim per divisa;
- cost de conversió;
- divisa de referència;
- univers de divises.

Les regles s'han de **congelar abans d'observar els resultats del test principal**.

## Variables a registrar

- Capital final.
- Rendibilitat total.
- Rendibilitat anualitzada.
- Drawdown màxim.
- Volatilitat anualitzada.
- Índex Sharpe.
- Nombre de reequilibris.
- Costos de conversió acumulats.
- Percentil de l'agent dins la distribució aleatòria.
- Rendibilitat de cadascun dels holders.
- Resultats dels participants humans, si s'incorporen.

## Freqüència temporal

Les observacions del BCE corresponen normalment a dies laborables. El simulador anualitza volatilitat i Sharpe amb **252 sessions**.

Els agents aleatoris poden revisar la cartera cada 1, 5, 10 o 20 sessions.

## Precaucions metodològiques

- No interpretar un únic període favorable com una prova general de superioritat de l'anàlisi tècnica.
- No reajustar EMA, RSI, MACD o la puntuació mínima després de veure el resultat del test principal.
- Separar, si és possible, un període de desenvolupament d'un període fora de mostra.
- No confondre tipus de referència del BCE amb preus reals de broker.
- Deixar constància que el model no incorpora spread variable, slippage, interessos ni altres friccions del Forex real.
- No comparar directament aquest simulador amb estratègies apalancades sense explicar que el risc i l'estructura són diferents.

## Reproduïbilitat

A la memòria del TDR s'haurien d'anotar explícitament:

- versió del simulador;
- data d'execució;
- divisa de referència;
- divises seleccionades;
- període;
- capital inicial;
- cost de conversió;
- paràmetres EMA/RSI/MACD;
- puntuació mínima;
- pes màxim;
- nombre d'agents aleatoris;
- freqüència de decisió aleatòria.

Això permet repetir l'experiment amb la mateixa configuració.
