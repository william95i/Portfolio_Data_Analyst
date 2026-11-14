# Veille métier et technique

Pour améliorer mon analyse Bottleneck, je suis parti d'une question concrète : comment rapprocher les fichiers ERP, Web et liaison tout en gardant visibles les produits qui ne correspondent pas et les valeurs à vérifier ? J'ai consulté les documentations des outils et du métier, puis comparé ces pistes aux résultats obtenus sur les fichiers du projet.

## Ce que j'ai retenu

| Sujet | Sources consultées | Décision pour Bottleneck |
| --- | --- | --- |
| Jointures et valeurs manquantes | [Pandas : `merge`](https://pandas.pydata.org/docs/reference/api/pandas.merge.html) et [données manquantes](https://pandas.pydata.org/docs/user_guide/missing_data.html) | Utiliser des contrôles explicites sur les clés et les jointures. Le pipeline compte les produits appariés et ceux sans correspondance Web. |
| Référentiel produit et stocks | [Fiches produit](https://woocommerce.com/document/managing-products/product-editor-settings/) et [réglages de stock](https://woocommerce.com/document/configuring-woocommerce-settings/products/) de WooCommerce ; [standard GS1](https://ref.gs1.org/standards/gtin-management/) | Conserver `product_id` pour distinguer les produits, signaler les SKU partagés et demander une décision métier avant de modifier une clé ou un stock. Rien ne permet d'affirmer que les SKU du projet sont des GTIN. |
| Contrôles et performance | [Great Expectations](https://docs.greatexpectations.io/docs/core/introduction/gx_overview/), [Polars](https://docs.pola.rs/user-guide/concepts/lazy-api/) et [dbt](https://docs.getdbt.com/docs/build/data-tests) | Ces outils ont été étudiés dans leur documentation, mais pas testés sur les classeurs. Je garde les règles Pandas déjà exécutées ; aucun gain de temps ou de qualité n'a été mesuré pour les autres outils. |

J'ai également comparé deux façons de repérer les prix atypiques. Sur le lot étudié, le **Z-score signale 13 prix** et l'**IQR 31**, dont **13 communs**. Ce sont des alertes à examiner, pas des erreurs confirmées. Les essais et leurs limites sont détaillés dans la [comparaison du P13](Projets_OC/P13/comparaison_options.md).

## Comment je poursuis cette veille

Les documentations Pandas, Great Expectations, Polars et dbt ont été consultées pour le P13 le **24 septembre 2026**. J'ai aussi consulté le [flux des versions de Pandas](https://github.com/pandas-dev/pandas/releases.atom) et les [notes de version 3.0.6](https://pandas.pydata.org/pandas-docs/stable/whatsnew/v3.0.6.html) le **25 septembre 2026**.

Les pages WooCommerce et le standard GS1 cités plus haut ont été revus le **21 octobre 2026** pour vérifier les points sur les SKU et les stocks.

Depuis le **26 octobre 2026**, une tâche Windows lance le [script Python de veille](Projets_OC/P13/src/veille_pandas.py) **chaque lundi à 12 h**. Il consulte les annonces officielles, écarte les préversions et repère les termes liés aux fichiers Excel, aux jointures, aux valeurs manquantes et aux exports. Son [historique daté](Projets_OC/P13/output/veille_pandas_state.json) garde les versions à relire jusqu'à ce que je les marque comme examinées. Le test du 26 octobre et le contrôle du 2 novembre ont réussi. Ce dernier n'a signalé aucune nouvelle version depuis pandas 3.1.0.

Je consulte l'historique pour voir quelles versions restent à examiner. Le tri par mots-clés m'aide à repérer les changements utiles. Je lis ensuite les notes officielles et je décide si une vérification ou une mise à jour est nécessaire.

Le **26 octobre 2026**, j'ai vérifié manuellement les [notes de Pandas 3.1.0](https://pandas.pydata.org/docs/whatsnew/v3.1.0.html), publié le 22 octobre. Cette version améliore notamment la vitesse de certaines jointures. Le P13 utilise des jointures sur un petit lot : je n'ai pas mesuré de gain ni trouvé de correction qui impose une mise à jour immédiate.

Le **9 novembre 2026**, le script a repéré la version [pandas 3.1.1](https://github.com/pandas-dev/pandas/releases/tag/v3.1.1). Après lecture des notes, j'ai marqué cette version comme examinée et conservé la version utilisée dans le projet.

Le projet utilise `pandas==3.0.1`. Avant une mise à jour, je relirais les changements utiles au projet, puis je relancerais les contrôles et comparerais les résultats aux exports de référence. La [documentation du P13](Projets_OC/P13/output/pdf/Documentation_P13_Missions_1_2.pdf) garde le détail des sources, des essais et des décisions.
