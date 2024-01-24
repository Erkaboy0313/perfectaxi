async def chat_room_serializer(room):
    data = {
        "room":room.name
    }
    return data

async def messages_serializer(messages):
    messages_list = []
    async for message in messages:
        data = await message_serializer(message)
        messages_list.append(data)
    return messages_list

async def message_serializer(message):
    data = {
        "author":message.author.id,
        "message":message.message,
        "time":message.time.strftime('%d-%m-%Y %H:%M')
    }
    return data