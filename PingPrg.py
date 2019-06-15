#######################################################################################
#  Ping Program:
#  Developed by Jorge Rodriguez
#  Date Created: Nov-7-2017
#  Last Updated: Feb-3-2018
######################################################################################

import os
import sys # Requires for the Class
import re  # Required for teh Class
import subprocess
import datetime
from time import time, sleep
try:
    import socket
    import threading
#    fromthreading import *
except:
    print ("NO Sockets is available")

try:
    from odbc_connector import *
    Is_ODBC_Available = True
except:
    print ("********************************************************************************** \n")
    print ("*** NO ODBC Library Found, please download it in order to access the Databases *** \n")
    print ("********************************************************************************** \n")
    Is_ODBC_Available = False    

Username = os.getlogin()

#**********************************************************************************************
#*=========================== Progres Bar Class <BEGIN> ======================================*
#**********************************************************************************************

class ProgressBar(object):
    DEFAULT = 'Progress: %(bar)s %(percent)3d%%'
    FULL = '%(bar)s %(current)d/%(total)d (%(percent)3d%%) %(remaining)d to go'

    def __init__(self, total, width=40, fmt=DEFAULT, symbol='=',
                 output=sys.stderr):
        assert len(symbol) == 1

        self.total = total
        self.width = width
        self.symbol = symbol
        self.output = output
        self.fmt = re.sub(r'(?P<name>%\(.+?\))d',
            r'\g<name>%dd' % len(str(total)), fmt)

        self.current = 0

    def __call__(self):
        percent = self.current / float(self.total)
        size = int(self.width * percent)
        remaining = self.total - self.current
        bar = '[' + self.symbol * size + ' ' * (self.width - size) + ']'

        args = {
            'total': self.total,
            'bar': bar,
            'current': self.current,
            'percent': percent * 100,
            'remaining': remaining
        }
        print('\r' + self.fmt % args, file=self.output, end=' ')

    def done(self):
        self.current = self.total
        self()
        print('', file=self.output)


#**********************************************************************************************
#*=========================== Progres Bar Class <END> ========================================*
#**********************************************************************************************

#**********************************************************************************************
#*=============================== Progres Bar <BEGIN> ========================================*
#**********************************************************************************************
        
def ProgressBar_Just_Percentage(Total, Progress, BarLength=20, ProgressIcon="#", BarIcon="-"):
    try:
        # You can't have a progress bar with zero or negative length.
        if BarLength <1:
            BarLength = 20
        # Use status variable for going to the next line after progress completion.
        Status = ""
        # Calcuting progress between 0 and 1 for percentage.
        Progress = float(Progress) / float(Total)
        # Doing this conditions at final progressing.
        if Progress >= 1.:
            Progress = 1
            Status = "\r\n"    # Going to the next line
        # Calculating how many places should be filled
        Block = int(round(BarLength * Progress))
        # Show this
        Bar = "[{}] {:.0f}% {}".format(ProgressIcon * Block + BarIcon * (BarLength - Block), round(Progress * 100, 0), Status)
        return Bar
    except:
        return "ERROR"

def ShowBar(Bar):
    sys.stdout.write(Bar)
    sys.stdout.flush()

#**********************************************************************************************
#*=============================== Progres Bar <END> ==========================================*
#**********************************************************************************************


