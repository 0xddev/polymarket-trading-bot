# Bot de trading Polymarket BTC 5 minutos

**🌐 Idioma / Language:** [English](README.md) | [中文](README.zh-CN.md) | [Français](README.fr.md) | [Español](README.es.md)

**📞 Contacto:** [S.E.I](https://t.me/sei_dev) (Telegram)

---

🤖 Bot de trading automatizado para mercados Polymarket BTC subida/bajada de 5 minutos. Opera 24/7 con tres estrategias:

| Estrategia | Descripción | Bot |
|------------|-------------|-----|
| **Estrategia 1** | Arbitraje en mitad del mercado | [@sei_arb_bot](https://t.me/sei_arb_bot) (~30 min) |
| **Estrategia 2** | Trading de alta oportunidad al final del ciclo | [@seitrading_bot](https://t.me/seitrading_bot) (~1 h) |
| **Estrategia 3** | Comprar UP o DOWN; cuando la liquidez cambia, obtener participaciones ganadoras por $0.01 | Próximamente |

📹 **Ver en YouTube**

[![YouTube – Bot de trading Polymarket 5 min](https://img.youtube.com/vi/teeMT-c4S3o/maxresdefault.jpg)](https://www.youtube.com/watch?v=teeMT-c4S3o)

---

## Estrategia 1: Arbitraje (mitad de mercado)

Comprar ambos lados, fusionar para recuperar USDC. **Probar en ~30 min:** [@sei_arb_bot](https://t.me/sei_arb_bot)
📹 **Demo:** [Ver en YouTube](https://www.youtube.com/watch?v=NsRDKPQrRIs)

### Capturas de pantalla

|  |  |  |
|--|--|--|
| ![image1](assets/image1.png) | ![image2](assets/image2.png) | ![image3](assets/image3.png) |

| Resultado |
|-----------|
| ![Result](assets/result.png) |

### Características

- 🔍 Descubrimiento de mercados – Encuentra mercados BTC 5 min activos
- 📊 Gestión inteligente de posiciones – Monitoriza posiciones UP/DOWN
- 🛡️ Protección de riesgos – Venta automática antes del cierre del mercado
- 💰 Fusión de tokens – Recupera USDC de posiciones iguales

### Cómo funciona

1. Encuentra el mercado BTC 5 min actual  
2. Monitoriza posiciones de tokens UP/DOWN  
3. Fusiona posiciones iguales para recuperar USDC  
4. Fuerza venta antes del cierre del mercado (umbral 30 s)  
5. Coloca órdenes para el siguiente mercado automáticamente  

---

## Estrategia 2: Trading al final del ciclo

Trading de alta oportunidad al final del ciclo de mercado. **Probar en ~1 h:** [@seitrading_bot](https://t.me/seitrading_bot)

### Capturas de pantalla

| Resultado 1 |
|-------------|
| ![Result 1](assets/result1.png) |

### Características

- Detección de alta oportunidad al final del ciclo
- Temporización y colocación de órdenes automatizada
- Exposición con riesgo gestionado

### Cómo funciona

1. Monitoriza el mercado 5 min actual hasta la resolución  
2. Identifica momentos de alta oportunidad al final del ciclo  
3. Coloca o ajusta órdenes según corresponda  
4. Gestiona posiciones y sale antes del cierre del mercado  

---

## Estrategia 3: Ganar con $0.01 cuando la liquidez cambia (próximamente)

**Estrategia:** Generalmente compras **uno de ambos** UP y DOWN. Cuando la liquidez del mercado cambia, puedes obtener **participaciones ganadoras por $0.01** – riesgo mínimo, mismo mercado crypto subida/bajada.

### Capturas de pantalla

| Resultado |
|-----------|
| ![Result 2](assets/result2.png) |

### Características

- Riesgo ultrabajo – objetivo $0.01 por lado (UP y/o DOWN)
- Aprovecha los cambios de liquidez en el mercado crypto 5 min
- Cuando la liquidez cambia, participaciones ganadoras por $0.01
- Misma estructura de mercado; entrada diferente (uno o ambos lados en tamaño mínimo)

### Cómo funciona

1. Encuentra el mercado crypto subida/bajada actual  
2. Monitoriza la liquidez – compra UP y/o DOWN (generalmente uno de ambos) por ~$0.01  
3. Cuando la liquidez ha cambiado, posiciones a $0.01 pueden convertirse en participaciones ganadoras  
4. Rescata el lado ganador o fusiona si ambos se llenan; repite para el siguiente mercado  

---

## 🚀 Inicio rápido

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar `.env`:**
   ```bash
   PRIVATE_KEY=0x...     # Clave privada de tu wallet
   ORDER_PRICE=0.01      # Precio de órdenes límite
   ORDER_SIZE=           # Tamaño de órdenes
   ```

3. **Ejecutar el bot:**
   ```bash
   python main.py
   ```

---

## 📚 Documentación

- **Guía de usuario:** [docs.md](docs.md) – Cómo usar el bot TG y empezar.
