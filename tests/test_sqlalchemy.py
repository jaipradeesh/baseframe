# -*- coding: utf-8 -*-

import unittest
from coaster.sqlalchemy import BaseMixin
from coaster.db import SQLAlchemy
from sqlalchemy import Column, Unicode
from baseframe import __
from baseframe import baseframe
import baseframe.forms as forms
import baseframe.forms.sqlalchemy as forms_sqlachemy
from .fixtures import app1, app2


db = SQLAlchemy()


class Container(BaseMixin, db.Model):
    __tablename__ = 'container'
    name = Column(Unicode(80), nullable=True)
    title = Column(Unicode(80), nullable=True)
    content = Column(Unicode(250))


class ContainerForm(forms.Form):
    name = forms.StringField(__("Name"), validators=[forms_sqlachemy.AvailableName()])
    title = forms.StringField(__("Title"), validators=[forms_sqlachemy.AvailableAttr('title')])
    content = forms.TextAreaField(__("Content"))


class TestFormSQLAlchemy(unittest.TestCase):
    app = app1

    def setUp(self):
        baseframe.init_app(self.app, requires=['baseframe'])
        db.init_app(self.app)
        self.ctx = self.app.test_request_context()
        self.ctx.push()
        db.create_all()
        self.session = db.session
        self.form = ContainerForm(model=Container, meta={'csrf': False})

    def tearDown(self):
        self.session.rollback()
        db.drop_all()
        self.ctx.pop()

    def test_available_attr(self):
        c1 = Container()
        self.form.process(name=u'c1', title=u't1')
        self.assertTrue(self.form.validate())
        self.form.populate_obj(c1)
        db.session.add(c1)

        c2 = Container()
        self.form.process(name=u'c2', title=u't1')
        # title u't1' is repeated
        self.assertFalse(self.form.validate())
        self.form.process(name=u'c2', title=u't2')
        self.assertTrue(self.form.validate())
        self.form.populate_obj(c2)
        db.session.add(c2)

        c3 = Container()
        self.form.process(name=u'c2', title=u't3')
        # name u'c2' repeated
        self.assertFalse(self.form.validate())
        self.form.process(name=u'c3', title=u't3')
        self.form.populate_obj(c3)
        db.session.add(c3)


class TestFormSQLAlchemyPG(TestFormSQLAlchemy):
    app = app2
