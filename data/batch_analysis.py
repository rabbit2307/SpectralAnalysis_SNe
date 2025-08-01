import json
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import spextractor
import traceback 

DATA_DIR = 'Supernovae Dataset' 
RESULTS_DIR = '../results' 
PAPER_CSV_PATH = 'sample_paper_data.csv' 
TEMP_FILENAME = 'temp_spectrum_for_analysis.dat'

if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)

def analyze_supernova(json_path, paper_df):
    """
    Analyzes a single supernova JSON file. It always returns a result dictionary
    for the final summary, but only saves individual files on success.
    """
    json_supernova_name = os.path.basename(json_path).replace('.json', '')
    
    try:
        with open(json_path, 'r') as f:
            input_data = json.load(f)

        json_key_name = list(input_data.keys())[0]
        supernova_data = input_data[json_key_name]
        print(f"--- Processing: {json_supernova_name} (Key: {json_key_name}) ---")

<<<<<<< HEAD
=======
        if json_supernova_name[0].isdigit():
            supernova_name_for_paper = f"SN{json_supernova_name}"
        else:
            supernova_name_for_paper = json_supernova_name
        
>>>>>>> ca43fffcdce855bd016bfb36b066cf3477600430
        if 'spectra' not in supernova_data or not supernova_data['spectra']:
            print(f"Skipping {json_supernova_name}: No spectral data found.")
            raise ValueError("No spectral data in JSON file.")
        
        spectral_data = supernova_data['spectra'][0].get('data', [])
        wavelengths = [float(point[0]) for point in spectral_data]
        fluxes = [float(point[1]) for point in spectral_data]

        np.savetxt(TEMP_FILENAME, np.transpose([wavelengths, fluxes]))
        
        supernova_type = supernova_data.get("claimedtype", [{}])[0].get("value", "Ia")
        redshift = float(supernova_data.get("redshift", [{}])[0].get("value", 0.0))

        analysis_type = supernova_type
        if 'Ia' in supernova_type and supernova_type != 'Ia':
            print(f"Found peculiar type '{supernova_type}', analyzing as standard 'Ia'.")
            analysis_type = 'Ia'

        pew, pew_err, vel, vel_err, _ = spextractor.process_spectra(
            TEMP_FILENAME, redshift, plot=False, type=analysis_type
        )
<<<<<<< HEAD
        
=======

        paper_row = paper_df[paper_df['supernova_name'] == supernova_name_for_paper]
        if paper_row.empty:
            print(f"Warning: No data found for '{supernova_name_for_paper}' in paper_data.csv")
            paper_results = {}
        else:
            paper_results = paper_row.iloc[0].to_dict()

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
        
        output_json_path = os.path.join(RESULTS_DIR, f"{json_supernova_name}_comparison.json")
        with open(output_json_path, 'w') as f:
            json.dump(combined_results, f, indent=4)

        plt.figure(figsize=(14, 8))
        plt.plot(wavelengths, fluxes, color='black', linewidth=1, label='Spectrum')
        plt.title(f"Analysis for {json_supernova_name}", fontsize=16)
        plt.xlabel("Wavelength (Å)", fontsize=12)
        plt.ylabel("Flux", fontsize=12)
        
>>>>>>> ca43fffcdce855bd016bfb36b066cf3477600430
        spex_pew = pew.get('Si II 6150A')
        analysis_successful = spex_pew is not None and not np.isnan(spex_pew)

        if not analysis_successful:
            print(f"Incomplete analysis for {json_supernova_name}: Key measurements (pEW) are invalid (nan).")

<<<<<<< HEAD
        if json_supernova_name.startswith('SN'):
             supernova_name_for_paper = json_supernova_name
        elif json_supernova_name[0].isdigit():
            supernova_name_for_paper = f"SN{json_supernova_name}"
        else:
            supernova_name_for_paper = json_supernova_name
            
        paper_row = paper_df[paper_df['supernova_name'] == supernova_name_for_paper]
        paper_results = paper_row.iloc[0].to_dict() if not paper_row.empty else {}
=======
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, f"{json_supernova_name}_comparison.png"), dpi=150)
        plt.close() 
