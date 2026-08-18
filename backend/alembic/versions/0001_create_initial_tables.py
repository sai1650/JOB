"""create initial tables

Revision ID: 0001_create_initial_tables
Revises: 
Create Date: 2026-08-15
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_create_initial_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'candidates',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('resume_filename', sa.String(length=512), nullable=True),
        sa.Column('resume_text', sa.Text(), nullable=True),
        sa.Column('extracted_skills', sa.JSON(), nullable=True),
        sa.Column('extracted_technologies', sa.JSON(), nullable=True),
        sa.Column('extracted_domains', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    op.create_table(
        'interview_sessions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('candidate_id', sa.String(length=36), nullable=False),
        sa.Column('selected_role', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('current_question_index', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'interview_questions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('session_id', sa.String(length=36), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('question_type', sa.String(length=50), nullable=True),
        sa.Column('difficulty', sa.String(length=50), nullable=True),
        sa.Column('topic', sa.String(length=255), nullable=True),
        sa.Column('retrieved_context', sa.JSON(), nullable=True),
        sa.Column('source_reference', sa.String(length=512), nullable=True),
        sa.Column('generation_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    op.create_table(
        'interview_answers',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('question_id', sa.String(length=36), nullable=False),
        sa.Column('session_id', sa.String(length=36), nullable=False),
        sa.Column('answer_text', sa.Text(), nullable=True),
        sa.Column('evaluation_score', sa.Float(), nullable=True),
        sa.Column('evaluation_feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    op.create_table(
        'interview_reports',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('session_id', sa.String(length=36), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('strengths', sa.JSON(), nullable=True),
        sa.Column('weaknesses', sa.JSON(), nullable=True),
        sa.Column('topic_scores', sa.JSON(), nullable=True),
        sa.Column('recommendation', sa.Text(), nullable=True),
        sa.Column('generated_at', sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('interview_reports')
    op.drop_table('interview_answers')
    op.drop_table('interview_questions')
    op.drop_table('interview_sessions')
    op.drop_table('candidates')
