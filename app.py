import streamlit as st
import pandas as pd
import numpy as np

# --- Autenticación simple por contraseña ---
def check_password():
    def password_entered():
        if st.session_state["password"] == "perri69":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Contraseña", type="password", on_change=password_entered, key="password")
        st.stop()
    elif not st.session_state["password_correct"]:
        st.text_input("Contraseña", type="password", on_change=password_entered, key="password")
        st.error("Contraseña incorrecta.")
        st.stop()

check_password()

st.set_page_config(page_title="Simulador de Puntos - Zoom Poker", layout="wide")

st.title("Simulador de Puntos para Tablas de Clasificación de Zoom Poker")

st.sidebar.header("Configuración de la simulación")
total_hands = st.sidebar.slider("Total de manos a jugar", 100, 1000, 500, step=100)
attempts = total_hands // 100
sim_runs = st.sidebar.number_input("Número de simulaciones a ejecutar", 1, 1000, 1)

st.markdown("""
### 🎯 Objetivo
Simular cuántos puntos puedes hacer en un reto de 500 manos (5 intentos de 100), donde solo cuenta el mejor intento para la clasificación.

### 📊 Reglas oficiales (según la promoción)
- Solo cuentan las **primeras 100 manos** jugadas tras la inscripción cada día.
- Se permiten hasta **5 intentos diarios por stake**, cuenta solo el mejor.
- **No es necesario ver el flop**: basta con recibir las cartas en una mano válida.
- La mano debe haberse jugado en una mesa con al menos **3 jugadores sentados**.

### 🔢 Sistema de puntuación
| Tipo de mano              | Puntuación          |
|---------------------------|---------------------|
| Ases de mano (AA)         | 125 puntos fijos    |
| Reyes de mano (KK)        | 104 puntos fijos    |
| Damas de mano (QQ)        | 96 puntos fijos     |
| Jotas de mano (JJ)        | 88 puntos fijos     |
| Parejas (2–10)            | (val1 + val2) × 4   |
| Conectores suited         | (val1 + val2) × 2   |
| Cualquier otra mano       | val1 + val2         |

---
""")

# Simulación real de manos

def generar_mano():
    valores = list(range(2, 15))  # 2 a As (14)
    palos = ["♠", "♥", "♦", "♣"]
    carta1 = (np.random.choice(valores), np.random.choice(palos))
    carta2 = (np.random.choice(valores), np.random.choice(palos))
    return carta1, carta2

def calcular_puntos(c1, c2):
    v1, p1 = c1
    v2, p2 = c2
    if v1 == v2:
        if v1 == 14:
            return 125
        elif v1 == 13:
            return 104
        elif v1 == 12:
            return 96
        elif v1 == 11:
            return 88
        elif 2 <= v1 <= 10:
            return (v1 + v2) * 4
    elif abs(v1 - v2) == 1 and p1 == p2:
        return (v1 + v2) * 2
    else:
        return v1 + v2

# Simulación por intento

def run_simulation():
    sim_data = []
    for intento in range(1, attempts + 1):
        puntos = 0
        tipo_manos = {
            "AA": 0, "KK": 0, "QQ": 0, "JJ": 0,
            "Parejas (2–10)": 0,
            "Conectores suited": 0,
            "Otras manos": 0
        }
        for _ in range(100):
            c1, c2 = generar_mano()
            score = calcular_puntos(c1, c2)
            puntos += score

            if c1[0] == c2[0]:
                if c1[0] == 14:
                    tipo_manos["AA"] += 1
                elif c1[0] == 13:
                    tipo_manos["KK"] += 1
                elif c1[0] == 12:
                    tipo_manos["QQ"] += 1
                elif c1[0] == 11:
                    tipo_manos["JJ"] += 1
                elif 2 <= c1[0] <= 10:
                    tipo_manos["Parejas (2–10)"] += 1
            elif abs(c1[0] - c2[0]) == 1 and c1[1] == c2[1]:
                tipo_manos["Conectores suited"] += 1
            else:
                tipo_manos["Otras manos"] += 1

        sim_data.append({
            "Intento": intento,
            **tipo_manos,
            "Puntos Totales": puntos
        })
    return pd.DataFrame(sim_data)

for i in range(sim_runs):
    df = run_simulation()
    st.subheader(f"Resultado de la simulación {i+1}")
    st.dataframe(df)
    best_attempt = df.loc[df["Puntos Totales"].idxmax()]
    st.success(f"El mejor intento (# {int(best_attempt['Intento'])}) logró {int(best_attempt['Puntos Totales'])} puntos")

st.markdown("""
---
### 💡 Recomendaciones Estratégicas
- Todas las manos jugadas cuentan, no hace falta llegar al flop.
- La clave es volumen + buscar manos que tengan multiplicador.
- Juega con constancia hasta lograr el intento con más puntos.

### 💸 Premios diarios (stake 0,25€/0,50€)
| Puesto | Premio   |
|--------|----------|
| 1º     | 125 €    |
| 2º     | 100 €    |
| 3º     | 85 €     |
| 4º     | 65 €     |
| 5º     | 50 €     |
| 6º-10º | 30 €     |
| 11º-15º| 20 €     |

¡Con constancia, puedes llevarte un buen extra diario!
""")
