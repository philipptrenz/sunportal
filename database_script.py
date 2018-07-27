import sqlite3
import os.path

#File name as a string, this filename is relative
FILE_NAME = "/var/www/SunPortal/temp.v"
#Update time in seconds
UPDATE_TIME = 300
#Hour in seconds
HOUR = 300 * 12
#Database name
DB = "/var/www/SunPortal/SBFspot.db"
#Query
Query = "SELECT * FROM DayData WHERE TimeStamp >= (SELECT MAX(TimeStamp) FROM DayData);"
#Serial number to write
SN = 1

conn = sqlite3.connect(DB)

c = conn.cursor()

c.execute(Query)

lastTime = c.fetchone()

if (len(lastTime) > 0):
    print("Last known update: ")
    print(lastTime[0])
    print("Checking for file existance in: "+FILE_NAME)
    if(not os.path.exists(FILE_NAME)):
        print("File does not yet exist, writing to: " +FILE_NAME)
        try:
            fio = open(FILE_NAME, "w")
            toWrite = str(lastTime[0]) + " \n"
            fio.write(toWrite)
            fio.write(toWrite)
            fio.close()
        except IOError:
            print("File could not be opened")
    else:
        print("File does already exist, updating time...")
        try:
            fio = open(FILE_NAME, "r")
            toRead = fio.readline().rstrip()
            toReadInt = int(toRead)
            timePassed = fio.readline().rstrip()
            timePassedInt = int(timePassed)
            if (toReadInt == lastTime[0]):
                fio.close()
                if (timePassedInt > (lastTime[0] + HOUR)):
                    if (len(lastTime) > 3):
                        print("Inserting into database...")
                        column1 = timePassedInt
                        column2 = SN
                        column3 = lastTime[2]
                        column4 = 0
                        c.execute("INSERT INTO DayData (TimeStamp, Serial, TotalYield, Power) VALUES ({c1}, {c2}, {c3}, {c4})".format(c1=column1, c2=column2, c3=column3, c4=column4))
                        conn.commit()
                try:
                    fio = open(FILE_NAME, "w")
                    toWrite = timePassedInt + UPDATE_TIME
                    fio.write(str(toReadInt) + "\n")
                    fio.write(str(toWrite) + "\n")
                    fio.close()
                except IOError:
                    print("File could not be opened")
            else:
                fio.close()
                try:
                    fio = open(FILE_NAME, "w")
                    toWrite = lastTime[0]
                    fio.write(str(toWrite) + "\n")
                    fio.write(str(toWrite) + "\n")
                    fio.close()
                except IOError:
                    print("File could not be opened")
        except IOError:
            print("File could not be opened")

conn.close()
