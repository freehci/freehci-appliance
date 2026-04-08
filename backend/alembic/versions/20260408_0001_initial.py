"""Tom initial revisjon – tabeller legges til i senere migrasjoner."""

from typing import Sequence, Union

from alembic import op

revision: str = "20260408_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
