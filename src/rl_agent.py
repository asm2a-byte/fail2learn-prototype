# rl_agent.py
import pandas as pd

# Charger le fichier de données
data = pd.read_csv("data/failures_data.csv")

# Traduire les solvants en chiffres
solvent_map = {
    "water": 0,
    "ethanol": 1,
    "acetone": 2,
    "methanol": 3,
    "dichloromethane": 4
}
data["solvent_id"] = data["solvent"].map(solvent_map)

# Voir à quoi ça ressemble
print(data[["temperature_C", "solvent_id", "pH", "reaction_time_min", "result"]].head())
