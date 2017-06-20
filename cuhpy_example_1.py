# Simple cuhpy example

import cuhpy


sc=cuhpy.Subcatchment(**{"name":'101',"area":0.0350893828125,"centroidLength":0.297157214015151,"length":0.644109473484848,
                         "slope":0.00350823545129406,"impervious":15.194058,"perviousDepressionStorage":0.4,
                         "imperviousDepressionStorage":0.1,"hortonsInitial":3.23278016228093,"hortonsDecay":0.00167197091074549,
                         "hortonsFinal":0.558195040570232,"dciaLevel":0})

std_gage = cuhpy.RainGage(**{"rgType":"Standard","oneHourDepth":2.47, "returnPeriod":100}) #establish raingauge
ac_gage = cuhpy.RainGage(**{"rgType":"AreaCorrected","oneHourDepth":2.47, "sixHourDepth":3.556,"correctionArea":15,"returnPeriod":100}) #establish raingauge

std_ro=cuhpy.Runoff(sc,std_gage,5)
ac_ro=cuhpy.Runoff(sc,ac_gage,5)


print ("Standard gage Peak Flow=" + "%.2f" % max(std_ro.runoff))
print ("Area corrected gage Peak Flow=" + "%.2f" % max(ac_ro.runoff))





