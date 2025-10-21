# Formula 1 Monte Carlo Simulation by Hiba Awais 
# October 6, 2025 

# A simulation for the probability an given driver can win the current season given the current points
# standings, race win probabilities per drivers, and track intensities 
# Note: The data used is based on assumptions, but this program can be modified to analyze based on historical 
# data. All current driver information is based on Oct 6, 2025.

import numpy as np, random
import matplotlib.pyplot as plt 

def monte_carlo():
    N = 30000 # Number of simulations, 30,000
    verst_wins = 0.0 # For F1 2025, I am looking at Max Verstappen's Championship possiblity
    ties = 0
    final_v = np.zeros(N, dtype=int)
    final_top = np.zeros(N, dtype=int)

    # Used basic Monte Carlo Sim structure for Max Verstappen win
    for sim in range(N):
        pts = np.array([start_pts[d] for d in drivers],dtype=int)
        for r in range(len(track_seq)):
            t = track_seq[r]
            adj_main   = base_main*mods[t]; adj_main   = adj_main/adj_main.sum()
            adj_sprint = base_sprint*mods[t]; adj_sprint= adj_sprint/adj_sprint.sum()
            # sprint
            if r in sprint_weeks:
                idxs = samp_order(adj_sprint); pts += alloc_sprint(idxs)
            # main
            idxm = samp_order(adj_main); add = alloc_main(idxm); add = maybe_dnf(add); pts += add
        mx = pts.max(); winners = np.where(pts==mx)[0]
        if 2 in winners:  # index 2 = Verstappen
            if len(winners)==1: verst_wins += 1.0
            else: verst_wins += 1.0/len(winners); ties += 1
        final_v[sim] = pts[2]; final_top[sim] = mx
    
    # Plot the Simulation results
    prob = verst_wins/N
    print(f"Estimated P(Verstappen champion): {prob*100:.3f}% (N={N})")
    print(f"Avg Verstappen final pts: {final_v.mean():.2f}, Avg season leader pts: {final_top.mean():.2f}, tie fraction: {ties/N:.6f}")

    diff = final_v - final_top
    plt.hist(diff,bins=60)
    plt.axvline(0,linestyle='--')
    plt.title(f"Verstappen pts - Season leader pts (track-dependent). P={prob*100:.3f}%")
    plt.xlabel("Verstappen Points – Season Leader Points")
    plt.ylabel("Frequency of Simulated Seasons")
    plt.show()

def samp_order(probs):
    noise = np.random.gamma(1, 0.25, size = probs.shape) # Add random noise to account for other variables
    scores = probs*noise
    return np.argsort(-scores) # Sort by finishing order 

# Helper function to give driver points based on their place in the race (index) 
def alloc_main(index):
    points = np.zeros(len(drivers), dtype = int)
    # Add main race points to driver
    for pos in range(min(10, len(index))):
        points[index[pos]] += main_pts[pos]
    return points

# Helper function to give driver points based on their place in the sprint (index) 
def alloc_sprint(index):
    points = np.zeros(len(drivers), dtype = int)
    for pos in range(min(8, len(index))):
        points[index[pos]] += sprint_pts[pos]
    return points

# Assume 5% DNF rate for each race 
def maybe_dnf(points):
    for i,d in enumerate(drivers):
        if np.random.rand() < 0.05:
            points[i] = 0
    return points

def main():
    global drivers, start_pts, base_main, base_sprint, main_pts, sprint_pts, mods, track_seq, sprint_weeks
    # Vector of Current Top 6 Drivers for F1 2025 Season 
    drivers = ["Piastri", "Norris", "Verstappen", "Russell", "Leclerc", "Hamilton"]
    # Dictionary of Current Top 6 Drivers Point Standings as of Oct 6, 2025 
    # start_pts = {"Piastri":336, "Norris": 314, "Verstappen": 273, "Russell": 237, "Leclerc": 173, "Hamilton": 125}
    start_pts = {"Piastri":346, "Norris": 332, "Verstappen": 306, "Russell": 252, "Leclerc": 192, "Hamilton": 142}

    # Base probabilities of each driver winning a main race and sprint, indices line up with drivers vector
    # Note: Assumptions are made based off of previous races but are not exact, can be changed to simulate different scenarios
    base_main = np.array([0.26, 0.23, 0.28, 0.08, 0.08, 0.07])
    base_sprint = np.array([0.25, 0.22, 0.30, 0.10, 0.08, 0.05])
    # base_main = np.array([0.30, 0.25, 0.20, 0.06, 0.05, 0.04]) # Main race probabilities 
    # base_sprint = np.array([0.28, 0.24, 0.22, 0.11, 0.07, 0.05]) # Sprint probabilities

    # Official FIA point system for main races and sprints 
    main_pts   = [25,18,15,12,10,8,6,4,2,1]
    sprint_pts = [8,7,6,5,4,3,2,1]

    # Track modifiers: Scale the win probability based on the track type (By constructor)
    # Ex: Oracle Red Bull performs 'better' in high downforce tracks (in the current season) so the weight is higher than McLaren's
    mods = {
        "High"   : np.array([0.90,0.90,1.30,1.05,1.00,0.95]),
        "Medium" : np.ones(6),
        "Low"    : np.array([1.10,1.10,0.85,0.95,0.95,1.00])
    }
    # Track modifiers for the remaining races of current season
    # track_seq = ["High","High","Medium","Low","Medium","High"]
    track_seq = ["High","Medium","Low","Medium","High"]
    # Number of sprints left in the season
    # sprint_weeks = set([0,1,2])
    sprint_weeks = set([1,2])

    print("Starting simulation...\n")
    monte_carlo()
        
if __name__ == "__main__":
    main()
    