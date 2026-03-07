# Bot de trading Polymarket BTC 5 minutes

**🌐 Langue / Language:** [English](README.md) | [中文](README.zh-CN.md) | [Français](README.fr.md) | [Español](README.es.md)

**📞 Contact :** [S.E.I](https://t.me/sei_dev) (Telegram)

---

🤖 Bot de trading automatisé pour les marchés Polymarket BTC hausse/baisse de 5 minutes. Trade 24/7 avec trois stratégies :

| Stratégie | Description | Bot |
|-----------|-------------|-----|
| **Stratégie 1** | Arbitrage au milieu du marché | [@sei_arb_bot](https://t.me/sei_arb_bot) (~30 min) |
| **Stratégie 2** | Trading haute opportunité en fin de cycle | [@seitrading_bot](https://t.me/seitrading_bot) (~1 h) |
| **Stratégie 3** | Acheter UP ou DOWN ; quand la liquidité change, obtenir des parts gagnantes pour 0,01 $ | Bientôt |

📹 **Voir sur YouTube**

[![YouTube – Bot de trading Polymarket 5 min](https://img.youtube.com/vi/teeMT-c4S3o/maxresdefault.jpg)](https://www.youtube.com/watch?v=teeMT-c4S3o)

---

## Stratégie 1 : Arbitrage (milieu de marché)

Acheter les deux côtés, fusionner pour récupérer l'USDC. **Essayer en ~30 min :** [@sei_arb_bot](https://t.me/sei_arb_bot)
📹 **Démo :** [Voir sur YouTube](https://www.youtube.com/watch?v=NsRDKPQrRIs)

### Captures d'écran

|  |  |  |
|--|--|--|
| ![image1](assets/image1.png) | ![image2](assets/image2.png) | ![image3](assets/image3.png) |

| Résultat |
|----------|
| ![Result](assets/result.png) |

### Fonctionnalités

- 🔍 Découverte automatique des marchés – Trouve les marchés BTC 5 min actifs
- 📊 Gestion intelligente des positions – Surveille les positions UP/DOWN
- 🛡️ Protection des risques – Vente auto avant fermeture du marché
- 💰 Fusion de tokens – Récupère l'USDC des positions égales

### Fonctionnement

1. Trouve le marché BTC 5 min actuel  
2. Surveille les positions de tokens UP/DOWN  
3. Fusionne les positions égales pour récupérer l'USDC  
4. Force la vente avant fermeture du marché (seuil 30 s)  
5. Passe des ordres pour le prochain marché automatiquement  

---

## Stratégie 2 : Trading en fin de cycle

Trading haute opportunité en fin de cycle de marché. **Essayer en ~1 h :** [@seitrading_bot](https://t.me/seitrading_bot)

### Captures d'écran

| Résultat 1 |
|------------|
| ![Result 1](assets/result1.png) |

### Fonctionnalités

- Détection de haute opportunité en fin de cycle
- Timing et passation d'ordres automatisés
- Exposition à risque maîtrisé

### Fonctionnement

1. Surveille le marché 5 min actuel jusqu'à la résolution  
2. Identifie les moments à haute opportunité en fin de cycle  
3. Passe ou ajuste les ordres en conséquence  
4. Gère les positions et sort avant la fermeture du marché  

---

## Stratégie 3 : Gagner avec 0,01 $ quand la liquidité change (bientôt)

**Stratégie :** Vous achetez généralement **l'un des deux** UP et DOWN. Quand la liquidité du marché change, vous pouvez obtenir **des parts gagnantes pour 0,01 $** – risque minimal, même marché crypto hausse/baisse.

### Captures d'écran

| Résultat |
|----------|
| ![Result 2](assets/result2.png) |

### Fonctionnalités

- Risque ultra-faible – objectif 0,01 $ par côté (UP et/ou DOWN)
- Exploite les changements de liquidité du marché crypto 5 min
- Quand la liquidité change, des parts gagnantes à 0,01 $
- Même structure de marché ; entrée différente (un ou les deux côtés en taille minimale)

### Fonctionnement

1. Trouve le marché crypto hausse/baisse actuel  
2. Surveille la liquidité – achète UP et/ou DOWN (en général l'un des deux) à ~0,01 $  
3. Quand la liquidité a changé, les positions à 0,01 $ peuvent devenir des parts gagnantes  
4. Récupère le côté gagnant ou fusionne si les deux sont remplis ; répète pour le prochain marché  

---

## 🚀 Démarrage rapide

1. **Installer les dépendances :**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurer `.env` :**
   ```bash
   PRIVATE_KEY=0x...     # Clé privée du portefeuille
   ORDER_PRICE=0.01      # Prix des ordres à cours limité
   ORDER_SIZE=           # Taille des ordres
   ```

3. **Lancer le bot :**
   ```bash
   python main.py
   ```

---

## 📚 Documentation

- **Guide utilisateur :** [docs.md](docs.md) – Comment utiliser le bot TG et démarrer.
