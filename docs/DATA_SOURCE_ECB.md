# Font de dades · tipus de canvi de referència del BCE

## Font

Academic FX Investment Simulator utilitza la sèrie històrica oficial dels **Euro foreign exchange reference rates** del Banc Central Europeu (BCE).

- Informació institucional: https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/
- CSV històric utilitzat pel programa: https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.csv

El programa no utilitza credencials ni una API privada.

## Convenció de les dades del BCE

Les columnes del BCE indiquen **unitats de divisa per 1 EUR**.

Si una observació diu:

```text
USD = 1.1500
GBP = 0.8600
```

significa:

```text
1 EUR = 1.1500 USD
1 EUR = 0.8600 GBP
```

## Conversió utilitzada pel simulador

Per valorar una unitat de la divisa actiu `A` en la divisa de referència `R`:

```text
preu(A en R) = BCE(R per EUR) / BCE(A per EUR)
```

Es defineix:

```text
BCE(EUR per EUR) = 1
```

Per tant:

```text
USD/EUR = 1 / BCE(USD)
GBP/USD = BCE(USD) / BCE(GBP)
EUR/USD = BCE(USD)
```

Aquesta convenció fa que un augment de la sèrie `A/R` signifiqui que la divisa A s'ha apreciat respecte de R.

## Freqüència

El BCE publica habitualment una observació per dia laborable. El simulador treballa, per tant, amb **dades diàries de referència**, no amb OHLC intradia.

Per a volatilitat i índex Sharpe s'utilitzen 252 sessions per anualitzar.

## Limitacions

Els tipus del BCE es publiquen amb finalitat informativa. El model no reprodueix necessàriament:

- bid/ask spread;
- slippage;
- preus intradia;
- swaps;
- interessos;
- comissions concretes d'un broker;
- costos de finançament.

El camp **Cost de conversió** del simulador és una hipòtesi simplificada per introduir fricció transaccional de manera transparent.

## Reproduïbilitat

Per reproduir un experiment cal registrar:

- versió del simulador;
- data d'execució;
- divisa de referència;
- divises seleccionades;
- dates inicial i final;
- paràmetres de l'agent;
- cost de conversió.

El CSV es descarrega de nou quan s'executa una simulació; si el BCE revisés excepcionalment dades històriques, una execució posterior podria incorporar aquesta revisió.
