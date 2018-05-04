#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Axiom_AIR_Mini32/AxiomAirMini32.py
from __future__ import with_statement
import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from _Framework.TransportComponent import TransportComponent
from _Framework.SessionComponent import SessionComponent
from _Framework.MixerComponent import MixerComponent
from _Framework.ChannelStripComponent import ChannelStripComponent
from _Framework.ModeSelectorComponent import ModeSelectorComponent
from _Framework.DeviceComponent import DeviceComponent as RawDeviceComponent
from Axiom_DirectLink.BestBankDeviceComponent import BestBankDeviceComponent as DeviceComponent
from _Framework.ButtonMatrixElement import ButtonMatrixElement

from DeviceNavComponent import DeviceNavComponent

# Live logfile /Users/<username>/Library/Preferences/Ableton/Live 8.x.x/Log.txt

NUM_TRACKS = 8
GLOBAL_CHANNEL = 0

def make_button(cc_no, is_momentary=True):
    return ButtonElement(is_momentary, MIDI_NOTE_TYPE, GLOBAL_CHANNEL, cc_no)


def make_encoder(cc_no):
    return EncoderElement(MIDI_CC_TYPE, GLOBAL_CHANNEL, cc_no, Live.MidiMap.MapMode.absolute)


class AAA(ControlSurface):
    """ Heavily modified script for the M-Audio Axiom A.I.R. Mini 32 """
    """ Meant for Livid Code v2 using default settings and channel 2 """

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        with self.component_guard():

            self._device_selection_follows_track_selection = True

            self._encoders = tuple([
                make_encoder(1), make_encoder(5),
                make_encoder(9), make_encoder(13),
                make_encoder(17), make_encoder(21),
                make_encoder(25), make_encoder(29),

                make_encoder(2), make_encoder(6),
                make_encoder(10), make_encoder(14),
                make_encoder(18), make_encoder(22),
                make_encoder(26), make_encoder(30),

                make_encoder(3), make_encoder(7),
                make_encoder(11), make_encoder(15),
                make_encoder(19), make_encoder(23),
                make_encoder(27), make_encoder(31),

                make_encoder(4), make_encoder(8),
                make_encoder(12), make_encoder(16),
                make_encoder(20), make_encoder(24),
                make_encoder(28), make_encoder(32)
            ])

            self._encoder_buttons = ButtonMatrixElement()
            self._encoder_buttons.add_row(tuple([
                make_button(1), make_button(5),
                make_button(9), make_button(13),
                make_button(17), make_button(21),
                make_button(25), make_button(29)
            ]))
            self._encoder_buttons.add_row(tuple([
                make_button(2), make_button(6),
                make_button(10), make_button(14),
                make_button(18), make_button(22),
                make_button(26), make_button(30)
            ]))
            self._encoder_buttons.add_row(tuple([
                make_button(3), make_button(7),
                make_button(11), make_button(15),
                make_button(19), make_button(23),
                make_button(27), make_button(31)
            ]))
            self._encoder_buttons.add_row(tuple([
                make_button(4), make_button(8),
                make_button(12), make_button(16),
                make_button(20), make_button(24),
                make_button(28), make_button(32)
            ]))
            Live.Base.log("button matrix %s %s" %
                          (self._encoder_buttons.width(),
                           self._encoder_buttons.height())
            )

            self._side_buttons = tuple([
                make_button(33), make_button(34),
                make_button(35), make_button(36)
            ])

            # self._big_button = make_button(37)

            self._bottom_buttons = tuple([
                make_button(38), make_button(39),
                make_button(40), make_button(41),
                make_button(42), make_button(43),
                make_button(44), make_button(45)
            ])

            self._selector = MainModeSelector(self._encoders,
                                              self._encoder_buttons,
                                              self._side_buttons,
                                              # self._big_button,
                                              self._bottom_buttons,
                                              self)

            self.set_highlighting_session_component(
                self._selector.session_component())

    def tmp_show_message(self, message):
        pass

    def refresh_state(self):
        ControlSurface.refresh_state(self)
        for component in self.components:
            if isinstance(component, ModeSelectorComponent):
                # by default select mixer mode
                component.set_mode(0)

    def handle_sysex(self, midi_bytes):
        pass

    def disconnect(self):
        self._encoders = None
        self._encoder_buttons = None
        self._side_buttons = None
        # self._big_button = None
        self._bottom_buttons = None
        self._selector = None
        ControlSurface.disconnect(self)

    def _on_selected_track_changed(self):
        ControlSurface._on_selected_track_changed(self)
        track = self.song().view.selected_track
        device_to_select = track.view.selected_device
        if device_to_select == None and len(track.devices) > 0:
            device_to_select = track.devices[0]
        if device_to_select != None:
            self.song().view.select_device(device_to_select)
        self._device_component.set_device(device_to_select)


class SpecialMixerComponent(MixerComponent):
    """ Special mixer class that uses return tracks alongside midi and audio tracks """

    def tracks_to_use(self):
        return tuple(self.song().visible_tracks) + tuple(self.song().return_tracks)

    def _create_strip(self):
        return ChannelStripComponent()


