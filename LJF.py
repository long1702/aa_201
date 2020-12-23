import pandas as pd
import numpy as np
from queue import Queue, PriorityQueue
SEMESTER_WEEKS = 15
INTERN_WEEKS = 4
START_INTERN_WEEK = SEMESTER_WEEKS // 2


class Subject:
    def __init__(self, name="Empty", module_num=0, credit=0, max_module_per_week=0, max_periods_per_module=0):
        self.name = name
        self.module_num = module_num
        self.credit = credit
        self.max_module_per_week = max_module_per_week
        self.max_periods_per_module = max_periods_per_module
        self.module_left = module_num
        self.is_finished = False

    def reduce_module_left(self):
        if self.is_finished:
            return
        self.module_left -= 1
        if self.module_left < 0:
            self.is_finished = True


class WeeklyTimeTable:
    def __init__(self, subjects=[], time_list=np.array([])):
        pre_week_time_table = np.array([])
        for day in time_list:
            day_array = np.array([])
            for period in day[1:]:
                if period == 0:
                    day_array = np.append(day_array, Subject())
                else:
                    day_array = np.append(day_array, subjects[period-1])
            pre_week_time_table = np.append(pre_week_time_table, day_array)
        if time_list.size != 0:
            self.week_time_table = np.reshape(pre_week_time_table, (12, 7))
        else:
            self.week_time_table = time_list

    def reduce_module_left_subject(self):
        for day in self.week_time_table:
            for period in day:
                if period.name == "Empty":
                    continue
                elif not period.is_finished:
                    period.reduce_module_left()
                    if period.is_finished:
                        period = Subject()
                    

class SemesterTimeTable:
    def __init__(self, weekly_time_table=WeeklyTimeTable(), is_intern=False):
        pre_semester_time_table = np.array([])
        if is_intern:
            for i in range(START_INTERN_WEEK):
                weekly_time_table.reduce_module_left_subject()
                pre_semester_time_table = np.append(pre_semester_time_table, weekly_time_table.week_time_table)
                

            for i in range(INTERN_WEEKS):
                pre_semester_time_table = np.append(pre_semester_time_table,  np.repeat([Subject("Intern")], 12 * 7))

            for i in range(SEMESTER_WEEKS - START_INTERN_WEEK - INTERN_WEEKS):
                weekly_time_table.reduce_module_left_subject()
                pre_semester_time_table = np.append(pre_semester_time_table,  weekly_time_table.week_time_table)
                

        else:
            for i in range(SEMESTER_WEEKS):
                weekly_time_table.reduce_module_left_subject()
                pre_semester_time_table = np.append(pre_semester_time_table,  weekly_time_table.week_time_table)
                
        # ExtraWeek
        weekly_time_table.reduce_module_left_subject()
        pre_semester_time_table = np.append(pre_semester_time_table, weekly_time_table.week_time_table)
        self.semester_time_table =  np.reshape(pre_semester_time_table, (16, 7, 12))

    def get_distinct_subject_in_day(self, day_time_table):
        subjects = []
        for subject in day_time_table:
            if (subject.name != "Empty") and (subject.name not in subjects):
                subjects.append(subject.name)
        return subjects

    def self_check(self):
        subjects =  []
        subjects_name = []
        for day in self.semester_time_table[15]:
            for period in day:
                if (period.module_left > 0) and (period.name not in subjects_name):
                    subjects.append(period)
                    subjects_name.append(period.name)
        return subjects

    def self_schedule(self):
        for i in range(SEMESTER_WEEKS - START_INTERN_WEEK - INTERN_WEEKS):
            
            return

class GroupClass:
    def __init__(self, group_name="", is_intern=False, weekly_time_table_path=""):
        self.group_name = group_name
        self.is_intern = is_intern
        self.subjects = self.subject_from_csv()
        self.weekly_time_table = WeeklyTimeTable(self.subjects, np.array(pd.DataFrame(pd.read_csv(weekly_time_table_path).to_numpy())))
        self.semester_time_table = SemesterTimeTable(self.weekly_time_table, self.is_intern)
        self.subject_queue = self.add_queue_subject()

    def subject_from_csv(self, path="./subject_requirements.csv"):
        subject_df = pd.DataFrame(pd.read_csv(path))
        subjects = []
        for i in range(subject_df.shape[0]):
            subject = subject_df.iloc[i]
            subjects.append(
                Subject(subject['Subject'], subject['Num_of_modules'], subject['Credits'],
                        subject['Max_modules_per_week'],
                        subject['Periods_per_module']))
        return subjects

    def add_queue_subject(self):
        pq = PriorityQueue(maxsize=0)
        subjects = self.semester_time_table.self_check()
        for subject in subjects:
            pq.put((subject.max_periods_per_module, subject.credit, subject))
        return pq

def schedule(group_classes):
    standard_class = None
    for classes in group_classes:
        if classes.subject_queue.empty():
            return


class_list = np.array(pd.DataFrame(pd.read_csv("./intern.csv", header=None)).to_numpy())
group_classes = []
for groupclass in class_list:
    group_classes.append(GroupClass("group_"+str(groupclass[0]), groupclass[1], "./group_"+str(groupclass[0])+".csv"))

