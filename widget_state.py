__author__ = 'masslab'


from config import slider_max


def state_initial(ui):
    ui.addRadio.setChecked(True)
    ui.recordRadio.setChecked(False)
    ui.freqSlider.setEnabled(True)
    ui.selectButton.setEnabled(True)
    ui.portCombo.setEnabled(False)
    ui.acquireButton.setEnabled(False)
    ui.instrTable.setEnabled(True)

def state_instrument_selected(ui):
    ui.addRadio.setChecked(True)
    ui.recordRadio.setChecked(False)
    ui.freqSlider.setEnabled(True)
    ui.selectButton.setEnabled(True)
    ui.portCombo.setEnabled(True)
    ui.acquireButton.setEnabled(True)

def state_after_add(ui):
    ui.addRadio.setChecked(True)
    ui.recordRadio.setChecked(False)
    ui.addRadio.setEnabled(True)
    ui.recordRadio.setEnabled(True)
    ui.freqSlider.setEnabled(True)
    ui.selectButton.setEnabled(True)
    ui.portCombo.setEnabled(False)
    ui.acquireButton.setEnabled(False)
    ui.instrTable.setEnabled(True)

def state_record_mode(ui):
    ui.addRadio.setChecked(False)
    ui.recordRadio.setChecked(True)
    ui.freqSlider.setEnabled(False)
    ui.selectButton.setEnabled(False)
    ui.portCombo.setEnabled(False)
    ui.acquireButton.setEnabled(False)
    ui.instrTable.setEnabled(False)

def state_acquiring(ui):
    ui.addRadio.setChecked(True)
    ui.recordRadio.setChecked(False)
    ui.addRadio.setEnabled(False)
    ui.recordRadio.setEnabled(False)
    ui.freqSlider.setEnabled(False)
    ui.selectButton.setEnabled(False)
    ui.portCombo.setEnabled(False)
    ui.acquireButton.setEnabled(False)
    ui.instrTable.setEnabled(False)

