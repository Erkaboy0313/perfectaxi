from chat.models import Message,Room

async def serialize_chats(chats:list[Room]):
    return [await serialize_chat(chat) async for chat in chats]

async def serialize_chat(chat:Room):
    return {
        "name": chat.name,
        "user": chat.non_admin_user_name
    }
    
    eyJpdiI6Ik5wYmtnQjdjVURkb1NsQ0NwS2xPbUE9PSIsInZhbHVlIjoiZXBqNUpPM1BNNVhTYlFuZVhSVFh2L2pFUXJMNU8xVHBuQnVPc0p0UGErT0MrdDF5QWFka0YyOVV2c24vVUlCdG4yamxickFoQjFrb0V4VEREd0xNcFlVUzFnTGtjTkFFc3dtMVpaRmtnWUh3STZDUkQzUnQ1WWcyMU5SVkc3SEY0czQ0WlkvNVRvOGJ1R2dDKzg1cVB3SWRmOXRTWVN3bnZHSmh2K2NuUUNoaWEyU1pkNUViUW0xUjEvYmZVVTJTOTNVL1dpRnI0cXVJaEI1djl1bEF3TUM5UGFlMUc1ZmRiVmtzL1dUcTZBaUxmd01VeGNDb3h4Z2V0U3lVZmJXSmU0UHVBaURYencxRWNGRXdURVdWZ3daR1ZnS0hraDFTQ2hoNXZHYXZLRjFrVDh5MzBzQXFOQ2h0UXBXMDQ4cUN0WE82YlFzMHcxOWNaYUppN3l1NDRQdlVsd0pueGVRQUxlK0J1ejNNdnNrYnFOZjlCeC95aEZ0UGo4TEpKT3luIiwibWFjIjoiYTExZDgyOTMyYTczN2EzOTFhM2M1MmQzOTNhNzhjMjY4ODVhNzY1NDdjZDM2YmM5ZmRiZjk3Y2JhOWMwNDgwYyIsInRhZyI6IiJ9
    eyJpdiI6ImVIUkdoMUFzMHduSHZtdGt6bEx3TUE9PSIsInZhbHVlIjoiZWh1ZGRzQm1FOW9LMkkrR1N2MnZsTkpBSVcwOXhTOWNsb3NIYndSVjMxd1dmTGhMOTVXeXR4a1JKRnJmUEFqb0dlZmJZU0pWdWZhNkZxb3VERXN5RnRscUp4VnRsQ0xPTFBGcm5kbDIvbFp5TmdhdmJCK1g3OUlJNHdJQmc3MUxLM0VJWnhmdXhxQ2lwdGZRajFCcHc3TEU0SitVbEdTZTliQ1pRbFJQd3c5dVRTTkMrWkhuYzgrY3dsTEtCQ0x0bFRuUUhPK1krbWpOa0I2RHJkblUzTzhaYmNucFA3c0hkWVRMUXNMK3NLYTJEWElpU3lIUEl6NVhWYnVRNW9jU3hBK3I2N0E3ZmUwOFFPRjhOZzVzVGlDMUJWN1dzMEpSSlliYmprdTB6Znpua2d2VEdGdWN1TzhuekFyRzl2d3B0dUZodk0rYUxpbllPanN1ZUExd3pDd1NoTkVFZ3Q2dDRZN29vbXYzeWI1by9acVFXYjZIV3lpYzU4SVVnTEtXIiwibWFjIjoiYzkzODhlZjhiYTEyZDhhNmYzZDNmM2NmYTlkMzY3ZWQ0MDg5OWFjOGEwNzQ2NWE1Yjg3YTljYThlNTRlMDI1NSIsInRhZyI6IiJ9
    eyJpdiI6IjZPVjFWVUtFK2VETnR5bDZqTlZHQkE9PSIsInZhbHVlIjoieHdsWTZyMEJhM2x0MEkrUDVzTy9PQ09uTEozOEZHU1NJdnNnelR0dVUwcGV5RTY0ak1RUkZ6RTJaY3piK1hldHJMN3lhbU41bWdrc2dQTVR3MDl5TUI2SlZNVlJuZHNzM1N3cHcxaG5ERTNodXdJR3Y1cGNFUmtYSE5odWYzMkZWaWwxQlNINElQRUdKbXUwTEg1Q0NpZURGM0d3ZlI0dWZmT3Z4Z2RNSXN2c0laQmhyUkl6a01oVGlkRnMzTHpRUWhseDNOSEFrWGVjMmUyWXhERGN1K3dKRDJJK1JUbUhLVnlaU2ZDNGc4cUpSc05GT3kxbXlEb0RDQTc1d0RHZytKZ2U1WlJmZDdmQ2YzNC9nNm44d0RtQVBwajVHc3FZYmtNdkVGN3ZXS3NVVFRLMllvNXJvc2ZzdGpUMW1EZGh1Y3c3N3NBRUhiY1lMdmhmcENBa25halJrb2Z0dnd4eVJwYlFvU3ZScEZjK2h1WTdtVlBrdmp4SHN1cnVxMVBWIiwibWFjIjoiZTM0ZmY2ZmY0NzAyMzM3MzI2ZDJiNDgwNWEyZjYxOGYyYzg1Yzc2ODNhZDk2MDZlNmNlZGM2MTFiNjBkYzg1MiIsInRhZyI6IiJ9
