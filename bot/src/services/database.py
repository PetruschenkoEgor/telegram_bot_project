from bot.src.config.settings import db_manager


async def create_table_users(table_name="users_reg"):
    async with db_manager as client:
        await client.create_table(
            table_name=table_name,
            columns=[
                "user_id INT8 PRIMARY KEY",
                "full_name VARCHAR(255)",
                "user_login VARCHAR(255)",
                "refer_id INT8",
                "count_refer INT4 DEFAULT 0",
                "date_reg TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            ],
        )