class MainModeSelector(ModeSelectorComponent):

    def __init__(self,
                 encoders,
                 encoder_buttons,
                 side_buttons,
                 # big_button,
                 bottom_buttons,
                 control_surface):

        ModeSelectorComponent.__init__(self)
        Live.Base.log("init!")

        self._control_surface = control_surface

        self._encoders = encoders
        self._encoder_buttons = encoder_buttons
        # self._big_button = big_button
        self._bottom_buttons = bottom_buttons

        self._mode_index = 0
        self.set_mode_buttons(side_buttons)

        self._session = SessionComponent(
            self._encoder_buttons.width(),
            self._encoder_buttons.height()
        )
        self._mixer = SpecialMixerComponent(self._encoder_buttons.width())
        self._session.set_mixer(self._mixer)
        self._device = DeviceComponent()
        self._customdevice = [
            RawDeviceComponent(),
            RawDeviceComponent(),
            RawDeviceComponent(),
            RawDeviceComponent(),
            RawDeviceComponent(),
            RawDeviceComponent(),
            RawDeviceComponent(),
            RawDeviceComponent()
        ]
        self._control_surface.set_device_component(self._device)
        self._device_nav = DeviceNavComponent()
        self._transport = TransportComponent()

    def number_of_modes(self):
        return 4

    def on_enabled_changed(self):
        self.update()

    def disconnect(self):

        for button in self._modes_buttons:
            button.remove_value_listener(self._mode_value)

        self.release_controls()

        self.setup_session_paging(as_active=False)

        self._session = None
        self._mixer = None
        self._device = None
        self._device_nav = None
        self._transport = None

        ModeSelectorComponent.disconnect(self)

    def session_component(self):
        return self._session

    def update(self):
        assert (self._modes_buttons != None)
        if self.is_enabled():

            self.update_mode_buttons()

            as_active = True

            self._session.set_allow_update(False)
            self._mixer.set_allow_update(False)

            self.release_controls()

            self.setup_session_paging(as_active)

            if self._mode_index in [0, 1]:

                self.setup_device(not as_active)
                self.setup_custom(not as_active)

                if self._mode_index == 0:

                    self.setup_mixer(as_active)

                elif self._mode_index == 1:

                    self.setup_sends(as_active)

            elif self._mode_index == 2:

                self.setup_mixer(not as_active)
                self.setup_sends(not as_active)
                self.setup_custom(not as_active)

                self.setup_device(as_active)

            elif self._mode_index == 3:

                self.setup_device(not as_active)
                self.setup_mixer(not as_active)
                self.setup_sends(not as_active)

                self.setup_custom(as_active)

            self._mixer.set_allow_update(True)
            self._session.set_allow_update(True)

    def update_mode_buttons(self):

        for b in self._modes_buttons:
            b.reset()

        self._modes_buttons[self._mode_index].send_value(127)

    def release_controls(self):
        Live.Base.log("release controls!")
        # reset encoder button leds
        for b in self._encoder_buttons.iterbuttons():
            b[0].release_parameter()
            b[0].send_value(0, force=True)
        # reset encoder leds
        for e in self._encoders:
            e.release_parameter()
            e.send_value(0, force=True)
        # self._big_button.reset()

    def setup_session_paging(self, as_active=True):
        assert isinstance(as_active, type(False))
        Live.Base.log("setup session paging!")
        if as_active:
            self._mixer.set_select_buttons(
                self._bottom_buttons[5],
                self._bottom_buttons[4])
            self._session.set_page_up_button(self._bottom_buttons[0])
            self._session.set_page_down_button(self._bottom_buttons[1])
            self._session.set_page_left_button(self._bottom_buttons[2])
            self._session.set_page_right_button(self._bottom_buttons[3])
            self._transport.set_metronome_button(self._bottom_buttons[6])
            self._transport.set_tap_tempo_button(self._bottom_buttons[7])
        else:
            self._mixer.set_select_buttons(
                None,
                None)
            self._session.set_page_up_button(None)
            self._session.set_page_down_button(None)
            self._session.set_page_left_button(None)
            self._session.set_page_right_button(None)
            self._transport.set_metronome_button(None)
            self._transport.set_tap_tempo_button(None)

    def setup_device(self, as_active=True):
        assert isinstance(as_active, type(False))
        Live.Base.log("setup device!")

        if as_active:

            self._device.set_on_off_button(
                self._encoder_buttons.get_button(0, 0))
            self._device.set_bank_nav_buttons(
                self._encoder_buttons.get_button(0, 2),
                self._encoder_buttons.get_button(1, 2))
            self._device_nav.set_device_nav_buttons(
                self._encoder_buttons.get_button(2, 2),
                self._encoder_buttons.get_button(3, 2))

            self._device.set_bank_buttons(tuple([
                self._encoder_buttons.get_button(0, 1),
                self._encoder_buttons.get_button(1, 1),
                self._encoder_buttons.get_button(2, 1),
                self._encoder_buttons.get_button(3, 1),
                self._encoder_buttons.get_button(4, 1),
                self._encoder_buttons.get_button(5, 1),
                self._encoder_buttons.get_button(6, 1),
                self._encoder_buttons.get_button(7, 1)
            ]))

            self._device.set_parameter_controls(tuple(self._encoders[:8]))

        else:

            self._device.set_on_off_button(
                None)
            self._device.set_bank_nav_buttons(
                None,
                None)
            self._device_nav.set_device_nav_buttons(
                None,
                None)

            self._device.set_bank_buttons(tuple([
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None
            ]))

            self._device.set_parameter_controls(tuple([
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None
            ]))

        for index in range(self._encoder_buttons.width()):

            strip = self._mixer.channel_strip(index)

            if as_active:

                strip.set_select_button(
                    self._encoder_buttons.get_button(index, 3)
                )

            else:

                strip.set_select_button(
                    None
                )

    def setup_mixer(self, as_active=True):
        assert isinstance(as_active, type(False))

        Live.Base.log("mixer mode!")

        for index in range(self._encoder_buttons.width()):

            strip = self._mixer.channel_strip(index)

            if as_active:

                strip.set_send_controls([
                    self._encoders[index],
                    self._encoders[index + 8],
                    None,
                    None
                ])
                strip.set_pan_control(self._encoders[index + 16])
                strip.set_volume_control(self._encoders[index + 24])

                strip.set_mute_button(self._encoder_buttons.get_button(index, 1))
                strip.set_solo_button(self._encoder_buttons.get_button(index, 2))
                strip.set_arm_button(self._encoder_buttons.get_button(index, 3))

            else:

                strip.set_volume_control(None)
                strip.set_pan_control(None)
                strip.set_send_controls([None, None, None, None])

                strip.set_arm_button(None)
                strip.set_solo_button(None)
                strip.set_mute_button(None)

        if as_active:

            self._session.set_stop_track_clip_buttons(tuple([
                self._encoder_buttons.get_button(0, 0),
                self._encoder_buttons.get_button(1, 0),
                self._encoder_buttons.get_button(2, 0),
                self._encoder_buttons.get_button(3, 0),
                self._encoder_buttons.get_button(4, 0),
                self._encoder_buttons.get_button(5, 0),
                self._encoder_buttons.get_button(6, 0),
                self._encoder_buttons.get_button(7, 0)
            ]))

        else:

            self._session.set_stop_track_clip_buttons(tuple([
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None
            ]))


    def setup_sends(self, as_active=True):
        assert isinstance(as_active, type(False))
        Live.Base.log("send mode!")

        for index in range(NUM_TRACKS):

            strip = self._mixer.channel_strip(index)

            if as_active:

                strip.set_send_controls([
                    self._encoders[index],
                    self._encoders[index + 8],
                    self._encoders[index + 16],
                    self._encoders[index + 24]
                ])

            else:

                strip.set_volume_control(None)
                strip.set_pan_control(None)
                strip.set_send_controls([None, None, None, None])

                strip.set_mute_button(None)
                strip.set_solo_button(None)
                strip.set_arm_button(None)

    def setup_custom(self, as_active=True):
        assert isinstance(as_active, type(False))
        Live.Base.log("custom mode!")

        for scene_index in range(self._encoder_buttons.height()):
            scene = self._session.scene(scene_index)
            for track_index in range(self._encoder_buttons.width()):
                clip_slot = scene.clip_slot(track_index)
                if as_active:

                    clip_slot.set_launch_button(
                        self._encoder_buttons.get_button(
                            track_index,
                            scene_index)
                    )

                else:

                    clip_slot.set_launch_button(
                        None
                    )

        for index in range(self._encoder_buttons.width()):

            # device_comp.disconnect()

            strip = self._mixer.channel_strip(index)
            track = strip._track
            device = None
            Live.Base.log(str(index))
            if track is not None:
                if len(track.devices) > 0:
                    device = track.devices[0]
                # for d in track.devices:
                #     Live.Base.log(str(d.parameters))
                #     Live.Base.log(str(dir(d.parameters)))

            if as_active:

                if device is not None:
                    device_comp = self._customdevice[index]
                    Live.Base.log(str(device))
                    device_comp.set_lock_to_device(True, device)
                    device_comp.set_parameter_controls(
                        tuple([
                            self._encoders[index],
                            self._encoders[index + 8],
                            self._encoders[index + 16],
                            self._encoders[index + 24]
                        ])
                    )

                # strip.set_send_controls([
                #     self._encoders[index],
                #     self._encoders[index + 8],
                #     None,
                #     None
                # ])
                # strip.set_pan_control(self._encoders[index + 16])
                # strip.set_volume_control(self._encoders[index + 24])

            else:

                pass
                # strip.set_volume_control(None)
                # strip.set_pan_control(None)
                # strip.set_send_controls([None, None, None, None])