def Clean_History():

    today = datetime.date.today()
    Days_Ago1 = datetime.timedelta(days=60) # <------ 30 day history !!!!
    Days_Ago2 = datetime.timedelta(days=30) # <------ 30 day history !!!!
    From_Date = today - Days_Ago1
    To_Date   = today - Days_Ago2
    print ("******************************************************************************")
    print ("*            Self Cleaning Procedure for the past 30 days                    *")
    print ("From Day:    %d"%From_Date.day)
    print ("Fron Month:  %d"%From_Date.month)
    print ("From Year:   %d"%From_Date.year)
    print ("-------------------------------------")
    print ("To Day:      %d"%To_Date.day)
    print ("To Month:    %d"%To_Date.month)
    print ("To Year:     %d"%To_Date.year)
    print ("******************************************************************************")
    file_sumary.write("******************************************************************************")
    file_sumary.write("*            Self Cleaning Procedure for the past 30 days                    *")
    file_sumary.write("From Day:   %d"%From_Date.day)
    file_sumary.write("Fron Month: %d"%From_Date.month)
    file_sumary.write("From Year:  %d"%From_Date.year)
    file_sumary.write("-------------------------------------")
    file_sumary.write("To Day:     %d"%To_Date.day)
    file_sumary.write("To Month:   %d"%To_Date.month)
    file_sumary.write("To Year:    %d"%To_Date.year)
    file_sumary.write("******************************************************************************")
    if Is_ODBC_Available:
        day_increments = 1
        #today = datetime.date.today()
        while (day_increments <= 30):                                       # <------ How many days to support history 
            one_day_increments = datetime.timedelta(days=day_increments)    # <------ 1 day increments !!!!
            delete_date = To_Date - one_day_increments
            if db.Connect() and db2.Connect():
                #print ("Success")
                
                print ("================== TRACEROUTE CLEAN UP ====================================")
                sql = "SELECT * FROM TRACEROUTE WHERE month = %d AND day = %d AND year = %d" % (delete_date.month,delete_date.day,delete_date.year)
                #print (sql)
                if (db.Execute(sql)):
                    print ("No of TRACEROUTE Rows:"+str(len(db.results)))
                    sql = "DELETE FROM TRACEROUTE WHERE month = %d AND day = %d AND year = %d" % (delete_date.month,delete_date.day,delete_date.year)
                    #print (sql)
                    if (db.Add_Move_Change_Data(sql)):
                        print ("Success Deleting ALL TRACEROUTE Records!!") 
                    else:
                        print ("***** Failure Deleting TRACEROUTE BULK Records, switchin to one by one!!")
                        i = 0
                        results = db.results
                        progress = ProgressBar(len(results), fmt=ProgressBar.FULL)
                        while (i < len(results)):
                            #progressBar = "\rProgress: " + ProgressBar(len(results), i, 20, '|', '.')
                            progress.current += 1
                            #print (results[i][0])
                            primary_key = results[i][0].strip()
                            sql = "DELETE FROM TRACEROUTE WHERE Device_IP_Date_Time_Hop_No = '%s'" % (primary_key)
                            #print (sql)
                            if (db.Add_Move_Change_Data(sql)):
                                #ShowBar(progressBar)
                                progress()
                                #print ("Success Deleting TRACEROUTE individual Record!! [%d/%d] "%(i,len(results))) 
                            else:
                                print ("***** Failure Deleting TRACEROUTE indvidual Records!!")
                            i = i + 1
                        progress.done()
                else:
                    print ("Record not Found")
                    
                print ("================== ICMP CLEAN UP ====================================")
                sql = "SELECT * FROM ICMP WHERE month = %d AND day = %d AND year = %d" % (delete_date.month,delete_date.day,delete_date.year)
                #print (sql)
                if (db.Execute(sql)):
                    print ("No of ICMP Rows:"+str(len(db.results)))
                    sql = "DELETE FROM ICMP WHERE month = %d AND day = %d AND year = %d" % (delete_date.month,delete_date.day,delete_date.year)
                    #print (sql)
                    if (db.Add_Move_Change_Data(sql)):
                        print ("Success Deleting ALL ICMP Records!!") 
                    else:
                        print ("***** Failure Deleting ICMP BULK Records switchin to one by one!!")
                        i = 0
                        results = db.results
                        progress = ProgressBar(len(results), fmt=ProgressBar.FULL)
                        while (i < len(results)):
                            #print (results[i][0]) #PK
                            #print (results[i][1]) #IP
                            #print (results[i][4]) #Day
                            #print (results[i][5]) #mon
                            #print (results[i][6]) #yea
                            #print (results[i][0])
                            progress.current += 1
                            primary_key = results[i][0].strip()
                            IP = results[i][1].strip()
                            Day = results[i][4]
                            Month = results[i][5]
                            Year = results[i][6]
                            sql = "delete FROM ICMP WHERE Device_IP_Date_Time_Size_of_Ping = '%s'" % (primary_key)
                            #sql = "DELETE FROM ICMP WHERE Device_IP = '%s' AND Day = %d AND Month = %d AND Year = %d" % (IP,Day,Month,Year)
                            ######sql = "delete FROM ICMP WHERE Device_IP = '%s' AND Day = %d AND Month = %d AND Year = %d" % (IP,Day,Month,Year)
                            #print (sql)
                            #if (db.Execute(sql)):                    
                            if (db.Add_Move_Change_Data(sql)):
                                progress()
                                #print ("Success Deleting ICMP individual Records!! [%d/%d] "%(i,len(results)))
                            else:
                                print ("********** Failure Deleting ICMP individual Record **********")
                            i = i + 1
                else:
                    print ("Record not Found")                 
                db.Disconnect()
                db2.Disconnect()
            else:
                file_sumary.write("==== NOT ABLE TO CONNECT to the DATABASE =============\r\n")
            day_increments = day_increments + 1
        print ("================== END OF THE CLEAN UP ====================================")
    
