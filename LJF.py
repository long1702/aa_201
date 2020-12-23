import pandas as pd
import numpy as np

class WeeklyTimeTable():
    def __init__(self, group_name=None, time_list=[]):
        self.group_name = group_name
        self.week_time_table = np.array(time_list)
        
    #def from_csv(self, path):


class SemesterTimeTable():
    def __init__(self, group_name, weekly_time_table, isItern):
        self.sem_week = 15
        self.group_name = group_name
        pre_semester_time_table = np.array([])
        if isItern:
            for i in range(self.sem_week//2):
               pre_semester_time_table = np.append(pre_semester_time_table, weekly_time_table.week_time_table)
            
            for i in range(4):
                pre_semester_time_table = np.append(pre_semester_time_table, np.repeat([0],13*7))

            for i in range(self.sem_week-self.sem_week//2-4):
                pre_semester_time_table = np.append(pre_semester_time_table, weekly_time_table.week_time_table)
        else:
            for i in range(self.sem_week):
                pre_semester_time_table = np.append(pre_semester_time_table, weekly_time_table.week_time_table)
        self.semester_time_table = np.reshape(pre_semester_time_table, (13,7,-1))
   

class Subject():
    def __init__(self, name, module_num, credit, max_module_per_week, max_periods_per_module):
        self.name = name
        self.module_num = module_num
        self.credit = credit
        self.max_module_per_week = max_module_per_week
        self.max_periods_per_module = max_periods_per_module
        self.module_left = module_num 

class Group_Class():
    def __init__(self, group_name, isIntern):
        self.group_name = group_name
        self.isIntern = isIntern


subject_df = pd.DataFrame(pd.read_csv("./subject_requirements-Sheet1.csv"))
subjects = []
for i in range(subject_df.shape[0]):
    subject = subject_df.iloc[i]
    subjects.append(Subject(subject['Subject'], subject['Num_of_modules'], subject['Credits'], subject['Max_modules_per_week'], subject['Periods_per_module']))


weekly_time_table = np.array(pd.DataFrame(pd.read_csv("./group_1.csv")).to_numpy())
weeklyTimeTable = WeeklyTimeTable("group_1", weekly_time_table) 

semesterTimeTable = SemesterTimeTable("group_1", weeklyTimeTable, True)
print(semesterTimeTable.semester_time_table)