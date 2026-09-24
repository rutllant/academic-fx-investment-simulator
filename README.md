# Academic FX Investment Simulator · v0.1.0

Aplicació educativa per comparar una estratègia sistemàtica sobre **divises** amb holders, agents aleatoris i inversors humans utilitzant tipus de canvi de referència diaris del Banc Central Europeu (BCE).

**No executa operacions reals, no utilitza palanquejament, no necessita claus API i no ofereix assessorament financer.**

## Què simula?

L'usuari tria una **divisa de referència** per valorar tota la cartera —per exemple EUR— i un conjunt de divises en què l'agent pot convertir part del capital —per exemple USD, GBP, JPY o CHF.

El programa compara:

- **Agent tècnic:** aplica regles mecàniques basades en EMA, RSI i MACD.
- **Holders:** converteixen el capital inicial a una sola divisa i la mantenen.
- **Agents aleatoris:** creen carteres aleatòries amb el mateix univers de divises i el mateix pes màxim per actiu.
- **Inversors humans:** permeten importar decisions mitjançant CSV.

## Font de dades: BCE

La v0.1.0 utilitza la sèrie històrica oficial de tipus de canvi de referència de l'euro publicada pel BCE:

`https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.csv`

El BCE publica els tipus com a unitats de cada divisa per euro. El simulador deriva matemàticament els tipus creuats quan la divisa de referència no és EUR.

Per exemple, si el BCE publica USD/EUR i GBP/EUR, el programa pot calcular el valor d'una lliura en dòlars sense recórrer a una segona font.

> Els tipus del BCE són tipus de referència informatius i no preus executables de trading. El simulador els utilitza perquè són una font institucional, transparent i reproduïble per a recerca acadèmica.

## Sense Forex apalancat

Aquesta primera versió no simula:

- palanquejament;
- posicions curtes;
- CFD;
- futurs;
- swaps;
- interessos sobre el cash;
- finançament overnight.

La lògica és deliberadament simple: convertir una part de la cartera d'una moneda a una altra i valorar-la posteriorment amb el tipus de referència.

## Cost de conversió

El camp **Cost de conversió (%)** representa de manera simplificada els costos que podria comportar canviar d'una divisa a una altra.

No pretén reproduir exactament l'spread o les comissions d'un broker concret. Serveix per evitar que una estratègia amb molts canvis de cartera sigui comparada com si operar fos gratuït.

## Regles tècniques

Es mantenen les mateixes regles transparents del simulador original:

- EMA curta vs EMA llarga;
- interval RSI;
- MACD vs línia de senyal;
- puntuació mínima per entrar;
- pes màxim per divisa.

L'agent no utilitza intel·ligència artificial ni un model opac per decidir. Davant les mateixes dades i paràmetres, produeix les mateixes decisions.

## Resultats

El simulador calcula, entre altres:

- capital final;
- rendibilitat total;
- drawdown màxim;
- volatilitat anualitzada;
- índex Sharpe;
- nombre de reequilibris;
- costos de conversió;
- percentil de l'agent respecte dels agents aleatoris;
- rendibilitat de cada holder.

Per a les dades diàries de divises, volatilitat i Sharpe s'anualitzen amb **252 sessions**.

## Manuals

- **[Manual en català](docs/MANUAL_USUARI.md)**
- **[User manual in English](docs/USER_MANUAL_EN.md)**
- **[Protocol experimental suggerit](docs/PROTOCOL_TDR.md)**
- **[Font de dades i fórmula de tipus creuats](docs/DATA_SOURCE_ECB.md)**

Els manuals estan pensats perquè una persona sense coneixements previs d'inversió pugui entendre divisa de referència, tipus creuat, cartera, CASH, EMA, RSI, MACD, holders, Monte Carlo, drawdown, Sharpe, percentils i overfitting.

## Interfície multiidioma

La interfície manté:

- Català
- Español
- English
- Euskara
- Galego

## Windows

La distribució està preparada per generar:

- `Agent_FX_TDR_Windows_v0.1.0.zip` — versió portable;
- `Agent_FX_TDR_Setup_v0.1.0.exe` — instal·lador Inno Setup;
- `SHA256SUMS.txt` — verificació d'integritat.

El paquet inclou Python i les dependències; no cal instal·lar Python manualment.

L'accés a Internet és necessari quan el simulador descarrega les dades oficials del BCE.

## Criteri metodològic

Per a un experiment acadèmic, les regles i paràmetres s'han de definir **abans d'observar el període de test**. Modificar-los repetidament fins a obtenir un resultat favorable introdueix risc de sobreajustament (*overfitting*).

Un resultat favorable en un backtest no demostra que la mateixa estratègia funcioni en altres períodes o en el futur.

## Origen del projecte

Aquest projecte deriva de l'arquitectura de **Academic Crypto Investment Simulator**, però substitueix els exchanges de criptomonedes per tipus de canvi institucionals del BCE i adapta el model a una cartera de divises sense palanquejament.
