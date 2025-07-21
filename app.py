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

check_password()  # Llama a la función antes de mostrar nada más

st.set_page_config(page_title="Simulador de Puntos - Zoom Poker", layout="wide")

st.title("Simulador de Puntos para Tablas de Clasificación de Zoom Poker")

st.sidebar.header("Configuración de la simulación")
total_hands = st.sidebar.slider("Total de manos a jugar", 100, 1000, 500, step=100)
attempts = total_hands // 100
mw_flop_rate = st.sidebar.slider("% de manos que ven el flop MW (3 jugadores)", 10, 100, 40) / 100
sim_runs = st.sidebar.number_input("Número de simulaciones a ejecutar", 1, 1000, 1)

st.markdown("""
### 🎯 Objetivo
Simular cuántos puntos puedes hacer en un reto de 500 manos (5 intentos de 100), donde solo cuenta el mejor intento para la clasificación.

### 📊 Reglas:
- Solo cuentan manos jugadas en Zoom con dinero real.
- Las manos deben ver el **flop con al menos 3 jugadores**.
- Solo puntúan combinaciones específicas de manos iniciales.

### 🔢 Sistema de puntuación
- **Pocket Aces**: 125 puntos
- **Pocket Kings**: 104 puntos
- **Pocket Queens**: 96 puntos
- **Pocket Jacks**: 88 puntos
- **Pocket Pairs (2-10)**: (7+7)x4 = 56 puntos
- **Suited Connectors**: (6+7)x2 = 26 puntos
""")

probabilities = {
    "Pocket Aces": 0.0045,
    "Pocket Kings": 0.0045,
    "Pocket Queens": 0.0045,
    "Pocket Jacks": 0.0045,
    "Pocket Pairs (2-10)": 0.055,
    "Suited Connectors": 0.03,
}

points = {
    "Pocket Aces": 125,
    "Pocket Kings": 104,
    "Pocket Queens": 96,
    "Pocket Jacks": 88,
    "Pocket Pairs (2-10)": 56,
    "Suited Connectors": 26,
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
            mw_hands = int(estimated_hands * mw_flop_rate)
            hand_points = mw_hands * points[hand_type]
            hand_results[hand_type] = mw_hands
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
### 📚 Recomendaciones Estratégicas
- Limpear más manos específicas para inducir MW flop.
- Evitar asustar a los rivales con 3-bets grandes.
- No aislarse preflop con premiums si eso reduce los puntos.
- Jugar muchas manos suited y pares bajos buscando volumen.

### 💸 Objetivo
Se puede llegar a **125 dólares diarios** si logras un intento que se acerque al top de la tabla de puntos. Con esta app puedes explorar tus chances y definir tu estrategia.
""")
