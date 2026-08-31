# Example artifact from the agent-scaffold study: a from-scratch Gaussian .log parser
# the coding agent wrote in the NONE arm (no harness), task Gaussian__TRpxYNCX. Preserved
# to illustrate what an unassisted agent produces; not part of the parse-patrol package.
# The same code is also embedded in agent_study/runs/Gaussian__TRpxYNCX__NONE__0.json.
import json, re, os

F = "tests/.data/TRpxYNCXoPIhy1jB15tmKpLHyqCE/d9DagJChRxyeUKBEwzSiFw/G-I-O-P-gjf-out/G.LOG"
lines = open(F).read().splitlines()

Z2SYM = {1:"H",6:"C",7:"N",8:"O"}

# charge / multiplicity
charge = mult = None
for l in lines:
    m = re.search(r"Charge =\s*(-?\d+)\s*Multiplicity =\s*(\d+)", l)
    if m:
        charge, mult = int(m.group(1)), int(m.group(2)); break

# last Standard orientation coordinate block
atomic_numbers=[]; coords=[]
idx=[i for i,l in enumerate(lines) if "Standard orientation:" in l]
start=idx[-1]
# skip header lines to data (dashed lines)
i=start
# find third dashed line after start
dash=[j for j in range(start,len(lines)) if set(lines[j].strip())=={"-"}]
d1,d2,d3=dash[0],dash[1],dash[2]
for l in lines[d2+1:d3]:
    p=l.split()
    if len(p)>=6:
        atomic_numbers.append(int(p[1]))
        coords.append([float(p[3]),float(p[4]),float(p[5])])
elements=[Z2SYM[z] for z in atomic_numbers]
n_atoms=len(atomic_numbers)

# formula Hill
from collections import Counter
c=Counter(elements)
def hill(c):
    s=""
    order=[]
    if "C" in c:
        order.append("C")
        if "H" in c: order.append("H")
    for e in sorted(c):
        if e in ("C","H"): continue
        order.append(e)
    if "C" not in c:
        order=sorted(c)
    for e in order:
        s+=e+(str(c[e]) if c[e]>1 else "")
    return s
formula=hill(c)

# scf energy
scf=None
for l in lines:
    m=re.search(r"SCF Done:\s*E\(\S+\)\s*=\s*(-?\d+\.\d+)",l)
    if m: scf=float(m.group(1))

# thermochem
def grab(pat):
    for l in lines:
        m=re.search(pat,l)
        if m: return float(m.group(1))
    return None
zpve=grab(r"Zero-point correction=\s*(-?\d+\.\d+)")
enthalpy=grab(r"Sum of electronic and thermal Enthalpies=\s*(-?\d+\.\d+)")
free=grab(r"Sum of electronic and thermal Free Energies=\s*(-?\d+\.\d+)")

# frequencies and IR intensities
freqs=[]; irs=[]
for l in lines:
    if l.strip().startswith("Frequencies --"):
        freqs+=[float(x) for x in l.split("--")[1].split()]
    if l.strip().startswith("IR Inten"):
        irs+=[float(x) for x in l.split("--")[1].split()]

# mulliken charges (first section "Mulliken charges and spin densities:")
mull=[]
for i,l in enumerate(lines):
    if l.strip()=="Mulliken charges and spin densities:":
        j=i+2
        while j<len(lines):
            p=lines[j].split()
            if len(p)>=4 and p[0].isdigit():
                mull.append(float(p[2]))  # charge column (spin is p[3])
                j+=1
            else:
                break
        break

out={
 "metadata":{"program":"Gaussian 16","formula":formula,"charge":charge,"multiplicity":mult,"n_atoms":n_atoms},
 "geometry":{"elements":elements,"atomic_numbers":atomic_numbers,"coords":coords},
 "energetics":{"scf_energy":scf,"zpve":zpve,"enthalpy":enthalpy,"free_energy":free},
 "vibrational":{"frequencies_cm1":freqs,"ir_intensities":irs},
 "charges":{"mulliken":mull},
}
os.makedirs("agent_study/runs",exist_ok=True)
json.dump(out,open("agent_study/runs/Gaussian__TRpxYNCX__NONE__0.output.json","w"),indent=2)
print("n_atoms",n_atoms,"formula",formula,"nfreq",len(freqs),"nir",len(irs),"nmull",len(mull))
print("scf",scf,"zpve",zpve,"enth",enthalpy,"free",free,"charge",charge,"mult",mult)
