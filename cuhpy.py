'''
cuhpy - A python implementation of the Colorado Urban Hydrograph Procedure (2.0.0)

Version P2.0.0
by David Delagarza / RESPEC
June 2017
Code converted from CUHP 2.0.0 VBA / Excel

 Requires math & numpy - Download windows binaries from (http://www.lfd.uci.edu/~gohlke/pythonlibs/)
 Requires cuhpdata.py
 matplotlib is optional optional for plotting functions

'''

import math
import numpy as np
import cuhpdata
import datetime
import collections

_dataLib = cuhpdata._Data()
almostZero = 0.00001 #Global Value used in VBA version, might as well use it here
errorMessages = [] #List of various error messages

class Subcatchment():
    """The Subcatchment object represents individual subcatchments and their attributes
    It computes the parameters for each subcatchment as described and  is independent of rainfall and raingage data"""

    def __init__(self,name,area,centroidLength,length,slope,impervious,perviousDepressionStorage,
                 imperviousDepressionStorage,hortonsInitial,hortonsDecay,hortonsFinal,dciaLevel=0,
                 dcifOverride=None,rpfOverride=None,ctOverride=None,cpOverride=None,w50Override=None,
                 w75Override=None,k50Override=None,k75Override=None,swmmNode=None,rainGageName=None,comment=None):
        # --User Input Variables--
        self.name=str(name) #subcatchment name (string)
        self.area=float(area) #subcatchment area (mi^2)
        self.centroidLength=float(centroidLength) #length to Centroid (mi)
        self.length=float(length) #subcatchment length (mi)
        self.slope=float(slope) #subcatchment slope (ft/ft)
        self.impervious=float(impervious) #impervious percentage(%) - as a whole interger, i.e. 9.1 not .0091 for 9.1%
        self.perviousDepressionStorage=float(perviousDepressionStorage) #Maximum pervious depression storage (in)
        self.imperviousDepressionStorage=float(imperviousDepressionStorage) #Maximum impervious depression storage (in)
        self.hortonsInitial=float(hortonsInitial) #Horton's initial infiltration rate (in/hr)
        self.hortonsDecay=float(hortonsDecay) #Horton's decay coefficient
        self.hortonsFinal=float(hortonsFinal) #Horton's final infiltration rate (in/hr)
        self.dciaLevel=int(dciaLevel) #Directly connected impervious area level (0,1,2)(optional)
        self.dcifOverride=dcifOverride #User input override for directly connected impervious area fraction (optional)
        self.rpfOverride=rpfOverride #User input override value for receiving pervious area fraction (optional)
        self.ctOverride=ctOverride #User input override value for time to peak coefficient (optional)
        self.cpOverride=cpOverride #User input override value for time to peak runoff rate (optional)
        self.w50Override = w50Override #User input override value for width of unit hydrograph at 50% PeakQ (optional)
        self.w75Override = w75Override #User input override value for width of unit hydrograph at 75% PeakQ (optional)
        self.k50Override = k50Override #User input override for fraction of hydrograph width before peak at 50% PeakQ (optional)
        self.k75Override = k75Override #User input override value for fraction of hydrograph width before peak at 75% PeakQ (optional)
        self.swmmNode=swmmNode #Corresponding SWMMnode (optional)
        self.rainGageName = rainGageName #Raingage name (optional)
        self.comment=comment #User Input Comment (optional)

        # --Computed Variables--
        self.rpf=None  # recieving pervious fraction
        self.spf = None  # separate pervious fraction
        self.dcif=None  # directly connected impervious fraction
        self.uif = None  # unconnected impervious fraction
        self.dcia = None  # directly connected impervious area (mi^2)
        self.uia = None  # unconnected impervious area (mi^2)
        self.rpa = None  # recieving pervious area (mi^2)
        self.spa = None  # separate pervious area (mi^2)
        self.avgInfiltration = None # Average Infiltration

        # --Run these functions on initialization--
        self._computePerviousFractions()
        self._computeAvgInfiltration()

    def _computePerviousFractions(self):
        """ Calculates rpf and dcif for the subcatchment"""

        decImperv = self.impervious / 100 #easier than dividing by 100 every time
        #-----Get Paramaters-----
        for i in range(0,len(_dataLib.rpfCoeff[self.dciaLevel])): #Find the appropriate rpf paramaters from the library
            if decImperv <= _dataLib.rpfCoeff[self.dciaLevel][i][0]:
                rpfParams = _dataLib.rpfCoeff[self.dciaLevel][i][1:]
                break

        for i in range(0,len(_dataLib.dcifCoeff[self.dciaLevel])):#Find the appropriate dcif paramaters from the library
            if decImperv <= _dataLib.dcifCoeff[self.dciaLevel][i][0]:
                dcifParams=_dataLib.dcifCoeff[self.dciaLevel][i][1:]
                break
        #-----Compute Pervious Fractions and areas-----
        self.dcif = self.impervious / 100 * dcifParams[0] + dcifParams[1] #Compute DCIF
        if self.dcifOverride is not None: #Look for DCIF override
            if 0 <= self.dcifOverride <= 1:
                self.dcif=self.dcifOverride
            else:
                errorMessages.append("DCIF Override out of Range, Ignoring")
        if self.dcif >= 1: self.dcif=1-almostZero
        if self.dcif <= 0: self.dcif=almostZero

        self.rpf = self.impervious / 100 * rpfParams[0] + rpfParams[1] #Compute RPF
        if self.rpfOverride is not None: #Look for RPF override
            if 0 <= self.rpfOverride <= 1:
                self.dcif=self.rpfOverride
            else:
                errorMessages.append("RPF Override out of Range, Ignoring")
        if self.rpf >= 1: self.rpf = 1 - almostZero
        if self.rpf <= 0: self.rpf = almostZero

        self.uif = 1 - self.dcif
        self.spf = 1 - self.rpf

        self.uia=((1-self.dcif)*self.area*self.impervious/100) # Compute unconnected impervious area, Eqn B-21
        self.rpa=self.rpf*((1-self.impervious/100)*self.area)# Compute recieving pervious area, Eqn B-22
        self.dcia = self.dcif * self.impervious/100 * self.area # Compute directly connected impervious area
        self.spa = self.spf * ((1 - self.impervious / 100) * self.area)  # Compute separate pervious area

        return True

    def _computeAvgInfiltration(self): #Computes the Average Infiltration per Eqn B-25
        self.avgInfiltration=(self.hortonsFinal+((self.hortonsInitial-self.hortonsFinal)/(7200*self.hortonsDecay))
             *(1-math.exp(-7200*self.hortonsDecay))) #Eqn B-25, average
        return True