def Proccess_File_Traceroute():
    try:
        file = open(report_file_name,'r')
    except:
        file = open(report_file_name,'w')
        file.close()
        file = open(report_file_name,'r')
    no_of_lines = 0
    row = []
    ttl = 0
    none = 0
    normal = 0
    time_out = 0
    traceroute = []
    hop_no = 0
    total_no_of_hosts = 0
    total_min_response_time = 1000
    total_max_response_time = 0
    total_avg_response_time_upper_imit = 0
    total_avg_response_time_lower_imit = 1000
    
    for line in file:
        if (len(line.rstrip()) > 0):
             row.insert(no_of_lines,line.rstrip())
             no_of_lines = no_of_lines + 1
    print ("Total Number of lines to be processed => " + str(no_of_lines))
    file.close()
    i = 0
    while (i < no_of_lines):
        #print ("----------------------> processing ["+str(i+1)+"/"+str(no_of_lines)+"]")
        if (row[i].find("Tracing route to",0) != -1):
            #print (row[i])
            host = "0.0.0.0"
            host_in_trace = "0.0.0.0"
            hop_sequence = "0"
            next_hop = "0.0.0.0"
            total_no_of_hosts += 1 
            if (row[i-1].find("Hostname:",0) != -1):
                host = row[i-1][10:] # <------- Host in File
                #print ("Analizing Host:. ["+host+"]")
            if ((row[i].find("[",0) != -1) and (row[i].find("]",0) != -1)):
                pos1 = row[i].find("[",0)
                pos1 = pos1 + 1
                pos2 = row[i].find("]",0)
                pos2 = pos2 - 1
                host_in_trace = row[i][pos1:pos2] # <------- Host in the response trace route
            else:
                if ((row[i].find("Tracing route to",0) != -1) and (row[i].find("over",0) != -1)):
                    pos1 = row[i].find("Tracing route to",0)
                    pos1 = pos1 + 17
                    pos2 = row[i].find("over",0)
                    pos2 = pos2 - 1
                    host_in_trace = row[i][pos1:pos2] # <------- Host in the response trace route
            #print ("Processing Host: ["+host_in_trace+"]")
            end_trace_search = 1
            #ping_response = "Not Found"
            i = i + 1
            j = i
            hop_no = 0
            while ((j < no_of_lines) and (end_trace_search == 1)):
                if ((row[j].find(" ms ",0) != -1) or (row[j].find("*",0) != -1)):
                    #print ("-> " + row[j])
                    hop_no = hop_no + 1
                    pos1 = row[j].find(str(hop_no),0)
                    pos1 = pos1
                    if ((row[j].find(" ms ",0) != -1)):
                        pos2 = row[j].find("ms",0)
                        pos2 = pos2 -1
                    if ((row[j].find("*",0) != -1)):
                        pos2 = row[j].find("*",0)
                        pos2 = pos2
                    hop_sequence = row[j][(pos1):pos1+len(str(hop_no))]
                    #print ("Hop No:["+str(hop_no)+"]:.......["+hop_sequence+"]")
                    hop_line = row[j].split(" ")
                    #print (hop_line)
                    # looking for the min, max and avg times
                    k = 0
                    minimum_respose_time = "" # <---------- Min
                    maximum_respose_time = "" # <---------- Max
                    average_respose_time = "" # <---------- Avg
                    while (k < len(hop_line)):
                        if (hop_line[k] == "ms"):
                            if (minimum_respose_time == ""):
                                minimum_respose_time = hop_line[k-1]
                            else:
                                if (maximum_respose_time == ""):
                                    maximum_respose_time = hop_line[k-1]
                                else:
                                    if (average_respose_time == ""):
                                        average_respose_time = hop_line[k-1]
                        if (hop_line[k] == "*"):                   
                            if (minimum_respose_time == ""):
                                minimum_respose_time = hop_line[k]
                            else:
                                if (maximum_respose_time == ""):
                                    maximum_respose_time = hop_line[k]
                                else:
                                    if (average_respose_time == ""):
                                        average_respose_time = hop_line[k]
                        # --- Case:      *     10.184.48.2  reports: Destination host unreachable
                        if (hop_line[k].find(".",0) != -1):                  
                            if (minimum_respose_time == ""):
                                minimum_respose_time = "*"
                            else:
                                if (maximum_respose_time == ""):
                                    maximum_respose_time = "*"
                                else:
                                    if (average_respose_time == ""):
                                        average_respose_time = "*"                                        
                        k = k + 1
                    next_hop1 = hop_line[len(hop_line)-1].replace("[","")
                    next_hop = next_hop1.replace("]","")
                    #---------------------------- Database Entry per Host Hop -----------------------------
                    if ( minimum_respose_time != "*" or maximum_respose_time != "*" or average_respose_time != "*"):
                        #print (minimum_respose_time)
                        if (minimum_respose_time[0] == "<"):
                            temp = minimum_respose_time[1:]
                            minimum_respose_time = temp
                            print (int(minimum_respose_time))
                            
                        if (maximum_respose_time[0] == "<"):
                            temp = maximum_respose_time[1:]
                            maximum_respose_time = temp
                            print (int(maximum_respose_time))
                            
                        if (average_respose_time[0] == "<"):
                            temp = average_respose_time[1:]
                            average_respose_time = temp
                            print (int(average_respose_time))
                            
                        print ("Analized Host:...........["+host+"]")
                        print ("Processed Host:..........["+host_in_trace+"]")
                        print ("Hop No:..................["+str(hop_no)+"]")
                        print ("NEXT HOP:................[" +next_hop+"]")
                        print ("Response Time in ms Min: ["+minimum_respose_time+"] Max: ["+maximum_respose_time+"] Avg: ["+average_respose_time+"]")
                        print ("-----------------------------------------------------------------------")
                        if Is_ODBC_Available:
                            if db.Connect():
                                print ("Success")
                                pk = host_in_trace + "-" + date_str + "-" + time_str + "-" + str(hop_no)
                                sql = "INSERT INTO TRACEROUTE(Device_IP_Date_Time_Hop_No,Device_IP,Date_String,Time_String,Hop_No, \
                                       Day,Month,Year,Hour,Minute,Second,Next_Hop,Response_Time_Max,Response_Time_Min, \
                                       Response_Time_Avg,Executed_by_UserID) \
                                       VALUES ('%s','%s','%s','%s','%d','%d','%d','%d','%d','%d','%d','%s','%s','%s','%s', \
                                                '%s')" % \
                                           (pk,host_in_trace,date_str,time_str,hop_no,day,month,year,hour,minute,second, \
                                            next_hop,maximum_respose_time,minimum_respose_time,average_respose_time,Username)
                                if (db.Add_Move_Change_Data(sql)):
                                    print ("Record Added it....!!!")
                                else:
                                    print ("Error adding the record, posible dupliated it")
                                db.Disconnect()
                        if (maximum_respose_time != "*"):
                            if (int(maximum_respose_time) > (total_max_response_time)):
                                total_max_response_time = int(maximum_respose_time)
                        if (minimum_respose_time != "*"):
                            if (int(minimum_respose_time) < total_min_response_time):
                                total_min_response_time = int(minimum_respose_time)
                        if (average_respose_time != "*"):
                            if (int(average_respose_time) < total_avg_response_time_lower_imit):
                                total_avg_response_time_lower_imit = int(average_respose_time)
                            if (int(average_respose_time) > total_avg_response_time_upper_imit):
                                total_avg_response_time_upper_imit = int(average_respose_time)
                else:
                    if((row[j].find("[END]",0) != -1) or (row[j].find("[BEGIN]",0) != -1) or (row[j].find("Hostname:",0) != -1) or
                       (row[j].find("Tracing route to",0) != -1)):
                        end_trace_search = 0
                        j = j - 1
                j = j + 1
            i = j - 1
        else:
            i = i + 1
    #---------------------------------- Database Entry for Summary ------------------------------------        
    if Is_ODBC_Available:
        if db.Connect():
            print ("Success")
            pk = date_str + "-" + time_str
            sql = "INSERT INTO TRACEROUTE_SUMMARY(Date_Time,Date_String,Time_String, \
                    Total_No_Of_Traceroute,Day,Month,Year,Hour,Minute,Second, \
                    Total_Max_Response_Time, Total_Min_Response_Time, \
                    Total_Avg_Response_Time_lower_limit,Total_Avg_Response_Time_Upper_limit,\
                    Executed_by_UserID) \
                    VALUES ('%s','%s','%s','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%s')"  %  \
                        (pk,date_str,time_str,total_no_of_hosts,day,month,year,hour,minute,second, \
                        total_max_response_time,total_min_response_time,total_avg_response_time_lower_imit, \
                        total_avg_response_time_upper_imit,Username)
            if (db.Add_Move_Change_Data(sql)):
                print ("Record Added it....!!!")
            else:
                print ("Error adding the record, posible dupliated it")
                file_sumary.write("== Error adding the record, posible dupliated it ==\r\n")
            db.Disconnect()
        else:
            file_sumary.write("==== NOT ABLE TO CONNECT to the DATABASE =============\r\n")
    file_sumary.write("==================================\r\n")
    file_sumary.write("[Date]: "+date_str+"\r\n")
    file_sumary.write("[Time]: "+time_str+"\r\n")
    file_sumary.write("Total Numbre of Traceroutes:.........["+str(total_no_of_hosts)+"]\r\n")
    file_sumary.write("Maximum Response Time in ms:.........["+str(total_max_response_time)+"]\r\n")
    file_sumary.write("Minimum Response Time in ms:.........["+str(total_min_response_time)+"]\r\n")
    file_sumary.write("Lowest Average Response Time in ms:..["+str(total_avg_response_time_lower_imit)+"]\r\n")
    file_sumary.write("Maximum Average Response Time in ms:.["+str(total_avg_response_time_upper_imit)+"]\r\n")
    file_sumary.write("==================================\r\n")
    print ("==================================\r\n")
    print ("[Date]: "+date_str)
    print ("[Time]: "+time_str)
    print ("Total Numbre of Traceroutes:.........["+str(total_no_of_hosts)+"]")
    print ("Maximum Response Time in ms:.........["+str(total_max_response_time)+"]")
    print ("Minimum Response Time in ms:.........["+str(total_min_response_time)+"]")
    print ("Lowest Average Response Time in ms:..["+str(total_avg_response_time_lower_imit)+"]")
    print ("Maximum Average Response Time in ms:.["+str(total_avg_response_time_upper_imit)+"]")
    print ("==================================\r\n")
    print ("End of trace route process")
    
