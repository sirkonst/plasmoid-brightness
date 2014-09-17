# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript

from PyQt4.QtCore import Qt
from PyQt4 import QtGui

import dbus
from dbus.mainloop.qt import DBusQtMainLoop
# ------------------------------------------------------------------------------


class BrightnessPlasmoid(plasmascript.Applet):

    def __init__(self, parent, args=None):
        plasmascript.Applet.__init__(self, parent)
        self.dbusloop = DBusQtMainLoop()
        self.bus = dbus.SessionBus(mainloop=self.dbusloop)

    def init(self):
        self.setHasConfigurationInterface(False)
        self.setAspectRatioMode(Plasma.IgnoreAspectRatio)

        # -- widgets
        slider = BrightnessSlider(self.bus, self.applet)
        icon_incr = Plasma.IconWidget(
            QtGui.QIcon(
                self.package().path() + "contents/images/brightness_incr.png"),
            "", self.applet
        )
        icon_decr = Plasma.IconWidget(
            QtGui.QIcon(
                self.package().path() + "contents/images/brightness_decr.png"),
            "", self.applet
        )

        # -- some logic
        icon_incr.clicked.connect(slider.stepUp)
        icon_decr.clicked.connect(slider.stepDown)

        # -- layoyt
        layout = QtGui.QGraphicsLinearLayout(Qt.Vertical, self.applet)
        layout.addItem(icon_incr)
        layout.addItem(slider)
        layout.setAlignment(slider, Qt.AlignCenter)
        layout.addItem(icon_decr)

        self.applet.setLayout(layout)


class BrightnessSlider(Plasma.Slider):

    def __init__(self, bus, *a, **kw):
        super(BrightnessSlider, self).__init__(*a, **kw)

        power_obj = bus.get_object(
            "org.freedesktop.PowerManagement",
            "/org/kde/Solid/PowerManagement/Actions/BrightnessControl"
        )
        self.bright_if = dbus.Interface(
            power_obj,
            "org.kde.Solid.PowerManagement.Actions.BrightnessControl"
        )
        curr_bright = self.bright_if.brightness()

        self.setMinimum(5)
        self.setMaximum(100)
        self.setValue(curr_bright)
        self.sliderMoved.connect(self.on_change_value)
        self.valueChanged.connect(self.on_change_value)

        self.bright_if.connect_to_signal(
            "brightnessChanged", self.change_value_ex
        )

    def on_change_value(self, value):
        self.bright_if.setBrightness(value)

    def change_value_ex(self, value):
        self.blockSignals(True)
        self.setValue(value)
        self.blockSignals(False)

    def stepUp(self):
        val = self.value() + 5
        if val > self.maximum():
            val = self.maximum()
        self.setValue(val)

    def stepDown(self):
        val = self.value() - 5
        if val < self.minimum():
            val = self.minimum()
        self.setValue(val)


def CreateApplet(parent):
    return BrightnessPlasmoid(parent)