class RainGage():
    # The RainGage object computes and holds raingage data
    # Each type of raingage has a different input method
    def __init__(self,rgType,rgName=None,timeStep=None,userInputDepths=None,oneHourDepth=None,sixHourDepth=None,correctionArea=None,returnPeriod=None):
        # --User input variables
        self.rgType = rgType
        self.rgName = rgName # raingage name (optional)
        self.timeStep = timeStep #timeStep - 5 min for standard CUHP raingages, variable for user input
        self.oneHourDepth = oneHourDepth
        self.sixHourDepth = sixHourDepth
        self.correctionArea = correctionArea
        self.returnPeriod = returnPeriod
        self.userInputDepths = userInputDepths

        # --Computed Variables
        self.twoHourDepth = None
        self.threeHourDepth = None
        self.rainDepths=[]

        if self.rgType == "UserInput":
            if None in (self.timeStep,self.userInputDepths): raise ValueError("User defined gage requires timestep and depths")
            self.timeStep = timeStep
            self.oneHourDepth = oneHourDepth
            time, totalDepth = 0, 0

            for value in self.userInputDepths:
                time += self.timeStep
                self.rainDepths.append(value)
                totalDepth += value
                if time >= 60 and self.oneHourDepth is None:
                    self.oneHourDepth = totalDepth

        elif self.rgType == "Standard": #Standard distribution with 5-minute hyetograph
            if None in (self.oneHourDepth, self.returnPeriod): raise ValueError(
                "Standard distribution gage requires one hour depth and return period")
            self.timeStep = 5
            self.oneHourDepth = oneHourDepth
            self.returnPeriod = returnPeriod

            hyetograph = _dataLib.oneHourDistribution
            if self.returnPeriod not in hyetograph[0][1]: raise ValueError("Invalid Return Period for RainGage")
            else: rindex = hyetograph[0][1].index(self.returnPeriod)
            time = self.timeStep
            while time <= 120:
                thisHyetoDepth = hyetograph[time/5+1][1][rindex]
                thisGageDepth = thisHyetoDepth * self.oneHourDepth
                self.rainDepths.append(thisGageDepth)
                time += self.timeStep
            self.rainDepths.append(0.0)
            self._adjustDips()

        elif self.rgType == "AreaCorrected":
            if None in (self.oneHourDepth, self.sixHourDepth, self.returnPeriod, self.correctionArea): raise ValueError(
                "Area corrected gage requires 1- and 6- hour depths, return period and correction area")
            self.oneHourDepth = oneHourDepth
            self.sixHourDepth = sixHourDepth
            self.correctionArea = correctionArea
            self.returnPeriod = returnPeriod
            self.timeStep = 5

            self.twoHourDepth = (self.sixHourDepth - self.oneHourDepth) * 0.342
            self.threeHourDepth = (self.sixHourDepth - self.oneHourDepth) * 0.597
            hyetograph = _dataLib.oneHourDistribution
            if self.returnPeriod not in hyetograph[0][1]: raise ValueError("Invalid Return Period for RainGage")
            else: rindex = hyetograph[0][1].index(self.returnPeriod)
            time = self.timeStep

            while time <= 600 / self.timeStep: # Fill out first two hours from the standard hyetograph
                thisHyetoDepth = hyetograph[time/5+1][1][rindex]
                thisGageDepth = thisHyetoDepth * self.oneHourDepth
                self.rainDepths.append(thisGageDepth)
                time += self.timeStep

            darfChart = None
            if self.correctionArea >= 15: #Correction areas greater than 15 square miles get filled out to six hours
                while time < 180 + self.timeStep: #uniformally distribute the 2-3 hour depth
                    time += self.timeStep
                    self.rainDepths.append((self.threeHourDepth-self.twoHourDepth)/12)
                threeToSixHourIncrement = (self.sixHourDepth - np.sum(self.rainDepths)) /36
                while time <  360 + self.timeStep: #Evenly distribute the remaining rainfall
                    time += self.timeStep
                    self.rainDepths.append(threeToSixHourIncrement)
                self.rainDepths.append(0.0)

                #Get the Appropriate Depth Area Reduction Factors (DARF) if appropriate:
                if self.returnPeriod <= 10:
                    if self.correctionArea >= _dataLib.darf_under_10yr[0][1][0]: darfChart = _dataLib.darf_under_10yr
                else:
                    if self.correctionArea >= _dataLib.darf_over_10yr[0][1][0]: darfChart = _dataLib.darf_over_10yr
            elif self.returnPeriod <= 10 and self.correctionArea >= _dataLib.darf_under_10yr: darfChart = _dataLib.darf_under_10yr
            self._adjustDips()

            #Apply DARF
            if darfChart is not None:
                self.uncorrectedDepths = self.rainDepths
                if self.correctionArea in darfChart[0][1]:  # test if the correction area is in the chart
                    dIndex = darfChart[0][1].index(self.correctionArea)
                    for i in range(len(self.rainDepths)):
                        self.rainDepths[i] = self.uncorrectedDepths[i] * darfChart[i + 2][1][dIndex]
                else:
                    j = 1
                    lIndex, uIndex, multiplier = None, None, None #lower index
                    while multiplier is None:  # if the correction area is not in the chart, use the nearest correction area
                        if self.correctionArea <= darfChart[0][1][j]:
                            lIndex = j - 1
                            uIndex = j + 1
                            multiplier = (float(self.correctionArea) - float(darfChart[0][1][j-1])) / (float(darfChart[0][1][j]) - float(darfChart[0][1][j-1]))
                        j += 1
                        if j > len(darfChart[0][1]): lIndex, uIndex = j
                    for i in range(len(self.rainDepths)):
                        self.rainDepths[i] = self.uncorrectedDepths[i] * (darfChart[i + 1][1][lIndex] + multiplier * (darfChart[i + 2][1][uIndex] - darfChart[i + 2][1][lIndex]))
        else: raise ValueError("Invalid Rain Gage Type")

    def _adjustDips(self):
        isSmooth = False
        numIterations = 0
        adjustment = 0.0
        while not isSmooth:
            dips_found = False
            for i in range(self.rainDepths.index(max(self.rainDepths)), len(self.rainDepths) - 1):
                if self.rainDepths[i] < self.rainDepths[i + 1]:
                    dips_found = True
                    for j in range(i - 1, self.rainDepths.index(max(self.rainDepths)), -1):
                        if self.rainDepths[j] > self.rainDepths[i + 1]:
                            avg = (self.rainDepths[j] + self.rainDepths[i + 1]) / 2
                            if avg > self.rainDepths[i + 1]:
                                self.rainDepths[i + 1] = avg
                                adjustment += avg - self.rainDepths[i + 1]
                                break
            if dips_found:
                numIterations += 1
            else:
                isSmooth = True
            if numIterations > 100: raise ValueError("Error generating curve: Unusual rainfall values and/or multiple peaks detected.")
        if adjustment != 0:
            peakIndex = self.rainDepths.index(max(self.rainDepths))
            totalRainfall = 0
            for i in range(peakIndex - 2, peakIndex + 3):
                totalRainfall += self.rainDepths[i]
            test_value = self.rainDepths[peakIndex - 2] - adjustment * self.rainDepths[peakIndex - 2] / totalRainfall
            if test_value < self.rainDepths[peakIndex - 3]: test_value = self.rainDepths[peakIndex - 3]
            self.rainDepths[peakIndex - 2] = test_value
            test_value = self.rainDepths[peakIndex + 2] - adjustment * self.rainDepths[
                peakIndex + 2] / totalRainfall
            if test_value < self.rainDepths[peakIndex + 3]: test_value = self.rainDepths[peakIndex + 3]
            self.rainDepths[peakIndex + 2] = test_value
            test_value = self.rainDepths[peakIndex - 1] - adjustment * self.rainDepths[peakIndex - 1] / totalRainfall
            if test_value < self.rainDepths[peakIndex - 2]: test_value = self.rainDepths[peakIndex - 2]
            self.rainDepths[peakIndex - 1] = test_value
            test_value = self.rainDepths[peakIndex + 1] - adjustment * self.rainDepths[
                peakIndex + 1] / totalRainfall
            if test_value < self.rainDepths[peakIndex + 2]: test_value = self.rainDepths[peakIndex + 2]
            self.rainDepths[peakIndex + 1] = test_value
            test_value = self.rainDepths[peakIndex] - adjustment * self.rainDepths[
                peakIndex] / totalRainfall
            if test_value < self.rainDepths[peakIndex + 1] or test_value < self.rainDepths[peakIndex - 1]: test_value = \
            self.rainDepths[peakIndex - 1]
            self.rainDepths[peakIndex + 1] = test_value




