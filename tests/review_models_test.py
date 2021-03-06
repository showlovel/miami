import unittest
import os
os.environ['MIAMI_ENV'] = 'test'
from datetime import datetime, timedelta
import miami
from miami.models import User, Team, Task, TimeSlot, Category
from miami import db
from mockito import when, unstub


class ReviewModelsTest(unittest.TestCase):

    def setUp(self):
        when(miami.utils).now().thenReturn(datetime(2012, 11, 5, 9, 0, 0))
        miami.init_db()
        team = Team('Log')
        team.members.append(User('yachuan.chen', email='yachuan.chen@chinacache.com'))
        team.members.append(User('yue.zhang', email='yue.zhang@chinacache.com'))
        team.members.append(User('peng.yua', email='peng.yuan@chinacache.com'))
        db.session.add(team)
        db.session.add(Category('Feature'))
        db.session.add(Category('Bug'))
        db.session.add(Category('Test'))
        db.session.commit()

        task = Task('title1', 'detail', status='DONE', price=2, estimate=4, team=Team.query.get(1), start_time=miami.utils.get_last_monday().replace(hour=10), ready_time=miami.utils.get_last_monday().replace(hour=10))
        ts = TimeSlot(miami.utils.get_last_monday().replace(hour=10), 7200, User.query.get(1))
        task.time_slots.append(ts)
        task.categories.append(Category.query.get(1))
        db.session.add(task)
        db.session.commit()

        task = Task('title2', 'detail2', status='DONE', price=2, estimate=4, team=Team.query.get(1), start_time=miami.utils.get_last_monday().replace(hour=12), ready_time=miami.utils.get_last_monday().replace(hour=12))
        ts = TimeSlot(miami.utils.get_last_monday().replace(hour=12), 3600, User.query.get(1), partner=User.query.get(2))
        task.time_slots.append(ts)
        task.categories.append(Category.query.get(1))
        db.session.add(task)
        db.session.commit()

        ##unplanned
        task = Task('title3', 'detail3', status='DONE', price=2, estimate=4, team=Team.query.get(1), start_time=(miami.utils.get_last_monday() + timedelta(days=1)).replace(hour=14), ready_time=(miami.utils.get_last_monday() + timedelta(days=1)).replace(hour=14))
        ts = TimeSlot(miami.utils.get_last_monday().replace(hour=14), 3600, User.query.get(2), partner=User.query.get(1))
        task.time_slots.append(ts)
        task.categories.append(Category.query.get(2))
        db.session.add(task)
        db.session.commit()

        ###Ready###
        task = Task('title4', 'detail4', status='READY', price=2, estimate=4, team=Team.query.get(1), start_time=miami.utils.get_last_monday().replace(hour=14), ready_time=miami.utils.get_last_monday().replace(hour=14))
        ts = TimeSlot(miami.utils.get_last_monday().replace(hour=14), 3600, User.query.get(2), partner=User.query.get(1))
        task.time_slots.append(ts)
        task.categories.append(Category.query.get(1))
        db.session.add(task)
        db.session.commit()

        task = Task('title6', 'detail6', status='READY', price=1, estimate=4, team=Team.query.get(1), start_time=miami.utils.get_last_monday().replace(hour=10), ready_time=miami.utils.get_last_monday().replace(hour=10))
        db.session.add(task)
        task.categories.append(Category.query.get(3))
        db.session.commit()

        ###history###
        task = Task('title5', 'detail5', status='DONE', price=2, estimate=4, team=Team.query.get(1), start_time=(miami.utils.get_last_monday() - timedelta(days=5)).replace(hour=14), ready_time=(miami.utils.get_last_monday() - timedelta(days=5)).replace(hour=14))
        ts = TimeSlot((miami.utils.get_last_monday() - timedelta(days=5)).replace(hour=14), 3600, User.query.get(2))
        task.time_slots.append(ts)
        task.categories.append(Category.query.get(1))
        db.session.add(task)
        db.session.commit()

    def tearDown(self):
        unstub()

    def test_review_data(self):
        ##uncategories
        task = Task('title2', 'detail2', status='DONE', price=2, estimate=4, team=Team.query.get(1), start_time=miami.utils.get_last_monday().replace(hour=12), ready_time=miami.utils.get_last_monday().replace(hour=12))
        ts = TimeSlot(miami.utils.get_last_monday().replace(hour=12), 3600, User.query.get(1), partner=User.query.get(2))
        task.time_slots.append(ts)
        db.session.add(task)
        db.session.commit()

        team = Team.query.get(1)

        rd = team.review_data(miami.utils.get_last_monday())

        self.assertEquals(11, rd.price)
        self.assertEquals(8, rd.done_price)
        self.assertEquals(16, rd.estimate)
        self.assertEquals(6, rd.working_hours)
        self.assertEquals(5, rd.valuable_hours)
        self.assertEquals(4, rd.paired_time)
        self.assertEquals(1, rd.unplanneds)
        self.assertEquals("[['$1', 0], ['$2', 4], ['$5', 0], ['$10', 0]]", rd.price_ratio())
        self.assertEquals(u'[["Uncategorized", 1], ["Feature", 2], ["Bug", 1]]', rd.categories_ratio())
        self.assertEquals(u'[["Uncategorized", 2], ["Feature", 4], ["Bug", 2]]', rd.categories_price_ratio())

    def test_review_data_sorted_tasks(self):
        team = Team.query.get(1)
        rd = team.review_data(miami.utils.get_last_monday())

        tasks = rd.sorted_tasks()
         
        self.assertEquals([u'READY', u'READY', u'DONE', u'DONE', u'DONE'],[t.status for t in tasks])

    def test_personal_review_data(self):
        member = User.query.get(2)

        rd = member.review_data(miami.utils.get_last_monday(), 1)

        self.assertEquals(6, rd.price)
        self.assertEquals(4, rd.done_price)
        self.assertEquals(4, rd.estimate)
        self.assertEquals(3.0, rd.working_hours)
        self.assertEquals(2.0, rd.valuable_hours)
        self.assertEquals(3.0, rd.paired_time)

    def test_personal_review_data_nodata(self):
        member = User.query.get(3)
        rd = member.review_data(miami.utils.get_last_monday(), 1)

        self.assertEquals(0, rd.price)
        self.assertEquals(0, rd.done_price)
        self.assertEquals(0, rd.estimate)
        self.assertEquals(0, rd.working_hours)
        self.assertEquals(0, rd.valuable_hours)
        self.assertEquals(0, rd.paired_time)

    def test_personal_card(self):
        member = User.query.get(2)

        pc = member.personal_card()

        self.assertEquals(6, pc.fortune)
        self.assertEquals(4, pc.working_hours)
        self.assertEquals(3, pc.valuable_hours)
        self.assertEquals(8, pc.estimate)
        self.assertEquals(3, pc.paired_hours)
        self.assertEquals('37.50%', pc.estimate_deviation())
        self.assertEquals('75.00%',pc.paired_ratio())
