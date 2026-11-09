# ==============================================================================
# 🏛️ ELKEM ASA TECHNOLOGY — UNIVERSAL CSV ANALYSESKRIPT & BANANA CURVE
# ==============================================================================
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def run_analysis():
    data_dir = "./data" if os.path.exists("./data") else "."
    print(f"📂 Søker etter CSV-filer i '{data_dir}'...\n")

    banana_file = os.path.join(data_dir, "09_p6_banana_curve_early_late.csv")
    if os.path.exists(banana_file):
        df_b = pd.read_csv(banana_file)
        print("------------------------------------------------------------------")
        print("🍌 PRIMAVERA P6 BANANA CURVE ANALYSE (Early vs Late Start S-Kurve)")
        print("------------------------------------------------------------------")
        print(df_b.to_string(index=False))

        plt.figure(figsize=(10, 5))
        plt.plot(df_b['Month'], df_b['Early_Start_PV_NOK'] / 1e6, 'b-o', label='Early Start S-Curve (Øvre grense)', linewidth=2)
        plt.plot(df_b['Month'], df_b['Late_Start_PV_NOK'] / 1e6, 'r-o', label='Late Start S-Curve (Nedre grense)', linewidth=2)
        plt.plot(df_b['Month'], df_b['Actual_EV_NOK'] / 1e6, 'g--s', label='Faktisk Fremdrift (EV / BCWP)', linewidth=2.5)

        plt.fill_between(df_b['Month'], df_b['Late_Start_PV_NOK'] / 1e6, df_b['Early_Start_PV_NOK'] / 1e6, color='khaki', alpha=0.35, label='Banana Envelope (Tillatt slakk-område)')
        plt.title('Primavera P6 Banana Curve — CA-5020 (Fiskå 2026)', fontsize=14, fontweight='bold')
        plt.xlabel('Måned (2026)')
        plt.ylabel('Akkumulert Verdi (MNOK)')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend(loc='upper left')
        plt.tight_layout()
        plt.savefig('banana_curve_plot.png', dpi=150)
        print("\n✓ Banana Curve-graf lagret som 'banana_curve_plot.png'.")

if __name__ == "__main__":
    run_analysis()
