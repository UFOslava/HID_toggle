"""Controls the UI within the terminal, to control the pointer device monitor daemon process"""
import rich.style
from rich.console import Console
from rich.table import Table
from rich import inspect
from pynput import keyboard
from daemon import HID, map_HID

app_run: bool = True

console = Console()

# Temp Pointer list; TODO fetch Pointer list from daemon process.
HID_list: list[HID] = map_HID()
selected_HID: int = 0


def display_HID_in_console():
    # Definitions
    global selected_HID
    default_style = rich.style.Style()

    # Init
    console.clear()
    console.print("Watching the list of HID, currently connected and not ignored,"
                  " and enabling the toggled device when none are present.")
    console.print("Example: enabling touchpad when no mice are connected.")

    # Table header
    main_table = Table(title="Pointer Devices", expand=True)
    main_table.add_column("Action", style="green", width=9)
    main_table.add_column("Device Name")
    main_table.add_column("Device ID", style="bold orange1")

    # Table content
    for index, item in enumerate(HID_list):
        style = default_style
        state: str = "Monitored"
        if item.ignored:
            style = style.combine([style, rich.style.Style(dim=True)])
            state = "Ignored"
        elif item.toggled:
            style = style.combine([style, rich.style.Style(color="gold1")])
            state = "Toggle"
        if selected_HID == index:
            style = style.combine([style, rich.style.Style(bgcolor="grey30")])

        main_table.add_row(state,
                           item.name,
                           f"#{item.device_id}",
                           style=style)
    console.print(main_table, justify="left")

    # Table Footer
    console.print("SPACE [dim]- Ignore or restore device.[/dim]")
    console.print("T [dim]- Set device to toggle.[/dim]")
    console.print("Q, Esc [dim]- Quit.[/dim]")


# TODO add increment and decrement selection functions.
# TODO draw selected row
# TODO mark rows for ignore or toggled, using buttons
# TODO send update to daemon (names only?)


def exit_app(confirm: bool = False):
    global app_run
    if confirm:
        # exit(0)
        app_run = False
        quit(0)


def key_released(key: keyboard.Key | keyboard.KeyCode | None = None):
    # print(inspect(key))
    global HID_list, selected_HID
    if isinstance(key, keyboard.Key):
        if key == keyboard.Key.esc:
            exit_app(True)
        elif key == keyboard.Key.up:
            selected_HID -= 1
            selected_HID = selected_HID % len(HID_list)
            display_HID_in_console()
            # print(selected_HID)
        elif key == keyboard.Key.down:
            selected_HID += 1
            selected_HID = selected_HID % len(HID_list)
            display_HID_in_console()
            # print(selected_HID)
        elif key == keyboard.Key.space:
            HID_list[selected_HID].ignore()
            display_HID_in_console()
        return
    elif isinstance(key, keyboard.KeyCode):
        if key.char == "q":
            exit_app(True)
        elif key.char == "t":
            HID_list[selected_HID].toggle()
            display_HID_in_console()
        return
    else:
        print("Unknown keyboard event!")


if __name__ == "__main__":
    selected_HID = 0
    display_HID_in_console()
    while app_run:
        with keyboard.Listener(on_release=key_released) as listener:
            listener.join(5.0)
    console.clear(True)
