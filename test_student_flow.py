#!/usr/bin/env python3
"""
O'quvchi uchun to'liq test flow ni test qilish
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
        if reply_markup:
            if hasattr(reply_markup, 'inline_keyboard'):
                print('🎛️ Inline keyboard tugmalari:')
                for i, row in enumerate(reply_markup.inline_keyboard):
                    for j, button in enumerate(row):
                        print(f'  [{i+1}.{j+1}] {button.text} -> {button.callback_data}')
            elif hasattr(reply_markup, 'keyboard'):
                print('⌨️ Reply keyboard tugmalari:')
                for i, row in enumerate(reply_markup.keyboard):
                    for j, button in enumerate(row):
                        print(f'  [{i+1}.{j+1}] {button.text}')
            print('=' * 50)
        return True

class FakeUpdate:
    def __init__(self, user_id, first_name, message_text):
        self.effective_user = FakeUser(user_id, first_name)
        self.message = FakeMessage(message_text)

class FakeContext:
    def __init__(self):
        self.user_data = {}

async def test_student_complete_flow():
    print('🔍 O\'quvchi uchun to\'liq test flow ni test qilish...')
    print('=' * 50)
    
    try:
        # Bot instance yaratish
        bot = TestBot()
        message_handlers = MessageHandlers(bot)
        
        # 1. "Mavjud testlar" tugmasini bosish
        print('1️⃣ "Mavjud testlar" tugmasini bosish:')
        update1 = FakeUpdate(123456789, 'O\'quvchi', '📝 Mavjud testlar')
        context1 = FakeContext()
        
        await message_handlers.handle_message(update1, context1)
        
        # 2. "Ommaviy testlar" tugmasini bosish
        print('\n2️⃣ "Ommaviy testlar" tugmasini bosish:')
        update2 = FakeUpdate(123456789, 'O\'quvchi', '🌍 Ommaviy testlar')
        context2 = FakeContext()
        
        await message_handlers.handle_message(update2, context2)
        
        # 3. "Orqaga" tugmasini bosish
        print('\n3️⃣ "Orqaga" tugmasini bosish:')
        update3 = FakeUpdate(123456789, 'O\'quvchi', '🔙 Orqaga')
        context3 = FakeContext()
        
        await message_handlers.handle_message(update3, context3)
        
        # 4. "Testni qidirish" tugmasini bosish
        print('\n4️⃣ "Testni qidirish" tugmasini bosish:')
        update4 = FakeUpdate(123456789, 'O\'quvchi', '🔍 Testni qidirish')
        context4 = FakeContext()
        
        await message_handlers.handle_message(update4, context4)
        
        # 5. "Orqaga" tugmasini bosish (test qidirishdan)
        print('\n5️⃣ "Orqaga" tugmasini bosish (test qidirishdan):')
        update5 = FakeUpdate(123456789, 'O\'quvchi', '🔙 Orqaga')
        context5 = FakeContext()
        context5.user_data['searching_test'] = True
        
        await message_handlers.handle_message(update5, context5)
        
        print('\n✅ O\'quvchi uchun to\'liq test flow muvaffaqiyatli ishladi!')
        
    except Exception as e:
        print(f'❌ Xatolik: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_student_complete_flow())
