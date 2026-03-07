"""
Migración: catálogos Opción B
- Crea: provinces, sectors, amenities, property_amenities
- Modifica: properties (province_id FK, sector_id FK, drop province/sector strings)
- Crea índices de búsqueda
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_catalogs_option_b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:

    # ── 1. provinces ───────────────────────────────────────────────────
    op.create_table(
        "provinces",
        sa.Column("id",   sa.Integer(),     primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100),   nullable=False, unique=True),
        sa.Column("code", sa.String(10),    nullable=False, unique=True),
    )

    # ── 2. sectors ─────────────────────────────────────────────────────
    op.create_table(
        "sectors",
        sa.Column("id",          sa.Integer(),   primary_key=True, autoincrement=True),
        sa.Column("name",        sa.String(100), nullable=False),
        sa.Column("province_id", sa.Integer(),   sa.ForeignKey("provinces.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("name", "province_id", name="uq_sector_name_province"),
    )
    op.create_index("idx_sectors_province_id", "sectors", ["province_id"])

    # ── 3. amenities ───────────────────────────────────────────────────
    op.create_table(
        "amenities",
        sa.Column("id",       sa.Integer(),    primary_key=True, autoincrement=True),
        sa.Column("name",     sa.String(100),  nullable=False, unique=True),
        sa.Column("slug",     sa.String(100),  nullable=False, unique=True),
        sa.Column("category", sa.Enum(
            "security", "recreation", "services", "exterior",
            name="amenity_category"
        ), nullable=False),
        sa.Column("icon",     sa.String(50),   nullable=True),
    )

    # ── 4. property_amenities ──────────────────────────────────────────
    op.create_table(
        "property_amenities",
        sa.Column("property_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("properties.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("amenity_id",  sa.Integer(),
                  sa.ForeignKey("amenities.id",  ondelete="CASCADE"), primary_key=True),
    )

    # ── 5. Agregar columnas FK a properties ────────────────────────────
    op.add_column("properties", sa.Column("province_id", sa.Integer(), nullable=True))
    op.add_column("properties", sa.Column("sector_id",   sa.Integer(), nullable=True))

    # ── 6. Migrar datos existentes (province string → province_id) ─────
    op.execute("""
        UPDATE properties p
        SET province_id = pv.id
        FROM provinces pv
        WHERE LOWER(TRIM(p.province)) = LOWER(TRIM(pv.name))
    """)

    # ── 7. Eliminar filas sin province_id (datos no migrables) ─────────
    op.execute("DELETE FROM favorites WHERE property_id IN (SELECT id FROM properties WHERE province_id IS NULL)")
    op.execute("DELETE FROM property_images WHERE property_id IN (SELECT id FROM properties WHERE province_id IS NULL)")
    op.execute("DELETE FROM properties WHERE province_id IS NULL")

    # ── 8. Hacer province_id NOT NULL después de migrar ────────────────
    op.alter_column("properties", "province_id", nullable=False)

    # ── 9. Crear FK constraints ────────────────────────────────────────
    op.create_foreign_key("fk_properties_province", "properties", "provinces", ["province_id"], ["id"])
    op.create_foreign_key("fk_properties_sector",   "properties", "sectors",   ["sector_id"],   ["id"])

    # ── 10. Eliminar columnas string antiguas ──────────────────────────
    op.drop_column("properties", "province")
    op.drop_column("properties", "sector")

    # ── 11. Índices de búsqueda ────────────────────────────────────────
    # Los que existían en el SQL inicial se recrean solo si no existen
    op.create_index("idx_properties_province_id",    "properties", ["province_id"], if_not_exists=True)
    op.create_index("idx_properties_sector_id",      "properties", ["sector_id"],   if_not_exists=True)
    op.create_index("idx_properties_operation_type", "properties", ["operation_type"], if_not_exists=True)
    op.create_index("idx_properties_property_type",  "properties", ["property_type"],  if_not_exists=True)
    op.create_index("idx_properties_price",          "properties", ["price"],   if_not_exists=True)
    op.create_index("idx_properties_status",         "properties", ["status"],  if_not_exists=True)


def downgrade() -> None:
    # Restaurar columnas string
    op.add_column("properties", sa.Column("province", sa.String(100), nullable=True))
    op.add_column("properties", sa.Column("sector",   sa.String(100), nullable=True))

    # Recuperar datos
    op.execute("""
        UPDATE properties p
        SET province = pv.name
        FROM provinces pv
        WHERE p.province_id = pv.id
    """)

    # Eliminar FK y columnas nuevas
    op.drop_constraint("fk_properties_province", "properties", type_="foreignkey")
    op.drop_constraint("fk_properties_sector",   "properties", type_="foreignkey")
    op.drop_column("properties", "province_id")
    op.drop_column("properties", "sector_id")

    # Eliminar índices
    op.drop_index("idx_properties_province_id")
    op.drop_index("idx_properties_sector_id")
    op.drop_index("idx_properties_operation_type")
    op.drop_index("idx_properties_property_type")
    op.drop_index("idx_properties_price")
    op.drop_index("idx_properties_status")

    # Eliminar tablas catálogo
    op.drop_table("property_amenities")
    op.drop_table("amenities")
    op.drop_table("sectors")
    op.drop_table("provinces")
    op.execute("DROP TYPE IF EXISTS amenity_category")
