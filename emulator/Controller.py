import time

from hooks_api import IHook
from model.Emulator import Emulator
from view.IControls import IControls
from view.IGraphics import IGraphics
from view.ISound import ISound


class Controller:
    def __init__(self):

        self.emulator:Emulator=Emulator()
        self.gfx:dict[str,IGraphics] = dict()
        self.sound:dict[str,ISound] = dict()
        self.controls:dict[str,IControls] = dict()

        self.pre_cycle_hooks:dict[str,IHook] = dict()
        self.post_cycle_hooks:dict[str,IHook] = dict()
        self.init_hooks:dict[str,IHook] = dict()

        self.__looping_forwards:bool = False
        self.__looping_backwards:bool = False
        self.__frame_limit:bool = False
        self.__debug:bool = False

        self.__time:float = 0




    #### Private

    def __call_graphics(self):
       for _,v in self.gfx.items():
            if self.emulator.draw_flag:
                v.draw(self.emulator.gfx_pixels)

    def __call_controls(self):
        for _, v in self.controls.items():
            for i in v.get_keys_pressed():
                self.emulator.press_key(i)

            for i in v.get_keys_released():
                self.emulator.release_key(i)


    def __call_sound(self):
        for _, v in self.sound.items():
            if self.emulator.beep_flag:
                v.beep()

    def __start_cycle_timer(self):
        self.__time = time.clock()

    def __wait_for_timer(self):
        elapsed = time.clock() - self.__time
        if elapsed < (1/60):
            time.sleep((1/60) - elapsed)

    def __call_init_hooks(self) -> None:
        for _, v in self.init_hooks.items():
            v()

    def __call_pre_hooks(self) -> None:
        for _, v in self.pre_cycle_hooks.items():
            v()

    def __call_post_hooks(self) -> None:
        for _, v in self.post_cycle_hooks.items():
            v()

    #### Modules

    def add_gfx(self, name:str, gfx: IGraphics) -> None:
        self.gfx[name] = gfx

    def add_sound(self, name:str, sound: ISound) -> None:
        self.sound[name]=sound

    def add_controls(self, name:str, controls: IControls) -> None:
        self.controls[name] = controls

    #### Hooks

    def add_init_hook(self, name: str, function) -> None:
        self.init_hooks[name] = function

    def add_pre_cycle_hook(self, name: str, function) -> None:
        self.pre_cycle_hooks[name] = function

    def add_post_cycle_hook(self, name: str, function) -> None:
        self.post_cycle_hooks[name] = function

    def remove_init_hook(self, name: str) -> bool:
        if self.init_hooks[name]:
            del self.init_hooks[name]
            return True
        return False

    def remove_pre_cycle_hook(self, name: str) -> bool:
        if self.pre_cycle_hooks[name]:
            del self.pre_cycle_hooks[name]
            return True
        return False

    def removePostcycleHook(self, name: str) -> bool:
        if self.post_cycle_hooks[name]:
            del self.post_cycle_hooks[name]
            return True
        return False


    #### Controls

    def load_rom(self, path) -> None:
        with open(path, "rb") as f:
            rom = bytearray(512)
            byte = f.read(1)
            i = 0
            while byte != b'':
                rom[i] = byte[0]
                byte = f.read(1)
                i += 1

        self.emulator.load_rom(rom)

    def step(self) -> None:
        self.__call_pre_hooks()
        self.__call_graphics()
        self.__call_graphics()
        self.__call_controls()
        self.__call_sound()
        self.emulator.gamestep()
        self.__call_post_hooks()


    def step_backwards(self) -> None:
        self.__call_pre_hooks()
        self.__call_graphics()
        self.__call_controls()
        self.__call_sound()
        self.emulator.gamestep_backwards()
        self.__call_post_hooks()


    def begin_loop_forwards(self) -> None:
        self.__looping_forwards = True
        while self.__looping_forwards:

            if self.__frame_limit:
                self.__start_cycle_timer()

            self.step()

            if self.__frame_limit:
                self.__wait_for_timer()

    def begin_loop_backwards(self) -> None:
        self.__looping_backwards = True
        while self.__looping_backwards:

            if self.__frame_limit:
                self.__start_cycle_timer()

            self.step_backwards()

            if self.__frame_limit:
                self.__wait_for_timer()

    def end_looping_forwards(self) -> None:
        self.__looping_forwards = False

    def end_loop_backwards(self) -> None:
        self.__looping_backwards = False