class UnitHydrograph():
    """ Computes Unit Hydrograph based on a given subcatchment class, 1 hour precipitation depth and timeStep"""

    def __init__(self,subcatchment,p1,timeStep):
        # ---user input variables---
        self.subcatchment = subcatchment #Subcatchment Object
        self.p1=float(p1) #1 hour precipitation depth (in)
        self.timeStep=float(timeStep) #CUHP time step (min)
        # ---computed variables---
        self.eia = None  # effective impervious area
        self.ct = None  # time to peak coefficient
        self.cp = None  # peaking coefficient
        self.p = None  # peaking parameter
        self.tp_hr = None  # time to peak from midpoint of the storm (hours)
        self.tp = None  # time to peak from the start of the storm (minutes)
        self.unit_qp = None  # unit peak discharge
        self.qp = None # peak discharge (cfs)
        self.w50 = None  # width of the unit hydrograph at 50% peakQ
        self.w75 = None  # width of the unit hydrograph at 75% peakQ
        self.k50 = None  # offset parameter, fraction of w50 before peak discharge
        self.k75 = None  # offset parameter, fraction of w75 before peak discharge
        self.unitHydrograph = None  # unit hydrograph - list of values at each timeStep
        # ---run on initialization---
        self._computeEia()
        self._calcCT()
        self._calcCp()
        self._calcTp()
        self._calcQp()
        self._calcWidth()
        self._buildUnitHydrograph()

    def _computeEia(self):
        # Compute Impervious Reduction Factor (EIA)
        # EIA  represents a reduced the watershed imperviousness for unit hydrograph calcuation in watersheds with
        # unconnected impervious area based on fractional areas and infiltration to intensity ratios

        decImperv = self.subcatchment.impervious/100 #easier than dividing by 100 over and over again
        if decImperv < almostZero: #If %Imp = 0%, EIA = 0%
            self.eia = almostZero
            return True
        if decImperv >= (1-almostZero): #If %Imp = 100%, EIA = 100%
            self.eia = 100 - almostZero
            return True

        ia = self.subcatchment.uia/(self.subcatchment.uia+self.subcatchment.rpa) #Eqn B-23, area-weighted imperviousness fraction
        intensity=1.157*self.p1/2 #Eqn B-24, average rainfall intensity over a 2-hour duration based on 1-hour rainfall depth

        fOverI = self.subcatchment.avgInfiltration/intensity #Average infitration to 2-hour intensity ratio

        if fOverI>2: fOverI=2 #We don't have any data above a ratio of 2, so limit it it 2.
        if fOverI <=0 and ia > 0: k=1
        elif ia >= 1: k=1 #If the area weighted imperviousness area is 100%, K=1
        elif ia == 0: k=0 #If the area weighted imperviousness area is 0%, K=0

        else: #Compute K baed on Equation B-27
            for i in _dataLib.kcoeff:
                if ia < i[0]:
                    kcoeff = i[1:]
                    break
            kSlope = kcoeff[0][0] * fOverI ** 3 + kcoeff[0][1] * fOverI ** 2 + kcoeff[0][2] * fOverI + kcoeff[0][3]
            kIntercept = kcoeff[1][0] * fOverI ** 3 + kcoeff[1][1] * fOverI ** 2 + kcoeff[1][2] * fOverI + kcoeff[1][3]
            k = kSlope * ia + kIntercept
        if k < 0: k=0
        if k > 1: k=1

        self.eia = ((self.subcatchment.dcia + (k * self.subcatchment.uia)) / self.subcatchment.area) * 100 #Volume Weighted Impervious, Eqn B-27

    def _calcCT(self):
        #Ct relates the imperviousness of the subcatchment to the time to peak

        # Find the appropriate Ct Parameters from the _dataLib
        if self.eia <= _dataLib.ctCoeff[0][0]: ctParams= _dataLib.ctCoeff[0][1:]
        elif self.eia <= _dataLib.ctCoeff[1][0]: ctParams = _dataLib.ctCoeff[1][1:]
        else: ctParams = _dataLib.ctCoeff[2][1:]

        # Calculate Ct - Eqn. B-28
        self.ct=ctParams[0]*self.eia**2+ctParams[1]*self.eia+ctParams[2]

        #Look for Overrides
        if self.subcatchment.ctOverride is not None:
            if .07 < self.subcatchment.ctOverride < .164: #Ct should be between .07 and .164
                self.ct=self.subcatchment.ctOverride
            else:
                errorMessages.append("Ct override out of range, ignoring")

    def _calcCp(self):
        # Cp relates the imperviousness to the peak runoff value

        # Find the appropriate peaking parameter coefficients from the _dataLib
        if self.eia <= _dataLib.pCoeff[0][0]: pParams = _dataLib.pCoeff[0][1:]
        else: pParams = _dataLib.pCoeff[1][1:]

        # Calculate the peaking paramater, P (Figure B-8)
        self.p=pParams[0]*self.eia**2+pParams[1]*self.eia+pParams[2]

        # Find the appropriate Cp coefficients from the _dataLib
        if self.subcatchment.area*640 <= _dataLib.cpCoeff[0][0]: cpParams=_dataLib.cpCoeff[0][1:]
        else: cpParams=_dataLib.cpCoeff[1][1:]

        # Calculate Cp (Eqn B-28)
        self.cp=cpParams[0]*self.p*self.ct*self.subcatchment.area**cpParams[1]

        # Look for Cp Override and Validate
        if self.subcatchment.cpOverride is not None:
            if self.subcatchment.cpOverride > 0: #Cp must be greater than 0
                self.cp=self.subcatchment.cpOverride
            else:
                errorMessages.append("Cp override out of range, ignoring")

    def _calcTp(self):
        # Calculate Time to Peak, Tp (equations B-29 and B-30)
        self.tp_hr=self.ct*(self.subcatchment.length*self.subcatchment.centroidLength/self.subcatchment.slope**.5)**0.48
        self.tp=self.tp_hr*60.0+0.5*self.timeStep

    def _calcQp(self):
        #Calculate Peak Runoff Rate (equations B-33 and B-32)
        self.unit_qp=640.0*self.cp/self.tp_hr #unit runoff rate, Eqn B-32
        self.qp=self.subcatchment.area*self.unit_qp #peak runoff rate, Eqn B-33

    def _calcWidth(self):
        # calculate Width Parameters w50 and w75
        self.w50 = 60.0 * 500.0 / self.unit_qp  # eqn B-34
        if self.subcatchment.w50Override is not None: #Check for W50Override Paramater
            if self.subcatchment.w50Override > 0: #Must be greater than 0
                self.w50=self.subcatchment.w50Override
            else:
                errorMessages.append("W50 Override Parameter Out of Range, ignoring")

        self.w75=60*260/self.unit_qp #eqn B-35

        if self.subcatchment.w75Override is not None: #Check for W75Override Paramater
            if self.subcatchment.w75Override > 0: #Must be greater than 0
                self.w75=self.subcatchment.w75Override
            else:
                errorMessages.append("W75 Override Parameter Out of Range, ignoring")

        # Calculate Offset parameters k50 and k75
        if (0.35*self.w50) <= 0.6*self.tp:
            self.k50=0.35
            self.k75=0.45
        else:
            self.k50=0.6*self.tp/self.w50
            self.k75=0.424*self.tp/self.w75

        # Check for k50 and K75 overrides
        if self.subcatchment.k50Override is not None:
            if 0 > self.subcatchment.k50Override > 1: #Must be between 0 and 1
                self.k50=self.subcatchment.k50Override
            else:
                errorMessages.append("K50 Override Parameter Out of Range, ignoring")
        if self.subcatchment.k75Override is not None:
            if 0 > self.subcatchment.k75Override > 1:  # Must be between 0 and 1
                self.k75 = self.subcatchment.k75Override
            else:
                errorMessages.append("K50 Override Parameter Out of Range, ignoring")

    def _buildUnitHydrograph(self):
        '''This function develops the curve data for the unit hydrograph.
        The Unit Hydrograph curves are developed by establishing linear, binomal, and cubic polynomials
         based on the hydrograph points defined by the width and peak paramaters.'''

        self.uhCurveData=[] #Empty list to hold the curve data as it is built
        tList=[] #Empty list to import time points into
        qList=[] #Empty list to import flow points into

        # Unit Hydrograph time values, from figure B-12
        tList.append(0) #t0 = 0
        tList.append(self.tp - self.k50 * self.w50) #t1=Tp-k50*w50
        tList.append(self.tp - self.k75 * self.w75) #t2=Tp-k75*w75
        tList.append(self.tp) #t3= Tp
        tList.append(self.tp + (1 - self.k75) * self.w75)  # T4=Tp+(1-K75)W75
        tList.append(self.tp + (1 - self.k50) * self.w50) # T5=Tp+(1-K50)W50

        #Unit Hydrograph Q values, from figure B-12
        qList.append(0) #t0
        qList.append(.5*self.qp) #t1
        qList.append(.75 * self.qp) #t2
        qList.append(self.qp) #t3
        qList.append(.75 * self.qp) #t4
        qList.append(.5 * self.qp) #t5
        qList.append(.2 * self.qp) #t6
        qList.append(0) #t7

        # Compute uh Volume and area
        self.uhVolume=self.subcatchment.area*640*43560/12 #UH runoff volume (ft^3), from figure B-12

        #initialize the linear solver matrix for a cubic polynomial.
        input_matrix=np.zeros((4,4)) #Matrix for linear equation coefficient matrix
        ordinate_vector=np.zeros(4) #Vector for dependent variables

        #------Compute Segment 1  - t(0) to t(2)------
        # The Initial try for segment 1 is a cubic polynomial of the form:
        # Q(t) = at^3 + bt^2 + ct + d
        # Given three known points for this polynomial (t[0-2],q[0-2]), we can establish three linear equations:
        # The fourth point comes from a relationship between points 4 and 5 and this first segment which is coded in CUHP,
        # but is not documented in either the guide or the code. This relationship is c=(1/3)((Q4/t4)+(Q5/t5))

        input_matrix[0, 0] = 1
        input_matrix[1, 1] = 1
        input_matrix[2, 0] = 1
        input_matrix[2, 1] = tList[1]
        input_matrix[2, 2] = tList[1] ** 2
        input_matrix[2, 3] = tList[1] ** 3
        input_matrix[3, 0] = 1
        input_matrix[3, 1] = tList[2]
        input_matrix[3, 2] = tList[2] ** 2
        input_matrix[3, 3] = tList[2] ** 3

        ordinate_vector[1] = ((qList[4]/tList[4]) + (qList[5] / tList[5]))*.033333333333
        ordinate_vector[2] = qList[1]
        ordinate_vector[3] = qList[2]

        try: #compute cubic polynomial
            result_vector=np.linalg.solve(input_matrix,ordinate_vector)
            coeffs = np.flipud(result_vector)
            roots = np.roots(coeffs)
            realroots = roots[np.isreal(roots)]
            segment_1_recalculate = False
        except: #if the cubic polynomial cannot compute
            result_vector=None
            segment_1_recalculate = True
            realroots=[]

        #Check for zero values in segment 1
        for i in realroots:
            if 0 < i < tList[2]: segment_1_recalculate=True  #If a zero occurs in this segment, we need to split it into two segments, 1.1 and 1.2

        if segment_1_recalculate: #go with biomial and linear segments
            segment1_1_coeffs = (qList[1] / (tList[1] ** 2), 0, 0)  # segment 1.1 binomial with zero intersect
            self.uhCurveData.append((tList[1], segment1_1_coeffs))
            segment1_2_slope = (qList[2] - qList[1]) / (
            tList[2] - tList[1])  # segment 1.2, if used, is linear between t(1) and t(2)
            segment1_2_intercept = qList[1] - segment1_2_slope * tList[1]
            segment1_2_coeffs = (segment1_2_slope, segment1_2_intercept)
            self.uhCurveData.append((tList[2], segment1_2_coeffs))
        else:
            self.uhCurveData.append((tList[2], coeffs))

        # ------Compute Segment 2 t(2) to t(4)------
        #reinitialize input matrix and ordinate vector for cubic polynomial
        input_matrix = np.zeros((4, 4))
        ordinate_vector = np.zeros(4)

        #segment 2 has three known points (t(2-4), q(2-4)) and a known slope (0 at t(3)/Qpeak)
        #the derivative of y=ax^3+by^2+cy+d is dy=3ax^2+2bx+c, which is represented as the third linear equation
        #The equations used are:
        # T(2)^3 * A + T(2)^2 * B + T(2) * C + D = Q(2) (point T(2),Q(2))
        # T(3)^3 * A + T(3)^2 * B + T(3) * C + D = Q(3) (point T(3),Q(3))
        # T(3)^2 * 3A + T(3) * 2B + C = 0 (Derivative at peak is 0)
        # T(4)^3 * A + T(4)^2 * B + T(4) * C + D = Q(4) (point T(4),Q(4))

        input_matrix[0, 0] = 1
        input_matrix[0, 1] = tList[2]
        input_matrix[0, 2] = tList[2] ** 2
        input_matrix[0, 3] = tList[2] ** 3
        input_matrix[1, 0] = 1
        input_matrix[1, 1] = tList[3]
        input_matrix[1, 2] = tList[3] ** 2
        input_matrix[1, 3] = tList[3] ** 3
        input_matrix[2, 0] = 0
        input_matrix[2, 1] = 1
        input_matrix[2, 2] = 2 * tList[3]
        input_matrix[2, 3] = 3 * tList[3] ** 2
        input_matrix[3, 0] = 1
        input_matrix[3, 1] = tList[4]
        input_matrix[3, 2] = tList[4] ** 2
        input_matrix[3, 3] = tList[4] ** 3

        ordinate_vector[0] = qList[2]
        ordinate_vector[1] = qList[3]
        ordinate_vector[2] = 0
        ordinate_vector[3] = qList[4]

        try: #compute cubic polynomial
            result_vector = np.linalg.solve(input_matrix, ordinate_vector)
            coeffs = np.flipud(result_vector)
            dual_binomial_used = False
        except: #if the cubic polynomial cannot compute
            dual_binomial_used = True
            result_vector = None

        # I'll just copy the great explanation from the excel version:
        # Now we need to check for inflections.  To accomplish this daring feat of mathematics we
        # will be taking the second derivative and solving for the zero.  Since it's
        # possible for there to be a 0 as the third order coefficient, we have to make sure to verify that it's not a
        # constant before we start.  (The leading coefficient being a zero is a good thing, this means a binomial fit,
        # and thusly no inflections at all.)

        if not dual_binomial_used and coeffs[0] <> 0:  # A leading coefficient of zero indicates a binomial
            # Check to see if A is zero.  Since zero is good we'll only operate if A is non - zero.

            # The second derivative ofa cubic polynomial is  AX^3 + BX^2 + CX + D is 6AX + 2B so the zero is set at
            # -2B / 6A which reduces to B / (A * (-3)).
            zero_point=coeffs[1]/(coeffs[0]*(-3))

            # We're looking for the inflection point landing inside the range we're working in so we want zero point
            # to be less than start or more than end.  But numerical error in the zero point calculation could
            # artificially place the point inside, so we allow for 1% of the total width excursion of the zero point
            # into the invalid range.  This should have little to no impact on valid systems and doesn't rule out
            # systems where the inflection point is right at the intersection point (actually, we WANT that to be true
            # since the ACTUAL curve has an inflection point around there.)  If an inflection point is found within the
            # segment, it will switch to the dual binomial method

            if tList[2] + .01*self.w75 < zero_point < tList[4] - .01*self.w75: dual_binomial_used = True
        if dual_binomial_used:  #Split segment 2 into segment 2.1 and 2.2
            # Setup Solver for the segment 2.1 binomial
            input_matrix = np.zeros((3, 3))  # Matrix for 3-dimensional linear equation coefficient matrix
            ordinate_vector = np.zeros(3)  # Vector for dependent variables
            # The equations are:
            # T(2)^2 * A + T(2) * B + C = Q(2) (point T(2),Q(2))
            # T(3)^2 * A + T(3) * B + C = Q(3) (point T(3),Q(3))
            # T(3)^2 * 2A + B = 0 (Derivative at peak is 0)

            input_matrix[0, 0] = 1
            input_matrix[0, 1] = tList[2]
            input_matrix[0, 2] = tList[2] ** 2
            input_matrix[1, 0] = 1
            input_matrix[1, 1] = tList[3]
            input_matrix[1, 2] = tList[3] ** 2
            input_matrix[2, 0] = 0
            input_matrix[2, 1] = 1
            input_matrix[2, 2] = tList[3] * 2

            ordinate_vector[0] = qList[2]
            ordinate_vector[1] = qList[3]
            ordinate_vector[2] = 0

            try: #compute binomial
                result_vector = np.linalg.solve(input_matrix, ordinate_vector)
                coeffs = np.flipud(result_vector)
            except: #Give up and go linear
                segment2_1_slope=(qList[3]-qList[2])/(tList[3]-tList[2])
                segment2_1_intercept=qList[2]-segment2_1_slope*tList[2]
                coeffs =(segment2_1_slope,segment2_1_intercept)
                result_vector = None
            self.uhCurveData.append((tList[3],coeffs))

            # Update Solver for the segment 2.2 binomial
            # Swap Out the first equation from the previous setup with point 4, the other two can remain
            # The equations are:
            # T(4)^2 * A + T(4) * B + C = Q(4) (point T(4),Q(4))

            input_matrix[0, 0] = 1
            input_matrix[0, 1] = tList[4]
            input_matrix[0, 2] = tList[4] ** 2

            ordinate_vector[0] = qList[4]

            try: #compute binomial
                result_vector = np.linalg.solve(input_matrix, ordinate_vector)
                coeffs = np.flipud(result_vector)
            except: # Give up and go linear
                segment2_2_slope = (qList[4] - qList[3]) / (tList[4] - tList[3])
                segment2_2_intercept = qList[3] - segment2_2_slope * tList[3]
                coeffs = (segment2_2_slope,segment2_2_intercept)
                result_vector = None
            self.uhCurveData.append((tList[4], coeffs))

        else:
            self.uhCurveData.append((tList[4],coeffs))

        # ------Compute Segment 3 t(4) to t(5) (Linear Fit)------
        segment3_slope=(qList[5]-qList[4]) / (tList[5]-tList[4])
        segment3_intercept=qList[4]-segment3_slope * tList[4]
        coeffs = (segment3_slope,segment3_intercept)
        self.uhCurveData.append((tList[5],coeffs))

        #Compute area under the curve
        end_time=0
        uhCumulativeArea=0
        for segment in self.uhCurveData:
            begin_time=end_time
            end_time=segment[0]
            expanded_coeffs=np.append(np.zeros(4-len(segment[1])),segment[1]) #pads leading zeros into lower order coefficients
            thisarea = (expanded_coeffs[0] * (end_time ** 4) / 4 + expanded_coeffs[1] * (end_time ** 3) / 3 +
                        expanded_coeffs[2] * (end_time ** 2) / 2 + expanded_coeffs[3] * end_time -
                        (expanded_coeffs[0] * (begin_time ** 4) / 4 + expanded_coeffs[1] * (begin_time ** 3) / 3 +
                        expanded_coeffs[2] * (begin_time ** 2) / 2 + expanded_coeffs[3] * begin_time))
            uhCumulativeArea += thisarea

        uhCumulativeVolume=uhCumulativeArea*60.0
        VolRemaining=self.uhVolume-uhCumulativeVolume

        # Compute T6 and T7
        tList.append(None) #Hold for T6
        tList.append(tList[5]+2*VolRemaining/(60*0.3667*qList[3])) #T7
        tList[6]=tList[5]+0.333333333*(tList[7]-tList[5])

        # ------Compute Segment 4 t5 to t6 (Linear Fit)------
        segment4_slope=(qList[6]-qList[5]) / (tList[6]-tList[5])
        segment4_intercept=qList[5]-segment4_slope * tList[5]
        coeffs = (segment4_slope,segment4_intercept)
        self.uhCurveData.append((tList[6],coeffs))
        uhCumulativeArea += segment4_slope * tList[6] ** 2 / 2 + segment4_intercept * tList[6] - (
                            segment4_slope * tList[5] ** 2 / 2 + segment4_intercept * tList[5])

        # ------Compute Segment 5 t6 to t7 (Linear Fit)------
        segment5_slope=(qList[7]-qList[6]) / (tList[7]-tList[6])
        segment5_intercept=qList[6]-segment5_slope * tList[6]
        coeffs = (segment5_slope,segment5_intercept)
        self.uhCurveData.append((tList[7],coeffs))
        uhCumulativeArea += segment5_slope * tList[7] ** 2 / 2 + segment5_intercept * tList[7] - (
                            segment5_slope * tList[6] ** 2 / 2 + segment5_intercept * tList[6])

        uhCumulativeVolume = uhCumulativeArea * 60.0
        uhVolError = (self.uhVolume - uhCumulativeVolume) / self.uhVolume

        # ----Compute Unit Hydrograph----
        numSteps = int(math.ceil(tList[7] / self.timeStep))
        self.unitHydrograph = []
        thisCurveData=None
        for step in range(1,numSteps+1):
            thisTime=step*self.timeStep
            if thisCurveData is None or thisCurveData[0] < thisTime: #Test if we need to find new uh coefficients.
                lastvalue=0
                for i in range(0,len(self.uhCurveData)):
                    if lastvalue < thisTime <= self.uhCurveData[i][0]:
                        thisCurveData=self.uhCurveData[i]
                    lastvalue=self.uhCurveData[i][0]
                if thisTime > tList[7] or thisTime <= 0: thisCurveData=[0,[0]] #Flows are 0 beyond the end of the unit hydrograph
                thisCoeffs=np.append(np.zeros(4-len(thisCurveData[1])),thisCurveData[1])
            thisQ = (thisCoeffs[0]*thisTime ** 3 + thisCoeffs[1]*thisTime ** 2 + thisCoeffs[2]*thisTime + thisCoeffs[3])
            self.unitHydrograph.append(thisQ)

    def plot(self):
        import matplotlib.pyplot as plt
        timeData=np.array(range(len(self.unitHydrograph))) * self.timeStep
        plt.plot(timeData,self.unitHydrograph)
        plt.show()


