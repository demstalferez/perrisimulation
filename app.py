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
flop_seen_rate = st.sidebar.slider("% de manos que ven el flop", 10, 100, 40) / 100
sim_runs = st.sidebar.number_input("Número de simulaciones a ejecutar", 1, 1000, 1)

st.markdown("""
### 🎯 Objetivo
Simular cuántos puntos puedes hacer en un reto de 500 manos (5 intentos de 100), donde solo cuenta el mejor intento para la clasificación.

### 📊 Reglas oficiales (según la promoción)
- Solo cuentan las **primeras 100 manos** jugadas tras la inscripción cada día.
- Se permiten hasta **5 intentos diarios por stake**, cuenta solo el mejor.
- La mano debe **ver el flop** para puntuar (ya no es necesario que sea multiway).
- Los puntos se asignan sumando el valor de las cartas: A=14, K=13, Q=12, J=11...

### 🔢 Multiplicadores y puntos fijos
| Tipo de mano              | Puntuación          |
|---------------------------|---------------------|
| Ases de mano (AA)         | 125 puntos fijos    |
| Reyes de mano (KK)        | 104 puntos fijos    |
| Damas de mano (QQ)        | 96 puntos fijos     |
| Jotas de mano (JJ)        | 88 puntos fijos     |
| Parejas (2–10)            | (val1 + val2) × 4   |
| Conectores suited         | (val1 + val2) × 2   |
| Cualquier otra mano       | val1 + val2         |

En caso de empate, el primero en jugar la última mano válida ese día queda mejor clasificado.

---
""")

probabilities = {
    "Pocket Aces": 0.0045,
    "Pocket Kings": 0.0045,
    "Pocket Queens": 0.0045,
    "Pocket Jacks": 0.0045,
    "Pocket Pairs (2-10)": 0.055,
    "Suited Connectors": 0.03,
}

# Simulación

def run_simulation():
    sim_data = []
    for i in range(attempts):
        hand_count = 100
        hand_results = {}
        total_points = 0

        for hand_type, prob in probabilities.items():
            estimated_hands = np.random.binomial(hand_count, prob)
            flop_seen_hands = int(estimated_hands * flop_seen_rate)
            
            hand_points = 0
            if hand_type == "Pocket Aces":
                hand_points = flop_seen_hands * 125
            elif hand_type == "Pocket Kings":
                hand_points = flop_seen_hands * 104
            elif hand_type == "Pocket Queens":
                hand_points = flop_seen_hands * 96
            elif hand_type == "Pocket Jacks":
                hand_points = flop_seen_hands * 88
            elif hand_type == "Pocket Pairs (2-10)":
                # Random valor entre 2 y 10
                values = np.random.randint(2, 11, size=flop_seen_hands)
                hand_points = np.sum((values + values) * 4)
            elif hand_type == "Suited Connectors":
                # Random conectores entre 3 y 11 (J)
                values = np.random.randint(3, 12, size=flop_seen_hands)
                hand_points = np.sum((values + (values + 1)) * 2)

            hand_results[hand_type] = flop_seen_hands
            total_points += hand_points

        sim_data.append({
            "Intento": i + 1,
            **hand_results,
            "Puntos Totales": total_points
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
- Juega manos que maximizan el multiplicador (suited connectors, pares bajos).
- No hagas foldear a los villanos preflop: juega slow para ver el flop.
- Aumenta volumen jugando muchas manos, no solo premiums.
- Puedes hacer hasta **5 intentos diarios**. Solo el mejor puntúa.

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