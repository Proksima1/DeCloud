import asyncio

from backend_context.containers.api_container import ApiContainer
from backend_context.presentation.app import create_app
from base.presentation import runner
from base.presentation.rest import uvicorn


async def main() -> None:
    api_container = await ApiContainer.build_from_settings()
    main_app = await create_app(container=api_container)

    await runner.run(uvicorn.run(main_app))


if __name__ == "__main__":
    asyncio.run(main())