class Runoff():
    # Runoff computes and holds the flow information
    #  excess precipitation information
    #  Subcatchment, RainGage, unitHydrograph objects as arguments

    def __init__(self,subcatchment,rainGage,timeStep,unitHydrograph = None):
        self.subcatchment=subcatchment # Subcatchment object
        self.rainGage=rainGage # RainGage object
        self.timeStep = timeStep
        if unitHydrograph is not None:
            self.unitHydrograph=unitHydrograph
            if self.unitHydrograph.timeStep != self.timeStep: errorMessages.append("Runoff timeStep != unit hydrograph timeStep, ignoring runoff timeStep")
        else:
            self.unitHydrograph = UnitHydrograph(self.subcatchment,self.rainGage.oneHourDepth,timeStep)

        # --calculated parameters
        self.excessPrecip = None #List containing excess precipitation values
        self.runoff = None #List containing runoff values


        # --execute on initialization
        self._computeExcessPrecip()
        self._computeFlows()

    def _computeExcessPrecip(self):
        decImperv = self.subcatchment.impervious / 100.00  # easier than dividing by 100 every time
        if decImperv <= 0: decImperv = almostZero
        if decImperv >= 1: decImperv = 1 - almostZero
        imperviousDepressionStorage=self.subcatchment.imperviousDepressionStorage
        rpaDepressionStorage=self.subcatchment.perviousDepressionStorage
        spaDepressionStorage=self.subcatchment.perviousDepressionStorage
        lastFt = self.subcatchment.hortonsInitial  # Initialize the starting infiltration rate to hortons initial
        self.excessPrecip=[]

        #Compute effective precipitation for each timeStep

        if self.rainGage.timeStep < self.unitHydrograph.timeStep : raise ValueError("Unit Hydrograph Timestep Cannot Exceed RainGage Timestep")
        for stepTime in range(int(self.unitHydrograph.timeStep),int(len(self.rainGage.rainDepths) * self.rainGage.timeStep + self.unitHydrograph.timeStep), int(self.unitHydrograph.timeStep)):

            incrementalPrecip = self.rainGage.rainDepths[int(math.ceil(float(stepTime) / self.rainGage.timeStep))-1]

            # ------------Compute Impervious Area (DCIA + UIA) effective precipitation
            if imperviousDepressionStorage > 0: # everything goes to depression storage, no impervious runoff
                if incrementalPrecip <= imperviousDepressionStorage:
                    imperviousDepressionStorage -= incrementalPrecip
                    effectiveImperviousPrecip = 0.0
                else: # some goes to depression storage, the rest runs off , less the impervious loss percent (5%)
                    effectiveImperviousPrecip = .95 * (decImperv *
                                                              (incrementalPrecip-imperviousDepressionStorage))
                    imperviousDepressionStorage = 0.0

            else: # depression storage is full - everything runs off, less the impervious loss percent (5%)
                effectiveImperviousPrecip = .95 * decImperv * incrementalPrecip


            #Compute DCIF and UIF precipitation
            effectiveDcifPrecip = effectiveImperviousPrecip * self.subcatchment.dcif #Eqn B-12
            effectiveUifPrecip = effectiveImperviousPrecip * self.subcatchment.uif #Eqn B-13

            #Compute maximum infiltration using Hortons equation
            thisFt=(self.subcatchment.hortonsFinal+(self.subcatchment.hortonsInitial - self.subcatchment.hortonsFinal) *
                    math.exp(-1.0 * self.subcatchment.hortonsDecay * stepTime * 60.0)) # Eqn B-8
            maxInfiltration = ((thisFt + lastFt) / 2.0) * (self.rainGage.timeStep / 60.0)  #Figure B-4
            lastFt=thisFt

            # ------------Compute Separate Pervious Area (SPA) effective precipitation

            if incrementalPrecip < maxInfiltration:# all the water infiltrates
                effectiveSpaPrecip=0.0

            else: #not all the water infiltrates, check depression storage
                remainingSpaPrecip = incrementalPrecip - maxInfiltration #whats left after infiltration
                if spaDepressionStorage > 0: #if depression storage volume is remaining
                    if remainingSpaPrecip <= spaDepressionStorage: #all the water goes into depression storage
                        spaDepressionStorage -= remainingSpaPrecip
                        effectiveSpaPrecip = 0.0
                    else: # some goes to depression storage, the rest runs off
                        effectiveSpaPrecip = (remainingSpaPrecip - spaDepressionStorage) * self.subcatchment.spf * (1.0 - decImperv)
                        spaDepressionStorage = 0.0
                else: #depression storage is full
                    effectiveSpaPrecip = remainingSpaPrecip * self.subcatchment.spf * (1.0 - decImperv)


            # ------------Compute Receiving Pervious Area (RPA) effective precipitation
            rpaInflow = incrementalPrecip + effectiveUifPrecip / (self.subcatchment.rpf * (1.0 - decImperv)) #distribute effective UIA precipitation into RPA
            if rpaInflow < maxInfiltration:# all the water infiltrates
                effectiveRpaPrecip = 0.0

            else: #not all the water infiltrates, check depression storage
                remainingRpaPrecip = rpaInflow - maxInfiltration
                if rpaDepressionStorage > 0.0: #if depression storage volume is remaining
                    if remainingRpaPrecip <= rpaDepressionStorage: #all the water goes into depression storage
                        rpaDepressionStorage -= remainingRpaPrecip
                        effectiveRpaPrecip = 0.0
                    else: # some goes to depression storage, the rest runs off
                        effectiveRpaPrecip = (remainingRpaPrecip - rpaDepressionStorage) * self.subcatchment.rpf * (1.0 - decImperv)
                        rpaDepressionStorage = 0.0
                else: #depression storage is full
                    effectiveRpaPrecip = remainingRpaPrecip * self.subcatchment.rpf * (1.0 - decImperv)
            self.excessPrecip.append((effectiveDcifPrecip+effectiveSpaPrecip+effectiveRpaPrecip))

    def _computeFlows(self):
        #Build a Matrix of flows for each timeStep and unit hydrograph output

        #initialize the blank matrix
        flowMatrix = np.zeros((len(self.excessPrecip),len(self.excessPrecip) + len(self.unitHydrograph.unitHydrograph)))

        #Multiply the Unit Hydrograph by the Excess Precipitation for each timeStep of precip
        for time in range(len(self.excessPrecip)):
            thisHydrograph = np.multiply(self.unitHydrograph.unitHydrograph, self.excessPrecip[time])
            flowMatrix[time,time:time + len(thisHydrograph)] = thisHydrograph

        #Sum the columns of the flow matrix to determine runoff
        self.runoff = np.sum(flowMatrix,0)

    def plotHydrograph(self):
        import matplotlib.pyplot as plt
        timeData=np.array(range(len(self.runoff))) * self.rainGage.timeStep
        plt.plot(timeData,self.runoff)
        plt.show()

