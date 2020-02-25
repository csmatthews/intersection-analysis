# -----------------------------------------------------------------------------
# Name:        Intersection Analysis Tool
# Version: 	   1.1.0
# Purpose:     Analyzes intersections for crash analysis
# Author:      Christian Matthews, Rockingham Planning Commission
#              cmatthews@therpc.org
# Last Updated: 04/19/2019
# -----------------------------------------------------------------------------
# Import System Libraries
import arcpy
import time
import math
start_time = time.clock()
arcpy.env.overwriteOutput = True


# Setup
arcpy.env.workspace = r"O:\d-multiyear\d-Transportation_Plan\d-IntersectionAnalysis\d-data\IntersectionAnalysis.gdb"
crash = r"T:\d-accident\d-data\d-2017\Data.gdb\NH_Crashes_0616"
injury = r"T:\d-accident\d-data\d-2017\Data.gdb\NH_PersonalInjury_0616"
urban = r"G:\t-drive\d-urban_compacts\Compact.shp"
signals = r"G:\t-drive\d-traffic_signals\d-data\TrafficSignals.gdb\
            TrafficSignals_NH"
intersections = "Raymond"
print("Completed Setup: " + str(round((time.clock()-start_time)/60, 1)) +
      " Minutes")


# Add Fields
addFields = [["Urban", "SHORT", "Urban"],
             ["AADT_Bin", "LONG", 'AADT_Bin'],
             ["Signalized", "SHORT", "Signalized"],
             ["JoinField", "TEXT", "JoinField"],
             ["Bike_Ped_Fatality", "SHORT", "Bike/Ped Fatality"],
             ["Bike_Ped_Incap_Injury", "SHORT",
              "Bike/Ped Incapacitating Injury"],
             ["C_2006", "SHORT", "2006 Crashes"],
             ["C_2007", "SHORT", "2007 Crashes"],
             ["C_2008", "SHORT", "2008 Crashes"],
             ["C_2009", "SHORT", "2009 Crashes"],
             ["C_2010", "SHORT", "2010 Crashes"],
             ["C_2011", "SHORT", "2011 Crashes"],
             ["C_2012", "SHORT", "2012 Crashes"],
             ["C_2013", "SHORT", "2013 Crashes"],
             ["C_2014", "SHORT", "2014 Crashes"],
             ["C_2015", "SHORT", "2015 Crashes"],
             ["C_2016", "SHORT", "2016 Crashes"],
             ["Total_Crashes", "SHORT", "Total Crashes"],
             ["C_2006_2010", "DOUBLE", "2006-2010 Crashes"],
             ["C_2007_2011", "DOUBLE", "2007-2011 Crashes"],
             ["C_2008_2012", "DOUBLE", "2008-2012 Crashes"],
             ["C_2009_2013", "DOUBLE", "2009-2013 Crashes"],
             ["C_2010_2014", "DOUBLE", "2010-2014 Crashes"],
             ["C_2011_2015", "DOUBLE", "2011-2015 Crashes"],
             ["C_2012_2016", "DOUBLE", "2012-2016 Crashes"],
             ["Crash_Trend", "DOUBLE", "Crash Trend"],
             ["Fatality", "SHORT", "Fatality"],
             ["Incapacitating", "SHORT", "Incapacitating"],
             ["Nonincapacitating", "SHORT", "Nonincapacitating"],
             ["Possible", "SHORT", 'Possible'],
             ["No_Injury", "SHORT", "No Injury"],
             ["Crash_Rate", "DOUBLE", "Crash Rate"],
             ["Expected_Crash_Rate", "DOUBLE", "Expected Crash Rate"],
             ["Exposure", "DOUBLE", 'Exposure'],
             ["Critical_Crash_Rate", "DOUBLE", "Critical Crash Rate"],
             ["Crash_Rate_Dif", "DOUBLE", "Crash Rate Difference"],
             ["EPDO", "DOUBLE", 'EPDO'],
             ["Weighted_Score", "DOUBLE", 'Weighted Score']]
for field in addFields:
    arcpy.AddField_management(intersections, field[0], field[1], '', '', '',
                              field[2])
print("Added Fields: "+str(round((time.clock()-start_time)/60, 1)) +
      " Minutes")


# Spatial Joins
yrList = [['2006', '06'],
          ['2007', '07'],
          ['2008', '08'],
          ['2009', '09'],
          ['2010', '10'],
          ['2011', '11'],
          ['2012', '12'],
          ['2013', '13'],
          ['2014', '14'],
          ['2015', '15'],
          ['2016', '16']]
