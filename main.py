import glfw
import OpenGL.GL as gl
import imgui
from imgui.integrations.glfw import GlfwRenderer
import math
import pygetwindow as gw
import pymem, utility
import webbrowser
import threading
import time
import sys

rapid_int_change_on = False

process = pymem.Pymem("30XX.exe")
LocalPlayerOffset = process.base_address + 0x99A260
MainWeaponPointer = utility.FindDMAAddy(process.process_handle, LocalPlayerOffset, [0x594])
QWeaponPointer = utility.FindDMAAddy(process.process_handle, LocalPlayerOffset, [0x1FA8])
WWeaponPointer = utility.FindDMAAddy(process.process_handle, LocalPlayerOffset, [0x1FAC])
EWeaponPointer = utility.FindDMAAddy(process.process_handle, LocalPlayerOffset, [0x1FB0])
DamagePointer = utility.FindDMAAddy(process.process_handle, LocalPlayerOffset, [0x610])
LightningPointer = utility.FindDMAAddy(process.process_handle, LocalPlayerOffset, [0x640])
SpeedPointer = utility.FindDMAAddy(process.process_handle, LocalPlayerOffset, [0x5F8])
HealthAddress = process.base_address + 0x43E107
EnergyAddress = process.base_address + 0x4E6D3B
InstantKillAddress = process.base_address + 0x4E6355
InstantKillRAddress = process.base_address + 0x4E635C
ColorCyclePointer = process.base_address + 0x49A037C
BypassColorAddress = process.base_address + 0x408A86  

addresses = [MainWeaponPointer, QWeaponPointer, WWeaponPointer, EWeaponPointer]
original_values = [process.read_int(address) for address in addresses]
values_set_to_zero = [False] * len(addresses)

def init_imgui(window):
    imgui.create_context()
    impl = GlfwRenderer(window)
    imgui.style_colors_dark()
    return impl

bypass_color_flag = False
Unlimited_Energy_Flag = False
God_Mode_Flag = False
Instant_Kill_Flag = False

def toggle_bypass_color_flag():
    global bypass_color_flag
    bypass_color_flag = not bypass_color_flag

def toggle_unlimited_energy():
    global Unlimited_Energy_Flag
    Unlimited_Energy_Flag = not Unlimited_Energy_Flag

def toggle_god_mode():
    global God_Mode_Flag
    God_Mode_Flag = not God_Mode_Flag

def toggle_instant_kill():
    global Instant_Kill_Flag
    Instant_Kill_Flag = not Instant_Kill_Flag

def render_imgui(impl, values):
    imgui.new_frame()
    if imgui.begin_main_menu_bar():
        if imgui.begin_menu("IX v0.0.1 SynX Edition",  True):
            clicked_quit, selected_quit = imgui.menu_item("Quit", 'Cmd+Q', False, True)
            if clicked_quit:
                sys.exit()
            imgui.end_menu()
        imgui.end_main_menu_bar()

    imgui.begin("Main Menu", True)

    for i in range(len(values)):
        changed, value = imgui.input_int(f"Value##{i+1}", values[i])
        if changed:
            values[i] = value
            if value == 0 and not values_set_to_zero[i]:
                process.write_int(addresses[i], original_values[i])  
                values_set_to_zero[i] = True
            elif value != 0 and values_set_to_zero[i]:
                values_set_to_zero[i] = False

            if value != 0:  
                process.write_int(addresses[i], value)

    imgui.text("Debug Output:")
    for i, value in enumerate(values):
        color = [math.sin(glfw.get_time() * 2.0) * 0.5 + 0.5,
                 math.sin(glfw.get_time() * 3.0) * 0.5 + 0.5,
                 math.sin(glfw.get_time() * 1.0) * 0.5 + 0.5, 1.0]
        imgui.text_colored(f"Value {i+1}: {value}", *color)

    if rapid_int_change_on:
        imgui.text_colored("RainBow Character: ON", *color)
    else:
        imgui.text("RainBow Character: OFF")

    if imgui.button("Toggle Rainbow Character"):
        toggle_rapid_int_change()

    if imgui.button("Bypass Color"):
        toggle_bypass_color_flag()

    if     imgui.button("Unlimited Power"):
        toggle_unlimited_energy()

    if imgui.button("God-Mode"):
        toggle_god_mode()

    if imgui.button("Instant-Kill"):
        toggle_instant_kill()

    if imgui.button("The Mod Menu Maintainer's YouTube Channel"):
        webbrowser.open("https://www.youtube.com/channel/UCAXpJbKZC9G41TRl5yMRawQ?sub_confirmation=1")

    if imgui.button("Learn Everything About Game Hacking."):
        webbrowser.open("https://www.youtube.com/channel/UCCMi6F5Ac3kQDfffWXQGZDw?sub_confirmation=1")

    imgui.text_colored("Cheat the game because it doesn't mind cheating you. ~ CTG", *color)
    if imgui.button("Learn Cheat Engine"):
        webbrowser.open("https://www.youtube.com/@ChrisFayte?sub_confirmation=1")
    
    if Instant_Kill_Flag:
        process.write_bytes(InstantKillAddress, b"\x48\xB8\x00\x00\x00\x00\x00\x00\x00\x00" ,10)
    else:
        process.write_bytes(InstantKillAddress, b"\x48\x8B\x83\xB8\x01\x00\x00" ,7)
        process.write_bytes(InstantKillRAddress, b"\x48\x2B\xC5" ,3)

    if bypass_color_flag:
        process.write_bytes(BypassColorAddress, b"\x75\x1A" ,2)
    else:
        process.write_bytes(BypassColorAddress, b"\x74\x1A" ,2)  

    if Unlimited_Energy_Flag:
        process.write_bytes(EnergyAddress, b"\x90\x90\x90\x90\x90\x90\x90" ,7)
    else:
        process.write_bytes(EnergyAddress, b"\x48\x29\x9F\xE8\x01\x00\xf0" ,7)

    if God_Mode_Flag:
        process.write_bytes(HealthAddress, b"\x90\x90\x90" ,3)
    else:
        process.write_bytes(HealthAddress, b"\x48\x2B\xCF" ,3)  

    imgui.end()

    imgui.render()
    impl.process_inputs()
    impl.render(imgui.get_draw_data())

def toggle_rapid_int_change():
    global rapid_int_change_on
    rapid_int_change_on = not rapid_int_change_on
    if rapid_int_change_on:
        threading.Thread(target=rapid_int_change_thread).start()

def rapid_int_change_thread():
    value = 0
    while rapid_int_change_on:
        process.write_int(ColorCyclePointer, value)
        value = (value + 1) % 13
        if value == 0:
            value = 1
        time.sleep(0.1)

def main():
    menu_visible = True

    if not glfw.init():
        return -1

    glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)
    glfw.window_hint(glfw.FOCUSED, glfw.TRUE)
    glfw.window_hint(glfw.DECORATED, glfw.FALSE)
    window = glfw.create_window(1280, 720, "Python Developer Menu", None, None)
    if not window:
        glfw.terminate()
        return -1

    glfw.make_context_current(window)

    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    impl = init_imgui(window)

    values = [0] * len(addresses)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        if glfw.get_key(window, glfw.KEY_INSERT) == glfw.PRESS:
            menu_visible = not menu_visible
            if menu_visible:
                pywindow = gw.getWindowsWithTitle("Python Developer Menu")[0]
                pywindow.activate()

        if menu_visible:
            render_imgui(impl, values)

        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()

    return 0

if __name__ == "__main__":
    main()
