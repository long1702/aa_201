import pandas as pd
import numpy as np

SEMESTER_WEEKS = 15
INTERN_WEEKS = 4


class Subject:
    def __init__(self, name="Empty", module_num=0, credit=0, max_module_per_week=0, max_periods_per_module=0):
        self.name = name
        self.module_num = module_num
        self.credit = credit
        self.max_module_per_week = max_module_per_week
        self.max_periods_per_module = max_periods_per_module
        self.module_left = module_num


class GroupClass:
    def __init__(self, group_name="", is_intern=False):
        self.group_name = group_name
        self.is_intern = is_intern
        self.subjects = self.subject_from_csv()

    @staticmethod
    def subject_from_csv(path="./subject_requirements.csv"):
        subject_df = pd.DataFrame(pd.read_csv(path))
        subjects = []
        for i in range(subject_df.shape[0]):
            subject = subject_df.iloc[i]
            subjects.append(
                Subject(subject['Subject'], subject['Num_of_modules'], subject['Credits'],
                        subject['Max_modules_per_week'],
                        subject['Periods_per_module']))
        return subjects


class WeeklyTimeTable:
    def __init__(self, group_class=GroupClass(), time_list=np.array([])):
        self.group_class = group_class
        pre_week_time_table = np.array([])
        for day in time_list:
            day_array = np.array([])
            for period in day[1:]:
                if period == 0:
                    day_array = np.append(day_array, Subject())
                else:
                    day_array = np.append(day_array, self.group_class.subjects[period-1])
            pre_week_time_table = np.append(pre_week_time_table, day_array)

        self.week_time_table = np.reshape(pre_week_time_table, (12, 7))


class SemesterTimeTable:
    def __init__(self, group_class=GroupClass(), week_time_table=np.array([])):
        self.sem_week = SEMESTER_WEEKS
        self.group_class = group_class
        self.weekly_time_table = WeeklyTimeTable(group_class, week_time_table)
        pre_semester_time_table = np.array([])
        if self.group_class.is_intern:
            for i in range(self.sem_week // 2):
                pre_semester_time_table = np.append(pre_semester_time_table, self.weekly_time_table.week_time_table)

            for i in range(INTERN_WEEKS):
                pre_semester_time_table = np.append(pre_semester_time_table, np.repeat([0], 12 * 7))

            for i in range(self.sem_week - self.sem_week // 2 - INTERN_WEEKS):
                pre_semester_time_table = np.append(pre_semester_time_table, self.weekly_time_table.week_time_table)
        else:
            for i in range(self.sem_week):
                pre_semester_time_table = np.append(pre_semester_time_table, self.weekly_time_table.week_time_table)
        self.semester_time_table = np.reshape(pre_semester_time_table, (12, 7, -1))


class_list = np.array(pd.DataFrame(pd.read_csv("./intern.csv")).to_numpy())
for groupclass in class_list:
    gclass = GroupClass("group_"+groupclass[0], groupclass[1])
    weekly_time_table = np.array(pd.DataFrame(pd.read_csv("./group_"+groupclass[0]+".csv")).to_numpy())
    semesterTimeTable = SemesterTimeTable(gclass, weekly_time_table)


