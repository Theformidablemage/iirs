import numpy as np
from read_qub import parse_pds5_spectrum_xml,read_qub
import matplotlib.pyplot as plt
import tifffile as tif
from thermal import thermal_corrector_np

xml=r"/home/megha/arshveer/ch2_iir_nci_20211218T0038037745_d_img_hw1/data/calibrated/20211218/ch2_iir_nci_20211218T0038037745_d_img_hw1.xml"
qub=r"/home/megha/arshveer/ch2_iir_nci_20211218T0038037745_d_img_hw1/data/calibrated/20211218/ch2_iir_nci_20211218T0038037745_d_img_hw1.qub"
w=r"/home/megha/arshveer/Solar flux.txt"
meta=parse_pds5_spectrum_xml(xml)
cube=read_qub(qub,meta,skip_bands=0)

b,h,c=cube.shape
spec=cube[:,h//2,c//2]
wave=np.loadtxt(w,usecols=0)
'''
plt.figure()
plt.plot(wave,spec)
plt.xlabel("Wavelengths in nm")
plt.ylabel("Radiance values")
plt.title("Spectrum of a pixel from IIRS strip")
plt.grid(True)
plt.show()

c=cube[48,:,:]
vmin = np.nanpercentile(c, 2)
vmax = np.nanpercentile(c, 98)
plt.figure(figsize=(16,6))
plt.imshow(c,cmap="gray",vmin=vmin, vmax=vmax)
plt.tick_params(
    left=False, right=False,
    bottom=False, top=False,
    labelleft=False, labelbottom=False
)

plt.box(True)  # ensures border stays

plt.show()

s=r"/home/megha/arshveer/topographhy/dem2_slope.tif"
slope=tif.imread(s)
r,c=np.where(slope<5)
print(r,c)
'''

c,temp=thermal_corrector_np(cube,wave,0.95,None)

rug=c[:,297,9]
fl=c[:,481,9]
cr=cube[:,297,9]
cf=cube[:,481,9]

plt.figure()
plt.plot(wave,rug,color='red',label='Thermally corrected Rugged Pixel')
plt.plot(wave,fl,color='green', label='Thermally corrected flat pixel')
plt.xlabel("Wavelengths in nm")
plt.ylabel("Radiance")
plt.title("Thermally corrected spectra")
plt.legend()
plt.show()

plt.figure()
plt.plot(wave,cr,color='red',linestyle='--',label='Rugged pixel without thermal correction')
plt.plot(wave,cf,color='green',linestyle='--',label='Flat pixel without thermal correction')
plt.xlabel("Wavelengths in nm")
plt.ylabel("Radiance")
plt.title("Rugged and flat pixel spectrum without thermal correction")
plt.legend()
plt.show()



