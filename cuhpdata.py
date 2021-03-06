# cuhpy P2.0.0 data file
# by David Delagarza / RESPEC
# June 2017
# This file contains data, such as coefficients and computation factors needed to run cuhpy
# No actual cuhpy code is in this file


class _Data(): #This class holds coefficients and data needed for CUHP
    def __init__(self):
        # dcifCoeff is a library of coefficients based on Eqns B-5, B-6, and B-7
        # used to calculate the directly connected impervious fraction
        # Format - (DCIA LEVEL(MaxI,x,y)) Given D=x*I+y valid for I<MaxI
        self.dcifCoeff = (((.4, 2, 0), (.6, .5, .6), (.9, .2, .78), (1.0, .4, .6)),
                    ((.1, 1.1, 0), (.2, 1.2, -.01), (.3, 1.4, -.05), (.4, 1.3, -.02), (.5, 1.1, -.01), (.6, .9, .16),
                     (.7, .7, .28), (.8, .8, .21), (.9, .7, .29), (1.0, .8, .2)),
                    ((.6, .5, 0), (.7, 1, -.3),
                     (1, 2, -1)))

        # dcifCoeff is a library of coefficients based on Eqns B-5, B-6, and B-7
        # used to calculate the recieving pervious fraction
        # Format - (DCIA LEVEL(MaxI,x,y)) Given D=x*I+y valid for I<MaxI
        self.rpfCoeff = (((.1, 1, 0), (.2, .3, .07), (.3, .4, .05), (.4, .3, .08), (.5, .3, .08),
                    (.6, .4, .03), (.7, .3, .09), (.8, .3, .09), (.9, .4, .01), (1.0, .3, .1)),
                   ((.1, 2.0, 0), (.2, .4, .16), (.3, .5, .14), (.4, .4, .17), (.5, .5, .13),
                    (.6, .4, .18), (.7, .5, .12), (.8, .4, .19), (.9, .5, .11), (1, .4, .2)),
                   ((.1, 3, 0), (.2, .6, .24), (.3, .5, .26), (.4, .6, .23), (.5, .5, .27),
                    (.6, .6, .22), (.7, .5, .28), (.8, .6, .21), (.9, .5, .29), (1, .6, .2)))

        self.ctCoeff = ((10,0,-0.00371,0.163),(40,.0000230,-.0022400,.146),(100,0.0000033,-.0008010,.12))
        self.pCoeff = ((25,0.00060,0.00000,2.30),(100,-0.000500,0.120000,0.0000))
        self.cpCoeff = ((120,1.30,0.450),('NA',1.000,0.3000))
        self.kcoeff = ((.2,(-0.1895, 0.536, -1.6925, 4.9141),(0,0,0,0)),
                       (.8, (0.0554, -0.1028, 0.2302, 0.0776),(-0.0512, 0.143, -.4085, .9755)),
                       (1, (0.232, -0.2275, 1.0019, -0.147), (-0.0235, 0.2286, -1.0032, 1.1474)))


        self.oneHourDistribution = ((None,(2,5,10,25,50,100,500)), #Return Periods
                                    (0, (0, 0, 0, 0, 0, 0, 0)),
                                    (5,(0.02,0.02,0.02,0.013,0.013,0.01,0.01)),
                                    (10,(0.04,0.037,0.037,0.035,0.035,0.03,0.03)),
                                    (15,(0.084,0.087,0.082,0.05,0.05,0.046,0.046)),
                                    (20,(0.16,0.153,0.15,0.08,0.08,0.08,0.08)),
                                    (25,(0.25,0.25,0.25,0.15,0.15,0.14,0.14)),
                                    (30,(0.14,0.13,0.12,0.25,0.25,0.25,0.25)),
                                    (35,(0.063,0.058,0.056,0.12,0.12,0.14,0.14)),
                                    (40,(0.05,0.044,0.043,0.08,0.08,0.08,0.08)),
                                    (45,(0.03,0.036,0.038,0.05,0.05,0.062,0.062)),
                                    (50,(0.03,0.036,0.032,0.05,0.05,0.05,0.05)),
                                    (55,(0.03,0.03,0.032,0.032,0.032,0.04,0.04)),
                                    (60,(0.03,0.03,0.032,0.032,0.032,0.04,0.04)),
                                    (65,(0.03,0.03,0.032,0.032,0.032,0.04,0.04)),
                                    (70,(0.02,0.03,0.032,0.024,0.024,0.02,0.02)),
                                    (75,(0.02,0.025,0.032,0.024,0.024,0.02,0.02)),
                                    (80,(0.02,0.022,0.025,0.018,0.018,0.012,0.012)),
                                    (85,(0.02,0.022,0.019,0.018,0.018,0.012,0.012)),
                                    (90,(0.02,0.022,0.019,0.014,0.014,0.012,0.012)),
                                    (95,(0.02,0.022,0.019,0.014,0.014,0.012,0.012)),
                                    (100,(0.02,0.015,0.019,0.014,0.014,0.012,0.012)),
                                    (105,(0.02,0.015,0.019,0.014,0.014,0.012,0.012)),
                                    (110,(0.02,0.015,0.019,0.014,0.014,0.012,0.012)),
                                    (115,(0.01,0.015,0.017,0.014,0.014,0.012,0.012)),
                                    (120,(0.01,0.013,0.013,0.014,0.014,0.012,0.012)))

        self.darf_under_10yr = ((None,(2,5,10,15,20,30,40,50,75)),
                                (0, (1, 1, 1, 1, 1, 1, 1, 1, 1)),
                                (5,(1,1,1,1,1,1,1,1,1)),
                                (10,(1,1,1,1,1,1,1,1,1)),
                                (15,(1,0.97,0.94,0.91,0.9,0.85,0.75,0.65,0.56)),
                                (20,(1,0.86,0.75,0.68,0.61,0.55,0.48,0.42,0.35)),
                                (25,(1,0.86,0.75,0.68,0.61,0.55,0.48,0.42,0.35)),
                                (30,(1,0.86,0.75,0.68,0.61,0.55,0.48,0.42,0.42)),
                                (35,(1,0.97,0.94,0.91,0.9,0.9,0.9,0.9,0.89)),
                                (40,(1,0.97,0.94,0.91,0.9,0.9,0.9,0.9,0.89)),
                                (45,(1,1,1,1.02,1.02,1.01,1.01,1.01,1)),
                                (50,(1,1,1,1.02,1.02,1.01,1.01,1.01,1)),
                                (55,(1,1,1,1.02,1.02,1.01,1.01,1.01,1)),
                                (60,(1,1,1,1.02,1.02,1.01,1.01,1.01,1)),
                                (65,(1,1,1,1.02,1.02,1.01,1.01,1.01,1)),
                                (70,(1,1,1,1.02,1.02,1.01,1.01,1.01,1)),
                                (75,(1,1,1,1.02,1.02,1.01,1.01,1.01,1)),
                                (80,(1,1,1,1.02,1.02,1.01,1.01,1.01,1)),
                                (85,(1,1,1,1.02,1.02,1.01,1.01,1.01,1)),
                                (90,(1,1,1,1.02,1.02,1.01,1.01,1.01,1)),
                                (95,(1,1,1,1.02,1.02,1.01,1.01,1.01,1)),
                                (100,(1,1,1,1.02,1.02,1.01,1.01,1.01,1)),
                                (105,(1,1,1,1.02,1.02,1.01,1.01,1.01,1)),
                                (110,(1,1,1,1.02,1.02,1.01,1.01,1.01,1)),
                                (115,(1,1,1,1.02,1.02,1.01,1.01,1.01,1)),
                                (120,(1,1,1,1.02,1.02,1.01,1.01,1.01,1)),
                                (125,(0,0,0,1,1,1,1,1,1)),
                                (130,(0,0,0,1,1,1,1,1,1)),
                                (135,(0,0,0,1,1,1,1,1,1)),
                                (140,(0,0,0,1,1,1,1,1,1)),
                                (145,(0,0,0,1,1,1,1,1,1)),
                                (150,(0,0,0,1,1,1,1,1,1)),
                                (155,(0,0,0,1,1,1,1,1,1)),
                                (160,(0,0,0,1,1,1,1,1,1)),
                                (165,(0,0,0,1,1,1,1,1,1)),
                                (170,(0,0,0,1,1,1,1,1,1)),
                                (175,(0,0,0,1,1,1,1,1,1)),
                                (180,(0,0,0,1,1,1,1,1,1)),
                                (185,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (190,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (195,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (200,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (205,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (210,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (215,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (220,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (225,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (230,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (235,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (240,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (245,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (250,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (255,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (260,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (265,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (270,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (275,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (280,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (285,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (290,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (295,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (300,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (305,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (310,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (315,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (320,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (325,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (330,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (335,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (340,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (345,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (350,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (355,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (360,(0,0,0,1.23,1.28,1.3,1.32,1.33,1.33)),
                                (365, (0, 0, 0, 1.23, 1.28, 1.3, 1.32, 1.33, 1.33)))

        self.darf_over_10yr = ((None,(15,20,30,40,50,75)), #Watershed area by mi^2
                        (0, (1.15, 1.15, 1.15, 1.15, 1.15, 1.1)),
                        (5,(1.15,1.15,1.15,1.15,1.15,1.1)), #Depth corrections by min
                        (10,(1.15,1.15,1.15,1.15,1.15,1.1)),
                        (15,(1.15,1.15,1.15,1.15,1.15,1.1)),
                        (20,(1.25,1.18,1.1,1.05,1,0.9)),
                        (25,(0.73,0.69,0.64,0.6,0.58,0.55)),
                        (30,(0.73,0.69,0.64,0.6,0.58,0.55)),
                        (35,(0.73,0.69,0.64,0.6,0.58,0.55)),
                        (40,(1.05,1.02,0.95,0.9,0.85,0.8)),
                        (45,(1.2,1.2,1.2,1.15,1.05,0.95)),
                        (50,(1.15,1.15,1.15,1.15,1.05,0.95)),
                        (55,(1.15,1.15,1.15,1.15,1.15,1.15)),
                        (60,(1.15,1.15,1.15,1.15,1.15,1.15)),
                        (65,(1.08,1.1,1.13,1.15,1.15,1.15)),
                        (70,(1.08,1.1,1.13,1.15,1.15,1.15)),
                        (75,(1.08,1.1,1.13,1.15,1.15,1.15)),
                        (80,(1.08,1.1,1.13,1.15,1.15,1.15)),
                        (85,(1.08,1.1,1.13,1.15,1.15,1.15)),
                        (90,(1.08,1.1,1.13,1.15,1.15,1.15)),
                        (95,(1.08,1.1,1.13,1.15,1.15,1.15)),
                        (100,(1.08,1.1,1.13,1.15,1.15,1.15)),
                        (105,(1.08,1.1,1.13,1.15,1.15,1.15)),
                        (110,(1.08,1.1,1.13,1.15,1.15,1.15)),
                        (115,(1.08,1.1,1.13,1.15,1.15,1.15)),
                        (120,(1.08,1.1,1.13,1.15,1.15,1.15)),
                        (125,(1.08,1.1,1.13,1.15,1.25,1.25)),
                        (130,(1.08,1.1,1.13,1.15,1.25,1.25)),
                        (135,(1.08,1.1,1.13,1.15,1.25,1.25)),
                        (140,(1.08,1.1,1.13,1.15,1.25,1.25)),
                        (145,(1.08,1.1,1.13,1.15,1.25,1.25)),
                        (150,(1.08,1.1,1.13,1.15,1.25,1.25)),
                        (155,(1.08,1.1,1.13,1.15,1.25,1.25)),
                        (160,(1.08,1.1,1.13,1.15,1.25,1.25)),
                        (165,(1.08,1.1,1.13,1.15,1.25,1.25)),
                        (170,(1.08,1.1,1.13,1.15,1.25,1.25)),
                        (175,(1.08,1.1,1.13,1.15,1.25,1.25)),
                        (180,(1.08,1.1,1.13,1.15,1.25,1.25)),
                        (185,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (190,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (195,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (200,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (205,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (210,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (215,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (220,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (225,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (230,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (235,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (240,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (245,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (250,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (255,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (260,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (265,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (270,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (275,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (280,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (285,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (290,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (295,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (300,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (305,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (310,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (315,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (320,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (325,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (330,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (335,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (340,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (345,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (350,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (355,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (360,(1.05,1.1,1.1,1.1,1.1,1.13)),
                        (360, (1.05, 1.1, 1.1, 1.1, 1.1, 1.13)))
