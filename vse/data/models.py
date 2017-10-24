# -*- coding: utf-8 -*-
"""Data models."""

from vse.database import Column, Model, SurrogatePK, db, reference_col, relationship

class Data(SurrogatePK, Model):
    """A dataset, attached to a project."""

    __tablename__ = 'data'
    name = Column(db.String(80), unique=False, nullable=False)
    description = Column(db.Text, unique=False, nullable=True)
    data = Column(db.Text, unique=False, nullable=True)

    project_id = reference_col('projects', nullable=True)
    project = relationship('Project', backref='data')

    def __init__(self, name, description, project_id, data, **kwargs):
        """Create instance."""
        db.Model.__init__(self, name=name, description=description, project_id=project_id, data=data, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Dataset({name}, {id})>'.format(name=self.name, id=self.id)
