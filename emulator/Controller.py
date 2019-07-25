import time

from api.hooks import Hook
from emulator.model.Emulator import Emulator
from emulator.view.IControls import IControls
from emulator.view.IGraphics import IGraphics
from emulator.view.ISound import ISound


class Controller:
    def __init__(self):

        self.emulator: Emulator = Emulator()

        self.__gfx: dict = dict()
        self.__sound: dict = dict()
        self.__controls: dict = dict()

        self.__pre_cycle_hooks: dict = dict()
        self.__pre_frame_hooks = dict()
        self.__post_cycle_hooks: dict = dict()
        self.__post_frame_hooks = dict()
        self.__init_hooks: dict = dict()

        self.__looping_forwards: bool = False
        self.__looping_backwards: bool = False
        self.__frame_limit: bool = False
        self.__debug: bool = False

        self.__started: bool = False

        self.__time: float = 0

    # Private

    def __call_graphics(self):
        if self.emulator.draw_flag:
            for _, v in self.__gfx.items():
                v.draw(self.emulator.gfx_pixels)

    def __call_controls(self):
        for _, v in self.__controls.items():
            for i in v.get_keys_pressed():
                self.emulator.press_key(i)

            for i in v.get_keys_released():
                self.emulator.release_key(i)

    def __call_sound(self):
        for _, v in self.__sound.items():
            if self.emulator.beep_flag:
                v.beep()

    def __start_cycle_timer(self):
        self.__time = time.clock()

    def __wait_for_timer(self):
        elapsed = time.clock() - self.__time
        if elapsed < (1 / 60):
            time.sleep((1 / 60) - elapsed)

    def __call_init_hooks(self) :
        for _, v in self.__init_hooks.items():
            v.call()

    def __call_pre_hooks(self) :
        for _, v in self.__pre_cycle_hooks.items():
            v.call()

    def __call_pre_frame_hooks(self):
        for _, v in self.__pre_frame_hooks.items():
            v.call()

    def __call_post_hooks(self) :
        for _, v in self.__post_cycle_hooks.items():
            v.call()

    def __call_post_frame_hooks(self):
        for _, v in self.__post_frame_hooks.items():
            v.call()

    def __start(self):
        self.__started = True
        self.__call_init_hooks()

    # Modules

    def add_gfx(self, name: str, gfx: IGraphics) :
        self.__gfx[name] = gfx

    def add_sound(self, name: str, sound: ISound) :
        self.__sound[name] = sound

    def add_controls(self, name: str, controls: IControls) :
        self.__controls[name] = controls

    # Hooks

    def add_init_hook(self, name: str, hook: Hook) :
        self.__init_hooks[name] = hook

    def add_pre_cycle_hook(self, name: str, hook: Hook) :
        self.__pre_cycle_hooks[name] = hook

    def add_post_cycle_hook(self, name: str, hook: Hook) :
        self.__post_cycle_hooks[name] = hook

    def add_pre_frame_hook(self, name: str, hook: Hook) :
        self.__pre_frame_hooks[name] = hook

    def add_post_frame_hook(self, name: str, hook: Hook) :
        self.__post_frame_hooks[name] = hook

    def remove_init_hook(self, name: str) -> bool:
        if self.__init_hooks[name]:
            del self.__init_hooks[name]
            return True
        return False

    def remove_pre_cycle_hook(self, name: str) -> bool:
        if self.__pre_cycle_hooks[name]:
            del self.__pre_cycle_hooks[name]
            return True
        return False

    def remove_post_cycle_hook(self, name: str) -> bool:
        if self.__post_cycle_hooks[name]:
            del self.__post_cycle_hooks[name]
            return True
        return False

    # Controls

    def load_rom(self, path: str) -> bytearray:
        with open(path, "rb") as f:
            rom = bytearray(512)
            byte = f.read(1)
            i = 0
            while byte != b'':
                rom[i] = byte[0]
                byte = f.read(1)
                i += 1

        self.emulator.load_rom(rom)
        return rom

    def step(self) :
        if not self.__started:
            self.__start()

        frame = False
        if self.emulator.draw_flag:
            frame = True

        self.__call_pre_hooks()
        if frame:
            self.__call_pre_frame_hooks()

        self.__call_graphics()
        self.__call_controls()
        self.__call_sound()

        self.emulator.gamestep()

        self.__call_post_hooks()
        if frame:
            self.__call_post_frame_hooks()

    def step_backwards(self):
        self.__call_pre_hooks()
        self.__call_graphics()
        self.__call_controls()
        self.__call_sound()
        self.emulator.gamestep_backwards()
        self.__call_post_hooks()

    def start_looping_forwards(self):
        if not self.__started:
            self.__start()

        self.__looping_forwards = True
        while self.__looping_forwards:

            if self.__frame_limit:
                self.__start_cycle_timer()

            self.step()

            if self.__frame_limit:
                self.__wait_for_timer()

    def start_looping_backwards(self):
        self.__looping_backwards = True
        while self.__looping_backwards:

            if self.__frame_limit:
                self.__start_cycle_timer()

            self.step_backwards()

            if self.__frame_limit:
                self.__wait_for_timer()

    def stop_looping_forwards(self):
        self.__looping_forwards = False

    def stop_looping_backwards(self):
        self.__looping_backwards = False

    def next_frame(self):
        while not self.emulator.draw_flag:
            self.step()
        self.step()

    def previous_frame(self):
        while not self.emulator.draw_flag:
            self.step_backwards()
        self.step_backwards()

    def set_frame_limit(self, val:bool):
        self.__frame_limit = val