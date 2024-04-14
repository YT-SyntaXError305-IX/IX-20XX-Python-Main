import glfw
import OpenGL.GL as gl
import imgui
from imgui.integrations.glfw import GlfwRenderer
import pygetwindow as gw
import pymem, utility
import webbrowser
import sys
import math

process = pymem.Pymem("20XX.exe")
LocalPlayerOffset = process.base_address + 0x47B88B8
MainWeaponPointer = utility.FindDMAAddy(process.process_handle, LocalPlayerOffset, [0x34C])
QWeaponPointer = utility.FindDMAAddy(process.process_handle, LocalPlayerOffset, [0xF44])
WWeaponPointer = utility.FindDMAAddy(process.process_handle, LocalPlayerOffset, [0xF48])
EWeaponPointer = utility.FindDMAAddy(process.process_handle, LocalPlayerOffset, [0xF4C])
DamagePointer = utility.FindDMAAddy(process.process_handle, LocalPlayerOffset, [0x388])
PowerDamagePointer = utility.FindDMAAddy(process.process_handle, LocalPlayerOffset, [0x3B8])
SpeedPointer = utility.FindDMAAddy(process.process_handle, LocalPlayerOffset, [0x370])
JumpPointer = utility.FindDMAAddy(process.process_handle, LocalPlayerOffset, [0x380])
HealthAddress = utility.FindDMAAddy(process.process_handle, LocalPlayerOffset, [0xF0])
EnergyAddress = utility.FindDMAAddy(process.process_handle, LocalPlayerOffset, [0x118])
StaticBolts = process.base_address + 0x4699188
SoulChips = process.base_address + 0x680278
CharacterId = process.base_address + 0x47AFE18

Unlimited = 33000

addresses = [MainWeaponPointer, QWeaponPointer, WWeaponPointer, EWeaponPointer]
original_values = [process.read_int(address) for address in addresses] 
values_set_to_zero = [False] * len(addresses)

Unlimited_Energy_Flag = False
God_Mode_Flag = False
Instant_Kill_Flag = False

def init_imgui(window):
    imgui.create_context()
    impl = GlfwRenderer(window)
    imgui.style_colors_dark()
    return impl

def toggle_unlimited_energy():
    global Unlimited_Energy_Flag
    Unlimited_Energy_Flag = not Unlimited_Energy_Flag
    if Unlimited_Energy_Flag:
        process.write_int(EnergyAddress, Unlimited)
    else:
        print("Unlimited Energy Toggled: OFF")

def toggle_god_mode():
    global God_Mode_Flag
    God_Mode_Flag = not God_Mode_Flag
    if God_Mode_Flag:
        process.write_int(HealthAddress, Unlimited)
        print("God-Mode Toggled: ON")
    else:
        process.write_int(HealthAddress, original_values)
        print("God-Mode Toggled: OFF")

def toggle_instant_kill():
    global Instant_Kill_Flag
    Instant_Kill_Flag = not Instant_Kill_Flag
    if Instant_Kill_Flag:
        process.write_int(DamagePointer, Unlimited)
        process.write_int(PowerDamagePointer, Unlimited)
        print("Instant Kill Toggled: ON")
    else:
        process.write_int(DamagePointer, 0)
        process.write_int(PowerDamagePointer, 0)
        print("Instant Kill Toggled: OFF")

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

    if imgui.button("Unlimited Power"):
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
    imgui.end()
    imgui.render()
    impl.process_inputs()
    impl.render(imgui.get_draw_data())

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

