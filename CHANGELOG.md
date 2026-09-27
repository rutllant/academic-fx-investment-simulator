# Changelog

## 0.1.1
- Corregida la descàrrega dels tipus de canvi del BCE a la distribució Windows portable.
- El runtime empaquetat utilitza el magatzem de certificats HTTPS del sistema mitjançant `truststore`, amb `certifi` com a fallback.
- El programa intenta primer el ZIP històric oficial que enllaça el web del BCE i conserva el CSV directe com a ruta alternativa.
- Afegits reintents i missatges d'error més informatius per problemes de xarxa, antivirus o tallafoc.
- Afegit un test de connectivitat real amb el BCE que s'executa amb el mateix Python portable abans de publicar una Release.
- Es manté el smoke test determinista independent de la xarxa.

## 0.1.0
- Primera versió de l'Academic FX Investment Simulator, derivada de l'arquitectura del simulador de criptomonedes.
- Substituït CCXT pels tipus de canvi de referència diaris del Banc Central Europeu (BCE).
- Afegides carteres amb divisa de referència configurable i tipus creuats derivats matemàticament.
- Mantingudes les regles sistemàtiques EMA, RSI i MACD.
- Mantinguts els controls amb holders, agents aleatoris Monte Carlo i inversors humans.
- Els agents treballen sense palanquejament, sense posicions curtes, sense futurs, CFD ni swaps.
- El cost configurable representa un cost simplificat de conversió.
- Volatilitat i Sharpe anualitzats amb 252 sessions.
- Interfície multiidioma: català, castellà, anglès, euskera i gallec.
- Distribució Windows autocontinguda amb ZIP portable, Setup.exe i SHA256SUMS.txt.
- Manuals introductoris en català i anglès adaptats al mercat de divises.
