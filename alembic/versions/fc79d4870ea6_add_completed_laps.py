"""add completed laps

Revision ID: fc79d4870ea6
Revises: f9a4e3411ca9
Create Date: 2022-08-03 18:22:31.391668

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc79d4870ea6'
down_revision = 'f9a4e3411ca9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('driver_race_summary', sa.Column('laps_completed', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('driver_race_summary', 'laps_completed')
    # ### end Alembic commands ###
