"""Added bio and profile_picture to User model

Revision ID: 095ff9ed5d6e
Revises: 
Create Date: 2024-04-15 22:28:31.654747

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = '095ff9ed5d6e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
       with op.batch_alter_table('user', schema=None) as batch_op:
              inspector = inspect(op.get_bind())
              columns = [column['name'] for column in inspector.get_columns('user')]
              if 'bio' not in columns:
                     batch_op.add_column(sa.Column('bio', sa.String(length=500), nullable=True))
              if 'profile_picture' not in columns:
                     batch_op.add_column(sa.Column('profile_picture', sa.String(length=500), nullable=True))

              batch_op.alter_column('username',
                                   existing_type=sa.VARCHAR(length=80),
                                   type_=sa.String(length=100),
                                   existing_nullable=False)
              batch_op.alter_column('password',
                                   existing_type=sa.VARCHAR(length=120),
                                   type_=sa.String(length=200),
                                   existing_nullable=False)

def downgrade():
       with op.batch_alter_table('user', schema=None) as batch_op:
              batch_op.alter_column('password',
                                   existing_type=sa.String(length=200),
                                   type_=sa.VARCHAR(length=120),
                                   existing_nullable=False)
              batch_op.alter_column('username',
                                   existing_type=sa.String(length=100),
                                   type_=sa.VARCHAR(length=80),
                                   existing_nullable=False)
              batch_op.drop_column('profile_picture')
              batch_op.drop_column('bio')