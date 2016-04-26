ui_%.py: %.ui
	pyuic5 $< > $@

ui: \
	hanalyse/ui_mainwindow.py \
	hanalyse/ui_tagdialog.py