for yr in yrList:
    arcpy.MakeFeatureLayer_management(crash, "in_memory/C"+yr[0],
                                      "ACDYEAR = '"+yr[1]+"'")
    arcpy.SpatialJoin_analysis(intersections, "in_memory/C"+yr[0],
                               "in_memory/join_"+yr[0], "", "", "",
                               "WITHIN A DISTANCE", "105 FEET")
    arcpy.Delete_management("in_memory/C"+yr[0])
    arcpy.JoinField_management(intersections, "INTERSECTION_ID",
                               "in_memory/join_"+yr[0], "INTERSECTION_ID",
                               ["Join_Count"])
    arcpy.Delete_management("in_memory/join_"+yr[0])
    arcpy.CalculateField_management(intersections, "C_"+yr[0], "!Join_Count!",
                                    "PYTHON3")
    arcpy.DeleteField_management(intersections, "Join_Count")
crList = [['k', 'Killed', 'Fatality'],
          ['i', 'Incapacitating', 'Incapacitating'],
          ['ni', 'Non_Incapacitating', 'Nonincapacitating'],
          ['p', 'Possible', 'Possible'],
          ['no', 'No Apparent Injury', 'No_Injury']]
for crType in crList:
    arcpy.MakeFeatureLayer_management(crash, "in_memory/crash_"+crType[0],
                                      "SEVERITY = '"+crType[1]+"'")
    arcpy.SpatialJoin_analysis(intersections, "in_memory/crash_"+crType[0],
                               "in_memory/join_"+crType[0], "", "", "",
                               "WITHIN A DISTANCE", "105 FEET")
    arcpy.Delete_management("in_memory/crash_"+crType[0])
    arcpy.JoinField_management(intersections, "INTERSECTION_ID",
                               "in_memory/join_"+crType[0], "INTERSECTION_ID",
                               ["Join_Count"])
    arcpy.Delete_management("in_memory/join_"+crType[0])
    arcpy.CalculateField_management(intersections, crType[2], "!Join_Count!",
                                    "PYTHON3")
    arcpy.DeleteField_management(intersections, "Join_Count")
exList = ['Urban', 'Signalized']
for ex in exList:
    arcpy.SpatialJoin_analysis(intersections, urban, "in_memory/"+ex,
                               "", "", "", "INTERSECT")
    arcpy.JoinField_management(intersections, "INTERSECTION_ID",
                               "in_memory/"+ex, "INTERSECTION_ID",
                               ["Join_Count"])
    arcpy.Delete_management("in_memory/"+ex)
    arcpy.CalculateField_management(intersections, ex, "!Join_Count!",
                                    "PYTHON3")
    arcpy.DeleteField_management(intersections, "Join_Count")
print("Completed Spatial Joins: "+str(round((time.clock()-start_time)/60, 1)) +
      " Minutes")


# Field Calculations

fields = ("C_2006", "C_2007", "C_2008", "C_2009", "C_2010", "C_2011", "C_2012",
          "C_2013", "C_2014", "C_2015", "C_2016", "Total_Crashes")
with arcpy.da.UpdateCursor(intersections, fields) as cursor:
    for row in cursor:
        row[11] = row[0] + row[1] + row[2] + row[3] + row[4] + row[5] + row[6]
        + row[7] + row[8] + row[9] + row[10]
        cursor.updateRow(row)
del cursor

fields = ("C_2006", "C_2007", "C_2008", "C_2009", "C_2010", "C_2011", "C_2012",
          "C_2013", "C_2014", "C_2015", "C_2016", "C_2006_2010", "C_2007_2011",
          "C_2008_2012", "C_2009_2013", "C_2010_2014", "C_2011_2015",
          "C_2012_2016")
with arcpy.da.UpdateCursor(intersections, fields) as cursor:
    for row in cursor:
        row[11] = (row[0]+row[1]+row[2]+row[3]+row[4])/5
        row[12] = (row[1]+row[2]+row[3]+row[4]+row[5])/5
        row[13] = (row[2]+row[3]+row[4]+row[5]+row[6])/5
        row[14] = (row[3]+row[4]+row[5]+row[6]+row[7])/5
        row[15] = (row[4]+row[5]+row[6]+row[7]+row[8])/5
        row[16] = (row[5]+row[6]+row[7]+row[8]+row[9])/5
        row[17] = (row[6]+row[7]+row[8]+row[9]+row[10])/5
        cursor.updateRow(row)
del cursor

fields = ("C_2006_2010", "C_2012_2016", "Crash_Trend")
with arcpy.da.UpdateCursor(intersections, fields) as cursor:
    for row in cursor:
        row[2] = row[1]-row[0]
        cursor.updateRow(row)
del cursor

fields = ("AADT_For_I", "Total_Crashes", "Crash_Rate")
with arcpy.da.UpdateCursor(intersections, fields) as cursor:
    for row in cursor:
        if row[0] is not None:
            row[2] = (row[1]*1000000)/(365*10*row[0])
        cursor.updateRow(row)
del cursor

fields = ("AADT_For_I", "AADT_Bin")
with arcpy.da.UpdateCursor(intersections, fields) as cursor:
    for row in cursor:
        if row[0] is not None and row[0] <= 1000:
            row[1] = 1
        elif row[0] is not None and row[0] > 1000 and row[0] <= 2500:
            row[1] = 2
        elif row[0] is not None and row[0] > 2500 and row[0] <= 10000:
            row[1] = 3
        elif row[0] is not None and row[0] > 10000:
            row[1] = 4
        cursor.updateRow(row)
