ui_%.py: %.ui
	pyuic5 $< > $@

ui: \
	ui_mainwindow.py \
	ui_tagdialog.py
