# Security

## Abast del projecte

Academic FX Investment Simulator és una aplicació educativa i de recerca. No executa operacions reals, no demana credencials bancàries o de brokers i no necessita claus API.

## Font de dades

El programa descarrega únicament els tipus de canvi de referència històrics publicats pel Banc Central Europeu (BCE) des del domini oficial `ecb.europa.eu`. Aquests tipus són dades de referència informatives i no s'han d'interpretar com a preus executables de negociació.

## Distribució Windows

Les Releases de Windows es construeixen automàticament mitjançant GitHub Actions. El runtime Python i les dependències s'incorporen durant el procés de build; l'ordinador de l'usuari no instal·la Python ni executa un bootstrap PowerShell.

La distribució publica:
- un ZIP portable;
- un instal·lador Inno Setup;
- un fitxer `SHA256SUMS.txt` amb el hash SHA-256 dels artefactes.

## Verificació

A PowerShell de Windows es pot comprovar un fitxer descarregat amb:

```powershell
Get-FileHash .\Agent_FX_TDR_Windows_v0.1.0.zip -Algorithm SHA256
```

El valor ha de coincidir amb el publicat a `SHA256SUMS.txt` de la mateixa Release.

## Signatura digital

L'instal·lador no està signat actualment amb un certificat comercial de code signing. Windows SmartScreen o alguns antivirus poden mostrar avisos de reputació o indicar «editor desconegut».
