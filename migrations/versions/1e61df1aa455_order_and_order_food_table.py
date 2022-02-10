"""order and order_food table

Revision ID: 1e61df1aa455
Revises: e03c2c075619
Create Date: 2022-02-02 23:21:29.317183

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e61df1aa455'
down_revision = 'e03c2c075619'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('order',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=25), nullable=True),
    sa.Column('phone_number', sa.String(length=10), nullable=True),
    sa.Column('address', sa.String(length=512), nullable=True),
    sa.Column('start_order', sa.DateTime(), nullable=True),
    sa.Column('delivery_datetime', sa.DateTime(), nullable=True),
    sa.Column('payment_method', sa.String(length=20), nullable=True),
    sa.Column('total_price', sa.Integer(), nullable=True),
    sa.Column('persons', sa.Integer(), nullable=True),
    sa.Column('order_notes', sa.String(length=256), nullable=True),
    sa.Column('end_order', sa.DateTime(), nullable=True),
    sa.Column('order_status', sa.String(length=25), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_delivery_datetime'), 'order', ['delivery_datetime'], unique=False)
    op.create_index(op.f('ix_order_end_order'), 'order', ['end_order'], unique=False)
    op.create_index(op.f('ix_order_phone_number'), 'order', ['phone_number'], unique=False)
    op.create_index(op.f('ix_order_start_order'), 'order', ['start_order'], unique=False)
    op.create_table('User_Food',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('food_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['food_id'], ['food.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'food_id')
    )
    op.create_table('order__food',
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('food_id', sa.Integer(), nullable=False),
    sa.Column('food_quantity', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['food_id'], ['food.id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.PrimaryKeyConstraint('order_id', 'food_id')
    )
    op.drop_table('user_food')
    op.create_unique_constraint(None, 'food', ['slug'])
    op.create_unique_constraint(None, 'menu_category', ['slug'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'menu_category', type_='unique')
    op.drop_constraint(None, 'food', type_='unique')
    op.drop_index(op.f('ix_order_start_order'), table_name='order')
    op.drop_index(op.f('ix_order_phone_number'), table_name='order')
    op.drop_index(op.f('ix_order_end_order'), table_name='order')
    op.drop_index(op.f('ix_order_delivery_datetime'), table_name='order')
    op.drop_table('order')
    # ### end Alembic commands ###