del cursor

arcpy.Statistics_analysis(intersections, intersections+"_stats",
                          [["Crash_Rate", "Mean"]],
                          ["SEGMENTS", "Urban", "AADT_Bin", "Signalized"])
arcpy.AddField_management(intersections+"_stats", "JoinField", "TEXT")

fields = ("SEGMENTS", "Urban", "AADT_Bin", "JoinField", "Signalized")
with arcpy.da.UpdateCursor(intersections+"_stats", fields) as cursor:
    for row in cursor:
        row[3] = str(row[0]) + str(row[1]) + str(row[2]) + str(row[4])
        cursor.updateRow(row)
del cursor

fields = ("SEGMENTS", "Urban", "AADT_Bin", "JoinField", "Signalized")
with arcpy.da.UpdateCursor(intersections, fields) as cursor:
    for row in cursor:
        row[3] = str(row[0]) + str(row[1]) + str(row[2]) + str(row[4])
        cursor.updateRow(row)
del cursor

arcpy.JoinField_management(intersections, "JoinField", intersections+"_stats",
                           "JoinField", "MEAN_Crash_Rate")

fields = ("Expected_Crash_Rate", "MEAN_Crash_Rate")
with arcpy.da.UpdateCursor(intersections, fields) as cursor:
    for row in cursor:
        row[0] = row[1]
        cursor.updateRow(row)
del cursor
arcpy.DeleteField_management(intersections, "MEAN_Crash_Rate")

fields = ("AADT_For_I", "SEGMENTS", "Exposure")
with arcpy.da.UpdateCursor(intersections, fields) as cursor:
    for row in cursor:
        if row[0] is not None:
            row[2] = row[0]*365*10*(row[1]*0.014205)
            cursor.updateRow(row)
del cursor

fields = ("Exposure", "Expected_Crash_Rate", "Critical_Crash_Rate")
with arcpy.da.UpdateCursor(intersections, fields) as cursor:
    for row in cursor:
        if row[1] is not None and row[0] > 0:
            row[2] = row[1]+(2.576*math.sqrt(row[1]/row[0]))+(1/(2*row[0]))
            cursor.updateRow(row)
del cursor

fields = ("Critical_Crash_Rate", "Crash_Rate", "Crash_Rate_Dif")
with arcpy.da.UpdateCursor(intersections, fields) as cursor:
    for row in cursor:
        if row[0] is not None and row[1] is not None:
            row[2] = row[1]-row[0]
            cursor.updateRow(row)
del cursor

fields = ("EPDO", "Fatality", "Incapacitating", "Nonincapacitating",
          "Possible", "No_Injury")
with arcpy.da.UpdateCursor(intersections, fields) as cursor:
    for row in cursor:
        row[0] = row[1]*574.01+row[2]*30.44+row[3]*11.12+row[4]*6.27
        +row[5]*1.01
        cursor.updateRow(row)
del cursor

maxCrashRateDifList = []
with arcpy.da.SearchCursor(intersections, "Crash_Rate_Dif") as cursor:
    for row in cursor:
        if row[0] is not None:
            maxCrashRateDifList.append(row[0])
del cursor

maxCrashRateList = []
with arcpy.da.SearchCursor(intersections, "Crash_Rate") as cursor:
    for row in cursor:
        if row[0] is not None:
            maxCrashRateList.append(row[0])
del cursor

maxTotalCrashesList = []
with arcpy.da.SearchCursor(intersections, "Total_Crashes") as cursor:
    for row in cursor:
        if row[0] is not None:
            maxTotalCrashesList.append(row[0])
del cursor

maxCrashRateDif = sorted(maxCrashRateDifList, reverse=True)[0]
maxCrashRate = sorted(maxCrashRateList, reverse=True)[0]
maxEPDO = sorted([row[0] for row in arcpy.da.SearchCursor(intersections,
                  "EPDO")], reverse=True)[0]
maxCrashTrend = sorted([row[0] for row in arcpy.da.SearchCursor(intersections,
                        "Crash_Trend")], reverse=True)[0]
maxTotalCrashes = sorted(maxTotalCrashesList, reverse=True)[0]

fields = ("Weighted_Score", "EPDO", "Crash_Rate_Dif", "Crash_Trend",
          "Crash_Rate", "Total_Crashes")
with arcpy.da.UpdateCursor(intersections, fields) as cursor:
    for row in cursor:
        if row[2] is not None:
            row[0] = round(((row[1]/maxEPDO) + (row[2]/maxCrashRateDif) +
                            (row[3]/maxCrashTrend) + (row[4]/maxCrashRate) +
                            (row[5]/maxTotalCrashes))/5, 3)
            cursor.updateRow(row)
del cursor
print("Finished --- %s seconds ---" % (time.clock() - start_time))
