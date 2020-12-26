import pandas as pd
import numpy as np
from queue import PriorityQueue

SEMESTER_WEEKS = 15
INTERN_WEEKS = 4
START_INTERN_WEEK = SEMESTER_WEEKS // 2
MODULE_PER_WEEK = 1


class Subject:
    def __init__(self, name="Empty", module_num=0, credit=0, max_module_per_week=0, max_periods_per_module=0):
        self.name = name
        self.module_num = module_num
        self.credit = credit
        self.max_module_per_week = max_module_per_week
        self.max_periods_per_module = max_periods_per_module
        self.module_left = module_num
        self.current_module_per_week = MODULE_PER_WEEK
        self.is_finished = False

    def reduce_module_left(self):
        if self.is_finished:
            return
        self.module_left -= 1
        if self.module_left < 0:
            self.is_finished = True


class WeeklyTimeTable:
    def __init__(self, subjects=(), time_list=np.array([])):
        pre_week_time_table = [None] * 7
        for i, day in enumerate(time_list):
            day_array = [None] * 12
            for j, period in enumerate(day[1:]):
                if period == 0:
                    day_array[j] = Subject()
                else:
                    day_array[j] = Subject(subjects[period - 1].name, subjects[period - 1].module_num,
                                           subjects[period - 1].credit, subjects[period - 1].max_module_per_week,
                                           subjects[period - 1].max_periods_per_module)
            pre_week_time_table[i] = day_array
        if time_list.size != 0:
            self.week_time_table = np.array(pre_week_time_table)
        else:
            self.week_time_table = time_list

    def reduce_module_left_subject(self):
        for row, day in enumerate(self.week_time_table):
            for col, period in enumerate(day):
                if period.name == "Empty":
                    continue
                elif not period.is_finished:
                    period.reduce_module_left()
                    if period.is_finished:
                        self.week_time_table[row][col] = Subject()


def get_distinct_subject_in_day(day_time_table):
    subjects = []
    for subject in day_time_table:
        if (subject.name != "Empty") and (subject.name not in subjects):
            subjects.append(subject.name)
    return subjects


class SemesterTimeTable:
    def __init__(self, weekly_time_table=WeeklyTimeTable(), is_intern=False):
        pre_semester_time_table = [None] * (SEMESTER_WEEKS + 1)
        if is_intern:
            for i in range(START_INTERN_WEEK):
                weekly_time_table.reduce_module_left_subject()
                pre_semester_time_table[i] = weekly_time_table.week_time_table

            for i in range(INTERN_WEEKS):
                pre_semester_time_table[i + START_INTERN_WEEK] = np.reshape(np.repeat(Subject("Intern"), 12 * 7), (7, 12))

            for i in range(SEMESTER_WEEKS - START_INTERN_WEEK - INTERN_WEEKS):
                weekly_time_table.reduce_module_left_subject()
                pre_semester_time_table[i + INTERN_WEEKS + START_INTERN_WEEK] = weekly_time_table.week_time_table

        else:
            for i in range(SEMESTER_WEEKS):
                weekly_time_table.reduce_module_left_subject()
                pre_semester_time_table[i] = weekly_time_table.week_time_table

        # ExtraWeek
        weekly_time_table.reduce_module_left_subject()
        pre_semester_time_table[SEMESTER_WEEKS] = weekly_time_table.week_time_table
        self.semester_time_table = np.array(pre_semester_time_table)

    def self_check(self):
        subjects = []
        subjects_name = []
        for day in self.semester_time_table[15]:
            for period in day:
                if (period.module_left > 0) and (period.name not in subjects_name):
                    subjects.append(period)
                    subjects_name.append(period.name)
        return subjects


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


class GroupClass:
    def __init__(self, group_name="", is_intern=False, weekly_time_table_path=""):
        self.group_name = group_name
        self.is_intern = is_intern
        self.subjects = subject_from_csv()
        self.weekly_time_table = WeeklyTimeTable(self.subjects,
                                                 np.array(pd.DataFrame(pd.read_csv(weekly_time_table_path).to_numpy())))
        self.semester_time_table = SemesterTimeTable(self.weekly_time_table, self.is_intern)
        self.subject_queue = self.add_queue_subject()

    def add_queue_subject(self):
        pq = PriorityQueue(maxsize=0)
        subjects = self.semester_time_table.self_check()
        for subject in subjects:
            pq.put((-subject.max_periods_per_module, -subject.credit, -subject.name, subject))
        return pq

    def set_subject(self, week, day, period, subject):
        self.semester_time_table.semester_time_table[week][day][period] = subject


def get_others_class_subject(classes, group_class, week, day, period):
    subject_name = []
    for cl in group_class:
        if cl.group_name == classes.group_name:
            continue
        subject_name.append(cl.semester_time_table.semester_time_table[week][day][period].name)
    return subject_name


def schedule(group_class):
    for classes in group_class:
        for week, classes_week in enumerate(
                classes.semester_time_table.semester_time_table[START_INTERN_WEEK + INTERN_WEEKS:],
                START_INTERN_WEEK + INTERN_WEEKS):
            while not classes.subject_queue.empty():
                subject = classes.subject_queue.get()
                for day, classes_day in enumerate(classes_week, 0):
                    is_noon_period = False
                    has_7th_period = False
                    if classes_day[6].name != "Empty":
                        has_7th_period = True
                    today_class_subject = [x.name for x in classes_day]
                    for period, classes_period in enumerate(classes_day, 0):
                        if subject[3].name in today_class_subject:
                            break
                        if is_noon_period:
                            continue
                        if classes_period.name != "Empty":
                            if period == 5:
                                is_noon_period = True
                            continue
                        else:
                            others_class_subject = get_others_class_subject(classes, group_class, week, day, period)
                            if subject[3].name in others_class_subject:
                                break

                            available = True
                            for i in range(subject[3].max_periods_per_module):
                                if classes_day[period + i].name != "Empty":
                                    available = False
                                    break

                            if not available:
                                break
                            elif has_7th_period and (period + subject[3].max_periods_per_module - 1 >= 5):
                                break
                            elif period == 5 and subject[3].max_periods_per_module > 1:
                                break
                            else:
                                subject[3].current_module_per_week += 1
                                subject[3].reduce_module_left()
                                for i in range(subject[3].max_periods_per_module):
                                    classes.set_subject(week, day, period + i, subject[3])
                                break

                    if subject[3].current_module_per_week >= subject[3].max_module_per_week:
                        subject[3].current_module_per_week = MODULE_PER_WEEK
                        break
            classes.subject_queue = classes.add_queue_subject()


if __name__ == "__main__":
    class_list = np.array(pd.DataFrame(pd.read_csv("./intern_5.csv", header=None)).to_numpy())
    group_classes = []
    for groupclass in class_list:
        group_classes.append(
            GroupClass("group_" + str(groupclass[0]), groupclass[1], "./group_" + str(groupclass[0]) + ".csv"))

    schedule(group_classes)
    for cl in group_classes:
        print("{}".format(cl.group_name))
        for i, class_week in enumerate(
                cl.semester_time_table.semester_time_table):
            print("Week {}".format(i))
            for j, class_day in enumerate(class_week):
                print("Day {}".format(j))
                for k, class_period in enumerate(class_day):
                    if class_period.name != "Empty":
                        print("Period {}, Subject {}".format(k, class_period.name))
        break
