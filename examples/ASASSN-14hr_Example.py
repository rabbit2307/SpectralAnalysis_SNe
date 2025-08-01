import json
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import spextractor

INPUT_JSON_FILENAME = "/mnt/c/Users/Lenovo/OneDrive/Desktop/Supernova/Model Comparison/Sample Supernovae Dataset/ASASSN-14hr.json"
OUTPUT_PLOT_FILENAME = 'supernova_spectrum.png'
JSON_OUTPUT_FILENAME = 'supernova_analysis_results.json'
TEMP_FILENAME = 'temp_spectrum.dat' 

pew = {}
pew_err = {}
vel = {}
vel_err = {}
wavelengths = []
fluxes = []

try:
    print(f"Reading data from {INPUT_JSON_FILENAME}...")
    with open(INPUT_JSON_FILENAME, 'r') as f:
        input_data = json.load(f)

    supernova_name = list(input_data.keys())[0]
    supernova_data = input_data[supernova_name]

    if 'spectra' in supernova_data and len(supernova_data['spectra']) > 0:
        spectral_data = supernova_data['spectra'][0].get('data', [])
        wavelengths = [float(point[0]) for point in spectral_data]
        fluxes = [float(point[1]) for point in spectral_data]
        print("Spectral data extracted successfully.")
        
        np.savetxt(TEMP_FILENAME, np.transpose([wavelengths, fluxes]))
        
        supernova_type = supernova_data.get("claimedtype", [{}])[0].get("value", "Ia")
        redshift = float(supernova_data.get("redshift", [{}])[0].get("value", 0.0))
        
        print(f"\nAnalyzing with spextractor (Type: {supernova_type}, Redshift: {redshift})...")
        
        pew, pew_err, vel, vel_err, gp_model = spextractor.process_spectra(
            TEMP_FILENAME, 
            redshift, 
            downsampling=3, 
            plot=False, 
            type=supernova_type,
            sigma_outliers=3
        )
        print("Spextractor analysis complete.")

    else:
        print("Warning: No spectral data found in the JSON file.")

    print("\nData loaded and processed successfully.")

    print("\nPseudo-Equivalent Widths (Å):")
    if pew:
        for key in sorted(pew):
            print(f"{key}: {pew[key]:.2f} ± {pew_err[key]:.2f}")
    else:
        print("No pEW data could be calculated.")

    print("\nVelocities (10^3 km/s):")
    if vel:
        for key in sorted(vel):
            print(f"{key}: {vel[key]:.2f} ± {vel_err[key]:.2f}")
    else:
        print("No velocity data could be calculated.")

    output_data = {
        "metadata": {
            "source_type": supernova_type,
            "redshift": redshift,
            "plot_file": OUTPUT_PLOT_FILENAME,
            "source_file": INPUT_JSON_FILENAME
        },
        "pseudo_equivalent_widths_A": {
            key: {"value": round(pew[key], 2), "error": round(pew_err[key], 2)}
            for key in sorted(pew)
        },
        "velocities_10e3_km_s": {
            key: {"value": round(vel[key], 2), "error": round(vel_err[key], 2)}
            for key in sorted(vel)
        }
    }

    with open(JSON_OUTPUT_FILENAME, 'w') as json_file:
        json.dump(output_data, json_file, indent=4)
    
    print(f"\nAnalysis results saved to {JSON_OUTPUT_FILENAME}")

except FileNotFoundError:
    sys.exit(f"Error: The input file was not found at {INPUT_JSON_FILENAME}")
except Exception as e:
    sys.exit(f"An error occurred during processing: {e}")
finally:
    if os.path.exists(TEMP_FILENAME):
        os.remove(TEMP_FILENAME)
        print(f"Cleanup: Removed temporary file '{TEMP_FILENAME}'")

plt.figure(figsize=(12, 7))
if wavelengths and fluxes:
    plt.plot(wavelengths, fluxes, color='royalblue', linewidth=1, label='Original Spectrum')
    plt.title(f'Spectrum for {supernova_name}')
    plt.xlabel("Wavelength (Å)")
    plt.ylabel("Flux (erg/s/cm²/Å)")
    plt.legend()
else:
    plt.plot([], []) # Create an empty plot if no data
    plt.title('No Spectral Data to Plot')
    plt.xlabel("Wavelength (Å)")
    plt.ylabel("Flux")

plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig(OUTPUT_PLOT_FILENAME, dpi=300)

print(f"Plot saved to {OUTPUT_PLOT_FILENAME}")