def Proccess_File_Ping():
    try:
        file = open(report_file_name,'r')
    except:
        file = open(report_file_name,'w')
        file.close()
        file = open(report_file_name,'r')
    no_of_lines = 0
    row = []
    ttl = 0
    none = 0
    normal = 0
    time_out = 0
    percentage_0 = 0
    percentage_25 = 0
    percentage_50 = 0
    percentage_75 = 0
    percentage_100 = 0
    total_no_of_pings = 0
    
    for line in file:
        if (len(line.rstrip()) > 0):
             row.insert(no_of_lines,line.rstrip())
             no_of_lines = no_of_lines + 1
    print ("Total Number of lines to be processed => " + str(no_of_lines))
    file.close()
    i = 0
    while (i < no_of_lines):
        #print ("----------------------> processing ["+str(i+1)+"/"+str(no_of_lines)+"]")
        if (row[i].find("Pinging",0) != -1):
            #print (row[i])
            total_no_of_pings += 1
            host = "0.0.0.0"
            size_of_ping = "0"
            host_in_ping = "0.0.0.0"
            if (row[i-1].find("Hostname:",0) != -1):
                host = row[i-1][10:] # <------- Host in File
                #print ("Analizing Host: "+host)
            if ((row[i].find("with",0) != -1) and (row[i].find("bytes",0) != -1)):
                pos1 = row[i].find("with",0)
                pos1 = pos1 + 5
                pos2 = row[i].find("bytes",0)
                pos2 = pos2 - 1
                if ((row[i].find("[",0) != -1) and (row[i].find("]",0) != -1)):
                    pos3 = row[i].find("[",0)
                    pos3 = pos3 + 1
                    pos4 = row[i].find("]",0)
                    pos4 = pos4 - 1
                else:
                    pos3 = 8
                    pos4 = pos1 - 6
                size_of_ping = row[i][pos1:pos2] # <------- Size of the Ping
                host_in_ping = row[i][pos3:pos4] # <------- Host in the response ping
                #print ("Processing Host: ["+host_in_ping+"] with Package zise of: ["+size_of_ping+"] bytes")
            end_ping_search = 1
            j = i
            while ((j < no_of_lines) and (end_ping_search == 1)):
                if ((row[j].find("Packets: Sent",0) != -1) and (row[j].find("loss",0) != -1)):
                    pos1 = row[j].find("(",0)
                    pos1 = pos1 + 1
                    pos2 = row[j].find("%",0)
                    pos2 = pos2
                    percentage_loss = row[j][pos1:pos2]
                    #print ("The Percentage loss was:["+percentage_loss+"]%")
                    end_ping_search = 0
                    minimum_respose_time = "" # <---------- Min
                    maximum_respose_time = "" # <---------- Max
                    average_respose_time = "" # <---------- Avg
                    if ((row[i+1].find("time=",0) != -1) or (row[i+1].find("time<",0) != -1)):
                        ping_response = "Normal"
                    else:
                        if (row[i+1].find("Request timed out.",0) != -1):
                             ping_response = "Time out"
                        else:
                            if (row[i+1].find("TTL expired in transit",0) != -1):
                                 ping_response = "TTL expired"
                            else:
                                ping_response = "None"
                    #ping_response = row[i+1]  # <---------- Ping Response Replay, Time out or TTL
                    if ((percentage_loss != "100") and ((j + 2) < no_of_lines)):
                        j = j + 1
                        if (row[j].find("Approximate round trip times in milli-seconds:",0) != -1):
                            j = j + 1
                            #print (row[j])
                            if ((row[j].find("Minimum =",0) != -1) and (row[j].find("Average =",0) != -1)):
                                pos1 = row[j].find("Minimum =",0)
                                pos1 = pos1 + 10
                                pos2 = row[j].find(", Maximum =",0)
                                pos2 = pos2 - 2
                                minimum_respose_time = row[j][pos1:pos2]

                                pos1 = row[j].find("Maximum =",0)
                                pos1 = pos1 + 10
                                pos2 = row[j].find(", Average =",0)
                                pos2 = pos2 - 2
                                maximum_respose_time = row[j][pos1:pos2]
                                
                                pos1 = row[j].find("Average =",0)
                                pos1 = pos1 + 10
                                average_respose_time = row[j][pos1:-2]
                    #print ("Min ["+minimum_respose_time+"] Max ["+maximum_respose_time+"] Avg ["+average_respose_time+"]")
                else:
                    if((row[j].find("[END]",0) != -1) or (row[j].find("[BEGIN]",0) != -1) or (row[j].find("Hostname:",0) != -1)):
                        #print (row[j])
                        ping_response = "Not Found"
                        end_ping_search = 0
                        j = j - 1
                j = j + 1
            i = j - 1
            #---------------------------- Database Entry per Host -----------------------------
            if (ping_response != "Not Found"):
                if Is_ODBC_Available:
                    if db.Connect():
                        print ("Success")
                        if (minimum_respose_time == ""):
                            minimum_respose_time = "0"
                        if (maximum_respose_time == ""):
                            maximum_respose_time = "0"
                        if (average_respose_time == ""):
                            average_respose_time = "0"
                        pk = host_in_ping + "-" + date_str + "-" + time_str + "-" +size_of_ping
                        sql = "INSERT INTO ICMP(Device_IP_Date_Time_Size_of_Ping,Device_IP,Date_String, \
                            Time_String,Day,Month,Year,Hour,Minute,Second,Size_of_Ping,Percentage_Loss, \
                            Response_Time_Max,Response_Time_Min,Response_Time_Avg,Response_Status,Executed_by_UserID) \
                                VALUES ('%s','%s','%s','%s','%d','%d','%d','%d','%d','%d','%s','%d','%d','%d','%d', \
                                        '%s','%s')" % \
                                   (pk,host_in_ping,date_str,time_str,day,month,year,hour,minute,second,size_of_ping, \
                                     int(percentage_loss),int(maximum_respose_time),int(minimum_respose_time),int(average_respose_time), \
                                    ping_response,Username)
                        if (db.Add_Move_Change_Data(sql)):
                            print ("Record Added it....!!!")
                            ##################
                            if (size_of_ping == '64'):
                                sql = """
                                        SELECT * FROM Devices
                                        WHERE IP4_Address = '%s'
                                       """ % (host_in_ping)                
                                if (db.Execute(sql)):
                                    sql = "UPDATE Devices SET Last_Success_ICMP = '%s', Last_ICMP_Status = '%s' \
                                            WHERE IP4_Address  = '%s'" %(( date_str + " @ " + time_str ),(ping_response+" ( "+percentage_loss+" % Loss )"),host_in_ping)
                                    if (db.Add_Move_Change_Data(sql)):
                                        print ("Record Updated ....!!!")
                                    else:
                                        print ("Record NOT Updated it....!!!")
                            #################
                        else:
                            print ("Error adding the record, posible dupliated it")
                        db.Disconnect()                
                if (ping_response == "TTL expired"):
                    ttl = ttl + 1
                if (ping_response == "None"):
                    none = none + 1
                if (ping_response == "Normal"):
                    normal = normal + 1
                if (ping_response == "Time out"):
                    time_out = time_out + 1
                print ("---------------------------------------------------------")
                print ("Analized Host:...........["+host+"]")
                print ("Processed Host:..........["+host_in_ping+"]")
                print ("Package Size in byte.....["+size_of_ping+"]")
                print ("The Percentage loss was:.["+percentage_loss+"]%")
                print ("Response Time in ms Min: ["+minimum_respose_time+"] Max: ["+maximum_respose_time+"] Avg: ["+average_respose_time+"]")
                print ("Ping Response..........: ["+ping_response+"]")
                if ((int(percentage_loss) >= 0) and (int(percentage_loss) < 25)):
                    percentage_0 = percentage_0 + 1
                if ((int(percentage_loss) >= 25) and (int(percentage_loss) < 50)):
                    percentage_25 = percentage_25 + 1
                if ((int(percentage_loss) >= 50) and (int(percentage_loss) < 75)): 
                    percentage_50 = percentage_50 + 1
                if ((int(percentage_loss) >= 75) and (int(percentage_loss) < 10)):
                    percentage_75 = percentage_75 + 1
                if ((int(percentage_loss) >= 100)):
                    percentage_100 = percentage_100 + 1
        else:
            i = i + 1
    #---------------------------------- Database Entry for Summary ------------------------------------        
    if Is_ODBC_Available:
        if db.Connect():
            print ("Success")
            pk = date_str + "-" + time_str
            sql = "INSERT INTO ICMP_SUMMARY(Date_Time,Date_String,Time_String,Day,Month,Year,Hour,Minute, \
                    Second,Tota_no_of_Pings,Normal_Pings,Time_Out_Pings,TTL_Expired_Pings,None_Pings, \
                    Percentage_Loss_0,Percentage_Loss_25,Percentage_Loss_50,Percentage_Loss_75, \
                    Percentage_Loss_100,Executed_by_UserID) \
                    VALUES ('%s','%s','%s','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d','%d' \
                           ,'%d','%d','%d','%d','%s')" % \
                       (pk,date_str,time_str,day,month,year,hour,minute,second,total_no_of_pings, \
                        normal,time_out,ttl,none,percentage_0,percentage_25,percentage_50,percentage_75, \
                        percentage_100,Username)
            if (db.Add_Move_Change_Data(sql)):
                print ("Record Added it....!!!")
            else:
                print ("Error adding the record, posible dupliated it")
            db.Disconnect()
        else:
            file_sumary.write("=======  NO DATABASE AVAILABLE ===========\r\n")

    file_sumary.write("==================================\r\n")
    file_sumary.write("[Date]: "+date_str+"\r\n")
    file_sumary.write("[Time]: "+time_str+"\r\n")
    file_sumary.write("Normal Pings:..........["+str(normal)+"]\r\n")
    file_sumary.write("Time Out Pings:........["+str(time_out)+"]\r\n")
    file_sumary.write("TTL Expired Pings:.....["+str(ttl)+"]\r\n")
    file_sumary.write("None Pings:............["+str(none)+"]\r\n")
    file_sumary.write("------------------------------------\r\n")
    file_sumary.write("Total No Pings:............["+str(total_no_of_pings)+"]\r\n")
    file_sumary.write("------------ Lost % ----------------\r\n")
    file_sumary.write("> 0%   Lost:...........["+str(percentage_0)+"]\r\n")
    file_sumary.write("> 25%  Lost:...........["+str(percentage_25)+"]\r\n")
    file_sumary.write("> 50%  Lost:...........["+str(percentage_50)+"]\r\n")
    file_sumary.write("> 75%  Lost:...........["+str(percentage_75)+"]\r\n")
    file_sumary.write("> 100% Lost:...........["+str(percentage_100)+"]\r\n")
    file_sumary.write("==================================\r\n")
    print ("==================================")
    print ("Normal Pings:..........["+str(normal)+"]")
    print ("Time Out Pings:........["+str(time_out)+"]")
    print ("TTL Expired Pings:.....["+str(ttl)+"]")
    print ("None Pings:............["+str(none)+"]")
    print ("--------- Lost per % -------------\r\n")
    print ("> 0%   Lost:...........["+str(percentage_0)+"]\r\n")
    print ("> 25%  Lost:...........["+str(percentage_25)+"]\r\n")
    print ("> 50%  Lost:...........["+str(percentage_50)+"]\r\n")
    print ("> 75%  Lost:...........["+str(percentage_75)+"]\r\n")
    print ("> 100% Lost:...........["+str(percentage_100)+"]\r\n")
    print ("==================================")
    print ("End of ping process")

