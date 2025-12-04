"""Initial database schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2023-11-02 21:55:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create sports table
    op.create_table('sports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sports_id'), 'sports', ['id'], unique=False)
    op.create_index(op.f('ix_sports_name'), 'sports', ['name'], unique=True)

    # Create sportsbooks table
    op.create_table('sportsbooks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('base_url', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.String(length=10), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sportsbooks_id'), 'sportsbooks', ['id'], unique=False)
    op.create_index(op.f('ix_sportsbooks_name'), 'sportsbooks', ['name'], unique=True)

    # Create betting_markets table
    op.create_table('betting_markets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sport_id', sa.Integer(), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('game_name', sa.String(length=255), nullable=False),
        sa.Column('away_team', sa.String(length=100), nullable=False),
        sa.Column('home_team', sa.String(length=100), nullable=False),
        sa.Column('game_start_time', sa.DateTime(), nullable=False),
        sa.Column('timezone', sa.String(length=50), nullable=True),
        sa.Column('season', sa.String(length=50), nullable=True),
        sa.Column('league', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['sport_id'], ['sports.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_betting_markets_id'), 'betting_markets', ['id'], unique=False)
    op.create_index(op.f('ix_betting_markets_sport_id'), 'betting_markets', ['sport_id'], unique=False)
    op.create_index(op.f('ix_betting_markets_external_id'), 'betting_markets', ['external_id'], unique=False)
    op.create_index(op.f('ix_betting_markets_away_team'), 'betting_markets', ['away_team'], unique=False)
    op.create_index(op.f('ix_betting_markets_home_team'), 'betting_markets', ['home_team'], unique=False)
    op.create_index(op.f('ix_betting_markets_game_start_time'), 'betting_markets', ['game_start_time'], unique=False)
    op.create_index(op.f('ix_betting_markets_created_at'), 'betting_markets', ['created_at'], unique=False)
    
    # Composite indexes
    op.create_index('idx_market_sport_teams', 'betting_markets', ['sport_id', 'away_team', 'home_team'], unique=False)
    op.create_index('idx_market_time_sport', 'betting_markets', ['game_start_time', 'sport_id'], unique=False)
    
    # Unique constraint for market uniqueness
    op.create_unique_constraint('uq_unique_market', 'betting_markets', ['sport_id', 'away_team', 'home_team', 'game_start_time'])

    # Create market_snapshots table
    op.create_table('market_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('market_id', sa.Integer(), nullable=False),
        sa.Column('sportsbook_id', sa.Integer(), nullable=False),
        sa.Column('away_moneyline', sa.String(length=20), nullable=True),
        sa.Column('home_moneyline', sa.String(length=20), nullable=True),
        sa.Column('away_spread', sa.Float(), nullable=True),
        sa.Column('away_spread_price', sa.String(length=20), nullable=True),
        sa.Column('home_spread', sa.Float(), nullable=True),
        sa.Column('home_spread_price', sa.String(length=20), nullable=True),
        sa.Column('total_points', sa.Float(), nullable=True),
        sa.Column('over_price', sa.String(length=20), nullable=True),
        sa.Column('under_price', sa.String(length=20), nullable=True),
        sa.Column('additional_markets', sa.Text(), nullable=True),
        sa.Column('snapshot_time', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['market_id'], ['betting_markets.id'], ),
        sa.ForeignKeyConstraint(['sportsbook_id'], ['sportsbooks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_market_snapshots_id'), 'market_snapshots', ['id'], unique=False)
    op.create_index(op.f('ix_market_snapshots_market_id'), 'market_snapshots', ['market_id'], unique=False)
    op.create_index(op.f('ix_market_snapshots_sportsbook_id'), 'market_snapshots', ['sportsbook_id'], unique=False)
    op.create_index(op.f('ix_market_snapshots_snapshot_time'), 'market_snapshots', ['snapshot_time'], unique=False)
    
    # Composite indexes for performance
    op.create_index('idx_snapshot_market_time', 'market_snapshots', ['market_id', 'snapshot_time'], unique=False)
    op.create_index('idx_snapshot_sportsbook_time', 'market_snapshots', ['sportsbook_id', 'snapshot_time'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_snapshot_sportsbook_time', table_name='market_snapshots')
    op.drop_index('idx_snapshot_market_time', table_name='market_snapshots')
    op.drop_index(op.f('ix_market_snapshots_snapshot_time'), table_name='market_snapshots')
    op.drop_index(op.f('ix_market_snapshots_sportsbook_id'), table_name='market_snapshots')
    op.drop_index(op.f('ix_market_snapshots_market_id'), table_name='market_snapshots')
    op.drop_index(op.f('ix_market_snapshots_id'), table_name='market_snapshots')
    op.drop_table('market_snapshots')
    
    op.drop_constraint('uq_unique_market', 'betting_markets', type_='unique')
    op.drop_index('idx_market_time_sport', table_name='betting_markets')
    op.drop_index('idx_market_sport_teams', table_name='betting_markets')
    op.drop_index(op.f('ix_betting_markets_created_at'), table_name='betting_markets')
    op.drop_index(op.f('ix_betting_markets_game_start_time'), table_name='betting_markets')
    op.drop_index(op.f('ix_betting_markets_home_team'), table_name='betting_markets')
    op.drop_index(op.f('ix_betting_markets_away_team'), table_name='betting_markets')
    op.drop_index(op.f('ix_betting_markets_external_id'), table_name='betting_markets')
    op.drop_index(op.f('ix_betting_markets_sport_id'), table_name='betting_markets')
    op.drop_index(op.f('ix_betting_markets_id'), table_name='betting_markets')
    op.drop_table('betting_markets')
    
    op.drop_index(op.f('ix_sportsbooks_name'), table_name='sportsbooks')
    op.drop_index(op.f('ix_sportsbooks_id'), table_name='sportsbooks')
    op.drop_table('sportsbooks')
    
    op.drop_index(op.f('ix_sports_name'), table_name='sports')
    op.drop_index(op.f('ix_sports_id'), table_name='sports')
    op.drop_table('sports')