#!/usr/bin/env python3
"""
Test ishlash funksiyasini test qilish
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

async def test_taking_flow():
    print('🔍 Test ishlash jarayonini test qilish...')
    print('=' * 50)
    
    try:
        # Bot instance yaratish
        bot = TestBot()
        message_handlers = MessageHandlers(bot)
        callback_handlers = CallbackHandlers(bot)
        
        # 1. Test tanlash
        print('1️⃣ Test tanlash (ID: 4):')
        update1 = FakeCallbackUpdate(123456789, 'O\'quvchi', 'take_test_4')
        context1 = FakeContext()
        
        await callback_handlers.take_test_callback(update1, context1, 4)
        
        # 2. Testni boshlash
        print('\n2️⃣ Testni boshlash:')
        update2 = FakeCallbackUpdate(123456789, 'O\'quvchi', 'start_test_4')
        context2 = FakeContext()
        
        await callback_handlers.start_test_callback(update2, context2, 4)
        
        # 3. Javob berish
        print('\n3️⃣ Javob berish (abcdabcd):')
        update3 = FakeUpdate(123456789, 'O\'quvchi', 'abcdabcd')
        context3 = FakeContext()
        context3.user_data['taking_test'] = True
        context3.user_data['current_test'] = {
            'test_id': 4,
            'session_id': 1,
            'current_question': 0,
            'answers': {},
            'start_time': None,
            'test_title': 'Test'
        }
        
        await message_handlers._handle_test_answers(update3, context3, 'abcdabcd')
        
        print('\n✅ Test ishlash jarayoni muvaffaqiyatli ishladi!')
        
    except Exception as e:
        print(f'❌ Xatolik: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_taking_flow())
