import asyncio

from base.presentation import runner
from neuro_api_context.containers.neuro_api_container import NeuroApiContainer
from neuro_api_context.presentation.rabbit.app import create_app


async def main() -> None:
    neuro_api_container = await NeuroApiContainer.build_from_settings()
    app = await create_app(neuro_api_container)
    await runner.run(app.run())


if __name__ == "__main__":
    asyncio.run(main())
