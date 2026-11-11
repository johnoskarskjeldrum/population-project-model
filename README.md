# Befolkningsmodell for Norge

Simulerer Norges befolkning person for person fra 1. januar 2023, uten inn- og utvandring, for ulike fruktbarhetstall (TFR).

## Kjøre modellen

```sh
uv run python main.py --years 50 --tfrs 1.1 1.66 2.1 --start-tfr 1.44 --fade-years 15
```

- `--years`: antall år som simuleres (standard 100).
- `--tfrs`: ett eller flere fruktbarhetstall; hvert gir ett scenario.
- `--start-tfr` og `--fade-years`: lineær overgang fra dagens TFR til scenarioets TFR.
- `--seed`: frø for tilfeldige trekk (standard 42). Samme frø gir identiske filer.
- `--projected-mortality`: bruk SSBs framskrevne dødelighet (stigende levealder) i stedet for konstant dødelighet på 2023-nivå. Filene får endelsen `_ssbdod`.
- `--net-immigration`: antall nettoinnvandrere som legges til hvert år (standard 0). Filene får endelsen `_innv<antall>`.

Resultatene skrives til `data/`:

- `befolkningsutvikling_<start>_<slutt>_<tfrs>.csv`: samlet folketall per år, én kolonne per scenario.
- `popfordeling_<start>-<slutt>_tfr<tfr>.csv`: antall personer per kjønn og alder for hvert år.
- `populasjon_<slutt>_tfr<tfr>.csv`: alle individer i sluttåret (ligger ikke i git).

## Forutsetninger

- **Startbefolkning**: `data/startpop_no.csv`, én rad per innbygger 1. januar 2023.
- **Dødelighet**: dødssannsynligheter per kjønn og ettårig alder fra SSB tabell 07902 for 2023 (`data/dodelighet_2023.csv`).
- **Fruktbarhet**: aldersfordelingen av fødsler ligger i `config.yaml` (`asfr_norm_avg`) og skaleres til valgt TFR. 51,3 % av nyfødte er gutter.
- **Framskrevet dødelighet** (valgfritt): SSB tabell 14745, middels levealder i 2026-framskrivingen (`data/dodelighet_framskrevet_ssb_2026.csv`). Årene før 2026 bruker 2023-tabellen.
- **Innvandring**: ikke med som standard. Med `--net-immigration` legges et fast antall personer til hvert år, med en aldersfordeling der de fleste er unge voksne (`create_pop` i `population_model/model.py`).

## Andre data

- `data/netto_overføring*.csv`: netto overføringer fra offentlig forvaltning per person etter alder (1000 kr), hentet fra figur i Perspektivmeldingen 2024. Alder 100+ er satt lik verdien for 99 år.
- `data/ssb_framskriving_2026.csv`: SSBs framskrevne folkemengde per alder (tabell 14740) for alternativene MMM (hovedalternativet), MME (ingen nettoinnvandring) og MKM (konstant levealder), til sammenligning.
- `data_barnefordeling/`: barnetallsfordeling etter kjønn, alder og fødselskohort.

## Notebooks

- `Befolkningsfremskrivning_plots_for_article.ipynb`: figurene til artikkelen.
- `befolkningsfremskrivning_figurer.ipynb`: befolkningspyramider per år til `Figures/aldersfordeling_til_gif/`.
