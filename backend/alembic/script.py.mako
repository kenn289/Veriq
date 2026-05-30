"""Revision script template."""

from alembic import op
import sqlalchemy as sa

revision = "${up_revision}"
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    """Description: Apply schema changes for this revision.
    Parameters:
        None
    Returns:
        None
    Usage Example:
        upgrade()
    """
    pass


def downgrade() -> None:
    """Description: Revert schema changes for this revision.
    Parameters:
        None
    Returns:
        None
    Usage Example:
        downgrade()
    """
    pass
