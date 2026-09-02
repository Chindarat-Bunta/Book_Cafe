try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    try:
        import MySQLdb
    except ImportError:
        pass

# Django 6+ requires MySQL 8.4+ by default.
# Patch minimum_database_version to support local MySQL 8.0 (e.g. 8.0.17 from AppServ/XAMPP).
try:
    from django.db.backends.mysql.features import DatabaseFeatures
    DatabaseFeatures.minimum_database_version = property(lambda self: (8, 0))
except Exception:
    pass
