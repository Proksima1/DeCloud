from faststream.rabbit import RabbitQueue

process_image_queue = RabbitQueue(
    name="decloud_process_image",
    durable=True,
    auto_delete=False,
)
