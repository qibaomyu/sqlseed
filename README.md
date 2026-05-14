# sqlseed

A declarative database seeding tool that generates realistic test data from schema definitions.

---

## Installation

```bash
pip install sqlseed
```

---

## Usage

Define your schema in a YAML file and let sqlseed handle the rest.

**`seed.yml`**
```yaml
users:
  count: 50
  fields:
    id: uuid
    name: full_name
    email: email
    created_at: datetime
```

Run the seeder against your database:

```bash
sqlseed run seed.yml --db postgresql://user:pass@localhost/mydb
```

Or use it programmatically:

```python
from sqlseed import Seeder

seeder = Seeder("seed.yml")
seeder.connect("postgresql://user:pass@localhost/mydb")
seeder.run()
```

Supported field types include `uuid`, `full_name`, `email`, `phone`, `address`, `datetime`, `integer`, `boolean`, and more.

---

## Supported Databases

- PostgreSQL
- MySQL
- SQLite

---

## License

This project is licensed under the [MIT License](LICENSE).