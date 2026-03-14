from django.db import migrations


def drop_legacy_supplier_column(apps, schema_editor):
    table_name = 'products_product'
    connection = schema_editor.connection

    with connection.cursor() as cursor:
        columns = [col.name for col in connection.introspection.get_table_description(cursor, table_name)]
        if 'supplier_id' not in columns:
            return

        if connection.vendor == 'mysql':
            cursor.execute(
                """
                SELECT CONSTRAINT_NAME
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = %s
                  AND COLUMN_NAME = 'supplier_id'
                  AND REFERENCED_TABLE_NAME IS NOT NULL
                """,
                [table_name],
            )
            for row in cursor.fetchall():
                cursor.execute(f"ALTER TABLE {table_name} DROP FOREIGN KEY {row[0]}")
            cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN supplier_id")
        elif connection.vendor == 'sqlite':
            # SQLite can fail dropping this legacy column when historical indexes
            # still reference it. Keep migration idempotent for local dev.
            return


def noop_reverse(apps, schema_editor):
    # No reverse migration for legacy cleanup column.
    return


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_category_metadata_activitylog'),
    ]

    operations = [
        migrations.RunPython(drop_legacy_supplier_column, reverse_code=noop_reverse),
    ]