def importExcel(filename):
    #  Imports subcatchment and raingage parameters from a CUHP 2.0 excel workbook
    # returns a list of catchment and raingage objects
    #  Requires xlrd (xlutils)
    import xlrd
    subcatchmentList = collections.OrderedDict()
    rgList = {}
    workbook = xlrd.open_workbook(filename)

    def _getText(cell): #returns formatted string
        if cell.ctype == 1: #if the cell is text
            if len(cell.value) > 0: return cell.value
            else: return None
        elif cell.ctype == 2: #if the cell is a number, we need to do some formatting
            if math.floor(cell.value) == cell.value:  # assume 10.0 should actually be '10'
                return str(int(cell.value))
            else:
                return str(cell.value)
        else:
            return None

    def _getNum(cell): #returns a float
        if 2 <= cell.ctype <= 3: #if the cell is a number or date cell
            return float(cell.value)
        elif cell.ctype == 1: #if the cell is text
            try:
                fvalue = float(cell.value) #see if the text looks like a number
                return fvalue
            except ValueError:
                return None
        else: return None

    #Get subcatchment paramaters
    worksheet = workbook.sheet_by_name('Subcatchments')

    parameterDict = {0:'name',1:'swmmNode',2:'rainGageName',3:'area',4:'centroidLength',5:'length',
                     6:'slope',7:"impervious",8:"perviousDepressionStorage",9:"imperviousDepressionStorage",
                     10:"hortonsInitial",11:'hortonsDecay',12:"hortonsFinal",13:"dciaLevel", 14:'dcifOverride',
                     16:"rpfOverride",19:"ctOverride",21:"cpOverride"}

    for i in range(10,worksheet.nrows):
        scName = _getText(worksheet.cell(i, 0))
        if scName is None: break #if we hit a blank name cell, stop reading subcatchments
        parameterList = {'name': scName} #Build Kwargs dictionary for subcatchment object
        for x in range(3,13,1): #The first 10 parameters are required
            thisParam = _getNum(worksheet.cell(i,x))
            if thisParam is None:
                print("invalid value in subcatchment " + scName + " parameter " + parameterDict[x])
                print("ignoring subcatchment")
                parameterList = None
                break
            else:
                parameterList.update({parameterDict[x]:thisParam})
        if parameterList is not None:
            for x in (1,2): #text Parameters
                thisParam = _getText(worksheet.cell(i, x))
                if thisParam is not None:
                    parameterList.update({parameterDict[x]:thisParam})
            for x in (13,14,16,19,21): #Optional Parameters
                thisParam = _getNum(worksheet.cell(i, x))
                if thisParam is not None:
                    parameterList.update({parameterDict[x]:thisParam})
            subcatchmentList.update([(parameterList['name'],Subcatchment(**parameterList))]) #kwargs definition for subcatchment

    #get raingage parameters
    worksheet = workbook.sheet_by_name('Raingages')
    rgNameType=[]
    for i in range(6,worksheet.nrows):
        rgName = _getText(worksheet.cell(i,0))
        rgType = worksheet.cell(i,3).value[:worksheet.cell(i,3).value.find(":")]
        rgNameType.append([rgName,rgType])
    for thisRg in rgNameType:
        worksheet = workbook.sheet_by_name(thisRg[0])
        if thisRg[1] == "sheet": #User defined gage
            flowList = [] #list for flows
            timeStep = None
            for i in range(5,worksheet.nrows):
                values = (_getNum(worksheet.cell(i,0)),_getNum(worksheet.cell(i,1)))
                if None in values: break #Stop importing for blank values
                if timeStep is None:
                    if i > 5: timeStep = (values[0] - _getNum(worksheet.cell(i-1,0))) * 24 * 60
                else:
                    if ((values[0] - _getNum(worksheet.cell(i-1,0))) * 24 * 60) != timeStep:
                        print ("User input raingage " + thisRg[0] + " timestep is not even, using first step only")
            flowList.append(values[1])
            if timeStep is not None and len(flowList) > 1:
                rgList.update({thisRg[0]:RainGage(**{"rgName":thisRg[0],"rgType":"UserInput","timeStep":timeStep,"userInputDepths":flowList})})

        if thisRg[1] == "dist":
            oneHourDepth = _getNum(worksheet.cell(1,1))
            returnPeriod = _getNum(worksheet.cell(2,1))
            if None not in (oneHourDepth, returnPeriod):
                rgList.update({thisRg[0]:RainGage(**{"rgType":"Standard","rgName":thisRg[0],"oneHourDepth":oneHourDepth,"returnPeriod":returnPeriod})})

        if thisRg[1] == "distarea":
            oneHourDepth = _getNum(worksheet.cell(1,1))
            sixHourDepth = _getNum(worksheet.cell(2, 1))
            correctionArea = _getNum(worksheet.cell(3, 1))
            returnPeriod = _getNum(worksheet.cell(4,1))
            if None not in (oneHourDepth, sixHourDepth, correctionArea, returnPeriod):
                rgList.update({thisRg[0]:RainGage(**{"rgType": "AreaCorrected", "rgName": thisRg[0], "oneHourDepth": oneHourDepth,
                                          "sixHourDepth":sixHourDepth, "correctionArea":correctionArea, "returnPeriod": returnPeriod})})
    return(subcatchmentList,rgList)


