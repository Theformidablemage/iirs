import os
os.system('cls')

path=r"D:\ch2_iir_nci_20210720T2333026105_d_img_d32\miscellaneous\calibrated\20210720\ch2_iir_nci_20210720T2333026105_d_img_d32.oat"
ps=r"D:\ch2_iir_nci_20210720T2333026105_d_img_d32\miscellaneous\calibrated\20210720\ch2_iir_nci_20210720T2333026105_d_img_d32.spm"

'''
For OAT file
Solar azimuth 398:412
Solar elevation 412:426
Emission angle 479:488
Phase angle 488:498
Solar zenith 521:530

'''
def oat(path):
    print("\nSolar Azimuth\t\tSolar Elevation\t\tEmission\t\tPhase\t\tSolar Zenith\t\tIncidence\n", flush=True)
    #exit()
    with open(path,"r") as f:
        for line in f:
            #if not line.startswith("ORBTATTD 12114 62820"):
            #   continue
            #print(len(line), repr(line[:20]))
            
            sa=float(line[398:412].strip())
            se=float(line[412:426].strip())
            e=float(line[479:488].strip())
            ph=float(line[488:498].strip())
            sza=float(line[521:530].strip())
            inc=90-se
            print(f"{sa}\t\t{se}\t\t{e}\t\t{ph}\t\t{sza}\t\t{inc}")

    return 0

'''
    For SPM file:
    Phase angle 142:151
    Sun Azimuth 160:169
    Sun Elevation 169:178
'''
def spm(path):

    with open(path, "r") as f:
        for line in f:
            print(repr(line), len(line))
            p=float(line[142:151].strip())
            a=float(line[160:169].strip())
            e=float(line[169:178].strip())
            print(f"{p}\t\t{a}\t\t{e}")

    return 0

spm(ps)