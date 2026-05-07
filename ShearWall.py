import math
import os

# SHEAR WALL ANALYSIS & DESIGN - Updated to ACI 318-19 & ASCE 7-22
# Replaces SHEARSCR.BAS (1985)

def clear():
    os.system("cls" if os.name == "nt" else "clear")

# ---------- Code Constants ----------
PHI_FLEX = 0.9
PHI_SHEAR = 0.75
LAMBDA = 1.0   # Normal weight concrete

class WallPier:
    def __init__(self, name, h_ft, d_ft, t_in, x_ft, E_ksi):
        self.name = name
        self.H = h_ft * 12  # Convert to inches
        self.D = d_ft * 12  # Convert to inches
        self.T = t_in
        self.X = x_ft * 12  # Convert to inches (distance to CG)
        self.E = E_ksi * 1000 # Convert to psi
        self.A = self.D * self.T # Cross sectional area
        self.I = (self.T * self.D**3) / 12 # Moment of Inertia
        self.R = 0.0 # Rigidity
        self.V = 0.0 # Direct Shear (kips)
        self.M = 0.0 # Moment from torsion (ft-kips)
        self.Axial = 0.0 # Axial Load (kips) - Input later

    def calc_rigidity(self, type="Frame"):
        """ Calculates rigidity based on ACI 318 principles """
        # Rigidity = 1 / Delta
        # For a cantilever: Delta = (P * H^3) / (3 * E * I)
        if self.E == 0 or self.I == 0:
            self.R = 0
            return
            
        # Using Cantilever formula (dominant for shear walls)
        delta = (self.H**3) / (3 * self.E * self.I)
        self.R = 1 / delta if delta > 0 else 0

    def calc_shear_capacity(self, fc, fy, axial_load_k):
        """ ACI 318-19 §11.6.2 - Shear strength of walls """
        Acv = self.D * self.T
        # Concrete shear strength (simplified ACI Eq 11.6.2.1)
        # Vc = 2 * lambda * sqrt(fc) * Acv + 0.2 * (N_u * Acv / A_g)
        if axial_load_k > 0:
            Vc = (2 * LAMBDA * math.sqrt(fc) + 0.2 * (axial_load_k * 1000 / self.A)) * Acv / 1000 # kips
        else:
            Vc = 2 * LAMBDA * math.sqrt(fc) * Acv / 1000 # kips (no axial)
        
        phi_Vc = PHI_SHEAR * Vc
        return Vc, phi_Vc

    def check_boundary_elements(self, fc, fy, seismic_force_ratio):
        """ ACI 318-19 §18.10.6 - Special Boundary Elements """
        # Check if compression strain > 0.002 at extreme fiber
        # Simplified: if wall is in SDC D, E, or F and high shear
        # This is a placeholder for the complex strain compatibility check
        if seismic_force_ratio > 0.35: # Threshold for high seismic
            return True # Requires special boundary elements
        return False

def main():
    clear()
    print("SHEAR WALL DESIGN - ACI 318-19 / ASCE 7-22")
    print("-"*50)
    
    # Inputs
    fc = float(input("Concrete f'c (psi) [4000]: ") or 4000)
    fy = float(input("Steel f'y (psi) [60000]: ") or 60000)
    base_shear = float(input("Total Base Shear V (kips): "))
    num_piers = int(input("Number of Wall Piers: "))
    
    piers = []
    total_R = 0.0
    total_Rx = 0.0
    total_Rx2 = 0.0
    
    # Input Piers
    for i in range(num_piers):
        print(f"\n--- Pier {i+1} ---")
        name = input("Name: ")
        h = float(input("Height H (ft): "))
        d = float(input("Length D (ft): "))
        t = float(input("Thickness T (in): "))
        x = float(input("Distance to CG X (ft): "))
        E = float(input("Modulus E (ksi) [3000]: ") or 3000)
        
        pier = WallPier(name, h, d, t, x, E)
        pier.calc_rigidity()
        
        piers.append(pier)
        total_R += pier.R
        total_Rx += pier.R * pier.X
        total_Rx2 += pier.R * pier.X**2
        
    if total_R == 0:
        print("Error: Total Rigidity is zero.")
        return
        
    # Center of Rigidity (CR)
    X_cr = total_Rx / total_R
    J_t = total_Rx2 - (total_Rx**2 / total_R) # Torsional constant
    
    print(f"\nCenter of Rigidity (CR): {X_cr/12:.2f} ft")
    print(f"Torsional Constant J: {J_t:.2e}")
    
    # Distribute Shear
    for pier in piers:
        # Direct Shear
        pier.V = (pier.R / total_R) * base_shear
        
        # Torsional Shear (ASCE 7-22 §12.8.4.3)
        # M_t = V * (e) where e is eccentricity between CR and CM
        # Assume eccentricity e = 0.05 * Building Dimension (accidental torsion)
        # We'll use a simple accidental torsion model here
        e = 0.05 * (max(p.X for p in piers) - min(p.X for p in piers)) / 12 # ft
        M_t = base_shear * e * 12 # kip-in
        
        # Additional shear due to torsion
        if J_t > 0:
            V_t = M_t * pier.R * (pier.X - X_cr) / J_t
            pier.V += V_t / 1000 # kips
        
        # Check Shear Capacity
        Vc, phi_Vc = pier.calc_shear_capacity(fc, fy, pier.Axial)
        
        print(f"\nPier: {pier.name}")
        print(f"  Direct Shear: {pier.V:.2f} kips")
        print(f"  Shear Capacity (Vc): {Vc:.2f} kips, Phi*Vc: {phi_Vc:.2f} kips")
        if pier.V > phi_Vc:
            print("  WARNING: Shear exceeds capacity! Increase thickness or add steel.")
        else:
            print("  Shear OK.")

if __name__ == "__main__":
    main()