def outputUnitHydrographs(uhList,filename):
    # Writes the Unit Hydrograps to a file
    # Paramaters:
        # uhList - list of unitHydrograph objects to output
        # filename - filename to output to (eg. "c:\\temp\\outputfile.csv")
    flows=[]
    uhnames=[]
    timeSteps=[]
    numtimeSteps=[]
    for i in range(len(uhList)):
        timeSteps.append(uhList[i].timeStep)
        uhnames.append(uhList[i].subcatchment.name)
        numtimeSteps.append(len(uhList[i].unitHydrograph))
        flows.append(uhList[i].unitHydrograph)

    file = open(filename, 'w')
    file.write("Time,")
    for uhname in uhnames:
        file.write(uhname)
        file.write(",")
    file.write("\n")
    for timeStep in range(max(numtimeSteps)):
        currenttime=timeStep*timeSteps[0]
        file.write('%.1f' % currenttime)
        file.write(",")
        for i in range(len(flows)):
            if timeStep <= len(flows[i]):
                file.write('%.2f' % flows[i][timeStep-1])
            else:
                file.write('0.00')
            file.write(",")
        file.write("\n")
    file.close()


def outputHydrographs(rList,filename):
    # Writes the Unit Hydrograps to a file
    # Paramaters:
        # rList - list of runoff objects to output
        # filename - filename to output to (eg. "c:\\temp\\outputfile.csv")
    flows=[]
    hnames=[]
    timeSteps=[]
    numtimeSteps=[]
    for i in range(len(rList)):
        timeSteps.append(rList[i].rainGage.timeStep)
        hnames.append(rList[i].subcatchment.name)
        numtimeSteps.append(len(rList[i].runoff))
        flows.append(rList[i].runoff)

    file = open(filename, 'w')
    file.write("Time,")
    for hname in hnames:
        file.write(hname)
        file.write(",")
    file.write("\n")
    for timeStep in range(1,max(numtimeSteps)+1):
        currenttime=timeStep*timeSteps[0]
        file.write('%.1f' % currenttime)
        file.write(",")
        for i in range(len(flows)):
            if timeStep <= len(flows[i]):
                file.write('%.4f' % flows[i][timeStep-1])
            else:
                file.write('0.00')
            file.write(",")
        file.write("\n")
    file.close()

