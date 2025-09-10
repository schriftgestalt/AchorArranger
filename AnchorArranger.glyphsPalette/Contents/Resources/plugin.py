# encoding: utf-8

###########################################################################################################
#
#
#	Palette Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Palette
#
#
###########################################################################################################
# from __future__ import division, print_function, unicode_literals

import objc
import re  #for checking numbers in string
from GlyphsApp import Glyphs, GSEditViewController, UPDATEINTERFACE
from GlyphsApp.plugins import PalettePlugin
from vanilla import Window, Button, EditText, TextBox, RadioGroup, Popover, Group
from AppKit import NSImage, NSImageNameTouchBarGoUpTemplate, NSImageNameTouchBarGoDownTemplate
from Foundation import NSPoint


defaultMarginDigit = 62
class AnchorArranger(PalettePlugin):
    def GetarrangeType(self):
        ################# Top
        if hasattr(Glyphs.font, 'userData'):
            if Glyphs.font.userData['arrangeType']:
                arrangeType = Glyphs.font.userData['arrangeType']
            else:
                arrangeType = 0
        else:
            arrangeType = 0
        return int(arrangeType)

    def GetTopMargin(self) -> int:
        ################# Top
        if hasattr(Glyphs.font, 'userData'):
            userMargin = Glyphs.font.userData['TopMargin']
            if userMargin or userMargin == 0:
                anchorTopMargin = userMargin
            else:
                anchorTopMargin = defaultMarginDigit
        else:
            anchorTopMargin = defaultMarginDigit
        return int(anchorTopMargin)

    def GetBottomMargin(self):
        ################# Bottom
        userMargin = Glyphs.font.userData['BottomMargin']
        if hasattr(Glyphs.font, 'userData'):
            if userMargin or userMargin == 0:
                anchorBottomMargin = userMargin
            else:
                anchorBottomMargin = defaultMarginDigit
        else:
            anchorBottomMargin = defaultMarginDigit
        return anchorBottomMargin
