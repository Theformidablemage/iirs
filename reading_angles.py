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
            if not line.startswith("ORBTATTD"):
               continue
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
    -ALL WRONG-
    For SPM file:
    Phase angle 142:151
    Sun Azimuth 160:169
    Sun Elevation 169:178
    -RIGHT-

'''
def spm(path):
    count=0
    with open(path, "r") as f:
        for line in f:
            if not line.startswith("ORBTATTD"):
                continue
            #print(repr(line), len(line))
            #p=line[142:]
            #for i in p:
             #   if i.isdigit():
              #      break
               # count+=1
            #print(count)
            p=float(line[142:158].strip())
            a=float(line[174:190].strip())
            e=float(line[190:206].strip())
            i=90-e

            print(f"{p}\t\t{a}\t\t{e}\t\t{i}")

    return 0

spm(ps)
#oat(path)