def run_win_cmd(cmd):
    result = []
    global file_new
    process = subprocess.Popen(cmd,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    for line in process.stdout:
        result.append(line)
        print(line)
    errcode = process.returncode
    for line in result:
        #print(line)
        file_new.write(line.decode('utf-8'))
    if errcode is not None:
        raise Exception('cmd %s failed, see above for details', cmd)
        file_new.write('cmd %s failed, see above for details', cmd)
        
def Timestamp():
    global file_new
    
    #print ("Current date and time using str method of datetime object:")
    #print (str(now))
    #print ("Current date and time using instance attributes:")
    #print ("Current year: %d" % year)
    #print ("Current month: %d" % month)
    #print ("Current day: %d" % day)
    #print ("Current hour: %d" % hour)
    #print ("Current minute: %d" % minute)
    #print ("Current second: %d" % second)
    #print ("Current microsecond: %d" % now.microsecond)
    #print ("Current date and time using strftime:")
    #print (now.strftime("%Y-%m-%d %H:%M"))
    #print ("Current date and time using isoformat:")
    #print (now.isoformat())
    file_new.write("+--------------------------------------------+\r\n")
    file_new.write("[Date]: "+date_str+"\r\n")
    file_new.write("[Time]: "+time_str+"\r\n")
    file_new.write("+--------------------------------------------+\r\n")


def Get_IP_Address():
    print ("Gettig IP Addresses........")
    if Is_ODBC_Available:
        if db.Connect():
            #print ("Success")                
            print ("================== Getting IP Addresse from Devices Table ====================================")
            sql = "SELECT * FROM DEVICES WHERE Status <> '%s'" % ('obsolete')
            print (sql)
            if (db.Execute(sql)):
                print ("No of Devices:"+str(len(db.results)))
                file = open(ip_addresses_file_name,'w')
                file.close()
                i = 0
                results = db.results
                progress = ProgressBar(len(results), fmt=ProgressBar.FULL)
                while (i < len(results)):
                    #progressBar = "\rProgress: " + ProgressBar(len(results), i, 20, '|', '.')
                    progress.current += 1
                    #print (results[i][7])
                    if ((results[i][7] != None) and (results[i][7] != "0.0.0.0") and (results[i][7].find(".") > 0)):
                        if ((results[i][39] == None) or (results[i][39] == "YES")):
                            Device_IP = results[i][7].strip()
                            file = open(ip_addresses_file_name,'a')
                            file.write(Device_IP+'\r\n')
                            file.close()
                    #ShowBar(progressBar)
                    progress()
                    i = i + 1
                progress.done()
            else:
                 print ("Record not Found")
            db.Disconnect()
        else:
            file_sumary.write("==== NOT ABLE TO CONNECT to the DATABASE =============\r\n")
    
def Main():
    global file_new
    #print ("HELLO........")
    file = open(ip_addresses_file_name,'r')
    file_new = open(report_file_name,"w")
    Timestamp()
    ips = []
    no_of_ips = 0
    for line in file:
        if (len(line.rstrip()) > 1):
            ips.insert(no_of_ips,line.rstrip())
            no_of_ips = no_of_ips + 1
    print ("Total Number of IP address to be processed => " + str(no_of_ips))
    file.close()
    i = 0
    while (i < no_of_ips):
        print ("-----------------------------------------------> processing ["+str(i+1)+"/"+str(no_of_ips)+"]")
        print ("Pinging....64.......[ "+ips[i]+" ]")
        file_new.write("[BEGIN PING]\r\n")
        file_new.write("Hostname: "+ips[i])
        run_win_cmd('ping '+ ips[i] + " -l 64 -w 2")
        file_new.write("[END PING]\r\n")
        print ("Pinging....1470.....[ "+ ips[i] +" ]")
        file_new.write("[BEGIN PING]\r\n")
        file_new.write("Hostname: "+ips[i])
        run_win_cmd('ping '+ ips[i] + " -l 1470 -w 2")
        file_new.write("[END PING]\r\n")
        print ("Traceroute..........[ "+ ips[i] +" ]")
        file_new.write("[BEGIN TRACEROUTE]\r\n")
        file_new.write("Hostname: "+ips[i])
        run_win_cmd('tracert -h 15 -w 2 '+ ips[i])
        file_new.write("[END TRACEROUTE]\r\n")
        i = i + 1
        file_new.close()
        file_new = open(report_file_name,"a")
    file_new.close()

if __name__ == "__main__":

    ODBC_DSN_mame = "BV"
    if Is_ODBC_Available:
        db = ODBC(ODBC_DSN_mame)
        db2 = ODBC(ODBC_DSN_mame)
    else:
        db = "NONE"
    forever = 1

    # ---------------------- To test read report files <BEGIN> ---------
    '''
    forever = -1
    now = datetime.datetime.now()
    day = now.day
    month = now.month
    year = now.year
    hour = now.hour
    minute = now.minute
    second = now.second
    date_str_start = (str(month)+"-"+str(day)+"-"+str(year))
    time_str_start = (str(hour)+"-"+str(minute)+"-"+str(second))
    date_str = (str(month)+"-"+str(day)+"-"+str(year))
    time_str = (str(hour)+":"+str(minute)+":"+str(second))
    report_file_name = "report.txt" # <--- can use any name !
    file_sumary = open("report_sumary_"+date_str_start+"_"+time_str_start+"_start.txt","w")
    Proccess_File_Ping()
    Proccess_File_Traceroute()
    '''
    # ---------------------- To test read report files <END> ---------
    
    while (forever > 0):    
        ip_addresses_file_name = "ips.txt"
        report_file_name = "report.txt"
        count = 1
        now = datetime.datetime.now()
        day = now.day
        month = now.month
        year = now.year
        hour = now.hour
        minute = now.minute
        second = now.second
        date_str_start = (str(month)+"-"+str(day)+"-"+str(year))
        time_str_start = (str(hour)+"-"+str(minute)+"-"+str(second))
        file_sumary = open("report_sumary_"+date_str_start+"_"+time_str_start+"_start.txt","w")
        while count <= 10:
            print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>: "+str(count))
            Clean_History()
            Get_IP_Address()
            count = count + 1    
            now = datetime.datetime.now()
            day = now.day
            month = now.month
            year = now.year
            hour = now.hour
            minute = now.minute
            second = now.second
            date_str = (str(month)+"-"+str(day)+"-"+str(year))
            time_str = (str(hour)+":"+str(minute)+":"+str(second))
            Main()
            Proccess_File_Ping()
            Proccess_File_Traceroute()
            file_sumary.close()
            file_sumary = open("report_sumary_"+date_str_start+"_"+time_str_start+"_start.txt","a")               
            print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>: Sleep for 10 sec,")
            sleep(10)
        file_sumary.close()
    print ("Done")



