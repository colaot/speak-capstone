import keyboard

print('start')

keyboard.add_hotkey('h+o', lambda: print('Hello'))
keyboard.add_hotkey('w+d', lambda: print('World!'))
#keyboard.add_hotkey('page_up, page down', lambda: print('updog'))

print('hotkeys added')

recorded = keyboard.record(until='x')
#print('recorded 1')
#keyboard.play(recorded)

print(recorded)

keyboard.wait('space')
print('space pressed, exiting')

keyboard.record(until='x')