###############################################################################################


    def settings(self):

        self.name = "Anchor Arranger"
        # Create Vanilla window and group with controls
        width = 150
        height = 127
        self.w = Window((width, height))
        self.w.group = Group((0, 0, width, height))

        self.w.group.TopAnchorsLabel = TextBox((10, 4, 60, 17), "Top Anchors")
        self.w.group.TopAnchorsText = EditText((61, 1, 40, 23), self.GetTopMargin(), callback=self.editTextTopMargin)
        self.w.group.TopButton = Button((107, 0, 30, 23), title="", callback=self.moveAnchorTop)
        self.w.group.TopButton.getNSButton().setImage_(NSImage.imageNamed_(NSImageNameTouchBarGoUpTemplate))
        self.w.group.TopAnchorsCurrent = TextBox((141, 4, 60, 17), "0")

        self.w.group.BottomAnchorsLabel = TextBox((10, 31, 60, 17), "Bottom Anchors")
        self.w.group.BottomAnchorsText = EditText((61, 28, 40, 23), self.GetBottomMargin(), callback=self.editTextBottomMargin)
        self.w.group.BottomButton = Button((107, 27, 30, 23), title="", callback=self.moveAnchorBottom)
        self.w.group.BottomButton.getNSButton().setImage_(NSImage.imageNamed_(NSImageNameTouchBarGoDownTemplate))
        self.w.group.BottomAnchorsCurrent = TextBox((141, 31, 60, 17), "0")

        #self.w.group.Hline = HorizontalLine((10, 70, -10, 1))
        self.w.group.textBox = TextBox((10, 60, -10, 20), "Arrangment type")
        self.w.group.radioGroup = RadioGroup((10, 80, -10, 40), ["Glyph Last Node", "Current Position"], callback=self.radioGroupCallback)
        self.w.group.radioGroup.set(self.GetarrangeType())

        # Set dialog to NSView
        self.dialog = self.w.group.getNSView()

    @objc.python_method
    def radioGroupCallback(self, sender):
        Glyphs.font.userData['arrangeType'] = sender.get()

    @objc.python_method
    def editTextTopMargin(self, sender):
        topMargin = sender.get()
        if topMargin == '':
            dummyvalue = None
        else:
            if re.match('^[.0-9]*$', topMargin):
                if topMargin[0] == '.' or topMargin[-1] == '.':
                    dummyvalue = None
                else:
                    Glyphs.font.userData['TopMargin'] = int(float(topMargin))

    @objc.python_method
    def editTextBottomMargin(self, sender):
        BottomMargin = sender.get()
        if BottomMargin == '':
            dummyvalue = None
        else:
            if re.match('^[.0-9]*$', BottomMargin):
                if BottomMargin[0] == '.' or BottomMargin[-1] == '.':
                    dummyvalue = None
                else:
                    Glyphs.font.userData['BottomMargin'] = int(float(BottomMargin))

    @objc.python_method
    def start(self):
        Glyphs.addCallback(self.update, UPDATEINTERFACE)

    @objc.python_method
    def __del__(self):
        Glyphs.removeCallback(self.update)

    @objc.python_method
    def update(self, sender):
        currentTab = sender.object()
        if isinstance(currentTab, GSEditViewController):
            layer = currentTab.activeLayer()
            if layer is not None:
                if layer.selection:
                    self.UpdateCurrentTopAnchorPosition()
                    self.UpdateCurrentBottomAnchorPosition()

    @objc.python_method
    def popoverView(self, TextToShow, objectToShow):
        self.pop = Popover((200, 80))
        self.pop.text = TextBox((10, 10, -10, -10), TextToShow)
        self.pop.open(parentView=objectToShow, preferredEdge='left')


    @objc.python_method
    def moveAnchorTop(self, sender):
        if Glyphs.font.selectedLayers:
            if Glyphs.font.userData['arrangeType'] == 1:
                self.moveTopByAnchor()
            else:
                self.moveTopByLastNode()
        else:
            self.popoverView('Please Select A layer fist', self.w.group.TopButton)

    @objc.python_method
    def moveAnchorBottom(self, sender):
        if Glyphs.font.selectedLayers:
            if Glyphs.font.userData['arrangeType'] == 1:
                self.moveBottomByAnchor()
            else:
                self.moveBottomByLastNode()
        else:
            self.popoverView('Please Select A layer fist', self.w.group.BottomButton)

    @objc.python_method
    def UpdateCurrentTopAnchorPosition(self):
        if Glyphs.font.selectedLayers:
            layer = Glyphs.font.selectedLayers[0]
            for currentAnchor in Glyphs.font.selectedLayers[0].anchors:
                if currentAnchor.selected:
                    currentAnchorSelected = currentAnchor
                    CurrentTopAnchorPosition = layer.bounds.size.height + layer.bounds.origin.y
                    self.w.group.TopAnchorsCurrent.set(currentAnchor.y - CurrentTopAnchorPosition)

    @objc.python_method
    def UpdateCurrentBottomAnchorPosition(self):
        if Glyphs.font.selectedLayers:
            layer = Glyphs.font.selectedLayers[0]
            for currentAnchor in Glyphs.font.selectedLayers[0].anchors:
                if currentAnchor.selected:
                    currentAnchorSelected = currentAnchor
                    CurrentTopAnchorPosition = layer.bounds.size.height - layer.bounds.origin.y
                    self.w.group.BottomAnchorsCurrent.set(layer.bounds.origin.y - currentAnchor.y)

    @objc.python_method
    def moveBottomByAnchor(self):
        if Glyphs.font.selectedLayers:
            layer = Glyphs.font.selectedLayers[0]
            anchorsSelectedCount = 0
            for currentAnchor in Glyphs.font.selectedLayers[0].anchors:
                if currentAnchor.selected:
                    anchorsSelectedCount += 1
                    currentAnchorSelected = currentAnchor
                    currentAnchor.position = NSPoint(currentAnchor.x, currentAnchor.y - self.GetBottomMargin())
            if anchorsSelectedCount == 0:
                self.popoverView('Please Select At less one Anchor', self.w.group.TopAnchorsLabel)

    @objc.python_method
    def moveBottomByLastNode(self):
        if Glyphs.font.selectedLayers:
            layer = Glyphs.font.selectedLayers[0]
            anchorsSelectedCount = 0
            for currentAnchor in Glyphs.font.selectedLayers[0].anchors:
                if currentAnchor.selected:
                    anchorsSelectedCount += 1
                    currentAnchorSelected = currentAnchor
                    currentAnchor.position = NSPoint(currentAnchor.x, layer.bounds.origin.y - self.GetBottomMargin())
            if anchorsSelectedCount == 0:
                self.popoverView('Please Select At less one Anchor', self.w.group.TopAnchorsLabel)

    @objc.python_method
    def moveTopByAnchor(self):
        if Glyphs.font.selectedLayers:
            layer = Glyphs.font.selectedLayers[0]
            anchorsSelectedCount = 0
            for currentAnchor in Glyphs.font.selectedLayers[0].anchors:
                if currentAnchor.selected:
                    anchorsSelectedCount += 1
                    currentAnchorSelected = currentAnchor
                    currentAnchor.position = NSPoint(currentAnchor.x, currentAnchor.y + self.GetTopMargin())
            if anchorsSelectedCount == 0:
                self.popoverView('Please Select At less one Anchor', self.w.group.TopAnchorsLabel)

    @objc.python_method
    def moveTopByLastNode(self):
        if Glyphs.font.selectedLayers:
            layer = Glyphs.font.selectedLayers[0]
            anchorsSelectedCount = 0
            current_top_position = layer.bounds.size.height + layer.bounds.origin.y
            for currentAnchor in Glyphs.font.selectedLayers[0].anchors:
                if currentAnchor.selected:
                    anchorsSelectedCount += 1
                    currentAnchorSelected = currentAnchor
                    currentAnchor.position = NSPoint(currentAnchor.x, current_top_position + self.GetTopMargin())
            if anchorsSelectedCount == 0:
                self.popoverView('Please Select At less one Anchor', self.w.group.TopAnchorsLabel)