>>>>>>> ca43fffcdce855bd016bfb36b066cf3477600430

        full_results = {
            "supernova_name": json_supernova_name,
            "analysis_results": {
                "pEW_SiII_6150A": pew.get('Si II 6150A'), "pEW_SiII_6150A_err": pew_err.get('Si II 6150A'),
                "v_SiII_6150A": vel.get('Si II 6150A'), "v_SiII_6150A_err": vel_err.get('Si II 6150A')
            },
            "paper_results": paper_results
        }

        if analysis_successful:
            output_json_path = os.path.join(RESULTS_DIR, f"{json_supernova_name}_comparison.json")
            with open(output_json_path, 'w') as f:
                json.dump(full_results, f, indent=4)

            plt.figure(figsize=(14, 8))
            plt.plot(wavelengths, fluxes, color='black', linewidth=1, label='Spectrum')
            plt.title(f"Analysis for {json_supernova_name}", fontsize=16)
            plt.xlabel("Wavelength (Å)", fontsize=12)
            plt.ylabel("Flux", fontsize=12)
            
            text_content = (
                f"Spextractor Results:\n"
                f"  pEW(Si II 6150Å): {pew.get('Si II 6150A'):.1f} ± {pew_err.get('Si II 6150A'):.1f}\n"
                f"  v(Si II 6150Å): {vel.get('Si II 6150A'):.1f} ± {vel_err.get('Si II 6150A'):.1f} (x10³ km/s)\n\n"
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
            plt.close()

        return full_results, True

    except Exception:
        print(f"!!! FAILED to process {json_supernova_name} !!!")
        traceback.print_exc()
        placeholder_result = {
            "supernova_name": json_supernova_name,
            "analysis_results": {}, "paper_results": {}
        }
        return placeholder_result, False
    finally:
        if os.path.exists(TEMP_FILENAME):
            os.remove(TEMP_FILENAME)

<<<<<<< HEAD
=======

>>>>>>> ca43fffcdce855bd016bfb36b066cf3477600430
if __name__ == "__main__":
    try:
        paper_df = pd.read_csv(PAPER_CSV_PATH)
    except FileNotFoundError:
        sys.exit(f"Error: The paper data file was not found at '{PAPER_CSV_PATH}'")

    json_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
    
    all_results = []
    success_count = 0
    failure_count = 0
    
    for i, filename in enumerate(json_files):
        print(f"\nProcessing file {i+1}/{len(json_files)}: {filename}")
        json_path = os.path.join(DATA_DIR, filename)
        result, success = analyze_supernova(json_path, paper_df)
        all_results.append(result) 
        
        if success:
            success_count += 1
        else:
            failure_count += 1
            
    summary_data = []
    for res in all_results:
        def format_value(val):
            if val is None or not isinstance(val, (int, float)) or np.isnan(val):
                return 'N/A'
            return round(val, 1)

        summary_data.append({
            'supernova_name': res.get('supernova_name', 'Unknown'),
            'spextractor_pEW': format_value(res.get('analysis_results', {}).get('pEW_SiII_6150A')),
            'spextractor_pEW_err': format_value(res.get('analysis_results', {}).get('pEW_SiII_6150A_err')),
            'paper_pEW': res.get('paper_results', {}).get('pEW_SiII_6355', 'N/A'),
            'paper_pEW_err': res.get('paper_results', {}).get('pEW_SiII_6355_err', 'N/A'),
            'spextractor_vel': format_value(res.get('analysis_results', {}).get('v_SiII_6150A')),
            'spextractor_vel_err': format_value(res.get('analysis_results', {}).get('v_SiII_6150A_err')),
            'paper_vel': res.get('paper_results', {}).get('v_SiII', 'N/A'),
            'paper_vel_err': res.get('paper_results', {}).get('v_SiII_err', 'N/A')
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(os.path.join(RESULTS_DIR, 'final_comparison_summary.csv'), index=False)
    
    print("\n\n--- Batch Analysis Complete ---")
    print(f"Total files processed: {len(json_files)}")
    print(f"Successful analyses: {success_count}")
    print(f"Failed analyses: {failure_count}")
    print(f"Results saved in the '{RESULTS_DIR}' directory.")
    print(f"A complete summary for all {len(json_files)} SNe can be found in '{os.path.join(RESULTS_DIR, 'final_comparison_summary.csv')}'")
