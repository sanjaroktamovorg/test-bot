#!/usr/bin/env python3
"""
Test Bot - Oddiy test versiyasi
Bu versiya token muammosi bo'lsa ham funksiyalarni test qilish uchun
"""

import asyncio
from src.bot.handlers.message_handlers import MessageHandlers
from src.bot.handlers.callback_handlers import CallbackHandlers
from src.bot.bot import TestBot

# Fake telegram update yaratish
class FakeUser:
    def __init__(self, id, first_name):
        self.id = id
        self.first_name = first_name

class FakeMessage:
    def __init__(self, text):
        self.text = text
        
    async def reply_text(self, text, reply_markup=None):
        print('📱 Bot javobi:')
        print(text)
        print('=' * 50)
        if reply_markup and hasattr(reply_markup, 'inline_keyboard'):
            print('🎛️ Inline keyboard tugmalari:')
            for i, row in enumerate(reply_markup.inline_keyboard):
                for j, button in enumerate(row):
                    print(f'  [{i+1}.{j+1}] {button.text} -> {button.callback_data}')
            print('=' * 50)
        return True

class FakeUpdate:
    def __init__(self, user_id, first_name, message_text):
        self.effective_user = FakeUser(user_id, first_name)
        self.message = FakeMessage(message_text)

class FakeQuery:
    def __init__(self, data, user):
        self.data = data
        self.from_user = user
        
    async def answer(self):
        pass
        
    async def edit_message_text(self, text, reply_markup=None):
        print('📱 Callback javobi:')
        print(text)
        print('=' * 50)
        if reply_markup and hasattr(reply_markup, 'inline_keyboard'):
            print('🎛️ Inline keyboard tugmalari:')
            for i, row in enumerate(reply_markup.inline_keyboard):
                for j, button in enumerate(row):
                    print(f'  [{i+1}.{j+1}] {button.text} -> {button.callback_data}')
            print('=' * 50)
        return True

class FakeCallbackUpdate:
    def __init__(self, user_id, first_name, callback_data):
        user = FakeUser(user_id, first_name)
        self.callback_query = FakeQuery(callback_data, user)

class FakeContext:
    def __init__(self):
        self.user_data = {}

async def test_my_tests():
    print('🔍 "📋 Mening testlarim" funksiyasini test qilish...')
    print('=' * 50)
    
    try:
        # Bot instance yaratish
        bot = TestBot()
        message_handlers = MessageHandlers(bot)
        callback_handlers = CallbackHandlers(bot)
        
        # 1. "📋 Mening testlarim" tugmasini bosish
        print('1️⃣ "📋 Mening testlarim" tugmasini bosish:')
        update1 = FakeUpdate(7537966029, 'Sanjar', '📋 Mening testlarim')
        context1 = FakeContext()
        
        await message_handlers.my_tests_command(update1, context1)
        
        # 2. Birinchi testni tanlash (ID: 2)
        print('\n2️⃣ Test tanlash (h - ID: 2):')
        update2 = FakeCallbackUpdate(7537966029, 'Sanjar', 'view_teacher_test_2')
        context2 = FakeContext()
        
        await callback_handlers.view_teacher_test_callback(update2, context2, 2)
        
        # 3. Orqaga qaytish
        print('\n3️⃣ Orqaga qaytish:')
        update3 = FakeCallbackUpdate(7537966029, 'Sanjar', 'back_to_my_tests')
        context3 = FakeContext()
        
        await callback_handlers.back_to_my_tests_callback(update3, context3)
        
        print('\n✅ Barcha funksiyalar muvaffaqiyatli ishladi!')
        print('✅ "📋 Mening testlarim" bo\'limi to\'liq ishlaydi!')
        
    except Exception as e:
        print(f'❌ Xatolik: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_my_tests())
