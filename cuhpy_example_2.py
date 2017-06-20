# cuhpy example - import existing excel CUHP workbook

import cuhpy

CUHPdata = cuhpy.importExcel("c:\\temp\\CUHP_200.xlsm")
Subcatchments = CUHPdata[0]
Raingages = CUHPdata[1]
Runoffs = [] # Initialize list of runoff values
for sc in Subcatchments.itervalues():
    Runoffs.append(cuhpy.Runoff(sc,Raingages[sc.rainGageName],5)) # Arguments for runoff are subcatchment, raingage, timestep
cuhpy.writeSwmmFile(Runoffs,"c:\\temp\\cuhpy_swmm.txt") # SWMM interface file
cuhpy.outputHydrographs(Runoffs, "c:\\temp\\cuhpy_hydrographs2.csv") # Write output hydrographs to a csv file
