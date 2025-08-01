import json
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import spextractor

# --- CONFIGURATION ---
# This script is designed to be run from inside the 'data' directory.
# The JSON files are in the 'Supernovae Dataset' subdirectory.
DATA_DIR = 'Supernovae Dataset' 
# Results will be created one level up, outside the data directory.
RESULTS_DIR = '../results' 
# The paper CSV is also in the current directory.
PAPER_CSV_PATH = 'sample_paper_data.csv' 
TEMP_FILENAME = 'temp_spectrum_for_analysis.dat'

# Create the results directory if it doesn't exist
if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)

# --- MAIN ANALYSIS FUNCTION ---
def analyze_supernova(json_path, paper_df):
    """
    Analyzes a single supernova JSON file, compares it to paper data,
    and saves the results and a plot.
    """
    try:
        # --- 1. Load and Extract Data from JSON ---
        with open(json_path, 'r') as f:
            input_data = json.load(f)

        json_supernova_name = list(input_data.keys())[0]
        supernova_data = input_data[json_supernova_name]
        print(f"--- Processing: {json_supernova_name} ---")

        # --- Standardize supernova name to match CSV ---
        # If the name from JSON starts with a digit (e.g., "2005de"), prepend "SN"
        if json_supernova_name[0].isdigit():
            supernova_name_for_paper = f"SN{json_supernova_name}"
        else:
            supernova_name_for_paper = json_supernova_name
        
        # Extract spectral data
        if 'spectra' not in supernova_data or not supernova_data['spectra']:
            print(f"Skipping {json_supernova_name}: No spectral data found.")
            return None
        
        spectral_data = supernova_data['spectra'][0].get('data', [])
        wavelengths = [float(point[0]) for point in spectral_data]
        fluxes = [float(point[1]) for point in spectral_data]

        # --- 2. Run Spextractor ---
        np.savetxt(TEMP_FILENAME, np.transpose([wavelengths, fluxes]))
        
        supernova_type = supernova_data.get("claimedtype", [{}])[0].get("value", "Ia")
        redshift = float(supernova_data.get("redshift", [{}])[0].get("value", 0.0))

        pew, pew_err, vel, vel_err, _ = spextractor.process_spectra(
            TEMP_FILENAME, redshift, plot=False, type=supernova_type
        )

        # --- 3. Get Comparison Data from Paper ---
        paper_row = paper_df[paper_df['supernova_name'] == supernova_name_for_paper]
        if paper_row.empty:
            print(f"Warning: No data found for '{supernova_name_for_paper}' in paper_data.csv")
            paper_results = {}
        else:
            paper_results = paper_row.iloc[0].to_dict()

        # --- 4. Combine and Save Results ---
        # Use .get() to avoid errors if a key doesn't exist in the results
        combined_results = {
            "supernova_name": json_supernova_name,
            "metadata": {
                "type": supernova_type,
                "redshift": redshift
            },
            "analysis_results": {
                "pEW_SiII_6150A": pew.get('Si II 6150A'),
                "pEW_SiII_6150A_err": pew_err.get('Si II 6150A'),
                "v_SiII_6150A": vel.get('Si II 6150A'),
                "v_SiII_6150A_err": vel_err.get('Si II 6150A')
            },
            "paper_results": {
                "pEW_SiII_6355": paper_results.get('pEW_SiII_6355'),
                "pEW_SiII_6355_err": paper_results.get('pEW_SiII_6355_err'),
                "v_SiII": paper_results.get('v_SiII'),
                "v_SiII_err": paper_results.get('v_SiII_err')
            }
        }
        
        # Save detailed JSON output for this SN
        output_json_path = os.path.join(RESULTS_DIR, f"{json_supernova_name}_comparison.json")
        with open(output_json_path, 'w') as f:
            json.dump(combined_results, f, indent=4)

        # --- 5. Generate Comparison Plot ---
        plt.figure(figsize=(14, 8))
        plt.plot(wavelengths, fluxes, color='black', linewidth=1, label='Spectrum')
        plt.title(f"Analysis for {json_supernova_name}", fontsize=16)
        plt.xlabel("Wavelength (Å)", fontsize=12)
        plt.ylabel("Flux", fontsize=12)
        
        # Add a text box with the comparison
        # Use .get() with a default value to handle missing data gracefully
        spex_pew = pew.get('Si II 6150A')
        spex_pew_err = pew_err.get('Si II 6150A')
        spex_vel = vel.get('Si II 6150A')
        spex_vel_err = vel_err.get('Si II 6150A')

        text_content = (
            f"Spextractor Results:\n"
            f"  pEW(Si II 6150Å): {spex_pew:.2f} ± {spex_pew_err:.2f}\n" if spex_pew is not None else ""
            f"  v(Si II 6150Å): {spex_vel:.2f} ± {spex_vel_err:.2f} (x10³ km/s)\n\n" if spex_vel is not None else ""
            f"Paper Results:\n"
            f"  pEW(Si II 6355Å): {paper_results.get('pEW_SiII_6355', 'N/A')} ± {paper_results.get('pEW_SiII_6355_err', 'N/A')}\n"
            f"  v(Si II): {paper_results.get('v_SiII', 'N/A')} ± {paper_results.get('v_SiII_err', 'N/A')} (x10³ km/s)"
        )
        plt.text(0.05, 0.95, text_content, transform=plt.gca().transAxes, fontsize=10,
                 verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.5))

        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, f"{json_supernova_name}_comparison.png"), dpi=150)
        plt.close() # Close the plot to free up memory

        return combined_results

    except Exception as e:
        print(f"!!! FAILED to process {json_path}: {e}")
        return None
    finally:
        if os.path.exists(TEMP_FILENAME):
            os.remove(TEMP_FILENAME)

# --- SCRIPT EXECUTION ---
if __name__ == "__main__":
    # Load the paper data once
    try:
        paper_df = pd.read_csv(PAPER_CSV_PATH)
    except FileNotFoundError:
        sys.exit(f"Error: The paper data file was not found at '{PAPER_CSV_PATH}'")

    # Get the list of all JSON files to process
    json_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
    
    all_results = []
    
    # Loop through each file and analyze it
    for i, filename in enumerate(json_files):
        print(f"\nProcessing file {i+1}/{len(json_files)}: {filename}")
        json_path = os.path.join(DATA_DIR, filename)
        result = analyze_supernova(json_path, paper_df)
        if result:
            all_results.append(result)
            
    # --- Create a final summary CSV ---
    summary_data = []
    for res in all_results:
        summary_data.append({
            'supernova_name': res['supernova_name'],
            'spextractor_pEW': res['analysis_results']['pEW_SiII_6150A'],
            'paper_pEW': res['paper_results']['pEW_SiII_6355'],
            'spextractor_vel': res['analysis_results']['v_SiII_6150A'],
            'paper_vel': res['paper_results']['v_SiII']
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(os.path.join(RESULTS_DIR, 'final_comparison_summary.csv'), index=False)
    
    print("\n\n--- Batch Analysis Complete ---")
    print(f"Results saved in the '{RESULTS_DIR}' directory.")
    print(f"A full summary can be found in '{os.path.join(RESULTS_DIR, 'final_comparison_summary.csv')}'")
