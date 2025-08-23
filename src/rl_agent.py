# rl_agent.py
import pandas as pd
import random
import numpy as np

# 1. Charger les données
data = pd.read_csv("data/failures_data.csv")

# 2. Mapper les solvants en ID numériques
solvent_map = {
    "water": 0,
    "ethanol": 1,
    "acetone": 2,
    "methanol": 3,
    "dichloromethane": 4
}
data["solvent_id"] = data["solvent"].map(solvent_map)

# 3. Préparer les états (paramètres) et récompenses (résultat)
states = []
rewards = []

for i in range(len(data)):
    state = (
        int(data["temperature_C"][i] // 5),     # Regrouper par tranches de 5°C
        data["solvent_id"][i],
        int(data["pH"][i]),                     # Arrondi vers le bas
        int(data["reaction_time_min"][i] // 5)  # Tranches de 5 minutes
    )
    reward = data["result"][i]  # 1 = succès, 0 = échec
    states.append(state)
    rewards.append(reward)

# 4. Créer la Q-table (dictionnaire : état → score)
q_table = {}

for i, state in enumerate(states):
    if state not in q_table:
        q_table[state] = 0
    # Ajouter +1 si succès, -1 si échec
    q_table[state] += 1 if rewards[i] == 1 else -1

# 5. Fonction pour proposer une nouvelle stratégie (hors zones négatives)
def propose_strategy():
    while True:
        # Tirer au hasard un état
        temp = random.randint(10, 20) * 5
        solvent_id = random.randint(0, 4)
        pH = random.randint(3, 9)
        time = random.randint(2, 12) * 5

        state = (temp // 5, solvent_id, pH, time // 5)

        if q_table.get(state, 0) >= 0:
            # On a trouvé une zone "safe"
            reverse_map = {v: k for k, v in solvent_map.items()}
            return {
                "temperature_C": temp,
                "solvent": reverse_map[solvent_id],
                "pH": pH,
                "reaction_time_min": time
            }

# 6. Tester la suggestion
if __name__ == "__main__":
    print(" Suggested experimental strategy:")
    suggestion = propose_strategy()
    for key, value in suggestion.items():
        print(f"→ {key}: {value}")
