# -*- coding: utf-8 -*-
"""Project models."""
import datetime as dt

from crn_designer.database import Column, Model, SurrogatePK, db, reference_col, relationship

class Project(SurrogatePK, Model):
    """A project, owned by a user."""

    __tablename__ = 'projects'
    name = Column(db.String(80), unique=False, nullable=False)
    description = Column(db.Text, unique=False, nullable=True)
    public = Column(db.Boolean)

    user_id = reference_col('users', nullable=True)
    user = relationship('User', backref='projects')

    specifications = relationship('Specification', backref='project')

    def __init__(self, name, description, public, **kwargs):
        """Create instance."""
        db.Model.__init__(self, name=name, description=description, public=public, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Project({name}, {id})>'.format(name=self.name, id=self.id)