def writeSwmmFile(roList,filename,starttime=None):
    if starttime == None:
        starttime = datetime.datetime(2005,01,01)
    file=open(filename,'w')
    maxLength=0
    for ro in roList:
        if len(ro.runoff) > maxLength: maxLength = len(ro.runoff)
    file.write("SWMM5\n\n")
    file.write("%.0f" % maxLength)
    file.write("\n1\nFLOW CFS\n")
    file.write("%.0f" % len(roList) + "\n")

    for ro in roList:
        if ro.subcatchment.swmmNode is not None:
            file.write(ro.subcatchment.swmmNode + "\n")
        else:
            file.write(ro.subcatchment.name + "\n")

    file.write("\n")
    thistime = starttime
    for t in range(maxLength):
        thistime += datetime.timedelta(**{"minutes": roList[0].timeStep})
        for i in range(len(roList)):
            if roList[i].subcatchment.swmmNode is not None:
                writeString=roList[i].subcatchment.swmmNode
            else:
                writeString=roList[i].subcatchment.name
            writeString += thistime.strftime("  %Y  %m  %d  %H  %M  %S  ")
            if t < len(roList[i].runoff):
                writeString += str(roList[i].runoff[t])
            else:
                writeString += "0"
            file.write(writeString + "\n")
    file.close()
