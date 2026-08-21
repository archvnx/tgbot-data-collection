from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
from database.db import add_users
from status.users_state import users_create_menu
from collections import defaultdict
from aiogram.types import InputMediaPhoto
from database.db import add_discussion
import asyncio


albums= defaultdict(list)

_router=Router()
@_router.message(CommandStart())
async def _cmd_start(_message: Message,state: FSMContext):
    await state.clear()
    user_id = _message.from_user.id
    await add_users(user_id)
    username = _message.from_user.username
    if username:
        await _message.answer(
            f"Привет, {username}!\n"                
            "Этот бот принимает абсолютно всё, что ты хочешь обсудить.\n\n"
            "✍️ /create - создать обсуждение\n\n"
            )
    else:
        await _message.answer(
            "Привет, друг!\n"
            "Этот бот принимает абсолютно всё, что ты хочешь анонимно обсудить.\n\n"
            "✍️ /create - создать обсуждение\n\n"
            )


@_router.message(Command("create"))
async def cmd_create(message: Message,state: FSMContext):
    await state.set_state(users_create_menu.text_state)
    await message.answer("Напишите, что хотите обсудить")

@_router.message(users_create_menu.text_state)
async def state_of_create_q(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(text_create=message.text)  
        await message.answer("Вы хотите добавить фото?(y/n)")
        await state.set_state(users_create_menu.photo_state_question)
    else:
        await message.answer("Напишите, что хотите обсудить")


@_router.message(users_create_menu.photo_state_question)
async def state_of_create_ph(message: Message, state: FSMContext):
    if message.text == "y":
        await message.answer("Пришлите фото")
        await state.set_state(users_create_menu.photo_state)
    elif message.text == "n":
        await state.set_state(users_create_menu.check_state)
        await state_of_create_check(message,state)
    else:
        await message.answer("Неизвестная команда")



@_router.message(users_create_menu.photo_state)
async def state_of_create_send_ph(message: Message, state: FSMContext):
    if not message.photo and message.text!="n":
        await message.answer("Пришлите фото или завершите добавление(n)")
        return
    if message.text=="n":
        await state.set_state(users_create_menu.check_state)
        await state_of_create_check(message,state)
        return
    photo=await state.get_data()
    photos=photo.get("photo_create",[])
    ph_id= message.photo[-1].file_id
    if message.media_group_id:
        albums[message.media_group_id].append(ph_id)
        await asyncio.sleep(1)
        new_photos = albums.get(message.media_group_id)
        if new_photos is None:
            return
        new_photos=albums.pop(message.media_group_id, None)
        all_ph=new_photos+photos
        if len(all_ph)<3:
            count=len(all_ph)
            await message.answer(f"Добавлено {count} из 3 фото\n(n) - завершить добавление")
            await state.update_data(photo_create=all_ph)
        elif len(all_ph)==3:
            await state.update_data(photo_create=all_ph)
            await state.set_state(users_create_menu.check_state)
            await state_of_create_check(message,state)
        else:
            await message.answer("Максимум можно добавить три фото")
    else:
        photos.append(ph_id)
        await state.update_data(photo_create=photos)
        if len(photos)<3:
            count=len(photos)
            await message.answer(f"Добавлено {count} из 3 фото\n(n) - завершить добавление")
        else:
            await state.set_state(users_create_menu.check_state)
            await state_of_create_check(message,state)




@_router.message(users_create_menu.check_state, ~F.text.lower().in_(["y","n"]))
async def state_of_create_check(message:Message,state:FSMContext):
    await message.answer("Проверьте созданное обсуждение:\n")
    state_data = await state.get_data()
    created_text=state_data.get("text_create","")
    photos = state_data.get("photo_create", [])
    if len(photos)==0:
        await message.answer(created_text)
    elif len(photos)==1:
        await message.answer_photo(photos[0], caption=created_text)
    else:
        ph_group=[]
        first = True
        for ph in photos:
            if first:
                ph_group.append(InputMediaPhoto(media=ph, caption=created_text))
                first=False
            else:
                ph_group.append(InputMediaPhoto(media=ph))
        await message.answer_media_group(ph_group)
    await message.answer("Отправить на модерацию?(y/n)")
    
@_router.message(users_create_menu.check_state, F.text.lower().in_(["y","n"]))
async def state_of_create_check_accept(message:Message,state:FSMContext):
    text = message.text.lower()
    if text=="y":
        user_id=message.from_user.id
        state_data = await state.get_data()
        text_created=state_data.get("text_create","")
        photos = state_data.get("photo_create", [])
        photo_created=""
        for i in photos:
            photo_created+=i+" "
        await add_discussion(user_id,text_created,photo_created)
        await message.answer("успех")
        await state.clear()
    if text=="n":
        await state.clear()
        await _cmd_start(message,state)



@_router.message(F.text == "id")
async def _cmd_hello(_message: Message):
    id = _message.from_user.id
    await _message.answer(f"вотон {id}!")