import asyncio

import typer

from src.core.config import settings
from src.db.session import async_session_maker
from src.schemas.user import UserCreate
from src.services.user_service import UserService

app = typer.Typer(help="Создание супер пользователя")


@app.command('create-superuser')
def create_superuser(
        secret_code: str = typer.Option(..., prompt=True),
        username: str = typer.Option(..., prompt=True),
        email: str = typer.Option(..., prompt=True),
        password: str = typer.Option(..., prompt=True, hide_input=True),
):
    """Создать суперпользователя с ролью 'superuser'"""

    async def _create():
        try:
            if not secret_code or secret_code != settings.cli.secret:
                typer.echo("Вы ввели не правильный секрет при создании пользователя, попробуйте еще раз!")
                return

            async with async_session_maker() as session:
                user_service = UserService(session)

                # Проверка наличия одного суперпользователя
                superuser = await user_service.get_superuser()
                if superuser:
                    typer.echo("Суперпользователь уже существует. Разрешён только один суперпользователь.")
                    return

                # Проверка существования пользователя
                existing = await user_service.get_by_username(username)
                if existing:
                    typer.echo("Пользователь с таким username уже существует.")
                    return

                # Создание пользователя с is_superuser=True
                user_data = UserCreate(username=username, email=email, password=password)
                await user_service.create_user(user_data)
                await user_service.update_user(username, {"is_superuser": True})

                typer.echo(f"Суперпользователь {username} успешно создан.")
        except Exception as e:
            typer.echo(f"Ошибка: {e}")
            raise typer.Exit(code=1)

    asyncio.run(_create())


if __name__ == "__main__":
    app()
