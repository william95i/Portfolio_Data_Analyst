# Choix des contrôles du P13

J'ai testé trois façons de rapprocher les mêmes fichiers ERP, Web et liaison. Le but était de comprendre les écarts entre le code du P6 et ses exports, sans masquer les produits écartés de l'analyse.

| Méthode testée | Produits appariés | Après le filtre de marge | Ce que j'en retiens |
| --- | ---: | ---: | --- |
| **Données d'origine** (`raw`) : identifiants reçus | 714 | 713 | Les `product_id` correspondent à ceux des exports. |
| **Méthode du notebook P6** (`notebook_code`) : corrections avant jointure | 713 | 712 | Le résultat diffère des exports enregistrés. |
| **Reconstitution des exports P6** (`export_observed`) : libellés observés dans les exports | 714 | 713 | Les `product_id` et les libellés comparés retrouvent les exports. |

La **reconstitution des exports P6** sert à comparer le POC aux anciens fichiers. La méthode **Données d'origine** permet de voir les identifiants reçus. Ces méthodes traitent les mêmes fichiers ; elles ne désignent pas des fichiers supplémentaires. Cette concordance ne valide pas les corrections d'identifiants sur le plan métier.

Les règles explicites signalent notamment **91 `id_web` manquants** dans la liaison et **111 produits sans correspondance Web**. Pour les prix atypiques, le Z-score repère **13 cas** et l'IQR **31**, dont **13 en commun**. Ces alertes ne sont pas des erreurs confirmées.

## Critères de décision

| Critère | Ce que j'ai vérifié ou retenu |
| --- | --- |
| **Qualité** | Les contrôles montrent les clés, les jointures et les valeurs à revoir. Retrouver 714/713 identifiants ne prouve pas que toutes les colonnes sont exactes. |
| **Biais** | Les 111 produits sans Web ne figurent pas dans l'analyse des produits appariés ; le filtre de marge en écarte un autre. Z-score et IQR dépendent du lot et de leurs seuils. |
| **Temps** | Aucun temps avant/après ni test de vitesse entre outils n'a été mesuré : aucun gain chiffré n'est annoncé. |
| **Reproductibilité** | Le code distingue les trois méthodes et enregistre les résultats séparément. L'essai porte sur un seul lot ; il faut les trois classeurs pour le relancer. |
| **Sécurité** | Le traitement est local, les sources restent inchangées et les sorties sont séparées. Les droits d'accès et de partage restent à définir hors du POC. |
| **Conformité** | Les alertes ne corrigent rien automatiquement. Les règles métier et les conditions de diffusion n'ont pas été validées par ces essais. |

J'ai testé **Python et Pandas** sur les classeurs. **Great Expectations, Polars et dbt** ont été étudiés dans la veille, sans essai comparatif sur ce lot ; je ne leur attribue aucun gain mesuré. L'IA m'a aidé à explorer les pistes, mais j'ai vérifié ses propositions sur les fichiers et les résultats.

Les détails se trouvent dans les [rapports des trois méthodes](outputs/poc_20260924/), le [notebook](notebooks/P6_Bottleneck_ameliore_finalise.ipynb) et la [documentation du P13](output/pdf/Documentation_P13_Missions_1_2.pdf).
