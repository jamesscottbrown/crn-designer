# -*- coding: utf-8 -*-
"""Specification models."""
import datetime as dt

from vse.database import Column, Model, SurrogatePK, db, reference_col, relationship

class Specification(SurrogatePK, Model):
    """A specification, part of a project."""

    __tablename__ = 'specifications'
    name = Column(db.String(80), unique=False, nullable=False)
    description = Column(db.Text, unique=False, nullable=True)
    specification = Column(db.Text, unique=False, nullable=True)
    variable = Column(db.String(80), unique=False, nullable=True)

    project_id = reference_col('projects', nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))

    def __init__(self, name, description, specification, project_id, variable, **kwargs):
        """Create instance."""
        db.Model.__init__(self, name=name, description=description, specification=specification, variable=variable,
                          project_id=project_id, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Specification({name}, {id})>'.format(name=self.name, id=self.id)
